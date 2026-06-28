"""
iCLONE — Social (X / Twitter) layer.

A capability-isolated public voice for iCLONE: it can read mentions, reply, and like,
and nothing else. It imports NO economic skills (acp / crypto / wallet), so no message
received on X can make iCLONE take any economic action. Owner-gated, verified-only
replies, on-topic, anti-jailbreak hardened.

Public API:
    from agent.iclone.social import XEngine, XConfig
"""

from .config import XConfig, MODE_AUTONOMOUS, MODE_REVIEW, MODE_DRY_RUN
from .engine import XEngine
from .guardrails import XGuardrails
from .policy import EngagementPolicy, Author, Tweet, Decision

__all__ = [
    "XEngine", "XConfig", "XGuardrails", "EngagementPolicy",
    "Author", "Tweet", "Decision",
    "MODE_AUTONOMOUS", "MODE_REVIEW", "MODE_DRY_RUN",
]
