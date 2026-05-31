"""Serve launcher files and full app packages for Mac and Windows."""
from __future__ import annotations

import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APP_BUNDLE = ROOT / "Office Network Monitor.app"
DATA_DIR = ROOT / "data"
MAC_ZIP = DATA_DIR / "Office-Network-Monitor-Mac.zip"
FULL_MAC_ZIP = DATA_DIR / "Network-Monitor-Full-Mac.zip"
FULL_WIN_ZIP = DATA_DIR / "Network-Monitor-Full-Windows.zip"

TOP_LEVEL_FILES = (
    "START.command",
    "START.bat",
    "launcher.sh",
    "run.sh",
    "requirements.txt",
    "QUICKSTART.txt",
    "README.md",
    "RUN-IN-TERMINAL.txt",
)

INCLUDE_DIRS = ("server", "web")

SKIP_DIR_NAMES = {".venv", "__pycache__", ".git", "node_modules", "logs"}
SKIP_FILE_SUFFIXES = {".pyc", ".db", ".zip"}


def _file_response(path: Path, filename: str, media_type: str):
    from fastapi.responses import FileResponse

    if not path.is_file():
        from fastapi import HTTPException

        raise HTTPException(404, f"{filename} not found in app folder")
    return FileResponse(path, media_type=media_type, filename=filename)


def _should_skip(rel: Path) -> bool:
    parts = rel.parts
    if any(part in SKIP_DIR_NAMES for part in parts):
        return True
    if "locales" in parts and any(part.startswith("_") for part in parts):
        return True
    if rel.suffix.lower() in SKIP_FILE_SUFFIXES:
        return True
    name = rel.name
    if name.startswith(".") and name not in (".gitkeep",):
        return True
    return False


def _newest_mtime(paths: list[Path]) -> float:
    best = 0.0
    for p in paths:
        if p.is_file():
            best = max(best, p.stat().st_mtime)
        elif p.is_dir():
            for f in p.rglob("*"):
                if f.is_file():
                    best = max(best, f.stat().st_mtime)
    return best


def _build_full_zip(dest: Path, *, include_app: bool) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(".zip.part")
    if tmp.is_file():
        tmp.unlink()

    sources: list[Path] = []
    for name in TOP_LEVEL_FILES:
        p = ROOT / name
        if p.is_file():
            sources.append(p)
    for dirname in INCLUDE_DIRS:
        p = ROOT / dirname
        if p.is_dir():
            sources.append(p)
    if include_app and APP_BUNDLE.is_dir():
        sources.append(APP_BUNDLE)

    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zf:
        for src in sources:
            if src.is_file():
                arc = f"office-net-monitor/{src.name}"
                zf.write(src, arc)
                continue
            for f in sorted(src.rglob("*")):
                if not f.is_file():
                    continue
                rel = f.relative_to(ROOT)
                if _should_skip(rel):
                    continue
                arc = f"office-net-monitor/{rel.as_posix()}"
                zf.write(f, arc)

        readme = (
            "Network Monitor — full package\n\n"
            "1. Unzip this folder\n"
            "2. Mac: double-click office-net-monitor/START.command\n"
            "3. Windows: double-click office-net-monitor/START.bat\n"
            "4. Open http://127.0.0.1:5080/ in your browser\n\n"
            "Requires Python 3. First run installs dependencies.\n"
        )
        zf.writestr("office-net-monitor/INSTALL-FIRST.txt", readme)

    if dest.is_file():
        dest.unlink()
    tmp.rename(dest)


def _ensure_full_zip(dest: Path, *, include_app: bool) -> None:
    sources: list[Path] = [ROOT / "server", ROOT / "web", ROOT / "requirements.txt"]
    sources.extend(ROOT / n for n in TOP_LEVEL_FILES if (ROOT / n).is_file())
    if include_app and APP_BUNDLE.is_dir():
        sources.append(APP_BUNDLE)
    src_mtime = _newest_mtime(sources)
    if dest.is_file() and dest.stat().st_mtime >= src_mtime:
        return
    _build_full_zip(dest, include_app=include_app)


def download_start_command():
    return _file_response(
        ROOT / "START.command",
        "START.command",
        "application/octet-stream",
    )


def download_start_bat():
    return _file_response(ROOT / "START.bat", "START.bat", "application/octet-stream")


def download_mac_app_zip():
    if not APP_BUNDLE.is_dir():
        from fastapi import HTTPException

        raise HTTPException(404, "Network Monitor.app not found (Office Network Monitor.app)")
    MAC_ZIP.parent.mkdir(parents=True, exist_ok=True)
    app_mtime = max(
        (p.stat().st_mtime for p in APP_BUNDLE.rglob("*") if p.is_file()),
        default=0,
    )
    if MAC_ZIP.is_file() and MAC_ZIP.stat().st_mtime >= app_mtime:
        return _file_response(
            MAC_ZIP,
            "Office-Network-Monitor-Mac.zip",
            "application/zip",
        )
    base = MAC_ZIP.with_suffix("")
    if base.with_suffix(".zip").is_file():
        base.with_suffix(".zip").unlink()
    shutil.make_archive(str(base), "zip", ROOT, APP_BUNDLE.name)
    return _file_response(
        MAC_ZIP,
        "Office-Network-Monitor-Mac.zip",
        "application/zip",
    )


def download_full_mac_zip():
    _ensure_full_zip(FULL_MAC_ZIP, include_app=APP_BUNDLE.is_dir())
    return _file_response(
        FULL_MAC_ZIP,
        "Network-Monitor-Full-Mac.zip",
        "application/zip",
    )


def download_full_windows_zip():
    _ensure_full_zip(FULL_WIN_ZIP, include_app=False)
    return _file_response(
        FULL_WIN_ZIP,
        "Network-Monitor-Full-Windows.zip",
        "application/zip",
    )
