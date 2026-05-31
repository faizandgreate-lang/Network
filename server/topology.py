"""Network map from scanned facts only — no guessed roles."""
from __future__ import annotations

import re
from collections import defaultdict

from network_util import NetInterface, get_default_gateway, get_lan_ip


def _safe_id(text: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_]", "_", text)[:40]


def _device_label(d: dict) -> str:
    ip = d.get("ip") or "?"
    parts = [ip]
    if d.get("hostname"):
        parts.append(str(d["hostname"])[:20])
    elif d.get("vendor"):
        parts.append(str(d["vendor"])[:16])
    if d.get("it_label"):
        parts.append(str(d["it_label"])[:14])
    ms = d.get("latency_ms")
    if ms is not None and ms != "":
        parts.append(f"{ms}ms")
    return " ".join(parts)[:48]


MERMAID_INIT = (
    "%%{init: {'flowchart': {'rankSpacing': 55, 'nodeSpacing': 38, 'curve': 'basis'}, "
    "'themeVariables': {'fontSize': '15px', 'fontFamily': 'Segoe UI'}}}%%"
)


def build_topology(
    devices: list[dict],
    gateway: str | None = None,
    interfaces: list[NetInterface] | None = None,
) -> dict:
    gateway = gateway or get_default_gateway()
    lan_ip = get_lan_ip()
    online = [d for d in devices if d.get("status") == "online"]
    offline = [d for d in devices if d.get("status") != "online"]
    offline_n = len(offline)

    nodes: list[dict] = []
    edges: list[dict] = []

    def add_node(nid: str, label: str, ntype: str, count: int = 0, **extra: object):
        nodes.append({"id": nid, "label": label, "type": ntype, "count": count, **extra})

    def add_edge(src: str, dst: str, label: str = "", dotted: bool = False):
        edges.append({"from": src, "to": dst, "label": label, "dotted": dotted})

    add_node(
        "internet",
        "Internet",
        "cloud",
        0,
        detail={
            "title": "Internet",
            "summary": "WAN uplink — your network’s connection to the public internet.",
            "bullets": [
                "Traffic flows: Internet → Gateway → Wi‑Fi / LAN → devices.",
                "Click gateway or device nodes for scan details.",
            ],
        },
    )
    if gateway:
        gw_dev = next((d for d in online if d.get("ip") == gateway), None)
        if not gw_dev:
            gw_dev = next((d for d in offline if d.get("ip") == gateway), None)
        gw_label = f"Gateway {gateway}"
        if gw_dev:
            if gw_dev.get("hostname"):
                gw_label = f"{gw_dev['hostname']} {gateway}"
            elif gw_dev.get("vendor"):
                gw_label = f"{gw_dev['vendor']} {gateway}"
        add_node("gateway", gw_label, "router", 0, device=gw_dev, gateway_ip=gateway)
        add_edge("internet", "gateway", "WAN")
        root = "gateway"
    else:
        add_node("lan", "LAN (no gateway detected)", "segment", len(online))
        add_edge("internet", "lan")
        root = "lan"

    by_link: dict[str, list[dict]] = defaultdict(list)
    for d in online:
        if gateway and d.get("ip") == gateway:
            continue
        link = d.get("link") or "unknown"
        by_link[link].append(d)

    link_names = {"wifi": "Wi‑Fi", "ethernet": "LAN cable", "other": "Other", "unknown": "Unknown link"}
    max_per_branch = 24
    max_on_map = 60
    shown = 0

    for link, devs in sorted(by_link.items()):
        if shown >= max_on_map:
            break
        lid = f"link_{link}"
        ifaces = interfaces or []
        iface = next((i for i in ifaces if i.link == link), None)
        extra = f" {iface.name}" if iface else ""
        add_node(lid, f"{link_names.get(link, link)}{extra} ({len(devs)})", "segment", len(devs))
        add_edge(root, lid, link)
        room = min(max_per_branch, max_on_map - shown)
        for i, d in enumerate(sorted(devs, key=lambda x: x.get("ip", ""))[:room]):
            did = f"dev_{link}_{i}"
            add_node(did, _device_label(d), "device", 1, device=d)
            add_edge(lid, did)
            shown += 1

    if len(online) > shown + (1 if gateway else 0):
        add_node("more", f"+ {len(online) - shown} more (device list)", "group", 0)
        add_edge(root, "more")

    if offline_n:
        add_node("offline", f"Offline in DB: {offline_n}", "offline", offline_n)
        add_edge(root, "offline")
        for i, d in enumerate(sorted(offline, key=lambda x: x.get("ip", ""))[:8]):
            oid = f"off_{i}"
            add_node(oid, _device_label(d), "offline_device", 1, device=d)
            add_edge("offline", oid)

    if lan_ip:
        mon = next((d for d in online if d.get("ip") == lan_ip), None)
        add_node("monitor", f"This PC {lan_ip}", "device", 0, device=mon, monitor_ip=lan_ip)
        add_edge(root, "monitor", "you", dotted=True)

    mermaid = _to_mermaid(nodes, edges)

    return {
        "ok": True,
        "gateway": gateway,
        "main_router": {"ip": gateway, "name": gateway or "—"},
        "online": len(online),
        "offline": offline_n,
        "total_in_db": len(devices),
        "monitor_ip": lan_ip,
        "nodes": nodes,
        "edges": edges,
        "mermaid": mermaid,
        "updated_note": "From last scan only. Empty fields = not detected.",
        "needs_scan": len(online) == 0 and len(devices) == 0,
    }


def _to_mermaid(nodes: list[dict], edges: list[dict]) -> str:
    lines = [
        MERMAID_INIT,
        "flowchart LR",
        "  classDef cloud fill:#000,stroke:#22c55e,color:#fff",
        "  classDef router fill:#000,stroke:#22c55e,color:#fff",
        "  classDef segment fill:#000,stroke:#22c55e,color:#fff",
        "  classDef device fill:#000,stroke:#fff,color:#fff",
        "  classDef offline fill:#000,stroke:#ef4444,color:#fff",
        "  classDef group fill:#000,stroke:#888,color:#fff",
    ]
    style_map = {
        "cloud": "cloud",
        "router": "router",
        "segment": "segment",
        "device": "device",
        "offline": "offline",
        "offline_device": "offline",
        "group": "group",
    }
    for n in nodes:
        nid = _safe_id(n["id"])
        label = n["label"].replace("<br/>", " ").replace("\n", " ").replace('"', "'")
        if n["type"] == "router":
            lines.append(f'  {nid}{{"{label}"}}')
        elif n["type"] == "cloud":
            lines.append(f'  {nid}(["{label}"])')
        else:
            lines.append(f'  {nid}["{label}"]')
        lines.append(f"  class {nid} {style_map.get(n['type'], 'device')}")

    for e in edges:
        a, b = _safe_id(e["from"]), _safe_id(e["to"])
        lbl = e.get("label") or ""
        if e.get("dotted"):
            if lbl:
                lines.append(f"  {a} -.->|{lbl}| {b}")
            else:
                lines.append(f"  {a} -.-> {b}")
        elif lbl:
            lines.append(f"  {a} -->|{lbl}| {b}")
        else:
            lines.append(f"  {a} --> {b}")

    return "\n".join(lines)
