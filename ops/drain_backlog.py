#!/usr/bin/env python3
"""
Drain the client-side backlog: fund every budget_set job and complete every
submitted job where the given agent is the CLIENT. Uses job history for the
TRUE status (acp job list reports budget_set as "open").

Usage: ACP_CONFIG_DIR=<dir> python3 drain_backlog.py
"""
import json, subprocess, os, sys
CFG = os.environ["ACP_CONFIG_DIR"]
ENV = {**os.environ, "ACP_CONFIG_DIR": CFG}
CHAIN = "8453"

def acp(*a, t=90):
    r = subprocess.run(["acp", *a], capture_output=True, text=True, timeout=t, env=ENV)
    return (r.stdout.strip() or r.stderr.strip()), r.returncode

def status(jid):
    o, _ = acp("job", "history", "--job-id", str(jid), "--chain-id", CHAIN)
    if not o: return None
    p = o.splitlines()[0].split("\t")
    return p[1].strip().lower() if len(p) > 1 else None

mine = json.loads(open(CFG + "/config.json").read()).get("activeWallet", "").lower()
out, rc = acp("job", "list", "--json")
jobs = json.loads(out).get("jobs", []) if rc == 0 else []
client_jobs = [j for j in jobs if j.get("clientAddress", "").lower() == mine]
print(f"wallet={mine[:10]} | total={len(jobs)} | as_client={len(client_jobs)}")

funded = completed = skipped = 0
for j in client_jobs:
    jid = str(j.get("onChainJobId", ""))
    st = status(jid)
    if st in ("budget_set", "budgetset"):
        o, rc = acp("client", "fund", "--job-id", jid, "--chain-id", CHAIN)
        ok = rc == 0 or "funded" in o.lower()
        funded += ok
        print(f"  fund {jid}: {'OK' if ok else 'FAIL '+o[:80]}")
    elif st == "submitted":
        o, rc = acp("client", "complete", "--job-id", jid, "--chain-id", CHAIN)
        ok = rc == 0 or "completed" in o.lower()
        completed += ok
        print(f"  complete {jid}: {'OK' if ok else 'FAIL '+o[:80]}")
    else:
        skipped += 1
print(f"DONE — funded={funded} completed={completed} skipped(other/expired)={skipped}")
