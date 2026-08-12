"""Control-authority probe for a pull-side receiver.

Answers two questions about an endpoint whose playout clock cannot be commanded:

  Can it be told to play slightly fast or slow?
  How finely can it be told where to start?

The second answer cannot be trusted to the control API, which may report a precision it
does not deliver. It is taken from the origin instead: with constant-rate PCM, the byte a
receiver asks for is the position it truly chose. No microphone is involved, so this runs
before any rig exists.

The probe interrupts whatever the speaker is doing. It saves the transport state first and
restores it in a finally block, including on Ctrl-C.
"""

from __future__ import annotations

import argparse
import socket
import sys
import time
from pathlib import Path

from spike.harness import content, granularity, sonos

# Spread so the whole-second parts share no common factor. Targets at 30, 90, 150 would
# leave a one-second grid indistinguishable from a ten-second one. The fractions descend
# in binary steps so a receiver working in power-of-two subdivisions is also revealed.
DEFAULT_TARGETS_S = (30.0, 91.5, 152.25, 213.125, 264.75)
DEFAULT_BUDGET_MS = 10.0


def local_address_towards(host: str) -> str:
    """The address this machine presents to that host.

    Picked by asking the routing table rather than by listing interfaces, because a host
    with two addresses on one subnet gives no way to choose between them by inspection.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect((host, 1400))
        return s.getsockname()[0]
    finally:
        s.close()


def save_state(host: str) -> dict[str, str]:
    media = sonos.transport(host, "GetMediaInfo")
    volume = sonos.rendering(host, "GetVolume")
    mute = sonos.rendering(host, "GetMute")
    return {
        "CurrentURI": media.get("CurrentURI", "") or "",
        "CurrentURIMetaData": media.get("CurrentURIMetaData", "") or "",
        "volume": volume.get("CurrentVolume", "20"),
        "mute": mute.get("CurrentMute", "0"),
    }


def restore_state(host: str, state: dict[str, str]) -> bool:
    """Put the endpoint back. Returns whether the transport URI came back as saved."""
    try:
        sonos.transport(host, "Stop")
    except sonos.SoapFault:
        pass  # already stopped; the URI restore below is what matters
    sonos.rendering(host, "SetVolume", DesiredVolume=state["volume"])
    sonos.rendering(host, "SetMute", DesiredMute=state["mute"])
    sonos.transport(
        host,
        "SetAVTransportURI",
        CurrentURI=state["CurrentURI"],
        CurrentURIMetaData=state["CurrentURIMetaData"],
    )
    now = sonos.transport(host, "GetMediaInfo").get("CurrentURI", "")
    return now == state["CurrentURI"]


def wait_for_range_request(origin, client: str, seen: int, timeout: float = 12.0):
    """Wait for the receiver to open a new byte range, and return that request.

    Whole-file reads are ignored: a seek produces a header re-read at byte 0 followed by
    the range request that carries the answer.
    """
    deadline = time.time() + timeout
    while time.time() < deadline:
        ranged = [r for r in origin.requests(client) if r.range_header]
        if len(ranged) > seen:
            return ranged[-1], len(ranged)
        time.sleep(0.2)
    return None, seen


def probe_rate_actuator(host: str, speeds=("1.02", "0.98")) -> dict[str, str]:
    """Ask the endpoint to play off-speed. A refusal means no continuous actuator."""
    results = {}
    for speed in speeds:
        try:
            sonos.transport(host, "Play", Speed=speed)
            results[speed] = "ACCEPTED"
        except sonos.SoapFault as fault:
            results[speed] = f"refused, UPnP error {fault.code}"
    return results


def run(host: str, workdir: Path, targets, duration_s: float, volume: int, budget_ms: float):
    from spike.harness.origin import Origin

    workdir.mkdir(parents=True, exist_ok=True)
    wav = workdir / "probe.wav"
    if not wav.exists():
        print(f"generating {duration_s:g}s of constant-rate PCM ...")
        content.write_probe_wav(wav, duration_s)
    spec = content.PcmSpec()
    offset = content.data_offset(wav)

    advertise = local_address_towards(host)
    origin = Origin(wav, workdir / "origin_log.jsonl").start()
    url = origin.url_for(advertise)
    print(f"origin serving {url}  (data starts at byte {offset})")

    print(f"saving transport state of {host} ...")
    state = save_state(host)
    print(f"  was: {state['CurrentURI'] or '(nothing)'} at volume {state['volume']}")

    observations: list[granularity.SeekObservation] = []
    rate_results: dict[str, str] = {}
    try:
        sonos.rendering(host, "SetVolume", DesiredVolume=volume)
        sonos.transport(host, "BecomeCoordinatorOfStandaloneGroup")
        time.sleep(1.5)
        sonos.transport(host, "SetAVTransportURI", CurrentURI=url, CurrentURIMetaData="")
        sonos.transport(host, "Play", Speed="1")
        time.sleep(3.0)

        print("\nrate actuator:")
        rate_results = probe_rate_actuator(host)
        for speed, outcome in rate_results.items():
            print(f"  Play Speed={speed}: {outcome}")

        print("\nseek granularity:")
        seen = len([r for r in origin.requests(host) if r.range_header])
        for target in targets:
            text = sonos.format_rel_time(target)
            try:
                sonos.transport(host, "Seek", Unit="REL_TIME", Target=text)
            except sonos.SoapFault as fault:
                print(f"  {text:<16} refused, UPnP error {fault.code}")
                continue
            request, seen = wait_for_range_request(origin, host, seen)
            if request is None:
                print(f"  {text:<16} accepted, no new fetch (served from buffer)")
                continue
            observed = request.start_seconds(spec.bytes_per_second, offset)
            observations.append(granularity.SeekObservation(target, observed))
            print(
                f"  {text:<16} asked for byte {request.start_byte:>10}"
                f"  = {observed:10.6f}s   error {(observed - target) * 1000:+9.1f} ms"
            )
            time.sleep(1.5)
    finally:
        print("\nrestoring transport state ...")
        try:
            ok = restore_state(host, state)
            print(f"  restored: {ok}")
        except Exception as exc:  # noqa: BLE001 - report and continue; the log is the record
            print(f"  RESTORE FAILED: {exc}", file=sys.stderr)
            print(f"  saved state was: {state}", file=sys.stderr)
        origin.stop()

    if observations:
        report = granularity.analyse(observations)
        print("\n" + report.summary(budget_ms))
    return observations, rate_results


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("host", help="endpoint address, e.g. 192.0.2.13")
    parser.add_argument("--workdir", type=Path, default=Path("probe-run"))
    parser.add_argument("--duration", type=float, default=300.0)
    parser.add_argument("--volume", type=int, default=12, help="volume during the probe")
    parser.add_argument("--budget-ms", type=float, default=DEFAULT_BUDGET_MS)
    parser.add_argument(
        "--target", type=float, action="append", dest="targets",
        help="seek target in seconds; repeatable, defaults to a spread with fractions",
    )
    args = parser.parse_args(argv)
    run(
        host=args.host,
        workdir=args.workdir,
        targets=args.targets or list(DEFAULT_TARGETS_S),
        duration_s=args.duration,
        volume=args.volume,
        budget_ms=args.budget_ms,
    )


if __name__ == "__main__":
    main()
