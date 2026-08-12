# Harness

Measurement code for the feasibility spike. Written to keep: it becomes the nightly
acoustic rig later, so it is tested, unlike the protocol drivers next door.

## Control-authority probe

Answers two questions about an endpoint whose playout clock we cannot command:

- Can it be told to play slightly fast or slow?
- How finely can it be told where to start?

The second answer is not taken from the control API, because an endpoint can accept a
target it does not honour. Sonos accepts a millisecond seek, returns success, and starts
on the whole second below it. So the answer is read at the origin instead: with
constant-rate PCM, the byte a receiver asks for is the position it truly chose.

No microphone is involved, so this runs before any rig exists. Run it against every
pull-side endpoint before buying hardware.

```
uv run python -m spike.harness.probe 192.0.2.13
uv run python -m spike.harness.probe 192.0.2.13 --volume 8 --target 45.5 --target 121.25
```

The probe interrupts whatever the speaker is playing. It saves the transport state first
and restores it in a `finally` block, so an exception or a Ctrl-C still puts the speaker
back in its group at its original volume. If the restore itself fails it prints the saved
state to stderr so it can be replayed by hand.

## Modules

| Module | What it does | Tested |
|--------|--------------|--------|
| `content.py` | Constant-rate PCM corpus, and the byte-to-time arithmetic everything else depends on | yes |
| `origin.py` | Range-capable HTTP origin that logs where each receiver started reading | yes |
| `granularity.py` | Infers the real seek resolution from observed start positions | yes |
| `sonos.py` | Small UPnP client, enough to drive a probe | pure parts only |
| `probe.py` | Ties the above together against one endpoint | no, needs hardware |

`sonos.py` and `probe.py` are covered against real devices rather than mocks. A mocked
Sonos would confirm our assumptions about Sonos instead of testing them, and those
assumptions are the thing under investigation.

## Reading a result

`granularity.analyse()` reports the **coarsest** step consistent with the data, because
that is the weakest actuator the evidence rules out and a control loop has to be designed
against the weakest one. Two limits worth knowing:

- A receiver is only ever shown to be as fine as the targets asked it to be. Exact
  results mean "at least this fine", never "exactly this fine".
- The candidate list stops at one second. A coarser grid would not change any decision,
  since one second is already far outside any sync budget worth publishing.

## Tests

```
uv sync
uv run pytest
uv run ruff check .
```
