"""Only add data we actually measured — no guessed labels."""
from __future__ import annotations

import os
import platform
import re
import socket
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

from vendors import guess_device_type, guess_vendor

PROBE_PORTS: list[tuple[int, str]] = [
    (80, "http"),
    (443, "https"),
    (22, "ssh"),
    (445, "smb"),
    (631, "ipp"),
    (9100, "printer"),
    (5000, "upnp"),
    (8080, "http-alt"),
]


def _resolve_enabled() -> bool:
    return os.environ.get("RESOLVE_NAMES", "1") != "0"


def _ports_enabled() -> bool:
    return os.environ.get("ENRICH_PORTS", "1") != "0"


def format_mac(mac: str | None) -> str | None:
    if not mac:
        return None
    parts = re.split(r"[-:]", mac.strip().lower())
    if len(parts) != 6:
        return None
    try:
        return ":".join(f"{int(p, 16):02x}" for p in parts)
    except ValueError:
        return None


def is_invalid_host_ip(ip: str) -> bool:
    if ip.endswith(".255") or ip.endswith(".0"):
        return True
    if ip in ("0.0.0.0", "255.255.255.255"):
        return True
    return False


def _resolve_darwin(ip: str) -> str | None:
    try:
        out = subprocess.check_output(
            ["dscacheutil", "-q", "host", "-a", "ip_address", ip],
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=2,
        )
        for line in out.splitlines():
            if line.strip().startswith("name:"):
                name = line.split(":", 1)[1].strip()
                if name and name != ip:
                    return name.rstrip(".")
    except (subprocess.SubprocessError, OSError):
        pass
    try:
        out = subprocess.check_output(
            ["host", ip],
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=2,
        )
        m = re.search(r"domain name pointer\s+(\S+)", out)
        if m:
            return m.group(1).rstrip(".")
    except (subprocess.SubprocessError, OSError, FileNotFoundError):
        pass
    return None


def resolve_one_hostname(ip: str) -> str | None:
    if platform.system().lower() == "darwin":
        name = _resolve_darwin(ip)
        if name:
            return name
    try:
        socket.setdefaulttimeout(1.5)
        name, _, _ = socket.gethostbyaddr(ip)
        if name and name != ip:
            return name.rstrip(".")
    except OSError:
        pass
    return None


def resolve_hostnames_batch(ips: list[str], workers: int = 48) -> dict[str, str]:
    if not _resolve_enabled():
        return {}
    names: dict[str, str] = {}
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(resolve_one_hostname, ip): ip for ip in ips}
        for fut in as_completed(futures):
            ip = futures[fut]
            try:
                n = fut.result()
                if n:
                    names[ip] = n
            except Exception:
                pass
    return names


def _port_open(ip: str, port: int, timeout: float) -> bool:
    try:
        with socket.create_connection((ip, port), timeout=timeout):
            return True
    except OSError:
        return False


def probe_one_device(ip: str) -> str:
    if not _ports_enabled():
        return ""
    timeout = float(os.environ.get("PORT_PROBE_TIMEOUT", "0.28"))
    found: list[str] = []
    for port, label in PROBE_PORTS:
        if _port_open(ip, port, timeout):
            found.append(f"{label}:{port}")
    return ", ".join(found)


def probe_ports_batch(ips: list[str], workers: int = 32) -> dict[str, str]:
    if not _ports_enabled():
        return {}
    out: dict[str, str] = {}
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(probe_one_device, ip): ip for ip in ips}
        for fut in as_completed(futures):
            ip = futures[fut]
            try:
                out[ip] = fut.result()
            except Exception:
                out[ip] = ""
    return out


def enrich_device_list(
    devices: list,
    gateway: str | None = None,
) -> list:
    """MAC normalize + measured DNS names + open TCP ports. No invented data."""
    del gateway
    valid = [d for d in devices if not is_invalid_host_ip(d.ip)]
    ips = [d.ip for d in valid]

    names = resolve_hostnames_batch(ips)
    ports = probe_ports_batch(ips)
    if names or any(ports.values()):
        print(f"  Measured extras: DNS names for {len(names)}, ports on {sum(1 for v in ports.values() if v)} device(s)…")

    enriched: list = []
    for d in valid:
        mac = format_mac(d.mac) or d.mac
        hostname = names.get(d.ip) or d.hostname
        vendor = guess_vendor(mac)
        dtype = guess_device_type(hostname, vendor, mac)
        svc = ports.get(d.ip) or None

        d.mac = mac
        d.hostname = hostname
        d.vendor = vendor
        d.device_type = dtype
        d.services = svc if svc else None
        if not d.notes:
            d.notes = d.source if d.source else None
        enriched.append(d)
    return enriched
