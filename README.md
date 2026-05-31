# Network Monitor

**Creator:** [Mohammad Faizan Khan](https://khan.linux-aios.com) · [linux-aios.com](https://linux-aios.com)

A local IT dashboard to see **what is on your office or home Wi‑Fi and LAN** — without cloud accounts or extra hardware.

## Disclaimer

- **Learning & information only** — not for unauthorized scanning or any misuse.
- **Creator not responsible for misuse** — if someone uses this tool wrongly, Mohammad Faizan Khan is not liable.
- **Use only on networks you own or are allowed to monitor.**
- **Code is free** — use, copy, modify, and share however you want; no permission needed from the creator.

Full text: [DISCLAIMER.md](DISCLAIMER.md)

---

## Two ways to use this project

| Where | URL | What you get |
|--------|-----|----------------|
| **GitHub (preview)** | https://faizandgreate-lang.github.io/Network/ | Same **look** (pages, logo, theme). Scan/API need the local app. |
| **On your PC (full app)** | http://127.0.0.1:5080/ | **Everything** — same as the creator: scan Wi‑Fi/LAN, device list, map, CSV. |

### Download and run (anyone — same as localhost)

1. **Get the code:** [Download ZIP](https://github.com/faizandgreate-lang/Network/archive/refs/heads/main.zip) or `git clone https://github.com/faizandgreate-lang/Network.git`
2. **Unzip** (if ZIP) and open the folder `Network-main` (or `Network`).
3. **Start:**
   - **Mac:** double-click `START.command` (keep Terminal open)
   - **Windows:** double-click `START.bat` (keep the window open)
4. Browser opens **http://127.0.0.1:5080/** — use the site the same way as on the creator’s machine.

First run installs Python packages automatically (needs internet once).

**GitHub Pages setup (for the live preview):** repo → Settings → Pages → branch `main`, folder **`/web`**. See [GITHUB-PAGES.md](GITHUB-PAGES.md).

---

## Why we made it

- **See the whole network in one place** — PCs, phones, printers, and gateways on Wi‑Fi and Ethernet, not scattered router screens.
- **Real data only** — scans show IP, MAC, hostname, and ports when detected; empty fields mean “not detected,” not guessed labels.
- **Runs on your machine** — nothing leaves your LAN; you control when to scan and export CSV.
- **Simple for non‑technical staff** — double‑click start, open the browser, scan, name devices, view a map, download a guide or PDF.

Typical uses: office inventory, “what joined the Wi‑Fi?”, labeling printers and room PCs, sharing a device list with IT.

---

## How we made it

| Layer | What |
|--------|------|
| **Start** | `START.command` (Mac) or `START.bat` (Windows) → `launcher.sh` sets up Python venv, installs deps, opens **http://127.0.0.1:5080/** |
| **Backend** | Python **FastAPI** (`server/main.py`) — ping + ARP scan, SQLite device DB, optional DNS/port enrichment |
| **Frontend** | Static HTML/CSS/JS (`web/`) — home tutorial, device table, interactive network map (Mermaid) |
| **Map** | Flowchart from last scan: Internet → gateway → Wi‑Fi/LAN → devices; fit‑to‑screen, zoom at cursor, click nodes for details, PDF export |
| **UI** | Black background, white text, green online / red offline; logo processed to white‑on‑black on startup |

**Stack:** Python 3, FastAPI, uvicorn, SQLite, Mermaid.js (map). No React build step — easy to run from a folder copy.

**Honest limits:** A browser alone cannot scan the network; this app runs a small **server on your PC** on the same LAN. It does not record websites visited or full traffic — that needs router DNS/firewall tools (see below).

---

## Quick start

**Mac:** Double‑click `START.command` or `Office Network Monitor.app` (shows as **Network Monitor**) — keep Terminal open.

**Windows:** Double‑click `START.bat` — keep the window open.

Open **http://127.0.0.1:5080/** → **Device list** → **Scan Wi‑Fi + LAN** → **Network map**.

Download launchers from the home page (step 01) if you copied the project to another PC.

More detail: `QUICKSTART.txt` and `RUN-IN-TERMINAL.txt`.

---

## What you can see

| Feature | How |
|---------|-----|
| Device list (IP, MAC, status) | LAN scan + ARP |
| Vendor / hostname / open ports | When the device responds |
| IT labels | You type names in the table (saved locally) |
| Network map | Built from the last scan |
| Export | CSV + user guide + map PDF |

For **websites or bandwidth per person**, use router admin, Pi‑hole/AdGuard DNS logs, or ntopng — this app lists **who is connected**, not full browsing history.

---

## Optional settings

```bash
export OFFICE_SUBNET=192.168.1.0/24   # if auto-detect is wrong
export AUTO_SCAN_MINUTES=0            # default: scan only when you click
export BIND=0.0.0.0                   # let other PCs on LAN open the dashboard
```

---

## Project layout

```
office-net-monitor/
  START.command / START.bat    # one-click start
  launcher.sh / run.sh
  server/                      # FastAPI + scanner + topology
  web/                         # pages + site.css + map scripts
  data/                        # SQLite + OUI vendor data
```

Put the monitor on a PC that stays on the **same network** as the devices you want to find (usually behind your main router).
