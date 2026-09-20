# Scorecard

**1 of 7 measured properties hold.** Measured on `/Users/atulkapoor/Documents/fde-demo-receipts/project`. A property this build cannot measure is marked n/a, never counted as held. The service was booted on the machine that ran this card, not inside the deployed unit; the out-of-sample rows (holdout, external exam, generalisation gap, the baseline's bar) are the fitness rows, the rest are self-consistency.

| Property | Measured | Holds |
|---|---|---|
| own tests | no tests/ directory | **no** |
| lint | [*] 1 fixable with the `--fix` option (6 hidden fixes can be enabled with the `--unsafe-fixes` option). | **no** |
| exam | the harness wrote no report | **no** |
| exam record | no evals/manifest.json | **no** |
| holdout | the harness wrote no report | **no** |
| external exam | not given | n/a |
| edge | no app/service.py | n/a |
| risk register: scaffolds | none | yes |
| risk register: gates waived | none | n/a |
| risk register: asserted facts | 0 boundary-bearing fact(s) asserted | n/a |
| environment | no deploy/env.example | **no** |
| training path | none in this build | n/a |
| regression from the last card | no previous card | n/a |

## Not holding

- **own tests**: no tests/ directory -- the deliverable ships none
- **lint**: [*] 1 fixable with the `--fix` option (6 hidden fixes can be enabled with the `--unsafe-fixes` option).
- **exam**: the harness wrote no report -- usage: harness.py [-h] [--min-score MIN_SCORE] [--cases CASES]
harness.py: error: unrecognized arguments: --report /Users/atulkapoor/Documents/fde-demo-receipts/project/scorecard-harness.json --allow-uncalibrated

- **exam record**: no evals/manifest.json -- the split seed, share and digests of every eval file
- **holdout**: the harness wrote no report
- **environment**: no deploy/env.example

## Notes

- external exam: a second out-of-sample set (--external <jsonl>), e.g. the client's own later export; a component that memorises the holdout file scores 100% there and single digits here
- risk register: scaffolds: a scaffold raises on use; a green exam cannot include it
- risk register: gates waived: reported, not judged: a waiver is the engagement's decision, on the record
- risk register: asserted facts: reported: confirm each with the client before the decisions resting on it stand
