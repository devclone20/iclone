# 📚 Treino — Especialidade (Ter/Qui) — 2026-08-18

_Sessão: Scheduled · 05:22 UTC · 2/2 agentes treinados._

## Resumo

| Agente | Módulos de hoje | Drills | Sessões totais |
| --- | --- | --- | --- |
| **doctor-agent** | IST academic standards — writing at Técnico level · The university's scientific repository — Doctor's home ground | 3/3 ✅ | 10 |
| **forense-ai** | Root-cause investigation — to the origin, always · Investigating on the open web — any web, verified | 4/4 ✅ | 10 |

## Tópicos cobertos hoje

- IST academic standards — writing at Técnico level
- Investigating on the open web — any web, verified
- Root-cause investigation — to the origin, always
- The university's scientific repository — Doctor's home ground

## Por agente

### doctor-agent — academic rigor (IST)
Foco: IST-standard papers and dissertations; the university's scientific repository.
- Estudou **IST academic standards — writing at Técnico level** → skill actualizada em `training/skills/doctor-agent/d1-ist-standards.md`
- Estudou **The university's scientific repository — Doctor's home ground** → skill actualizada em `training/skills/doctor-agent/d2-ist-repository.md`
- Drills: todos verificados ✅
- Sonda web: Técnico Scholar — repositório científico do IST → ⚠️ inacessível (URLError) — treino continua com o currículo (<https://scholar.tecnico.ulisboa.pt>)
- Sonda web: Repositório da Universidade de Lisboa → ⚠️ inacessível (URLError) — treino continua com o currículo (<https://repositorio.ulisboa.pt>)

### forense-ai — forensics / investigation
Foco: tracing any incident to its origin; evidence-first method on the open web.
- Estudou **Root-cause investigation — to the origin, always** → skill actualizada em `training/skills/forense-ai/f1-root-cause.md`
- Estudou **Investigating on the open web — any web, verified** → skill actualizada em `training/skills/forense-ai/f2-osint-web.md`
- Drills: todos verificados ✅
- Sonda web: Internet Archive — Wayback Machine → ✅ HTTP 200 — “Wayback Machine” (<https://web.archive.org>)
- Sonda web: Certificate Transparency — crt.sh → ⚠️ inacessível (HTTPError) — treino continua com o currículo (<https://crt.sh>)

## Camada LLM (coach)

sem créditos na API Anthropic — o treino correu completo no núcleo determinístico. (Repor créditos reactiva esta camada sozinha.)

## Próxima sessão

Módulos seguintes: The review craft — reading a paper the IST way · IST academic standards — writing at Técnico level

---
_Sistema único de treino (hub devclone20/iclone). Frota Seg/Qua/Sex · Especialidade Ter/Qui (doctor-agent: padrão IST + repositório científico · forense-ai: investigação até à origem na web aberta). Lei da frota: quarentena de 14 dias para qualquer pacote._
