# 📚 Treino — Especialidade (Ter/Qui) — 2026-08-11

_Sessão: Scheduled · 05:49 UTC · 2/2 agentes treinados._

## Resumo

| Agente | Módulos de hoje | Drills | Sessões totais |
| --- | --- | --- | --- |
| **doctor-agent** | The review craft — reading a paper the IST way · IST academic standards — writing at Técnico level | 3/3 ✅ | 4 |
| **forense-ai** | Digital evidence — preserve first, analyse second · Root-cause investigation — to the origin, always | 3/3 ✅ | 4 |

## Tópicos cobertos hoje

- Digital evidence — preserve first, analyse second
- IST academic standards — writing at Técnico level
- Root-cause investigation — to the origin, always
- The review craft — reading a paper the IST way

## Por agente

### doctor-agent — academic rigor (IST)
Foco: IST-standard papers and dissertations; the university's scientific repository.
- Estudou **The review craft — reading a paper the IST way** → skill actualizada em `training/skills/doctor-agent/d3-review-craft.md`
- Estudou **IST academic standards — writing at Técnico level** → skill actualizada em `training/skills/doctor-agent/d1-ist-standards.md`
- Drills: todos verificados ✅
- Sonda web: Técnico Scholar — repositório científico do IST → ✅ HTTP 200 — “Search - Scholar” (<https://scholar.tecnico.ulisboa.pt>)
- Sonda web: Repositório da Universidade de Lisboa → ✅ HTTP 200 — “Repositório :: Página inicial” (<https://repositorio.ulisboa.pt>)

### forense-ai — forensics / investigation
Foco: tracing any incident to its origin; evidence-first method on the open web.
- Estudou **Digital evidence — preserve first, analyse second** → skill actualizada em `training/skills/forense-ai/f3-digital-evidence.md`
- Estudou **Root-cause investigation — to the origin, always** → skill actualizada em `training/skills/forense-ai/f1-root-cause.md`
- Drills: todos verificados ✅
- Sonda web: Internet Archive — Wayback Machine → ✅ HTTP 200 — “Wayback Machine” (<https://web.archive.org>)
- Sonda web: Certificate Transparency — crt.sh → ⚠️ inacessível (TimeoutError) — treino continua com o currículo (<https://crt.sh>)

## Camada LLM (coach)

sem créditos na API Anthropic — o treino correu completo no núcleo determinístico. (Repor créditos reactiva esta camada sozinha.)

## Próxima sessão

Módulos seguintes: The university's scientific repository — Doctor's home ground · The review craft — reading a paper the IST way

---
_Sistema único de treino (hub devclone20/iclone). Frota Seg/Qua/Sex · Especialidade Ter/Qui (doctor-agent: padrão IST + repositório científico · forense-ai: investigação até à origem na web aberta). Lei da frota: quarentena de 14 dias para qualquer pacote._
