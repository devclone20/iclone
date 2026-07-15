#!/usr/bin/env python3
"""
Bootstrap visibility run — contrata 4 agentes externos a $0.10, monitoriza, termina.
Corre uma vez e sai. Nenhum loop permanente.
"""
import subprocess, json, time, re, sys, os
from pathlib import Path

CHAIN_ID   = "8453"
CONFIG_DIR = os.getenv("ACP_CONFIG_DIR", "/home/iclone/.config/acp-iclone/acp")
ENV        = {**os.environ, "ACP_CONFIG_DIR": CONFIG_DIR}
ACP_BIN    = next((p for p in ["/usr/bin/acp", "/usr/local/bin/acp"] if Path(p).exists()), "acp")
MAX_JOBS   = 4
MAX_PRICE  = 0.10

# Agentes externos conhecidos com offerings $0.10 (Virtuals ecosystem)
# Se browse falhar, usamos esta lista de fallback com wallets conhecidas
FALLBACK_TARGETS = [
    # (wallet, offering, description)
    # Deixar em branco — bootstrapper vai descobrir via acp browse
]

def acp(*args, timeout=90):
    r = subprocess.run([ACP_BIN, *args], capture_output=True, text=True, timeout=timeout, env=ENV)
    return r.stdout.strip(), r.stderr.strip(), r.returncode

def browse_candidates():
    """Tenta descobrir agentes via acp browse. Retorna lista de (wallet, offering, price, name)."""
    candidates = []
    for query in ["research", "crypto", "analysis", "trading"]:
        out, err, rc = acp("browse", query, "--top-k", "10",
                           "--sort-by", "successfulJobCount", "--json", timeout=60)
        if not out:
            continue
        try:
            data = json.loads(out)
            agents = data.get("data", data if isinstance(data, list) else [])
            if isinstance(agents, dict):
                agents = agents.get("agents", [])
            for a in (agents or []):
                wallet = (a.get("walletAddress") or "").lower()
                if not wallet:
                    continue
                offerings = a.get("offerings") or a.get("services") or []
                for o in (offerings if isinstance(offerings, list) else []):
                    name = o.get("name") or o.get("offeringName") if isinstance(o, dict) else None
                    raw_price = (o.get("priceV2", {}).get("value") or
                                 o.get("price") or o.get("priceValue") or 999) if isinstance(o, dict) else 999
                    try:
                        price = float(raw_price)
                    except (TypeError, ValueError):
                        continue
                    if name and 0 < price <= MAX_PRICE:
                        candidates.append((wallet, name, price, a.get("name", wallet[:10])))
                        break  # um offering por agente
        except Exception:
            continue
        if len(candidates) >= MAX_JOBS * 3:
            break

    # Dedup por wallet
    seen = set()
    unique = []
    for c in candidates:
        if c[0] not in seen:
            seen.add(c[0])
            unique.append(c)
    return unique

def create_job(wallet, offering, requirements):
    req = json.dumps({"offering_id": offering, **requirements})
    out, err, rc = acp("client", "create-job",
                       "--provider", wallet,
                       "--offering-name", offering,
                       "--requirements", req,
                       "--chain-id", CHAIN_ID, timeout=60)
    blob = out + " " + err
    m = re.search(r"#?(\d{4,})", blob)
    if m:
        return m.group(1)
    return None

def fund_job(job_id):
    out, err, rc = acp("client", "fund", "--job-id", job_id, "--chain-id", CHAIN_ID, timeout=60)
    return rc == 0 or "funded" in (out + err).lower()

def complete_job(job_id):
    out, err, rc = acp("client", "complete", "--job-id", job_id, "--chain-id", CHAIN_ID, timeout=60)
    return rc == 0 or "completed" in (out + err).lower()

def job_status(job_id):
    out, _, _ = acp("job", "history", "--job-id", job_id, "--chain-id", CHAIN_ID, timeout=30)
    if not out:
        return None
    parts = out.splitlines()[0].split("\t")
    return parts[1].strip().lower() if len(parts) > 1 else None

def main():
    print(f"Bootstrap: a contratar {MAX_JOBS} agentes externos a ${MAX_PRICE} cada")
    print("A descobrir candidatos via acp browse...")

    candidates = browse_candidates()
    print(f"Encontrados {len(candidates)} candidatos")

    if not candidates:
        print("ERRO: Nenhum candidato encontrado via browse. Verifica autenticação ACP.")
        sys.exit(1)

    # Seleccionar os primeiros MAX_JOBS únicos
    selected = candidates[:MAX_JOBS]
    jobs = []  # (job_id, wallet, offering, agent_name)

    # Fase 1: Criar todos os jobs
    print(f"\n─── Fase 1: Criar {len(selected)} jobs ───")
    for wallet, offering, price, name in selected:
        print(f"  Criar job → {name} ({offering} @ ${price})")
        job_id = create_job(wallet, offering, {"query": "crypto market analysis"})
        if job_id:
            print(f"  ✅ Job #{job_id} criado")
            jobs.append((job_id, wallet, offering, name))
        else:
            print(f"  ❌ Falhou criar job para {name}")
        time.sleep(5)

    if not jobs:
        print("Nenhum job criado. A terminar.")
        sys.exit(1)

    # Fase 2: Esperar budget_set e fundar
    print(f"\n─── Fase 2: Aguardar budget_set e fundar ───")
    funded = []
    deadline = time.time() + 300  # 5 min para todos ficarem budget_set
    pending = list(jobs)
    while pending and time.time() < deadline:
        for job in list(pending):
            job_id, wallet, offering, name = job
            st = job_status(job_id)
            if st in ("budget_set", "budgetset"):
                print(f"  Job #{job_id} budget_set — a fundar...")
                if fund_job(job_id):
                    print(f"  ✅ Job #{job_id} fundado")
                    funded.append(job)
                else:
                    print(f"  ❌ Job #{job_id} fundo falhou")
                pending.remove(job)
            elif st in ("rejected", "expired", "cancelled"):
                print(f"  ⚠️  Job #{job_id} estado terminal: {st}")
                pending.remove(job)
        if pending:
            time.sleep(15)

    if not funded:
        print("Nenhum job fundado. A terminar.")
        sys.exit(1)

    # Fase 3: Monitorizar até entrega e completar
    print(f"\n─── Fase 3: Monitorizar {len(funded)} jobs até entrega ───")
    completed = []
    deadline = time.time() + 1800  # 30 min para todos serem entregues
    pending = list(funded)
    while pending and time.time() < deadline:
        for job in list(pending):
            job_id, wallet, offering, name = job
            st = job_status(job_id)
            print(f"  Job #{job_id} ({name}/{offering}): {st}")
            if st == "submitted":
                if complete_job(job_id):
                    print(f"  ✅ Job #{job_id} completo — escrow libertado!")
                    completed.append(job)
                else:
                    print(f"  ❌ Job #{job_id} complete falhou")
                pending.remove(job)
            elif st in ("completed",):
                print(f"  ✅ Job #{job_id} já completo")
                completed.append(job)
                pending.remove(job)
            elif st in ("rejected", "expired", "cancelled"):
                print(f"  ⚠️  Job #{job_id} terminal: {st}")
                pending.remove(job)
        if pending:
            time.sleep(30)

    print(f"\n═══ Bootstrap concluído ═══")
    print(f"  Jobs criados: {len(jobs)}")
    print(f"  Jobs fundados: {len(funded)}")
    print(f"  Jobs completos: {len(completed)}")
    print(f"  Gasto total: ${len(funded) * MAX_PRICE:.2f}")
    print("Bootstrap terminado. Somos visíveis no marketplace.")

if __name__ == "__main__":
    main()
