"""Range-capable HTTP origin that records where a receiver starts reading.

Pull-side receivers fetch a URL instead of being handed a timestamped stream. That makes
the origin the only place their real behaviour is visible: the byte range a receiver asks
for after a seek is the position it actually chose, which is not always the position its
control API reports.
"""

from __future__ import annotations

import json
import re
import socketserver
import threading
import time
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler
from pathlib import Path

_RANGE = re.compile(r"bytes=(\d*)-(\d*)")


def parse_byte_range(header: str | None, size: int) -> tuple[int, int] | None:
    """Resolve a Range header to an inclusive byte span, or None for a whole-file read.

    Only the single-span form is handled. Multi-range replies would need a multipart body
    and no audio receiver has been seen asking for one.
    """
    if not header:
        return None
    match = _RANGE.match(header.strip())
    if not match:
        return None
    start_text, end_text = match.group(1), match.group(2)
    if not start_text and not end_text:
        return None
    if not start_text:  # suffix form: the last N bytes
        length = int(end_text)
        return max(0, size - length), size - 1
    start = int(start_text)
    end = int(end_text) if end_text else size - 1
    return start, min(end, size - 1)


@dataclass(frozen=True)
class OriginRequest:
    at_s: float
    method: str
    client: str
    path: str
    range_header: str | None
    start_byte: int | None

    def start_seconds(self, bytes_per_second: int, data_offset: int) -> float | None:
        if self.start_byte is None:
            return None
        return (self.start_byte - data_offset) / bytes_per_second


class Origin:
    """Serves one file over HTTP and appends a JSON line per request."""

    def __init__(self, file_path: str | Path, log_path: str | Path, port: int = 0):
        self.file_path = Path(file_path)
        self.log_path = Path(log_path)
        self.size = self.file_path.stat().st_size
        self._requested_port = port
        self._server: socketserver.ThreadingTCPServer | None = None
        self._thread: threading.Thread | None = None
        self._started_at = 0.0

    @property
    def port(self) -> int:
        if self._server is None:
            raise RuntimeError("origin is not running")
        return self._server.server_address[1]

    def url_for(self, host: str) -> str:
        return f"http://{host}:{self.port}/{self.file_path.name}"

    def start(self) -> Origin:
        origin = self

        class Handler(BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.1"

            def log_message(self, *args):
                pass  # the JSONL log is the record; stderr noise hides it

            def _record(self, start_byte: int | None):
                origin._append(
                    OriginRequest(
                        at_s=round(time.time() - origin._started_at, 3),
                        method=self.command,
                        client=self.client_address[0],
                        path=self.path,
                        range_header=self.headers.get("Range"),
                        start_byte=start_byte,
                    )
                )

            def do_HEAD(self):
                self._record(None)
                self.send_response(200)
                self._common_headers(origin.size)
                self.end_headers()

            def do_GET(self):
                span = parse_byte_range(self.headers.get("Range"), origin.size)
                if span is None:
                    start, end = 0, origin.size - 1
                    self._record(0)
                    self.send_response(200)
                    self._common_headers(origin.size)
                else:
                    start, end = span
                    self._record(start)
                    self.send_response(206)
                    self.send_header("Content-Range", f"bytes {start}-{end}/{origin.size}")
                    self._common_headers(end - start + 1)
                self.end_headers()
                self._send_span(start, end)

            def _common_headers(self, length: int):
                self.send_header("Content-Type", "audio/wav")
                self.send_header("Content-Length", str(length))
                self.send_header("Accept-Ranges", "bytes")

            def _send_span(self, start: int, end: int):
                remaining = end - start + 1
                try:
                    with open(origin.file_path, "rb") as f:
                        f.seek(start)
                        while remaining > 0:
                            chunk = f.read(min(65536, remaining))
                            if not chunk:
                                break
                            self.wfile.write(chunk)
                            remaining -= len(chunk)
                except (BrokenPipeError, ConnectionResetError):
                    # A receiver that seeks drops the old connection mid-body. That is the
                    # normal path here, not an error, so it is recorded rather than raised.
                    pass

        class Server(socketserver.ThreadingTCPServer):
            allow_reuse_address = True
            daemon_threads = True

        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self.log_path.write_text("")
        self._started_at = time.time()
        self._server = Server(("0.0.0.0", self._requested_port), Handler)
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()
        return self

    def stop(self) -> None:
        if self._server is not None:
            self._server.shutdown()
            self._server.server_close()
            self._server = None

    def __enter__(self) -> Origin:
        return self.start()

    def __exit__(self, *exc) -> None:
        self.stop()

    def _append(self, request: OriginRequest) -> None:
        with open(self.log_path, "a") as f:
            f.write(json.dumps(request.__dict__) + "\n")

    def requests(self, client: str | None = None) -> list[OriginRequest]:
        if not self.log_path.exists():
            return []
        out = []
        for line in self.log_path.read_text().splitlines():
            if not line.strip():
                continue
            record = OriginRequest(**json.loads(line))
            if client is None or record.client == client:
                out.append(record)
        return out
