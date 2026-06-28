"""
iCLONE — Social engagement POLICY.

Encodes the owner's exact rules:

  REPLY  — only when ALL hold:
    • the tweet @mentions @icloneframe                (require_mention)
    • it is a direct QUESTION to iCLONE               (require_question)
    • the author is X-VERIFIED (blue / gold / business / gov)   (reply_verified_only)
    • it passes the guardrails (no injection)         (engine-applied)
    • it is on-topic: about our project               (engine-applied)
    • we have not already answered it                  (state-applied)
    • we are under the reply rate limits               (state-applied)

  LIKE   — only when:
    • the tweet is genuine PRAISE / appreciation about iCLONE or CLONE FRAME
    • on-topic
    • under the like rate limits
    • (verified-only if like_verified_only, else any account — owner choice)

This module is pure decision logic over already-fetched data — no network, no LLM —
so it is fully unit-testable.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from .config import XConfig

# X verified_type values that count as a paid/verified checkmark.
_VERIFIED_TYPES = {"blue", "business", "government", "gold"}

# Praise / appreciation signals (English + Portuguese — the owner operates in both).
_PRAISE_TERMS = [
    "love", "amazing", "incredible", "great work", "great project", "impressive",
    "brilliant", "genius", "fire", "🔥", "🚀", "based", "goat", "well done", "congrats",
    "congratulations", "excited", "can't wait", "cant wait", "looking forward", "bullish",
    "best", "awesome", "clean", "beautiful", "solid", "respect", "underrated", "gem",
    "adoro", "incrível", "excelente", "ótimo", "parabéns", "fantástico", "lindo",
    "espetacular", "top", "brutal", "genial",
]
_NEGATION_NEAR_PRAISE = re.compile(r"(?i)\b(not|n't|never|no)\b\s+\w*\s*(good|great|impressive|love)")


@dataclass
class Author:
    """Minimal author view (from X user.fields)."""
    id: str
    username: str
    verified: bool = False
    verified_type: str = "none"

    @property
    def is_verified(self) -> bool:
        return bool(self.verified) or (self.verified_type or "none").lower() in _VERIFIED_TYPES


@dataclass
class Tweet:
    """Minimal tweet view."""
    id: str
    text: str
    author: Author
    is_reply: bool = False
    lang: str = ""


@dataclass
class Decision:
    act: bool
    action: str          # "reply" | "like" | "skip"
    reason: str


class EngagementPolicy:
    def __init__(self, config: XConfig):
        self.cfg = config

    # --- replies ------------------------------------------------------------
    def evaluate_reply(self, tweet: Tweet, *, on_topic: bool, input_safe: bool) -> Decision:
        c = self.cfg
        if not input_safe:
            return Decision(False, "skip", "input failed guardrails")
        if c.require_mention and f"@{c.handle.lower()}" not in tweet.text.lower():
            return Decision(False, "skip", "does not mention @handle")
        if c.reply_verified_only and not tweet.author.is_verified:
            return Decision(False, "skip", "author not verified")
        if c.require_question and not self._is_question(tweet.text):
            return Decision(False, "skip", "not a direct question")
        if not on_topic:
            return Decision(False, "skip", "off-topic")
        # self-reply / owner guard — never auto-reply to our own account
        if tweet.author.username.lower() == c.handle.lower():
            return Decision(False, "skip", "own tweet")
        return Decision(True, "reply", "verified direct on-topic question to @handle")

    # --- likes --------------------------------------------------------------
    def evaluate_like(self, tweet: Tweet, *, on_topic: bool, input_safe: bool) -> Decision:
        c = self.cfg
        if not input_safe:
            return Decision(False, "skip", "input failed guardrails")
        if tweet.author.username.lower() == c.handle.lower():
            return Decision(False, "skip", "own tweet")
        if c.like_verified_only and not tweet.author.is_verified:
            return Decision(False, "skip", "likes restricted to verified")
        if not on_topic:
            return Decision(False, "skip", "off-topic")
        if not self._is_praise(tweet.text):
            return Decision(False, "skip", "not praise/appreciation")
        return Decision(True, "like", "genuine on-topic praise")

    # --- heuristics ---------------------------------------------------------
    @staticmethod
    def _is_question(text: str) -> bool:
        low = text.lower()
        if "?" in text:
            return True
        starters = ("what", "how", "why", "when", "where", "who", "which", "can you",
                    "could you", "do you", "does", "is ", "are ", "will ", "should ",
                    "tell me", "explain", "o que", "como", "porque", "porquê", "qual",
                    "quando", "podes", "consegues")
        stripped = low.lstrip()
        return any(stripped.startswith(s) for s in starters)

    @staticmethod
    def _is_praise(text: str) -> bool:
        low = text.lower()
        if _NEGATION_NEAR_PRAISE.search(low):
            return False
        return any(term in low for term in _PRAISE_TERMS)
