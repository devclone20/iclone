"""
iCLONE / VEGETA — Trade Engine v2
Real on-chain swap & bridge execution via the LI.FI API + `acp wallet send-transaction`.

We do NOT use `acp trade`: that CLI path intermittently fails with
"Body is unusable: Body has already been read" (an undici double-read bug that
hits Ethereum mainnet always and other chains unpredictably). Instead we call
LI.FI directly (which returns clean 200s) to get a ready-to-sign transaction,
then broadcast it from the agent's wallet via `acp wallet send-transaction`
(the same primitive used for refunds — proven reliable).

Flow:
  1. QUOTE   — GET li.quest/v1/quote → transactionRequest {to,data,value} + approvalAddress + toAmountMin.
  2. APPROVE — for ERC-20 input, if allowance < amount, send ERC-20 approve(spender, amount).
  3. SWAP    — send-transaction the LI.FI transactionRequest.
  4. STATUS  — for cross-chain (bridge), poll li.quest/v1/status until DONE.
  5. REFUND  — on failure after capital was received, return the input token in full.

Supported chains (anything LI.FI routes + the agent has gas on): 1 (Ethereum),
8453 (Base), 42161 (Arbitrum). Cross-chain between them is automatic.
"""
from __future__ import annotations

import json
import os
import subprocess
import time
from typing import Any

import requests

from .base_skill import SkillResult

ACP_BIN = os.environ.get("ACP_BIN", "/usr/bin/acp")
LIFI = "https://li.quest/v1"

SUPPORTED_CHAINS = {1, 8453, 42161}
NATIVE = "0x0000000000000000000000000000000000000000"

RPC = {
    1:     "https://eth.llamarpc.com",
    8453:  "https://mainnet.base.org",
    42161: "https://arb1.arbitrum.io/rpc",
}

TOKENS = {
    8453:  {"USDC": "0x833589fcd6edb6e08f4c7c32d4f71b54bda02913", "WETH": "0x4200000000000000000000000000000000000006"},
    42161: {"USDC": "0xaf88d065e77c8cc2239327c5edb3a432268e5831", "WETH": "0x82af49447d8a07e3bd95bd0d56f35241523fbab1"},
    1:     {"USDC": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48", "WETH": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"},
}

_SEL_DECIMALS = "0x313ce567"
_SEL_TRANSFER = "0xa9059cbb"
_SEL_APPROVE = "0x095ea7b3"
_SEL_ALLOWANCE = "0xdd62ed3e"
_MAX_UINT = "f" * 64


def _ok(output: str, data: dict) -> SkillResult:
    return SkillResult(success=True, output=output, data=data)


def _err(msg: str, data: dict | None = None) -> SkillResult:
    return SkillResult(success=False, output="", error=msg, data=data)


def _is_addr(s: Any) -> bool:
    return isinstance(s, str) and s.startswith("0x") and len(s) == 42


def _run_acp(args: list[str], timeout: int = 200) -> tuple[int, str, str]:
    try:
        r = subprocess.run([ACP_BIN, *args], capture_output=True, text=True, timeout=timeout)
        return r.returncode, (r.stdout or "").strip(), (r.stderr or "").strip()
    except subprocess.TimeoutExpired:
        return 124, "", "timeout"
    except Exception as e:  # noqa: BLE001
        return 1, "", str(e)


def _eth_call(chain: int, to: str, data: str) -> str | None:
    rpc = RPC.get(chain)
    if not rpc:
        return None
    try:
        resp = requests.post(rpc, json={"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                                        "params": [{"to": to, "data": data}, "latest"]}, timeout=15).json()
        return resp.get("result")
    except Exception:  # noqa: BLE001
        return None


class TradeEngine:
    """Swaps/bridges executed via LI.FI + acp wallet send-transaction."""

    def __init__(self):
        self._addr: str | None = None
        self._dec_cache: dict[tuple[int, str], int] = {}

    # ---- identity / token helpers -------------------------------------------
    def _agent_address(self) -> str | None:
        if self._addr:
            return self._addr
        rc, out, err = _run_acp(["--json", "wallet", "address"], timeout=40)
        try:
            self._addr = json.loads(out).get("address") if out.startswith("{") else out.split()[-1]
        except Exception:  # noqa: BLE001
            self._addr = out.strip() or None
        return self._addr

    def _resolve(self, token: str, chain: int) -> str:
        if not token:
            return token
        t = token.strip()
        if t.lower() in ("eth", "native", NATIVE):
            return NATIVE
        if _is_addr(t):
            return t.lower()
        return TOKENS.get(chain, {}).get(t.upper(), t)

    def _decimals(self, token: str, chain: int) -> int | None:
        if token == NATIVE:
            return 18
        key = (chain, token)
        if key in self._dec_cache:
            return self._dec_cache[key]
        res = _eth_call(chain, token, _SEL_DECIMALS)
        d = int(res, 16) if res and res != "0x" else None
        if d is not None:
            self._dec_cache[key] = d
        return d

    def _read(self, req: dict[str, Any], chain_in: int, chain_out: int) -> dict | None:
        token_in = self._resolve(req.get("token_in") or req.get("sell_token", ""), chain_in)
        token_out = self._resolve(req.get("token_out") or req.get("buy_token", ""), chain_out)
        amount_in = req.get("amount_in") or req.get("amount")
        recipient = req.get("recipient")
        if not (token_in and token_out and amount_in and recipient and _is_addr(recipient)):
            return None
        try:
            slippage = max(0.001, min(float(req.get("max_slippage_pct", req.get("slippage", 3))) / 100.0, 0.5))
        except (TypeError, ValueError):
            slippage = 0.03
        return {"token_in": token_in, "token_out": token_out, "amount_in": str(amount_in),
                "recipient": recipient, "slippage": slippage}

    # ---- LI.FI ---------------------------------------------------------------
    def _quote(self, p: dict, chain_in: int, chain_out: int, from_addr: str) -> tuple[dict | None, str | None]:
        dec = self._decimals(p["token_in"], chain_in)
        if dec is None:
            return None, f"could not read decimals for {p['token_in']}"
        try:
            amount_base = int(round(float(p["amount_in"]) * (10 ** dec)))
        except (TypeError, ValueError):
            return None, "bad amount_in"
        params = {
            "fromChain": chain_in, "toChain": chain_out,
            "fromToken": p["token_in"], "toToken": p["token_out"],
            "fromAmount": str(amount_base), "fromAddress": from_addr,
            "toAddress": p["recipient"], "slippage": p["slippage"],
        }
        try:
            r = requests.get(f"{LIFI}/quote", params=params, timeout=30)
        except Exception as e:  # noqa: BLE001
            return None, f"quote request failed: {e}"
        if r.status_code != 200:
            return None, f"no route (LI.FI {r.status_code}): {r.text[:160]}"
        q = r.json()
        q["_amount_base"] = amount_base
        return q, None

    def _status_done(self, tx_hash: str, chain_in: int, chain_out: int, deadline: float) -> bool:
        while time.time() < deadline:
            try:
                r = requests.get(f"{LIFI}/status", params={"txHash": tx_hash, "fromChain": chain_in,
                                                           "toChain": chain_out}, timeout=20).json()
                st = (r.get("status") or "").upper()
                if st == "DONE":
                    return True
                if st == "FAILED":
                    return False
            except Exception:  # noqa: BLE001
                pass
            time.sleep(8)
        return False

    # ---- tx primitives -------------------------------------------------------
    def _send(self, chain: int, to: str, data: str, value_wei: int) -> tuple[str | None, str]:
        rc, out, err = _run_acp(["--json", "wallet", "send-transaction", "--chain-id", str(chain),
                                 "--to", to, "--data", data, "--value", str(value_wei)], timeout=200)
        blob = out + " " + err
        try:
            d = json.loads(out)
            h = d.get("transactionHash") or d.get("txHash") or d.get("hash")
            if h:
                return h, blob
        except Exception:  # noqa: BLE001
            pass
        return None, blob

    def _ensure_allowance(self, token: str, spender: str, amount_base: int, chain: int, owner: str) -> str | None:
        """Returns an error string if approval was needed but failed; None on ok."""
        if token == NATIVE:
            return None
        cur = _eth_call(chain, token, _SEL_ALLOWANCE + owner[2:].rjust(64, "0").lower() + spender[2:].rjust(64, "0").lower())
        try:
            have = int(cur, 16) if cur and cur != "0x" else 0
        except (TypeError, ValueError):
            have = 0
        if have >= amount_base:
            return None
        data = _SEL_APPROVE + spender[2:].rjust(64, "0").lower() + _MAX_UINT
        h, blob = self._send(chain, token, data, 0)
        if not h:
            return f"approve failed: {blob[:160]}"
        time.sleep(3)
        return None

    # ---- public: preflight ---------------------------------------------------
    def preflight(self, req: dict[str, Any], chain_in: int, chain_out: int | None = None) -> SkillResult:
        chain_out = chain_out or chain_in
        if chain_in not in SUPPORTED_CHAINS or chain_out not in SUPPORTED_CHAINS:
            return _err(f"unsupported chain (only {sorted(SUPPORTED_CHAINS)})")
        p = self._read(req, chain_in, chain_out)
        if p is None:
            return _err("missing/invalid fields: need token_in, token_out, amount_in, recipient(0x address)")
        addr = self._agent_address()
        if not addr:
            return _err("could not resolve agent wallet address")
        q, e = self._quote(p, chain_in, chain_out, addr)
        if e:
            return _err(f"preflight failed: {e}")
        est = q.get("estimate", {})
        return _ok("route ok", {"tool": q.get("tool"), "toAmountMin": est.get("toAmountMin"),
                                "gasUSD": [g.get("amountUSD") for g in est.get("gasCosts", [])]})

    # ---- public: execute -----------------------------------------------------
    def swap(self, req: dict[str, Any], *, chain_in: int, chain_out: int | None = None) -> SkillResult:
        chain_out = chain_out or chain_in
        if chain_in not in SUPPORTED_CHAINS or chain_out not in SUPPORTED_CHAINS:
            return _err(f"unsupported chain (only {sorted(SUPPORTED_CHAINS)})")
        p = self._read(req, chain_in, chain_out)
        if p is None:
            return _err("missing/invalid fields: need token_in, token_out, amount_in, recipient(0x address)")
        addr = self._agent_address()
        if not addr:
            return _err("could not resolve agent wallet address")

        q, e = self._quote(p, chain_in, chain_out, addr)
        if e:
            return _err(f"no route / quote failed: {e}")  # nothing executed yet

        amount_base = q["_amount_base"]
        tr = q.get("transactionRequest") or {}
        to = tr.get("to")
        data = tr.get("data")
        try:
            value_wei = int(str(tr.get("value", "0x0")), 16)
        except (TypeError, ValueError):
            value_wei = 0
        spender = q.get("estimate", {}).get("approvalAddress")
        if not (to and data):
            return _err("LI.FI returned no transactionRequest")

        # 1) approve if ERC-20 input
        if spender:
            aerr = self._ensure_allowance(p["token_in"], spender, amount_base, chain_in, addr)
            if aerr:
                return _err(aerr)  # no capital spent on the swap itself yet

        # 2) execute swap
        tx_hash, blob = self._send(chain_in, to, data, value_wei)
        if not tx_hash:
            refund = self._refund(p["token_in"], p["amount_in"], p["recipient"], chain_in)
            return _err(f"swap tx failed: {blob[:200]}", {"deliverable": {"status": "failed", "refund": refund}})

        # 3) cross-chain settlement
        bridged = True
        if chain_in != chain_out:
            bridged = self._status_done(tx_hash, chain_in, chain_out, time.time() + 25 * 60)

        deliverable = {
            "status": "success" if bridged else "pending_bridge",
            "kind": "bridge" if chain_in != chain_out else "swap",
            "tool": q.get("tool"), "tx_hash": tx_hash, "tx_hashes": [tx_hash],
            "token_in": p["token_in"], "token_out": p["token_out"],
            "amount_in": p["amount_in"], "recipient": p["recipient"],
            "chain_in": chain_in, "chain_out": chain_out,
            "min_received": q.get("estimate", {}).get("toAmountMin"),
        }
        return _ok(f"{deliverable['kind']} ok ({tx_hash[:12]})", {"deliverable": deliverable})

    # ---- refund --------------------------------------------------------------
    def _refund(self, token_in: str, amount_in: str, recipient: str, chain: int) -> dict:
        token = self._resolve(token_in, chain)
        if token == NATIVE:
            # return native ETH
            dec = 18
            try:
                base = int(round(float(amount_in) * (10 ** dec)))
            except (TypeError, ValueError):
                return {"status": "manual_review", "reason": "bad amount"}
            h, blob = self._send(chain, recipient, "0x", base)
            return {"status": "refunded" if h else "manual_review", "tx": h, "raw": blob[:150]}
        dec = self._decimals(token, chain)
        if dec is None or not _is_addr(token) or not _is_addr(recipient):
            return {"status": "manual_review", "reason": "token/decimals unresolved", "token": token}
        try:
            base = int(round(float(amount_in) * (10 ** dec)))
        except (TypeError, ValueError):
            return {"status": "manual_review", "reason": "bad amount"}
        data = _SEL_TRANSFER + recipient[2:].rjust(64, "0").lower() + format(base, "064x")
        h, blob = self._send(chain, token, data, 0)
        return {"status": "refunded" if h else "manual_review", "token": token, "amount": amount_in,
                "tx": h, "raw": blob[:150]}
