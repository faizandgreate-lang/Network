#!/usr/bin/env python3
"""Make web/ work on GitHub Pages (/Network/) and locally."""
from __future__ import annotations

import re
from pathlib import Path

WEB = Path(__file__).resolve().parent.parent / "web"
HTML = list(WEB.glob("*.html"))
JS_FILES = [
    WEB / "logo.js",
    WEB / "map-interactions.js",
    WEB / "topology.js",
    WEB / "world-calendars.js",
    WEB / "retro-theme.js",
]

NAV = {
    'href="/"': 'href="index.html"',
    "href='/\"": "href='index.html'",
    'href="/devices.html"': 'href="devices.html"',
    'href="/map.html"': 'href="map.html"',
    'href="/calendar.html"': 'href="calendar.html"',
    'href="/clock.html"': 'href="clock.html"',
    'href="/about.html"': 'href="about.html"',
    'href="/about"': 'href="about.html"',
}


def fix_html_inline_fetch(text: str) -> str:
    return re.sub(
        r"fetch\(\s*(['\"])/api/",
        r"fetch(appUrl(\1/api/",
        text,
    )


def fix_html(text: str) -> str:
    if "app-base.js" not in text:
        text = text.replace(
            '<script src="static/theme-boot.js">',
            '<script src="static/app-base.js"></script>\n  <script src="static/theme-boot.js">',
            1,
        )
    text = text.replace('href="/static/', 'href="static/')
    text = text.replace("href='/static/", "href='static/")
    text = text.replace('src="/static/', 'src="static/')
    text = text.replace("src='/static/", "src='static/")
    text = text.replace('href="/assets/', 'href="assets/')
    text = text.replace('src="/assets/', 'src="assets/')
    for old, new in NAV.items():
        text = text.replace(old, new)
    text = fix_html_inline_fetch(text)
    return text


def fix_js_fetch(text: str) -> str:
    return re.sub(
        r"fetch\(\s*(['\"])/api/",
        r"fetch(appUrl(\1/api/",
        text,
    )


def fix_js_paths(text: str) -> str:
    text = text.replace("'/assets/", "appUrl('/assets/")
    text = text.replace('"/assets/', 'appUrl("/assets/')
    if "logo.js" in text or "LOGO" in text:
        pass
    return fix_js_fetch(text)


def main() -> None:
    for path in HTML:
        path.write_text(fix_html(path.read_text(encoding="utf-8")), encoding="utf-8")
        print("html", path.name)
    for path in JS_FILES:
        if not path.is_file():
            continue
        t = path.read_text(encoding="utf-8")
        path.write_text(fix_js_fetch(t), encoding="utf-8")
        print("js", path.name)
    (WEB / ".nojekyll").write_text("", encoding="utf-8")
    print("wrote .nojekyll")


if __name__ == "__main__":
    main()
