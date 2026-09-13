# Deployment

Topology: **on-prem**  
Substrate: **systemd-unit**  
Provisioning: **ansible-playbook**

Neither of these is a default. The substrate is a ladder and this is the rung the profile earned; the provisioner follows what the team already operates, whether there is an API to call, and whether this environment has to be destroyed cleanly.

The reasoning for each is in `ARCHITECTURE.md`, alongside what was rejected and why.

## What the service needs from its environment

Configuration is environment, not code, so these are set in the unit rather
than committed. The first one is not optional: the representation component
is `llm-extraction` and it does not guess when the model is absent.

| Variable | What it is | Default |
|---|---|---|
| `LLM_ENDPOINT` | An OpenAI-compatible server **on this machine or network** -- the data cannot leave, so `app/llm.py` refuses the hosted path outright. | none; extraction fails loudly without it |
| `LLM_MODEL` | The model name that endpoint serves. | `default`, which most servers do not have -- set it |
| `RECEIPTS_LEDGER` | Where a submission is recorded: the finance system's own store, or a file inside the boundary. | `var/submissions.sqlite3` beside the app |
| `FDE_OPERATOR` | Who the audit names for the submissions this service records. | the process owner; the approval gate refuses when neither is answerable |

`ReadWritePaths` in the unit has to include the ledger's directory, and the
ledger is state: it is what makes a retry a no-op rather than a second
submission, so it belongs in the backup set.
