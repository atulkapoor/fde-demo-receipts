# Risks accepted

No gate was waived and no recommendation overridden. Every component in scope was decided; decided is not implemented -- see below for what still raises.

## Decided, emitted, not on the payload path

These components were decided and their modules are emitted, but the request path does not run them: the edge's structured log is the observability that runs, the ledger is the audit that runs, the unit is the deployment. Each module says so in its first lines. Wire one in, or leave it as the reference it is -- but do not read its presence as running code.

- `deployment`
- `evaluation`
- `governance`
- `observability`
- `provisioning`

## Identity at the edge

One bearer token, one service principal, one set of scopes: every caller acts as the same identity, so the audit names the service, not a person. Per-caller identity is an `access_model` decision nobody has answered; accept this or front the service with something that does.

## Facts this design stands on

The governance, the boundary and the topology follow from these values. A value learned from a person or inferred is asserted, not established -- confirm it with the client before the decision that rests on it stands.

- `data_residency = cannot_leave` -- interview -- asserted, not established: confirm before the decisions resting on it stand
- `hosting = on-prem` -- interview -- asserted, not established: confirm before the decisions resting on it stand

