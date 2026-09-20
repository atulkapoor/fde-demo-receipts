# Deployment

Topology: **on-prem**  
Substrate: **systemd-unit**  
Provisioning: **ansible-playbook**

Neither of these is a default. The substrate is a ladder and this is the rung the profile earned; the provisioner follows what the team already operates, whether there is an API to call, and whether this environment has to be destroyed cleanly.

The reasoning for each is in `ARCHITECTURE.md`, alongside what was rejected and why.

## Install

The playbook is the installer -- it creates everything the unit
expects (service account, venv, state dir, env file):

```bash
# hosts go in deploy/ansible/inventory.ini first
ansible-playbook -i deploy/ansible/inventory.ini deploy/ansible/site.yml
```

Then prove it from the host:

```bash
curl -s localhost:8080/health   # liveness: the process answers
curl -s localhost:8080/ready    # readiness: dependencies answer
journalctl -u app -n 20 --no-pager
```
