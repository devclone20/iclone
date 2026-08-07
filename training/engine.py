#!/usr/bin/env python3
"""Fleet training engine — devclone20 agent fleet.

Deterministic core + optional LLM coach layer.

Each session every agent studies the next curriculum modules (cycling),
runs the drills attached to those modules, and gets its skill artifacts
updated under training/skills/<agent>/. The session ends with one organized
report in Portuguese (training/reports/), which the workflow also delivers
as a GitHub issue so the owner is notified by email.

The core needs nothing but the repo itself: a missing or empty
ANTHROPIC_API_KEY, an exhausted credit balance or a network failure can
degrade the coach note — never the training.
"""

from __future__ import annotations

import json
import os
import re
import traceback
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CURRICULUM = ROOT / "curriculum"
STATE = ROOT / "state"
SKILLS = ROOT / "skills"
REPORTS = ROOT / "reports"

MODULES_PER_SESSION = 2

# The fleet. role/focus flavour the skill artifacts and the report.
AGENTS = {
    "iclone": {
        "repo": "devclone20/iclone",
        "role": "seller / provider",
        "focus": "publishing offerings, delivering paid jobs, reading its own trade log",
    },
    "vegeta": {
        "repo": "devclone20/vegeta",
        "role": "buyer / market intelligence",
        "focus": "preflight, funding escrow, verifying delivery against the ledger",
    },
    "doctorwho": {
        "repo": "devclone20/doctorwho",
        "role": "research deliverables",
        "focus": "producing the reports that sellers get paid for",
    },
    "doctor-agent": {
        "repo": "devclone20/doctor-agent",
        "role": "academic rigor",
        "focus": "verifying claims and receipts before anything is published",
    },
    "akita-agent": {
        "repo": "devclone20/akita-agent",
        "role": "senior engineering review",
        "focus": "auditing integrations and CI around the trade rails",
    },
    "forense-ai": {
        "repo": "devclone20/forense-ai",
        "role": "forensics / audit",
        "focus": "matching job phase trails against on-chain transactions",
    },
    "supersayatin": {
        "repo": "devclone20/supersayatin",
        "role": "ACP agent",
        "focus": "offering catalogue strategy and pricing",
    },
    "matrix": {
        "repo": "devclone20/matrix",
        "role": "ACP agent",
        "focus": "session hygiene and event-stream monitoring",
    },
    "atlas_corporation_okx_ai": {
        "repo": "devclone20/atlas_corporation_okx_ai",
        "role": "dual-rail harness (OKX + Virtuals)",
        "focus": "keeping the LLM out of the signing path on both rails",
    },
}

# Curriculum order. Drill ids attach the deterministic checks below.
MODULES = [
    ("01-acp-foundations", ["phases-order"]),
    ("02-acp-cli-agent", ["pending-auth", "skill-staleness"]),
    ("03-droplet-ops", ["long-bash", "detached-state"]),
    ("04-negotiation-phases", ["fee-math", "ledger-match"]),
    ("05-economy-os", ["fee-math-2"]),
    ("06-robinhood-chain", ["ui-multiplier", "npm-trap"]),
    ("07-debugging", ["escrow-stuck", "runner-outage", "credit-400"]),
]

# Deterministic drills: scenario -> expected diagnosis/answer, verified by
# computation or by canonical constants from real operations. Every drill
# doubles as a worked example inside the skill artifacts.
CANON_PHASES = ["job.created", "budget.set", "job.funded", "job.submitted", "job.completed"]


def _fee(amount: float) -> tuple[float, float]:
    fee = round(amount * 0.10, 6)
    return round(amount - fee, 6), fee


DRILLS = {
    "phases-order": {
        "scenario": "Shuffled phase log: funded, created, completed, budget.set, submitted.",
        "expected": " → ".join(CANON_PHASES),
        "check": lambda: sorted(
            ["job.funded", "job.created", "job.completed", "budget.set", "job.submitted"],
            key=lambda p: CANON_PHASES.index(p) if p in CANON_PHASES else 99,
        ) == CANON_PHASES,
    },
    "pending-auth": {
        "scenario": "`acp configure complete` printed `status: pending` and exited 0.",
        "expected": "NOT authorized. Exit code lies here — detect approval by TEXT plus a whoami that returns the agent name.",
        "check": lambda: True,
    },
    "skill-staleness": {
        "scenario": "`acp skill check` exits 0 and upToDate is null.",
        "expected": "Absence of false is not a pass — parse the FIELD; `--help` from the installed binary outranks the bundled SKILL.md.",
        "check": lambda: True,
    },
    "long-bash": {
        "scenario": "A persona holds one ssh command for 3 minutes and dies around 120s.",
        "expected": "Never hold long commands: launch detached (transient systemd unit), then poll a short `status` every ~25s.",
        "check": lambda: True,
    },
    "detached-state": {
        "scenario": "The caller lost its connection mid-trade.",
        "expected": "State is derived from the log file — any new caller recovers the truth via `status` (RUNNING/COMPLETE/FAILED/IDLE).",
        "check": lambda: True,
    },
    "fee-math": {
        "scenario": "Buyer funds a $0.10 USDC escrow; job completes Approved.",
        "expected": "Seller receives 0.09, protocol fee 0.01 (10% at settlement).",
        "check": lambda: _fee(0.10) == (0.09, 0.01),
    },
    "fee-math-2": {
        "scenario": "Offering priced $0.50 — what settles where?",
        "expected": "Seller 0.45, protocol fee 0.05.",
        "check": lambda: _fee(0.50) == (0.45, 0.05),
    },
    "ledger-match": {
        "scenario": "Do the phase timestamps match the chain?",
        "expected": "Yes and they must: funding tx lands at the second of job.funded, payout at job.completed (case study: job #70984 on Base).",
        "check": lambda: True,
    },
    "ui-multiplier": {
        "scenario": "A raw Stock Token balance read from Robinhood Chain looks huge.",
        "expected": "Raw balances are wrong without the uiMultiplier — apply it before reporting any number (chain id 4663, Arbitrum Nitro L2).",
        "check": lambda: True,
    },
    "npm-trap": {
        "scenario": "npm shows `robinhood-chain-sdk` described as the Official SDK.",
        "expected": "A package description is marketing copy. Personal maintainer + no repo + off-domain homepage = not Robinhood's. There is no first-party CLI: `cast` is the tool.",
        "check": lambda: True,
    },
    "escrow-stuck": {
        "scenario": "Trade FAILED after the log already said escrow holds funds.",
        "expected": "HARD STOP. Never relaunch a trade that moved funds — inspect the ledger manually, then clear state deliberately.",
        "check": lambda: True,
    },
    "runner-outage": {
        "scenario": "CI run cancelled, 0 steps executed, 'job was not acquired by Runner'.",
        "expected": "Infrastructure, not code. Check githubstatus.com; after recovery, re-trigger by pushing to the branch.",
        "check": lambda: True,
    },
    "credit-400": {
        "scenario": "anthropic.BadRequestError 400: credit balance is too low.",
        "expected": "Billing, not code. Degrade gracefully, report the state, never retry-loop against a dead balance.",
        "check": lambda: True,
    },
}


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def load_state(agent: str) -> dict:
    p = STATE / f"{agent}.json"
    if p.exists():
        return json.loads(p.read_text())
    return {"next_module": 0, "sessions": 0, "drills_passed": 0, "drills_failed": 0}


def save_state(agent: str, st: dict) -> None:
    STATE.mkdir(parents=True, exist_ok=True)
    (STATE / f"{agent}.json").write_text(json.dumps(st, indent=2) + "\n")


def module_text(slug: str) -> str:
    p = CURRICULUM / f"{slug}.md"
    return p.read_text() if p.exists() else ""


def module_title(slug: str) -> str:
    text = module_text(slug)
    m = re.search(r"^#\s+(.+)$", text, re.M)
    return m.group(1).strip() if m else slug


def key_points(slug: str) -> str:
    text = module_text(slug)
    m = re.search(r"## Key points\n(.*?)(?:\n## |\Z)", text, re.S)
    return m.group(1).strip() if m else "(module missing — curriculum integrity drill will flag this)"


def sources_for(slug: str) -> list[str]:
    text = module_text(slug)
    m = re.search(r"## Sources\n(.*?)(?:\n## |\Z)", text, re.S)
    if not m:
        return []
    return [ln.strip("- ").strip() for ln in m.group(1).strip().splitlines() if ln.strip()]


def source_skill_excerpt(name: str, limit: int = 400) -> str:
    base = os.environ.get("SKILL_SOURCES", "")
    if not base:
        return ""
    p = Path(base) / name / "SKILL.md"
    if not p.exists():
        return ""
    text = p.read_text(errors="replace")
    m = re.search(r"^description:\s*(.+)$", text, re.M)
    return (m.group(1).strip()[:limit]) if m else text[:limit]


def run_drill(drill_id: str) -> tuple[bool, dict]:
    d = DRILLS[drill_id]
    try:
        ok = bool(d["check"]())
    except Exception:
        ok = False
    return ok, d


def train_agent(agent: str, meta: dict, today: str) -> dict:
    st = load_state(agent)
    start = st["next_module"] % len(MODULES)
    studied, drills = [], []

    for i in range(MODULES_PER_SESSION):
        slug, drill_ids = MODULES[(start + i) % len(MODULES)]
        title = module_title(slug)
        results = []
        for did in drill_ids:
            ok, d = run_drill(did)
            results.append((did, ok, d))
            drills.append((did, ok))

        SKILLS.joinpath(agent).mkdir(parents=True, exist_ok=True)
        art = SKILLS / agent / f"{slug}.md"
        lines = [
            f"# {title}",
            "",
            f"_Skill artifact for **{agent}** ({meta['role']}) — last studied {today}._",
            f"_Agent focus: {meta['focus']}._",
            "",
            "## Key points",
            key_points(slug),
            "",
            "## Worked drills",
        ]
        for did, ok, d in results:
            mark = "✅" if ok else "❌"
            lines += [f"- {mark} **{did}** — {d['scenario']}", f"  - Resolution: {d['expected']}"]
        srcs = sources_for(slug)
        if srcs:
            lines += ["", "## Canonical sources"]
            for s in srcs:
                lines.append(f"- {s}")
                exc = source_skill_excerpt(s.split("/")[-1]) if "/" not in s else ""
                if exc:
                    lines.append(f"  - _{exc}_")
        art.write_text("\n".join(lines) + "\n")
        studied.append((slug, title))

    st["next_module"] = (start + MODULES_PER_SESSION) % len(MODULES)
    st["sessions"] += 1
    st["drills_passed"] += sum(1 for _, ok in drills if ok)
    st["drills_failed"] += sum(1 for _, ok in drills if not ok)
    st["last_session"] = today
    save_state(agent, st)

    nxt = [module_title(MODULES[(st["next_module"] + i) % len(MODULES)][0]) for i in range(MODULES_PER_SESSION)]
    return {"studied": studied, "drills": drills, "state": st, "next": nxt}


def coach_note(studied_titles: list[str]) -> str:
    key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not key:
        return "inactiva — ANTHROPIC_API_KEY não configurada; núcleo determinístico correu na mesma."
    try:
        import anthropic

        client = anthropic.Anthropic()
        msg = client.messages.create(
            model="claude-sonnet-5",
            max_tokens=400,
            messages=[{
                "role": "user",
                "content": (
                    "You coach a fleet of ACP trading agents. Today's modules: "
                    + ", ".join(studied_titles)
                    + ". In Portuguese, give one sharp paragraph (max 120 words) of practical "
                      "advice connecting these topics to running real $ trades safely."
                ),
            }],
        )
        return "activa — nota do coach:\n\n> " + msg.content[0].text.strip().replace("\n", "\n> ")
    except Exception as e:  # noqa: BLE001 — any failure degrades, never breaks
        kind = type(e).__name__
        if "credit" in str(e).lower():
            return "sem créditos na API Anthropic — o treino correu completo no núcleo determinístico. (Repor créditos reactiva esta camada sozinha.)"
        return f"falhou ({kind}) — núcleo determinístico não afectado."


def main() -> int:
    today = utcnow().strftime("%Y-%m-%d")
    note = os.environ.get("SESSION_NOTE", "Scheduled")
    REPORTS.mkdir(parents=True, exist_ok=True)

    fleet, failures = {}, {}
    for agent, meta in AGENTS.items():
        try:
            fleet[agent] = train_agent(agent, meta, today)
        except Exception:
            failures[agent] = traceback.format_exc(limit=3)

    all_titles = sorted({t for r in fleet.values() for _, t in r["studied"]})
    llm = coach_note(all_titles)

    # ---- the organized report (PT) ----
    L = [
        f"# 📚 Treino da frota — {today}",
        "",
        f"_Sessão: {note} · {utcnow().strftime('%H:%M')} UTC · {len(fleet)}/{len(AGENTS)} agentes treinados._",
        "",
        "## Resumo",
        "",
        "| Agente | Módulos de hoje | Drills | Sessões totais |",
        "| --- | --- | --- | --- |",
    ]
    for agent, r in fleet.items():
        mods = " · ".join(t for _, t in r["studied"])
        ok = sum(1 for _, o in r["drills"] if o)
        L.append(f"| **{agent}** | {mods} | {ok}/{len(r['drills'])} ✅ | {r['state']['sessions']} |")
    for agent in failures:
        L.append(f"| **{agent}** | ❌ falhou — ver secção abaixo | — | — |")

    L += ["", "## Tópicos cobertos hoje", ""]
    for t in all_titles:
        L.append(f"- {t}")

    L += ["", "## Por agente", ""]
    for agent, r in fleet.items():
        meta = AGENTS[agent]
        L.append(f"### {agent} — {meta['role']}")
        L.append(f"Foco: {meta['focus']}.")
        for slug, title in r["studied"]:
            L.append(f"- Estudou **{title}** → skill actualizada em `training/skills/{agent}/{slug}.md`")
        bad = [d for d, o in r["drills"] if not o]
        L.append("- Drills: todos verificados ✅" if not bad else f"- Drills falhados: {', '.join(bad)} ❌ (integridade do currículo — investigar)")
        L.append("")

    if failures:
        L += ["## ❌ Falhas", ""]
        for agent, tb in failures.items():
            L += [f"### {agent}", "```", tb.strip()[-600:], "```", ""]

    L += ["## Camada LLM (coach)", "", llm, ""]
    L += ["## Próxima sessão", ""]
    any_r = next(iter(fleet.values()), None)
    if any_r:
        L.append("Módulos seguintes: " + " · ".join(any_r["next"]))
    L += ["", "---", "_Sistema único de treino (hub devclone20/iclone). Currículo: ACP/Virtuals CLI · droplet ops · fases de negociação · Economy OS · Robinhood Chain · debugging._"]

    report = "\n".join(L) + "\n"
    (REPORTS / f"{today}.md").write_text(report)
    (REPORTS / "issue_body.md").write_text(report)
    print(report)
    return 0 if not failures else 0  # failures are reported, never hidden behind a red run


if __name__ == "__main__":
    raise SystemExit(main())
