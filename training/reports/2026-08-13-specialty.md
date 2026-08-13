# 📚 Treino — Especialidade (Ter/Qui) — 2026-08-13

_Sessão: Scheduled · 06:11 UTC · 2/2 agentes treinados._

## Resumo

| Agente | Módulos de hoje | Drills | Sessões totais |
| --- | --- | --- | --- |
| **doctor-agent** | The university's scientific repository — Doctor's home ground · The review craft — reading a paper the IST way | 2/2 ✅ | 6 |
| **forense-ai** | Investigating on the open web — any web, verified · Digital evidence — preserve first, analyse second | 3/3 ✅ | 6 |

## Tópicos cobertos hoje

- Digital evidence — preserve first, analyse second
- Investigating on the open web — any web, verified
- The review craft — reading a paper the IST way
- The university's scientific repository — Doctor's home ground

## Por agente

### doctor-agent — academic rigor (IST)
Foco: IST-standard papers and dissertations; the university's scientific repository.
- Estudou **The university's scientific repository — Doctor's home ground** → skill actualizada em `training/skills/doctor-agent/d2-ist-repository.md`
- Estudou **The review craft — reading a paper the IST way** → skill actualizada em `training/skills/doctor-agent/d3-review-craft.md`
- Drills: todos verificados ✅
- Sonda web: Técnico Scholar — repositório científico do IST → ✅ HTTP 200 — “Search - Scholar” (<https://scholar.tecnico.ulisboa.pt>)
- Sonda web: Repositório da Universidade de Lisboa → ✅ HTTP 200 — “Repositório :: Página inicial” (<https://repositorio.ulisboa.pt>)

### forense-ai — forensics / investigation
Foco: tracing any incident to its origin; evidence-first method on the open web.
- Estudou **Investigating on the open web — any web, verified** → skill actualizada em `training/skills/forense-ai/f2-osint-web.md`
- Estudou **Digital evidence — preserve first, analyse second** → skill actualizada em `training/skills/forense-ai/f3-digital-evidence.md`
- Drills: todos verificados ✅
- Sonda web: Internet Archive — Wayback Machine → ⚠️ inacessível (HTTPError) — treino continua com o currículo (<https://web.archive.org>)
- Sonda web: Certificate Transparency — crt.sh → ⚠️ inacessível (HTTPError) — treino continua com o currículo (<https://crt.sh>)

## Camada LLM (coach)

sem créditos na API Anthropic — o treino correu completo no núcleo determinístico. (Repor créditos reactiva esta camada sozinha.)

## Próxima sessão

Módulos seguintes: IST academic standards — writing at Técnico level · The university's scientific repository — Doctor's home ground

---
_Sistema único de treino (hub devclone20/iclone). Frota Seg/Qua/Sex · Especialidade Ter/Qui (doctor-agent: padrão IST + repositório científico · forense-ai: investigação até à origem na web aberta). Lei da frota: quarentena de 14 dias para qualquer pacote._
