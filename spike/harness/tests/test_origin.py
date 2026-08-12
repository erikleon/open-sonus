"""The origin is the measuring instrument. If it misreports a byte range, the seek result
is wrong in a way nothing downstream can detect."""

from __future__ import annotations

import urllib.request

import pytest

from spike.harness.content import PcmSpec, data_offset, write_probe_wav
from spike.harness.origin import Origin, parse_byte_range


@pytest.fixture
def origin(tmp_path):
    wav = write_probe_wav(tmp_path / "probe.wav", duration_s=2.0)
    with Origin(wav, tmp_path / "log.jsonl") as o:
        yield o


def fetch(origin, byte_range=None):
    request = urllib.request.Request(origin.url_for("127.0.0.1"))
    if byte_range:
        request.add_header("Range", byte_range)
    with urllib.request.urlopen(request, timeout=5) as response:
        return response.status, response.headers, response.read()


@pytest.mark.parametrize(
    ("header", "size", "expected"),
    [
        ("bytes=100-", 1000, (100, 999)),
        ("bytes=100-200", 1000, (100, 200)),
        ("bytes=0-0", 1000, (0, 0)),
        ("bytes=100-99999", 1000, (100, 999)),  # clamped, not an error
        ("bytes=-50", 1000, (950, 999)),        # suffix form
        (None, 1000, None),
        ("bogus", 1000, None),
        ("bytes=-", 1000, None),
    ],
)
def test_range_header_parsing(header, size, expected):
    assert parse_byte_range(header, size) == expected


def test_whole_file_read_returns_200_and_full_length(origin):
    status, headers, body = fetch(origin)
    assert status == 200
    assert len(body) == origin.size
    assert headers["Accept-Ranges"] == "bytes"


def test_range_read_returns_206_with_correct_content_range(origin):
    status, headers, body = fetch(origin, "bytes=1000-1999")
    assert status == 206
    assert headers["Content-Range"] == f"bytes 1000-1999/{origin.size}"
    assert len(body) == 1000


def test_range_read_returns_the_bytes_actually_asked_for(origin):
    _, _, whole = fetch(origin)
    _, _, part = fetch(origin, "bytes=5000-5999")
    assert part == whole[5000:6000]


def test_log_records_the_start_byte_the_client_asked_for(origin):
    fetch(origin, "bytes=88244-")
    logged = [r for r in origin.requests("127.0.0.1") if r.range_header]
    assert logged[-1].start_byte == 88244


def test_logged_start_byte_converts_back_to_the_intended_time(origin, tmp_path):
    spec = PcmSpec()
    offset = data_offset(origin.file_path)
    wanted = 1.25
    fetch(origin, f"bytes={spec.seconds_to_byte(wanted, offset)}-")
    logged = [r for r in origin.requests("127.0.0.1") if r.range_header][-1]
    assert logged.start_seconds(spec.bytes_per_second, offset) == pytest.approx(wanted)


def test_whole_file_read_is_distinguishable_from_a_range_read(origin):
    # A seek produces a header re-read at byte 0 followed by the range request. Confusing
    # the two would attribute the seek to position zero.
    fetch(origin)
    fetch(origin, "bytes=4000-")
    records = origin.requests("127.0.0.1")
    assert records[-2].range_header is None
    assert records[-1].range_header == "bytes=4000-"


def test_stopping_twice_is_safe(tmp_path):
    wav = write_probe_wav(tmp_path / "p.wav", duration_s=0.2)
    o = Origin(wav, tmp_path / "log.jsonl").start()
    o.stop()
    o.stop()
