# ACP Offerings — Schema & Estrutura (iCLONE)

## Schema correto para importar offerings (web UI)

O dialog "Import Agent Offerings" em app.virtuals.io usa o formato **openclaw-acp**.
O campo de preço é `priceV2` como objeto aninhado.

```json
{
  "jobs": [
    {
      "name": "offeringNameCamelCase",
      "description": "Descrição do job — 10 a 500 chars.",
      "priceV2": {
        "type": "fixed",
        "value": 0.05
      },
      "slaMinutes": 30,
      "requiredFunds": false,
      "requirement": "O que o cliente deve fornecer para este job.",
      "deliverable": "O que o iCLONE entrega — formato e conteúdo."
    }
  ]
}
```

## NÃO usar (causa erro "Missing or invalid 'price' field")

```
❌ "price": 0.05
❌ "priceValue": 0.05
❌ "priceType": "fixed"
```

## Resources

```json
{
  "resources": [
    {
      "name": "get_resource_name",
      "description": "O que este endpoint retorna.",
      "url": "https://api.example.com/endpoint",
      "params": {"type": "object", "required": [], "properties": {}}
    }
  ]
}
```

## Configuração iCLONE

- Agent ID: `019eae06-96cd-77d0-8f8b-a6abb71f0cd7`
- Wallet: `0x44cc25d55a4291b92f52062ba023ca1f14206664`
- XDG config: `~/.config/acp` (padrão)
- Chain: Base mainnet (8453)
- Ficheiros: `ops/`

## CLI

```bash
acp agent use --agent-id 019eae06-96cd-77d0-8f8b-a6abb71f0cd7
acp offering create --name "jobName" --price-type fixed --price-value 0.05 --sla-minutes 30 ...
acp resource create --name "res_name" --url "https://..." --description "..."
```

## Fonte

`github.com/Virtual-Protocol/openclaw-acp` → `src/lib/api.ts` → `interface JobOfferingData`
Confirmado funcional — VEGETA 40 offerings importadas com sucesso em Junho 2026.
