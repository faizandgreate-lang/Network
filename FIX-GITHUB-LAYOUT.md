# Fix broken layout on GitHub

## What went wrong

GitHub Pages has a **custom domain** set: `network.linux-aios.com`

- That domain loads the HTML page
- But **CSS and images return 404** → plain unstyled text, “nothing looks right”

## Fix (choose one)

### Option A — Recommended (easiest)

1. Open: https://github.com/faizandgreate-lang/Network/settings/pages  
2. Under **Custom domain**, **clear** `network.linux-aios.com` (empty box)  
3. Click **Save**  
4. Set **Branch:** `main` · **Folder:** `/docs`  
5. Wait 5 minutes, open: **https://faizandgreate-lang.github.io/Network/**  
6. Hard refresh: **Cmd+Shift+R**

### Option B — Keep custom domain

The code now loads CSS from `faizandgreate-lang.github.io/Network/` when you open `network.linux-aios.com`.

Push the latest `docs/` folder, wait for Pages to rebuild, then refresh.

You still need DNS: `network` CNAME → `faizandgreate-lang.github.io`

---

## Settings checklist

| Setting | Value |
|---------|--------|
| Source | Deploy from branch |
| Branch | `main` |
| Folder | **`/docs`** (not root) |

After you change `web/`, run:

```bash
bash scripts/sync-docs-for-github-pages.sh
git add docs
git commit -m "Update docs"
git push
```
