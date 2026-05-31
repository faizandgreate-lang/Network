# Fix “404 — There isn’t a GitHub Pages site here”

## Correct URL (project repo)

**https://faizandgreate-lang.github.io/Network/**

Do **not** open only `https://faizandgreate-lang.github.io/` — that shows 404 unless you have a separate user site.

---

## Turn on Pages (do this once)

### Method A — GitHub Actions (recommended)

1. Open: https://github.com/faizandgreate-lang/Network/settings/pages  
2. **Build and deployment** → **Source:** choose **GitHub Actions** (not “Deploy from branch”)  
3. After you push this repo, open: https://github.com/faizandgreate-lang/Network/actions  
4. Run workflow **Deploy GitHub Pages** — wait until green ✓  
5. Open **https://faizandgreate-lang.github.io/Network/**

### Method B — Branch `docs`

1. Settings → Pages  
2. Source: **Deploy from a branch**  
3. Branch: **`main`** · Folder: **`/docs`**  
4. Save, wait 5 minutes  
5. Open **https://faizandgreate-lang.github.io/Network/**

---

## Custom domain

If you see 404 or broken layout on `network.linux-aios.com`:

1. Settings → Pages → **Custom domain** → **clear the box** → Save  
2. Use **https://faizandgreate-lang.github.io/Network/** first until that works  

---

## Full app (scan Wi‑Fi)

GitHub only hosts the **website preview**. To scan devices:

1. Download ZIP or clone the repo  
2. **Mac:** `START.command` · **Windows:** `START.bat`  
3. **http://127.0.0.1:5080/**
