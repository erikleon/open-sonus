# open-sonus issue backlog

This backlog translates the deferred work in `TODOS.md` and the strategic decisions in `plans/2026-08-10-open-sonus-ceo.md` into actionable GitHub issues.

Sources:
- `TODOS.md`
- `plans/2026-08-10-open-sonus-ceo.md`

## Triggered issues

### Issue 1: Freedom-to-operate patent analysis
- Status: Triggered
- Source: `TODOS.md`, `plans/.../2026-08-10-open-sonus-ceo.md` (`Patent screen, parallel lane`)
- Trigger: M0 gate passes AND (first public binary release OR any commercial activity OR first outside contributor merge)
- Description: Commission a professional review of multi-room audio synchronization patents beyond the self-read screen used during M0.
- Why it matters: A credible infringement concern can invalidate the synchronization mechanism itself; Sonos holds multiple relevant patents and the legal risk is material.
- Acceptance criteria:
  - [ ] External counsel or specialist review is commissioned before the first public binary release or commercial activity.
  - [ ] The review evaluates the chosen synchronization architecture against the relevant patent landscape.
  - [ ] The result is documented in-repo and linked to the release/engineering decision gate.

### Issue 2: Cast endpoint validation
- Status: Triggered
- Source: `TODOS.md`, `plans/.../2026-08-10-open-sonus-ceo.md` (`Required pairs, and the Cast decision`)
- Trigger: Before public claims that open-sonus groups Cast devices, or before M1 freezes the endpoint contract.
- Description: Measure a Cast receiver against the decision table and answer the live-edge question for pull-side joins.
- Why it matters: The M0 plan explicitly leaves the Cast/live-edge case unresolved; without validation, no M0 claim can be generalized to Cast.
- Acceptance criteria:
  - [ ] A Cast receiver is acquired or otherwise available for test.
  - [ ] Pull-side live-edge behavior is measured under the decision table.
  - [ ] The findings are recorded and either published as a contract decision or triaged as a required M1 task.

### Issue 3: Trademark owner and policy
- Status: Triggered
- Source: `TODOS.md`
- Trigger: Before the first public release.
- Description: Name a legal owner for the project trademark and publish usage policy.
- Why it matters: Apache-2.0 does not protect the mission; a downstream vendor could close the product the project exists to oppose.
- Acceptance criteria:
  - [ ] A named trademark owner is documented.
  - [ ] A public usage policy is published.
  - [ ] The policy is reviewed by legal or project leadership before the first public release.

### Issue 4: Open multi-room specification
- Status: Triggered
- Source: `TODOS.md`
- Trigger: A second independent implementation exists.
- Description: Extract and publish the wire protocol and endpoint contract as a versioned specification.
- Why it matters: An Apache-2.0 project needs a published protocol to preserve ecosystem openness and compatibility.
- Acceptance criteria:
  - [ ] The protocol and endpoint contract are versioned and documented.
  - [ ] The specification is stable enough to support multiple independent implementations.
  - [ ] The project has a process for version changes and compatibility notes.

### Issue 5: Host failover for bridged groups
- Status: Triggered
- Source: `TODOS.md`
- Trigger: Field evidence that host loss is a common complaint.
- Description: Design a transfer path for an active bridged group to another host without loss of group state identity.
- Why it matters: Host identity and group audio state must be designed for transfer from the start; the expensive part is state ownership design.
- Acceptance criteria:
  - [ ] State ownership model is designed for host handoff.
  - [ ] The transfer mechanism is documented and tested.
  - [ ] Failure and recovery behavior is captured in the design notes and tests.

## Deferred issues (no trigger yet)

### Issue 6: Custom manufactured hardware
- Status: Deferred
- Source: `TODOS.md`
- Why deferred: Cost before validation. Revisit after phase two has users.
- Description: Evaluate a custom-manufactured reference speaker or hardware route only after real users and usage evidence exist.
- Acceptance criteria:
  - [ ] A user need is documented and validated.
  - [ ] The hardware plan is compared against existing open hardware and phase-two requirements.
  - [ ] The cost and support model are reviewed before committing to manufacturing.

### Issue 7: Television, HDMI eARC, and lip sync
- Status: Deferred
- Source: `TODOS.md`
- Why deferred: Hard, specialist, and orthogonal to the multi-room thesis.
- Description: Investigate HDMI eARC, television integration, and lip-sync fidelity once the core multi-room group design is proven.
- Acceptance criteria:
  - [ ] The technical constraints are documented.
  - [ ] The effort is scoped against the core roadmap.
  - [ ] A decision is made whether to defer or pursue as a separate project lane.

### Issue 8: Remote access from outside the home
- Status: Deferred
- Source: `TODOS.md`
- Why deferred: Large attack surface, weak first-year demand, and inconsistent with local-first trust until the model is proven.
- Description: Design remote access only after the local-first trust model is validated.
- Acceptance criteria:
  - [ ] Threat model and security review are completed.
  - [ ] User demand and support cost are validated.
  - [ ] The feature is gated behind a clear trust and remote-auth architecture.

### Issue 9: Voice assistants
- Status: Deferred
- Source: `TODOS.md`
- Why deferred: Enormous surface area and reintroduces cloud dependency.
- Description: Evaluate voice assistant integration only when the platform architecture, trust model, and user demand are clear.
- Acceptance criteria:
  - [ ] A narrow, well-scoped voice integration plan exists.
  - [ ] Privacy and cloud dependencies are explicitly evaluated.
  - [ ] The feature is not added before the local-first architecture is stable.

### Issue 10: Per-person accounts and permissions
- Status: Deferred
- Source: `TODOS.md`
- Why deferred: A household is one trust domain until evidence says otherwise.
- Description: Delay per-person accounts until there is evidence that household-level trust boundaries are not adequate.
- Acceptance criteria:
  - [ ] Household trust model is documented.
  - [ ] The need for multi-user permissions is validated by real usage and not conjecture.
  - [ ] Explicit account design is deferred unless evidence supports it.

### Issue 11: Room correction and automatic tuning
- Status: Deferred
- Source: `TODOS.md`
- Why deferred: Genuine acoustics work and a phase-two hardware feature.
- Description: Investigate room correction and automatic tuning after the core multi-room system is validated and hardware is more mature.
- Acceptance criteria:
  - [ ] The feature is scoped as a phase-two hardware or acoustics project.
  - [ ] Measurement and tuning workflows are defined.
  - [ ] A user-facing value proposition exists before committing resources.

### Issue 12: Hosting a bridged group from a phone
- Status: Deferred
- Source: `TODOS.md`
- Why deferred: Mobile background execution limits probably make it infeasible; the app-embedded core becomes native-group-only.
- Description: Determine whether phone-hosted bridged groups are feasible and document the resulting platform constraints.
- Acceptance criteria:
  - [ ] The limits of phone execution and background service support are evaluated.
  - [ ] The project decides whether the embedded app remains native-group-only.
  - [ ] The decision is documented for app and architecture design.

## Rejected issue

### Issue 13: Reimplement streaming service clients
- Status: Rejected
- Source: `TODOS.md`
- Why rejected: Keeps the repository distributable, sponsorable and app-store safe; users can install grey-area providers themselves.
- Description: Do not reimplement streaming service clients in the main repository.
- Acceptance criteria:
  - [ ] Maintain an out-of-tree provider plugin boundary.
  - [ ] Keep direct support to local, Jellyfin, Navidrome, Subsonic, and radio, as planned.
  - [ ] Refuse in-repo implementations that create legal or distributability risk.

## Open issues without an owner

### Issue 14: Named user
- Status: Open, no owner
- Source: `TODOS.md`
- Description: Define a real named user or user persona who is the primary design target.
- Acceptance criteria:
  - [ ] The project identifies a named user or specific user segment.
  - [ ] The persona is used in design and product decisions.

### Issue 15: Contributor acquisition plan
- Status: Open, no owner
- Source: `TODOS.md`, `plans/.../2026-08-10-open-sonus-ceo.md`
- Description: Create a concrete contributor acquisition plan rather than relying on community as an abstract goal.
- Acceptance criteria:
  - [ ] A plan is published for attracting contributors.
  - [ ] It names concrete onboarding, maintenance, and visibility actions.

### Issue 16: Maintainer time budget
- Status: Open, no owner
- Source: `TODOS.md`
- Description: Estimate and document a realistic maintainer time budget.
- Acceptance criteria:
  - [ ] The project publishes a maintainer time estimate.
  - [ ] It is honest about capacity and maintenance load.

### Issue 17: Success metric beyond engineering demonstrations
- Status: Open, no owner
- Source: `TODOS.md`
- Description: Define a user- and business-facing success metric that is not merely an engineering proof point.
- Acceptance criteria:
  - [ ] A non-technical success metric is documented.
  - [ ] It tracks the project’s broader outcome, not only technical viability.

## Plan-backed product issues from the CEO roadmap

These are strategic backlog items that appear in the plan and should be tracked as product and architecture issues even though they are not all listed in `TODOS.md`.

### Issue 18: Cross-ecosystem discovery and grouping
- Status: Planned for phase one
- Source: `plans/.../2026-08-10-open-sonus-ceo.md` (`Scope decisions`, item 1)
- Description: Support cross-ecosystem discovery and grouping across Sonos, AirPlay, Chromecast, UPnP, and Snapcast in phase one.
- Acceptance criteria:
  - [ ] Endpoint discovery is abstracted by room and not protocol.
  - [ ] Grouping works across ecosystems without forcing users to learn vendor terminology.

### Issue 19: Sync accuracy and CI gate
- Status: Planned for M0/M1
- Source: `plans/.../2026-08-10-open-sonus-ceo.md` (`Scope decisions`, item 2)
- Description: Implement a sync library and measurement rig with explicit performance budgets and CI enforcement.
- Acceptance criteria:
  - [ ] There is a published per-protocol accuracy budget.
  - [ ] The measurement harness is used as a nightly CI gate.
  - [ ] Drift and correction trade-offs are explicit and testable.

### Issue 20: Local-first streaming service plugin boundary
- Status: Planned
- Source: `plans/.../2026-08-10-open-sonus-ceo.md` (`Scope decisions`, item 3)
- Description: Keep direct support for local media and a plugin boundary for streaming providers.
- Acceptance criteria:
  - [ ] Repository stays distributable and sponsorable.
  - [ ] Provider plugins remain out-of-tree and optional.

### Issue 21: Device identity, encrypted control plane, and signed updates
- Status: Planned from day one
- Source: `plans/.../2026-08-10-open-sonus-ceo.md` (`Scope decisions`, item 4)
- Description: Implement device identity, authenticated and encrypted control plane messaging, signed releases, and a threat model from day one.
- Acceptance criteria:
  - [ ] Device identity and trust model are specified.
  - [ ] Control-plane encryption and authentication are in place.
  - [ ] Signed update and rollback policy is documented.

### Issue 22: Reference speaker build
- Status: Planned for phase one
- Source: `plans/.../2026-08-10-open-sonus-ceo.md` (`Scope decisions`, item 5)
- Description: Publish a reference speaker build with parts list, printable case, flashable image, and measured sync numbers.
- Acceptance criteria:
  - [ ] A reproducible reference speaker build exists.
  - [ ] The build is documented and reviewable.
  - [ ] Sync numbers are measured and published.

### Issue 23: CLI, browser UI, and diagnostics surface
- Status: Planned
- Source: `plans/.../2026-08-10-open-sonus-ceo.md` (`Scope decisions`, item 6)
- Description: Deliver the CLI, browser surface, and room diagnostics view needed for power users and debugging.
- Acceptance criteria:
  - [ ] A command-line interface exists for local control and diagnostics.
  - [ ] A browser-based interface is available for install-free local use.
  - [ ] Live per-room diagnostics support debugging and performance validation.

## Notes

- This file intentionally does not rewrite the repository’s original planning documents; it is a backlog view of the same decisions.
- The backlog should be used as a source of truth for issue creation in GitHub or another tracker, while `TODOS.md` remains the live trigger list and the CEO plan remains the design rationale.
