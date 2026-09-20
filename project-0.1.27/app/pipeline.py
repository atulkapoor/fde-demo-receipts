"""The order things run in.

Ordered by phase -- what reads text before what chunks it, what
indexes before what queries, nothing outward before reasoning has
decided -- so when an answer is wrong there is somewhere to look.
Approval gates and critics run first on the request path: they pass
everything that is not an action, and refuse an action before anything
costs money. Removing one is a visible diff, not an oversight.

Only payload-transforming components are chained here. Deployment,
provisioning, evaluation, serving and their kin are decided and
emitted, but a service unit is not a step a payload passes through.

Every step reads and writes one envelope (app/shapes.py). run()
normalises the caller's raw input into it and returns the OUTPUT --
what output() picks from the finished envelope -- so the evaluation
harness and the HTTP edge hand over, and get back, the same things.
"""

import json
import sys

from app import (
    boundary,  # noqa: F401 -- placement checked at import
    controls,
)
from app.components import (
    integration,
    perception,
    representation,
)
from app.contract import RefusedInput
from app.shapes import envelope

# The request path.
#
# What is wired, and what is deliberately not:
#
#   perception      engine=scan, and 'header' declared critical -- the
#                   letterhead is where the company and the address are, so
#                   an illegible line there is a page for a person, not an
#                   average to hide in.
#   representation  the page nominates, and with no model served inside the
#                   boundary the page's own ranking chooses. Pass
#                   complete=<callable> here to hand the same closed
#                   question to a model instead (app/llm.py is the one
#                   touchpoint); every record records which one decided.
#   integration     left unwired, with its gate and its critic. ARCHITECTURE
#                   says so: until an external system's client is registered
#                   and both controls are given callables, an action-shaped
#                   request is refused rather than taken. Nothing on the
#                   read path asks for anything outward, so nothing here is
#                   waiting on it.
STEPS = [
    ('approve-integration', controls.ApprovalGate(guards='integration')),
    ('critic-integration', controls.Critic(guards='integration')),
    ('perception', perception.Perception(engine=perception.scan,
                                         critical_regions={'header'})),
    ('representation', representation.Representation()),
    ('integration', integration.Integration()),
]


def _run_steps(steps, payload: dict) -> dict:
    for name, step in steps:
        try:
            payload = step.run(payload)
        except RefusedInput:
            raise
        except Exception:
            sys.stderr.write(json.dumps({"failed_step": name,
                                         "request_id": payload.get("request_id")})
                             + "\n")
            sys.stderr.flush()
            raise
    return payload


def output(payload: dict) -> object:
    """What a caller gets back: the answer, the decision, the mapped
    record, the plan -- whichever this system produces -- never the
    whole envelope with the principal and the raw input inside it.
    The evaluation harness compares THIS against each case's output.
    """
    for key in ("answer", "decision", "plan", "integration"):
        if key in payload:
            return payload[key]
    records = payload.get("records")
    if isinstance(records, list) and records and "mapped" in records[0]:
        if len(records) == 1:
            return records[0]["mapped"]
        return [r["mapped"] for r in records]
    if "retrieved" in payload:
        return payload["retrieved"]
    return {k: v for k, v in payload.items()
            if k not in ("request_id", "principal", "input")}


def run_envelope(raw: object, *, request_id: str | None = None,
                 principal: dict | None = None) -> dict:
    """The whole envelope after every step -- for tests and diagnosis."""
    payload = envelope(raw)
    payload["request_id"] = request_id or "local"
    payload["principal"] = principal or {"subject": "anonymous", "scopes": []}
    return _run_steps(STEPS, payload)


def run(raw: object, *, request_id: str | None = None,
        principal: dict | None = None) -> object:
    """One request through the payload path, answered.

    Exceptions propagate unchanged -- the edge maps their types to
    status codes -- but a failing step's name and the request id
    reach the journal first, so no traceback is anonymous. A refusal
    is an answer, not a failure, and passes through untouched.
    """
    return output(run_envelope(raw, request_id=request_id, principal=principal))


if __name__ == "__main__":
    from app.service import main

    raise SystemExit(main())
