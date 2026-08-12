"""Byte offset has to map to time exactly, or every seek reading built on it is wrong."""

from __future__ import annotations

import struct
import wave

import pytest

from spike.harness.content import PcmSpec, data_offset, write_probe_wav


@pytest.fixture
def wav(tmp_path):
    return write_probe_wav(tmp_path / "probe.wav", duration_s=3.0)


def test_spec_bytes_per_second_matches_cd_stereo():
    assert PcmSpec().bytes_per_second == 176400


def test_byte_and_time_round_trip_on_the_sample_grid(wav):
    spec, offset = PcmSpec(), data_offset(wav)
    for seconds in (0.0, 0.5, 1.0, 2.5):
        byte = spec.seconds_to_byte(seconds, offset)
        assert spec.byte_to_seconds(byte, offset) == pytest.approx(seconds, abs=1e-9)


def test_a_time_off_the_sample_grid_lands_within_one_frame(wav):
    # 2.999 s is 132255.9 frames at 44.1 kHz, so it has no exact representation. The
    # round trip should lose less than a frame and never silently drift further.
    spec, offset = PcmSpec(), data_offset(wav)
    byte = spec.seconds_to_byte(2.999, offset)
    assert spec.byte_to_seconds(byte, offset) == pytest.approx(2.999, abs=1 / 44100)


def test_every_offset_lands_on_a_frame_boundary(wav):
    # A mid-frame offset would hand the receiver half a sample and swap the channels for
    # the rest of the stream.
    spec, offset = PcmSpec(), data_offset(wav)
    for seconds in (0.0, 0.3333, 1.7, 2.999):
        byte = spec.seconds_to_byte(seconds, offset)
        assert (byte - offset) % spec.frame_bytes == 0


def test_data_offset_points_at_the_first_frame_not_a_guessed_44(wav):
    offset = data_offset(wav)
    assert PcmSpec().byte_to_seconds(offset, offset) == 0.0
    with open(wav, "rb") as f:
        f.seek(offset - 8)
        assert f.read(4) == b"data"


def test_data_offset_survives_an_extra_chunk_before_the_data(tmp_path):
    # A writer may emit LIST or fact chunks first. Assuming 44 would shift every reading.
    source = write_probe_wav(tmp_path / "plain.wav", duration_s=0.2)
    raw = source.read_bytes()
    split = raw.index(b"data")
    extra = b"LIST" + struct.pack("<I", 10) + b"INFOhello\x00"
    padded = tmp_path / "padded.wav"
    padded.write_bytes(raw[:split] + extra + raw[split:])
    assert data_offset(padded) == data_offset(source) + len(extra)


def test_duration_and_format_are_what_the_probe_assumes(wav):
    with wave.open(str(wav)) as w:
        assert (w.getframerate(), w.getnchannels(), w.getsampwidth()) == (44100, 2, 2)
        assert w.getnframes() == 44100 * 3


def test_a_click_marks_every_whole_second(wav):
    spec, offset = PcmSpec(), data_offset(wav)
    raw = wav.read_bytes()[offset:]

    def peak_near(seconds):
        start = round(seconds * spec.sample_rate) * 4
        window = raw[start : start + 4 * int(spec.sample_rate * 0.002)]
        samples = struct.unpack(f"<{len(window) // 2}h", window)
        return max(abs(s) for s in samples)

    for second in (0, 1, 2):
        assert peak_near(second) > peak_near(second + 0.5) * 2


def test_rejects_a_file_that_is_not_wav(tmp_path):
    bad = tmp_path / "not.wav"
    bad.write_bytes(b"this is not a riff file at all")
    with pytest.raises(ValueError, match="not a RIFF/WAVE"):
        data_offset(bad)
