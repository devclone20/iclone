#!/usr/bin/env python3
"""
Ping-pong de jobs premium (2 USDC) entre VEGETA e iCLONE.

Fluxo (alternância ESTRITA, um job de cada vez, totalmente completo):
  1. VEGETA contrata iCLONE  → deepCryptoIntelReport ($2) → VEGETA paga
  2. iCLONE contrata VEGETA  → roboticsSystemDesign  ($2) → iCLONE paga
  (repete para sempre)

Regras:
  - Só avança para o outro lado quando o job atual está COMPLETO (escrow libertado).
  - Cadência: um job a cada 4 min (medido do início de cada job).
  - Estado persistido em pingpong_state.json. Se parar, resume EXACTAMENTE no
    lado e no job onde ficou (continuidade perfeita).
  - Idempotente: a máquina é guiada pelo estado real on-chain (job history),
    por isso reentra sem duplicar fund/complete.
  - Se um job ficar preso/não pagar: não avança; mantém o lado e retenta.

Requer keyring acessível (operações de client). Correr via:
  su -l iclone -s /bin/bash -c 'dbus-run-session -- python3 pingpong.py'
"""
import json
import logging
import os
import re
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# ── Config ───────────────────────────────────────────────────────────────────
ACP        = "/usr/bin/acp"
CHAIN      = "8453"
STATE_FILE = Path("/opt/iclone/ops/pingpong_state.json")
CADENCE_SEC = 600          # 10 min entre inicios de job (baixo custo, manter live)
JOB_DRIVE_TIMEOUT = 600       # 10 min máx para levar um job a completo
POLL_SEC   = 10               # intervalo de verificação de status
LOW_USDC_WARN = 0.15           # avisar se saldo USDC < preço do job (0.10)
LOW_ETH_WARN  = 0.0004        # avisar se gás baixo

ICLONE_CFG    = "/home/iclone/.config/acp-iclone/acp"
VEGETA_CFG    = "/home/iclone/.config/acp-vegeta/acp"
ICLONE_WALLET = "0x44cc25d55a4291b92f52062ba023ca1f14206664"
VEGETA_WALLET = "0xe09f40114af6c78788a8003da127c49c56158584"

# Rotação de inputs para variar os deliverables
CRYPTO_TOPICS = ["BTC", "ETH", "SOL", "BNB", "AVAX", "LINK", "ARB", "OP"]
ROBOT_TASKS = [
    "bimanual manipulation pipeline",
    "warehouse autonomous navigation",
    "dexterous grasping with vision",
    "humanoid locomotion control",
    "drone waypoint inspection",
    "mobile manipulation fetch-and-place",
]

SIDES = {
    "vegeta_hires_iclone": {
        "client_cfg":      VEGETA_CFG,
        "provider_wallet": ICLONE_WALLET,
        "offering":        "riskRewardCalculator",
        "label":           "VEGETA→iCLONE ($0.10 riskRewardCalculator)",
        "next":            "iclone_hires_vegeta",
    },
    "iclone_hires_vegeta": {
        "client_cfg":      ICLONE_CFG,
        "provider_wallet": VEGETA_WALLET,
        "offering":        "roboticsRepoScan",
        "label":           "iCLONE→VEGETA ($0.10 roboticsRepoScan)",
        "next":            "vegeta_hires_iclone",
    },
}

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [pingpong] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    stream=sys.stdout,
)
def log(msg, *args):
    logging.info(msg, *args)


_running = True


def _stop(signum, frame):
    global _running
    _running = False
    log("SIGTERM recebido — a terminar de forma limpa (estado já persistido).")


signal.signal(signal.SIGTERM, _stop)
signal.signal(signal.SIGINT, _stop)


# ── Helpers ──────────────────────────────────────────────────────────────────
def now_iso():
    return datetime.now(timezone.utc).isoformat()


def acp(cfg, *args, timeout=120):
    env = {**os.environ, "ACP_CONFIG_DIR": cfg}
    try:
        r = subprocess.run([ACP, *args], capture_output=True, text=True,
                           env=env, timeout=timeout)
        return r.returncode, (r.stdout or "").strip(), (r.stderr or "").strip()
    except subprocess.TimeoutExpired:
        return 124, "", "timeout"
    except Exception as e:
        return 1, "", str(e)


REPOS = ["huggingface/lerobot", "google-deepmind/mujoco", "facebookresearch/habitat-lab",
         "ros-planning/moveit2", "NVIDIA-Omniverse/IsaacGymEnvs", "openai/gym"]
TRADES = [("BTC","60000","72000","56000"), ("ETH","3000","3800","2750"),
          ("SOL","140","190","120"), ("LINK","14","20","12"),
          ("ARB","0.9","1.4","0.75"), ("OP","1.6","2.3","1.3")]

def build_requirements(side_key, cycle):
    if side_key == "vegeta_hires_iclone":
        tok, e, t, st = TRADES[cycle % len(TRADES)]
        return {"offering_id": "riskRewardCalculator", "token": tok,
                "entry": e, "target": t, "stop": st}
    else:
        repo = REPOS[cycle % len(REPOS)]
        return {"offering_id": "roboticsRepoScan", "repo": repo,
                "focus": "structure, components, how to run"}


def keyring_broken(blob):
    b = blob.lower()
    return "keyrevoked" in b or "secret service" in b or "platform storage" in b


def job_status(cfg, job_id):
    rc, out, err = acp(cfg, "job", "history", "--job-id", job_id,
                       "--chain-id", CHAIN, timeout=40)
    if not out:
        return None
    first = out.splitlines()[0]
    parts = first.split("\t")
    return parts[1].strip().lower() if len(parts) > 1 else None


def check_gas_and_balance(cfg, who):
    rc, out, err = acp(cfg, "wallet", "balance", "--chain-id", CHAIN, timeout=40)
    if rc != 0 or not out:
        return
    eth = usdc = None
    for line in out.splitlines():
        c = line.split("\t")
        if len(c) >= 3:
            if c[0] == "ETH":
                try: eth = float(c[2])
                except ValueError: pass
            elif c[0] == "USDC":
                try: usdc = float(c[2])
                except ValueError: pass
    if eth is not None and eth < LOW_ETH_WARN:
        log("⚠️  GÁS BAIXO em %s: %.6f ETH — faz top-up de ETH (Base) senão as tx vão falhar.", who, eth)
    if usdc is not None and usdc < LOW_USDC_WARN:
        log("⚠️  USDC BAIXO em %s: %.4f USDC (< $2) — fund pode falhar até receber/top-up.", who, usdc)


def create_job(cfg, side):
    reqs = side["_reqs"]
    rc, out, err = acp(cfg, "client", "create-job",
                       "--provider", side["provider_wallet"],
                       "--offering-name", side["offering"],
                       "--requirements", json.dumps(reqs),
                       "--chain-id", CHAIN, timeout=120)
    blob = out + " " + err
    if keyring_broken(blob):
        log("❌ KeyRevoked/keyring inacessível ao criar job. "
            "O serviço TEM de correr sob 'su -l iclone + dbus-run-session'.")
        return None
    m = re.search(r"#(\d{4,})", blob)
    if not m:
        log("❌ create-job falhou (%s): %s", side["label"], blob[:200])
        return None
    return m.group(1)


def drive_to_completion(cfg, job_id, label):
    """Leva o job ao estado COMPLETED, de forma idempotente.
    Retorna: 'completed' | 'failed' (terminal) | 'timeout'."""
    deadline = time.time() + JOB_DRIVE_TIMEOUT
    last_action = None
    while _running and time.time() < deadline:
        st = job_status(cfg, job_id)
        if st == "completed":
            return "completed"
        if st in ("rejected", "expired", "cancelled"):
            log("   job #%s estado terminal: %s", job_id, st)
            return "failed"

        if st in ("budget_set", "budgetset"):
            if last_action != "fund":
                rc, out, err = acp(cfg, "client", "fund", "--job-id", job_id,
                                   "--chain-id", CHAIN, timeout=120)
                blob = out + " " + err
                if keyring_broken(blob):
                    log("   ❌ keyring inacessível no fund #%s", job_id)
                    return "timeout"
                bl = blob.lower()
                if ("insufficient" in bl or "exceeds balance" in bl
                        or "execution reverted" in bl or "transfer amount exceeds" in bl):
                    # Saldo USDC insuficiente para o escrow → o fund reverte on-chain.
                    # Logar com "saldo insuficiente" para o watchdog detetar e parar.
                    log("   ⚠️ saldo insuficiente para fund #%s (escrow reverteu) — aguardar/top-up", job_id)
                elif rc == 0 and "error" not in bl:
                    log("   #%s fundado", job_id)
                    last_action = "fund"
                else:
                    log("   ⚠️ fund #%s falhou: %s", job_id, blob[:160])
        elif st == "submitted":
            rc, out, err = acp(cfg, "client", "complete", "--job-id", job_id,
                               "--chain-id", CHAIN, timeout=120)
            blob = out + " " + err
            if keyring_broken(blob):
                log("   ❌ keyring inacessível no complete #%s", job_id)
                return "timeout"
            log("   #%s complete enviado (escrow libertado ao provider)", job_id)
            last_action = "complete"
        # open / funded / pending → esperar o provider agir
        time.sleep(POLL_SEC)
    return "timeout"


# ── Estado ───────────────────────────────────────────────────────────────────
def load_state():
    if STATE_FILE.exists():
        try:
            s = json.loads(STATE_FILE.read_text())
            s.setdefault("current_side", "vegeta_hires_iclone")
            s.setdefault("inflight_job", None)
            s.setdefault("cycle", 0)
            return s
        except Exception as e:
            log("estado ilegível (%s) — a recomeçar limpo", e)
    return {"current_side": "vegeta_hires_iclone", "inflight_job": None, "cycle": 0}


def save_state(s):
    s["updated_at"] = now_iso()
    tmp = STATE_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(s, indent=2, ensure_ascii=False))
    tmp.replace(STATE_FILE)


# ── Loop principal ───────────────────────────────────────────────────────────
def main():
    log("════════ Ping-pong VEGETA↔iCLONE ($0.10/job, 1 job / 5 min) ════════")
    state = load_state()
    log("Estado inicial: lado=%s inflight=%s cycle=%d",
        state["current_side"], state["inflight_job"], state["cycle"])

    while _running:
        side_key = state["current_side"]
        side = SIDES[side_key]
        cfg = side["client_cfg"]
        side["_reqs"] = build_requirements(side_key, state["cycle"])
        who = "VEGETA" if cfg == VEGETA_CFG else "iCLONE"

        t0 = time.time()
        check_gas_and_balance(cfg, who)

        # Resolver job (resume ou criar novo)
        job_id = state.get("inflight_job")
        if job_id:
            st = job_status(cfg, job_id)
            if st in (None, "rejected", "expired", "cancelled"):
                log("inflight #%s não utilizável (%s) — vou recriar no mesmo lado",
                    job_id, st)
                job_id = None
                state["inflight_job"] = None
                save_state(state)
            else:
                log("↻ RESUME %s — job #%s (status: %s)", side["label"], job_id, st)

        if not job_id:
            log("▶ %s — cycle %d — req=%s", side["label"], state["cycle"],
                json.dumps(side["_reqs"], ensure_ascii=False))
            job_id = create_job(cfg, side)
            if not job_id:
                log("   create falhou — retry em 30s (sem avançar de lado)")
                time.sleep(30)
                continue
            state["inflight_job"] = job_id
            save_state(state)
            log("   job #%s criado", job_id)

        # Levar o job a completo
        result = drive_to_completion(cfg, job_id, side["label"])

        if result == "completed":
            state["inflight_job"] = None
            state["current_side"] = side["next"]
            state["cycle"] += 1
            save_state(state)
            log("✅ COMPLETO %s — job #%s | próximo lado: %s | cycle=%d",
                side["label"], job_id, SIDES[state["current_side"]]["label"],
                state["cycle"])
            # cadência: 1 job / 5 min (a contar do início)
            elapsed = time.time() - t0
            wait = max(0, CADENCE_SEC - elapsed)
            if wait and _running:
                log("   ⏲ aguardar %.0fs para respeitar cadência de 5 min", wait)
                # dormir em fatias para reagir a SIGTERM
                end = time.time() + wait
                while _running and time.time() < end:
                    time.sleep(min(5, end - time.time()))
        elif result == "failed":
            # terminal: mantém o MESMO lado, recria no próximo loop
            log("⚠️ %s job #%s terminou mal — recriar no MESMO lado", side["label"], job_id)
            state["inflight_job"] = None
            save_state(state)
            time.sleep(20)
        else:  # timeout
            log("⏳ %s job #%s não completou a tempo — mantém inflight e retoma", side["label"], job_id)
            time.sleep(30)

    log("Loop terminado (estado: lado=%s inflight=%s cycle=%d).",
        state["current_side"], state["inflight_job"], state["cycle"])


if __name__ == "__main__":
    main()
