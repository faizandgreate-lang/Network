"""Derived device facts from stored scan rows only."""
from __future__ import annotations

import hashlib
from datetime import datetime, timezone


def _parse_iso(ts: str | None) -> datetime | None:
    if not ts:
        return None
    try:
        s = ts.replace("Z", "+00:00")
        return datetime.fromisoformat(s)
    except ValueError:
        return None


def device_display_name(d: dict) -> str | None:
    for key in ("it_label", "hostname", "vendor"):
        v = d.get(key)
        if v and str(v).strip():
            return str(v).strip()
    return d.get("ip")


def session_duration_text(d: dict) -> str | None:
    first = _parse_iso(d.get("first_seen"))
    last = _parse_iso(d.get("last_seen"))
    if not first or not last:
        return None
    if last < first:
        return None
    delta = last - first
    secs = int(delta.total_seconds())
    if secs < 60:
        return f"{secs} seconds (first → last seen in our scans)"
    if secs < 3600:
        return f"{secs // 60} minutes (first → last seen in our scans)"
    if secs < 86400:
        return f"{secs // 3600} hours (first → last seen in our scans)"
    days = secs // 86400
    return f"{days} day(s) (first → last seen in our scans)"


def device_fingerprint(d: dict) -> str | None:
    parts = [
        d.get("mac") or "",
        d.get("vendor") or "",
        d.get("hostname") or "",
        d.get("services") or "",
        d.get("device_type") or "",
    ]
    raw = "|".join(str(p).lower().strip() for p in parts)
    if not raw.replace("|", "").strip():
        return None
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def enrich_device_row(d: dict) -> dict:
    """Attach computed fields for API/UI — no invented measurements."""
    out = dict(d)
    out["device_name"] = device_display_name(d)
    out["session_duration"] = session_duration_text(d)
    out["device_fingerprint"] = device_fingerprint(d)
    td = d.get("top_domains")
    out["top_domains_display"] = td if td else None
    if d.get("dns_source") and td:
        out["frequent_sites_note"] = f"From {d.get('dns_source')} DNS log (domain names only)"
    else:
        out["frequent_sites_note"] = None
    return out
