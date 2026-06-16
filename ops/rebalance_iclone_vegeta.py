#!/usr/bin/env python3
"""
Rebalance: iCLONE executa 10 jobs para VEGETA.
VEGETA paga iCLONE por cada job entregue.
Corre sequencialmente, 1 job de cada vez, e termina.

O saldo ficou desequilibrado porque jobs anteriores falharam a libertar o escrow.
Este script faz 10 transacções limpas iCLONE→VEGETA para nivelar.
"""
import subprocess, json, time, re, sys, os
from pathlib import Path

CHAIN_ID        = "8453"
ICLONE_CONFIG   = "/home/iclone/.config/acp-iclone/acp"
VEGETA_CONFIG   = "/home/iclone/.config/acp-vegeta/acp"
ICLONE_ENV      = {**os.environ, "ACP_CONFIG_DIR": ICLONE_CONFIG}
VEGETA_ENV      = {**os.environ, "ACP_CONFIG_DIR": VEGETA_CONFIG}
ACP_BIN         = next((p for p in ["/usr/bin/acp", "/usr/local/bin/acp"] if Path(p).exists()), "acp")

ICLONE_WALLET   = "0x44cc25d55a4291b92f52062ba023ca1f14206664"
VEGETA_WALLET   = "0xe09f40114af6c78788a8003da127c49c56158584"
TOTAL_JOBS      = 10

# Offerings iCLONE com preço $0.05 — rápidos de executar
OFFERINGS = [
    ("tokenSnapshotQuick",  '{"symbol":"BTC","offering_id":"tokenSnapshotQuick"}'),
    ("cryptoNewsFlash",     '{"offering_id":"cryptoNewsFlash"}'),
    ("tokenSnapshotQuick",  '{"symbol":"ETH","offering_id":"tokenSnapshotQuick"}'),
    ("cryptoNewsFlash",     '{"offering_id":"cryptoNewsFlash"}'),
    ("tokenSnapshotQuick",  '{"symbol":"SOL","offering_id":"tokenSnapshotQuick"}'),
    ("cryptoNewsFlash",     '{"offering_id":"cryptoNewsFlash"}'),
    ("tokenSnapshotQuick",  '{"symbol":"BNB","offering_id":"tokenSnapshotQuick"}'),
    ("cryptoNewsFlash",     '{"offering_id":"cryptoNewsFlash"}'),
    ("tokenSnapshotQuick",  '{"symbol":"AVAX","offering_id":"tokenSnapshotQuick"}'),
    ("cryptoNewsFlash",     '{"offering_id":"cryptoNewsFlash"}'),
]

def acp_as(env, *args, timeout=90):
    r = subprocess.run([ACP_BIN, *args], capture_output=True, text=True, timeout=timeout, env=env)
    return r.stdout.strip(), r.stderr.strip(), r.returncode

def job_status(job_id, env=None):
    _env = env or VEGETA_ENV
    out, _, _ = acp_as(_env, "job", "history", "--job-id", job_id, "--chain-id", CHAIN_ID, timeout=30)
    if not out:
        return None
    parts = out.splitlines()[0].split("\t")
    return parts[1].strip().lower() if len(parts) > 1 else None

def wait_for(job_id, target, timeout_sec, env=None):
    deadline = time.time() + timeout_sec
    while time.time() < deadline:
        st = job_status(job_id, env)
        if st == target:
            return True
        if st in ("rejected", "expired", "cancelled"):
            return False
        time.sleep(12)
    return False

def run_one_job(n, offering, requirements):
    print(f"\n── Job {n}/{TOTAL_JOBS}: {offering} ──")

    # VEGETA cria o job (contrata iCLONE)
    req = requirements
    out, err, rc = acp_as(VEGETA_ENV, "client", "create-job",
                          "--provider", ICLONE_WALLET,
                          "--offering-name", offering,
                          "--requirements", req,
                          "--chain-id", CHAIN_ID, timeout=60)
    blob = out + " " + err
    m = re.search(r"#?(\d{4,})", blob)
    if not m:
        print(f"  ❌ create-job falhou: {blob[:200]}")
        return False
    job_id = m.group(1)
    print(f"  Job #{job_id} criado (VEGETA→iCLONE)")

    # Esperar iCLONE definir budget
    print(f"  Aguardar budget_set...")
    if not wait_for(job_id, "budget_set", timeout_sec=180, env=VEGETA_ENV):
        print(f"  ❌ timeout budget_set")
        return False
    print(f"  budget_set ✓")

    # VEGETA funda o job (paga iCLONE)
    out, err, rc = acp_as(VEGETA_ENV, "client", "fund",
                          "--job-id", job_id, "--chain-id", CHAIN_ID, timeout=60)
    funded = rc == 0 or "funded" in (out + err).lower()
    if not funded:
        print(f"  ❌ fund falhou: {err[:150]}")
        return False
    print(f"  Fundado ✓ (VEGETA pagou)")

    # Esperar iCLONE submeter o deliverable
    print(f"  Aguardar entrega iCLONE...")
    if not wait_for(job_id, "submitted", timeout_sec=300, env=VEGETA_ENV):
        print(f"  ❌ timeout submitted")
        return False
    print(f"  Deliverable submetido ✓")

    # VEGETA completa o job (liberta escrow → iCLONE recebe pagamento)
    out, err, rc = acp_as(VEGETA_ENV, "client", "complete",
                          "--job-id", job_id, "--chain-id", CHAIN_ID, timeout=60)
    ok = rc == 0 or "completed" in (out + err).lower()
    if ok:
        print(f"  ✅ Job #{job_id} completo — iCLONE recebeu pagamento")
    else:
        print(f"  ❌ complete falhou: {err[:150]}")
    return ok

def main():
    print("═══ Rebalance iCLONE ← VEGETA: 10 jobs ═══")
    print(f"  iCLONE: {ICLONE_WALLET[:12]}...")
    print(f"  VEGETA: {VEGETA_WALLET[:12]}...")
    print()

    done = 0
    for i, (offering, requirements) in enumerate(OFFERINGS, 1):
        ok = run_one_job(i, offering, requirements)
        if ok:
            done += 1
        # Pausa entre jobs para evitar nonce conflicts
        if i < TOTAL_JOBS:
            print(f"  Pausa 20s antes do próximo job...")
            time.sleep(20)

    print(f"\n═══ Rebalance concluído ═══")
    print(f"  {done}/{TOTAL_JOBS} jobs completados com sucesso")
    print(f"  iCLONE recebeu ${done * 0.05:.2f} USDC em pagamentos")

if __name__ == "__main__":
    main()
