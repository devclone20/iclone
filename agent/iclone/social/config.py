"""
iCLONE — Social (X / Twitter) layer configuration.

A SEPARATE automation from the ACP commerce stack. It runs as its own systemd
service (`iclone-x.service`), with its own state directory and its own env, and it
imports NONE of the economic skills (acp/crypto/wallet). This is capability
isolation by design: no instruction received on X can make iCLONE move funds,
trade, or take any economic action — those capabilities do not exist in this
process. The X surface can only do three things: read mentions, reply, and like.

All configuration comes from environment variables. No secret is ever hardcoded.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


def _bool(name: str, default: bool) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on", "y"}


def _int(name: str, default: int) -> int:
    try:
        return int(os.environ.get(name, "").strip())
    except (TypeError, ValueError):
        return default


# Posting autonomy modes
MODE_DRY_RUN = "dry_run"      # log intended actions only — send NOTHING to X
MODE_REVIEW = "review"        # queue drafts for owner approval — send NOTHING until approved
MODE_AUTONOMOUS = "autonomous"  # act within policy, no human in the loop per action
VALID_MODES = {MODE_DRY_RUN, MODE_REVIEW, MODE_AUTONOMOUS}


@dataclass
class XConfig:
    """Configuration for iCLONE's public X voice. Defaults are SAFE by design."""

    # --- master switches -----------------------------------------------------
    enabled: bool = False             # kill-switch. False = engine idles, sends nothing.
    mode: str = MODE_DRY_RUN          # dry_run | review | autonomous

    # --- identity ------------------------------------------------------------
    handle: str = "icloneframe"       # our handle, without '@'
    owner_handle: str = ""            # the developer's own handle (optional), without '@'

    # --- credentials (X API) -------------------------------------------------
    api_key: str = ""                 # OAuth1 consumer key
    api_secret: str = ""              # OAuth1 consumer secret
    access_token: str = ""            # OAuth1 user access token
    access_token_secret: str = ""     # OAuth1 user access token secret
    bearer_token: str = ""            # OAuth2 app-only bearer (reads)

    # --- LLM -----------------------------------------------------------------
    anthropic_api_key: str = ""
    model: str = "claude-opus-4-8"    # matches neural_soul base model
    max_reply_tokens: int = 400

    # --- engagement policy ---------------------------------------------------
    reply_verified_only: bool = True  # replies ONLY to verified (blue/gold/business) accounts
    like_verified_only: bool = False  # likes allowed from any account (owner choice)
    require_question: bool = True     # reply only to direct QUESTIONS to @handle
    require_mention: bool = True      # reply only when @handle is mentioned
    max_tweet_chars: int = 280        # hard cap on generated replies

    # --- rate limits (defense-in-depth + cost control) -----------------------
    poll_interval_seconds: int = 180
    max_replies_per_hour: int = 5
    max_replies_per_day: int = 30
    max_likes_per_hour: int = 20
    max_likes_per_day: int = 100
    mentions_per_poll: int = 20       # how many recent mentions to pull per cycle

    # --- storage -------------------------------------------------------------
    home: Path = field(default_factory=lambda: Path(os.environ.get("ICLONE_X_HOME", "./.x-state")))

    # ------------------------------------------------------------------------
    @classmethod
    def from_env(cls) -> "XConfig":
        mode = os.environ.get("X_MODE", MODE_DRY_RUN).strip().lower()
        if mode not in VALID_MODES:
            mode = MODE_DRY_RUN

        cfg = cls(
            enabled=_bool("X_ENABLED", False),
            mode=mode,
            handle=os.environ.get("X_HANDLE", "icloneframe").lstrip("@").strip(),
            owner_handle=os.environ.get("X_OWNER_HANDLE", "").lstrip("@").strip(),
            api_key=os.environ.get("X_API_KEY", ""),
            api_secret=os.environ.get("X_API_SECRET", ""),
            access_token=os.environ.get("X_ACCESS_TOKEN", ""),
            access_token_secret=os.environ.get("X_ACCESS_TOKEN_SECRET", ""),
            bearer_token=os.environ.get("X_BEARER_TOKEN", ""),
            anthropic_api_key=os.environ.get("ANTHROPIC_API_KEY", ""),
            model=os.environ.get("X_MODEL", "claude-opus-4-8"),
            max_reply_tokens=_int("X_MAX_REPLY_TOKENS", 400),
            reply_verified_only=_bool("X_REPLY_VERIFIED_ONLY", True),
            like_verified_only=_bool("X_LIKE_VERIFIED_ONLY", False),
            require_question=_bool("X_REQUIRE_QUESTION", True),
            require_mention=_bool("X_REQUIRE_MENTION", True),
            max_tweet_chars=_int("X_MAX_TWEET_CHARS", 280),
            poll_interval_seconds=_int("X_POLL_INTERVAL", 180),
            max_replies_per_hour=_int("X_MAX_REPLIES_PER_HOUR", 5),
            max_replies_per_day=_int("X_MAX_REPLIES_PER_DAY", 30),
            max_likes_per_hour=_int("X_MAX_LIKES_PER_HOUR", 20),
            max_likes_per_day=_int("X_MAX_LIKES_PER_DAY", 100),
            mentions_per_poll=_int("X_MENTIONS_PER_POLL", 20),
            home=Path(os.environ.get("ICLONE_X_HOME", "./.x-state")),
        )
        return cfg

    # ------------------------------------------------------------------------
    @property
    def has_write_creds(self) -> bool:
        """OAuth1 user-context creds present (needed to post + like)."""
        return all([self.api_key, self.api_secret, self.access_token, self.access_token_secret])

    @property
    def has_read_creds(self) -> bool:
        """Bearer or user creds present (reads still require X API Basic tier+)."""
        return bool(self.bearer_token) or self.has_write_creds

    @property
    def will_post(self) -> bool:
        """True only when the engine is actually allowed to publish to X."""
        return self.enabled and self.mode == MODE_AUTONOMOUS and self.has_write_creds

    def redacted(self) -> dict:
        """Safe-to-log view — never exposes secrets."""
        def mark(v: str) -> str:
            return "set" if v else "MISSING"
        return {
            "enabled": self.enabled,
            "mode": self.mode,
            "handle": f"@{self.handle}",
            "owner_handle": f"@{self.owner_handle}" if self.owner_handle else "",
            "model": self.model,
            "reply_verified_only": self.reply_verified_only,
            "like_verified_only": self.like_verified_only,
            "require_question": self.require_question,
            "poll_interval_seconds": self.poll_interval_seconds,
            "rate_limits": {
                "replies_h": self.max_replies_per_hour, "replies_d": self.max_replies_per_day,
                "likes_h": self.max_likes_per_hour, "likes_d": self.max_likes_per_day,
            },
            "creds": {
                "api_key": mark(self.api_key), "api_secret": mark(self.api_secret),
                "access_token": mark(self.access_token),
                "access_token_secret": mark(self.access_token_secret),
                "bearer_token": mark(self.bearer_token),
                "anthropic_api_key": mark(self.anthropic_api_key),
            },
            "home": str(self.home),
        }
