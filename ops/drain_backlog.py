#!/usr/bin/env python3
"""
Drain the client-side backlog FAST. For every non-terminal job where this agent
is the client, blind-try `client fund` (succeeds only if it's budget_set; harmless
error otherwise), then blind-try `client complete` (succeeds only if submitted).
No per-job history lookup — half the acp spawns, much lighter on a 1-vCPU box.

Run with: python3 -u drain_backlog.py   (unbuffered, line-by-line progress)
Usage: ACP_CONFIG_DIR=<dir> python3 -u drain_backlog.py
"""
import json, subprocess, os, sys
CFG = os.environ["ACP_CONFIG_DIR"]
ENV = {**os.environ, "ACP_CONFIG_DIR": CFG}
CHAIN = "8453"

def acp(*a, t=60):
    try:
        r = subprocess.run(["acp", *a], capture_output=True, text=True, timeout=t, env=ENV)
        return (r.stdout.strip() or r.stderr.strip()), r.returncode
    except subprocess.TimeoutExpired:
        return "TIMEOUT", 1

def out(s):
    print(s, flush=True)

mine = json.loads(open(CFG + "/config.json").read()).get("activeWallet", "").lower()
o, rc = acp("job", "list", "--json")
jobs = json.loads(o).get("jobs", []) if rc == 0 else []
client_jobs = [j for j in jobs if j.get("clientAddress", "").lower() == mine
               and (j.get("jobStatus", "") or "").lower() not in ("completed", "rejected", "expired", "cancelled")]
out(f"wallet={mine[:10]} total={len(jobs)} client_active={len(client_jobs)}")

funded = completed = 0
for j in client_jobs:
    jid = str(j.get("onChainJobId", ""))
    o, rc = acp("client", "fund", "--job-id", jid, "--chain-id", CHAIN)
    if rc == 0 or "funded" in o.lower():
        funded += 1
        out(f"  fund {jid}: OK")
        continue
    o2, rc2 = acp("client", "complete", "--job-id", jid, "--chain-id", CHAIN)
    if rc2 == 0 or "completed" in o2.lower():
        completed += 1
        out(f"  complete {jid}: OK")
    else:
        out(f"  skip {jid} (not fundable/completable)")
out(f"DONE funded={funded} completed={completed}")
