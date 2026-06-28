"""
iCLONE — X (Twitter) API client.

A thin, tier-aware wrapper over tweepy's v2 Client. Responsibilities:
  • Authenticate (OAuth1 user-context for write/like; bearer for reads).
  • Read mentions WITH author verified fields (requires X API Basic tier+).
  • Post replies and likes — but ONLY when allowed to publish (see config.will_post).
  • Degrade safely on Free tier: read endpoints there return 403 → we disable reads
    and log clearly instead of crashing or guessing.
  • Honour dry-run / review: never call write endpoints unless config.will_post.

tweepy is imported lazily so this module (and the tests) import fine without it.
"""

from __future__ import annotations

import logging

from .config import XConfig
from .policy import Author, Tweet

logger = logging.getLogger("iclone.social.x_client")


class XClient:
    def __init__(self, config: XConfig):
        self.cfg = config
        self._client = None
        self._me = None
        self.read_enabled = config.has_read_creds
        self.write_enabled = config.has_write_creds

    # --- connection ---------------------------------------------------------
    def _connect(self):
        if self._client is not None:
            return self._client
        import tweepy  # lazy
        self._client = tweepy.Client(
            bearer_token=self.cfg.bearer_token or None,
            consumer_key=self.cfg.api_key or None,
            consumer_secret=self.cfg.api_secret or None,
            access_token=self.cfg.access_token or None,
            access_token_secret=self.cfg.access_token_secret or None,
            wait_on_rate_limit=True,
        )
        return self._client

    def verify(self) -> dict:
        """Confirm credentials and resolve our own user id. Safe to call on any tier."""
        result = {"ok": False, "me": None, "read_enabled": self.read_enabled,
                  "write_enabled": self.write_enabled, "error": ""}
        try:
            client = self._connect()
            me = client.get_me(user_auth=self.cfg.has_write_creds)
            self._me = me.data
            result["ok"] = True
            result["me"] = {"id": str(me.data.id), "username": me.data.username}
        except Exception as exc:
            result["error"] = str(exc)
            logger.error("verify() failed: %s", exc)
        return result

    @property
    def my_id(self) -> str | None:
        return str(self._me.id) if self._me else None

    # --- reads (require Basic tier+) ---------------------------------------
    def get_mentions(self, since_id: str | None, max_results: int = 20) -> list[Tweet]:
        """Fetch recent mentions of our account, with author verified fields.

        On Free tier this raises Forbidden (403) → we disable reads and return [].
        """
        if not self.read_enabled:
            return []
        try:
            client = self._connect()
            if self._me is None:
                self.verify()
            if self.my_id is None:
                return []
            resp = client.get_users_mentions(
                id=self.my_id,
                since_id=since_id or None,
                max_results=max(5, min(max_results, 100)),
                tweet_fields=["author_id", "lang", "in_reply_to_user_id", "referenced_tweets"],
                expansions=["author_id"],
                user_fields=["username", "verified", "verified_type"],
                user_auth=self.cfg.has_write_creds,
            )
            return self._parse_mentions(resp)
        except Exception as exc:
            name = type(exc).__name__
            if "Forbidden" in name or "403" in str(exc):
                logger.error(
                    "Reading mentions is FORBIDDEN — X API Free tier cannot read mentions. "
                    "Upgrade to Basic ($100/mo)+ to enable the verified-mention loop. "
                    "Disabling reads for this run."
                )
                self.read_enabled = False
            else:
                logger.error("get_mentions failed (%s): %s", name, exc)
            return []

    @staticmethod
    def _parse_mentions(resp) -> list[Tweet]:
        users = {}
        includes = getattr(resp, "includes", None) or {}
        for u in (includes.get("users") or []):
            users[str(u.id)] = u
        out: list[Tweet] = []
        for t in (resp.data or []):
            u = users.get(str(t.author_id))
            author = Author(
                id=str(t.author_id),
                username=getattr(u, "username", "") if u else "",
                verified=bool(getattr(u, "verified", False)) if u else False,
                verified_type=(getattr(u, "verified_type", "none") or "none") if u else "none",
            )
            refs = getattr(t, "referenced_tweets", None) or []
            is_reply = any(getattr(r, "type", "") == "replied_to" for r in refs)
            out.append(Tweet(id=str(t.id), text=t.text or "", author=author,
                             is_reply=is_reply, lang=getattr(t, "lang", "") or ""))
        return out

    # --- writes (gated by config.will_post) --------------------------------
    def reply(self, text: str, in_reply_to_id: str) -> dict:
        if not self.cfg.will_post:
            logger.info("[NO-POST] would reply to %s: %s", in_reply_to_id, text)
            return {"posted": False, "dry_run": True, "text": text, "in_reply_to": in_reply_to_id}
        try:
            client = self._connect()
            resp = client.create_tweet(text=text, in_reply_to_tweet_id=in_reply_to_id,
                                       user_auth=True)
            tid = str(resp.data.get("id")) if getattr(resp, "data", None) else ""
            logger.info("Replied to %s → %s", in_reply_to_id, tid)
            return {"posted": True, "id": tid, "in_reply_to": in_reply_to_id}
        except Exception as exc:
            logger.error("reply failed: %s", exc)
            return {"posted": False, "error": str(exc), "in_reply_to": in_reply_to_id}

    def like(self, tweet_id: str) -> dict:
        if not self.cfg.will_post:
            logger.info("[NO-POST] would like %s", tweet_id)
            return {"liked": False, "dry_run": True, "tweet_id": tweet_id}
        try:
            client = self._connect()
            client.like(tweet_id, user_auth=True)
            logger.info("Liked %s", tweet_id)
            return {"liked": True, "tweet_id": tweet_id}
        except Exception as exc:
            logger.error("like failed: %s", exc)
            return {"liked": False, "error": str(exc), "tweet_id": tweet_id}
