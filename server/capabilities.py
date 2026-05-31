"""Honest feature matrix — router-admin reality vs this LAN scanner."""
from __future__ import annotations

# category: basic | internet | enterprise
CAPABILITIES: list[dict] = [
    {
        "id": "device_name",
        "category": "basic",
        "label": "Device name",
        "status": "partial",
        "router_typical": "Often visible in router client list (DHCP hostname).",
        "we_provide": "DNS hostname, MAC vendor (OUI), and your IT label.",
        "needs": None,
    },
    {
        "id": "device_type",
        "category": "basic",
        "label": "Device type",
        "status": "partial",
        "router_typical": "Router may show icon/type if it recognizes the vendor.",
        "we_provide": "Guess from vendor + hostname + open ports.",
        "needs": None,
    },
    {
        "id": "mac",
        "category": "basic",
        "label": "MAC address",
        "status": "supported",
        "router_typical": "Yes — standard on almost all routers.",
        "we_provide": "From ARP after ping when the device is on LAN.",
        "needs": None,
    },
    {
        "id": "ip",
        "category": "basic",
        "label": "IP address",
        "status": "supported",
        "router_typical": "Yes — DHCP / ARP tables.",
        "we_provide": "From ping + ARP (+ nmap if installed).",
        "needs": None,
    },
    {
        "id": "connected_time",
        "category": "basic",
        "label": "Connected time",
        "status": "partial",
        "router_typical": "Routers often show “connected since” per client.",
        "we_provide": "First seen / last seen from our scans — not router uptime.",
        "needs": "Router admin page or API for authoritative session times.",
    },
    {
        "id": "data_usage",
        "category": "basic",
        "label": "Data usage (upload/download)",
        "status": "unavailable",
        "router_typical": "Many routers show per-device traffic totals.",
        "we_provide": None,
        "needs": "Router traffic page, SNMP, or UniFi/Meraki API — not this LAN scanner.",
    },
    {
        "id": "signal_strength",
        "category": "basic",
        "label": "Signal strength",
        "status": "partial",
        "router_typical": "Wi‑Fi routers/controllers show RSSI per wireless client.",
        "we_provide": "RSSI for this Mac only (to your AP), not every device.",
        "needs": "Router or enterprise Wi‑Fi controller for each client’s signal.",
    },
    {
        "id": "connection_history",
        "category": "basic",
        "label": "Connection history",
        "status": "partial",
        "router_typical": "Some routers log join/disconnect events.",
        "we_provide": "Our activity log when devices reappear in scans.",
        "needs": "Router syslog or controller for full history.",
    },
    {
        "id": "websites",
        "category": "internet",
        "label": "Websites / domains (e.g. youtube.com, google.com)",
        "status": "unavailable",
        "router_typical": "Possible if DNS queries go through the router and logging is enabled.",
        "we_provide": None,
        "needs": "Router DNS log, Pi-hole, AdGuard, or DNS filtering service.",
    },
    {
        "id": "dns_requests",
        "category": "internet",
        "label": "DNS requests",
        "status": "unavailable",
        "router_typical": "Same as above — domain names from DNS, not full HTTPS pages.",
        "we_provide": None,
        "needs": "DNS logging on router or separate DNS server you control.",
    },
    {
        "id": "bandwidth_per_app",
        "category": "internet",
        "label": "Bandwidth per app/service",
        "status": "unavailable",
        "router_typical": "Rare on home routers; more common on advanced firewalls/QoS.",
        "we_provide": None,
        "needs": "Firewall DPI/QoS, or software on each device.",
    },
    {
        "id": "captive_portal",
        "category": "enterprise",
        "label": "Captive portals",
        "status": "unavailable",
        "router_typical": "Guest Wi‑Fi portals can log name/email/phone when users sign in.",
        "we_provide": None,
        "needs": "Guest portal system you administer (+ consent).",
    },
    {
        "id": "dpi",
        "category": "enterprise",
        "label": "Deep Packet Inspection (DPI)",
        "status": "unavailable",
        "router_typical": "Enterprise firewalls/ISPs — still limited vs HTTPS content.",
        "we_provide": None,
        "needs": "UTM/firewall with DPI and legal basis to use it.",
    },
    {
        "id": "firewall",
        "category": "enterprise",
        "label": "Firewall appliances",
        "status": "partial",
        "router_typical": "Full traffic/policy stats on the appliance.",
        "we_provide": "Firewall may appear as a LAN device (IP/MAC/ports) only.",
        "needs": "Vendor API (FortiGate, pfSense, etc.).",
    },
    {
        "id": "wifi_controller",
        "category": "enterprise",
        "label": "Enterprise Wi‑Fi controllers",
        "status": "unavailable",
        "router_typical": "Client list, RSSI, roam history, sometimes location hints.",
        "we_provide": None,
        "needs": "UniFi, Aruba, Cisco, Meraki dashboard API.",
    },
    {
        "id": "login_pii",
        "category": "enterprise",
        "label": "Login emails / phone numbers",
        "status": "unavailable",
        "router_typical": "Usually only via captive portal or identity system — not passive LAN scan.",
        "we_provide": None,
        "needs": "Portal/MDM/SSO you operate, with user consent where required.",
    },
    {
        "id": "browsing_categories",
        "category": "enterprise",
        "label": "Browsing categories",
        "status": "unavailable",
        "router_typical": "From DNS/security filters (e.g. family/business categories).",
        "we_provide": None,
        "needs": "Cisco Umbrella, FortiGuard, Pi-hole groups, etc.",
    },
    {
        "id": "session_duration",
        "category": "enterprise",
        "label": "Session duration",
        "status": "partial",
        "router_typical": "Router/controller session timers.",
        "we_provide": "Estimate from first_seen → last_seen in our database.",
        "needs": "Router/controller for live session length.",
    },
    {
        "id": "fingerprint",
        "category": "enterprise",
        "label": "Device fingerprint",
        "status": "partial",
        "router_typical": "Enterprise gear may use MAC + DHCP fingerprinting.",
        "we_provide": "Hash of MAC + vendor + hostname + ports (ID aid only).",
        "needs": None,
    },
    {
        "id": "location",
        "category": "enterprise",
        "label": "Location inside building",
        "status": "unavailable",
        "router_typical": "Multi-AP systems may estimate zone from strongest AP.",
        "we_provide": None,
        "needs": "Controller maps, BLE beacons, or manual floor plans.",
    },
    {
        "id": "app_usage",
        "category": "enterprise",
        "label": "App usage statistics",
        "status": "unavailable",
        "router_typical": "Not from router alone — needs endpoint software.",
        "we_provide": None,
        "needs": "MDM/agent on each device.",
    },
]

DEPENDS_ON: list[str] = [
    "Router brand and firmware (features vary a lot)",
    "Whether you own or administer the network",
    "Local privacy laws and workplace policies",
    "Whether users were informed and gave consent where required",
]

HTTPS_CANNOT_SEE: list[str] = [
    "Passwords",
    "Private message contents",
    "HTTPS page contents (what you read on a secure site)",
    "WhatsApp / Signal / iMessage chat contents",
    "Banking and payment details inside encrypted sessions",
]

SECTIONS: list[dict] = [
    {
        "id": "basic",
        "title": "Basic network data (typical router admin)",
        "intro": "If you manage the Wi‑Fi/router, this layer is common. This app collects part of it by scanning the LAN from one computer — without logging into your router.",
    },
    {
        "id": "internet",
        "title": "Internet activity (limited on normal routers)",
        "intro": "Many routers can log domain names when DNS passes through them. They still do not see encrypted page content. This app does not read router DNS logs.",
    },
    {
        "id": "enterprise",
        "title": "Advanced monitoring (enterprise / ISP / special systems)",
        "intro": "Captive portals, DPI, firewalls, and Wi‑Fi controllers can collect more — usually only on networks you legally control, with appropriate notices and consent.",
    },
]


def capabilities_payload() -> dict:
    supported = sum(1 for c in CAPABILITIES if c["status"] == "supported")
    partial = sum(1 for c in CAPABILITIES if c["status"] == "partial")
    unavailable = sum(1 for c in CAPABILITIES if c["status"] == "unavailable")
    by_category: dict[str, list[dict]] = {}
    for c in CAPABILITIES:
        by_category.setdefault(c["category"], []).append(c)

    return {
        "items": CAPABILITIES,
        "depends_on": DEPENDS_ON,
        "https_cannot_see": HTTPS_CANNOT_SEE,
        "sections": [
            {**sec, "items": by_category.get(sec["id"], [])}
            for sec in SECTIONS
        ],
        "summary": {
            "supported": supported,
            "partial": partial,
            "unavailable": unavailable,
            "total": len(CAPABILITIES),
        },
        "policy": "No fake or demo data. Empty cells mean not detected.",
        "this_app_role": (
            "Network Monitor scans devices on your LAN (IP, MAC, hostname, ports, ping). "
            "It does not replace your router admin panel, DNS logs, or enterprise Wi‑Fi dashboard."
        ),
    }
