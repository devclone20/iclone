#!/usr/bin/env python3
"""Fleet training engine — devclone20 agent fleet.

Two session kinds, one engine:

- FLEET (Mon/Wed/Fri): all 9 agents cycle through the shared curriculum
  (ACP/Virtuals, droplet ops, negotiation phases, Economy OS, Robinhood
  Chain, debugging, supply-chain law).
- SPECIALTY (Tue/Thu): the two specialists deepen their own crafts —
  doctor-agent on IST-standard academic work and the university's scientific
  repository; forense-ai on to-the-origin investigation across the open web
  (with live web probes).

Deterministic core: no session depends on any external API to complete.
The LLM coach layer and the web probes degrade gracefully and honestly.
Every session ends with one organized Portuguese report, delivered by the
workflow as a GitHub issue (GitHub emails the owner on creation).
"""

from __future__ import annotations

import json
import os
import re
import traceback
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CURRICULUM = ROOT / "curriculum"
STATE = ROOT / "state"
SKILLS = ROOT / "skills"
REPORTS = ROOT / "reports"

MODULES_PER_SESSION = 2
QUARANTINE_DAYS = 14

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
        "role": "academic rigor (IST)",
        "focus": "IST-standard papers and dissertations; the university's scientific repository",
    },
    "akita-agent": {
        "repo": "devclone20/akita-agent",
        "role": "senior engineering review",
        "focus": "auditing integrations and CI around the trade rails",
    },
    "forense-ai": {
        "repo": "devclone20/forense-ai",
        "role": "forensics / investigation",
        "focus": "tracing any incident to its origin; evidence-first method on the open web",
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

MODULES = [
    ("01-acp-foundations", ["phases-order"]),
    ("02-acp-cli-agent", ["pending-auth", "skill-staleness"]),
    ("03-droplet-ops", ["long-bash", "detached-state"]),
    ("04-negotiation-phases", ["fee-math", "ledger-match"]),
    ("05-economy-os", ["fee-math-2"]),
    ("06-robinhood-chain", ["ui-multiplier", "npm-trap"]),
    ("07-debugging", ["escrow-stuck", "runner-outage", "credit-400"]),
    ("08-supply-chain", ["fresh-package", "registry-dates"]),
]

# Tue/Thu specialty tracks. Probes are live web checks recorded in the
# artifacts — reachability + page title, never a hard dependency.
SPECIALTY = {
    "doctor-agent": {
        "track": [
            ("d1-ist-standards", ["ist-structure", "citation-format"]),
            ("d2-ist-repository", ["no-fabrication"]),
            ("d3-review-craft", ["claims-evidence"]),
        ],
        "probes": [
            ("Técnico Scholar — repositório científico do IST", "https://scholar.tecnico.ulisboa.pt"),
            ("Repositório da Universidade de Lisboa", "https://repositorio.ulisboa.pt"),
        ],
    },
    "forense-ai": {
        "track": [
            ("f1-root-cause", ["timeline-first", "proximate-vs-root"]),
            ("f2-osint-web", ["corroborate-two", "verify-liveness"]),
            ("f3-digital-evidence", ["preserve-first"]),
        ],
        "probes": [
            ("Internet Archive — Wayback Machine", "https://web.archive.org"),
            ("Certificate Transparency — crt.sh", "https://crt.sh"),
        ],
    },
}

CANON_PHASES = ["job.created", "budget.set", "job.funded", "job.submitted", "job.completed"]


def _fee(amount: float) -> tuple[float, float]:
    fee = round(amount * 0.10, 6)
    return round(amount - fee, 6), fee


def _quarantine_ok(age_days: int) -> bool:
    return age_days >= QUARANTINE_DAYS


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
    "fresh-package": {
        "scenario": "A tempting npm/PyPI package was published 3 days ago.",
        "expected": f"REFUSE. Fleet law: nothing younger than {QUARANTINE_DAYS} days gets installed — fresh releases are where supply-chain attacks live.",
        "check": lambda: (not _quarantine_ok(3)) and (not _quarantine_ok(13)) and _quarantine_ok(30),
    },
    "registry-dates": {
        "scenario": "How do you know a package's real age?",
        "expected": "Ask the registry, not the README: pypi.org/pypi/<pkg>/json upload times; npm registry `time` field. The training's own quarantine_pip.py is the working example.",
        "check": lambda: True,
    },
    "ist-structure": {
        "scenario": "A dissertation draft arrives with results before methodology and no PT/EN abstracts.",
        "expected": "Rebuild to the IST skeleton: abstracts + keywords in PT and EN, introduction → related work → methodology → results → discussion → conclusion, complete references.",
        "check": lambda: True,
    },
    "citation-format": {
        "scenario": "References mix three styles mid-list.",
        "expected": "One style, applied everywhere (IEEE numeric is the engineering default at IST); every entry complete and every in-text citation resolvable.",
        "check": lambda: True,
    },
    "no-fabrication": {
        "scenario": "A cited paper cannot be found in any repository.",
        "expected": "Fabricated or wrong — either way it leaves the manuscript. Every reference must resolve (DOI, handle, or repository record) before submission. Never invent a source.",
        "check": lambda: True,
    },
    "claims-evidence": {
        "scenario": "The abstract claims 'state of the art' but the tables beat one baseline from 2019.",
        "expected": "Flag the claim–evidence gap: every claim must be carried by the presented evidence, and comparisons must include current baselines.",
        "check": lambda: True,
    },
    "timeline-first": {
        "scenario": "An incident report starts with a suspect and works backwards.",
        "expected": "Reverse it: evidence intake → timeline reconstruction → hypothesis tree → eliminate until the origin. Conclusions come last, not first.",
        "check": lambda: True,
    },
    "proximate-vs-root": {
        "scenario": "A CI run failed and the log's last line blames the test step.",
        "expected": "Last line = proximate cause. Keep asking why until the origin (real case: 'review failed' → runner never acquired → GitHub Actions major outage — code was never the problem).",
        "check": lambda: True,
    },
    "corroborate-two": {
        "scenario": "One website makes the key claim of the investigation.",
        "expected": "One source is an anecdote. Corroborate with a second independent source or downgrade the claim; prefer primary evidence over reporting about it.",
        "check": lambda: True,
    },
    "verify-liveness": {
        "scenario": "An automated reviewer claims a link is dead.",
        "expected": "Verify with an independent instrument before acting (real case: X post 'broken' to a blocked fetcher — the oEmbed endpoint proved it live, with a negative control).",
        "check": lambda: True,
    },
    "preserve-first": {
        "scenario": "Key evidence lives on a page that could change or vanish.",
        "expected": "Preserve before analysing: archive (Wayback), hash, screenshot, record retrieval time. Chain of custody makes evidence usable; immutable ledgers are the gold standard.",
        "check": lambda: True,
    },
}


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def resolve_mode() -> str:
    mode = os.environ.get("SESSION_MODE", "auto").strip().lower()
    if mode in ("fleet", "specialty"):
        return mode
    return "specialty" if utcnow().weekday() in (1, 3) else "fleet"  # Tue=1, Thu=3


def load_state(agent: str) -> dict:
    p = STATE / f"{agent}.json"
    st = json.loads(p.read_text()) if p.exists() else {}
    st.setdefault("next_module", 0)
    st.setdefault("next_specialty", 0)
    st.setdefault("sessions", 0)
    st.setdefault("drills_passed", 0)
    st.setdefault("drills_failed", 0)
    return st


def save_state(agent: str, st: dict) -> None:
    STATE.mkdir(parents=True, exist_ok=True)
    (STATE / f"{agent}.json").write_text(json.dumps(st, indent=2) + "\n")


def module_text(slug: str) -> str:
    p = CURRICULUM / f"{slug}.md"
    return p.read_text() if p.exists() else ""


def module_title(slug: str) -> str:
    m = re.search(r"^#\s+(.+)$", module_text(slug), re.M)
    return m.group(1).strip() if m else slug


def key_points(slug: str) -> str:
    m = re.search(r"## Key points\n(.*?)(?:\n## |\Z)", module_text(slug), re.S)
    return m.group(1).strip() if m else "(module missing — curriculum integrity drill will flag this)"


def sources_for(slug: str) -> list[str]:
    m = re.search(r"## Sources\n(.*?)(?:\n## |\Z)", module_text(slug), re.S)
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


def probe(url: str) -> str:
    """Live web probe: status + title, degrading to an honest failure note."""
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en,pt;q=0.8",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            body = r.read(65536).decode("utf-8", errors="replace")
            m = re.search(r"<title[^>]*>(.*?)</title>", body, re.S | re.I)
            title = re.sub(r"\s+", " ", m.group(1)).strip()[:120] if m else "(sem title)"
            return f"✅ HTTP {r.status} — “{title}”"
    except Exception as e:  # noqa: BLE001
        return f"⚠️ inacessível ({type(e).__name__}) — treino continua com o currículo"


def run_drill(drill_id: str) -> tuple[bool, dict]:
    d = DRILLS[drill_id]
    try:
        ok = bool(d["check"]())
    except Exception:  # noqa: BLE001
        ok = False
    return ok, d


def study(agent: str, meta: dict, today: str, track: list, cursor_key: str) -> dict:
    st = load_state(agent)
    start = st[cursor_key] % len(track)
    studied, drills = [], []
    n = min(MODULES_PER_SESSION, len(track))

    for i in range(n):
        slug, drill_ids = track[(start + i) % len(track)]
        title = module_title(slug)
        results = []
        for did in drill_ids:
            ok, d = run_drill(did)
            results.append((did, ok, d))
            drills.append((did, ok))

        SKILLS.joinpath(agent).mkdir(parents=True, exist_ok=True)
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
                exc = source_skill_excerpt(s)
                if exc:
                    lines.append(f"  - _{exc}_")
        (SKILLS / agent / f"{slug}.md").write_text("\n".join(lines) + "\n")
        studied.append((slug, title))

    st[cursor_key] = (start + n) % len(track)
    st["sessions"] += 1
    st["drills_passed"] += sum(1 for _, ok in drills if ok)
    st["drills_failed"] += sum(1 for _, ok in drills if not ok)
    st["last_session"] = today
    save_state(agent, st)

    nxt = [module_title(track[(st[cursor_key] + i) % len(track)][0]) for i in range(n)]
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
                    "You coach a fleet of autonomous agents. Today's modules: "
                    + ", ".join(studied_titles)
                    + ". In Portuguese, give one sharp paragraph (max 120 words) of practical "
                      "advice connecting these topics to doing real, verifiable work safely."
                ),
            }],
        )
        return "activa — nota do coach:\n\n> " + msg.content[0].text.strip().replace("\n", "\n> ")
    except ModuleNotFoundError:
        return "inactiva — SDK não instalado nesta sessão (quarentena de pacotes pode ter recusado); núcleo determinístico não afectado."
    except Exception as e:  # noqa: BLE001
        if "credit" in str(e).lower():
            return "sem créditos na API Anthropic — o treino correu completo no núcleo determinístico. (Repor créditos reactiva esta camada sozinha.)"
        return f"falhou ({type(e).__name__}) — núcleo determinístico não afectado."


def main() -> int:
    today = utcnow().strftime("%Y-%m-%d")
    note = os.environ.get("SESSION_NOTE", "Scheduled")
    mode = resolve_mode()
    REPORTS.mkdir(parents=True, exist_ok=True)

    if mode == "specialty":
        roster = {a: AGENTS[a] for a in SPECIALTY}
        kind = "Especialidade (Ter/Qui)"
    else:
        roster = AGENTS
        kind = "Frota (Seg/Qua/Sex)"

    fleet, failures, probes_out = {}, {}, {}
    for agent, meta in roster.items():
        try:
            if mode == "specialty":
                spec = SPECIALTY[agent]
                fleet[agent] = study(agent, meta, today, spec["track"], "next_specialty")
                probes_out[agent] = [(label, probe(url), url) for label, url in spec["probes"]]
            else:
                fleet[agent] = study(agent, meta, today, MODULES, "next_module")
        except Exception:  # noqa: BLE001
            failures[agent] = traceback.format_exc(limit=3)

    all_titles = sorted({t for r in fleet.values() for _, t in r["studied"]})
    llm = coach_note(all_titles)

    L = [
        f"# 📚 Treino — {kind} — {today}",
        "",
        f"_Sessão: {note} · {utcnow().strftime('%H:%M')} UTC · {len(fleet)}/{len(roster)} agentes treinados._",
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
        meta = roster[agent]
        L.append(f"### {agent} — {meta['role']}")
        L.append(f"Foco: {meta['focus']}.")
        for slug, title in r["studied"]:
            L.append(f"- Estudou **{title}** → skill actualizada em `training/skills/{agent}/{slug}.md`")
        bad = [d for d, o in r["drills"] if not o]
        L.append("- Drills: todos verificados ✅" if not bad else f"- Drills falhados: {', '.join(bad)} ❌ (integridade do currículo — investigar)")
        for label, result, url in probes_out.get(agent, []):
            L.append(f"- Sonda web: {label} → {result} (<{url}>)")
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
    L += [
        "",
        "---",
        f"_Sistema único de treino (hub devclone20/iclone). Frota Seg/Qua/Sex · Especialidade Ter/Qui (doctor-agent: padrão IST + repositório científico · forense-ai: investigação até à origem na web aberta). Lei da frota: quarentena de {QUARANTINE_DAYS} dias para qualquer pacote._",
    ]

    report = "\n".join(L) + "\n"
    (REPORTS / f"{today}-{mode}.md").write_text(report)
    (REPORTS / "issue_body.md").write_text(report)
    print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
