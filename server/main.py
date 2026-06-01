#!/usr/bin/env python3
"""Office LAN monitor — company-owned devices on your network."""
from __future__ import annotations

import csv
import io
import os
import socket
import sqlite3
import sys
import threading
import time
import webbrowser
from contextlib import asynccontextmanager
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from datetime import datetime, timezone

from network_util import (
    get_default_gateway,
    get_lan_ip,
    get_local_wifi_signal,
    list_active_interfaces,
    subnet_display_summary,
)
from install_assets import install_web_assets
from downloads import (
    download_full_mac_zip,
    download_full_windows_zip,
    download_mac_app_zip,
    download_start_bat,
    download_start_command,
)
from dns_sources import dns_status_for_api, merge_dns_into_devices
from device_meta import enrich_device_row
from network_metrics import get_network_measurements, refresh_network_measurements
from topology import build_topology
from device_control import (
    http_device_request,
    is_allowed_control_ip,
    normalize_ip,
    open_links_for_device,
    ping_device,
    probe_device_ports,
    send_wake_on_lan,
)
from scanner import (
    Device,
    default_subnet,
    last_scan_error,
    refresh_subnet,
    run_best_scan,
)

ROOT = Path(__file__).resolve().parent.parent
WEB = ROOT / "web"
DB = ROOT / "data" / "devices.db"

_scan_lock = threading.Lock()
_db_lock = threading.Lock()
_scanning = False
_auto_stop = threading.Event()
_last_dns_merge: dict | None = None

# Mac often uses 5000 for AirPlay — default to 5080
DEFAULT_PORT = 5080
PORT_CANDIDATES = (5080, 5081, 5082, 8760, 5001, 5002, 9090)


def get_runtime_port() -> int:
    return int(os.environ.get("PORT", str(DEFAULT_PORT)))


def port_available(port: int, host: str = "0.0.0.0") -> bool:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((host, port))
        return True
    except OSError:
        return False


def pick_port(preferred: int | None = None) -> int:
    start = preferred if preferred is not None else get_runtime_port()
    tried: set[int] = set()
    for p in (start, *PORT_CANDIDATES):
        if p in tried:
            continue
        tried.add(p)
        if port_available(p):
            return p
    raise SystemExit("ERROR: No free port (tried 5080–5082, 8760, 5001–5002). Quit other apps.")


@asynccontextmanager
async def lifespan(application: FastAPI):
    try:
        assets = install_web_assets()
        print(f"   Logo:    {assets['logo']}  |  mono: {assets.get('logo_mono', '—')}")
        print(f"   Photo:   {assets['creator']}  |  mono: {assets.get('creator_mono', '—')}")
    except Exception as exc:
        print(f"   Assets:  skip ({exc})")
    init_db()
    refresh_subnet()
    threading.Thread(target=_startup_scan, daemon=True).start()
    if int(os.environ.get("AUTO_SCAN_MINUTES", "0")) > 0:
        threading.Thread(target=_delayed_auto_scan, daemon=True).start()
    yield
    _auto_stop.set()


def _db_connect() -> sqlite3.Connection:
    con = sqlite3.connect(str(DB), timeout=60.0, check_same_thread=False)
    con.execute("PRAGMA journal_mode=WAL")
    con.execute("PRAGMA synchronous=NORMAL")
    con.execute("PRAGMA busy_timeout=60000")
    return con


app = FastAPI(title="Network Monitor", lifespan=lifespan)


def init_db() -> None:
    DB.parent.mkdir(parents=True, exist_ok=True)
    with _db_connect() as con:
        con.executescript(
            """
            CREATE TABLE IF NOT EXISTS devices (
                device_key TEXT PRIMARY KEY,
                ip TEXT NOT NULL,
                mac TEXT,
                hostname TEXT,
                status TEXT,
                last_seen TEXT,
                source TEXT,
                vendor TEXT,
                device_type TEXT,
                it_label TEXT,
                first_seen TEXT,
                scan_count INTEGER DEFAULT 0,
                subnet TEXT,
                link TEXT,
                interface_name TEXT,
                services TEXT,
                notes TEXT,
                latency_ms INTEGER,
                top_domains TEXT,
                dns_source TEXT
            );
            CREATE TABLE IF NOT EXISTS scan_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scanned_at TEXT,
                devices_found INTEGER
            );
            CREATE TABLE IF NOT EXISTS activity_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ip TEXT,
                mac TEXT,
                event TEXT,
                detail TEXT,
                logged_at TEXT
            );
            """
        )
        _migrate_devices_schema(con)
        con.commit()


def _migrate_devices_schema(con: sqlite3.Connection) -> None:
    cols = {r[1] for r in con.execute("PRAGMA table_info(devices)").fetchall()}
    if not cols:
        return
    if "device_key" in cols:
        for col, typ in (
            ("subnet", "TEXT"),
            ("link", "TEXT"),
            ("interface_name", "TEXT"),
            ("services", "TEXT"),
            ("notes", "TEXT"),
            ("latency_ms", "INTEGER"),
            ("top_domains", "TEXT"),
            ("dns_source", "TEXT"),
        ):
            if col not in cols:
                con.execute(f"ALTER TABLE devices ADD COLUMN {col} {typ}")
        return
    # Old schema (ip PRIMARY KEY) → Wi‑Fi + LAN schema
    con.executescript(
        """
        CREATE TABLE devices_new (
            device_key TEXT PRIMARY KEY,
            ip TEXT NOT NULL,
            mac TEXT,
            hostname TEXT,
            status TEXT,
            last_seen TEXT,
            source TEXT,
            vendor TEXT,
            device_type TEXT,
            it_label TEXT,
            first_seen TEXT,
            scan_count INTEGER DEFAULT 0,
            subnet TEXT,
            link TEXT,
            interface_name TEXT
        );
        INSERT INTO devices_new (
            device_key, ip, mac, hostname, status, last_seen, source,
            vendor, device_type, it_label, first_seen, scan_count
        )
        SELECT ip || '|legacy', ip, mac, hostname, status, last_seen, source,
               vendor, device_type, it_label, first_seen, scan_count
        FROM devices;
        DROP TABLE devices;
        ALTER TABLE devices_new RENAME TO devices;
        """
    )


def _log_activity_conn(
    con: sqlite3.Connection,
    ip: str,
    mac: str | None,
    event: str,
    detail: str,
) -> None:
    con.execute(
        "INSERT INTO activity_log (ip, mac, event, detail, logged_at) VALUES (?,?,?,?,datetime('now'))",
        (ip, mac, event, detail),
    )


def log_activity(ip: str, mac: str | None, event: str, detail: str) -> None:
    with _db_lock:
        con = _db_connect()
        try:
            _log_activity_conn(con, ip, mac, event, detail)
            con.commit()
        finally:
            con.close()


def save_devices(devices: list[Device]) -> None:
    now = (
        devices[0].last_seen
        if devices
        else datetime.now(timezone.utc).isoformat()
    )
    new_count = 0
    with _db_lock:
        con = _db_connect()
        try:
            seen_keys = {d.device_key for d in devices}
            for d in devices:
                key = d.device_key
                row = con.execute(
                    "SELECT first_seen, scan_count, it_label FROM devices WHERE device_key=?",
                    (key,),
                ).fetchone()
                first = row[0] if row and row[0] else d.last_seen
                count = (row[1] or 0) + 1 if row else 1
                it_label = row[2] if row else None
                prev = con.execute(
                    "SELECT mac, hostname FROM devices WHERE device_key=?",
                    (key,),
                ).fetchone()
                if prev and (prev[0] != d.mac or prev[1] != d.hostname):
                    _log_activity_conn(
                        con,
                        d.ip,
                        d.mac,
                        "identity_change",
                        f"was mac={prev[0]} host={prev[1]}",
                    )
                con.execute(
                    """
                    INSERT INTO devices (
                        device_key, ip, mac, hostname, status, last_seen, source,
                        vendor, device_type, it_label, first_seen, scan_count,
                        subnet, link, interface_name, services, notes, latency_ms,
                        top_domains, dns_source
                    ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                    ON CONFLICT(device_key) DO UPDATE SET
                        mac=excluded.mac,
                        hostname=excluded.hostname,
                        status='online',
                        last_seen=excluded.last_seen,
                        source=excluded.source,
                        vendor=excluded.vendor,
                        device_type=excluded.device_type,
                        scan_count=excluded.scan_count,
                        subnet=excluded.subnet,
                        link=excluded.link,
                        interface_name=excluded.interface_name,
                        services=excluded.services,
                        notes=excluded.notes,
                        latency_ms=excluded.latency_ms,
                        top_domains=excluded.top_domains,
                        dns_source=excluded.dns_source
                    """,
                    (
                        key,
                        d.ip,
                        d.mac,
                        d.hostname,
                        d.status,
                        d.last_seen,
                        d.source,
                        d.vendor,
                        d.device_type,
                        it_label,
                        first,
                        count,
                        d.subnet,
                        d.link,
                        d.interface_name,
                        getattr(d, "services", None),
                        getattr(d, "notes", None),
                        getattr(d, "latency_ms", None),
                        getattr(d, "top_domains", None),
                        getattr(d, "dns_source", None),
                    ),
                )
                if not row:
                    new_count += 1
                else:
                    _log_activity_conn(
                        con,
                        d.ip,
                        d.mac,
                        "seen_online",
                        f"scan #{count} · {d.link or 'link?'} · {d.latency_ms or '?'}ms",
                    )

            offline_n = 0
            for (key, ip, mac, hostname) in con.execute(
                "SELECT device_key, ip, mac, hostname FROM devices"
            ).fetchall():
                if key not in seen_keys:
                    con.execute(
                        "UPDATE devices SET status='offline', last_seen=? WHERE device_key=?",
                        (now or "", key),
                    )
                    offline_n += 1

            if now:
                con.execute(
                    "INSERT INTO scan_log (scanned_at, devices_found) VALUES (?,?)",
                    (now, len(devices)),
                )
            _log_activity_conn(
                con,
                "",
                None,
                "scan_done",
                f"{len(devices)} online, {new_count} new, {offline_n} offline",
            )
            con.commit()
        finally:
            con.close()


def load_devices() -> list[dict]:
    with _db_lock:
        con = _db_connect()
        try:
            con.row_factory = sqlite3.Row
            rows = con.execute(
                """
                SELECT device_key, ip, mac, hostname, status, last_seen, source,
                       vendor, device_type, it_label, first_seen, scan_count,
                       subnet, link, interface_name, services, notes, latency_ms,
                       top_domains, dns_source
                FROM devices ORDER BY status DESC, link, ip
                """
            ).fetchall()
            return [enrich_device_row(dict(r)) for r in rows]
        finally:
            con.close()


def load_activity(limit: int = 50) -> list[dict]:
    with _db_lock:
        con = _db_connect()
        try:
            con.row_factory = sqlite3.Row
            rows = con.execute(
                """
                SELECT ip, mac, event, detail, logged_at
                FROM activity_log ORDER BY id DESC LIMIT ?
                """,
                (limit,),
            ).fetchall()
            return [dict(r) for r in rows]
        finally:
            con.close()


class ScanResult(BaseModel):
    count: int
    subnet: str
    devices: list[dict]
    online: int
    offline: int


class LabelUpdate(BaseModel):
    label: str


class ControlHttpBody(BaseModel):
    ip: str
    port: int = 80
    method: str = "GET"
    path: str = "/"
    use_https: bool = False


class ControlWolBody(BaseModel):
    ip: str
    mac: str | None = None


class ControlIpBody(BaseModel):
    ip: str


def _device_by_ip(ip: str) -> dict | None:
    ip = ip.strip()
    for d in load_devices():
        if d.get("ip") == ip:
            return d
    return None


def do_scan() -> ScanResult:
    global _scanning, _last_dns_merge
    with _scan_lock:
        if _scanning:
            data = load_devices()
            on = sum(1 for d in data if d.get("status") == "online")
            return ScanResult(
                count=len(data),
                subnet=default_subnet(),
                devices=data,
                online=on,
                offline=len(data) - on,
            )
        _scanning = True
    try:
        devices = run_best_scan()
        try:
            _last_dns_merge = merge_dns_into_devices(devices)
            if _last_dns_merge.get("devices_matched"):
                print(
                    f"  DNS sites: {_last_dns_merge['devices_matched']} device(s) "
                    f"from {_last_dns_merge.get('source') or 'log'}"
                )
            elif _last_dns_merge.get("tries"):
                print(f"  DNS sites: {_last_dns_merge['tries'][-1]}")
        except Exception as de:
            print(f"  DNS lookup skipped: {de}")
            _last_dns_merge = {"ok": False, "error": str(de)}
        save_devices(devices)
        try:
            refresh_network_measurements()
        except Exception as me:
            print(f"  Network metrics: {me}")
        err = last_scan_error()
        if err and not devices:
            print(f"  WARNING: {err}")
        data = load_devices()
        on = sum(1 for d in data if d.get("status") == "online")
        err = last_scan_error()
        return ScanResult(
            count=len(data),
            subnet=default_subnet(),
            devices=data,
            online=on,
            offline=len(data) - on,
        )
    except Exception as e:
        print(f"  SCAN ERROR: {e}")
        import traceback
        traceback.print_exc()
        data = load_devices()
        on = sum(1 for d in data if d.get("status") == "online")
        return ScanResult(
            count=len(data),
            subnet=default_subnet(),
            devices=data,
            online=on,
            offline=len(data) - on,
        )
    finally:
        with _scan_lock:
            _scanning = False


def _delayed_auto_scan() -> None:
    """Wait so startup scan finishes before background rescans."""
    if _auto_stop.wait(90):
        return
    auto_scan_loop()


def auto_scan_loop() -> None:
    interval = int(os.environ.get("AUTO_SCAN_MINUTES", "3")) * 60
    if interval <= 0:
        return
    while not _auto_stop.wait(interval):
        try:
            do_scan()
        except Exception as e:
            print(f"Auto-scan error: {e}")


def _startup_scan() -> None:
    time.sleep(3)
    try:
        print("Running first network scan…")
        result = do_scan()
        print(f"  Saved {result.online} devices to dashboard")
    except Exception as e:
        print(f"  First scan failed: {e}")


@app.get("/api/health")
def health() -> dict:
    return {
        "ok": True,
        "subnet": default_subnet(),
        "auto_scan_minutes": int(os.environ.get("AUTO_SCAN_MINUTES", "5")),
        "topology_api": True,
        "map_url": "/?view=map",
    }


@app.get("/api/info")
def server_info() -> dict:
    lan = get_lan_ip()
    port = get_runtime_port()
    urls = [f"http://127.0.0.1:{port}/"]
    if lan:
        urls.append(f"http://{lan}:{port}/")
    return {
        "ok": True,
        "subnet": default_subnet(),
        "subnet_info": subnet_display_summary(),
        "interfaces": [
            {
                "device": i.device,
                "name": i.name,
                "link": i.link,
                "ip": i.ip,
                "subnet": i.subnet,
            }
            for i in list_active_interfaces()
        ],
        "scan_error": last_scan_error(),
        "network_measurements": get_network_measurements(),
        "wifi_signal": get_local_wifi_signal(),
        "dns": {**(dns_status_for_api()), "last_merge": _last_dns_merge},
        "lan_ip": lan,
        "port": port,
        "urls": urls,
        "auto_scan_minutes": int(os.environ.get("AUTO_SCAN_MINUTES", "3")),
        "message": "Keep this app running on a PC connected to the office LAN.",
    }


@app.post("/api/subnet/refresh")
def subnet_refresh() -> dict:
    s = refresh_subnet()
    return {"subnet": s, "subnet_info": subnet_display_summary()}


@app.post("/api/dns/refresh")
def dns_refresh() -> dict:
    """Re-fetch Pi-hole/AdGuard logs and update top_domains for known devices."""
    global _last_dns_merge
    data = load_devices()

    class _DnsRow:
        __slots__ = ("ip", "top_domains", "dns_source")

        def __init__(self, ip: str):
            self.ip = ip
            self.top_domains = None
            self.dns_source = None

    rows = [_DnsRow(d["ip"]) for d in data]
    _last_dns_merge = merge_dns_into_devices(rows)
    ip_map = {r.ip: r for r in rows}
    with _db_lock:
        con = _db_connect()
        try:
            for d in data:
                r = ip_map.get(d["ip"])
                if not r:
                    continue
                con.execute(
                    "UPDATE devices SET top_domains=?, dns_source=? WHERE device_key=?",
                    (getattr(r, "top_domains", None), getattr(r, "dns_source", None), d["device_key"]),
                )
            con.commit()
        finally:
            con.close()
    return {"ok": True, "devices": load_devices(), **_last_dns_merge}


@app.get("/api/topology")
def topology() -> dict:
    """Flowchart data for network map page (rebuilt from last scan)."""
    data = build_topology(
        load_devices(),
        interfaces=list_active_interfaces(),
    )
    data["scan_error"] = last_scan_error()
    data["network_measurements"] = get_network_measurements()
    data["wifi_signal"] = get_local_wifi_signal()
    return data


@app.get("/api/devices")
def list_devices() -> dict:
    data = load_devices()
    on = sum(1 for d in data if d.get("status") == "online")
    return {"devices": data, "subnet": default_subnet(), "online": on, "offline": len(data) - on}


@app.get("/api/activity")
def activity(limit: int = 80) -> dict:
    return {"events": load_activity(limit)}


@app.get("/api/devices/by-ip/{ip}")
def device_detail(ip: str) -> dict:
    """Everything stored for this IP — for map click details."""
    ip = ip.strip()
    if not ip or len(ip) > 45:
        raise HTTPException(400, "Invalid IP")
    devices = [d for d in load_devices() if d.get("ip") == ip]
    devices = [enrich_device_row(d) for d in devices]
    events = [
        e
        for e in load_activity(limit=200)
        if e.get("ip") == ip or (not e.get("ip") and ip in (e.get("detail") or ""))
    ]
    return {
        "ip": ip,
        "devices": devices,
        "device": devices[0] if devices else None,
        "activity": events,
        "subnet": default_subnet(),
        "subnet_info": subnet_display_summary(),
        "gateway": get_default_gateway(),
        "interfaces": [
            {
                "device": i.device,
                "name": i.name,
                "link": i.link,
                "ip": i.ip,
                "subnet": i.subnet,
            }
            for i in list_active_interfaces()
        ],
        "network_measurements": get_network_measurements(),
        "wifi_signal": get_local_wifi_signal(),
    }


@app.post("/api/devices/{ip}/label")
def set_label(ip: str, body: LabelUpdate) -> dict:
    with _db_lock:
        con = _db_connect()
        try:
            cur = con.execute(
                "UPDATE devices SET it_label=? WHERE ip=? OR device_key LIKE ?",
                (body.label, ip, f"{ip}|%"),
            )
            if cur.rowcount == 0:
                raise HTTPException(404, "Device not found")
            _log_activity_conn(con, ip, None, "label_set", body.label)
            con.commit()
        finally:
            con.close()
    return {"ok": True, "ip": ip, "label": body.label}


@app.get("/api/control/device/{ip}")
def control_device_info(ip: str) -> dict:
    ip = ip.strip()
    if not is_allowed_control_ip(ip):
        raise HTTPException(400, "Only private LAN IP addresses are allowed.")
    try:
        normalize_ip(ip)
    except ValueError as e:
        raise HTTPException(400, str(e)) from e
    dev = _device_by_ip(ip)
    links = open_links_for_device(ip, dev.get("services") if dev else None)
    return {
        "ok": True,
        "ip": ip,
        "device": dev,
        "links": links,
        "allowed": True,
    }


@app.post("/api/control/ping")
def control_ping(body: ControlIpBody) -> dict:
    ip = body.ip.strip()
    if not is_allowed_control_ip(ip):
        raise HTTPException(400, "Only private LAN IPs are allowed.")
    result = ping_device(ip)
    dev = _device_by_ip(ip)
    log_activity(ip, dev.get("mac") if dev else None, "control_ping", str(result.get("latency_ms") or "offline"))
    return result


@app.post("/api/control/wake")
def control_wake(body: ControlWolBody) -> dict:
    ip = body.ip.strip()
    if not is_allowed_control_ip(ip):
        raise HTTPException(400, "Only private LAN IPs are allowed.")
    mac = body.mac
    if not mac:
        dev = _device_by_ip(ip)
        mac = dev.get("mac") if dev else None
    result = send_wake_on_lan(mac or "")
    log_activity(ip, mac, "control_wol", result.get("message") or result.get("error", ""))
    return {**result, "ip": ip}


@app.post("/api/control/probe")
def control_probe(body: ControlIpBody) -> dict:
    ip = body.ip.strip()
    if not is_allowed_control_ip(ip):
        raise HTTPException(400, "Only private LAN IPs are allowed.")
    result = probe_device_ports(ip)
    log_activity(ip, None, "control_probe", result.get("services") or "")
    return result


@app.post("/api/control/http")
def control_http(body: ControlHttpBody) -> dict:
    ip = body.ip.strip()
    if not is_allowed_control_ip(ip):
        raise HTTPException(400, "Only private LAN IPs are allowed.")
    result = http_device_request(
        ip,
        port=body.port,
        method=body.method,
        path=body.path,
        use_https=body.use_https,
    )
    log_activity(ip, None, "control_http", f"{body.method} {result.get('url', ip)}")
    return result


@app.post("/api/scan")
def run_scan() -> dict:
    try:
        result = do_scan()
        err = last_scan_error()
        return {
            **result.model_dump(),
            "scan_error": err,
            "ok": True,
            "hint": err or f"Found {result.online} device(s) on your network.",
        }
    except Exception as e:
        data = load_devices()
        on = sum(1 for d in data if d.get("status") == "online")
        return {
            "count": len(data),
            "subnet": default_subnet(),
            "devices": data,
            "online": on,
            "offline": len(data) - on,
            "scan_error": str(e),
            "ok": False,
            "hint": str(e),
        }


@app.get("/api/export.csv")
def export_csv() -> StreamingResponse:
    data = load_devices()
    buf = io.StringIO()
    w = csv.DictWriter(
        buf,
        fieldnames=[
            "status",
            "device_name",
            "ip",
            "mac",
            "hostname",
            "it_label",
            "vendor",
            "device_type",
            "device_fingerprint",
            "session_duration",
            "services",
            "latency_ms",
            "top_domains",
            "dns_source",
            "notes",
            "subnet",
            "link",
            "interface_name",
            "first_seen",
            "last_seen",
            "scan_count",
        ],
    )
    w.writeheader()
    for row in data:
        w.writerow({k: row.get(k, "") for k in w.fieldnames})
    buf.seek(0)
    return StreamingResponse(
        iter([buf.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=office-devices.csv"},
    )


@app.get("/robots.txt")
def robots_txt() -> FileResponse:
    path = WEB / "robots.txt"
    if not path.is_file():
        raise HTTPException(404, "robots.txt missing")
    return FileResponse(path, media_type="text/plain")


@app.get("/sitemap.xml")
def sitemap_xml() -> FileResponse:
    path = WEB / "sitemap.xml"
    if not path.is_file():
        raise HTTPException(404, "sitemap.xml missing")
    return FileResponse(path, media_type="application/xml")


@app.get("/googlec845b45a3dd5dd12.html", response_class=HTMLResponse)
def google_search_console_verify() -> HTMLResponse:
    """Google Search Console ownership verification."""
    return HTMLResponse(
        content="google-site-verification: googlec845b45a3dd5dd12.html",
        media_type="text/html",
    )


@app.get("/", response_class=HTMLResponse)
def home_page() -> FileResponse:
    return FileResponse(WEB / "index.html")


def _html_page(name: str) -> FileResponse:
    path = WEB / name
    if not path.is_file():
        raise HTTPException(404, f"Page missing: {name}")
    headers = {}
    if name in ("devices.html", "control.html"):
        headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    return FileResponse(path, media_type="text/html", headers=headers)


@app.get("/devices", response_class=HTMLResponse)
@app.get("/devices/", response_class=HTMLResponse)
@app.get("/devices.html", response_class=HTMLResponse)
def devices_page() -> FileResponse:
    return _html_page("devices.html")


@app.get("/control", response_class=HTMLResponse)
@app.get("/control/", response_class=HTMLResponse)
@app.get("/control.html", response_class=HTMLResponse)
def control_page() -> FileResponse:
    return _html_page("control.html")


@app.get("/map", response_class=HTMLResponse)
@app.get("/map/", response_class=HTMLResponse)
@app.get("/map.html", response_class=HTMLResponse)
def network_map_page() -> FileResponse:
    return _html_page("map.html")


@app.get("/about", response_class=HTMLResponse)
@app.get("/about/", response_class=HTMLResponse)
@app.get("/about.html", response_class=HTMLResponse)
def about_page() -> FileResponse:
    return _html_page("about.html")


@app.get("/calendar", response_class=HTMLResponse)
@app.get("/calendar/", response_class=HTMLResponse)
@app.get("/calendar.html", response_class=HTMLResponse)
@app.get("/calender", response_class=HTMLResponse)
@app.get("/calender/", response_class=HTMLResponse)
@app.get("/calender.html", response_class=HTMLResponse)
def calendar_page() -> FileResponse:
    return _html_page("calendar.html")


@app.get("/clock", response_class=HTMLResponse)
@app.get("/clock/", response_class=HTMLResponse)
@app.get("/clock.html", response_class=HTMLResponse)
def clock_page() -> FileResponse:
    return _html_page("clock.html")


@app.get("/index.html", response_class=HTMLResponse)
def index_html() -> FileResponse:
    return _html_page("index.html")


@app.get("/home", response_class=HTMLResponse)
@app.get("/tutorial", response_class=HTMLResponse)
def home_aliases() -> FileResponse:
    return _html_page("index.html")


@app.get("/network-map")
def network_map_alias() -> RedirectResponse:
    return RedirectResponse(url="/map.html", status_code=302)


def _asset_png(filename: str) -> FileResponse:
    install_web_assets()
    path = WEB / "assets" / filename
    if not path.is_file():
        raise HTTPException(
            404,
            f"{filename} not found. Restart app after placing files in web/assets/",
        )
    headers = {}
    if filename in (
        "logo.png",
        "logo-mono.png",
        "logo-display.png",
        "creator.png",
        "creator-mono.png",
        "creator-display.png",
        "favicon-16.png",
        "favicon-32.png",
        "apple-touch-icon.png",
    ):
        headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return FileResponse(path, media_type="image/png", headers=headers)


@app.get("/favicon.ico", include_in_schema=False)
def favicon_ico() -> FileResponse:
    path = WEB / "favicon.ico"
    if not path.is_file():
        path = WEB / "assets" / "favicon-32.png"
    return FileResponse(path, media_type="image/x-icon")


@app.get("/favicon.png", include_in_schema=False)
def favicon_png() -> FileResponse:
    path = WEB / "favicon.png"
    if not path.is_file():
        path = WEB / "assets" / "favicon-32.png"
    return FileResponse(path, media_type="image/png")


@app.get("/assets/favicon-16.png")
def favicon_16() -> FileResponse:
    return _asset_png("favicon-16.png")


@app.get("/assets/favicon-32.png")
def favicon_32() -> FileResponse:
    return _asset_png("favicon-32.png")


@app.get("/assets/apple-touch-icon.png")
def apple_touch_icon() -> FileResponse:
    return _asset_png("apple-touch-icon.png")


@app.get("/assets/logo.png")
def site_logo() -> FileResponse:
    return _asset_png("logo.png")


@app.get("/assets/logo-mono.png")
def site_logo_mono() -> FileResponse:
    return _asset_png("logo-mono.png")


@app.get("/assets/creator.png")
def creator_image() -> FileResponse:
    return _asset_png("creator.png")


@app.get("/assets/creator-mono.png")
def creator_image_mono() -> FileResponse:
    return _asset_png("creator-mono.png")


@app.get("/assets/logo-display.png")
def site_logo_display() -> FileResponse:
    return _asset_png("logo-display.png")


@app.get("/assets/creator-display.png")
def creator_image_display() -> FileResponse:
    return _asset_png("creator-display.png")


@app.get("/api/download/start-command")
def download_start_command_route() -> FileResponse:
    return download_start_command()


@app.get("/api/download/start-bat")
def download_start_bat_route() -> FileResponse:
    return download_start_bat()


@app.get("/api/download/mac-app.zip")
def download_mac_app_route() -> FileResponse:
    return download_mac_app_zip()


@app.get("/api/download/full-mac")
@app.get("/api/download/full-mac.zip")
def download_full_mac_route() -> FileResponse:
    return download_full_mac_zip()


@app.get("/api/download/full-windows")
@app.get("/api/download/full-windows.zip")
def download_full_windows_route() -> FileResponse:
    return download_full_windows_zip()


@app.get("/api/download/guide.txt")
def download_guide() -> FileResponse:
    guide = WEB / "guide.txt"
    if not guide.is_file():
        raise HTTPException(404, "Guide missing")
    return FileResponse(
        guide,
        media_type="text/plain",
        filename="office-network-monitor-guide.txt",
    )


DOWNLOADS_DIR = ROOT / "downloads"
if DOWNLOADS_DIR.is_dir():
    app.mount("/downloads", StaticFiles(directory=DOWNLOADS_DIR), name="downloads")

if WEB.is_dir():
    app.mount("/static", StaticFiles(directory=WEB), name="static")


def main() -> None:
    import uvicorn

    host = os.environ.get("BIND", "0.0.0.0")
    requested = get_runtime_port()
    port = pick_port(requested)
    os.environ["PORT"] = str(port)
    refresh_subnet()
    lan = get_lan_ip()

    print()
    print("=" * 54)
    print("   NETWORK MONITOR — running")
    print("=" * 54)
    if port != requested:
        print(f"   Note: port {requested} was busy (Mac AirPlay uses 5000).")
        print(f"         Using port {port} instead.")
    ifaces = list_active_interfaces()
    print(f"   Networks:       {len(ifaces)} interface(s) — Wi‑Fi + LAN")
    for i in ifaces:
        print(f"     • {i.name} ({i.link}): {i.subnet}  [{i.ip}]")
    print(f"   Auto-rescan:      every {os.environ.get('AUTO_SCAN_MINUTES', '3')} min")
    print()
    print("   Open in browser (keep this window open):")
    print(f"     → http://127.0.0.1:{port}/")
    print(f"     → http://127.0.0.1:{port}/devices.html  (device list)")
    print(f"     → http://127.0.0.1:{port}/control.html   (control by IP)")
    print(f"     → http://127.0.0.1:{port}/map.html       (network map)")
    print(f"     → http://127.0.0.1:{port}/calendar.html  (world calendars)")
    print(f"     → http://127.0.0.1:{port}/clock.html      (world clock)")
    if lan:
        print(f"     → http://{lan}:{port}/   (other PCs on same Wi‑Fi/LAN)")
        print(f"     → http://{lan}:{port}/map")
    print()
    print("   Office: run on IT PC plugged into company network.")
    print("   Home test: works on personal Wi‑Fi too (same steps).")
    print("=" * 54)
    print()
    threading.Thread(
        target=lambda: (time.sleep(2.0), webbrowser.open(f"http://127.0.0.1:{port}/devices.html")),
        daemon=True,
    ).start()
    uvicorn.run(app, host=host, port=port, log_level="warning")


if __name__ == "__main__":
    main()
