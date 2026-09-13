# Architecture

Topology: **on-prem**  
Fingerprint: `77d0ca12ee0864e0`

## Scope

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

## Decisions

| Component | Approach | Implemented with | Why |
|---|---|---|---|
| deployment | systemd-unit | plain-python | Service unit: always |
| evaluation | field-match | plain-python | Field-level matching: output_shape == structured |
| governance | boundary-and-audit | plain-python | Boundary and audit: data_residency == cannot_leave |
| integration | direct-call | plain-python | Direct call: external_systems < 2 |
| observability | structured-logs | plain-python | Structured logs: always |
| perception | ocr-pipeline | plain-python | OCR pipeline: input_format == scanned_documents |
| provisioning | ansible-playbook | plain-python | Convergent configuration: provisioning_api == false |
| representation | llm-extraction | plain-python | Model extraction: output_shape == structured |

## Tools and libraries

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

## Agent and tool posture

- `integration` acts on the world. In front of it: approve-integration, critic-integration; idempotency key `1224ad29445b9354` so re-running cannot act twice.
- One operating team acts here; the audit names people, not roles.
- Tool boundary realized via `plain-python`.


## Rejected alternatives

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

## Assumptions

Nobody answered these, so nothing was decided on them. Each is a question worth asking before this is built.

- none

## Licences

Everything this design pulls in, so it can be checked before a legal team checks it.

- `plain-python`: PSF
