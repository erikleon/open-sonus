"""Minimal Sonos UPnP client.

Deliberately small. Full Sonos control belongs in a driver built on SoCo; this exists so
the harness can drive an endpoint during a control-authority probe without taking a
dependency the harness itself does not need.
"""

from __future__ import annotations

import http.client
import re
import time
from dataclasses import dataclass

CONTROL_PORT = 1400

SERVICES = {
    "AVTransport": (
        "/MediaRenderer/AVTransport/Control",
        "urn:schemas-upnp-org:service:AVTransport:1",
    ),
    "RenderingControl": (
        "/MediaRenderer/RenderingControl/Control",
        "urn:schemas-upnp-org:service:RenderingControl:1",
    ),
}

_TAG = re.compile(r"<(\w+)>(.*?)</\1>", re.S)
_FAULT_CODE = re.compile(r"<errorCode>(\d+)</errorCode>")


class SoapFault(Exception):
    def __init__(self, action: str, code: str):
        super().__init__(f"{action} refused by device with UPnP error {code}")
        self.action = action
        self.code = code


@dataclass(frozen=True)
class SoapResult:
    values: dict[str, str]
    elapsed_ms: float

    def get(self, key: str, default: str | None = None) -> str | None:
        return self.values.get(key, default)


def call(
    host: str,
    service: str,
    action: str,
    args: dict[str, object] | None = None,
    timeout: float = 6.0,
) -> SoapResult:
    path, urn = SERVICES[service]
    body = "".join(f"<{k}>{v}</{k}>" for k, v in (args or {}).items())
    envelope = (
        '<?xml version="1.0"?>'
        '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" '
        's:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body>'
        f'<u:{action} xmlns:u="{urn}">{body}</u:{action}>'
        "</s:Body></s:Envelope>"
    )
    conn = http.client.HTTPConnection(host, CONTROL_PORT, timeout=timeout)
    started = time.perf_counter()
    try:
        conn.request(
            "POST",
            path,
            envelope.encode(),
            {
                "Content-Type": 'text/xml; charset="utf-8"',
                "SOAPACTION": f'"{urn}#{action}"',
            },
        )
        response = conn.getresponse()
        payload = response.read().decode("utf-8", "replace")
        elapsed_ms = (time.perf_counter() - started) * 1000
    finally:
        conn.close()

    if response.status != 200:
        fault = _FAULT_CODE.search(payload)
        raise SoapFault(action, fault.group(1) if fault else str(response.status))

    values = {m.group(1): m.group(2) for m in _TAG.finditer(payload)}
    return SoapResult(values=values, elapsed_ms=elapsed_ms)


def transport(host: str, action: str, **args) -> SoapResult:
    return call(host, "AVTransport", action, {"InstanceID": 0, **args})


def rendering(host: str, action: str, **args) -> SoapResult:
    return call(host, "RenderingControl", action, {"InstanceID": 0, "Channel": "Master", **args})


def format_rel_time(seconds: float) -> str:
    """Render a seek target as H:MM:SS.mmm.

    The fraction is kept on purpose. A receiver that cannot honour it should say so, and
    finding out that it silently discards it instead is the point of the probe.
    """
    whole = int(seconds)
    ms = round((seconds - whole) * 1000)
    h, rem = divmod(whole, 3600)
    m, s = divmod(rem, 60)
    base = f"{h:d}:{m:02d}:{s:02d}"
    return f"{base}.{ms:03d}" if ms else base
