# iCLONE / VEGETA — Contexto Completo (handoff 2026-06-15)

## 1. Visão geral
Ecossistema de agentes autónomos no **Virtuals Protocol ACP** (Agent Commerce Protocol),
a correr 24/7 num droplet DigitalOcean. Cada agente é um participante económico completo:
**vende** (provider server executa offerings) e **contrata** (client autopilot cria/financia jobs),
entre os nossos agentes e o mercado externo.

- Repo: `https://github.com/devclone20/iclone.git` (conta devclone20). Código local em `~/Desktop/AI/iclone`.
- ACP CLI: `@virtuals-protocol/acp-cli` **v1.0.18** (pinada no droplet).
- Chain: Base mainnet (chainId **8453**). USDC: `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913`.

## 2. Infraestrutura (droplet)
- IP `188.166.114.148`, hostname `iclone-prod`, Ubuntu 22.04, **$6/mês (1 vCPU / 1GB / 25GB)** + 2GB swap.
- Código em `/opt/iclone`, user `iclone`, venv `/opt/iclone/venv312`, logs em `/var/log/iclone/`.
- Acesso: `ssh root@188.166.114.148` (chave `~/.ssh/id_ed25519`).
- ⚠️ **1 vCPU é o gargalo** — cada chamada `acp` lança um processo Node pesado. Com $200 DO (GitHub
  Student) subir para 2 vCPU / 2GB antes de ativar mais agentes.

## 3. Contas e carteiras
**Conta iCLONE** (owner `0xb4805e8d8c9f23fa4615422202be1e38fba6a739`) — 4 agentes:
| Agente | agent wallet | agent id | domínio | estado |
|--------|--------------|----------|---------|--------|
| iCLONE | 0x44cc25d55a4291b92f52062ba023ca1f14206664 | 019eae06-96cd-77d0-8f8b-a6abb71f0cd7 | cripto/research | LIVE |
| MATRIX | 0x07924dea2c8212969d5dc5655785aa5063adb2bc | 019ebb92-b4be-7660-82d3-4b1647843e6a | código/eng SW | preparado, inativo |
| DoctorWHO | 0x875242eb5c91270ca80ed7753a87d6e22e4f5acf | 019ebb92-93e8-7b4e-b2e8-39c3419843c9 | research/data | preparado, inativo |
| SuperSayatin | 0x18f3aeadbad9c4b626c114ab14b89e586e4f6df3 | 019ebb92-7415-7baa-93e9-ee19a7742877 | conteúdo/marketing | preparado, inativo |

**Conta VEGETA** (owner `0x743665952ec1240d62a3e580e5dc2c9e421d0537`) — 1 agente:
| Agente | agent wallet | agent id | domínio | estado |
|--------|--------------|----------|---------|--------|
| VEGETA | 0xe09f40114af6c78788a8003da127c49c56158584 | 019ec5ec-4b48-750d-894a-7f1fedebb988 | robótica/IA embodied | LIVE |

Config dirs (isolados por agente): `~/.config/acp-iclone/acp`, `~/.config/acp-vegeta/acp` (+ a criar p/ os 3).

## 4. Serviços systemd (no droplet)
**ATIVOS:**
- `iclone-server` — iCLONE provider (40 offerings cripto/research)
- `iclone-vegeta-server` — VEGETA provider (40 offerings robótica)
- `iclone-vegeta` — VEGETA client (contrata iCLONE)
- `iclone-client` — iCLONE client (contrata VEGETA)
- `iclone-token-refresh` — keep-alive (whoami 20min)
- `iclone-training.timer` — treino 07:00+19:00 UTC
- `iclone-bootstrap.timer` — scan de mercado cada 30min

**INATIVOS (instalados, disabled):** `iclone-{doctorwho,supersayatin,matrix}-{server,client}`

## 5. Arquitectura de código (generalizada — 1 base, N agentes)
- `agent/server.py` — provider server. Env: `ACP_CONFIG_DIR`, `ICLONE_AGENT_NAME`,
  `ICLONE_OFFERINGS_FILE`, identidade (wallet/id) lida do config.json. Gate por wallet do provider.
- `agent/iclone/skills/execution_engine.py` — `ExecutionEngine.execute(offering_id, requirements, offering_meta)`.
  `_generic_offering()`: cumpre QUALQUER offering a partir da sua description+deliverable via Claude.
  **Conteúdo vai em `result.data`** (é o que o server submete).
- `ops/client_autopilot.py` — client buy-side generalizado. Env: `TARGET_WALLET`, `JOBS_FILE`,
  `FIRE_PERIOD_MIN`/`FIRE_OFFSET_MIN` (cadência por slot), `MAX_ADVANCE_PER_PASS`, `CYCLE_SLEEP`,
  `EXTERNAL_EVERY`/`EXTERNAL_QUERY` (compra externa, off por defeito).
- `ops/bootstrap.py` — scan de mercado (`acp browse`), escreve `market_map_<agente>.json`.
- `published_offerings_<slug>.json` — catálogo de cada agente (price_usdc, description, deliverable).
- `ops/client_jobs_<slug>.json` — templates de jobs que cada client contrata (com offering_id).

## 6. Descobertas críticas (gotchas)
1. **Signer P256 é hardware-bound ao Mac** (Secure Enclave). NÃO portável — cada máquina/agente
   regista o seu via `acp agent add-signer --policy restricted` + aprovação no browser.
2. **Tokens migram via keychain** (`migrate-tokens.sh`), mas a operação dos agentes autentica-se
   **assinando cada request com o signer on-chain** (não JWT) → **sem risco de expiração**.
3. **`acp job list` reporta budget_set como "open"** — usar `acp job history` para o estado real.
4. **ACP NÃO propaga o nome da offering ao provider** — o cliente DEVE incluir `offering_id` nos requirements.
5. **2 fontes de preço** têm de sincronizar: marketplace (`acp offering update`) + `published_offerings.json`
   (o server cobra deste). Banda actual: **$0.05–$0.10**.
6. **`.env.local` segundo EnvironmentFile** no systemd (override do placeholder ANTHROPIC_API_KEY no `.env`).
7. **PyYAML** é dependência (estava em falta).

## 7. Estado actual (validado 2026-06-15 ~22:40)
- Economia bidireccional VEGETA↔iCLONE: **cadência de 4 min alternada** (VEGETA slots :00/:08/:16,
  iCLONE :04/:12/:20) via disparo por slot. Validado: 22:28→22:40 perfeito.
- Disparo por SLOT (`current_slot()`) resolve o loop lento saltar o minuto-alvo.
- `advance_inflight` throttled (≤6 history-calls/passagem, 30s tick). Load 6.7→2.6.
- Há um backlog de ~39 jobs budget_set (da cadência antiga de 1min) — escoa sozinho ou expira.

## 8. Planos de 100 agentes (PLANEADO, nada criado ainda)
- **iCLONE**: 100 agentes (4 live + UNIX + 95), nomes míticos/históricos alinhados à função,
  10 tracks Virtuals Hackathon. Ficheiros: `agent_fleet_plan_100.json`,
  `~/Desktop/Widget Design/iclone_100_agents_hackathon_plan.html`.
- **VEGETA**: 100 agentes (1 live + 99), nomes de anime maioritariamente maiúsculas, mesmos 10 tracks.
  Ficheiros: `agent_fleet_plan_vegeta_100.json`, `~/Desktop/Widget Design/vegeta_100_agents_anime_hackathon_plan.html`.
- 10 tracks: DeFi/Trading, Market Intelligence, Dev Tools/Code, Research/Knowledge, Content/Media,
  Robotics/Physical AI, Security/Audit, Creative/Art, Gaming/Worlds, Commerce/Payments/Oracles.

## 9. Como criar/ativar um agente (runbook)
`acp agent create` → `acp agent add-signer --policy restricted --no-wait` (aprovar URL no browser) →
`signer-status` → gerar `published_offerings_<slug>.json` → publicar via `acp offering create` →
systemd server+client units → fund USDC → enable+start.
Helper para os 3 já preparados: `ops/do/activate-agent.sh <slug> setup` + `... finish <reqId> <pubKey>`.

## 10. Comandos úteis
```bash
# Monitor da fleet
bash ops/do/monitor.sh 188.166.114.148           # snapshot
ssh root@188.166.114.148 'tail -f /var/log/iclone/vegeta.log'
ssh root@188.166.114.148 'systemctl status iclone-server iclone-vegeta-server --no-pager'
# Atualizar código
bash ops/do/deploy.sh 188.166.114.148
# Whoami por agente
ssh root@188.166.114.148 "sudo -u iclone env HOME=/home/iclone ACP_CONFIG_DIR=/home/iclone/.config/acp-iclone/acp acp agent whoami"
```

## 11. Tarefas em aberto
- [ ] Resgatar **$200 DigitalOcean** via GitHub Student Pack (lembrete agendado 2026-06-15 22:00).
- [ ] Subir droplet a **2 vCPU / 2GB** antes de ativar mais agentes.
- [ ] Ativar DoctorWHO/SuperSayatin/MATRIX quando financiados (`activate-agent.sh`).
- [ ] Começar criação real dos planos de 100 (por lotes, track a track).
- [ ] (opcional) ligar compra externa (`EXTERNAL_EVERY>0`) e widget Neural Engine 3D (adiado).

## 12. Memórias persistentes relevantes
iclone_cloud_deploy · iclone_agent_architecture · iclone_fleet_economy · iclone_pricing ·
acp_schema_ops_knowledge · acp_offerings_schema · iclone_100_agent_plan · github_student_do
