"""
ACP Offerings Publishing — Conhecimento aprendido por iCLONE em sessão real.

Schema correcto validado contra o Virtuals OS em 2026-06-11.
Cada campo foi testado individualmente até passar (verde) no import form.
"""

ACP_OFFERINGS_KNOWLEDGE = {
    "source": "Virtuals Protocol Whitepaper + teste real no Virtuals OS",
    "validated_date": "2026-06-11",
    "guide_url": "https://whitepaper.virtuals.io/acp/acp-dev-onboarding-guide/set-up-agent-profile/add-resource/import-and-export-agent-job-resource",

    "schema": {
        "description": "Schema exacto aceite pelo Import Agent Jobs / Import Agent Offerings no Virtuals OS",
        "top_level": {
            "jobs": "array of job objects — ONLY this key allowed at top level. 'resources' and 'subscriptions' are NOT allowed in the same import."
        },
        "job_fields": {
            "name": {
                "type": "string",
                "format": "camelCase ou snake_case",
                "note": "Title Case com espaços é REJEITADO",
                "example": "webResearchQuick"
            },
            "description": {
                "type": "string",
                "required": True
            },
            "requiredFunds": {
                "type": "boolean",
                "note": "True apenas para jobs que gerem capital do cliente (trading, DeFi). Não é um valor monetário.",
                "example": False
            },
            "slaMinutes": {
                "type": "number",
                "note": "Tempo em MINUTOS (não horas). Mínimo 5.",
                "example": 60
            },
            "requirement": {
                "type": "string ou JSON schema object",
                "note": "SINGULAR 'requirement', não 'requirements'",
                "example": "query"
            },
            "deliverable": {
                "type": "string ou JSON schema object",
                "example": "JSON: {summary, sources[], key_facts[]}"
            },
            "price": {
                "type": "object",
                "structure": {"type": "fixed | percentage", "value": "number"},
                "note": "OBJECTO, não número. Nem string. Nem wei. Apenas {'type': 'fixed', 'value': N}",
                "example": {"type": "fixed", "value": 1}
            }
        },
        "errors_and_fixes": [
            {
                "error": "Name must be in camelCase or snake_case format",
                "cause": "Nome com espaços ou Title Case",
                "fix": "Converter para camelCase: 'Web Research Quick' → 'webResearchQuick'"
            },
            {
                "error": "Missing or invalid 'slaMinutes' field",
                "cause": "Campo chamado 'sla' em vez de 'slaMinutes', ou valor em horas",
                "fix": "Renomear para 'slaMinutes' e multiplicar horas por 60"
            },
            {
                "error": "Missing or invalid 'price' field",
                "cause": "price como número (1), string ('1'), wei ('1000000000000000000'), ou campos separados priceType/priceValue",
                "fix": "price deve ser objecto: {\"type\": \"fixed\", \"value\": 1}"
            },
            {
                "error": "Missing or invalid 'requiredFunds' field",
                "cause": "requiredFunds como número ou string",
                "fix": "requiredFunds deve ser boolean: true ou false"
            },
            {
                "error": "Found unexpected fields: resources, subscriptions",
                "cause": "Top level tem mais campos além de 'jobs'",
                "fix": "Remover 'resources' e 'subscriptions' do JSON. Importar separadamente."
            },
            {
                "error": "Context 'jobs' only allows: jobs",
                "cause": "Mesmo que o anterior",
                "fix": "JSON deve ser apenas {\"jobs\": [...]}"
            }
        ]
    },

    "minimal_valid_example": {
        "jobs": [
            {
                "name": "webResearchQuick",
                "description": "Single-query web research. 5 sources, 200-word summary.",
                "requiredFunds": False,
                "slaMinutes": 60,
                "requirement": "query",
                "deliverable": "JSON: {summary, sources[], key_facts[]}",
                "price": {"type": "fixed", "value": 1}
            }
        ]
    },

    "publication_flow": [
        "1. Abrir Virtuals OS → Agent Profile → Jobs/Offerings",
        "2. Clicar 'Import Agent Jobs' ou 'Import Agent Offerings'",
        "3. Seleccionar 'Paste JSON'",
        "4. Colar o JSON com o schema correcto",
        "5. Validação em tempo real — borda verde = passou, vermelha = erros",
        "6. Clicar 'Next' quando verde",
        "7. Review da lista de jobs importados",
        "8. Clicar 'Import All' para publicar todos de uma vez",
        "9. Jobs ficam activos no ACP marketplace"
    ],

    "sdk_vs_form_difference": {
        "note": "O SDK (@virtuals-protocol/acp-node-v2) usa campos diferentes do form de import",
        "sdk_fields": {"priceType": "string", "priceValue": "number", "requirements": "plural"},
        "form_fields": {"price": {"type": "string", "value": "number"}, "requirement": "singular"},
        "conclusion": "Para publicar via UI usar o schema do form. Para SDK usar priceType/priceValue."
    }
}


def get_offerings_schema() -> dict:
    """Retorna o schema validado para publicar offerings no Virtuals OS."""
    return ACP_OFFERINGS_KNOWLEDGE["schema"]


def build_job_offering(
    name: str,
    description: str,
    requirement: str,
    deliverable: str,
    price_value: float,
    sla_minutes: int,
    required_funds: bool = False,
    price_type: str = "fixed"
) -> dict:
    """
    Constrói um job offering com o schema correcto para import no Virtuals OS.

    Args:
        name: camelCase ou snake_case (sem espaços)
        description: descrição do serviço
        requirement: o que o cliente deve fornecer
        deliverable: o que será entregue
        price_value: valor em USDC
        sla_minutes: tempo máximo de entrega em minutos
        required_funds: True apenas para jobs que gerem capital do cliente
        price_type: "fixed" ou "percentage"
    """
    return {
        "name": name,
        "description": description,
        "requiredFunds": required_funds,
        "slaMinutes": sla_minutes,
        "requirement": requirement,
        "deliverable": deliverable,
        "price": {
            "type": price_type,
            "value": price_value
        }
    }


def build_offerings_json(jobs: list[dict]) -> dict:
    """Wraps a list of job dicts into the correct top-level import structure."""
    return {"jobs": jobs}
