# Issue 02: Cast endpoint validation

- Status: Triggered
- Source: `TODOS.md`, `plans/2026-08-10-open-sonus-ceo.md`
- Trigger: Before public claims that open-sonus groups Cast devices, or before M1 freezes the endpoint contract

## Summary

Measure a Cast receiver against the decision table and answer the live-edge question the authority matrix raises for pull-side joins.

## Why this matters

M0 intentionally leaves the Cast/live-edge case unresolved. Without validation, no M0 result can be quoted as covering Cast devices.

## Acceptance criteria

- [ ] A Cast receiver is acquired or otherwise available for test.
- [ ] Pull-side live-edge behavior is measured under the published decision table.
- [ ] The results are recorded and either published as a contract decision or triaged as a required M1 task.
