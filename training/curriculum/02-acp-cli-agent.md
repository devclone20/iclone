# Building an agent with the ACP CLI

`acp` (`@virtuals-protocol/acp-cli`) is how an agent becomes real: it
authenticates the operator, creates the agent and its signer, publishes
offerings and drives the job lifecycle. It is not a normal CLI — it holds
wallets and moves USDC.

**Authority ranking when sources disagree** (they do): 1) `acp <cmd> --help`
from the installed binary — generated from the code that runs; 2) the bundled
`SKILL.md` (`acp skill print`) — good prose, demonstrably stale; 3) any note
of ours — lowest, and it must say so when it loses.

**The authentication trap that cost us a real show:** `acp configure complete`
prints `status: pending` and **exits 0** while approval is still pending.
Never infer success from an exit code here. Approval is detected by TEXT
("pending" gone) plus a `whoami` that returns the agent's name. The same
class of bug: `acp skill check` exits 0 even when stale, and with no
`--against` its `upToDate` field is `null` — absence of a `false` is not a
pass. Parse fields, not exit codes.

Agent setup that survives contact: one session per agent identity; the
provider publishes offerings under the current price schema (priceV2); the
client needs a funded wallet before any preflight can say FUNDABLE.

## Key points

- `--help` of the installed binary is the highest authority; bundled docs go stale (frontmatter said 1.0.9 while the binary was 1.0.24).
- `acp configure complete` exits 0 while pending — detect approval by text + whoami, never by exit code.
- `acp skill check` exits 0 when stale; `upToDate: null` is not `true`. Parse the field.
- One CLI session per agent identity; provider needs a published offering (priceV2), client needs a funded wallet.
- Fund-moving commands are owner-gated; ad-hoc dispatches without the approval token are refused.

## Sources

- virtuals-cli
