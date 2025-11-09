#!/usr/bin/env python3
"""
Fetch social / utility SVG logos from simpleicons.org, normalize them to
use `fill="currentColor"` and add an inline default color style `color: #000`
so they render black by default but can be recolored via CSS.

Usage:
    .venv\Scripts\python tools\fetch_logos.py

Output directory (created if missing):
    app/static/images/logos/
"""

import os
import re
import sys
from pathlib import Path

try:
    import requests
except ImportError:
    print("Please install requests first: pip install requests")
    sys.exit(1)


# Map local filename -> simpleicons slug (urls are https://simpleicons.org/icons/<slug>.svg)
ICONS = {
    "facebook.svg": "facebook",
    "instagram.svg": "instagram",
    "linkedin.svg": "linkedin",
    "youtube.svg": "youtube",
    "tiktok.svg": "tiktok",
    "x.svg": "x",
    "appstore.svg": "appstore",      # fixed
    "googleplay.svg": "googleplay",
    "bitcoin.svg": "bitcoin",
    "crypto.svg": "ethereum",        # good fallback
    "linkedin.svg": "utensils",    # fallback from FontAwesome-like
}


OUT_DIR = Path("app/static/images/logos")
OUT_DIR.mkdir(parents=True, exist_ok=True)

SIMPLE_ICONS_BASE = "https://simpleicons.org/icons"


def fetch_svg(slug: str) -> str | None:
    url = f"{SIMPLE_ICONS_BASE}/{slug}.svg"
    try:
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            return r.text
        else:
            print(f"Warning: {url} returned status {r.status_code}")
            return None
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None


def normalize_svg(svg_text: str, default_color: str = "#000000") -> str:
    """
    1. Replace any fill="#...." or fill="rgb(...)" on <path> / <g> with fill="currentColor".
    2. Ensure the <svg ...> tag contains style="color: <default_color>" so the icon renders black by default.
    3. Remove width/height attributes (optional) to keep SVG scalable; keep viewBox.
    """
    # 1) Convert fills to currentColor (avoid changing gradient defs)
    # Replace fill="..." in path/g elements; be conservative: only replace hex/rgb values
    svg_text = re.sub(r'fill="(#(?:[0-9a-fA-F]{3,8})|rgb\([^\)]*\))"', 'fill="currentColor"', svg_text)

    # 2) Ensure svg tag has style="color: <default_color>"
    # If svg tag already has a style, append/replace color
    def _add_color_to_svg_tag(match):
        tag = match.group(0)
        if "style=" in tag:
            # replace existing color:... if present, otherwise append
            if re.search(r'color\s*:', tag):
                tag = re.sub(r'color\s*:\s*[^;"]+;?', f'color:{default_color};', tag)
            else:
                # insert style attribute content (before closing '>')
                tag = tag.rstrip('>') + f' style="color:{default_color};">'
        else:
            # add style attribute right before >
            tag = tag.rstrip('>') + f' style="color:{default_color};">'
        # Remove explicit width/height to keep responsive/scalable SVG (optional)
        tag = re.sub(r'\s(width|height)="[^"]+"', '', tag)
        return tag

    svg_text = re.sub(r'<svg[^>]*>', _add_color_to_svg_tag, svg_text, count=1)

    return svg_text


def save_svg(filename: Path, svg_text: str):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(svg_text)
    print(f"Wrote: {filename}")


def main():
    print("Fetching icons to", OUT_DIR.resolve())
    for fn, slug in ICONS.items():
        svg = fetch_svg(slug)
        if svg:
            normalized = normalize_svg(svg, default_color="#000000")
            save_svg(OUT_DIR / fn, normalized)
        else:
            print(f"Skipping {fn} (slug={slug} not found). You may provide a custom SVG manually.")
    print("Done.")


if __name__ == "__main__":
    main()
