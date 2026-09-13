# Service objectives

Two buckets, because reporting one is half a story. A technical number nobody outside the team cares about, and a business number nobody inside it can move directly -- and a system healthy on the first while the second does not move is a system nobody will renew.

## Technical

- **Latency** — p95 under 30000ms at expected peak. Measured at the edge, not inside a component, because that is where somebody experiences it.
- **Availability** — business hours: planned windows outside them are free.
- **Evaluation score** — the golden layer at or above the threshold CI gates on. A drop here is a regression whether or not anything is down.
- **Adversarial score** — tracked separately and never averaged in. Scoring well on golden and badly on adversarial means nobody has attacked it yet.

## Business

- **The thing that should move** — stated by whoever asked for this, in their words, before it was built. If nobody can say what should change, that is the finding.

## Baseline

**Captured.** The numbers to beat, by their recorded definitions:

- **volume** — 850 receipts/month (receipts submitted for reimbursement (demo scenario figure, labelled simulated in the demo README))
- **cycle_time_per_unit_seconds** — 180 s (submission to keyed-in, per receipt, hand-keying (scenario))
- **labour_hours_per_week** — 20 h/week (finance assistant keying time (scenario))
- **rework_rate** — 0.08 ratio (entries corrected after posting (scenario))
- **exception_rate** — 0.05 ratio (receipts routed to a person for judgement (scenario))
- **error_rate** — 0.03 ratio (wrong company, date or total posted (scenario))
- **business_metric** — 6 days (mean days from submission to reimbursement (scenario))
- sampled: n=40, demo engagement on the public SROIE corpus; operational figures are a stated scenario, extraction ground truth is the dataset's human annotation

Re-measure by identical definitions in 60 days. A comparison that quietly changes a definition is a comparison with its thumb on the scale.
