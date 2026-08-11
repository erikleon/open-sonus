# TODOS

Deferred work. Deferred means scheduled or triggered, not abandoned. Each item keeps
its reasoning in `plans/2026-08-10-open-sonus-ceo.md`.

## Triggered items

These have a written trigger so they cannot drift into the pile of things that are
always next year.

### Freedom-to-operate patent analysis

Professional analysis of multi-room audio synchronisation patents, beyond the
self-read screen that runs during M0.

**Trigger:** M0 gate passes AND (first public binary release OR any commercial
activity OR first outside contributor merge). Fires early if the M0 screen concludes
the chosen mechanism looks close to an existing claim.

**Why it matters:** a credible infringement concern can invalidate the synchronisation
mechanism itself, so this is not orthogonal to engineering. Sonos holds at least five
patents titled "Time-synchronized, multizone media streaming" (US 10334306, 10587908,
11051066, 11463762, 11871067) and on 28 August 2025 the Federal Circuit reinstated a
$32.5M verdict against Google on zone-scene patents. An engineer's reading of a claim
chart carries no weight later.

**Why deferred:** a project with no users and no revenue is a poor damages target.
Cost scales with exposure, and exposure starts at public release. The M0 screen tells
you whether to worry; that is enough until the trigger.

### Trademark owner and policy

Name a legal owner for the project trademark and publish a usage policy.

**Trigger:** before the first public release.

**Why it matters:** Apache-2.0 does not protect the mission. A manufacturer may take
this code, close it, and ship exactly the locked-down product the project exists to
oppose. Trademark policy, the gravity of the reference implementation and a published
specification are the only levers, and trademark is the only one that is enforceable.

### Open multi-room specification

Extract and publish the wire protocol and endpoint contract as a versioned spec.

**Trigger:** a second independent implementation exists. Phase two provides it.

**Why it matters:** given the Apache-2.0 choice, a published specification is one of
the few remaining levers for keeping the ecosystem open.

### Host failover for bridged groups

Transfer a running bridged group to another host.

**Trigger:** field evidence that host loss is a common complaint.

**Architecture reserved now:** host identity and group audio state must be designed as
transferable from the start, even though nothing transfers them yet. The expensive
part is the state ownership design, not the handover code, and that part is being paid
for during M1.

## Deferred, no trigger yet

| Item | Why deferred |
|------|--------------|
| Custom manufactured hardware | Cost before validation. Revisit after phase two has users |
| Television, HDMI eARC, lip sync | Hard, specialist, orthogonal to the multi-room thesis |
| Remote access from outside the home | Large attack surface, weak first-year demand, contradicts local-first until the trust model is proven |
| Voice assistants | Enormous surface, and it reintroduces cloud dependency |
| Per-person accounts and permissions | A household is one trust domain until evidence says otherwise |
| Room correction and automatic tuning | Genuine acoustics work, and a phase two hardware feature |
| Hosting a bridged group from a phone | Mobile background execution limits probably make it infeasible. Note the consequence: the app-embedded core build is permanently native-group-only |

## Rejected, not deferred

| Item | Why |
|------|-----|
| Reimplementing streaming service clients | Keeps the repository distributable, sponsorable and app-store safe. Users can install grey-area providers themselves |

## Open, no owner

Raised by review and not yet answered. These are not engineering tasks and none of
them has been assigned.

- A named user. Not a segment, a person you can describe.
- A contributor acquisition plan. Community from day one is a decision, not a plan.
- A maintainer time budget, honestly estimated.
- A success metric that is not an engineering demonstration.
