# Root-cause investigation — to the origin, always

Forense's craft: any incident — a crime, a broken pipeline, a vanished file,
a failed trade — is investigated **to its origin**, never to its most
convenient explanation.

**The method, in order:**

1. **Evidence intake.** Collect before interpreting: logs, ledgers,
   screenshots, timestamps, run ids. Preserve first (f3).
2. **Timeline reconstruction.** Lay every event on one clock (UTC). Most
   mysteries die here — sequences expose causality that narratives hide.
3. **Hypothesis tree.** Enumerate candidate causes, cheapest-to-test first.
   Each test eliminates branches; never pick a favourite before testing.
4. **Descend to the origin.** Ask *why* until the answer is outside your
   system's control or points to a decision. The last log line is the
   *proximate* cause; the origin is usually layers below.
5. **Prove it.** A root cause you cannot demonstrate from primary evidence
   is a hypothesis, not a finding.

**Real cases from this fleet's own history:** a "failed review" whose truth
was *runner never acquired → GitHub Actions major outage* (0 steps executed
— the code was never suspect); a "stalled trade" whose origin was an ssh
tool's ~120s limit, not the marketplace (the trade had completed on-chain);
a training system failing on two unrelated origins at once (an archived
repository and an exhausted API balance) — one symptom, two causes, both
provable.

## Key points

- Order is law: evidence intake → timeline (one clock, UTC) → hypothesis tree → descend to origin → prove from primary evidence.
- Proximate ≠ root: the last log line names the symptom; keep asking why until the answer leaves your system.
- Test hypotheses cheapest-first; eliminate branches, never adopt favourites untested.
- One symptom can have several origins — enumerate before closing.
- A finding = a demonstration from primary evidence; anything less stays a hypothesis.

## Sources

- guardrails
