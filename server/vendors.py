"""MAC OUI lookup — only when prefix is in database."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANUF_FILE = ROOT / "data" / "oui-manuf.txt"

OUI_VENDORS: dict[str, str] = {
    "00:03:93": "Apple",
    "00:05:02": "Apple",
    "00:0a:27": "Apple",
    "00:0a:95": "Apple",
    "00:0d:93": "Apple",
    "00:10:fa": "Apple",
    "00:11:24": "Apple",
    "00:14:51": "Apple",
    "00:16:cb": "Apple",
    "00:16:78": "Intel",
    "00:17:f2": "Apple",
    "00:19:e3": "Apple",
    "00:1b:63": "Apple",
    "00:1c:42": "Apple",
    "00:1d:4f": "Apple",
    "00:1e:52": "Apple",
    "00:1e:c2": "Apple",
    "00:1f:5b": "Apple",
    "00:1f:f3": "Apple",
    "00:21:e9": "Apple",
    "00:22:41": "Apple",
    "00:23:12": "Cisco",
    "00:23:6c": "Apple",
    "00:23:df": "Apple",
    "00:24:36": "Apple",
    "00:24:d6": "Apple",
    "00:25:00": "Apple",
    "00:25:4b": "Apple",
    "00:25:bc": "Apple",
    "00:26:08": "Apple",
    "00:26:4a": "Apple",
    "00:26:bb": "Apple",
    "00:30:65": "Apple",
    "00:50:56": "VMware",
    "00:0c:29": "VMware",
    "00:1b:21": "Intel",
    "00:1e:68": "Apple",
    "00:21:5a": "HP",
    "00:22:64": "HP",
    "00:17:c8": "Kyocera",
    "00:20:6b": "Lexmark",
    "18:65:90": "Dell",
    "f8:bc:12": "Dell",
    "b8:27:eb": "Raspberry Pi",
    "dc:a6:32": "Raspberry Pi",
    "3c:52:82": "Hewlett Packard",
    "9c:93:4e": "Xerox",
    "00:24:81": "Samsung",
    "00:26:ab": "Samsung",
    "ac:84:c6": "TP-Link",
    "50:c7:bf": "TP-Link",
    "74:da:88": "TP-Link",
    "e4:8d:8c": "MikroTik",
    "fc:ec:da": "Ubiquiti",
    "30:68:93": "Espressif",
    "a8:47:4a": "Espressif",
    "4c:63:71": "Google",
    "b8:7b:c5": "Samsung",
    "20:9b:e6": "Samsung",
    "dc:7f:cc": "Cisco",
    "0c:ef:15": "Amazon",
}

_loaded_manuf: dict[str, str] | None = None
_mac_lookup = None


def _oui_prefix(mac: str) -> str | None:
    parts = re.split(r"[-:]", mac.strip().lower())
    if len(parts) < 3:
        return None
    try:
        return ":".join(f"{int(p, 16):02x}" for p in parts[:3])
    except ValueError:
        return None


def _load_manuf_file() -> dict[str, str]:
    global _loaded_manuf
    if _loaded_manuf is not None:
        return _loaded_manuf
    extra: dict[str, str] = {}
    if MANUF_FILE.is_file():
        for line in MANUF_FILE.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) >= 3:
                prefix = parts[1].strip().lower()[:8]
                vendor = parts[2].strip()
                if prefix and vendor:
                    extra[prefix] = vendor
    _loaded_manuf = {**OUI_VENDORS, **extra}
    return _loaded_manuf


def _lookup_mac_package(mac: str) -> str | None:
    global _mac_lookup
    try:
        from mac_vendor_lookup import MacLookup

        if _mac_lookup is None:
            _mac_lookup = MacLookup()
        return _mac_lookup.lookup(mac)
    except Exception:
        return None


def guess_vendor(mac: str | None) -> str | None:
    if not mac:
        return None
    prefix = _oui_prefix(mac)
    if not prefix:
        return None
    db = _load_manuf_file()
    if prefix in db:
        return db[prefix]
    parts = re.split(r"[-:]", mac.strip().lower())
    if len(parts) == 6:
        full = ":".join(f"{int(p, 16):02x}" for p in parts)
        return _lookup_mac_package(full)
    return None


def guess_device_type(
    hostname: str | None, vendor: str | None, mac: str | None
) -> str | None:
    """Only when hostname or known vendor clearly states it."""
    del mac
    h = (hostname or "").lower()
    v = (vendor or "").lower()
    if not h and not v:
        return None
    if any(x in h for x in ("printer", "print", "mfp", "copier")):
        return "printer"
    if any(x in v for x in ("xerox", "lexmark", "kyocera", "hewlett packard", "hp")):
        return "printer"
    if any(x in h for x in ("iphone", "ipad", "android")):
        return "phone"
    if any(x in h for x in ("router", "gateway", "modem")):
        return "router"
    if any(x in v for x in ("cisco", "ubiquiti", "mikrotik", "tp-link")):
        return "network"
    return None
