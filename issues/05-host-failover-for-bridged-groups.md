# Issue 05: Host failover for bridged groups

- Status: Triggered
- Source: `TODOS.md`
- Trigger: Field evidence that host loss is a common complaint

## Summary

Design a transfer path for a running bridged group to another host while preserving group identity and audio state.

## Why this matters

Host identity and group audio state must be designed as transferable from the start. The expensive part is ownership design, not the handover code itself.

## Acceptance criteria

- [ ] The state ownership model supports host handoff.
- [ ] Transfer logic is documented and tested.
- [ ] Failure and recovery behavior is captured in architecture notes and test specs.
