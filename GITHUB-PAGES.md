# GitHub Pages — same layout as localhost

**URL:** https://faizandgreate-lang.github.io/Network/

## Settings

| Setting | Value |
|---------|--------|
| Source | Deploy from a branch |
| Branch | `main` |
| Folder | **`/docs`** |
| Custom domain | **leave empty** |

Wait 5 minutes after saving, then hard-refresh (Cmd+Shift+R).

## Why it looked broken before

The site uses `static/site.css` (same as localhost). The `docs/` folder was missing the **`static/`** subfolder, so CSS returned 404 and the page had no layout.

After `bash scripts/sync-docs-for-github-pages.sh`, `docs/static/site.css` exists.

## What GitHub cannot do

Scan Wi‑Fi, device list API, and CSV need the real app:

1. From the site: **Download & start** → Mac/Windows full `.zip` (or GitHub Code → Download ZIP)  
2. Unzip, then `START.command` (Mac) or `START.bat` (Windows)  
3. Open http://127.0.0.1:5080/

## Sitemap (Google Search Console)

- **Sitemap URL:** `https://network.linux-aios.com/sitemap.xml`
- **Robots:** `https://network.linux-aios.com/robots.txt`
- In Search Console → **Sitemaps** → add: `sitemap.xml`
- Regenerate after page changes: `bash scripts/generate-sitemap.sh && bash scripts/sync-docs-for-github-pages.sh`  
3. Open **http://127.0.0.1:5080/**

That is the full software — same as on your PC.
