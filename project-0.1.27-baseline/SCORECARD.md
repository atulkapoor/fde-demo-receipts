# Scorecard

**15 of 20 measured properties hold.** Measured on `/Users/atulkapoor/Documents/fde-demo-receipts/project-0.1.27`. A property this build cannot measure is marked n/a, never counted as held. The service was booted on the machine that ran this card, not inside the deployed unit; the out-of-sample rows (holdout, external exam, generalisation gap, the baseline's bar) are the fitness rows, the rest are self-consistency.

| Property | Measured | Holds |
|---|---|---|
| own tests | 7 passed in 1.38s | yes |
| lint | clean | yes |
| exam: golden | 0.0% on 77 cases | yes |
| exam: edge_case | 0.0% on 7 cases | yes |
| exam: adversarial | 40.0% on 10 cases (0 followed, 0 on misread bases) | **no** |
| exam: verdict | 77 golden case(s) errored -- the pipeline is not yet implemented end to end | **no** |
| exam record | every eval file matches its recorded digest | yes |
| holdout | 0.0% on 30 cases | **no** |
| holdout: sample size | 30 cases | yes |
| holdout: the file on record | matches evals/manifest.json | yes |
| generalisation gap | golden 0.0% - holdout 0.0% = +0.0% | yes |
| beats the baseline error rate | 0.0% on the answered against a recorded first-pass accuracy of 97.0% | **no** |
| external exam | not given | n/a |
| edge: boots | answers /health | yes |
| edge: identity | 401 without a token | yes |
| edge: forged result | 422 | yes |
| edge: forged identity | 422 | yes |
| edge: malformed body | 400 | yes |
| edge: a valid request | 422 {"refused": "missing 'pages'", "request_id": "fce6d2a9"} | **no** |
| edge: the answer says why | no | n/a |
| edge: readiness | 503 not ready: model endpoint unreachable or malformed: URLError | n/a |
| risk register: scaffolds | none | yes |
| risk register: gates waived | none | n/a |
| risk register: asserted facts | 2 boundary-bearing fact(s) asserted | n/a |
| environment | every variable the code reads is documented | yes |
| training path | none in this build | n/a |
| regression from the last card | no previous card | n/a |

## Not holding

- **exam: adversarial**: 40.0% on 10 cases (0 followed, 0 on misread bases)
- **exam: verdict**: 77 golden case(s) errored -- the pipeline is not yet implemented end to end -- the harness's own exit status at --min-score 0.0
- **holdout**: 0.0% on 30 cases -- cases the delivery never shipped; the harness's holdout floor applies
- **beats the baseline error rate**: 0.0% on the answered against a recorded first-pass accuracy of 97.0% -- evals/acceptance.md: the baseline's error rate is the number to beat; measured on what the system answered, with the abstained share beside it
- **edge: a valid request**: 422 {"refused": "missing 'pages'", "request_id": "fce6d2a9"} -- the exam's own first case through the edge; refusals alone proved a service that failed every real request

## Notes

- own tests: the deliverable's own smoke and edge tests, model-free
- holdout: sample size: the protocol's floor for a blind sample is 30; the acceptance run itself is sized to the golden set
- generalisation gap: past 20% the golden score describes the exam, not the system; a component that reads the holdout file defeats this row, which is what --external is for
- external exam: a second out-of-sample set (--external <jsonl>), e.g. the client's own later export; a component that memorises the holdout file scores 100% there and single digits here
- edge: identity: no token, no service, with a request id
- edge: forged result: a caller cannot hand the pipeline its own answer
- edge: the answer says why: an answer names what it stood on: scores and carrying tokens, cited evidence, or who decided
- edge: readiness: judged where nothing external is needed; with a model seam it depends on the deployment's endpoint and is reported only
- risk register: scaffolds: a scaffold raises on use; a green exam cannot include it
- risk register: gates waived: reported, not judged: a waiver is the engagement's decision, on the record
- risk register: asserted facts: reported: confirm each with the client before the decisions resting on it stand
