"""Only the pure parts are covered here. Everything that talks to a device is exercised by
running the probe against real hardware, because a mocked Sonos would confirm our
assumptions about Sonos rather than test them."""

from __future__ import annotations

import pytest

from spike.harness.sonos import SoapFault, format_rel_time


@pytest.mark.parametrize(
    ("seconds", "expected"),
    [
        (0.0, "0:00:00"),
        (30.0, "0:00:30"),
        (91.5, "0:01:31.500"),
        (152.25, "0:02:32.250"),
        (213.125, "0:03:33.125"),
        (3661.0, "1:01:01"),
        (3661.007, "1:01:01.007"),
    ],
)
def test_rel_time_formatting(seconds, expected):
    assert format_rel_time(seconds) == expected


def test_fraction_is_sent_rather_than_pre_rounded():
    # The probe exists to find out what the device does with a fraction it cannot honour.
    # Rounding here would answer the question with our own behaviour instead.
    assert format_rel_time(90.5).endswith(".500")


def test_fault_carries_the_upnp_code_for_the_report():
    fault = SoapFault("Play", "717")
    assert fault.code == "717"
    assert "717" in str(fault)
