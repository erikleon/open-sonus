"""Tests for wait_for_range_request in spike.harness.probe."""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from spike.harness.probe import wait_for_range_request


@dataclass
class FakeRequest:
    range_header: str | None = None


@pytest.fixture
def origin():
    """A fake origin that yields requests via requests(client)."""
    return FakeOrigin()


class FakeOrigin:
    def __init__(self):
        self._requests: list[FakeRequest] = []

    def requests(self, client: str) -> list[FakeRequest]:
        return self._requests


# ---------------------------------------------------------------------------
# No ranged request arrives before timeout
# ---------------------------------------------------------------------------

def test_whole_file_read_returns_none(origin):
    """A request without range_header is ignored; timeout yields (None, seen)."""
    origin._requests = [FakeRequest(range_header=None)]
    result, new_seen = wait_for_range_request(
        origin, client="192.0.2.1", seen=0, timeout=0.5,
    )
    assert result is None
    assert new_seen == 0


# ---------------------------------------------------------------------------
# A new ranged request appears beyond seen
# ---------------------------------------------------------------------------

def test_new_ranged_request_returns_the_request(origin):
    """When a fresh ranged request exists past seen the probe picks it up."""
    origin._requests = [FakeRequest(range_header=None), FakeRequest("bytes=1000-")]
    result, new_seen = wait_for_range_request(
        origin, client="192.0.2.1", seen=0, timeout=0.5,
    )
    assert result is not None
    assert result.range_header == "bytes=1000-"
    assert new_seen == 1


# ---------------------------------------------------------------------------
# Multiple ranged requests: returns last one
# ---------------------------------------------------------------------------

def test_several_ranged_requests_returns_last(origin):
    """With several ranged requests the probe returns the final count and request."""
    origin._requests = [
        FakeRequest("bytes=0-999"),
        FakeRequest("bytes=1000-1999"),
        FakeRequest("bytes=2000-2999"),
    ]
    result, new_seen = wait_for_range_request(
        origin, client="192.0.2.1", seen=0, timeout=0.1,
    )
    assert result is not None
    assert result.range_header == "bytes=2000-2999"
    assert new_seen == 3


# ---------------------------------------------------------------------------
# No new ranged request beyond seen
# ---------------------------------------------------------------------------

def test_no_new_ranged_returns_none_when_already_seen(origin):
    """If there is nothing past seen the probe returns (None, seen)."""
    origin._requests = [FakeRequest(range_header="bytes=0-999")]
    result, new_seen = wait_for_range_request(
        origin, client="192.0.2.1", seen=1, timeout=0.5,
    )
    assert result is None
    assert new_seen == 1
