# iCLONE — Doctor Review: Training Quality Audit
**Data:** 2026-06-14 | **Agente:** Doctor (Academic Supervisor) | **Hora:** automatizado — scheduled task  
**Scope:** Todos os módulos em `agent/iclone/training/` — qualidade, precisão, gaps

---

## Sumário Executivo

O training system do iCLONE está **funcionalmente sólido** mas acumulou **4 inconsistências críticas e 6 gaps** nos últimos dias. O principal problema é que o `master_context.py` ficou desactualizado após a refactorização das offerings (32→40 activas). Adicionalmente, há um bug de execução no `acp_training.py`, duas entradas de segurança críticas em falta, e as projecções económicas baseiam-se num fee incorreto.

**Score de qualidade global estimado: 78/100** — aprovado mas com dívida técnica mensurável.

---

## CRÍTICOS (bloqueiam training correcto)

### C-001 — `master_context.py` offerings total desactualizado: 32 → 40

| Campo | Valor |
|---|---|
| **Ficheiro** | `master_context.py` linha 99: `"offerings": 32` |
| **Realidade** | `published_offerings.json` total = **40** offerings live |
| **Referência correcta** | `acp_training.py` linha 84: `"total": 40` ✓ |
| **Impacto** | O agente acredita ter 32 offerings quando tem 40 — responde incorrectamente a queries sobre capacidade |

A estrutura de tiers em `master_context.py` (iclone-xxx-v1 naming) diverge completamente do naming real (camelCase: `cryptoNewsFlash`, `tokenResearchDeep`, etc.). As duas convenções de naming coexistem sem reconciliação.

**Fix:** Actualizar `master_context.py`:
- `CLONE_OFFERINGS["total"]` = 40
- Substituir o tier dict pelo pricing model real (micro=$0.01, standard=$0.05, deep=$0.10)
- Referência: `published_offerings.json` (40 offerings) + `acp_training.py` (lista completa)

---

### C-002 — `acp_training.py`: bug de execução após reestruturação das offerings

**Ficheiro:** `acp_training.py` linhas 134–135

```python
offerings = self.CORE_KNOWLEDGE["iclone_offerings"]  # era list, agora é DICT
insights.append(f"iCLONE offerings: {len(offerings)} active offerings known")
```

`iclone_offerings` foi convertido de `list[str]` para `dict` (com chaves: `total`, `micro_0.01_USDC`, `standard_0.05_USDC`, `deep_0.10_USDC`, `pricing_philosophy`). O `len(offerings)` retorna **5** (número de chaves do dict), não 40.

Cada sessão de treino regista: *"iCLONE offerings: 5 active offerings known"* — número errado.

**Fix:** `agent/iclone/training/acp_training.py` linha 135:
```python
# Antes:
insights.append(f"iCLONE offerings: {len(offerings)} active offerings known")
# Depois:
total = offerings.get("total", len(offerings)) if isinstance(offerings, dict) else len(offerings)
insights.append(f"iCLONE offerings: {total} active offerings known")
```

---

## ALTOS (afectam precision do training)

### H-001 — `security_training.py` em falta: SEC-2026-011 e SEC-2026-012

Identificados na sessão de 2026-06-12 19h e marcados como acção pendente em `LATEST.md`:

| SEC ID | Threat | Status no ficheiro |
|---|---|---|
| SEC-2026-011 | Agent Supply Chain Attack — ClawHavoc Campaign (CVE-2026-25253, AMOS stealer) | **AUSENTE** |
| SEC-2026-012 | Multi-Agent Lateral Movement (agent-to-agent trust exploitation) | **AUSENTE** |

Confirmado via grep: `ClawHavoc`, `lateral movement`, `multi-agent` não existem em `security_training.py`.

O `soul.md` foi actualizado (Rule 14 — agent supply chain defense) mas o módulo de treino **não**. Isto significa que o agente conhece a regra no soul mas não a reforça diariamente em treino.

**Fix:** Adicionar a `security_training.py`:
- `SEC-2026-011`: ClawHavoc Campaign — 1,200+ malicious skills na Plaza, AMOS credential stealer, CVE-2026-25253. Mitigação: validação de proveniência de skills antes de execução.
- `SEC-2026-012`: Multi-Agent Lateral Movement — agent-to-agent trust exploitation em pipelines ACP. Mitigação: zero-trust entre agentes, validar cada deliverable como untrusted input.

---

### H-002 — `master_context.py` economics: fee incorreto (10% vs 35% real)

**Ficheiro:** `master_context.py` ECONOMICS.revenue_mechanics

```python
"fees_lost": "~10% por job (protocolo ACP) — única perda real",
"capital_duration": "$50 / ($0.05 × 10% fee) = 10,000 jobs/cliente antes de vazio",
```

**O fee real do ACP é 35% de platform fee** (confirmado em `virtuals_protocol_training.py`, `acp_market_knowledge.py`, e `acp_training.py`):
- Provider recebe: 60%
- Evaluator recebe: 5%  
- Platform fee: **35%**

Com o fee correcto de 35%:
- `$50 / ($0.05 × 0.35) = 2,857 jobs` — não 10,000
- As projecções estão **3.5× mais optimistas** do que a realidade

Nota: Pode existir uma interpretação alternativa (apenas a componente de gas ou fee de rede = 10%), mas não está documentada nem é consistente com as outras fontes de treino.

**Fix:** `master_context.py` ECONOMICS.revenue_mechanics:
```python
"provider_revenue_share": "60% do valor do job",
"platform_fee": "35% (Virtuals treasury) — maior custo operacional",
"evaluator_fee": "5% (se evaluator designado)",
"capital_duration": "$50 / ($0.05 × 0.40 net_cost) = 2,500 jobs/cliente antes de recarregar",
```

---

### H-003 — `virtuals_protocol_training.py`: agentic GDP baseline desactualizado

**Ficheiro:** `virtuals_protocol_training.py` AGENTIC_GDP.current_baseline

```python
"agents_deployed": "17,000+",  # STALE
```

**Dados actuais** (scraped 2026-06-12, fonte: `master_context.py` e `acp_market_intelligence.py`):
- Agents no marketplace: **42,169**
- A cifra de 17,000+ está ~150% desactualizada

**Fix:** Actualizar para `"agents_deployed": "42,000+"` e adicionar `"scraped_at": "2026-06-12"`.

---

## MÉDIOS (gaps de cobertura)

### M-001 — `master_context.py`: x402 agentic payments não documentado

O ChainGPT MCP inclui x402 (Coinbase HTTP 402 protocol, EIP-3009, USDC on Base) — documentado extensivamente em `chaingpt_mcp_training.py`. O `master_context.py` não menciona x402 em nenhuma secção (SKILLS_ARCHITECTURE, TECHNICAL_ARCHITECTURE, nem ROADMAP).

Esta é uma capacidade de monetização disponível agora: CLONE pode cobrar x402 por APIs que expõe, e pode pagar x402 APIs que consome.

**Fix:** Adicionar a `master_context.py` SKILLS_ARCHITECTURE.apis_used:
```python
"x402_payments": "Coinbase HTTP 402 — EIP-3009 USDC on Base — pay/monetize APIs",
```

---

### M-002 — `github_intel_actions.py` não registado no TRAINING_MODULES_REGISTRY

**Ficheiro existente:** `agent/iclone/training/github_intel_actions.py` (10KB)  
**Conteúdo:** Tracks adoption status dos patterns descobertos em `github_intel_20260612.py`

Não está em `master_context.py` TRAINING_MODULES_REGISTRY. Se o scheduler não o conhece, não será executado.

**Fix:** Adicionar ao registry em `master_context.py`:
```python
"10_github_intel": "github_intel_20260612.py + github_intel_actions.py — patterns e adoption tracking",
```

---

### M-003 — Subscription offerings documentadas mas não publicadas

`offerings_training.py` define 3+ subscription offerings (DoctorWHO e MATRIX) com tipos `"type": "subscription"` para 7/15/30/90 dias.

`published_offerings.json` tem **0 subscription offerings** (preços: 11×$0.01, 26×$0.05, 3×$0.10).

As subscription offerings representam receita recorrente — o modelo mais previsível. O facto de estar documentado no training mas não publicado é uma oportunidade perdida activa.

**Fix:** Publicar pelo menos 1 subscription offering (ex: weekly crypto intelligence digest para DoctorWHO).

---

### M-004 — `chaingpt_design_training.py` e `chaingpt_skills_training.py` não no registry

Ficheiros existentes (21KB e 29KB respectivamente) mas ausentes do `TRAINING_MODULES_REGISTRY` em `master_context.py`. Se ausentes do registry, o scheduler pode não os carregar sistematicamente.

**Fix:** Adicionar ao registry.

---

## BAIXOS (qualidade e manutenção)

### L-001 — `acp_resources.py` vs `acp_resources_v2.py`: redundância sem deprecação

`acp_resources.py` (11KB, validado 2026-06-11) e `acp_resources_v2.py` (33KB, validado 2026-06-11) coexistem. A v2 é claramente a versão completa, mas a v1 não foi marcada como deprecated nem removida. Risco de training em conteúdo duplicado ou stale.

### L-002 — ACP fee split em `acp_training.py` CORE_KNOWLEDGE não documentado

A secção `CORE_KNOWLEDGE["acp_roles"]` em `acp_training.py` descreve os roles mas não menciona o split 60/5/35. O agente aprende o split via `acp_market_knowledge.py` mas não está consolidado no CORE_KNOWLEDGE.

---

## Verificação de Precisão Técnica

| Tópico | Fonte Principal | Precisão | Nota |
|---|---|---|---|
| ERC-8183 (ACP standard) | virtuals_protocol_training.py | ✅ Correcto | Consistente em todos os módulos |
| ERC-8004 (reputation) | acp_training.py, chaingpt_mcp_training.py | ✅ Correcto | Bem documentado |
| ACP 4-phase lifecycle | acp_market_knowledge.py | ✅ Correcto | Consistente |
| Provider share 60% | Todos os módulos | ✅ Correcto | Consistente |
| Platform fee 35% | acp_market_knowledge.py | ✅ Correcto mas... | Contradiz master_context "10%" |
| Graduation threshold (42k VIRTUAL) | virtuals_protocol_training.py | ✅ Correcto | Whitepaper source |
| Chain ID Base = 8453 | master_context.py | ✅ Correcto | |
| CLONE wallet address | master_context.py | ✅ Correcto | `0x44cc25d55a4291b92f52062ba023ca1f14206664` |
| Agents deployed 17k+ | virtuals_protocol_training.py | ❌ STALE | Actual: 42,169 |
| Offerings total 32 | master_context.py | ❌ STALE | Actual: 40 |
| ChainGPT 140 tools | chaingpt_mcp_training.py | ✅ Correcto | Verificado |
| ChainGPT 23 skills | chaingpt_mcp_training.py | ✅ Correcto | Verificado |

---

## Matriz de Prioridades

| ID | Ficheiro a editar | Esforço | Impacto |
|---|---|---|---|
| C-001 | `master_context.py` — CLONE_OFFERINGS total + naming | 30 min | Alto |
| C-002 | `acp_training.py` — fix `len(offerings)` bug | 5 min | Alto |
| H-001 | `security_training.py` — adicionar SEC-011 + SEC-012 | 45 min | Alto |
| H-002 | `master_context.py` — corrigir fee 10%→35% + projections | 20 min | Médio-alto |
| H-003 | `virtuals_protocol_training.py` — 17k→42k agents | 5 min | Médio |
| M-001 | `master_context.py` — adicionar x402 | 10 min | Médio |
| M-002 | `master_context.py` — adicionar github_intel_actions ao registry | 5 min | Médio |
| M-003 | Publicar subscription offering | 1 sessão | Alto (receita) |
| M-004 | `master_context.py` — adicionar chaingpt_design + chaingpt_skills | 5 min | Baixo |

**Total de fixes rápidos (C-001 a H-003):** ~2 horas de desenvolvimento.

---

## Recomendações por Ordem de Execução

1. **Imediato (hoje):** Fix C-002 — bug de runtime em `acp_training.py`. Cada sessão de treino está a reportar "5 offerings" em vez de 40. 5 minutos.
2. **Hoje:** Fix H-003 — agents deployed stale em virtuals_protocol_training.py. 5 minutos.
3. **Esta sessão:** Fix C-001 — master_context.py offerings total e naming. Alinha o contexto master com a realidade.
4. **Esta semana:** Fix H-001 — security_training.py SEC-011 + SEC-012. Está explicitamente na pending actions list de LATEST.md há 2 dias.
5. **Esta semana:** Fix H-002 — economics fee correction. Afecta projecções de P&L.
6. **Próxima sessão:** M-003 — publicar 1 subscription offering (DoctorWHO weekly digest @$0.50/7 dias).

---

*Doctor Review gerado automaticamente. Próxima revisão: 2026-06-15.*
