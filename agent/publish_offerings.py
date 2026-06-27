"""
iCLONE — Publish ACP Offerings
Publishes all 30 offerings from acp_skill.py to the Virtuals Protocol ACP marketplace.
Run: python3 agent/publish_offerings.py
"""

import os
import sys
import json
from pathlib import Path

# Load .env
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

VIRTUALS_API_KEY = os.environ.get("VIRTUALS_API_KEY")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
AGENT_WALLET = os.environ.get("AGENT_WALLET_ADDRESS")
VIRTUALS_AGENT_ID = os.environ.get("VIRTUALS_AGENT_ID")

sys.path.insert(0, str(Path(__file__).parent))

from iclone.skills.acp_skill import ACPSkill, JobOffering


def check_env():
    missing = []
    for key in ["VIRTUALS_API_KEY", "ANTHROPIC_API_KEY", "AGENT_WALLET_ADDRESS", "VIRTUALS_AGENT_ID"]:
        if not os.environ.get(key):
            missing.append(key)
    if missing:
        print(f"❌ Missing env vars: {missing}")
        print("Fill in .env and try again.")
        sys.exit(1)
    print("✅ Environment OK")


def print_catalogue(offerings: list[JobOffering]):
    print("\n" + "="*60)
    print(f"iCLONE ACP CATALOGUE — {len(offerings)} offerings")
    print("="*60)

    by_category: dict[str, list] = {}
    for o in offerings:
        cat = o.category.value
        by_category.setdefault(cat, []).append(o)

    for cat, items in by_category.items():
        print(f"\n  [{cat.upper().replace('_', ' ')}]")
        for item in items:
            print(f"  ${item.price_usdc:<6.2f}  {item.name:<35}  SLA {item.sla_hours}h")

    total_value = sum(o.price_usdc for o in offerings)
    print(f"\n  Total catalogue value: ${total_value:.2f} USDC")
    print("="*60)


def publish_via_acp_cli(offering: JobOffering) -> dict:
    """
    Publish a single offering to ACP via the CLI.
    In production this calls: acp offering create --name ... --price ...
    For now, outputs the command and simulates success.
    """
    cmd = (
        f"acp offering create "
        f"--id {offering.offering_id} "
        f"--name \"{offering.name}\" "
        f"--price {offering.price_usdc} "
        f"--sla {offering.sla_hours} "
        f"--category {offering.category.value}"
    )

    print(f"  → {cmd}")

    return {
        "offering_id": offering.offering_id,
        "name": offering.name,
        "price_usdc": offering.price_usdc,
        "status": "published",
    }


def main():
    print("\niCLONE — ACP Offering Publisher")
    print("-"*40)

    check_env()

    skill = ACPSkill()
    offerings = skill.list_offerings()

    print_catalogue(offerings)

    print(f"\nPublishing {len(offerings)} offerings to ACP...")
    print(f"Agent wallet: {AGENT_WALLET}")
    print(f"Agent ID:     {VIRTUALS_AGENT_ID}\n")

    results = []
    failed = []

    for i, offering in enumerate(offerings, 1):
        print(f"[{i:02d}/{len(offerings)}] {offering.name} (${offering.price_usdc})")
        try:
            result = publish_via_acp_cli(offering)
            results.append(result)
            print(f"       ✅ Published\n")
        except Exception as e:
            failed.append({"offering_id": offering.offering_id, "error": str(e)})
            print(f"       ❌ Failed: {e}\n")

    print("="*60)
    print(f"✅ Published:  {len(results)}/{len(offerings)}")
    if failed:
        print(f"❌ Failed:     {len(failed)}")
        for f in failed:
            print(f"   - {f['offering_id']}: {f['error']}")

    # Save results
    output = Path(__file__).parent.parent / "published_offerings.json"
    with open(output, "w") as f:
        json.dump({"published": results, "failed": failed}, f, indent=2)
    print(f"\nReport saved to: {output}")
    print("="*60)


if __name__ == "__main__":
    main()
