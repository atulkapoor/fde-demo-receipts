# fde-demo-receipts

> **The deliverable is in this repo**: [`project/`](project/) — the emitted, implemented, deployable output (pipeline service, deploy assets, runbooks, evals, ARCHITECTURE.md, RISKS.md). Start at [`project/README.md`](project/README.md).

A complete engagement run through [fde-framework](https://github.com/atulkapoor/fde-framework)
on real data — 626 scanned retail receipts from the public
[SROIE](https://github.com/zzzDavid/ICDAR-2019-SROIE) corpus (ICDAR 2019),
each with human-verified labels for company, date, address and total.

Nothing here is staged. Every refusal, every guardrail trip, and every bug
the run surfaced is preserved below, because the refusals are the product.

## The run, in numbers

| Stage | Result |
|---|---|
| Gates | 7/7 passed on real evidence — data access recorded against a sqlite store that returned 626 real rows; baseline recorded (operational figures are a stated scenario, labelled as such; extraction ground truth is the dataset's human annotation) |
| Build | 84 golden + 2 adversarial cases from verified labels; on-prem topology; fully deterministic architecture chosen first — `llm-extraction` rejected on the record: *"deterministic is simpler and applies here"* |
| Implement, attempt 1 | Agent went green on a 42-case golden set — **holdout (20 unseen receipts): 30%**. The loop refused: *"green golden, red holdout — the golden file may have been memorized; not accepting this."* Forensics: no hardcoded answers; the agent had overfit its rules to the receipts it could see |
| Implement, attempt 2 | Diverse exam (84 golden spread across the corpus, 30-receipt disjoint holdout, 85% bar): agent reached **73.8% golden / 33.3% holdout** and plateaued; the bounded loop stopped at its round cap |
| The measurement | The plateau *is* the answer to the question the architecture document had flagged under "Assumptions": `cheap_path_coverage`. Recorded as 0.33 |
| The flip | Rebuild: representation flips **deterministic → llm-extraction**, with the old choice and the measured reason preserved in the rejection record. Same facts, same fingerprint discipline — one measured number changed the design, and the documents say which and why |

## What the run found in the framework itself

Using the product honestly found and shipped two releases the same day:

- **0.1.6** — `fde build <bare-name>` silently emitted a project with an
  empty golden set while sixty verified pairs sat on disk (the harness's
  empty-exam refusal was the net that caught it). The build receipt now
  counts its own exam.
- **0.1.7** — the implement fence flagged Python's own `__pycache__`
  bytecode as "the agent edited the exam", stopping every real loop at
  round 1. The fence now guards against the agent, not the interpreter.
- Logged for 0.1.8: the loop's default green bar is CI's `--min-score 0.0`,
  so a half-finished implementation can reach the holdout, whose verdict
  then overstates ("memorized") what is sometimes just "not finished" —
  the verdict should be relative to the golden score.

## Reproduce it

Everything regenerates from public sources — no data is redistributed here.

```bash
git clone --depth 1 https://github.com/zzzDavid/ICDAR-2019-SROIE.git dataset
python3 prepare.py               # pairs.jsonl, holdout.jsonl, receipts.db from the dataset

python3.12 -m venv venv && venv/bin/pip install "fde-framework==0.1.7"
venv/bin/fde start receipts --statement "Extract company, date, address and total from scanned retail receipts; 626 receipts with labelled ground truth; data stays on this machine; a finance assistant waits on each receipt."
venv/bin/fde ask receipts --role admin       # then eval_owner, then user
venv/bin/fde samples receipts --file engagement-prep/pairs.jsonl
cp engagement-prep/holdout.jsonl engagements/receipts/artifacts/holdout.jsonl
venv/bin/fde scan receipts
venv/bin/fde baseline receipts --file engagements/receipts/baseline.yaml
venv/bin/fde data-access receipts --note "sqlite receipts.db: SELECT returned 626 real rows"
venv/bin/fde security-review receipts --note "self-review for the public demo"
venv/bin/fde build receipts --out project
venv/bin/fde implement project --holdout engagements/receipts/artifacts/holdout.jsonl \
  --max-rounds 6 --check "python evals/harness.py --min-score 0.85"
```

**The deliverable itself is committed under [`project/`](project/)** — the
emitted, agent-implemented production output: `app/` at its measured
72.6/50.0 state, `deploy/`, `ops/` (runbook, diagnosis walk, SLOs),
`ARCHITECTURE.md` with every rejection, `RISKS.md` with the waiver. Only
the case files regenerate (they embed dataset text).

The recorded interview answers, the baseline, and the implement round logs
are all in this repository (`engagements/`, `implement-run*.log`).

## The model path, measured (added after Ollama arrived)

The flipped architecture ran against a local model — `qwen3:0.6b`, the
smallest one on the machine, deliberately: measure first, upgrade on
evidence. Same 84-case exam, same 30 unseen receipts:

| Path | Golden | Holdout (unseen) |
|---|---|---|
| Rules, agent-tuned to plateau | 73.8% | 33.3% |
| Model (qwen3:0.6b), agent-built pipeline | 72.6% | **50.0%** |

Then the agent did something better than passing: **it audited its own
exam and proved the exam caps below the bar.** Its analysis
([`project/ops/golden-ceiling.md`](project/ops/golden-ceiling.md)) claims
23 of the 84 golden cases carry label values that do not exist verbatim in
their own OCR input — SROIE's annotations reassemble addresses differently
than the scans read. We re-derived the claim independently, byte by byte:
**confirmed.** Under the copy-only injection defence (no invented values,
ever), the metric-level optima are 61/84 golden and 17/30 holdout
(verbatim-substring bound; the implementation's own audit derives 16/30
under its stricter copy rules — either way the model's 15 sits at 88–94%
of achievable). Recompute the table against what is achievable:

| Path | Golden, of achievable | Holdout, of achievable |
|---|---|---|
| Rules | 62/61 — past the optimum only by *transforming* text, which is what the injection defence forbids | 10/17 (59%) |
| Model (qwen3:0.6b) | **61/61 — the exam's maximum** | **15/17 (88%)** |

Three findings the corrected numbers force:

1. **The model didn't plateau — it maxed the exam.** Seven rounds ended
   at the provable optimum, and the loop's refusal to call that "done"
   was the exam's defect, not the model's.
2. **The holdout still separates them.** 88% vs 59% of achievable on
   receipts neither ever saw: the rules memorized structure, the model
   generalized.
3. **A canonical benchmark's ground truth disagrees with its own inputs
   in ~27% of sampled cases** — surfaced by an exact-match exam, claimed
   by the implementing agent, verified independently. This is
   `ops/diagnosis.md` §1 (a definitions problem wearing a model-error
   costume) happening on a famous public dataset.

This run also improved the framework twice more: an agent round that
outlives its budget is now a round result with `--agent-timeout`, never
a traceback, and the emitted judge learned to speak discrete verdicts.

## Where it stopped originally — before Ollama arrived

The flipped architecture calls a model, and the engagement's boundary says
data cannot leave — so the emitted `app/llm.py` refuses hosted APIs and
wants a **local** OpenAI-compatible endpoint. `fde scan` had already
recommended the runtime for this machine: Ollama on 17GB of unified
memory. Ollama was not installed on the demo machine, so the run concludes
here — exactly where a real engagement would pause for an infrastructure
decision, with the requirement written down instead of worked around.

The documented next step, for anyone (or us, later):

```bash
brew install ollama && ollama pull qwen3.5:9b
export LLM_ENDPOINT=http://localhost:11434
venv/bin/fde build receipts --out project
venv/bin/fde implement project --holdout engagements/receipts/artifacts/holdout.jsonl \
  --max-rounds 6 --check "python evals/harness.py --min-score 0.85"
# then: deploy via project/deploy, run project/ops/runbook.md, and
# fde retro after the measurement window
```

## Transcripts, verbatim

The refusal that starts the story — `fde build` before the gates:

```
[hard] data_access: Credentials have not been shown to work against real data.
    -> Get a connection that returns real rows, even a handful, then record it:
       `fde data-access <eng> --note "what returned rows"`. Promised access is not access.
...
refused: gates above are unsatisfied. Soft gates take `fde waive <gate> --reason`;
data access has no workaround, only credentials that return real rows.
```

The flip, as the decision record wrote it — one measured number ruled the
old choice out, by name:

```
**representation**
- `deterministic` -- ruled out by cheap_path_coverage < 0.95
```

And the model path's honest end — the loop refusing to call 72.6% done:

```
round 7: red

stopped by: round cap. Log: ops/implement-log.md
exit: 1
```

## Honesty notes

- The operational baseline figures (volume, cycle time, labour hours) are a
  stated scenario, labelled as such in `baseline.yaml` — a demo cannot
  measure a client's back office. The extraction ground truth is real:
  SROIE's human annotations.
- This demonstrates the machinery end to end on real data. It is not a
  production engagement: the framework's own status stays
  **built, demonstrated, unproven** until a client engagement runs
  start to finish with a measured before/after.
- Scoring is `field_exact_match` on OCR'd text — an unforgiving metric on
  noisy receipts, chosen because it is the framework's default for
  structured output, not because it flatters the numbers.
- **Holdout scope, precisely**: the holdout was never shown to the
  implementing agent during the loop. The shipped audit document
  (`project/ops/golden-ceiling.md`) examined both files post-hoc, and one
  implementation constant (`LINE_CHARS`) was verified against both — so
  the honest claim is "held out from the agent", not "never examined by
  anyone". The audit quotes holdout values; that is disclosed here.
- **The model's 15/30 sits exactly on the harness's 0.5 holdout floor** —
  a framework constant since v0.1.7, not a bar tuned for this repo. One
  more miss and the loop would have printed "memorized".
- "No data is redistributed" needs precision after committing the
  deliverable: the corpus is not included and regenerates from the public
  mirror, but individual receipt texts do appear inside the committed
  project — the adversarial probe and the few-shot examples the agent
  chose. SROIE is a public research corpus of shop receipts; nothing
  personal, and the claim now says exactly what is true.
