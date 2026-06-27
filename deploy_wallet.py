"""
Deploy iCLONE smart wallet on Base mainnet.

Sends a zero-value self-transfer via ERC-4337 UserOperation.
This triggers the counterfactual deployment of the smart account.

Run once:
  ~/Desktop/AI/iclone/venv312/bin/python3.12 deploy_wallet.py
"""

import os, sys, json, time, logging
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path.home() / ".env.local")
load_dotenv(Path(__file__).parent / ".env", override=False)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
log = logging.getLogger("deploy")

sys.path.insert(0, str(Path(__file__).parent / "agent"))
from server import _decode_private_key

from eth_account import Account
from web3 import Web3
from virtuals_acp.configs.configs import BASE_MAINNET_CONFIG_V2
from virtuals_acp.alchemy import AlchemyAccountKit, AlchemyRPCClient
from virtuals_acp.models import OperationPayload

RAW_KEY    = os.environ["AGENT_PRIVATE_KEY"]
ENTITY_ID  = int(os.environ["VIRTUALS_ENTITY_ID"])
SMART_WALLET = os.environ["AGENT_WALLET_ADDRESS"]  # 0xFFFFC4...

private_key = _decode_private_key(RAW_KEY)
owner = Account.from_key(private_key)

log.info("Signer EOA   : %s", owner.address)
log.info("Smart wallet : %s", SMART_WALLET)
log.info("Entity ID    : %d", ENTITY_ID)

# Check current state
w3 = Web3(Web3.HTTPProvider(BASE_MAINNET_CONFIG_V2.rpc_url))
code = w3.eth.get_code(Web3.to_checksum_address(SMART_WALLET))
if len(code) > 0:
    log.info("Smart wallet already deployed. Nothing to do.")
    sys.exit(0)

balance_eth = w3.eth.get_balance(Web3.to_checksum_address(SMART_WALLET)) / 1e18
log.info("Smart wallet ETH: %.6f", balance_eth)

# Build AlchemyAccountKit with mainnet policy
alchemy = AlchemyAccountKit(
    config=BASE_MAINNET_CONFIG_V2,
    agent_wallet_address=SMART_WALLET,
    entity_id=ENTITY_ID,
    owner_account=owner,
    chain_id=BASE_MAINNET_CONFIG_V2.chain_id,
    chains=BASE_MAINNET_CONFIG_V2.chains,
)

# Fix the hardcoded Sepolia policy — patch with mainnet policy
alchemy.rpc_client.base_url = BASE_MAINNET_CONFIG_V2.alchemy_base_url

log.info("Sending deploy UserOperation (zero-value self-transfer)...")

# A zero-value ETH transfer to self — cheapest valid call, forces deployment
zero_call = OperationPayload(
    to=SMART_WALLET,
    value=0,
    data="0x",
)

try:
    # Override the hardcoded sepolia policy in prepare_calls
    original_prepare = alchemy.prepare_calls

    def patched_prepare(calls, capabilities=None, chain_id=None):
        caps = capabilities or {}
        caps["paymasterService"] = {"policyId": BASE_MAINNET_CONFIG_V2.alchemy_policy_id}
        return original_prepare(calls, caps, chain_id)

    alchemy.prepare_calls = patched_prepare

    result = alchemy.handle_user_operation([zero_call])
    log.info("UserOperation result: %s", json.dumps(result, indent=2)[:500])

    # Verify deployment
    time.sleep(3)
    code = w3.eth.get_code(Web3.to_checksum_address(SMART_WALLET))
    if len(code) > 0:
        log.info("SUCCESS — smart wallet deployed at %s", SMART_WALLET)
        log.info("Now run: venv312/bin/python3.12 agent/server.py")
    else:
        log.warning("UserOp submitted but contract not yet visible — may need a few seconds. Check basescan.org for %s", SMART_WALLET)

except Exception as e:
    log.error("Deploy failed: %s", e)
    log.info("")
    log.info("Alternative: deploy via Virtuals dashboard → Agent Settings → Connect Wallet")
    sys.exit(1)
