from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from io import BytesIO
from pathlib import Path
from typing import Dict, Optional, Tuple

import qrcode
from PIL import Image, ImageDraw, ImageFont

from .style_utils import add_rounded_corners
from .url_shortener import create_social_shortlink, get_full_url


RGB = Tuple[int, int, int]


@dataclass(frozen=True)
class PlatformSpec:
    """Defines brand-specific colors, text, and logo for each social platform."""
    colors: Tuple[RGB, ...]
    scan_text: str
    logo_filename: str


class SocialQRGenerator:
    """
    High-performance social QR generator with:
      • caching of QR matrices and rendered bitmaps,
      • optional centered platform logo,
      • gradient coloring for Instagram,
      • bottom text section (name, link, tagline),
      • optional rounded corners for the final output.
    """

    PLATFORM_SPECS: Dict[str, PlatformSpec] = {
        "facebook": PlatformSpec(
            colors=((63, 92, 153),),
            scan_text="Scan to follow on Facebook",
            logo_filename="facebook_logo.png",
        ),
        "instagram": PlatformSpec(
            colors=(
                (64, 93, 230),
                (88, 81, 219),
                (131, 58, 180),
                (193, 53, 132),
                (225, 48, 108),
            ),
            scan_text="Scan to follow on Instagram",
            logo_filename="instagram_logo.png",
        ),
        "linkedin": PlatformSpec(
            colors=((34, 89, 130),),
            scan_text="Scan to connect on LinkedIn",
            logo_filename="linkedin_logo.png",
        ),
    }

    def __init__(self) -> None:
        """Initialize fonts, color palette, and logo directory."""
        project_root = Path(__file__).resolve().parents[2]
        self._logos_root = project_root / "static" / "images" / "logos"

        # Color palette
        self._white: RGB = (255, 255, 255)
        self._text_primary: RGB = (51, 51, 51)
        self._text_secondary: RGB = (102, 102, 102)

        # Font setup (fallback to default if arial not available)
        try:
            self._font_large = ImageFont.truetype("arialbd.ttf", 24)
            self._font_medium = ImageFont.truetype("arial.ttf", 16)
            self._font_small = ImageFont.truetype("arial.ttf", 14)
        except Exception:
            self._font_large = self._font_medium = self._font_small = ImageFont.load_default()

        # Resampling constant for Pillow 9/10 compatibility
        self._resample = getattr(Image, "Resampling", Image).LANCZOS  # type: ignore[attr-defined]

    # ---------- Public API ----------

    def generate_social_qr(
        self,
        platform: str,
        profile_url: str,
        display_name: str,
        use_shortlink: bool = True,
        rounded_corners: bool = False,
        corner_radius: int = 40,
        qr_size: int = 300,
        colorful: bool = True,
    ) -> Tuple[Image.Image, Optional[str], str]:
        """
        Main entrypoint.

        Returns:
            tuple: (final PIL.Image, shortlink or None, full_url)
        """
        platform = platform.strip().lower()
        spec = self._get_spec(platform)

        # Normalize and resolve the full URL / shortlink
        if use_shortlink:
            shortlink = create_social_shortlink(profile_url, platform)
            qr_data = get_full_url(shortlink, platform)
        else:
            shortlink = None
            qr_data = get_full_url(profile_url, platform)

        # 1) Generate the base QR code
        if colorful:
            if platform == "instagram" and len(spec.colors) > 1:
                png_bytes = self._make_gradient_qr_png_bytes(qr_data, spec.colors, qr_size)
            else:
                png_bytes = self._make_solid_qr_png_bytes(qr_data, spec.colors[0], qr_size)
        else:
            # Pure black-and-white QR
            png_bytes = self._make_solid_qr_png_bytes(qr_data, (0, 0, 0), qr_size)

        qr_img = Image.open(BytesIO(png_bytes)).convert("RGBA")

        # 2) Overlay central logo (skip in mono mode)
        qr_with_logo = qr_img if not colorful else self._overlay_logo_center(qr_img, platform, qr_size)

        # 3) Add bottom text and color bar (monochrome = neutral gray)
        bar_color = self._primary_color(spec) if colorful else (0, 0, 0)
        text_color = self._text_primary if colorful else (40, 40, 40)

        final_img = self._add_text_section(
            qr_with_logo.convert("RGB"),
            platform_color=bar_color,
            display_name=display_name,
            shortlink=shortlink,
            scan_text=spec.scan_text if colorful else "Scan QR code",
            qr_size=qr_size,
            text_color=text_color,
        )

        # 4) Optional rounded corners
        if rounded_corners and corner_radius > 0:
            final_img = add_rounded_corners(final_img, corner_radius)

        return final_img, shortlink, qr_data

    # ---------- QR rendering & caching ----------

    @staticmethod
    @lru_cache(maxsize=512)
    def _qr_matrix(data: str) -> Tuple[Tuple[bool, ...], ...]:
        """Builds a QR matrix and caches it as an immutable tuple."""
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        matrix = qr.get_matrix()
        return tuple(tuple(bool(c) for c in row) for row in matrix)

    @staticmethod
    def _png_from_image(img: Image.Image) -> bytes:
        """Converts a PIL image to raw PNG bytes."""
        buf = BytesIO()
        img.save(buf, "PNG")
        return buf.getvalue()

    @classmethod
    @lru_cache(maxsize=512)
    def _make_solid_qr_png_bytes(cls, data: str, color: RGB, size: int) -> bytes:
        """Creates a solid-color QR image and returns PNG bytes (cached)."""
        from qrcode.image.styledpil import StyledPilImage
        from qrcode.image.styles.colormasks import SolidFillColorMask

        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)

        qr_img = qr.make_image(
            image_factory=StyledPilImage,
            color_mask=SolidFillColorMask(back_color=(255, 255, 255), front_color=color),
        ).convert("RGBA")

        qr_img = qr_img.resize((size, size), getattr(Image, "Resampling", Image).LANCZOS)  # type: ignore[attr-defined]
        return cls._png_from_image(qr_img)

    @classmethod
    @lru_cache(maxsize=512)
    def _make_gradient_qr_png_bytes(cls, data: str, colors: Tuple[RGB, ...], size: int) -> bytes:
        """
        Draws a QR code manually using a module matrix with a cyclic gradient (Instagram-style).
        """
        matrix = cls._qr_matrix(data)
        box_size = 10
        border = 4

        width_modules = len(matrix)
        width_px = width_modules * box_size + 2 * border * box_size

        img = Image.new("RGBA", (width_px, width_px), (255, 255, 255, 255))
        draw = ImageDraw.Draw(img)

        num_colors = len(colors)
        for y, row in enumerate(matrix):
            for x, module in enumerate(row):
                if not module:
                    continue
                color = colors[(x + y) % num_colors]
                x_pos = x * box_size + border * box_size
                y_pos = y * box_size + border * box_size
                draw.rectangle([x_pos, y_pos, x_pos + box_size, y_pos + box_size], fill=color)

        img = img.resize((size, size), getattr(Image, "Resampling", Image).LANCZOS)  # type: ignore[attr-defined]
        return cls._png_from_image(img)

    # ---------- Composition: logo & text ----------

    def _overlay_logo_center(self, qr_img: Image.Image, platform: str, qr_size: int) -> Image.Image:
        """Places a centered logo if available. Silently skips missing or invalid files."""
        logo_path = self._logos_root / self._logo_filename(platform)
        if not logo_path.exists():
            return qr_img

        try:
            logo = Image.open(logo_path).convert("RGBA")
        except Exception:
            return qr_img

        logo_size = max(32, qr_size // 5)
        logo = logo.resize((logo_size, logo_size), self._resample)

        pad = max(8, logo_size // 8)
        bg_size = (logo_size + pad * 2, logo_size + pad * 2)
        bg = Image.new("RGBA", bg_size, (255, 255, 255, 255))
        bg.paste(logo, (pad, pad), logo)

        result = qr_img.copy()
        pos = ((qr_size - bg_size[0]) // 2, (qr_size - bg_size[1]) // 2)
        result.alpha_composite(bg, dest=pos)
        return result

    def _add_text_section(
        self,
        qr_img_rgb: Image.Image,
        platform_color: RGB,
        display_name: str,
        shortlink: Optional[str],
        scan_text: str,
        qr_size: int,
        text_color: RGB = (51, 51, 51),
    ) -> Image.Image:
        """
        Appends a text section below the QR:
          • display_name (platform color)
          • shortlink and/or scan_text
          • bottom color bar
        """
        text_height = 120
        total_h = qr_size + text_height

        canvas = Image.new("RGB", (qr_size, total_h), self._white)
        canvas.paste(qr_img_rgb, (0, 0))

        draw = ImageDraw.Draw(canvas)

        # Display name
        name_w = draw.textlength(display_name, font=self._font_large)
        name_x = int((qr_size - name_w) / 2)
        draw.text((name_x, qr_size + 15), display_name, fill=platform_color, font=self._font_large)

        # Shortlink and scan text
        if shortlink:
            sl_w = draw.textlength(shortlink, font=self._font_medium)
            sl_x = int((qr_size - sl_w) / 2)
            draw.text((sl_x, qr_size + 50), shortlink, fill=text_color, font=self._font_medium)

            sc_w = draw.textlength(scan_text, font=self._font_small)
            sc_x = int((qr_size - sc_w) / 2)
            draw.text((sc_x, qr_size + 80), scan_text, fill=self._text_secondary, font=self._font_small)
        else:
            sc_w = draw.textlength(scan_text, font=self._font_small)
            sc_x = int((qr_size - sc_w) / 2)
            draw.text((sc_x, qr_size + 60), scan_text, fill=self._text_secondary, font=self._font_small)

        # Bottom color bar
        bar_h = 6
        draw.rectangle([0, total_h - bar_h, qr_size, total_h], fill=platform_color)

        return canvas

    # ---------- Utilities ----------

    def _get_spec(self, platform: str) -> PlatformSpec:
        """Fetch platform spec or fallback to black-and-white defaults."""
        if platform not in self.PLATFORM_SPECS:
            return PlatformSpec(colors=((0, 0, 0),), scan_text="Scan QR code", logo_filename="")
        return self.PLATFORM_SPECS[platform]

    def _primary_color(self, spec: PlatformSpec) -> RGB:
        """Return the primary color of the given spec."""
        return spec.colors[0] if spec.colors else (0, 0, 0)

    def _logo_filename(self, platform: str) -> str:
        """Resolve platform logo filename (may be empty)."""
        spec = self._get_spec(platform)
        return spec.logo_filename or ""
