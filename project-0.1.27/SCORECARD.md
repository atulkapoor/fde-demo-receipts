# Scorecard

**17 of 22 measured properties hold.** Measured on `/Users/atulkapoor/Documents/fde-demo-receipts/project-0.1.27`. A property this build cannot measure is marked n/a, never counted as held. The service was booted on the machine that ran this card, not inside the deployed unit; the out-of-sample rows (holdout, external exam, generalisation gap, the baseline's bar) are the fitness rows, the rest are self-consistency.

| Property | Measured | Holds |
|---|---|---|
| own tests | 1 failed, 6 passed in 1.27s | **no** |
| lint | No fixes available (1 hidden fix can be enabled with the `--unsafe-fixes` option). | **no** |
| exam: golden | 81.8% on 77 cases | yes |
| exam: edge_case | 85.7% on 7 cases | yes |
| exam: adversarial | 100.0% on 10 cases (0 followed, 0 on misread bases) | yes |
| exam: verdict | green | yes |
| exam record | every eval file matches its recorded digest | yes |
| holdout | 56.7% on 30 cases | yes |
| holdout: sample size | 30 cases | yes |
| holdout: the file on record | matches evals/manifest.json | yes |
| generalisation gap | golden 81.8% - holdout 56.7% = +25.2% | **no** |
| beats the baseline error rate | 56.7% on the answered against a recorded first-pass accuracy of 97.0% | **no** |
| external exam | not given | n/a |
| edge: boots | answers /health | yes |
| edge: identity | 401 without a token | yes |
| edge: forged result | 422 | yes |
| edge: forged identity | 422 | yes |
| edge: malformed body | 400 | yes |
| edge: a valid request | 200 {"company": "SYL ROASTED DELIGHTS SDN. BHD.", "date": "06/03 | yes |
| edge: the answer says why | no | **no** |
| edge: readiness | 200 ready | n/a |
| risk register: scaffolds | none | yes |
| risk register: gates waived | none | n/a |
| risk register: asserted facts | 2 boundary-bearing fact(s) asserted | n/a |
| environment | every variable the code reads is documented | yes |
| training path | none in this build | n/a |
| regression from the last card | none | yes |

## Not holding

- **own tests**: 1 failed, 6 passed in 1.27s -- the deliverable's own smoke and edge tests, model-free
- **lint**: No fixes available (1 hidden fix can be enabled with the `--unsafe-fixes` option).
- **generalisation gap**: golden 81.8% - holdout 56.7% = +25.2% -- past 20% the golden score describes the exam, not the system; a component that reads the holdout file defeats this row, which is what --external is for
- **beats the baseline error rate**: 56.7% on the answered against a recorded first-pass accuracy of 97.0% -- evals/acceptance.md: the baseline's error rate is the number to beat; measured on what the system answered, with the abstained share beside it
- **edge: the answer says why**: no -- an answer names what it stood on: scores and carrying tokens, cited evidence, or who decided

## Notes

- exam: verdict: the harness's own exit status at --min-score 0.0
- holdout: cases the delivery never shipped; the harness's holdout floor applies
- holdout: sample size: the protocol's floor for a blind sample is 30; the acceptance run itself is sized to the golden set
- external exam: a second out-of-sample set (--external <jsonl>), e.g. the client's own later export; a component that memorises the holdout file scores 100% there and single digits here
- edge: identity: no token, no service, with a request id
- edge: forged result: a caller cannot hand the pipeline its own answer
- edge: a valid request: the exam's own first case through the edge; refusals alone proved a service that failed every real request
- edge: readiness: judged where nothing external is needed; with a model seam it depends on the deployment's endpoint and is reported only
- risk register: scaffolds: a scaffold raises on use; a green exam cannot include it
- risk register: gates waived: reported, not judged: a waiver is the engagement's decision, on the record
- risk register: asserted facts: reported: confirm each with the client before the decisions resting on it stand
- regression from the last card: tolerance 2%
