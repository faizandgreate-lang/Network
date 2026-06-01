"""LAN device control by IP — office/private networks only."""
from __future__ import annotations

import ipaddress
import platform
import re
import socket
import subprocess
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from enrich import probe_one_device
from network_metrics import ping_rtt_ms

_MAC_RE = re.compile(r"^([0-9a-f]{2}[:-]){5}[0-9a-f]{2}$", re.I)


def normalize_ip(ip: str) -> str:
    return str(ipaddress.ip_address(ip.strip()))


def is_allowed_control_ip(ip: str) -> bool:
    """Only RFC1918 / local LAN — no public internet targets."""
    try:
        addr = ipaddress.ip_address(ip.strip())
    except ValueError:
        return False
    if addr.is_loopback or addr.is_multicast or addr.is_link_local or addr.is_reserved:
        return False
    return addr.is_private


def validate_mac(mac: str | None) -> str | None:
    if not mac:
        return None
    m = mac.strip().lower().replace("-", ":")
    if not _MAC_RE.match(m):
        return None
    if m in ("ff:ff:ff:ff:ff:ff", "00:00:00:00:00:00"):
        return None
    return m


def send_wake_on_lan(mac: str) -> dict[str, Any]:
    mac_norm = validate_mac(mac)
    if not mac_norm:
        return {"ok": False, "error": "Valid MAC required (from scan or enter manually)."}
    try:
        mac_bytes = bytes.fromhex(mac_norm.replace(":", ""))
        if len(mac_bytes) != 6:
            return {"ok": False, "error": "Invalid MAC length."}
        packet = b"\xff" * 6 + mac_bytes * 16
        sent = 0
        for target in ("255.255.255.255", "<broadcast>"):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                    sock.settimeout(2.0)
                    sock.sendto(packet, (target, 9))
                    sent += 1
            except OSError:
                continue
        if not sent:
            return {"ok": False, "error": "Could not send Wake-on-LAN packet."}
        return {"ok": True, "mac": mac_norm, "message": "Wake-on-LAN magic packet sent."}
    except OSError as e:
        return {"ok": False, "error": str(e)}


def ping_device(ip: str) -> dict[str, Any]:
    if not is_allowed_control_ip(ip):
        return {"ok": False, "error": "Only private LAN IPs (192.168.x.x, 10.x.x.x, etc.) are allowed."}
    ms = ping_rtt_ms(ip, 1500)
    if ms is None:
        return {"ok": True, "ip": ip, "online": False, "latency_ms": None}
    return {"ok": True, "ip": ip, "online": True, "latency_ms": ms}


def probe_device_ports(ip: str) -> dict[str, Any]:
    if not is_allowed_control_ip(ip):
        return {"ok": False, "error": "Only private LAN IPs are allowed."}
    services = probe_one_device(ip)
    open_ports: list[dict[str, Any]] = []
    for part in (services or "").split(","):
        part = part.strip()
        if ":" in part:
            name, port_s = part.rsplit(":", 1)
            try:
                open_ports.append({"port": int(port_s), "name": name.strip()})
            except ValueError:
                pass
    return {
        "ok": True,
        "ip": ip,
        "open_ports": open_ports,
        "services": services or "",
    }


def http_device_request(
    ip: str,
    *,
    port: int = 80,
    method: str = "GET",
    path: str = "/",
    use_https: bool = False,
    timeout_sec: float = 5.0,
) -> dict[str, Any]:
    if not is_allowed_control_ip(ip):
        return {"ok": False, "error": "Only private LAN IPs are allowed."}
    if port < 1 or port > 65535:
        return {"ok": False, "error": "Invalid port."}
    method = (method or "GET").upper()
    if method not in ("GET", "HEAD", "POST"):
        return {"ok": False, "error": "Method must be GET, HEAD, or POST."}
    path = path or "/"
    if not path.startswith("/"):
        path = "/" + path
    scheme = "https" if use_https else "http"
    url = f"{scheme}://{ip}:{port}{path}"
    try:
        req = Request(url, method=method)
        with urlopen(req, timeout=timeout_sec) as resp:
            body = resp.read(2048) if method != "HEAD" else b""
            return {
                "ok": True,
                "url": url,
                "status": resp.status,
                "headers": dict(resp.headers),
                "body_preview": body.decode("utf-8", errors="replace")[:500],
            }
    except HTTPError as e:
        body = e.read(512).decode("utf-8", errors="replace") if e.fp else ""
        return {
            "ok": True,
            "url": url,
            "status": e.code,
            "error": e.reason,
            "body_preview": body[:500],
        }
    except URLError as e:
        return {"ok": False, "url": url, "error": str(e.reason)}
    except OSError as e:
        return {"ok": False, "url": url, "error": str(e)}


def open_links_for_device(ip: str, services: str | None = None) -> list[dict[str, str]]:
    """Quick-open links for browser / apps (client opens these)."""
    links = [
        {"id": "http", "label": "Web (HTTP)", "url": f"http://{ip}/"},
        {"id": "https", "label": "Web (HTTPS)", "url": f"https://{ip}/"},
        {"id": "http8080", "label": "Web :8080", "url": f"http://{ip}:8080/"},
    ]
    if platform.system().lower() == "darwin":
        links.append({"id": "ssh", "label": "SSH (Terminal)", "url": f"ssh://{ip}"})
    else:
        links.append({"id": "ssh", "label": "SSH", "url": f"ssh://{ip}"})
    links.append({"id": "rdp", "label": "Remote Desktop", "url": f"rdp://full%20address={ip}"})
    svc = (services or "").lower()
    if "https" in svc and not any(l["id"] == "https" for l in links):
        pass
    if ":22" in svc or "ssh" in svc:
        links.insert(0, {"id": "ssh", "label": "SSH", "url": f"ssh://{ip}"})
    if ":631" in svc or "ipp" in svc:
        links.append({"id": "printer", "label": "Printer (IPP)", "url": f"http://{ip}:631/"})
    return links
