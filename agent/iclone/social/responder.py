"""
iCLONE — Social layer RESPONDER.

Generates a public reply for a vetted tweet. Flow:
  1. The tweet is already normalized + guardrail-cleared by the engine.
  2. We wrap it as DATA (spotlighting) and call Claude with the locked public-voice
     system prompt (soul + project knowledge + non-negotiable rules).
  3. We run the model output back through the OUTPUT guardrails (DLP, link allow-list,
     banned phrasing, length, mention-stripping).
  4. If the model declines, or output fails policy, we return None — the engine then
     skips (never sends an unsafe or off-policy reply).

Matches the codebase LLM pattern: anthropic.Anthropic(api_key=...).messages.create(...).
"""

from __future__ import annotations

import logging

from .config import XConfig
from .guardrails import XGuardrails
from .knowledge import build_system_prompt

logger = logging.getLogger("iclone.social.responder")


class Responder:
    def __init__(self, config: XConfig, guardrails: XGuardrails | None = None):
        self.cfg = config
        self.guard = guardrails or XGuardrails(handle=config.handle, max_chars=config.max_tweet_chars)
        self._system = build_system_prompt()
        self._client = None  # lazy

    def _anthropic(self):
        if self._client is None:
            import anthropic  # lazy import — keeps module importable offline / in tests
            self._client = anthropic.Anthropic(
                api_key=self.cfg.anthropic_api_key or None
            )
        return self._client

    def generate(self, tweet_text: str, *, author_handle: str = "") -> str | None:
        """Return a safe, policy-compliant reply, or None to skip."""
        normalized = self.guard.normalize(tweet_text)
        user_block = self.guard.wrap_as_data(normalized)
        prompt = (
            f"{user_block}\n\n"
            f"Reply as iCLONE to @{author_handle}'s question, following every PUBLIC VOICE "
            f"rule. One reply, ≤ {self.cfg.max_tweet_chars} characters. If you cannot answer "
            f"safely and on-topic, output exactly: DECLINE"
        )

        try:
            client = self._anthropic()
            msg = client.messages.create(
                model=self.cfg.model,
                max_tokens=self.cfg.max_reply_tokens,
                system=self._system,
                messages=[{"role": "user", "content": prompt}],
            )
            raw = "".join(
                block.text for block in msg.content if getattr(block, "type", "") == "text"
            ).strip()
        except Exception as exc:
            logger.error("LLM generation failed: %s", exc)
            return None

        if not raw or raw.strip().upper().startswith("DECLINE"):
            logger.info("Responder declined (model).")
            return None

        verdict = self.guard.inspect_output(raw)
        if not verdict.safe:
            logger.warning("Reply blocked by output guardrails: %s", verdict.reason)
            return None
        if verdict.violations:
            logger.info("Reply sanitized: %s", verdict.violations)
        return verdict.text
