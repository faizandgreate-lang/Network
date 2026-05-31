"""Detect Wi‑Fi + Ethernet (all active LAN interfaces)."""
from __future__ import annotations

import ipaddress
import os
import platform
import re
import socket
import subprocess
from dataclasses import dataclass


@dataclass
class NetInterface:
    device: str
    name: str
    link: str  # wifi | ethernet | other
    ip: str
    subnet: str
    netmask: str | None = None


def _mask_to_prefix(netmask: str) -> int:
    """Convert 0xffffff00 style or 255.255.255.0 to prefix length."""
    if netmask.startswith("0x"):
        n = int(netmask, 16)
        return bin(n).count("1")
    try:
        return ipaddress.ip_network(f"0.0.0.0/{netmask}", strict=False).prefixlen
    except ValueError:
        return 24


def _macos_port_map() -> dict[str, tuple[str, str]]:
    """device en0 -> (friendly name, link type)."""
    mapping: dict[str, tuple[str, str]] = {}
    try:
        out = subprocess.check_output(
            ["networksetup", "-listallhardwareports"],
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=5,
        )
        port_name = ""
        for line in out.splitlines():
            if line.startswith("Hardware Port:"):
                port_name = line.split(":", 1)[1].strip()
            elif line.startswith("Device:"):
                dev = line.split(":", 1)[1].strip()
                low = port_name.lower()
                if "wi-fi" in low or "wifi" in low or "airport" in low:
                    link = "wifi"
                elif "ethernet" in low or "lan" in low or "usb" in low:
                    link = "ethernet"
                elif "thunderbolt" in low:
                    link = "ethernet"
                else:
                    link = "other"
                mapping[dev] = (port_name or dev, link)
    except (subprocess.SubprocessError, OSError, FileNotFoundError):
        pass
    return mapping


def _parse_ifconfig_darwin() -> list[NetInterface]:
    port_map = _macos_port_map()
    try:
        out = subprocess.check_output(["ifconfig"], text=True, timeout=8)
    except (subprocess.SubprocessError, OSError):
        return []

    interfaces: list[NetInterface] = []
    current_dev: str | None = None
    for line in out.splitlines():
        if line and not line.startswith("\t") and not line.startswith(" "):
            m = re.match(r"^(\w+):", line)
            if m:
                current_dev = m.group(1)
            continue
        if not current_dev or current_dev == "lo0":
            continue
        im = re.search(
            r"inet\s+(\d+\.\d+\.\d+\.\d+)\s+(?:netmask\s+(\S+))?(?:\s+broadcast\s+(\S+))?",
            line,
        )
        if not im:
            continue
        ip = im.group(1)
        if ip.startswith("127."):
            continue
        mask = im.group(2) or "0xffffff00"
        prefix = _mask_to_prefix(mask)
        subnet = f"{ip}/{prefix}"
        friendly, link = port_map.get(current_dev, (current_dev, "other"))
        if current_dev.startswith("bridge") or current_dev.startswith("utun"):
            continue
        interfaces.append(
            NetInterface(
                device=current_dev,
                name=friendly,
                link=link,
                ip=ip,
                subnet=str(ipaddress.ip_network(subnet, strict=False)),
                netmask=mask,
            )
        )
    return interfaces


def _parse_ipconfig_windows() -> list[NetInterface]:
    try:
        out = subprocess.check_output(["ipconfig", "/all"], text=True, timeout=10)
    except (subprocess.SubprocessError, OSError):
        return []

    interfaces: list[NetInterface] = []
    adapter = "Ethernet"
    ip: str | None = None
    mask: str | None = None
    for line in out.splitlines():
        if "adapter" in line.lower() and ":" in line:
            if ip and mask:
                _flush_win(interfaces, adapter, ip, mask)
            adapter = line.split(":", 1)[0].strip()
            ip, mask = None, None
        if "IPv4 Address" in line or "IP Address" in line:
            m = re.search(r":\s*(\d+\.\d+\.\d+\.\d+)", line)
            if m and not m.group(1).startswith("127."):
                ip = m.group(1)
        if "Subnet Mask" in line:
            m = re.search(r":\s*(\d+\.\d+\.\d+\.\d+)", line)
            if m:
                mask = m.group(1)
    if ip and mask:
        _flush_win(interfaces, adapter, ip, mask)
    return interfaces


def _flush_win(
    interfaces: list[NetInterface],
    adapter: str,
    ip: str,
    mask: str,
) -> None:
    low = adapter.lower()
    if "wi-fi" in low or "wireless" in low or "wlan" in low:
        link = "wifi"
    elif "ethernet" in low or "lan" in low:
        link = "ethernet"
    else:
        link = "other"
    prefix = _mask_to_prefix(mask)
    subnet = str(ipaddress.ip_network(f"{ip}/{prefix}", strict=False))
    interfaces.append(
        NetInterface(
            device=adapter[:32],
            name=adapter,
            link=link,
            ip=ip,
            subnet=subnet,
            netmask=mask,
        )
    )


def _parse_ip_linux() -> list[NetInterface]:
    try:
        out = subprocess.check_output(["ip", "-4", "addr"], text=True, timeout=5)
    except (subprocess.SubprocessError, OSError):
        return []
    interfaces: list[NetInterface] = []
    dev = ""
    for line in out.splitlines():
        m = re.match(r"^\d+:\s+(\S+):", line)
        if m:
            dev = m.group(1).rstrip("@")
            continue
        im = re.search(r"inet\s+(\d+\.\d+\.\d+\.\d+)/(\d+)", line)
        if im and dev and dev != "lo":
            ip, prefix = im.group(1), int(im.group(2))
            if ip.startswith("127."):
                continue
            link = "wifi" if "wlan" in dev or "wl" in dev else (
                "ethernet" if dev.startswith("eth") or dev.startswith("enp") else "other"
            )
            subnet = str(ipaddress.ip_network(f"{ip}/{prefix}", strict=False))
            interfaces.append(
                NetInterface(
                    device=dev,
                    name=dev,
                    link=link,
                    ip=ip,
                    subnet=subnet,
                )
            )
    return interfaces


def list_active_interfaces() -> list[NetInterface]:
    """All IPv4 interfaces (Wi‑Fi + LAN + dock)."""
    system = platform.system().lower()
    if system == "darwin":
        raw = _parse_ifconfig_darwin()
    elif system == "windows":
        raw = _parse_ipconfig_windows()
    else:
        raw = _parse_ip_linux()

    seen_subnets: set[str] = set()
    result: list[NetInterface] = []
    for iface in raw:
        if iface.subnet in seen_subnets:
            continue
        seen_subnets.add(iface.subnet)
        result.append(iface)

    env = os.environ.get("OFFICE_SUBNET", "").strip()
    if env:
        for part in re.split(r"[\s,;]+", env):
            part = part.strip()
            if not part:
                continue
            try:
                net = str(ipaddress.ip_network(part, strict=False))
                if net not in seen_subnets:
                    seen_subnets.add(net)
                    result.append(
                        NetInterface(
                            device="manual",
                            name="Manual",
                            link="other",
                            ip="",
                            subnet=net,
                        )
                    )
            except ValueError:
                pass
    return result


def get_lan_ip() -> str | None:
    ifaces = list_active_interfaces()
    if not ifaces:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except OSError:
            return None
    wifi = next((i for i in ifaces if i.link == "wifi"), None)
    return (wifi or ifaces[0]).ip


def get_default_gateway() -> str | None:
    if platform.system().lower() == "darwin":
        try:
            out = subprocess.check_output(
                ["route", "-n", "get", "default"],
                stderr=subprocess.DEVNULL,
                text=True,
                timeout=3,
            )
            m = re.search(r"gateway:\s*(\d+\.\d+\.\d+\.\d+)", out)
            if m:
                return m.group(1)
        except (subprocess.SubprocessError, OSError):
            pass
    return None


def detect_subnet() -> str:
    """Comma-separated list of all subnets to scan."""
    ifaces = list_active_interfaces()
    if ifaces:
        return ",".join(i.subnet for i in ifaces)
    return "192.168.1.0/24"


def all_subnets() -> list[str]:
    env = os.environ.get("OFFICE_SUBNET", "").strip()
    if env and "," not in env and "/" in env:
        return [str(ipaddress.ip_network(env, strict=False))]
    if env:
        parts = []
        for p in re.split(r"[\s,;]+", env):
            p = p.strip()
            if p:
                parts.append(str(ipaddress.ip_network(p, strict=False)))
        if parts:
            return parts
    return [i.subnet for i in list_active_interfaces()] or ["192.168.1.0/24"]


def ip_in_subnet(ip: str, net: ipaddress.IPv4Network) -> bool:
    try:
        return ipaddress.ip_address(ip) in net
    except ValueError:
        return False


def get_local_wifi_signal() -> dict | None:
    """RSSI for this Mac’s Wi‑Fi link only — not remote clients."""
    if platform.system().lower() != "darwin":
        return None
    airport = (
        "/System/Library/PrivateFrameworks/Apple80211.framework/"
        "Versions/Current/Resources/airport"
    )
    try:
        out = subprocess.check_output([airport, "-I"], stderr=subprocess.DEVNULL, text=True, timeout=3)
    except (subprocess.SubprocessError, OSError, FileNotFoundError):
        return None
    ssid = rssi = channel = None
    for line in out.splitlines():
        line = line.strip()
        if line.startswith("SSID:"):
            ssid = line.split(":", 1)[1].strip()
        elif "agrCtlRSSI" in line:
            m = re.search(r"(-?\d+)", line)
            if m:
                rssi = int(m.group(1))
        elif line.startswith("channel:"):
            channel = line.split(":", 1)[1].strip()
    if rssi is None and ssid is None:
        return None
    return {
        "ssid": ssid,
        "rssi_dbm": rssi,
        "channel": channel,
        "note": "This Mac’s Wi‑Fi to the access point — not other devices on the LAN.",
    }


def subnet_display_summary() -> dict:
    ifaces = list_active_interfaces()
    return {
        "interfaces": [
            {
                "device": i.device,
                "name": i.name,
                "link": i.link,
                "ip": i.ip,
                "subnet": i.subnet,
            }
            for i in ifaces
        ],
        "subnets": [i.subnet for i in ifaces],
        "gateway": get_default_gateway(),
        "this_pc": get_lan_ip(),
    }
