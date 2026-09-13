"""integration: direct-call, via plain-python.

Direct call: external_systems < 2

One system, called directly. A registry for a single endpoint is ceremony, and
adding it before there is a second caller is the tidiness that costs an
engagement a week.

What does not get skipped: a mutative call still needs a key so a retry cannot
happen twice, and it still needs a timeout. Those are cheap here and expensive
to add once something is in production and occasionally double-charging.
"""

from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import time
from collections.abc import Callable
from contextlib import closing
from pathlib import Path
from typing import Any

from app.components.governance import Governance

DEFAULT_TIMEOUT_SECONDS = 10.0

# The one external system: the submission record a receipt is posted
# against. On this engagement it is a file on the same machine, because the
# data cannot leave it -- point RECEIPTS_LEDGER at the finance system's own
# store when there is one, and nothing above this line changes.
DEFAULT_LEDGER = Path(__file__).resolve().parents[2] / "var" / "submissions.sqlite3"

SCHEMA = """
CREATE TABLE IF NOT EXISTS submissions (
    key       TEXT PRIMARY KEY,
    action    TEXT NOT NULL,
    operator  TEXT NOT NULL,
    document  TEXT NOT NULL,
    pages     INTEGER NOT NULL,
    at        TEXT NOT NULL
)
"""


class Integration:
    """ToolBoundary, as direct-call."""

    interface = "ToolBoundary"
    approach = "direct-call"
    stack = "plain-python"

    def __init__(
        self,
        call: Callable[..., Any] | None = None,
        mutative: bool = True,
        timeout: float = DEFAULT_TIMEOUT_SECONDS,
    ) -> None:
        self._call = call
        # Assumed to change something. Guessing wrong this way costs a key
        # nobody needed; the other way costs a duplicate.
        self.mutative = mutative
        self.timeout = timeout
        self._seen: dict[str, Any] = {}

    def run(self, payload: dict[str, Any]) -> Any:
        if not self.mutative:
            return self._call(**payload)

        key = payload.get("idempotency_key") or self.key_for(payload)
        if key in self._seen:
            return {"result": self._seen[key], "duplicate": True}

        result = self._call(**payload, timeout=self.timeout)
        self._seen[key] = result
        return {"result": result, "duplicate": False, "key": key}

    @staticmethod
    def key_for(payload: dict[str, Any]) -> str:
        """From what the call is, so a retry produces the same key."""
        body = json.dumps(
            {k: v for k, v in payload.items() if k != "idempotency_key"},
            sort_keys=True, default=str,
        )
        return hashlib.sha256(body.encode()).hexdigest()[:32]


class SubmissionLedger:
    """The endpoint behind the boundary: one receipt, recorded once.

    Registering a submission is the call that changes something outside this
    system, so it is the call the approval gate and the critic sit in front
    of. Two properties are load-bearing and both are cheap here:

    - **It happens once.** The key comes from the document, the row is
      written with INSERT OR IGNORE, and the guard returns the stored
      outcome on a retry. At-least-once delivery meets idempotent
      processing, which is the only combination that exists.
    - **It records the document, not its contents.** A scan that may not
      leave the machine does not get copied into an audit table; the row
      names the document by digest and counts its pages. What was posted is
      recoverable from the document, and the document has not moved.
    """

    def __init__(self, path: str | Path | None = None,
                 guard: Governance | None = None) -> None:
        self.path = Path(path or os.environ.get("RECEIPTS_LEDGER") or DEFAULT_LEDGER)
        # The audit and the idempotency key live with the guard, because a
        # key whose outcome is stored somewhere else records actions the
        # system did not take.
        self.guard = guard or Governance()

    def record(
        self,
        *,
        action: str,
        operator: str,
        document: str,
        pages: int,
        records: list[dict[str, Any]],
        idempotency_key: str | None = None,
        timeout: float = DEFAULT_TIMEOUT_SECONDS,
    ) -> dict[str, Any]:
        """Register the submission, and hand back what it holds."""
        outcome = self.guard.run({
            "action": action,
            "operator": operator,
            "document": document,
            "pages": pages,
            # A submission cannot be unsent, so it does not run unapproved.
            "reversible": False,
            "approved_by": operator,
            "idempotency_key": idempotency_key,
        })
        if not outcome.get("duplicate"):
            self._append((outcome["key"], action, operator, document, pages,
                          time.strftime("%Y-%m-%dT%H:%M:%S")), timeout)
        return {
            "submission": outcome["key"],
            "duplicate": bool(outcome.get("duplicate")),
            # The registered submission, as the system of record hands it
            # back: the pages the extraction is about to run over.
            "records": records,
        }

    def _append(self, row: tuple[Any, ...], timeout: float) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with closing(sqlite3.connect(self.path, timeout=timeout)) as store:
            store.execute(SCHEMA)
            store.execute(
                "INSERT OR IGNORE INTO submissions VALUES (?, ?, ?, ?, ?, ?)", row
            )
            store.commit()
