"""Constant-rate PCM test content.

The control-authority probe reads a receiver's seek resolution from the byte offset it
asks the origin for. That inference only holds while byte offset maps to time without
ambiguity, so this content is uncompressed PCM at a fixed frame rate. A compressed
corpus breaks the mapping and cannot be used for the measurement.
"""

from __future__ import annotations

import math
import struct
import wave
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PcmSpec:
    sample_rate: int = 44100
    channels: int = 2
    sample_width: int = 2  # bytes per channel per frame

    @property
    def frame_bytes(self) -> int:
        return self.channels * self.sample_width

    @property
    def bytes_per_second(self) -> int:
        return self.sample_rate * self.frame_bytes

    def byte_to_seconds(self, offset: int, data_offset: int) -> float:
        return (offset - data_offset) / self.bytes_per_second

    def seconds_to_byte(self, seconds: float, data_offset: int) -> int:
        """Byte offset of the frame nearest that time.

        Snapped to a frame boundary, not to the nearest byte. An offset landing inside a
        frame would hand the receiver a half sample and swap the channels for the rest of
        the stream, which sounds like a fault in the endpoint rather than in the corpus.
        """
        frames = round(seconds * self.sample_rate)
        return data_offset + frames * self.frame_bytes


#: The corpus default. CD-rate stereo keeps the byte-to-time arithmetic in whole numbers
#: at every whole second, which makes an offset easy to check by hand against a log.
CD_STEREO = PcmSpec()


def data_offset(path: str | Path) -> int:
    """Byte offset of the first audio frame.

    Not a constant. A writer may emit LIST or fact chunks ahead of the data chunk, so
    assuming the canonical 44 shifts every later reading by whatever those chunks weigh.
    """
    with open(path, "rb") as f:
        riff = f.read(12)
        if len(riff) < 12 or riff[:4] != b"RIFF" or riff[8:12] != b"WAVE":
            raise ValueError(f"{path} is not a RIFF/WAVE file")
        while True:
            header = f.read(8)
            if len(header) < 8:
                raise ValueError(f"{path} has no data chunk")
            chunk_id, size = struct.unpack("<4sI", header)
            if chunk_id == b"data":
                return f.tell()
            f.seek(size + (size & 1), 1)  # chunks are word aligned


def write_probe_wav(
    path: str | Path,
    duration_s: float,
    spec: PcmSpec = CD_STEREO,
    tone_hz: float = 440.0,
    tone_level: float = 0.05,
    click_hz: float = 1800.0,
    click_level: float = 0.20,
    click_ms: float = 2.0,
) -> Path:
    """Write a quiet tone carrying a short click on every whole second.

    The clicks are acoustic markers with a sharp onset, so the same file still works once
    microphones reach the rig. The tone keeps the room from being silent, which matters
    because silence tells you nothing about whether a receiver is still pulling.
    """
    path = Path(path)
    total = int(duration_s * spec.sample_rate)
    click_frames = max(1, int(spec.sample_rate * click_ms / 1000.0))
    frames = bytearray()
    for n in range(total):
        t = n / spec.sample_rate
        value = tone_level * math.sin(2 * math.pi * tone_hz * t)
        phase = n % spec.sample_rate
        if phase < click_frames:
            decay = 1.0 - phase / click_frames
            value += click_level * math.sin(2 * math.pi * click_hz * t) * decay
        sample = int(max(-1.0, min(1.0, value)) * 32767)
        frames += struct.pack("<h", sample) * spec.channels

    with wave.open(str(path), "wb") as w:
        w.setnchannels(spec.channels)
        w.setsampwidth(spec.sample_width)
        w.setframerate(spec.sample_rate)
        w.writeframes(bytes(frames))
    return path
