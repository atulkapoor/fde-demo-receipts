# Where the failure lives

An unclear definition can look like a model error. Missing evidence can look like weak reasoning. A tool timeout can look like a capability limit. The expensive habit is re-prompting or switching models before finding which layer actually failed -- so this walks the layers in order, cheapest to check first, the model last.

## 1. Definitions

**Check** — take the failing case to whoever owns evaluation and ask what the right output is. If two people who should know disagree, stop here: no layer below this one can settle a question the client has not.

**If it is this** — the fix is a decision, recorded in the golden cases, not a change to any code. Disagreement here is a discovery finding, and surfacing it is this system working.

## 2. Tools

**Check** — the audit trail around the failing request, for timeouts, error returns and empty results from outward calls. A tool that failed quietly upstream reads as a reasoning failure downstream.

**If it is this** — fix the call or its timeout, and make the failure loud: a tool error the model narrates around is worse than one that stops the run.

## 3. The model -- only now

**Check** — the evaluation's error breakdown, with everything above ruled out. One field dominating usually means a mapping to fix; failures spread across fields mean a capability limit.

**If it is this** — change the prompt before changing the model, one change at a time, re-running the evaluation after each. An improvement nobody measured is a mood.
