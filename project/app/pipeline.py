"""The order things run in.

Ordered by what caps what: a step whose quality bounds another comes
first, so when an answer is wrong there is somewhere to look.
Approval gates and critics are steps like any other -- removing one
is a visible diff, not an oversight.

Only payload-transforming components are chained here. Deployment,
provisioning, evaluation and their kin are decided and emitted, but a
service unit is not a step a payload passes through.

The evaluation harness calls run() with each golden case's raw input.
Adapting that input to the first step's payload shape is yours: do it
at the top of run(), where the seam is visible.

The seams between steps are visible here for the same reason: each one is a
named function, because "shapes that almost match" is what the runbook lists
as the usual cause of a system whose parts are all correct.
"""

from __future__ import annotations

import getpass
import hashlib
import json
import os
import sys
from typing import Any

from app import boundary  # noqa: F401 -- placement checked at import
from app import controls
from app import llm
from app.components import integration
from app.components import observability
from app.components import perception
from app.components import representation
from app.contract import RefusedInput

# The declared output contract. Every step downstream is checked against it
# and nothing outside it is returned.
FIELDS = ["company", "date", "address", "total"]

# Named in the log, never printed into it. A scan that may not leave the
# machine does not leave it in a log line either, and a log aggregator is
# the most commonly forgotten way out of a boundary.
SENSITIVE = {"text", "pages", "regions", "records", "fields", "mapped"}

# The one action this pipeline takes on the world.
RECORD_SUBMISSION = "record_receipt_submission"


def _process_owner() -> str:
    """Who is running this, for the audit to name.

    One operating team acts here, so the audit names people rather than
    roles. Left unanswerable, this returns nothing and the approval gate
    refuses -- an action nobody can be named for is not an action this
    system takes.
    """
    try:
        return getpass.getuser()
    except Exception:  # noqa: BLE001 - no passwd entry is an answer, not a crash
        return ""


OPERATOR = os.environ.get("FDE_OPERATOR") or _process_owner()

# The endpoint behind the tool boundary, and the audit that goes with it.
LEDGER = integration.SubmissionLedger()


def approve_submission(action: dict[str, Any]) -> bool:
    """Standing approval for one action, and nothing else.

    A single operator runs this system and has said yes to recording a
    receipt submission -- that decision is here, in the code, where a diff
    shows it changing. What the policy does not do is say yes to a different
    action, to a run nobody can be named for, or to a call with no
    idempotency key: each of those is a question that has to come back and
    be asked.
    """
    return (
        action.get("action") == RECORD_SUBMISSION
        and bool(action.get("operator"))
        and bool(action.get("idempotency_key"))
        and bool(action.get("records"))
    )


def review_submission(action: dict[str, Any]) -> list[str]:
    """What has to hold before a submission is registered.

    Checked here rather than apologised for later. Each of these has a
    failure that looks fine in the logs: an action against a document
    nothing identifies, a page nothing could be read from, or a boundary
    that moved since the last review.
    """
    problems = []
    if action.get("action") != RECORD_SUBMISSION:
        problems.append(f"{action.get('action')!r} is not the approved action")
    if not action.get("document"):
        problems.append("nothing identifies the document being submitted")
    if not action.get("operator"):
        problems.append("no operator is named for this submission")
    if boundary.PLACEMENT.get("integration") != "in_boundary":
        problems.append("integration is placed outside the boundary")
    blank = [r.get("id") for r in action.get("records", []) if not r.get("regions")]
    if blank:
        problems.append(f"nothing was read from {blank}")
    return problems


def model(prompt: str) -> str:
    """The serving seam.

    One place talks to the model, and one line says so when it is not there:
    the harness reports a failed case by source, which reads identically for
    an unreachable model and a wrong answer, and those need different work.
    """
    try:
        return llm.complete(prompt)
    except Exception as exc:  # noqa: BLE001 - reported, then re-raised
        if not model.reported:
            model.reported = True
            print(
                f"app.pipeline: the model this architecture chose "
                f"({representation.Representation.approach}) is not "
                f"answering, so every case will fail as a system error -- "
                f"{exc}",
                file=sys.stderr,
            )
        raise


model.reported = False


STEPS = [
    ('perception', perception.Perception(engine=perception.scan,
                                         critical_regions={'header'})),
    ('approve-integration', controls.ApprovalGate(guards='integration', idempotency_key='1224ad29445b9354', approve=approve_submission)),
    ('critic-integration', controls.Critic(guards='integration', review=review_submission)),
    ('integration', integration.Integration(call=LEDGER.record, mutative=True)),
    ('representation', representation.Representation(complete=model)),
]


def ingest(raw: Any) -> dict[str, Any]:
    """The raw case, as the first step's payload -- or a refusal.

    Everything this rejects is something the pipeline must not act on: a
    document of the wrong type, a document with no pages, a page with
    nothing on it. Saying so is the correct answer; the alternative is a
    confident set of fields for a receipt nobody supplied.
    """
    if isinstance(raw, str):
        document = {"text": raw}
    elif isinstance(raw, dict):
        document = raw
    else:
        raise RefusedInput(
            f"a scanned document arrives as text or as pages, not as "
            f"{type(raw).__name__}"
        )

    pages = document.get("pages")
    if pages is None:
        if "text" not in document:
            raise RefusedInput("no 'text' and no 'pages': nothing was supplied")
        pages = [{"id": document.get("id", "1"), "text": document["text"]}]
    if not isinstance(pages, list):
        raise RefusedInput(f"'pages' is {type(pages).__name__}, not a list")

    read = []
    for number, page in enumerate(pages, 1):
        text = page.get("text") if isinstance(page, dict) else page
        if not isinstance(text, str):
            raise RefusedInput(f"page {number} carries no text")
        read.append({"id": (page.get("id") if isinstance(page, dict) else None)
                     or str(number), "text": text})
    if not read or not any(p["text"].strip() for p in read):
        raise RefusedInput("the document is empty")
    return {"pages": read}


def submission(perceived: dict[str, Any]) -> dict[str, Any]:
    """Perception's pages, as the action the gate and the critic judge.

    The key is derived from the document rather than from the build: the
    gate's own key names this deployment, and a retry of *this receipt* is
    what must not post twice.
    """
    pages = perceived.get("pages", [])
    digest = hashlib.sha256(
        "\n\n".join(p.get("text", "") for p in pages).encode()
    ).hexdigest()[:16]
    action = {
        "action": RECORD_SUBMISSION,
        "operator": OPERATOR,
        "document": digest,
        "pages": len(pages),
        "records": [
            {"id": p.get("id"), "regions": p.get("regions", []),
             "verify": bool(p.get("needs_human"))}
            for p in pages
        ],
    }
    action["idempotency_key"] = integration.Integration.key_for(action)
    return action


def mapping(recorded: dict[str, Any]) -> dict[str, Any]:
    """The registered submission, as the mapper's payload."""
    result = recorded.get("result") or {}
    return {
        "contract": FIELDS,
        "records": result.get("records", []),
        "submission": result.get("submission"),
    }


# What runs before each step, so a payload never arrives at a shape it does
# not expect.
SEAMS = {
    'approve-integration': submission,
    'representation': mapping,
}


def run(payload):
    """One scanned document in, the contract's fields out."""
    log = observability.Observability(sensitive=SENSITIVE)
    state = ingest(payload)
    log.event("ingested", page_count=len(state["pages"]))

    for name, step in STEPS:
        if name in SEAMS:
            state = SEAMS[name](state)
        state = step.run(state)
        log.event(name, **_reportable(state))

    records = (state.get("records") or [{}])
    fields = records[0].get("mapped") or {}
    log.event("extracted", fields=fields,
              unmapped=records[0].get("unmapped"),
              rejected=list(records[0].get("rejected") or ()))
    # The contract, and only the contract.
    return {field: fields.get(field) for field in FIELDS}


def _reportable(state: Any) -> dict[str, Any]:
    """The numbers from a step, without the document in them."""
    if not isinstance(state, dict):
        return {}
    return {key: state[key] for key in
            ("clean_share", "verify_queue", "duplicate", "submission",
             "mapped_share", "needs_attention", "action")
            if key in state}


def main() -> int:
    """One document per line on stdin, one extraction per line out.

    The service unit runs this module; a worker that reads its queue and
    writes what it found is the smallest thing that is not a stub.
    """
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            document = json.loads(line)
        except json.JSONDecodeError:
            document = line
        try:
            print(json.dumps(run(document)), flush=True)
        except RefusedInput as refusal:
            print(json.dumps({"refused": str(refusal)}), flush=True)
    return 0


if __name__ == "__main__":
    # Post-measurement ops hardening (fde-framework 0.1.11 backport, after
    # the measured runs): the agent's stdin worker below is kept for queue
    # use (pipe a JSONL through `python -m app.pipeline --stdin`), but the
    # service unit needs a process that serves -- a module reading a stdin
    # systemd never connects exits 0 silently and Restart=on-failure never
    # restarts it.
    import os as _os
    import sys as _sys

    if "--stdin" in _sys.argv:
        raise SystemExit(main())

    import json as _json
    from http.server import BaseHTTPRequestHandler, HTTPServer

    class _Handler(BaseHTTPRequestHandler):
        def _send(self, code, body):
            data = _json.dumps(body, default=str).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            if self.path == "/health":
                self._send(200, {"status": "ok"})
            else:
                self._send(404, {"error": "POST / with a JSON payload"})

        def do_POST(self):
            length = int(self.headers.get("Content-Length", 0))
            try:
                payload = _json.loads(self.rfile.read(length) or b"null")
            except ValueError:
                self._send(400, {"error": "body is not JSON"})
                return
            try:
                self._send(200, {"result": run(payload)})
            except RefusedInput as refusal:
                self._send(422, {"refused": str(refusal)})

        def log_message(self, fmt, *args):
            print(fmt % args)

    port = int(_os.environ.get("PORT", "8080"))
    print(f"serving on :{port} -- /health, POST /")
    HTTPServer(("0.0.0.0", port), _Handler).serve_forever()
