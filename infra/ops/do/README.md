# iCLONE — DigitalOcean Deploy (v2)

Mac desligado. Fleet 24/7 na cloud. **$6/mês** (droplet 1GB).

Topologia **viva** (não a antiga de 4 agentes):

| Serviço | Papel | Wallet (agent) | Unit |
|---------|-------|----------------|------|
| **iCLONE** | PROVIDER (executa offerings) | `0x44cc25d55a4291b92f52062ba023ca1f14206664` | `iclone-server` |
| **VEGETA** | CLIENT (cria/financia/fecha jobs) | `0xe09f40114af6c78788a8003da127c49c56158584` | `iclone-vegeta` |
| token keep-alive | mantém ambos os tokens vivos (20 min) | — | `iclone-token-refresh` |

**Auth sem browser:** os tokens estão no keychain do Mac. `migrate-tokens.sh` extrai-os
e injecta-os no droplet via `acp configure --token`. Cutover limpo — só uma máquina
detém os refresh tokens (que rodam a cada uso).

---

## PASSO 1 — Criar o Droplet (web UI DigitalOcean)

- Image: **Ubuntu 24.04 LTS**
- Plan: **Basic → Regular → $6/mês** (1 vCPU · 1 GB · 25 GB) — o `setup.sh` cria 2GB de swap para o install não rebentar
- Region: **Amsterdam (AMS3)** ou Frankfurt
- Auth: **SSH Key** → cola `~/.ssh/id_ed25519.pub`
- Hostname: `<HOSTNAME>`

Copia o **IP** quando estiver pronto e exporta:

```bash
export IP="<DROPLET_IP>"
```

## PASSO 2 — Setup do servidor (do Mac)

```bash
cd /Users/alexaist1107397/Desktop/AI/iclone
scp ops/do/setup.sh root@$IP:/tmp/
ssh root@$IP 'bash /tmp/setup.sh'      # swap + python3.12 + node20 + acp-cli 1.0.18 (pinned) + ufw + fail2ban
```

## PASSO 3 — Deploy do código + config (do Mac)

```bash
bash ops/do/deploy.sh $IP
```

Copia: código, `.env`, `~/.env.local` (ANTHROPIC_API_KEY), `config.json` dos 2 agentes,
e `signer-keys.json` (P256).

## PASSO 4 — Criar o venv + deps (no droplet)

```bash
ssh iclone@$IP 'cd /opt/iclone && python3.12 -m venv venv312 && \
  venv312/bin/pip install -U pip && venv312/bin/pip install -r ops/do/requirements.txt'
```

## PASSO 5 — Cutover limpo (do Mac) ⚠️ ORDEM IMPORTA

```bash
bash ops/do/cutover-mac.sh        # pára TODOS os daemons do Mac
bash ops/do/migrate-tokens.sh $IP # extrai tokens do keychain → injecta no droplet
```

> Migrar tokens **depois** de parar o Mac garante que só o droplet roda os refresh tokens.

## PASSO 5.5 — Registar signers no droplet ⚠️ OBRIGATÓRIO

As chaves P256 do signer (`~/Library/Application Support/acp-cli/signer-keys.json`)
estão **ligadas ao hardware do Mac** (Secure Enclave embrulha o segredo de decifragem).
Copiá-las para Linux falha com `decryption failed: cipher: message authentication failed`.
O droplet tem de gerar e registar o **seu próprio** signer por agente. Não-destrutivo —
o signer do Mac continua válido; um agente pode ter vários signers.

```bash
bash ops/do/register-signers.sh $IP          # imprime 2 signerUrl
#  → abre ambos no browser, aprova no Privy
bash ops/do/register-signers.sh $IP status   # cola requestId + publicKey de cada um
```

Política `restricted` = autónomo para todas as transacções ACP (igual ao Mac).

## PASSO 6 — Arrancar a fleet (no droplet)

```bash
ssh root@$IP 'bash /opt/iclone/ops/do/start-services.sh'
```

**✓ Mac pode ser desligado.**

---

## Verificação

```bash
ssh root@$IP 'systemctl status iclone-server iclone-vegeta iclone-token-refresh --no-pager'
ssh root@$IP 'tail -f /var/log/iclone/server.log'
ssh root@$IP 'tail -f /var/log/iclone/vegeta.log'
```

Confirma que ambos os agentes autenticam:

```bash
ssh root@$IP "sudo -u iclone env HOME=/home/iclone ACP_CONFIG_DIR=/home/iclone/.config/acp-iclone/acp acp agent whoami"
ssh root@$IP "sudo -u iclone env HOME=/home/iclone ACP_CONFIG_DIR=/home/iclone/.config/acp-vegeta/acp acp agent whoami"
```

---

## Operação contínua

```bash
# Actualizar código (Mac → droplet)
bash ops/do/deploy.sh $IP
ssh root@$IP 'systemctl restart iclone-server iclone-vegeta'

# Logs
ssh root@$IP 'tail -100 /var/log/iclone/server.log'
ssh root@$IP 'journalctl -u iclone-vegeta -f'

# Parar/arrancar individual
ssh root@$IP 'systemctl restart iclone-server'
ssh root@$IP 'systemctl stop iclone-vegeta'
```

---

## Troubleshooting

| Problema | Solução |
|----------|---------|
| Serviço não arranca | `journalctl -u iclone-server -n 50` ou `tail /var/log/iclone/server.log` |
| `ModuleNotFoundError` | falta dep no `requirements.txt` → `ssh iclone@$IP` + `venv312/bin/pip install <mod>` |
| `decryption failed` no signer | signer não registado no droplet → PASSO 5.5 (`register-signers.sh`) |
| `whoami` falha (session expired) | refresh token morto → `ssh iclone@$IP` e `ACP_CONFIG_DIR=... acp configure` (browser) |
| Claude API 401 | `~/.env.local` não foi copiado → re-run `deploy.sh` |
| OOM no install | `setup.sh` já cria swap; confirma `ssh root@$IP 'free -m'` |
| Tokens não migram | keychain do Mac pode pedir permissão — corre `migrate-tokens.sh` em terminal interactivo |

---

## Custos

| Item | $/mês |
|------|-------|
| DO Droplet 1GB | 6 |
| Supabase free tier | 0 |
| Claude API | pay-per-use |
| **Infra** | **6** |

*Opcional não incluído na fleet: `iclone-offerings-manager.{service,timer}` (gestão automática de offerings). Activar manualmente se necessário.*

---

*v2 · topologia iCLONE + VEGETA · auth via keychain migration · 2026-06-15*
