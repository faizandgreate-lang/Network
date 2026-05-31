"""Fetch real DNS/domain logs when Pi-hole or AdGuard is configured — no invented sites."""
from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter, defaultdict

from network_util import get_default_gateway, get_lan_ip

_SKIP_DOMAIN = re.compile(
    r"^(localhost|local|lan|home|arpa|in-addr\.arpa|ip6\.arpa|"
    r"([\w-]+\.)?localdomain|setup\.lan|\.)$",
    re.I,
)
_SKIP_SUFFIX = (".local", ".lan", ".home.arpa", ".internal")


def _http_get_json(url: str, headers: dict | None = None, timeout: float = 8.0) -> object | None:
    req = urllib.request.Request(url, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8", errors="replace"))
    except (urllib.error.URLError, OSError, json.JSONDecodeError, ValueError):
        return None


def _normalize_client(raw: str) -> str | None:
    if not raw:
        return None
    s = str(raw).strip().lower()
    if s in ("", "unknown", "na", "n/a", "0.0.0.0"):
        return None
    if "#" in s:
        s = s.split("#", 1)[0]
    if ":" in s and "." not in s.split(":")[0]:
        return None
    m = re.match(r"^(\d{1,3}(?:\.\d{1,3}){3})", s)
    if m:
        return m.group(1)
    return None


def _clean_domain(domain: str) -> str | None:
    if not domain:
        return None
    d = domain.strip().rstrip(".").lower()
    if not d or _SKIP_DOMAIN.match(d):
        return None
    if any(d.endswith(s) for s in _SKIP_SUFFIX):
        return None
    if d in ("pi.hole", "pi-hole", "doubleclick.net"):
        return None
    return d


def _format_top(counter: Counter, limit: int = 8) -> str | None:
    if not counter:
        return None
    parts = [f"{dom} ({n})" for dom, n in counter.most_common(limit)]
    return ", ".join(parts)


def fetch_pihole_domains(limit_queries: int = 800) -> tuple[dict[str, Counter], str | None]:
    """Returns {client_ip: Counter(domain)} and error message if any."""
    host = os.environ.get("PIHOLE_HOST", "").strip().rstrip("/")
    if not host:
        gw = get_default_gateway()
        if gw:
            host = f"http://{gw}"
    token = os.environ.get("PIHOLE_API_KEY", os.environ.get("PIHOLE_TOKEN", "")).strip()
    if not host:
        return {}, "PIHOLE_HOST not set (e.g. http://192.168.1.1)"

    q = urllib.parse.urlencode(
        {"getAllQueries": str(limit_queries), "auth": token} if token else {"getAllQueries": str(limit_queries)}
    )
    url = f"{host}/admin/api.php?{q}"
    data = _http_get_json(url)
    if data is None:
        return {}, f"Could not reach Pi-hole at {host}"

    queries = data.get("queries") if isinstance(data, dict) else None
    if not queries:
        return {}, "Pi-hole returned no queries (enable query logging)"

    by_ip: dict[str, Counter] = defaultdict(Counter)
    for row in queries:
        if not isinstance(row, (list, tuple)) or len(row) < 4:
            continue
        domain = _clean_domain(str(row[2]))
        client = _normalize_client(str(row[3]))
        if domain and client:
            by_ip[client][domain] += 1

    if not by_ip:
        return {}, "Pi-hole queries had no client IPs matched"
    return dict(by_ip), None


def fetch_adguard_domains(limit: int = 500) -> tuple[dict[str, Counter], str | None]:
    base = os.environ.get("ADGUARD_URL", "").strip().rstrip("/")
    if not base:
        return {}, None

    user = os.environ.get("ADGUARD_USER", "").strip()
    password = os.environ.get("ADGUARD_PASSWORD", "").strip()
    headers: dict[str, str] = {}
    if user or password:
        import base64

        cred = base64.b64encode(f"{user}:{password}".encode()).decode()
        headers["Authorization"] = f"Basic {cred}"

    url = f"{base}/control/querylog?limit={limit}&search="
    data = _http_get_json(url, headers=headers)
    if data is None:
        return {}, f"Could not reach AdGuard at {base}"

    rows = data.get("data") if isinstance(data, dict) else None
    if not rows:
        return {}, "AdGuard returned no query log rows"

    by_ip: dict[str, Counter] = defaultdict(Counter)
    for row in rows:
        if not isinstance(row, dict):
            continue
        domain = _clean_domain(str(row.get("domain") or row.get("host") or ""))
        client = _normalize_client(str(row.get("client") or row.get("client_ip") or ""))
        if domain and client:
            by_ip[client][domain] += 1

    if not by_ip:
        return {}, "AdGuard log had no usable client IPs"
    return dict(by_ip), None


def fetch_dns_by_client() -> tuple[dict[str, Counter], str, list[str]]:
    """
    Try configured DNS sources. Returns (ip->domain counts, source label, try log).
    """
    tries: list[str] = []
    merged: dict[str, Counter] = defaultdict(Counter)
    source = ""

    if os.environ.get("PIHOLE_HOST") or os.environ.get("PIHOLE_API_KEY") or os.environ.get("PIHOLE_TOKEN"):
        data, err = fetch_pihole_domains()
        if data:
            for ip, ctr in data.items():
                merged[ip].update(ctr)
            source = "pihole"
            tries.append(f"Pi-hole: {len(data)} client(s)")
        else:
            tries.append(f"Pi-hole: {err or 'failed'}")
    else:
        data, err = fetch_pihole_domains()
        if data:
            for ip, ctr in data.items():
                merged[ip].update(ctr)
            source = "pihole"
            tries.append(f"Pi-hole (gateway): {len(data)} client(s)")
        elif err and "not set" not in (err or "").lower():
            tries.append(f"Pi-hole (gateway): {err}")

    ag_data, ag_err = fetch_adguard_domains()
    if ag_data:
        for ip, ctr in ag_data.items():
            merged[ip].update(ctr)
        source = source + "+adguard" if source else "adguard"
        tries.append(f"AdGuard: {len(ag_data)} client(s)")
    elif os.environ.get("ADGUARD_URL") and ag_err:
        tries.append(f"AdGuard: {ag_err}")

    if not merged:
        return {}, "", tries

    return dict(merged), source.strip("+") or "dns", tries


def merge_dns_into_devices(devices: list) -> dict:
    """Attach top_domains + dns_source on each device from real DNS logs only."""
    by_ip, source, tries = fetch_dns_by_client()
    matched = 0
    for d in devices:
        ip = getattr(d, "ip", None) or d.get("ip")
        ctr = by_ip.get(ip) if ip else None
        top = _format_top(ctr) if ctr else None
        setattr(d, "top_domains", top)
        setattr(d, "dns_source", source if top else None)
        if top:
            matched += 1

    me = get_lan_ip()
    if me and me in by_ip and not any(getattr(x, "ip", None) == me for x in devices):
        tries.append(f"This PC ({me}) has DNS log entries but was already in scan")

    return {
        "ok": bool(by_ip),
        "source": source or None,
        "clients_in_log": len(by_ip),
        "devices_matched": matched,
        "tries": tries,
        "hint": (
            "Domains come from Pi-hole/AdGuard query logs on your network, "
            "not from LAN ping. HTTPS hides page content; only DNS names appear."
        ),
    }


def dns_status_for_api() -> dict:
    configured = []
    if os.environ.get("PIHOLE_HOST") or os.environ.get("PIHOLE_API_KEY"):
        configured.append("Pi-hole")
    elif get_default_gateway():
        configured.append("Pi-hole (auto-try gateway)")
    if os.environ.get("ADGUARD_URL"):
        configured.append("AdGuard Home")
    return {
        "configured": configured,
        "pihole_host": os.environ.get("PIHOLE_HOST") or (f"http://{get_default_gateway()}" if get_default_gateway() else None),
        "adguard_url": os.environ.get("ADGUARD_URL") or None,
        "note": "",
    }
