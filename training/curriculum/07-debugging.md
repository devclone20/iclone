# Debugging the trade rails — error taxonomy and resolution

Errors on money rails divide into classes, and the class decides the move.
Misclassifying is how tooling failures become financial ones.

**1. Authorization state lies.** `acp configure complete` exits 0 while
pending. Class: *false-success*. Move: detect by text + whoami; never trust
exit codes on this CLI (same for `skill check`'s `upToDate: null`).

**2. Payment required (402).** A paid gateway answers 402: the balance is
gone. Class: *billing*. Move: stop, report, top up deliberately. Retrying a
dead balance is noise at best, double-spend risk at worst. The same class
wears another mask on the Anthropic API: `400 credit balance is too low`.

**3. Funds moved, then failure.** The log said escrow holds funds, then the
run FAILED. Class: *post-funding failure* — the most dangerous. Move: HARD
STOP; never relaunch automatically; reconcile the ledger by hand (which
phases fired? did the payout land?), then clear state deliberately.

**4. Long-runner death.** A persona held a multi-minute command and died
~120s in. Class: *architecture*. Move: detach the work (transient unit),
derive state from the log, poll short. The fix is a pattern, not a retry.

**5. Infrastructure outage.** CI cancelled with 0 steps ("job was not
acquired by Runner"), or an event produced no run at all. Class: *infra*.
Move: check the status page first (Actions was in major_outage when this
module was written); after recovery, re-trigger by pushing to the branch.
0 steps executed = your code was never the problem.

**6. Stale documentation.** The bundled manual disagrees with `--help`.
Class: *authority conflict*. Move: the installed binary's help wins; note
the disagreement so the next agent doesn't relearn it.

The debugging discipline across all classes: reproduce the claim from
primary evidence (ledger, logs, status pages), classify before acting, and
make the safe move the *default* — guards in metal (cooldowns, in-flight
refusals, hard blocks) so a confused agent cannot hurt the wallet.

## Key points

- Classify first: false-success · billing · post-funding · architecture · infra · stale-docs. The class decides the move.
- Post-funding failure = hard stop + manual ledger reconciliation. Never auto-retry anything that moved funds.
- 402 / credit-low = billing: stop and report; retrying cannot fix a balance.
- CI cancelled with 0 steps = infrastructure; check the status page, re-trigger by push after recovery.
- Guards live in metal (cooldown, in-flight refusal, hard block) so no confused agent can spend twice.

## Sources

- virtuals-cli
- guardrails
