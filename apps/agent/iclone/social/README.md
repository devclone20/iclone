# iCLONE — Public Voice (X / Twitter)

iCLONE's **sandboxed spokesperson** for X. A separate automation from the ACP commerce
stack: it can read mentions, reply, and like — **and nothing else**. It imports no
economic skills, so **no message on X can make iCLONE move funds, trade, or take any
action**. That capability simply does not exist in this process.

> Owner-gated · verified-only replies · on-topic only · anti-jailbreak hardened ·
> default-OFF, with a kill-switch.

---

## The policy (exactly what the owner set)

**Reply** only when **all** hold:
- the tweet **@mentions @icloneframe**, and
- it is a **direct question**, and
- the author is **X-verified** (blue / gold / business / gov), and
- it is **on-topic** (iCLONE / CLONE FRAME / frames / iNFT / $ICLONE / ACP / Virtuals), and
- it **passes the guardrails** (no injection / jailbreak), and
- it has **not** already been answered, and
- we are **under the reply rate limits**.

**Like** only when the tweet is **genuine praise / appreciation** about iCLONE or
CLONE FRAME, is **on-topic**, and is under the like rate limits. Likes are allowed from
**any account** (owner choice); replies stay verified-only.

**Never:** post unprompted, reply to non-verified accounts, engage off-topic, promote
anything unplanned, give financial advice, share non-official links, promise actions,
or reveal internals.

---

## Security architecture (defense-in-depth)

| Layer | What it does |
|---|---|
| **0 · Capability isolation** | This process imports no wallet/ACP/crypto skills. The X surface can only read/reply/like. The strongest mitigation — by design. |
| **1 · Input normalization** | NFKC fold + strip zero-width/invisible chars → defeats obfuscated injections. |
| **2 · Threat detection** | Reuses `SecurityTraining.detect_threat()` + an obfuscation-robust regex layer (role-override, authority-escalation, prompt-extraction, indirect-injection, credential-phishing). |
| **3 · Context shaping** | Incoming tweet is wrapped as **DATA** (spotlighting) before it ever reaches the model. |
| **4 · Topic scope** | Only our project. @mentions are stripped before the topic check so a mention alone never counts as on-topic. |
| **5 · Output policy** | DLP for secrets/keys (fail-closed), banned financial/action phrasing (fail-closed), off-policy links (fail-closed), foreign-mention stripping, 280-char cap. |
| **6 · Owner gating** | `X_ENABLED` master switch + `X_MODE` (dry_run/review/autonomous) + per-hour/day rate limits + full audit log. |

Grounded in current open-source practice: OWASP LLM01, tldrsec/prompt-injection-defenses,
NeMo Guardrails, LLM Guard, Rebuff.

---

## Run

```bash
# offline self-test — no network, no keys (CI-friendly)
PYTHONPATH=. python -m agent.iclone.social.run --doctor

# verify X credentials + detect API tier
PYTHONPATH=. python -m agent.iclone.social.run --verify

# one cycle (dry-run unless X_ENABLED=true + X_MODE=autonomous + creds)
PYTHONPATH=. python -m agent.iclone.social.run --once

# the loop (what systemd runs)
PYTHONPATH=. python -m agent.iclone.social.run
```

Config is environment-driven (`agent/iclone/social/config.py`). Template:
[`ops/social/x.env.example`](../../../ops/social/x.env.example). **Defaults are safe:**
disabled, dry-run, nothing posts until you provide keys and flip `X_ENABLED=true`.

## Deploy (separate automation on the droplet)

```bash
ops/social/deploy_x.sh <DROPLET_IP>          # install, service stays OFF
# → fill /opt/iclone-x/x.env with your X keys
ops/social/deploy_x.sh <DROPLET_IP> enable   # start
ops/social/deploy_x.sh <DROPLET_IP> disable  # kill-switch
ops/social/deploy_x.sh <DROPLET_IP> status   # status + logs
```

Runtime is isolated: state/drafts/audit in `/opt/iclone-x/`, secrets in
`/opt/iclone-x/x.env`, service `iclone-x.service`, logs `/var/log/iclone/x.log`.

> ⚠️ **X API tier:** reading mentions + verified status requires **Basic ($100/mo)+**.
> On **Free tier** the engine authenticates and idles safely (reads return 403 → it
> disables the read loop and logs it) — it will not misfire. Upgrade to activate fully.
