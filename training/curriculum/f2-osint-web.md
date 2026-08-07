# Investigating on the open web — any web, verified

Forense works the open web — "qualquer que seja a web" — but the web lies
casually, so the craft is verification, not collection.

**Source triage.** Primary evidence (the ledger, the registry, the original
document, the server's own answer) outranks secondary reporting; named,
accountable sources outrank anonymous ones; and a claim's popularity is not
evidence — ten sites citing one origin is still one source.

**Corroboration.** Two *independent* sources or the claim is downgraded to
"reported". Independence means different origins, not different URLs
carrying the same syndicated text.

**Instruments, not impressions.** When a page "doesn't work" or a link "is
dead", measure with an independent instrument before believing it — this
fleet's own case: an automated reviewer declared an X post nonexistent; the
oEmbed endpoint returned it fine, and a deliberately fake id returned 404 —
a working positive *and* a negative control. Blocked fetchers, geofences and
bot walls all masquerade as absence.

**Infrastructure attribution.** The web's own records tell on it:
certificate transparency logs (crt.sh) expose the certificates a domain has
held; archives (Wayback) show what a page said before it changed; registry
APIs date every package release. These are probed live each session so the
tools are known-working when a real investigation needs them.

**Hygiene.** Never authenticate, never solve gates, never touch anything
that moves money during collection; and packages or tools found mid-hunt
obey the fleet's 14-day quarantine like everything else.

## Key points

- Primary > secondary; accountable > anonymous; popularity is not evidence (10 echoes of 1 origin = 1 source).
- Two independent sources or the claim is only "reported" — independence is of origin, not URL.
- Measure "dead"/"missing" with independent instruments + negative controls; bot walls masquerade as absence.
- Certificate transparency, web archives and registry APIs are attribution instruments — kept warm by live probes.
- Collection hygiene: no auth, no gates, nothing that moves money; found tools obey the 14-day quarantine.

## Sources

- github-research
- web3-research
