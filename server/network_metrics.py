"""Measured network facts from this PC only — no guessed speeds or browsing data."""
from __future__ import annotations

import platform
import re
import subprocess
import time
from datetime import datetime, timezone

from network_util import get_default_gateway

_cache: dict | None = None
_cache_at: float = 0.0
_TTL_SEC = 120.0


def _parse_ping_ms(output: str) -> int | None:
    m = re.search(r"time[=<]\s*(\d+(?:\.\d+)?)\s*ms", output, re.I)
    if m:
        return int(round(float(m.group(1))))
    m = re.search(r"(\d+(?:\.\d+)?)\s*ms", output)
    if m:
        return int(round(float(m.group(1))))
    return None


def ping_rtt_ms(ip: str, timeout_ms: int = 1500) -> int | None:
    """Round-trip time from this machine to ip (milliseconds), or None if unreachable."""
    system = platform.system().lower()
    param = "-n" if system == "windows" else "-c"
    wait = "-w" if system == "windows" else "-W"
    sec = max(1, (timeout_ms + 999) // 1000)
    try:
        r = subprocess.run(
            ["ping", param, "1", wait, str(sec), ip],
            capture_output=True,
            text=True,
            timeout=sec + 3,
        )
        if r.returncode != 0:
            return None
        return _parse_ping_ms(r.stdout or "")
    except (subprocess.SubprocessError, OSError):
        return None


def refresh_network_measurements() -> dict:
    global _cache, _cache_at
    gw = get_default_gateway()
    gateway_ms = ping_rtt_ms(gw) if gw else None
    internet_ms = ping_rtt_ms("1.1.1.1")
    if internet_ms is None:
        internet_ms = ping_rtt_ms("8.8.8.8")

    _cache = {
        "gateway_ip": gw,
        "gateway_ms": gateway_ms,
        "internet_ms": internet_ms,
        "measured_at": datetime.now(timezone.utc).isoformat(),
        "source": "ping from this PC",
    }
    _cache_at = time.monotonic()
    return _cache


def get_network_measurements(force: bool = False) -> dict:
    global _cache, _cache_at
    if force or _cache is None or (time.monotonic() - _cache_at) > _TTL_SEC:
        return refresh_network_measurements()
    return _cache
