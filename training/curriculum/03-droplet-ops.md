# Trading through a droplet — the remote body pattern

The fleet's law: **the ACP CLI never runs on the workstation.** The agents'
"body" is a remote host (a droplet) reached over an ssh alias; keys, signers
and sessions live there and only there. The workstation orchestrates; the
droplet executes.

The pattern that makes this reliable:

1. **Short calls only.** An agent persona that holds one ssh command for
   minutes dies mid-flight (~120s in our stack). Long work is never held.
2. **Detached execution.** Fund-moving work launches in a transient systemd
   unit (`systemd-run`) and the ssh call returns in about a second.
3. **Log as truth.** The unit appends to one log file; state is *derived*
   from it: RUNNING (unit active) → COMPLETE (log says so) → FAILED (log
   non-empty without completion) → IDLE. Any caller that lost its connection
   recovers the truth with one short `status` call.
4. **Poll, don't hold.** Follow a 2–4 minute trade with a short status poll
   every ~25 seconds — one quick command per poll.
5. **Guard rails in metal.** The wrapper refuses a second in-flight run,
   applies a cooldown after completion, and hard-blocks relaunch after any
   failure that happened post-funding.

Never in CI, never in training runs: no ssh to the droplet, no CLI
execution. Training studies the pattern; the droplet performs it.

## Key points

- ACP CLI is droplet-only; the workstation never holds keys or sessions.
- Long commands kill personas (~120s) — launch detached (transient systemd unit), return in ~1s.
- State is derived from the log: RUNNING / COMPLETE / FAILED / IDLE; `status` is always safe and instant.
- Poll every ~25s with short calls; never hold a connection across a trade.
- Wrapper guard rails: in-flight refusal · post-completion cooldown · hard block after FAILED-post-funding.

## Sources

- virtuals-cli
- clone-frame-orchestration
