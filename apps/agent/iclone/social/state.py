"""
iCLONE — Social layer persistent state.

JSON-backed, stored under ICLONE_X_HOME (a SEPARATE directory from the ACP stack).
Tracks: the mentions cursor (since_id), already-processed tweet ids (so we never
reply twice), a rolling action ledger for rate limiting, a drafts queue (review
mode), and an append-only audit log of every decision and action.

Pure stdlib — no external deps — so it is trivially testable offline.
"""

from __future__ import annotations

import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger("iclone.social.state")

_MAX_PROCESSED = 5000   # cap memory of processed ids
_MAX_LEDGER = 4000      # cap action ledger entries


class State:
    def __init__(self, home: Path):
        self.home = Path(home)
        self.home.mkdir(parents=True, exist_ok=True)
        self.state_file = self.home / "state.json"
        self.drafts_file = self.home / "drafts.jsonl"
        self.audit_file = self.home / "audit.jsonl"
        self._data = self._load()

    # --- persistence --------------------------------------------------------
    def _load(self) -> dict:
        if self.state_file.exists():
            try:
                return json.loads(self.state_file.read_text())
            except Exception as exc:  # corrupt file — start clean, keep a backup
                logger.error("state.json unreadable (%s) — starting fresh", exc)
                try:
                    self.state_file.rename(self.state_file.with_suffix(".corrupt"))
                except Exception:
                    pass
        return {"since_id": None, "processed": [], "ledger": []}

    def save(self) -> None:
        # atomic write
        tmp = self.state_file.with_suffix(".tmp")
        tmp.write_text(json.dumps(self._data, indent=2))
        tmp.replace(self.state_file)

    # --- mentions cursor ----------------------------------------------------
    @property
    def since_id(self) -> str | None:
        return self._data.get("since_id")

    @since_id.setter
    def since_id(self, value: str | None) -> None:
        if value is not None:
            self._data["since_id"] = str(value)

    # --- dedupe -------------------------------------------------------------
    def already_processed(self, tweet_id: str) -> bool:
        return str(tweet_id) in self._data.get("processed", [])

    def mark_processed(self, tweet_id: str) -> None:
        p = self._data.setdefault("processed", [])
        sid = str(tweet_id)
        if sid not in p:
            p.append(sid)
            if len(p) > _MAX_PROCESSED:
                del p[: len(p) - _MAX_PROCESSED]

    # --- rate limiting ------------------------------------------------------
    def _count_since(self, action: str, seconds: float) -> int:
        cutoff = time.time() - seconds
        return sum(
            1 for e in self._data.get("ledger", [])
            if e.get("action") == action and e.get("ts", 0) >= cutoff
        )

    def under_limit(self, action: str, per_hour: int, per_day: int) -> bool:
        return (
            self._count_since(action, 3600) < per_hour
            and self._count_since(action, 86400) < per_day
        )

    def record_action(self, action: str, tweet_id: str = "", meta: dict | None = None) -> None:
        ledger = self._data.setdefault("ledger", [])
        ledger.append({
            "action": action,
            "ts": time.time(),
            "tweet_id": str(tweet_id),
            "iso": datetime.now(timezone.utc).isoformat(),
            **(meta or {}),
        })
        if len(ledger) > _MAX_LEDGER:
            del ledger[: len(ledger) - _MAX_LEDGER]

    # --- drafts (review mode) ----------------------------------------------
    def enqueue_draft(self, draft: dict) -> None:
        draft = {"queued_at": datetime.now(timezone.utc).isoformat(), **draft}
        with self.drafts_file.open("a") as f:
            f.write(json.dumps(draft) + "\n")

    # --- audit log ----------------------------------------------------------
    def audit(self, event: str, **fields) -> None:
        rec = {"ts": datetime.now(timezone.utc).isoformat(), "event": event, **fields}
        try:
            with self.audit_file.open("a") as f:
                f.write(json.dumps(rec) + "\n")
        except Exception as exc:
            logger.error("audit write failed: %s", exc)

    # --- stats --------------------------------------------------------------
    def stats(self) -> dict:
        return {
            "since_id": self.since_id,
            "processed_count": len(self._data.get("processed", [])),
            "replies_last_hour": self._count_since("reply", 3600),
            "replies_last_day": self._count_since("reply", 86400),
            "likes_last_hour": self._count_since("like", 3600),
            "likes_last_day": self._count_since("like", 86400),
        }
