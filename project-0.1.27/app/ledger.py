"""Append-only record of what the system did, and what it must not do twice.

Two files under STATE_DIR: `audit.jsonl` -- every outward call's intent,
outcome or failure, with the request id that caused it -- and
`idempotency.jsonl`, keys reserved BEFORE a call is made. A retry after a
crash finds its key already taken and stops, instead of sending the letter
again. Both are fsync'd on every write; the rollback runbook's "the audit
trail is where the answer is" is only true if the trail survives the stop.

Without STATE_DIR the ledger lives in process memory and says so on every
start. Fine on a laptop. Not a service.
"""

from __future__ import annotations

import fcntl
import hashlib
import json
import os
import re
import sys
import threading
import time
import uuid
from pathlib import Path
from typing import Any

SENSITIVE_ARGUMENT = re.compile(r"(password|secret|token|api[_-]?key|ssn|card|account)",
                                re.IGNORECASE)


class KeyUnresolved(RuntimeError):
    """This key was reserved and never completed -- a crash mid-call. It
    needs a person to establish what happened; retrying blind is how one
    letter becomes two."""


def redact(arguments: dict[str, Any]) -> dict[str, Any]:
    return {k: ("<redacted>" if SENSITIVE_ARGUMENT.search(k) else v)
            for k, v in arguments.items()}


class Ledger:
    def __init__(self, directory: str | None = None) -> None:
        root = directory or os.environ.get("STATE_DIR")
        self.root = Path(root) if root else None
        self._lock = threading.Lock()
        self._keys: dict[str, dict[str, Any]] = {}
        self._audit: list[dict[str, Any]] = []
        # A ledger that cannot write must not stop the process from
        # starting with a traceback: it records the problem, and the
        # edge's preflight refuses the boot with one clear line (exit 78).
        self.problem: str | None = None
        if self.root is not None:
            try:
                self.root.mkdir(parents=True, exist_ok=True)
                probe = self.root / ".write-probe"
                probe.write_text("")
                probe.unlink()
            except OSError as exc:
                self.problem = f"STATE_DIR {self.root} is not writable: {exc}"
                self.root = None
        if self.root is not None:
            for line in self._read("idempotency.jsonl"):
                if "key" in line:
                    self._keys[line["key"]] = line
        else:
            why = self.problem or "STATE_DIR unset"
            sys.stderr.write(json.dumps({"level": "warning", "ledger":
                                         f"{why}: audit and idempotency live in "
                                         f"process memory and vanish on restart"}) + "\n")
            sys.stderr.flush()

    # -- files ---------------------------------------------------------------

    def _read(self, name: str) -> list[dict[str, Any]]:
        """Every intact record. A torn last line -- what a crash mid-write
        leaves -- is the crash record this ledger exists to survive, not
        a reason the process cannot start."""
        path = self.root / name
        if not path.exists():
            return []
        records, torn = [], 0
        for line in path.read_text(errors="replace").splitlines():
            if not line.strip():
                continue
            try:
                records.append(json.loads(line))
            except ValueError:
                torn += 1
        if torn:
            sys.stderr.write(json.dumps({"level": "warning", "ledger": name,
                                         "torn_lines_skipped": torn}) + "\n")
            sys.stderr.flush()
        return records

    def _locked(self):
        """An exclusive lock on STATE_DIR shared by every process that
        writes the ledger -- the service and the operator's compaction --
        so neither can interleave with, or rewrite under, the other."""
        return _DirectoryLock(self.root)

    def _write(self, name: str, record: dict[str, Any]) -> None:
        if self.root is None:
            return
        # One append per record, fsync'd, under the directory lock: a
        # crash leaves at most one torn line, never an interleaving.
        with self._locked():
            self._append_unlocked(name, record)

    def _append_unlocked(self, name: str, record: dict[str, Any]) -> None:
        """The append itself; the caller holds the directory lock."""
        if self.root is None:
            return
        data = (json.dumps(record, default=str) + "\n").encode()
        fd = os.open(self.root / name, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o600)
        try:
            os.write(fd, data)
            os.fsync(fd)
        finally:
            os.close(fd)

    # -- audit ---------------------------------------------------------------

    def append(self, record: dict[str, Any]) -> str:
        entry = {"id": str(uuid.uuid4()), "at": time.time(), **record}
        with self._lock:
            self._audit.append(entry)
            del self._audit[:-1000]  # a bounded tail in memory; the file is the record
            self._write("audit.jsonl", entry)
        return entry["id"]

    def recent(self, n: int = 50) -> list[dict[str, Any]]:
        return self._audit[-n:]

    # -- idempotency ---------------------------------------------------------

    @staticmethod
    def key_for(action: dict[str, Any]) -> str:
        """From what the action IS, so a retry derives the same key.

        Numbers are canonicalised first: 100 and 100.0 are the same amount,
        and a client that round-trips a float must not mint a second key
        for the same payment."""
        body = json.dumps(_canonical(action), sort_keys=True, default=str).encode()
        return hashlib.sha256(body).hexdigest()[:16]

    def reserve(self, key: str, digest: str) -> dict[str, Any] | None:
        """Take the key before acting. Returns the earlier outcome when
        this exact action already completed; raises when it was started
        and never finished; None when the key is now ours."""
        with self._lock, self._locked():
            # Re-check the file under the cross-process lock: a second
            # process on the same STATE_DIR (a debug run beside the unit,
            # a failover before the old instance is dead) must find the
            # key taken, not take it too.
            if self.root is not None:
                for line in self._read("idempotency.jsonl"):
                    if line.get("key") == key:
                        self._keys[key] = line
            existing = self._keys.get(key)
            if existing is not None:
                if existing.get("digest") != digest:
                    raise KeyUnresolved(f"key {key} was used for a different action")
                if "outcome" not in existing:
                    raise KeyUnresolved(f"key {key} was reserved and never completed")
                return existing
            record = {"key": key, "digest": digest, "at": time.time()}
            self._keys[key] = record
            self._append_unlocked("idempotency.jsonl", record)
            return None

    def complete(self, key: str, outcome: Any) -> None:
        with self._lock:
            record = {**self._keys.get(key, {"key": key}), "outcome": outcome,
                      "completed_at": time.time()}
            self._keys[key] = record
            self._write("idempotency.jsonl", record)

    def resolve(self, key: str, outcome: Any, by: str) -> None:
        """A person's determination of what happened to a call that was
        reserved and never completed -- the only way a stuck key moves.
        Recorded as such, with who decided."""
        with self._lock:
            record = {**self._keys.get(key, {"key": key}), "outcome": outcome,
                      "resolved_by": by, "completed_at": time.time()}
            self._keys[key] = record
            self._write("idempotency.jsonl", record)
        self.append({"phase": "resolved", "key": key, "by": by})


    def compact(self, retention_seconds: float) -> int:
        """Rewrite idempotency.jsonl keeping every unresolved key and every
        key completed within the retention. NEVER rotate that file: a key
        rotated away is an action that can happen twice. The file is
        RE-READ under the directory lock before it is rewritten, so a key
        the running service reserved a moment ago survives -- an earlier
        version rewrote from this process's stale snapshot and dropped it.
        Returns the number of records dropped."""
        cutoff = time.time() - retention_seconds
        with self._lock, self._locked():
            current: dict[str, dict[str, Any]] = dict(self._keys)
            if self.root is not None:
                for line in self._read("idempotency.jsonl"):
                    if "key" in line:
                        current[line["key"]] = line
            keep = {k: r for k, r in current.items()
                    if "outcome" not in r or r.get("completed_at", 0) >= cutoff}
            dropped = len(current) - len(keep)
            if self.root is not None:
                path = self.root / "idempotency.jsonl"
                tmp = path.with_suffix(".jsonl.tmp")
                fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
                try:
                    os.write(fd, "".join(json.dumps(r, default=str) + "\n"
                                         for r in keep.values()).encode())
                    os.fsync(fd)
                finally:
                    os.close(fd)
                os.replace(tmp, path)
                dir_fd = os.open(self.root, os.O_RDONLY)
                try:
                    os.fsync(dir_fd)
                finally:
                    os.close(dir_fd)
            self._keys = keep
        return dropped


class _DirectoryLock:
    """flock on STATE_DIR/.lock, or a no-op without a STATE_DIR."""

    def __init__(self, root: Path | None) -> None:
        self.root = root
        self.fd: int | None = None

    def __enter__(self):
        if self.root is not None:
            self.fd = os.open(self.root / ".lock", os.O_RDWR | os.O_CREAT, 0o600)
            fcntl.flock(self.fd, fcntl.LOCK_EX)
        return self

    def __exit__(self, *exc):
        if self.fd is not None:
            fcntl.flock(self.fd, fcntl.LOCK_UN)
            os.close(self.fd)
            self.fd = None


def _canonical(value: Any) -> Any:
    if isinstance(value, float) and value.is_integer():
        return int(value)
    if isinstance(value, dict):
        return {k: _canonical(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_canonical(v) for v in value]
    return value


LEDGER = Ledger()


if __name__ == "__main__":
    # python -m app.ledger resolve <key> '<outcome json>' --by <name>
    import argparse
    import getpass

    parser = argparse.ArgumentParser(description="the ledger's operator commands")
    parser.add_argument("command", choices=["resolve", "show", "compact"])
    parser.add_argument("key", nargs="?")
    parser.add_argument("outcome", nargs="?", default="null")
    parser.add_argument("--by", default=getpass.getuser())
    parser.add_argument("--keep-days", type=float, default=90.0,
                        help="compact: keep completed keys newer than this")
    args = parser.parse_args()
    if args.command == "show":
        print(json.dumps(LEDGER._keys.get(args.key), indent=2))  # noqa: SLF001
    elif args.command == "compact":
        print(f"dropped {LEDGER.compact(args.keep_days * 86400)} completed record(s)")
    else:
        LEDGER.resolve(args.key, json.loads(args.outcome), by=args.by)
        print(f"resolved {args.key} by {args.by}")
