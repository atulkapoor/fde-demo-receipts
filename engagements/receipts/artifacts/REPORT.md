# receipts: decision brief

Written by `fde report` on 2026-10-12 from the record at `engagements/receipts`. Every figure below is read off that record; nothing here is estimated. Where a section quotes a command, it is what the command prints today, and running it again is the way to check.

## The problem as stated

The first statement, as the client put it.

> Extract company, date, address and total from scanned retail receipts; 626 receipts with labelled ground truth; data stays on this machine; a finance assistant waits on each receipt.

## Where the engagement stands

The stage is computed from the evidence on the record, not declared.

```text
receipts: pilot

  ok discovery
       ok a problem statement: Extract company, date, address and total from scanned retail receipts; 626 recei...
  ok validation
       ok the gates pass or are waived on the record: all pass
       ok the exam is seeded from the client's pairs: 120 pairs
       ok a holdout the delivery never ships: 30 cases
       ok data access attested: sqlite receipts.db: SELECT returned 626 real rows (SROIE receipts, id/company/da
  ok prototype
       ok a build with its exam record: project-0.1.27
  ok pilot
       ok a scorecard on record: scorecard.json
       ok the out-of-sample rows hold: 56.7% on 30 cases
       ok the edge answers a valid request: 200 {"company": "SYL ROASTED DELIGHTS SDN. BHD.", "date": "06/03
  -- production
       NO a deployment on record: none: fde deployed <eng> --note
       ok no open incident: none open
  -- adoption
       NO an adoption figure measured in the field: none: fde outcome <eng> --metric adoption=<value>
  -- retrospective
       NO a retrospective captured as a case: none: fde retro

to reach production: a deployment on record -- none: fde deployed <eng> --note
```

## What the record knows, and who said it

Every fact carries its source. A fact learned from a person or inferred is asserted, not established; the gates below say which ones still need establishing.

```text
known (27)
  functional scope:
    external_systems = 1   [Atul Kapoor, admin]
    input_format = scanned_documents   [system]
    output_shape = structured   [system]
    query_pattern = lookup   [Atul Kapoor, eval_owner]
    recall_span = within_turn   [Atul Kapoor, admin]
  non-functional scope:
    access_model = single_operator   [Atul Kapoor, admin]
    availability_target = business_hours   [Atul Kapoor, admin]
    cheap_path_coverage = 0.33   [Atul Kapoor, eval_owner]
    confidence_calibrated = False   [Atul Kapoor, admin]
    human_waiting = yes   [Atul Kapoor, user]
    interpretability_required = False   [Atul Kapoor, eval_owner]
    latency_budget_ms = 30000   [Atul Kapoor, user]
  data scope:
    arrival_rate = 40   [Atul Kapoor, admin]
    corpus_churn = continuous   [Atul Kapoor, admin]
    corpus_size = 626   [Atul Kapoor, eval_owner]
    data_residency = cannot_leave   [Atul Kapoor, admin]
    labelled_count = 626   [system]
    sensitivity_present = True   [system]
  environment:
    accelerator = none   [Atul Kapoor, admin]
    container_competence = False   [Atul Kapoor, admin]
    environment_lifetime = permanent   [Atul Kapoor, admin]
    existing_cluster = False   [Atul Kapoor, admin]
    existing_iac_tool = none   [Atul Kapoor, admin]
    hosting = on-prem   [Atul Kapoor, admin]
    provisioning_api = False   [Atul Kapoor, admin]
  operations:
    operates_after_handover = app_team   [Atul Kapoor, admin]
  commercial:
    licence_posture = internal_only   [Atul Kapoor, admin]

100% of what gets decided is settled

waived (1)
  outcome_contract: no client owns an outcome: a public demonstration on a public receipt dataset; the baseline's business metric is stated, and nobody has set a target
```

## The number this system exists to move

No outcome contract is on the record; it is the eighth gate.

`fde outcome-contract` records the owner, the metric, its value today, the target, the method and the window -- or a waiver saying why not yet.

## The design, with its reasons

What `fde architect` decides from the facts above, with the approach each component takes and why; what could not be decided is listed under the risks. A build writes this same page as ARCHITECTURE.md.

Topology: **on-prem**  
Fingerprint: `77d0ca12ee0864e0`

### Scope

**Functional scope**
- `external_systems` = 1
- `input_format` = scanned_documents
- `output_shape` = structured
- `query_pattern` = lookup
- `recall_span` = within_turn

**Non-functional scope**
- `access_model` = single_operator
- `availability_target` = business_hours
- `cheap_path_coverage` = 0.33
- `confidence_calibrated` = False
- `human_waiting` = yes
- `interpretability_required` = False
- `latency_budget_ms` = 30000

**Data scope**
- `arrival_rate` = 40
- `corpus_churn` = continuous
- `corpus_size` = 626
- `data_residency` = cannot_leave
- `labelled_count` = 626
- `sensitivity_present` = True

**Environment**
- `accelerator` = none
- `container_competence` = False
- `environment_lifetime` = permanent
- `existing_cluster` = False
- `existing_iac_tool` = none
- `hosting` = on-prem
- `provisioning_api` = False

**Operations**
- `operates_after_handover` = app_team

**Commercial**
- `licence_posture` = internal_only

### Decisions

| Component | Approach | Implemented with | Why |
|---|---|---|---|
| deployment | systemd-unit (advisory: decided and emitted, not a payload step) | plain-python | Service unit: always |
| evaluation | field-match (advisory: decided and emitted, not a payload step) | plain-python | Field-level matching: output_shape == structured |
| governance | boundary-and-audit (advisory: decided and emitted, not a payload step) | plain-python | Boundary and audit: data_residency == cannot_leave |
| integration | direct-call | plain-python | Direct call: external_systems < 2 |
| observability | structured-logs (advisory: decided and emitted, not a payload step) | plain-python | Structured logs: always |
| perception | ocr-pipeline | plain-python | OCR pipeline: input_format == scanned_documents |
| provisioning | ansible-playbook (advisory: decided and emitted, not a payload step) | plain-python | Convergent configuration: provisioning_api == false |
| representation | llm-extraction | plain-python | Model extraction: output_shape == structured |

The tool boundary is emitted UNWIRED: no external system's tools are registered and the approval gate and critic are constructed without `approve=`/`review=`. Until the implementation registers tools and wires both, every action-shaped request is refused (409) -- fail closed, by design.

### Tools and libraries

| Component | Chosen | Licence | Alternatives in this topology |
|---|---|---|---|
| deployment | plain-python | PSF | -- |
| evaluation | plain-python | PSF | -- |
| governance | plain-python | PSF | -- |
| integration | plain-python | PSF | -- |
| observability | plain-python | PSF | -- |
| perception | plain-python | PSF | tesseract |
| provisioning | plain-python | PSF | -- |
| representation | plain-python | PSF | -- |

Adopting an alternative the client already operates: `fde reuse <engagement> <stack>` and rebuild -- the architecture does not change, only the emitted code does.

### Agent and tool posture

- `integration` acts on the world. In front of it: approve-integration, critic-integration; an idempotency key derived from each action and reserved in the ledger (app/ledger.py) before it runs, so a retry cannot act twice.
- One operating team acts here; the audit names people, not roles.
- Tool boundary realized via `plain-python`.


### Rejected alternatives

What this design is not, and why. Usually the more useful half.

**deployment**
- `compose` -- ruled out by container_competence == false
- `kubernetes-manifests` -- ruled out by container_competence == false and existing_cluster == false

**evaluation**
- `judged` -- ruled out by output_shape == structured
- `labelled-metrics` -- ruled out by output_shape == structured

**governance**
- `audit-only` -- ruled out by data_residency == cannot_leave
- `role-scoped-authority` -- ruled out by access_model == single_operator

**integration**
- `governed-tools` -- ruled out by external_systems < 2

**observability**
- `traced` -- ruled out by external_systems < 2

**perception**
- `passthrough` -- ruled out by input_format == scanned_documents
- `speech-transcription` -- nothing here matches input_format == audio
- `text-extraction` -- ruled out by input_format == scanned_documents
- `video-ingestion` -- nothing here matches input_format == video
- `windowed-ingestion` -- ruled out by input_format == scanned_documents

**provisioning**
- `gitops` -- ruled out by existing_cluster == false
- `terraform-module` -- ruled out by provisioning_api == false
- `manual-runbook` -- ansible-playbook is simpler and applies here

**representation**
- `assisted-deterministic` -- nothing here matches output_shape == structured and cheap_path_coverage < 0.95 and interpretability_required == true or output_shape == decision and cheap_path_coverage < 0.95
- `cascade` -- ruled out by confidence_calibrated == false
- `classical-ml` -- ruled out by output_shape == structured
- `deterministic` -- ruled out by cheap_path_coverage < 0.95
- `finetune` -- nothing here matches output_shape == freeform and labelled_count >= 1000
- `segmentation` -- ruled out by output_shape == structured

### Licences

Everything this design pulls in, so it can be checked before a legal team checks it.

- `plain-python`: PSF

## What the design rests on, and what was accepted

Waived gates, overridden recommendations, assumptions nobody has answered, and the facts the governance follows from. A build writes this same page as RISKS.md.

### Decided, emitted, not on the payload path

These components were decided and their modules are emitted, but the request path does not run them: the edge's structured log is the observability that runs, the ledger is the audit that runs, the unit is the deployment. Each module says so in its first lines. Wire one in, or leave it as the reference it is -- but do not read its presence as running code.

- `deployment`
- `evaluation`
- `governance`
- `observability`
- `provisioning`

### Identity at the edge

One bearer token, one service principal, one set of scopes: every caller acts as the same identity, so the audit names the service, not a person. Per-caller identity is an `access_model` decision nobody has answered; accept this or front the service with something that does.

### Facts this design stands on

The governance, the boundary and the topology follow from these values. A value learned from a person or inferred is asserted, not established -- confirm it with the client before the decision that rests on it stands.

- `data_residency = cannot_leave` -- interview -- asserted, not established: confirm before the decisions resting on it stand
- `hosting = on-prem` -- interview -- asserted, not established: confirm before the decisions resting on it stand

### Gates waived

Each was blocking at build time. Somebody decided to proceed anyway, and this is who said what.

- **outcome_contract** (2026-09-20) -- no client owns an outcome: a public demonstration on a public receipt dataset; the baseline's business metric is stated, and nobody has set a target
  - covered: Nobody has agreed which number this system exists to move: no outcome contract was recorded.

## Decision debt

Everything the engagement rests on that nobody has settled, each with an owner and an age.

```text
receipts: decision debt as of 2026-10-12

  open (10)
    waiver         outcome_contract: no client owns an outcome: a public demonstration on a public receipt dataset; the baseline's business metric is stated, and nobody has set a target
                   owner: the author  22 day(s)
                   next: meet the gate, or restate the waiver if it still holds
    stated         accelerator = none: said by Atul Kapoor (admin), measurable but not measured
                   owner: admin
                   next: measure it: fde scan, or a document the client owns
    stated         existing_iac_tool = none: said by Atul Kapoor (admin), measurable but not measured
                   owner: admin
                   next: measure it: fde scan, or a document the client owns
    stated         container_competence = False: said by Atul Kapoor (admin), measurable but not measured
                   owner: admin
                   next: measure it: fde scan, or a document the client owns
    stated         existing_cluster = False: said by Atul Kapoor (admin), measurable but not measured
                   owner: admin
                   next: measure it: fde scan, or a document the client owns
    stated         provisioning_api = False: said by Atul Kapoor (admin), measurable but not measured
                   owner: admin
                   next: measure it: fde scan, or a document the client owns
    unsigned       data_access (2026-09-10)
                   owner: unsigned  32 day(s) AGING
                   next: re-record with --by, or leave it and know it
    unsigned       security_review (2026-09-10)
                   owner: unsigned  32 day(s) AGING
                   next: re-record with --by, or leave it and know it
    unheard        sponsor has never been asked
                   owner: sponsor
                   next: fde ask <eng> --role sponsor
    unheard        skeptic has never been asked
                   owner: skeptic
                   next: fde ask <eng> --role skeptic

10 item(s): 0 blocking the build, 0 blocking production, 2 older than 30 days, 2 unsigned
```

## What would stop this

The conditions on record under which the honest answer is to stop, judged against what has been measured so far.

```text
no stop conditions on record: fde stop-when <eng> --when "answered_accuracy < 0.88"
```

## The next decision

The single best next action judged from everything above, and what turns on it.

```text
next: fde scan engagements/receipts
  this build calls a model and LLM_ENDPOINT is not set -- scan names the runtime, the model sized to this hardware, and the export line
```
