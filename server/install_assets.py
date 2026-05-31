"""Copy logo + creator photo into web/assets on startup."""
from __future__ import annotations

import shutil
from pathlib import Path

WEB = Path(__file__).resolve().parent.parent / "web"
ASSETS = WEB / "assets"

LOGO_NAME = "logo.png"
LOGO_MONO_NAME = "logo-mono.png"
LOGO_DISPLAY_NAME = "logo-display.png"
CREATOR_NAME = "creator.png"
CREATOR_MONO_NAME = "creator-mono.png"
CREATOR_DISPLAY_NAME = "creator-display.png"

_DISPLAY_INK = (67, 56, 202)
_CREATOR_INK = (51, 65, 85)

LOGO_SOURCES = (
    "logo.png",
    "logo_2-6c84e840-fe17-4005-9864-b09301639ef1.png",
    "logo_2-c6634556-d0f8-4fa9-b913-4294feb40663.png",
    "logo_2.png",
    "creator_logo-492bdca3-5f06-4165-a156-350f41aeb2e6.png",
    "creator_logo.png",
    "Sighnature-89f1f5d7-258f-44ce-ba5a-f4bd7de00c50.png",
    "signature.png",
    "logo.png",
)

CREATOR_SOURCES = (
    "creator.png",
    "creator-a87fd385-e26e-43b3-accc-3a85c014d61e.png",
    "MOHAMMAD_FAIZAN_KHAN-6faacc18-7ce1-40fd-9e33-cfdd278829dd.png",
    "MOHAMMAD_FAIZAN_KHAN-68df838b-7ce1-40fd-9e33-cfdd278829dd.png",
    "MOHAMMAD_FAIZAN_KHAN-6faacc18-5bfc-44a5-abdc-282480e577a2.png",
    "MOHAMMAD_FAIZAN_KHAN-8c6c138d-b559-4c21-b010-13d213909dd4.png",
    "creator-portrait.png",
)

_PHOSPHOR = (51, 255, 102)


def _phosphor_rgb(intensity: float) -> tuple[int, int, int]:
    t = max(0.0, min(1.0, intensity))
    return (
        int(_PHOSPHOR[0] * t),
        int(_PHOSPHOR[1] * t),
        int(_PHOSPHOR[2] * t),
    )


def _mono_rgb(intensity: float) -> tuple[int, int, int]:
    v = int(255 * max(0.0, min(1.0, intensity)))
    return (v, v, v)


def _ink_rgb(base: tuple[int, int, int], intensity: float) -> tuple[int, int, int]:
    t = max(0.0, min(1.0, intensity))
    return (int(base[0] * t), int(base[1] * t), int(base[2] * t))


def _safe_copy(src: Path, dst: Path) -> None:
    if src.resolve() == dst.resolve():
        return
    shutil.copy2(src, dst)


def _search_dirs() -> list[Path]:
    """Source folders only — never read already-built files from web/assets."""
    root = WEB.parent
    home = Path.home()
    return [
        root / "assets",
        root.parent / "assets",
        home
        / ".cursor"
        / "projects"
        / "Users-mohammadkhan-Downloads-RuView-main"
        / "assets",
        home / "Downloads" / "RuView-main" / "assets",
        home / "Downloads" / "RuView-main" / "office-net-monitor" / "assets",
    ]


def _find_file(names: tuple[str, ...]) -> Path | None:
    for folder in _search_dirs():
        if not folder.is_dir():
            continue
        for name in names:
            p = folder / name
            if p.is_file():
                return p
    return None


def _newest_glob_in_folder(folder: Path, pattern: str) -> Path | None:
    newest: Path | None = None
    newest_mtime = 0.0
    for p in folder.glob(pattern):
        if not p.is_file():
            continue
        mtime = p.stat().st_mtime
        if mtime >= newest_mtime:
            newest_mtime = mtime
            newest = p
    return newest


def _is_black_silhouette(path: Path) -> bool:
    """Skip black-only exports mistaken for a color portrait."""
    try:
        from PIL import Image
    except ImportError:
        return False
    im = Image.open(path).convert("RGBA")
    dark = 0
    color = 0
    for r, g, b, a in im.getdata():
        if a < 120:
            continue
        if r < 40 and g < 40 and b < 40:
            dark += 1
        elif max(r, g, b) - min(r, g, b) > 25:
            color += 1
    return dark > 400 and color < 80


def _find_logo_source() -> Path | None:
    """Project assets first — prefer logo.png / logo_2*.png with original colors."""
    for folder in _search_dirs():
        if not folder.is_dir():
            continue
        for name in LOGO_SOURCES:
            p = folder / name
            if p.is_file():
                return p
        for pattern in ("logo_2*.png", "creator_logo*.png"):
            hit = _newest_glob_in_folder(folder, pattern)
            if hit:
                return hit
    return None


def _find_creator_source() -> Path | None:
    """Prefer creator.png or full-color MOHAMMAD_FAIZAN_KHAN*.png (not black silhouettes)."""
    for folder in _search_dirs():
        if not folder.is_dir():
            continue
        for name in CREATOR_SOURCES:
            p = folder / name
            if p.is_file() and not _is_black_silhouette(p):
                return p
        hit = _newest_glob_in_folder(folder, "MOHAMMAD_FAIZAN_KHAN*.png")
        if hit and not _is_black_silhouette(hit):
            return hit
    return None


def _is_phosphor_tinted(path: Path) -> bool:
    """Detect old green terminal-tinted builds (not original teal/cyan art)."""
    try:
        from PIL import Image
    except ImportError:
        return False
    im = Image.open(path).convert("RGBA")
    phosphor = 0
    natural = 0
    for r, g, b, a in im.getdata():
        if a < 80:
            continue
        if g > 140 and r < 70 and b < 120:
            phosphor += 1
        if (r > 80 and b > 80) or (r > 150 and g > 150):
            natural += 1
    return phosphor > 400 and phosphor > natural


def _built_asset_ok(path: Path, *, min_opaque: int) -> bool:
    if not path.is_file():
        return False
    if _max_alpha(path) < 180:
        return False
    if _opaque_count(path) < min_opaque:
        return False
    if _is_phosphor_tinted(path):
        return False
    return True


def _logo_transparent_from_black(src: Path, dest: Path) -> bool:
    """Teal/colored art on solid black — keep original RGB, drop near-black pixels."""
    try:
        from PIL import Image
    except ImportError:
        return False

    im = Image.open(src).convert("RGBA")
    w, h = im.size
    px = im.load()
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    op = out.load()
    wrote = 0
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a < 12:
                continue
            lum = 0.299 * r + 0.587 * g + 0.114 * b
            chroma = max(r, g, b) - min(r, g, b)
            if lum < 32 and chroma < 28:
                continue
            alpha = int(min(255, a))
            op[x, y] = (r, g, b, alpha)
            wrote += 1
    if wrote < 80:
        return False
    dest.parent.mkdir(parents=True, exist_ok=True)
    out.save(dest, "PNG")
    return True


def _opaque_count(path: Path) -> int:
    try:
        from PIL import Image
    except ImportError:
        return 0
    im = Image.open(path).convert("RGBA")
    return sum(1 for _r, _g, _b, a in im.getdata() if a > 20)


def _max_alpha(path: Path) -> int:
    try:
        from PIL import Image
    except ImportError:
        return 0
    im = Image.open(path).convert("RGBA")
    return max((a for _r, _g, _b, a in im.getdata()), default=0)


def _resize_rgba(im, max_side: int = 640):
    try:
        from PIL import Image
    except ImportError:
        return im
    w, h = im.size
    if max(w, h) <= max_side:
        return im
    scale = max_side / max(w, h)
    nw, nh = max(1, int(w * scale)), max(1, int(h * scale))
    return im.resize((nw, nh), Image.Resampling.LANCZOS)


def _ensure_transparent_original(
    src: Path,
    dest: Path,
    *,
    min_opaque: int = 80,
) -> None:
    """Original colors on transparent PNG; never write an invisible asset."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        from PIL import Image
    except ImportError:
        _safe_copy(src, dest)
        return

    for processor in (_logo_transparent_from_black,):
        if processor(src, dest) and _opaque_count(dest) >= min_opaque and _max_alpha(dest) >= 64:
            im = Image.open(dest).convert("RGBA")
            _resize_rgba(im, 640).save(dest, "PNG")
            if _opaque_count(dest) >= min_opaque and _max_alpha(dest) >= 64:
                return

    if _preserve_original_colors(src, dest, creator=min_opaque >= 500):
        if _opaque_count(dest) >= min_opaque and _max_alpha(dest) >= 64:
            im = Image.open(dest).convert("RGBA")
            _resize_rgba(im, 640).save(dest, "PNG")
            if _opaque_count(dest) >= min_opaque and _max_alpha(dest) >= 64:
                return

    im = Image.open(src).convert("RGBA")
    w, h = im.size
    px = im.load()
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    op = out.load()
    wrote = 0
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a < 8:
                continue
            if r + g + b < 30:
                continue
            op[x, y] = (r, g, b, int(min(255, a)))
            wrote += 1
    if wrote >= min_opaque:
        _resize_rgba(out, 640).save(dest, "PNG")
        if _opaque_count(dest) >= min_opaque and _max_alpha(dest) >= 64:
            return

    _safe_copy(src, dest)


def _corner_bg_lum(px, w: int, h: int) -> float:
    pts = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1), (w // 2, 0), (w // 2, h - 1)]
    total = 0.0
    n = 0
    for x, y in pts:
        r, g, b, a = px[x, y]
        if a < 10:
            continue
        total += 0.299 * r + 0.587 * g + 0.114 * b
        n += 1
    return total / n if n else 128.0


def _to_black_transparent(
    src: Path,
    dest: Path,
    *,
    creator: bool = False,
) -> bool:
    """Drop background; render content as black ink on transparent PNG."""
    try:
        from PIL import Image
    except ImportError:
        return False

    im = Image.open(src).convert("RGBA")
    w, h = im.size
    px = im.load()
    bg_lum = _corner_bg_lum(px, w, h) if not creator else 240.0
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    op = out.load()
    wrote = 0
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a < 12:
                continue
            lum = 0.299 * r + 0.587 * g + 0.114 * b
            chroma = max(r, g, b) - min(r, g, b)
            if creator:
                if lum >= 238 and chroma < 45:
                    continue
                strength = (1.0 - lum / 255.0) * 0.35 + (lum / 255.0) * 0.85
                strength *= a / 255.0
                alpha = int(255 * min(1.0, strength))
            else:
                contrast = abs(lum - bg_lum)
                if contrast < 24:
                    continue
                strength = min(1.0, contrast / 110.0) * (a / 255.0)
                alpha = int(255 * min(1.0, strength * 1.15))
            if alpha < 16:
                continue
            op[x, y] = (0, 0, 0, alpha)
            wrote += 1
    min_wrote = 500 if creator else 80
    if wrote < min_wrote:
        return False
    dest.parent.mkdir(parents=True, exist_ok=True)
    out.save(dest, "PNG")
    return True


def _preserve_original_colors(
    src: Path,
    dest: Path,
    *,
    creator: bool = False,
) -> bool:
    """Drop light/neutral background; keep original pixel colors (no theme tint)."""
    try:
        from PIL import Image
    except ImportError:
        return False

    im = Image.open(src).convert("RGBA")
    w, h = im.size
    px = im.load()
    bg_lum = _corner_bg_lum(px, w, h) if not creator else 240.0
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    op = out.load()
    wrote = 0
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a < 12:
                continue
            lum = 0.299 * r + 0.587 * g + 0.114 * b
            chroma = max(r, g, b) - min(r, g, b)
            if creator:
                if lum >= 238 and chroma < 45:
                    continue
                alpha = int(min(255, a))
            else:
                contrast = abs(lum - bg_lum)
                if contrast < 18:
                    continue
                alpha = int(min(255, max(200, a)))
            if alpha < 16:
                continue
            op[x, y] = (r, g, b, alpha)
            wrote += 1
    min_wrote = 500 if creator else 80
    if wrote < min_wrote:
        return False
    dest.parent.mkdir(parents=True, exist_ok=True)
    out.save(dest, "PNG")
    return True


def _logo_transparent(
    src: Path,
    dest: Path,
    *,
    phosphor: bool = True,
    ink: tuple[int, int, int] | None = None,
) -> bool:
    """Signature/logo: keep pixels that contrast with corner background."""
    try:
        from PIL import Image
    except ImportError:
        return False

    im = Image.open(src).convert("RGBA")
    pad = 12
    w, h = im.size
    px = im.load()
    bg_lum = _corner_bg_lum(px, w, h)
    out = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    op = out.load()
    wrote = 0
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a < 12:
                continue
            lum = 0.299 * r + 0.587 * g + 0.114 * b
            contrast = abs(lum - bg_lum)
            if contrast < 28:
                continue
            strength = min(1.0, contrast / 110.0) * (a / 255.0)
            if strength < 0.06:
                continue
            if ink is not None:
                rgb = _ink_rgb(ink, strength)
            elif phosphor:
                rgb = _phosphor_rgb(strength)
            else:
                rgb = _mono_rgb(strength)
            alpha = int(255 * min(1.0, strength * 1.15))
            if alpha < 12:
                continue
            op[x + pad, y + pad] = (*rgb, alpha)
            wrote += 1
    if wrote < 80:
        return False
    dest.parent.mkdir(parents=True, exist_ok=True)
    out.save(dest, "PNG")
    return True


def _creator_transparent(
    src: Path,
    dest: Path,
    *,
    phosphor: bool = True,
    ink: tuple[int, int, int] | None = None,
) -> bool:
    """Portrait: drop bright neutral background; tint face/body for terminal theme."""
    try:
        from PIL import Image, ImageEnhance
    except ImportError:
        return False

    im = Image.open(src).convert("RGBA")
    im = ImageEnhance.Contrast(im).enhance(1.2)
    w, h = im.size
    px = im.load()
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    op = out.load()
    wrote = 0
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a < 16:
                continue
            lum = 0.299 * r + 0.587 * g + 0.114 * b
            chroma = max(r, g, b) - min(r, g, b)
            if lum >= 238 and chroma < 40:
                continue
            strength = 0.25 + 0.75 * (lum / 255.0)
            strength *= a / 255.0
            if strength < 0.08:
                continue
            if ink is not None:
                rgb = _ink_rgb(ink, strength)
            elif phosphor:
                rgb = _phosphor_rgb(strength)
            else:
                rgb = _mono_rgb(strength)
            alpha = int(255 * min(1.0, strength))
            if alpha < 16:
                continue
            op[x, y] = (*rgb, alpha)
            wrote += 1
    if wrote < 500:
        return False
    dest.parent.mkdir(parents=True, exist_ok=True)
    out.save(dest, "PNG")
    return True


def _build_variant(
    src: Path,
    dest: Path,
    *,
    phosphor: bool,
    creator: bool = False,
    ink: tuple[int, int, int] | None = None,
) -> None:
    if dest.resolve() == src.resolve():
        return
    processor = _creator_transparent if creator else _logo_transparent
    min_opaque = 500 if creator else 80
    if processor(src, dest, phosphor=phosphor, ink=ink) and _opaque_count(dest) >= min_opaque:
        return
    _safe_copy(src, dest)


def _procedural_logo(dest: Path, ink: tuple[int, int, int]) -> bool:
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        return False
    w, h = 300, 110
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(im)
    font = None
    for path in (
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/Library/Fonts/Arial Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ):
        try:
            font = ImageFont.truetype(path, 72)
            break
        except OSError:
            continue
    if font is None:
        font = ImageFont.load_default()
    text = "MFK"
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    draw.text(((w - tw) // 2, (h - th) // 2), text, font=font, fill=(*ink, 255))
    dest.parent.mkdir(parents=True, exist_ok=True)
    im.save(dest, "PNG")
    return dest.is_file()


def _procedural_creator(dest: Path, ink: tuple[int, int, int]) -> bool:
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        return False
    size = 240
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(im)
    fill = (*ink, 255)
    draw.ellipse((72, 36, 168, 132), fill=fill)
    draw.ellipse((48, 118, 192, 220), fill=(*_ink_rgb(ink, 0.85), 240))
    dest.parent.mkdir(parents=True, exist_ok=True)
    im.save(dest, "PNG")
    return dest.is_file()


def _ensure_asset(
    dest: Path,
    src: Path | None,
    *,
    phosphor: bool,
    creator: bool,
    ink: tuple[int, int, int] | None = None,
    procedural_ink: tuple[int, int, int] | None = None,
) -> None:
    if src:
        _build_variant(src, dest, phosphor=phosphor, creator=creator, ink=ink)
        if dest.is_file() and _opaque_count(dest) >= (500 if creator else 80):
            return
    if procedural_ink is not None:
        fn = _procedural_creator if creator else _procedural_logo
        if fn(dest, procedural_ink):
            return
    if src and src.is_file():
        _safe_copy(src, dest)


def _publish_exact(src: Path, dest: Path) -> None:
    """Byte-for-byte copy — no resize, no transparency pass, no color change."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    _safe_copy(src, dest)


def _is_near_black_bg(r: int, g: int, b: int, a: int) -> bool:
    if a < 12:
        return True
    lum = 0.299 * r + 0.587 * g + 0.114 * b
    chroma = max(r, g, b) - min(r, g, b)
    return lum < 42 and chroma < 32


def _publish_white_background(src: Path, dest: Path) -> bool:
    """Keep original teal art RGB; replace near-black background with white only."""
    try:
        from PIL import Image
    except ImportError:
        _safe_copy(src, dest)
        return False

    im = Image.open(src).convert("RGBA")
    w, h = im.size
    px = im.load()
    out = Image.new("RGBA", (w, h), (255, 255, 255, 255))
    op = out.load()
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if _is_near_black_bg(r, g, b, a):
                op[x, y] = (255, 255, 255, 255)
            else:
                op[x, y] = (r, g, b, 255)
    dest.parent.mkdir(parents=True, exist_ok=True)
    out.save(dest, "PNG")
    return True


def _publish_for_website(src: Path, dest: Path) -> None:
    """White background + original foreground colors (no filters)."""
    if not _publish_white_background(src, dest):
        _publish_exact(src, dest)


def install_web_assets() -> dict[str, str]:
    """Publish logo + creator to web/assets/ (white background, original colors)."""
    ASSETS.mkdir(parents=True, exist_ok=True)
    logo = ASSETS / LOGO_NAME
    logo_mono = ASSETS / LOGO_MONO_NAME
    logo_display = ASSETS / LOGO_DISPLAY_NAME
    creator = ASSETS / CREATOR_NAME
    creator_mono = ASSETS / CREATOR_MONO_NAME
    creator_display = ASSETS / CREATOR_DISPLAY_NAME

    project_assets = WEB.parent / "assets"

    logo_src = _find_logo_source()
    if logo_src:
        _publish_for_website(logo_src, logo)
        if project_assets.is_dir():
            _publish_for_website(logo_src, project_assets / LOGO_NAME)
    if logo.is_file():
        for variant in (logo_mono, logo_display):
            _publish_exact(logo, variant)

    creator_src = _find_creator_source()
    if creator_src:
        _publish_for_website(creator_src, creator)
        if project_assets.is_dir():
            _publish_for_website(creator_src, project_assets / CREATOR_NAME)
    if creator.is_file():
        for variant in (creator_mono, creator_display):
            _publish_exact(creator, variant)

    return {
        "logo": str(logo) if logo.is_file() else "missing",
        "logo_mono": str(logo_mono) if logo_mono.is_file() else "missing",
        "logo_display": str(logo_display) if logo_display.is_file() else "missing",
        "creator": str(creator) if creator.is_file() else "missing",
        "creator_mono": str(creator_mono) if creator_mono.is_file() else "missing",
        "creator_display": str(creator_display) if creator_display.is_file() else "missing",
    }
