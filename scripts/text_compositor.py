#!/usr/bin/env python3
"""
Text Compositor — Overlay styled text onto sticker images using Pillow.

Designed to replace SDXL text generation with clean, reliable post-processing.
Renders bold display text with outlines, shadows, and configurable styling
to match the chubby-mochi benchmark sticker packs.

Usage as module:
    from text_compositor import TextCompositor
    compositor = TextCompositor()
    result = compositor.composite_text(image, text_config, defaults)

Usage standalone (preview mode):
    python text_compositor.py --image input.png --text "LOL" --color "#FF3333"
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# Font search paths (repo-relative)
# ---------------------------------------------------------------------------
_SCRIPT_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _SCRIPT_DIR.parent
_FONTS_DIR = _REPO_ROOT / "fonts"

# Ordered preference: best match for benchmark style first
_FONT_FALLBACK_ORDER = [
    "FredokaOne-Regular.ttf",  # Thick rounded caps — closest to benchmark
    "ArialRoundedBold.ttf",  # Clean rounded bold — good backup
    "MarkerFelt.ttc",  # Hand-drawn feel — last resort
]

# ---------------------------------------------------------------------------
# Default text style (matches chubby-mochi benchmark analysis)
# ---------------------------------------------------------------------------
DEFAULT_TEXT_STYLE: dict[str, Any] = {
    "font": "FredokaOne-Regular.ttf",
    "font_size": 72,
    "color": "#FFFFFF",
    "outline_width": 5,
    "outline_color": "#1a1a1a",
    "shadow_offset": [4, 4],
    "shadow_color": "#00000080",
    "position": "top-center",
    "rotation": 0,
    "padding_top": 20,  # px above character for text placement
}


class TextCompositor:
    """Overlay styled text on sticker images using Pillow."""

    def __init__(self, fonts_dir: str | Path | None = None):
        self.fonts_dir = Path(fonts_dir) if fonts_dir else _FONTS_DIR

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def composite_text(
        self,
        image: Image.Image,
        text_config: dict | str,
        defaults: dict | None = None,
    ) -> Image.Image:
        """
        Overlay styled text onto a sticker image.

        Args:
            image: PIL Image (RGBA recommended).
            text_config: Either a plain string ("LOL") or a dict with keys:
                - content (str): The text to render (required).
                - color (str): Fill colour, e.g. "#FF3333".
                - font (str): Font filename in fonts_dir.
                - font_size (int): Size in pixels.
                - outline_width (int): Stroke width.
                - outline_color (str): Stroke colour.
                - shadow_offset (list[int,int]): [dx, dy] pixels.
                - shadow_color (str): Shadow colour with optional alpha.
                - position (str): "top-center", "top-left", "top-right",
                                  "center", "bottom-center", or [x, y].
                - rotation (float): Degrees counter-clockwise.
                - padding_top (int): Extra px gap above content area.
            defaults: Pack-level text_defaults dict. Per-sticker values
                      in *text_config* override these.

        Returns:
            New PIL Image with text composited (original is not modified).
        """
        # Normalise text_config to dict
        if isinstance(text_config, str):
            text_config = {"content": text_config}

        content = text_config.get("content", "")
        if not content:
            return image.copy()

        # Merge: per-sticker overrides > pack defaults > built-in defaults
        style = dict(DEFAULT_TEXT_STYLE)
        if defaults:
            style.update({k: v for k, v in defaults.items() if v is not None})
        style.update(
            {k: v for k, v in text_config.items() if v is not None and k != "content"}
        )

        # Load font
        font = self._load_font(style["font"], style["font_size"])

        # Ensure RGBA
        base = image.convert("RGBA") if image.mode != "RGBA" else image.copy()

        # Render text on a transparent overlay that may be larger than base
        # (to accommodate text above the character)
        text_layer = self._render_text_layer(
            content=content,
            font=font,
            style=style,
            base_size=base.size,
        )

        # Composite
        result = self._composite_layers(base, text_layer, style)
        return result

    # ------------------------------------------------------------------
    # Internal: font loading
    # ------------------------------------------------------------------

    def _load_font(self, font_name: str, size: int) -> ImageFont.FreeTypeFont:
        """Load a font by name from the fonts directory, with fallbacks."""
        # Try exact name first
        font_path = self.fonts_dir / font_name
        if font_path.exists():
            return ImageFont.truetype(str(font_path), size)

        # Try fallback order
        for fallback in _FONT_FALLBACK_ORDER:
            path = self.fonts_dir / fallback
            if path.exists():
                return ImageFont.truetype(str(path), size)

        # System default (ugly but functional)
        return ImageFont.load_default()

    # ------------------------------------------------------------------
    # Internal: text rendering
    # ------------------------------------------------------------------

    def _render_text_layer(
        self,
        content: str,
        font: ImageFont.FreeTypeFont,
        style: dict,
        base_size: tuple[int, int],
    ) -> Image.Image:
        """
        Render text with outline + shadow onto a transparent RGBA layer.

        The layer is sized to fit the base image plus headroom for text.
        """
        outline_w = style.get("outline_width", 0)
        shadow_dx, shadow_dy = style.get("shadow_offset", [0, 0])

        # Measure text bounding box
        # Use a temp draw context just for measuring
        temp_img = Image.new("RGBA", (1, 1))
        temp_draw = ImageDraw.Draw(temp_img)
        bbox = temp_draw.textbbox(
            (0, 0), content, font=font, stroke_width=outline_w, anchor="lt"
        )
        text_w = bbox[2] - bbox[0] + abs(shadow_dx)
        text_h = bbox[3] - bbox[1] + abs(shadow_dy)

        # Auto-scale font if text is wider than image
        base_w, base_h = base_size
        max_text_w = int(base_w * 0.92)  # 92% of image width max
        if text_w > max_text_w and text_w > 0:
            scale_factor = max_text_w / text_w
            new_size = max(12, int(style["font_size"] * scale_factor))
            font = self._load_font(style["font"], new_size)
            bbox = temp_draw.textbbox(
                (0, 0), content, font=font, stroke_width=outline_w, anchor="lt"
            )
            text_w = bbox[2] - bbox[0] + abs(shadow_dx)
            text_h = bbox[3] - bbox[1] + abs(shadow_dy)

        # Create layer same size as base image
        # Text is drawn within the base image bounds
        layer = Image.new("RGBA", base_size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(layer)

        # Calculate position
        padding_top = style.get("padding_top", 20)
        x, y = self._calc_position(
            style.get("position", "top-center"),
            base_size,
            (text_w, text_h),
            padding_top,
        )

        # Parse colours
        fill_color = self._parse_color(style["color"])
        outline_color = self._parse_color(style.get("outline_color", "#000000"))
        shadow_color = self._parse_color(style.get("shadow_color", "#00000080"))

        # 1) Draw shadow
        if shadow_dx or shadow_dy:
            draw.text(
                (x + shadow_dx, y + shadow_dy),
                content,
                font=font,
                fill=shadow_color,
                stroke_width=outline_w,
                stroke_fill=shadow_color,
                anchor="lt",
            )

        # 2) Draw outline + fill
        draw.text(
            (x, y),
            content,
            font=font,
            fill=fill_color,
            stroke_width=outline_w,
            stroke_fill=outline_color,
            anchor="lt",
        )

        # 3) Optional rotation
        rotation = style.get("rotation", 0)
        if rotation:
            layer = self._rotate_text_layer(
                layer, rotation, (x + text_w // 2, y + text_h // 2)
            )

        return layer

    def _calc_position(
        self,
        position: str | list,
        base_size: tuple[int, int],
        text_size: tuple[int, int],
        padding_top: int,
    ) -> tuple[int, int]:
        """Calculate top-left (x, y) for the text based on position spec."""
        base_w, base_h = base_size
        text_w, text_h = text_size

        # Explicit coordinates
        if isinstance(position, (list, tuple)) and len(position) == 2:
            return int(position[0]), int(position[1])

        # Named positions
        cx = (base_w - text_w) // 2  # centred X

        if position == "top-center":
            return cx, padding_top
        elif position == "top-left":
            return padding_top, padding_top
        elif position == "top-right":
            return base_w - text_w - padding_top, padding_top
        elif position == "center":
            return cx, (base_h - text_h) // 2
        elif position == "bottom-center":
            return cx, base_h - text_h - padding_top
        else:
            # Default: top-center
            return cx, padding_top

    @staticmethod
    def _rotate_text_layer(
        layer: Image.Image,
        angle: float,
        center: tuple[int, int],
    ) -> Image.Image:
        """Rotate the text layer around a given centre point."""
        # Pillow rotates around image centre by default; we translate to match
        rotated = layer.rotate(
            angle, resample=Image.BICUBIC, expand=False, center=center
        )
        return rotated

    @staticmethod
    def _parse_color(color_str: str) -> tuple[int, ...]:
        """
        Parse a colour string to an RGBA tuple.

        Supports:
          - "#RRGGBB"        -> (R, G, B, 255)
          - "#RRGGBBAA"      -> (R, G, B, A)
          - "rgb(R, G, B)"   -> (R, G, B, 255)
        """
        if not isinstance(color_str, str):
            return color_str  # Already a tuple

        color_str = color_str.strip()

        if color_str.startswith("#"):
            hex_str = color_str[1:]
            if len(hex_str) == 6:
                r = int(hex_str[0:2], 16)
                g = int(hex_str[2:4], 16)
                b = int(hex_str[4:6], 16)
                return (r, g, b, 255)
            elif len(hex_str) == 8:
                r = int(hex_str[0:2], 16)
                g = int(hex_str[2:4], 16)
                b = int(hex_str[4:6], 16)
                a = int(hex_str[6:8], 16)
                return (r, g, b, a)

        # Fallback: let Pillow handle it
        return color_str

    # ------------------------------------------------------------------
    # Internal: compositing
    # ------------------------------------------------------------------

    @staticmethod
    def _composite_layers(
        base: Image.Image,
        text_layer: Image.Image,
        style: dict,
    ) -> Image.Image:
        """Alpha-composite the text layer onto the base image."""
        result = base.copy()
        result = Image.alpha_composite(result, text_layer)
        return result


# ---------------------------------------------------------------------------
# Convenience function for use from comfyui_generator.py
# ---------------------------------------------------------------------------
_default_compositor: TextCompositor | None = None


def composite_text_on_image(
    image_path: str | Path,
    text_config: dict | str,
    defaults: dict | None = None,
    output_path: str | Path | None = None,
) -> Path:
    """
    High-level helper: load image, composite text, save.

    Args:
        image_path: Path to input image (PNG with transparency recommended).
        text_config: Text configuration (string or dict, see TextCompositor).
        defaults: Pack-level text_defaults.
        output_path: Where to save. Defaults to overwriting input.

    Returns:
        Path to the saved output image.
    """
    global _default_compositor
    if _default_compositor is None:
        _default_compositor = TextCompositor()

    image_path = Path(image_path)
    output_path = Path(output_path) if output_path else image_path

    img = Image.open(image_path).convert("RGBA")
    result = _default_compositor.composite_text(img, text_config, defaults)
    result.save(str(output_path), "PNG")
    return output_path


# ---------------------------------------------------------------------------
# CLI preview mode
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Preview text overlay on a sticker image",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic overlay:
  python text_compositor.py --image sticker.png --text "LOL" --color "#FF3333"

  # Custom styling:
  python text_compositor.py --image sticker.png --text "WHAT?!" \\
      --color "#3366FF" --outline-width 6 --font-size 90

  # Save to different file:
  python text_compositor.py --image sticker.png --text "NOPE" \\
      --output preview.png
""",
    )
    parser.add_argument("--image", required=True, help="Input image path")
    parser.add_argument("--text", required=True, help="Text to overlay")
    parser.add_argument("--color", default="#FFFFFF", help="Text fill colour (hex)")
    parser.add_argument("--outline-color", default="#1a1a1a", help="Outline colour")
    parser.add_argument(
        "--outline-width", type=int, default=5, help="Outline stroke width"
    )
    parser.add_argument("--font-size", type=int, default=72, help="Font size in px")
    parser.add_argument(
        "--font", default="FredokaOne-Regular.ttf", help="Font filename"
    )
    parser.add_argument(
        "--position", default="top-center", help="Position: top-center, center, etc."
    )
    parser.add_argument("--rotation", type=float, default=0, help="Rotation in degrees")
    parser.add_argument(
        "--output", default=None, help="Output path (default: <input>_text.png)"
    )
    parser.add_argument("--shadow-dx", type=int, default=4, help="Shadow X offset")
    parser.add_argument("--shadow-dy", type=int, default=4, help="Shadow Y offset")
    parser.add_argument("--shadow-color", default="#00000080", help="Shadow colour")
    args = parser.parse_args()

    input_path = Path(args.image)
    if not input_path.exists():
        print(f"ERROR: Image not found: {input_path}")
        exit(1)

    output = args.output or str(
        input_path.with_name(f"{input_path.stem}_text{input_path.suffix}")
    )

    text_config = {
        "content": args.text,
        "color": args.color,
        "font": args.font,
        "font_size": args.font_size,
        "outline_width": args.outline_width,
        "outline_color": args.outline_color,
        "shadow_offset": [args.shadow_dx, args.shadow_dy],
        "shadow_color": args.shadow_color,
        "position": args.position,
        "rotation": args.rotation,
    }

    result_path = composite_text_on_image(input_path, text_config, output_path=output)
    print(f"Saved: {result_path}")
    print(f"  Text: {args.text}")
    print(f"  Color: {args.color}")
    print(f"  Font: {args.font} @ {args.font_size}px")
    print(f"  Outline: {args.outline_width}px {args.outline_color}")
    print(f"  Shadow: [{args.shadow_dx}, {args.shadow_dy}] {args.shadow_color}")
    print(f"  Position: {args.position}")
