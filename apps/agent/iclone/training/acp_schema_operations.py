"""
ACP Schema Operations — Skill autónoma para iCLONE

Conhecimento validado em sessão real 2026-06-15.
Cobre três capacidades autónomas:
  1. Publicar / actualizar offerings via JSON + CLI
  2. Corrigir schema mismatches em offerings existentes
  3. Diagnosticar e reparar falhas de jobs (asset_symbol / topic / query)

Este módulo é importado pelo scheduler e pelo agente directamente.
"""

import json
import logging
import os
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger("iclone.training.acp_schema_ops")

ACP_BIN = next(
    (p for p in ["/opt/homebrew/bin/acp", "/usr/local/bin/acp"] if os.path.exists(p)),
    "acp",
)
ICLONE_CONFIG = str(Path.home() / ".config/acp-iclone/acp")


# ═══════════════════════════════════════════════════════════════════════════════
# KNOWLEDGE BASE — o que o agente sabe sobre publicação de jobs
# ═══════════════════════════════════════════════════════════════════════════════

OFFERING_JSON_SCHEMA = """
SCHEMA CORRECTO PARA PUBLICAR JOBS (validado 2026-06-15)
=========================================================

Ficheiro JSON de topo:
  { "jobs": [ <job>, <job>, ... ] }

CAMPOS OBRIGATÓRIOS de cada job:
  name          — camelCase ou snake_case. NUNCA espaços. ex: "tokenResearchStandard"
  description   — string descritiva
  requirement   — SINGULAR. string ou JSON schema. ex: "Token symbol ou topic query"
  deliverable   — string descritiva do output
  price         — OBJECTO: {"type": "fixed", "value": 0.05}
                  NÃO número. NÃO string. NÃO "priceValue"/"priceType" separados.
  slaMinutes    — número em MINUTOS (mínimo 5). ex: 120
  requiredFunds — boolean. True só para jobs que gerem capital do cliente.

ERROS COMUNS E FIXES:
  ✗ "price": 0.05                → ✓ "price": {"type": "fixed", "value": 0.05}
  ✗ "priceV2": {...}             → ✓ "price": {...}
  ✗ "requirements": "..."        → ✓ "requirement": "..."  (singular!)
  ✗ "name": "Token Research"     → ✓ "name": "tokenResearch"
  ✗ "slaMinutes": "120"          → ✓ "slaMinutes": 120

EXEMPLO COMPLETO VÁLIDO:
{
  "jobs": [
    {
      "name": "tokenResearchStandard",
      "description": "Research report on a crypto token or topic.",
      "requirement": "Send either: token (crypto symbol like BTC, ETH) OR topic (free-form research query). Optional: format (markdown/json).",
      "deliverable": "JSON: {summary, sources[], key_facts[], confidence}",
      "price": {"type": "fixed", "value": 0.05},
      "slaMinutes": 120,
      "requiredFunds": false
    }
  ]
}

PUBLICAR VIA CLI:
  acp offering create --file offerings.json
  (ou via Virtuals OS: app.virtuals.io/os → Import Agent Jobs)

ACTUALIZAR VIA CLI (sem JSON):
  acp offering update --offering-id <id> --requirements '<nova descrição>'
  acp offering update --offering-id <id> --price-value 0.10 --price-type fixed
"""

DUAL_FIELD_CONTRACT = """
CONTRATO DUAL-FIELD (padrão validado 2026-06-15)
=================================================

O problema: clientes externos enviam campos diferentes dos declarados nas offerings.
  - VEGETA envia: {"topic": "...", "format": "markdown"}
  - Offering declarava: "Token name or symbol"
  - Resultado: falha intermitente no backend de cumprimento

A SOLUÇÃO em duas camadas:

CAMADA 1 — Offering requirement (o que o cliente vê no marketplace):
  "Send either: (A) token — crypto symbol like BTC, ETH for price analysis;
   or (B) topic — free-form research query for any subject.
   Optional: format (markdown/json)."

CAMADA 2 — execution_engine.py (como o código executa):
  # Token prioritário, topic como fallback — NUNCA falha
  "tokenResearchStandard": lambda:
    self.wallet.crypto_research_quick(r.get("token", r.get("asset_symbol", "")))
    if (r.get("token") or r.get("asset_symbol"))
    else self.research.web_research_standard(
      r.get("topic", r.get("query", "crypto market overview")), "standard"
    ),

REGRA: qualquer offering de pesquisa DEVE aceitar topic/query como fallback.
       Nenhum campo deve ser estritamente obrigatório para offerings de pesquisa.
"""

SCHEMA_MISMATCH_DIAGNOSIS = """
DIAGNÓSTICO DE SCHEMA MISMATCH (protocolo autónomo)
====================================================

SINTOMAS:
  - Log: "Execution failed for job XXXXX: asset_symbol is required"
  - Log: "Execution failed for job XXXXX: query is required"
  - Log: "Research failed: Unterminated string starting at..."
  - Jobs em SUBMITTED com deliverable {"error": "...", "status": "failed"}

INVESTIGAÇÃO AUTÓNOMA:
  1. Ver o que o cliente enviou:
     acp job history --job-id XXXXX --chain-id 8453
     → ler o campo content do evento job.created

  2. Ver o que a offering declara:
     acp offering list --json | grep -A5 <offering_name>

  3. Ver o que o execution engine espera:
     grep -n '"<offering_name>"' agent/iclone/skills/execution_engine.py

  4. Identificar o campo em falta (ex: client enviou topic, engine esperava token)

FIXES DISPONÍVEIS (por ordem de impacto):
  A. Corrigir execution_engine.py — adicionar fallback para o campo que o cliente envia
     Padrão: r.get("token", r.get("asset_symbol", r.get("topic", r.get("query", "default"))))

  B. Actualizar requirement da offering — informar clientes do campo correcto:
     acp offering update --offering-id <id> --requirements '<descrição dual-field>'

  C. Ambos A+B — fix completo (recomendado)

NOTA: Jobs já submetidos com erro NÃO são recuperáveis.
      Vão para rejected quando o cliente avaliar, ou expiram.
      A prevenção está nas camadas A+B acima.
"""

TOKEN_REFRESH_KNOWLEDGE = """
GESTÃO DE TOKENS ACP CLI (validado 2026-06-15)
===============================================

ARQUITECTURA DOS TOKENS:
  - Access token: válido 60 minutos
  - Refresh token: rotativo, expira se não usado ~24h
  - Armazenamento: file keyring em ~/.config/acp-<agent>/acp/ (NÃO macOS keychain)
  - O CLI gere refresh internamente em cada chamada bem-sucedida

ESTRATÉGIA DE KEEP-ALIVE:
  - Chamar `acp agent whoami` a cada 20 minutos para forçar refresh
  - Se whoami retorna "Session expired": refresh token morto → re-login manual
  - Re-login: acp configure → abrir URL no browser → acp configure complete --request-id <id>

MÚLTIPLOS AGENTES (cada um tem config dir isolada):
  ACP_CONFIG_DIR=~/.config/acp-iclone/acp   → iCLONE (provider)
  ACP_CONFIG_DIR=~/.config/acp-vegeta/acp   → VEGETA (client)

INJECTAR EM TODOS OS SUBPROCESSOS:
  env = {**os.environ, "ACP_CONFIG_DIR": config_dir}
  subprocess.run([ACP_BIN, "job", "list", "--json"], env=env, ...)

NUNCA usar acp agent use / switch_to — causa timeouts e conflitos.
"""

JOB_LIFECYCLE_KNOWLEDGE = """
CICLO DE VIDA DE UM JOB ACP (perspectiva provider + client)
=============================================================

ESTADOS (uppercase na API v2):
  OPEN      → provider deve chamar: acp provider set-budget --job-id X --amount Y
  BUDGET_SET → client deve chamar: acp client fund --job-id X
  FUNDED    → provider executa e chama: acp provider submit --job-id X --deliverable '...'
  SUBMITTED → client avalia e chama: acp client complete --job-id X (liberta escrow)
  COMPLETED → payment released para provider ✓
  REJECTED  → client rejeitou deliverable (reputação afectada)
  EXPIRED   → timeout SLA

NOTA CRÍTICA — DISCREPÂNCIA DE ESTADOS:
  acp job list  → pode mostrar OPEN quando o job está realmente em BUDGET_SET
  acp job history --job-id X → mostra o estado real (ler a primeira linha: ID\tSTATUS\tCOUNT)

PROVIDER SERVER (iCLONE) — o que faz em cada estado:
  OPEN    → set-budget (preço da offering)
  FUNDED  → engine.execute(offering_id, requirements) → acp provider submit --deliverable '{...}'
  outros  → ignora (VEGETA que fecha)

CLIENT AUTOPILOT (VEGETA) — o que faz em cada estado:
  BUDGET_SET → acp client fund --job-id X --chain-id 8453
  SUBMITTED  → acp client complete --job-id X --chain-id 8453

RECUPERAÇÃO APÓS RESTART:
  - provider: budget_set_jobs e submitted_jobs são perdidos em memória
    → o server re-tenta set-budget em OPEN; ACP endpoint retorna erro "already set" (ignorar)
  - client: chamar get_job_status() via job history para cada job activo no startup
"""


# ═══════════════════════════════════════════════════════════════════════════════
# SKILL — operações autónomas
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class SchemaOpResult:
    success: bool
    action: str
    details: str = ""
    errors: list[str] = field(default_factory=list)


class ACPSchemaOperationsSkill:
    """
    Skill autónoma para iCLONE gerir e corrigir offering schemas.

    Uso:
        skill = ACPSchemaOperationsSkill()
        result = skill.update_offering_requirement("019ebe48-c616-...", "token OR topic")
        result = skill.publish_offerings_from_json(offerings_list)
        result = skill.diagnose_job_failure(job_id)
        result = skill.fix_execution_engine_dispatch(offering_name, fields_client_sends)
    """

    def __init__(self, config_dir: str = ICLONE_CONFIG):
        self.config_dir = config_dir
        self.env = {**os.environ, "ACP_CONFIG_DIR": config_dir}

    def _acp(self, *args: str, timeout: int = 30) -> tuple[str, str, int]:
        r = subprocess.run(
            [ACP_BIN, *args],
            capture_output=True, text=True, timeout=timeout, env=self.env,
        )
        return r.stdout.strip(), r.stderr.strip(), r.returncode

    # ── 1. Listar offerings com IDs ──────────────────────────────────────────

    def list_offerings(self) -> list[dict]:
        """Retorna todas as offerings do agente activo com id, name, requirements."""
        out, err, rc = self._acp("offering", "list", "--json")
        if rc != 0:
            logger.error("list_offerings failed: %s", err)
            return []
        try:
            data = json.loads(out)
            return data if isinstance(data, list) else data.get("offerings", [])
        except json.JSONDecodeError:
            return []

    def get_offering_id(self, name: str) -> str | None:
        """Resolve o UUID de uma offering pelo nome."""
        for o in self.list_offerings():
            if o.get("name") == name:
                return o.get("id")
        return None

    # ── 2. Actualizar requirement de uma offering ────────────────────────────

    def update_offering_requirement(self, offering_id: str, requirement: str) -> SchemaOpResult:
        """
        Actualiza o campo requirement de uma offering existente.

        Exemplo:
            skill.update_offering_requirement(
                "019ebe48-c616-...",
                "Send either: token (BTC, ETH) OR topic (free-form query)"
            )
        """
        out, err, rc = self._acp(
            "offering", "update",
            "--offering-id", offering_id,
            "--requirements", requirement,
        )
        if "updated successfully" in out.lower() or rc == 0:
            logger.info("Offering %s requirement updated ✓", offering_id)
            return SchemaOpResult(success=True, action="update_requirement", details=out[:200])
        return SchemaOpResult(success=False, action="update_requirement", errors=[err or out])

    def fix_offering_dual_field(self, offering_name: str,
                                 primary_field: str, fallback_field: str = "topic") -> SchemaOpResult:
        """
        Aplica o padrão dual-field a uma offering: aceita primary_field OU fallback_field.
        Resolve o offering_id automaticamente pelo nome.
        """
        oid = self.get_offering_id(offering_name)
        if not oid:
            return SchemaOpResult(
                success=False, action="fix_dual_field",
                errors=[f"Offering '{offering_name}' not found"]
            )
        requirement = (
            f"Send either: (A) {primary_field} — the primary input for this service; "
            f"or (B) {fallback_field} — free-form query describing what you need. "
            f"Optional: format (markdown/json). Both fields are optional; providing either is enough."
        )
        return self.update_offering_requirement(oid, requirement)

    # ── 3. Publicar novas offerings via JSON ─────────────────────────────────

    def build_offering_json(self, offerings: list[dict]) -> str:
        """
        Constrói o JSON correcto para publicar offerings.

        Cada dict deve ter: name, description, requirement, deliverable,
                            price_usdc (float), sla_minutes (int), required_funds (bool)

        Exemplo:
            skill.build_offering_json([{
                "name": "tokenResearchStandard",
                "description": "Research report on a crypto token or topic.",
                "requirement": "token (BTC, ETH) OR topic (free-form query)",
                "deliverable": "JSON: {summary, sources[], key_facts[], confidence}",
                "price_usdc": 0.05,
                "sla_minutes": 120,
                "required_funds": False,
            }])
        """
        jobs = []
        for o in offerings:
            jobs.append({
                "name": o["name"],
                "description": o["description"],
                "requirement": o["requirement"],
                "deliverable": o["deliverable"],
                "price": {"type": "fixed", "value": float(o.get("price_usdc", 0.05))},
                "slaMinutes": int(o.get("sla_minutes", 120)),
                "requiredFunds": bool(o.get("required_funds", False)),
            })
        return json.dumps({"jobs": jobs}, indent=2)

    def publish_offerings_from_json(self, offerings: list[dict],
                                     json_path: str = "/tmp/acp_offerings_publish.json") -> SchemaOpResult:
        """
        Publica uma lista de offerings via acp offering create --file.
        Grava o JSON no path indicado e chama o CLI.
        """
        payload = self.build_offering_json(offerings)
        Path(json_path).write_text(payload)
        logger.info("Wrote %d offerings to %s", len(offerings), json_path)

        out, err, rc = self._acp("offering", "create", "--file", json_path, timeout=60)
        if rc == 0 or "success" in out.lower() or "created" in out.lower():
            logger.info("Published %d offerings ✓", len(offerings))
            return SchemaOpResult(success=True, action="publish", details=out[:400])
        return SchemaOpResult(
            success=False, action="publish",
            errors=[err or out],
            details=f"JSON written to {json_path} — check for schema errors above",
        )

    # ── 4. Diagnóstico autónomo de falha de job ──────────────────────────────

    def diagnose_job_failure(self, job_id: str, chain_id: int = 8453) -> SchemaOpResult:
        """
        Investiga um job falhado: lê o histórico, identifica o campo em falta,
        e sugere a correcção exacta para execution_engine.py.
        """
        out, err, rc = self._acp(
            "job", "history", "--job-id", job_id, "--chain-id", str(chain_id)
        )
        if not out:
            return SchemaOpResult(success=False, action="diagnose", errors=["No history found"])

        # Extrair requirements enviados pelo cliente
        client_requirements: dict = {}
        offering_name = ""
        for line in out.splitlines():
            try:
                data = json.loads(line)
                if isinstance(data, dict):
                    offering_name = data.get("offering_id", data.get("offeringName", ""))
                    client_requirements = data
                    break
            except (json.JSONDecodeError, TypeError):
                pass

        # Detectar campos presentes
        present = [k for k in client_requirements if k not in ("offering_id", "format")]
        missing_common = []
        if not client_requirements.get("token") and not client_requirements.get("asset_symbol"):
            missing_common.append("token/asset_symbol")
        if not client_requirements.get("topic") and not client_requirements.get("query"):
            missing_common.append("topic/query")

        diagnosis = (
            f"Job {job_id} | Offering: {offering_name}\n"
            f"Client sent fields: {present}\n"
            f"Client requirements: {json.dumps(client_requirements)[:300]}\n"
        )

        fix_suggestion = ""
        if offering_name:
            sent_field = present[0] if present else "topic"
            fix_suggestion = (
                f"\nFIX em execution_engine.py:\n"
                f'  "{offering_name}": lambda: self.research.web_research_standard(\n'
                f'    r.get("{sent_field}", r.get("token", r.get("topic", r.get("query", "")))),\n'
                f'    "standard"\n'
                f'  ),\n'
                f"\nFIX no marketplace:\n"
                f"  acp offering update --offering-id <id> "
                f"--requirements 'Send either: token OR {sent_field} OR topic'\n"
            )

        logger.info("Diagnosis for job %s:\n%s%s", job_id, diagnosis, fix_suggestion)
        return SchemaOpResult(
            success=True, action="diagnose",
            details=diagnosis + fix_suggestion,
        )

    # ── 5. Audit autónomo de todas as offerings ──────────────────────────────

    def audit_all_offerings(self) -> list[SchemaOpResult]:
        """
        Verifica todas as offerings e identifica as que não têm o padrão dual-field.
        Retorna lista de issues encontrados.
        """
        offerings = self.list_offerings()
        issues = []
        keywords_ok = ["or", "either", "topic", "query", "optional"]

        for o in offerings:
            req = str(o.get("requirements", o.get("requirement", ""))).lower()
            has_dual = any(kw in req for kw in keywords_ok)
            if not has_dual:
                issue = SchemaOpResult(
                    success=False,
                    action="audit",
                    details=(
                        f"Offering '{o.get('name')}' ({o.get('id')}) "
                        f"tem requirement rígido: '{req[:80]}' — "
                        f"adicionar fallback topic/query"
                    ),
                )
                issues.append(issue)

        if not issues:
            logger.info("Audit passed — all %d offerings have flexible requirements ✓", len(offerings))
        else:
            logger.warning("Audit found %d offerings with rigid requirements", len(issues))
        return issues


# ═══════════════════════════════════════════════════════════════════════════════
# TRAINING — função de treino chamada pelo scheduler
# ═══════════════════════════════════════════════════════════════════════════════

TRAINING_KNOWLEDGE = {
    "topic": "ACP Schema Operations & Offering Management",
    "validated_date": "2026-06-15",
    "sections": {
        "offering_json_schema": OFFERING_JSON_SCHEMA,
        "dual_field_contract": DUAL_FIELD_CONTRACT,
        "schema_mismatch_diagnosis": SCHEMA_MISMATCH_DIAGNOSIS,
        "token_refresh": TOKEN_REFRESH_KNOWLEDGE,
        "job_lifecycle": JOB_LIFECYCLE_KNOWLEDGE,
    },
    "key_commands": [
        "acp offering list --json",
        "acp offering update --offering-id <id> --requirements '<text>'",
        "acp offering create --file offerings.json",
        "acp offering update --offering-id <id> --price-value 0.05 --price-type fixed",
        "acp job history --job-id <id> --chain-id 8453",
        "acp provider set-budget --job-id <id> --amount 0.05 --chain-id 8453 --json",
        "acp provider submit --job-id <id> --deliverable '<json>' --chain-id 8453 --json",
        "acp client fund --job-id <id> --chain-id 8453",
        "acp client complete --job-id <id> --chain-id 8453",
    ],
    "patterns_learned": [
        "requirement field is SINGULAR in JSON ('requirement', not 'requirements')",
        "price must be object: {'type': 'fixed', 'value': 0.05} — never a bare number",
        "offering names must be camelCase — spaces cause rejection",
        "acp job list may show OPEN when real state is BUDGET_SET — always use job history for ground truth",
        "ACP_CONFIG_DIR must be injected in ALL subprocesses — never use default config for multi-agent setups",
        "execution_engine dispatch: always fallback chain r.get('token', r.get('asset_symbol', r.get('topic', r.get('query', 'default'))))",
        "token refresh: call acp agent whoami every 20min — CLI handles rotation internally",
        "server execution: wrap engine.execute() in ThreadPoolExecutor with timeout=120 to prevent hangs",
    ],
}


def run_training() -> dict:
    """Executa treino de schema operations. Chamado pelo scheduler."""
    logger.info("ACP Schema Operations training starting...")

    skill = ACPSchemaOperationsSkill()

    # Audit offerings actuais
    issues = skill.audit_all_offerings()

    # Auto-fix offerings com requirement rígido
    fixed = 0
    for issue in issues:
        if issue.details:
            # Extrair offering_id do details
            parts = issue.details.split("(")
            if len(parts) > 1:
                oid = parts[1].split(")")[0].strip()
                name = issue.details.split("'")[1] if "'" in issue.details else ""
                if oid and name:
                    result = skill.fix_offering_dual_field(name, "token", "topic")
                    if result.success:
                        fixed += 1
                        logger.info("Auto-fixed offering '%s' ✓", name)

    summary = {
        "topic": TRAINING_KNOWLEDGE["topic"],
        "offerings_audited": len(skill.list_offerings()),
        "issues_found": len(issues),
        "auto_fixed": fixed,
        "knowledge_sections": list(TRAINING_KNOWLEDGE["sections"].keys()),
        "key_commands_count": len(TRAINING_KNOWLEDGE["key_commands"]),
        "patterns_learned": len(TRAINING_KNOWLEDGE["patterns_learned"]),
    }
    logger.info("ACP Schema Operations training complete: %s", summary)
    return summary
