#!/usr/bin/env python3
"""
VEGETA Autopilot — ciclo ACP autónomo
VEGETA (client) → iCLONE (provider)
Ciclo: create → wait budget_set → fund → wait submitted → complete → repeat

Usa XDG_CONFIG_HOME isolado para VEGETA em todos os comandos acp.
Nunca modifica o agente activo partilhado — zero conflito com o iCLONE server.
"""
import subprocess, json, time, random, logging, sys, os
from datetime import datetime

# ── Config ────────────────────────────────────────────────────────────────────
ICLONE_WALLET    = "0x44cc25d55a4291b92f52062ba023ca1f14206664"
CHAIN_ID         = "8453"
VEGETA_XDG       = os.path.expanduser("~/.config/acp-vegeta")

POLL_INTERVAL    = 8    # segundos entre polls de status
JOB_TIMEOUT      = 600  # 10 min max por job
CYCLE_INTERVAL   = int(os.getenv("CYCLE_INTERVAL", "3600"))  # 1h entre ciclos
JOBS_PER_CYCLE   = int(os.getenv("JOBS_PER_CYCLE", "1"))

ACP_BIN = next(
    (p for p in ["/opt/homebrew/bin/acp", "/usr/local/bin/acp", "acp"] if os.path.exists(p)),
    "acp"
)

VEGETA_AGENT_ID  = "019ec5ec-4b48-750d-894a-7f1fedebb988"
VEGETA_CONFIG    = os.path.expanduser("~/.config/acp-vegeta/acp")
VEGETA_ENV       = {**os.environ, "ACP_CONFIG_DIR": VEGETA_CONFIG}

OFFERINGS = [
    # ── Crypto Intel (core VEGETA mandate) ────────────────────────────────────
    ("tokenResearchStandard",  '{"topic":"Bitcoin macro outlook 2026","format":"markdown"}'),
    ("tokenResearchStandard",  '{"topic":"Ethereum L2 landscape","format":"markdown"}'),
    ("tokenResearchStandard",  '{"topic":"Solana ecosystem growth 2026","format":"markdown"}'),
    ("tokenResearchStandard",  '{"topic":"Base chain TVL and adoption","format":"markdown"}'),
    ("tokenResearchStandard",  '{"topic":"AI agent tokens on Virtuals Protocol","format":"markdown"}'),
    ("tokenResearchStandard",  '{"topic":"Physical Labor Layer robotics AI tokens","format":"markdown"}'),
    ("cryptoNewsFlash",        '{"format":"markdown"}'),
    ("cryptoNewsDaily",        '{"format":"markdown"}'),
    ("marketRegimeDetector",   '{"format":"markdown"}'),
    ("narrativeScanner",       '{"format":"markdown","focus":"AI agents and robotics"}'),
    ("tokenSnapshotQuick",     '{"token":"bitcoin","format":"markdown"}'),
    ("tokenSnapshotQuick",     '{"token":"ethereum","format":"markdown"}'),
    ("tokenSnapshotQuick",     '{"token":"virtual","format":"markdown"}'),
    ("fundingRateAlert",       '{"format":"markdown"}'),
    ("cryptoNewsSentiment",    '{"format":"markdown"}'),
    ("whaleActivityAlert",     '{"token":"bitcoin","format":"markdown"}'),
    ("yieldOpportunityFinder", '{"format":"markdown"}'),
    ("smartMoneyTracker",      '{"format":"markdown"}'),
    ("defiProtocolHealth",     '{"protocol":"uniswap","format":"markdown"}'),
    ("onChainFlowAnalysis",    '{"format":"markdown","chain":"base"}'),

    # ── Physical Labor Layer — Robotics Intel (new domain) ────────────────────
    # VEGETA hires CLONE to research robotics topics and GitHub repos
    # to power VEGETA's own robotics offering decisions
    ("tokenResearchStandard",  '{"topic":"huggingface lerobot manipulation learning","format":"markdown","offering_id":"tokenResearchStandard"}'),
    ("tokenResearchStandard",  '{"topic":"BerkeleyAutomation dex-net grasp synthesis AI","format":"markdown","offering_id":"tokenResearchStandard"}'),
    ("tokenResearchStandard",  '{"topic":"ROS2 navigation2 Nav2 autonomous mobile robots","format":"markdown","offering_id":"tokenResearchStandard"}'),
    ("tokenResearchStandard",  '{"topic":"YOLOv8 ultralytics robot perception pipeline","format":"markdown","offering_id":"tokenResearchStandard"}'),
    ("tokenResearchStandard",  '{"topic":"Segment Anything SAM robot visual grounding","format":"markdown","offering_id":"tokenResearchStandard"}'),
    ("tokenResearchStandard",  '{"topic":"diffusion policy columbia AI robot imitation learning","format":"markdown","offering_id":"tokenResearchStandard"}'),
    ("tokenResearchStandard",  '{"topic":"Genesis physics simulator embodied AI 2026","format":"markdown","offering_id":"tokenResearchStandard"}'),
    ("tokenResearchStandard",  '{"topic":"NVIDIA IsaacLab GPU robot training reinforcement learning","format":"markdown","offering_id":"tokenResearchStandard"}'),
    ("tokenResearchStandard",  '{"topic":"Google DeepMind dm-control MuJoCo robot RL","format":"markdown","offering_id":"tokenResearchStandard"}'),
    ("tokenResearchStandard",  '{"topic":"Physical Intelligence openpi pi0 foundation robot policy","format":"markdown","offering_id":"tokenResearchStandard"}'),
    ("tokenResearchStandard",  '{"topic":"Open X-Embodiment cross-robot dataset Google DeepMind","format":"markdown","offering_id":"tokenResearchStandard"}'),
    ("tokenResearchStandard",  '{"topic":"pddlstream task and motion planning manipulation TAMP","format":"markdown","offering_id":"tokenResearchStandard"}'),
    ("tokenResearchStandard",  '{"topic":"Unitree Go2 H1 quadruped humanoid robot deployment","format":"markdown","offering_id":"tokenResearchStandard"}'),
    ("tokenResearchStandard",  '{"topic":"MoveIt2 ROS2 motion planning arm robot","format":"markdown","offering_id":"tokenResearchStandard"}'),
    ("tokenResearchStandard",  '{"topic":"ALOHA bimanual robot teleoperation imitation ACT policy","format":"markdown","offering_id":"tokenResearchStandard"}'),
    ("tokenResearchStandard",  '{"topic":"RT-X robotics transformer Google research robot learning","format":"markdown","offering_id":"tokenResearchStandard"}'),
    ("tokenResearchStandard",  '{"topic":"Virtuals Protocol Physical Labor Layer robotics agents 2026","format":"markdown","offering_id":"tokenResearchStandard"}'),
    ("tokenResearchStandard",  '{"topic":"SERL sample efficient real robot reinforcement learning Berkeley","format":"markdown","offering_id":"tokenResearchStandard"}'),
    ("tokenResearchStandard",  '{"topic":"Florence-2 Microsoft vision language robot integration","format":"markdown","offering_id":"tokenResearchStandard"}'),
    ("tokenResearchStandard",  '{"topic":"K-Scale humanoid robot simulation kscalelabs training","format":"markdown","offering_id":"tokenResearchStandard"}'),
]

# ── Logging ───────────────────────────────────────────────────────────────────
LOG_PATH = os.path.expanduser("~/vegeta-autopilot.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s.%(msecs)03d [%(levelname)s] vegeta.autopilot: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_PATH),
    ],
)
log = logging.getLogger(__name__)

# ── Helpers ───────────────────────────────────────────────────────────────────
def acp_run(*args) -> tuple[str, str, int]:
    r = subprocess.run([ACP_BIN, *args], capture_output=True, text=True, timeout=60, env=VEGETA_ENV)
    return r.stdout.strip(), r.stderr.strip(), r.returncode

def get_job_status(job_id: str) -> str | None:
    """Poll job status from job history text output.
    First line format: '{job_id}\\t{status}\\t{entry_count}'
    """
    out, _, _ = acp_run("job", "history", "--job-id", job_id, "--chain-id", CHAIN_ID)
    if not out:
        return None
    first = out.splitlines()[0]
    parts = first.split("\t")
    if len(parts) >= 2:
        return parts[1].strip().lower()
    return None

def create_job(offering: str, requirements: str) -> str | None:
    try:
        req = json.loads(requirements)
        req["offering_id"] = offering
        requirements = json.dumps(req)
    except (json.JSONDecodeError, TypeError):
        pass

    out, err, rc = acp_run(
        "client", "create-job",
        "--provider", ICLONE_WALLET,
        "--offering-name", offering,
        "--requirements", requirements,
        "--chain-id", CHAIN_ID,
    )
    for line in out.splitlines():
        if "Job #" in line and "created" in line:
            job_id = line.split("#")[1].split()[0]
            log.info("Job #%s created — offering: %s", job_id, offering)
            return job_id
    log.error("create-job failed: %s | %s", out[:200], err[:200])
    return None

def wait_for_status(job_id: str, target: str, timeout: int) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        status = get_job_status(job_id)
        log.info("Job #%s status: %s (waiting for %s)", job_id, status, target)
        if status == target:
            return True
        if status in ("completed", "rejected", "expired"):
            log.warning("Job #%s terminal state: %s — aborting wait", job_id, status)
            return False
        time.sleep(POLL_INTERVAL)
    log.error("Job #%s timed out waiting for %s", job_id, target)
    return False

def fund_job(job_id: str) -> bool:
    out, err, rc = acp_run("client", "fund", "--job-id", job_id, "--chain-id", CHAIN_ID)
    ok = rc == 0 and "funded" in out.lower()
    if ok:
        log.info("Job #%s funded ✅", job_id)
    else:
        log.error("fund failed (rc=%d): %s | %s", rc, out[:200], err[:200])
    return ok

def complete_job(job_id: str) -> bool:
    out, err, rc = acp_run("client", "complete", "--job-id", job_id, "--chain-id", CHAIN_ID)
    ok = rc == 0 and "completed" in out.lower()
    if ok:
        log.info("Job #%s completed — escrow released to iCLONE ✅", job_id)
    else:
        log.error("complete failed (rc=%d): %s | %s", rc, out[:200], err[:200])
    return ok

# ── Core cycle ────────────────────────────────────────────────────────────────
def run_job_cycle() -> bool:
    offering, requirements = random.choice(OFFERINGS)
    log.info("── Starting cycle: %s ──", offering)

    job_id = create_job(offering, requirements)
    if not job_id:
        return False

    if not wait_for_status(job_id, "budget_set", JOB_TIMEOUT):
        return False

    if not fund_job(job_id):
        return False

    if not wait_for_status(job_id, "submitted", JOB_TIMEOUT):
        return False

    complete_job(job_id)
    log.info("── Cycle complete: Job #%s ──", job_id)
    return True

def recover_pending_jobs():
    """Fund any existing jobs that are in budget_set state (resuming after restart)."""
    out, err, rc = acp_run("job", "list", "--json")
    if rc != 0 or not out:
        return
    try:
        data = json.loads(out)
        jobs = data.get("jobs", [])
    except json.JSONDecodeError:
        return

    for j in jobs:
        jid = str(j.get("onChainJobId", ""))
        if not jid:
            continue
        status = get_job_status(jid)
        log.info("Recovery: job #%s status=%s", jid, status)
        if status == "budget_set":
            log.info("Recovery: funding job #%s", jid)
            if fund_job(jid):
                if wait_for_status(jid, "submitted", JOB_TIMEOUT):
                    complete_job(jid)
        elif status == "submitted":
            log.info("Recovery: completing job #%s", jid)
            complete_job(jid)

# ── Main loop ─────────────────────────────────────────────────────────────────
def main():
    log.info("VEGETA Autopilot starting — cycle: %ds, jobs/cycle: %d", CYCLE_INTERVAL, JOBS_PER_CYCLE)
    log.info("Recovering pending jobs from previous session...")
    try:
        recover_pending_jobs()
    except Exception as e:
        log.exception("Recovery error: %s", e)

    while True:
        for i in range(JOBS_PER_CYCLE):
            try:
                run_job_cycle()
            except Exception as e:
                log.exception("Unexpected error in cycle %d: %s", i + 1, e)
            if i < JOBS_PER_CYCLE - 1:
                time.sleep(30)

        log.info("Sleeping %ds until next cycle...", CYCLE_INTERVAL)
        time.sleep(CYCLE_INTERVAL)

if __name__ == "__main__":
    main()
