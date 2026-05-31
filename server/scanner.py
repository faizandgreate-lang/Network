"""LAN device discovery — optimized for macOS office/home Wi‑Fi."""
from __future__ import annotations

import ipaddress
import os
import platform
import re
import shutil
import socket
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, timezone

from network_util import (
    NetInterface,
    all_subnets,
    detect_subnet,
    get_default_gateway,
    get_lan_ip,
    ip_in_subnet,
    list_active_interfaces,
)
from enrich import enrich_device_list, is_invalid_host_ip
from network_metrics import ping_rtt_ms

_cached_subnet: str | None = None
_last_scan_error: str | None = None


def default_subnet() -> str:
    global _cached_subnet
    if _cached_subnet is None:
        _cached_subnet = detect_subnet()
    return _cached_subnet


def refresh_subnet() -> str:
    global _cached_subnet
    _cached_subnet = detect_subnet()
    return _cached_subnet


def last_scan_error() -> str | None:
    return _last_scan_error


@dataclass
class Device:
    ip: str
    mac: str | None
    hostname: str | None
    status: str
    last_seen: str
    source: str
    vendor: str | None = None
    device_type: str | None = None
    subnet: str | None = None
    link: str | None = None  # wifi | ethernet | other
    interface_name: str | None = None
    services: str | None = None  # open ports, e.g. "http:80, https:443"
    notes: str | None = None
    latency_ms: int | None = None  # ping RTT from this PC during scan
    top_domains: str | None = None  # from Pi-hole/AdGuard DNS logs only
    dns_source: str | None = None

    @property
    def device_key(self) -> str:
        return f"{self.ip}|{self.subnet or 'default'}"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def ping_host(ip: str, timeout_ms: int = 800) -> bool:
    system = platform.system().lower()
    param = "-n" if system == "windows" else "-c"
    wait = "-w" if system == "windows" else "-W"
    sec = max(1, (timeout_ms + 999) // 1000)
    try:
        r = subprocess.run(
            ["ping", param, "1", wait, str(sec), ip],
            capture_output=True,
            timeout=sec + 2,
        )
        return r.returncode == 0
    except (subprocess.SubprocessError, OSError):
        return False


def read_arp_table() -> dict[str, str]:
    mapping: dict[str, str] = {}
    try:
        if platform.system().lower() == "darwin":
            out = subprocess.check_output(["arp", "-an"], text=True, timeout=8)
            for line in out.splitlines():
                m = re.search(
                    r"\((\d+\.\d+\.\d+\.\d+)\)\s+at\s+([0-9a-f:]+)",
                    line,
                    re.I,
                )
                if m:
                    mac = m.group(2).lower()
                    if mac != "(incomplete)" and len(mac) >= 11:
                        mapping[m.group(1)] = mac
        elif platform.system().lower() == "windows":
            out = subprocess.check_output(["arp", "-a"], text=True, timeout=8)
            for line in out.splitlines():
                m = re.search(
                    r"(\d+\.\d+\.\d+\.\d+)\s+([0-9a-f-]{17})",
                    line.replace("-", ":"),
                    re.I,
                )
                if m:
                    mapping[m.group(1)] = m.group(2).lower()
        else:
            out = subprocess.check_output(["ip", "neigh"], text=True, timeout=8)
            for line in out.splitlines():
                parts = line.split()
                if len(parts) >= 5 and parts[3] == "lladdr":
                    mapping[parts[0]] = parts[4].lower()
    except (subprocess.SubprocessError, OSError):
        pass
    return mapping


def resolve_hostname(ip: str) -> str | None:
    """Optional slow DNS lookup — off by default (set RESOLVE_NAMES=1)."""
    if os.environ.get("RESOLVE_NAMES", "0") != "1":
        return None
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
    try:
        name, _, _ = socket.gethostbyaddr(ip)
        if name:
            return name.rstrip(".")
    except OSError:
        pass
    return None


def _ping_many(ips: list[str], workers: int = 80) -> tuple[set[str], dict[str, int]]:
    alive: set[str] = set()
    rtt: dict[str, int] = {}
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(ping_rtt_ms, ip, 900): ip for ip in ips}
        for fut in as_completed(futures):
            ip = futures[fut]
            try:
                ms = fut.result()
                if ms is not None:
                    alive.add(ip)
                    rtt[ip] = ms
            except Exception:
                pass
    return alive, rtt


def scan_subnet(
    subnet: str | None = None,
    iface: NetInterface | None = None,
    max_hosts: int = 254,
) -> list[Device]:
    global _last_scan_error
    _last_scan_error = None
    net = ipaddress.ip_network(subnet or default_subnet(), strict=False)
    host_ips = [str(h) for h in list(net.hosts())[:max_hosts]]

    # Wake up ARP cache: gateway + this PC's subnet neighbors
    seeds: list[str] = []
    gw = get_default_gateway()
    if gw and gw in host_ips:
        seeds.append(gw)
    me = get_lan_ip()
    if me:
        seeds.append(me)
    parts = str(net.network_address).split(".")
    if len(parts) == 4:
        for last in (1, 254):
            seeds.append(f"{parts[0]}.{parts[1]}.{parts[2]}.{last}")

    for ip in dict.fromkeys(seeds):
        ping_host(ip, 1200)

    print(f"  Scanning {len(host_ips)} addresses on {net} (parallel ping)…")
    alive, rtt_map = _ping_many(host_ips)
    print(f"  Ping found {len(alive)} hosts, reading ARP table…")

    arp = read_arp_table()
    for ip, mac in arp.items():
        if ip_in_subnet(ip, net) and ip not in alive:
            alive.add(ip)

    if me:
        alive.add(me)

    devices: list[Device] = []
    for ip in sorted(alive, key=ipaddress.ip_address):
        if is_invalid_host_ip(ip):
            continue
        mac = arp.get(ip)
        source = "ping+arp" if ip in arp else "ping"
        if ip in arp and ip not in host_ips:
            source = "arp"
        devices.append(
            Device(
                ip=ip,
                mac=mac,
                hostname=None,
                status="online",
                last_seen=_now(),
                source=source,
                subnet=str(net),
                link=iface.link if iface else None,
                interface_name=iface.name if iface else None,
                latency_ms=rtt_map.get(ip),
            )
        )

    devices = enrich_device_list(devices, gateway=gw)

    label = f"{iface.name} [{iface.link}]" if iface else str(net)
    print(f"  [{label}] {len(devices)} devices")
    if not devices:
        _last_scan_error = (
            "No devices found. Check OFFICE_SUBNET matches your Wi‑Fi "
            f"(this PC is {me or 'unknown'}, gateway {gw or 'unknown'}). "
            "Try: export OFFICE_SUBNET=YOUR.RANGE.0/24"
        )
    return devices


def scan_with_nmap(
    subnets: list[str] | None = None,
    iface_by_subnet: dict[str, NetInterface] | None = None,
) -> list[Device]:
    global _last_scan_error
    targets = subnets or all_subnets()
    target_str = " ".join(targets)
    if not shutil.which("nmap"):
        return scan_all_interfaces()
    try:
        print(f"  Running nmap -sn on {target_str}…")
        out = subprocess.check_output(
            ["nmap", "-sn", "-n", *targets],
            stderr=subprocess.STDOUT,
            text=True,
            timeout=240,
        )
    except (subprocess.SubprocessError, OSError) as e:
        _last_scan_error = f"nmap failed: {e}"
        return scan_all_interfaces()

    arp = read_arp_table()
    iface_by_subnet = iface_by_subnet or {}
    devices: list[Device] = []
    current_ip: str | None = None
    hostname: str | None = None
    for line in out.splitlines():
        if line.startswith("Nmap scan report for"):
            rest = line.replace("Nmap scan report for", "").strip()
            if "(" in rest and ")" in rest:
                current_ip = rest.split("(")[1].split(")")[0]
                hostname = rest.split("(")[0].strip() or None
            else:
                current_ip = rest
                hostname = None
            if current_ip and not current_ip.endswith("."):
                iface = _iface_for_ip(current_ip, targets, iface_by_subnet)
                mac = arp.get(current_ip)
                if is_invalid_host_ip(current_ip):
                    continue
                devices.append(
                    Device(
                        ip=current_ip,
                        mac=mac,
                        hostname=hostname if hostname != current_ip else None,
                        status="online",
                        last_seen=_now(),
                        source="nmap",
                        subnet=iface.subnet if iface else _subnet_for_ip(current_ip, targets),
                        link=iface.link if iface else None,
                        interface_name=iface.name if iface else None,
                    )
                )
    gw = get_default_gateway()
    devices = enrich_device_list(devices, gateway=gw)
    print(f"  nmap total: {len(devices)} devices")
    return devices


def _subnet_for_ip(ip: str, subnets: list[str]) -> str | None:
    try:
        addr = ipaddress.ip_address(ip)
        for s in subnets:
            if addr in ipaddress.ip_network(s, strict=False):
                return s
    except ValueError:
        pass
    return None


def _iface_for_ip(
    ip: str,
    subnets: list[str],
    iface_by_subnet: dict[str, NetInterface],
) -> NetInterface | None:
    s = _subnet_for_ip(ip, subnets)
    return iface_by_subnet.get(s) if s else None


def scan_all_interfaces() -> list[Device]:
    """Scan every active Wi‑Fi + Ethernet subnet on this Mac/PC."""
    global _last_scan_error
    ifaces = list_active_interfaces()
    if not ifaces:
        return scan_subnet()

    merged: dict[str, Device] = {}
    print(f"  Active networks: {len(ifaces)} (Wi‑Fi + LAN)")
    for iface in ifaces:
        print(f"  --- {iface.name} ({iface.link}) → {iface.subnet} ---")
        batch = scan_subnet(iface.subnet, iface=iface)
        for d in batch:
            merged[d.device_key] = d

    devices = list(merged.values())
    print(f"  Combined total: {len(devices)} devices across all interfaces")
    if not devices:
        _last_scan_error = (
            "No devices on Wi‑Fi or LAN. Check cables/Wi‑Fi, or set "
            "OFFICE_SUBNET=192.168.1.0/24,10.0.0.0/24"
        )
    return devices


def run_best_scan(subnet: str | None = None) -> list[Device]:
    """Scan Wi‑Fi + Ethernet (+ all OFFICE_SUBNET entries)."""
    ifaces = list_active_interfaces()
    iface_map = {i.subnet: i for i in ifaces}
    subnets = all_subnets() if not subnet else [subnet]

    if os.environ.get("USE_NMAP", "auto") == "0":
        return scan_all_interfaces()

    if shutil.which("nmap") and os.environ.get("USE_NMAP", "auto") != "0":
        devices = scan_with_nmap(subnets, iface_map)
        if devices:
            return devices

    return scan_all_interfaces()
