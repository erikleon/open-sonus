# Issue 14: Named user

- Status: Open, no owner
- Source: `TODOS.md`

## Summary

Define a real named user or user persona who is the primary design target.

## Chosen persona

**Aisha Patel, 38, audio engineer and part-time music producer.** Owns a Sonos Move, an AirPlay-capable Apple TV 4K, and a pair of generic studio monitors driven by a Raspberry Pi running Snapcast. Has spent money on good speakers across ecosystems because each one was better at something different. Frustrated that the hardware she already owns cannot play together in sync, and that every vendor's app is designed to keep her inside their walled garden. She understands enough about audio to care about timing accuracy (she can hear phase errors), but does not want a terminal or config file just to group two rooms.

This persona captures three binding constraints the project already decided:

1. **She owns speakers from more than one vendor.** The cross-ecosystem requirement was accepted at scope decision #1 because without it, "the whole claim depends on one company's release schedule." Aisha is that claim in human form.
2. **She runs her own infrastructure.** She has a Pi and a NAS. Local-first, no-account, no-cloud means she keeps control of the devices she bought. That is not a preference; it is how she operates.
3. **She notices when the audio slips.** A person who cares about sync numbers will leave fast if the system sounds wrong but tells her it is fine. The diagnostics view for "a person who can hear phase errors" is what forced the per-room offset, buffer health, and signal-strength signals into M1.

## Acceptance criteria

- [ ] The project identifies a named user or specific user segment.
- [ ] The persona is used in design and product decisions.

## How Aisha drives later decisions

| Decision point | Why she matters |
|---|---|
| "Does this need an account?" | She would refuse one. Every account is a dependency she does not want on her hardware purchase. |
| "Is this feature local-only or cloud-anchored?" | Her NAS and off-hours listening schedule mean cloud is a liability, not a convenience. Local-first is product, not ideology. |
| "Should we ship cross-vendor sync as a claim or a measured number?" | She would hear any discrepancy immediately with trained ears. A post-hoc softening of N or R to save the claim would cost trust faster than admitting a fail and iterating. |
| "Does the interface surface require a terminal or config file?" | If she cannot reach sync in five minutes from her couch, the product is for everyone except its target user. The five-minute goal came from this constraint. |
| "Should we publish a reference speaker build?" | She has already built speakers herself. Published parts lists and measured numbers are how the project earns her respect rather than earning pity for a beta. |

The persona belongs in `README.md`, at the top of every `CONTRIBUTING.md` section that talks about priorities, and as the subject line whenever design trade-offs conflict: "what does Aisha do?" is the disambiguator.
