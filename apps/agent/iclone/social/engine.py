"""
iCLONE — Social ENGINE (the autonomous loop).

One cycle:
  1. Guard: enabled? has read creds? (Free tier → reads disabled → idle safely.)
  2. Pull recent mentions since the cursor (newest verified-field author data).
  3. For each new mention, in order:
       a. guardrails.inspect_input  → block injections, normalize, topic check
       b. policy.evaluate_reply     → verified + mention + question + on-topic
          → if reply: responder.generate → x_client.reply (or queue draft / dry-run)
       c. policy.evaluate_like      → on-topic praise → x_client.like
     Every decision and action is audit-logged. Rate limits enforced via State.
  4. Advance the since_id cursor; persist state.

Capability isolation: this module imports ONLY the social package + guardrails +
knowledge. No economic skill is reachable from here.
"""

from __future__ import annotations

import logging
import signal
import time

from .config import XConfig, MODE_AUTONOMOUS, MODE_REVIEW, MODE_DRY_RUN
from .guardrails import XGuardrails
from .policy import EngagementPolicy
from .responder import Responder
from .state import State
from .x_client import XClient

logger = logging.getLogger("iclone.social.engine")


class XEngine:
    def __init__(self, config: XConfig | None = None):
        self.cfg = config or XConfig.from_env()
        self.state = State(self.cfg.home)
        self.guard = XGuardrails(handle=self.cfg.handle, max_chars=self.cfg.max_tweet_chars)
        self.policy = EngagementPolicy(self.cfg)
        self.responder = Responder(self.cfg, self.guard)
        self.client = XClient(self.cfg)
        self._stop = False

    # --- one cycle ----------------------------------------------------------
    def run_cycle(self) -> dict:
        summary = {"fetched": 0, "replied": 0, "liked": 0, "skipped": 0, "blocked": 0}

        if not self.cfg.enabled:
            logger.info("X engine disabled (X_ENABLED=false). Idling.")
            return summary

        if not self.client.read_enabled:
            logger.warning("No read credentials — cannot fetch mentions. Idling.")
            return summary

        mentions = self.client.get_mentions(self.state.since_id, self.cfg.mentions_per_poll)
        summary["fetched"] = len(mentions)
        if not self.client.read_enabled:
            # got flipped off mid-call (Free tier 403)
            return summary

        # Oldest first so the cursor advances monotonically.
        for tweet in sorted(mentions, key=lambda t: int(t.id)):
            self.state.since_id = tweet.id
            if self.state.already_processed(tweet.id):
                continue
            self.state.mark_processed(tweet.id)

            verdict = self.guard.inspect_input(tweet.text)
            if not verdict.safe:
                summary["blocked"] += 1
                self.state.audit("input_blocked", tweet_id=tweet.id,
                                 author=tweet.author.username, threats=verdict.threats)
                continue

            acted = self._maybe_reply(tweet, verdict.on_topic, summary)
            if not acted:
                self._maybe_like(tweet, verdict.on_topic, summary)

        self.state.save()
        logger.info("cycle: %s | state: %s", summary, self.state.stats())
        return summary

    # --- reply path ---------------------------------------------------------
    def _maybe_reply(self, tweet, on_topic: bool, summary: dict) -> bool:
        decision = self.policy.evaluate_reply(tweet, on_topic=on_topic, input_safe=True)
        if not decision.act:
            return False
        if not self.state.under_limit("reply", self.cfg.max_replies_per_hour,
                                      self.cfg.max_replies_per_day):
            self.state.audit("reply_ratelimited", tweet_id=tweet.id)
            summary["skipped"] += 1
            return True  # counts as "handled" — don't also like

        reply_text = self.responder.generate(tweet.text, author_handle=tweet.author.username)
        if not reply_text:
            self.state.audit("reply_declined", tweet_id=tweet.id, author=tweet.author.username)
            summary["skipped"] += 1
            return True

        if self.cfg.mode == MODE_REVIEW:
            self.state.enqueue_draft({
                "type": "reply", "in_reply_to": tweet.id, "author": tweet.author.username,
                "tweet": tweet.text, "draft": reply_text,
            })
            self.state.audit("reply_queued", tweet_id=tweet.id, author=tweet.author.username,
                             draft=reply_text)
            summary["replied"] += 1  # produced a draft
            return True

        # autonomous or dry-run (x_client gates the actual send via will_post)
        result = self.client.reply(reply_text, tweet.id)
        self.state.record_action("reply", tweet.id)
        self.state.audit("reply_sent" if result.get("posted") else "reply_dry_run",
                         tweet_id=tweet.id, author=tweet.author.username,
                         text=reply_text, result=result)
        summary["replied"] += 1
        return True

    # --- like path ----------------------------------------------------------
    def _maybe_like(self, tweet, on_topic: bool, summary: dict) -> None:
        decision = self.policy.evaluate_like(tweet, on_topic=on_topic, input_safe=True)
        if not decision.act:
            summary["skipped"] += 1
            self.state.audit("skip", tweet_id=tweet.id, author=tweet.author.username,
                             reason=decision.reason)
            return
        if not self.state.under_limit("like", self.cfg.max_likes_per_hour,
                                      self.cfg.max_likes_per_day):
            self.state.audit("like_ratelimited", tweet_id=tweet.id)
            summary["skipped"] += 1
            return
        if self.cfg.mode == MODE_REVIEW:
            self.state.enqueue_draft({"type": "like", "tweet_id": tweet.id,
                                      "author": tweet.author.username, "tweet": tweet.text})
            self.state.audit("like_queued", tweet_id=tweet.id, author=tweet.author.username)
            summary["liked"] += 1
            return
        result = self.client.like(tweet.id)
        self.state.record_action("like", tweet.id)
        self.state.audit("like_sent" if result.get("liked") else "like_dry_run",
                         tweet_id=tweet.id, author=tweet.author.username, result=result)
        summary["liked"] += 1

    # --- loop ---------------------------------------------------------------
    def run_forever(self) -> None:
        signal.signal(signal.SIGTERM, self._handle_signal)
        signal.signal(signal.SIGINT, self._handle_signal)
        logger.info("iCLONE X engine starting — config: %s", self.cfg.redacted())
        v = self.client.verify()
        logger.info("X auth: %s", {k: v[k] for k in ("ok", "me", "read_enabled", "write_enabled")})
        if not v["ok"]:
            logger.error("X credentials invalid — engine will idle. Error: %s", v.get("error"))
        while not self._stop:
            try:
                self.run_cycle()
            except Exception as exc:
                logger.exception("cycle error: %s", exc)
            slept = 0
            while slept < self.cfg.poll_interval_seconds and not self._stop:
                time.sleep(1)
                slept += 1
        logger.info("iCLONE X engine stopped cleanly.")

    def _handle_signal(self, signum, _frame):
        logger.info("signal %s received — shutting down.", signum)
        self._stop = True
