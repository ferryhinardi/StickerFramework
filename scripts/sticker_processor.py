#!/usr/bin/env python3
"""
Sticker Processor - Image processing pipeline for multi-platform sticker export.

Handles: background removal, white outline addition, color normalization,
resizing, format conversion, and size optimization.

Usage:
    # Process a directory of raw images:
    python sticker_processor.py pack01_emotions_v1/raw

    # Or use as a module:
    from sticker_processor import StickerProcessor
    processor = StickerProcessor()
    processor.process_batch("raw/", "final/", ["whatsapp", "telegram"])
"""

import io
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont


class StickerProcessor:
    """Process raw AI-generated images into platform-ready stickers."""

    # Platform specifications
    SPECS = {
        "whatsapp": {
            "size": (512, 512),
            "format": "WEBP",
            "max_kb": 100,
            "ext": ".webp",
        },
        "whatsapp_tray": {
            "size": (96, 96),
            "format": "WEBP",
            "max_kb": 50,
            "ext": ".webp",
        },
        "telegram": {
            "size": (512, 512),
            "format": "WEBP",
            "max_kb": 256,
            "ext": ".webp",
        },
        "imessage_small": {
            "size": (300, 300),
            "format": "PNG",
            "max_kb": 500,
            "ext": ".png",
        },
        "imessage_medium": {
            "size": (408, 408),
            "format": "PNG",
            "max_kb": 500,
            "ext": ".png",
        },
        "imessage_large": {
            "size": (618, 618),
            "format": "PNG",
            "max_kb": 500,
            "ext": ".png",
        },
        "line": {
            "size": (370, 320),
            "format": "PNG",
            "max_kb": 1000,
            "ext": ".png",
        },
        "line_main": {
            "size": (240, 240),
            "format": "PNG",
            "max_kb": 1000,
            "ext": ".png",
        },
        "line_tab": {
            "size": (96, 74),
            "format": "PNG",
            "max_kb": 1000,
            "ext": ".png",
        },
        # LINE Emoji — 180x180 PNG, transparent bg, no white outline
        "line_emoji": {
            "size": (180, 180),
            "format": "PNG",
            "max_kb": 1000,
            "ext": ".png",
            "outline": False,
            "fill_ratio": 0.95,
        },
        "line_emoji_tab": {
            "size": (96, 74),
            "format": "PNG",
            "max_kb": 1000,
            "ext": ".png",
            "outline": False,
            "fill_ratio": 0.90,
        },
        "print_etsy": {
            "size": (2048, 2048),
            "format": "PNG",
            "max_kb": None,
            "ext": ".png",
        },
        # Phase 2: Telegram animated (Lottie/TGS) and video (WebM VP9) stickers
        "telegram_animated": {
            "size": (512, 512),
            "format": "TGS",  # Lottie JSON gzipped
            "max_kb": 64,
            "ext": ".tgs",
        },
        "telegram_video": {
            "size": (512, 512),
            "format": "WEBM",  # VP9, no audio
            "max_kb": 256,
            "ext": ".webm",
        },
        # Phase 3: WhatsApp native app (stricter limits than Sticker.ly)
        "whatsapp_native": {
            "size": (512, 512),
            "format": "WEBP",
            "max_kb": 100,
            "ext": ".webp",
        },
        "whatsapp_native_tray": {
            "size": (96, 96),
            "format": "PNG",  # WhatsApp native app uses PNG tray
            "max_kb": 50,
            "ext": ".png",
        },
    }

    def __init__(self, outline_color: str = "white", outline_width: int = 12):
        """
        Args:
            outline_color: Color for the die-cut outline border
            outline_width: Pixel width of the outline (before final resize)
        """
        self.outline_color = outline_color
        self.outline_width = outline_width

    def remove_background(self, input_path: str) -> Image.Image:
        """
        Remove white background using flood-fill from corners.

        This approach reliably removes connected white backgrounds without
        erasing text, fine details, or decorative elements — unlike AI-based
        models (rembg/U2-Net) which can incorrectly classify text and small
        elements as background.

        Returns RGBA image with transparent background.
        """
        import numpy as np
        from scipy.ndimage import label as scipy_label

        img = Image.open(input_path).convert("RGB")
        arr = np.array(img)
        h, w = arr.shape[:2]

        # Mark pixels that are white enough to be background candidates
        # Threshold 225 handles off-white/cream backgrounds from some DALL-E outputs
        white_threshold = 225
        white_mask = np.all(arr > white_threshold, axis=2)

        # Label connected regions using 8-connectivity (diagonal gaps included)
        structure = np.ones((3, 3), dtype=int)
        labeled, _ = scipy_label(white_mask, structure=structure)

        # Sample a 5x5 patch at each corner — more robust than a single pixel
        patch = 5
        corner_labels = set()
        for cy_slice, cx_slice in [
            (slice(0, patch), slice(0, patch)),
            (slice(0, patch), slice(w - patch, w)),
            (slice(h - patch, h), slice(0, patch)),
            (slice(h - patch, h), slice(w - patch, w)),
        ]:
            for lbl in np.unique(labeled[cy_slice, cx_slice]):
                if lbl > 0:
                    corner_labels.add(lbl)

        # Build background mask: white pixels connected to corners
        bg_mask = np.zeros((h, w), dtype=bool)
        for lbl in corner_labels:
            bg_mask |= labeled == lbl

        # Compose RGBA: background pixels → alpha=0, content → alpha=255
        result = np.zeros((h, w, 4), dtype=np.uint8)
        result[:, :, :3] = arr
        result[:, :, 3] = np.where(bg_mask, 0, 255)

        return Image.fromarray(result)  # dtype uint8 + 4 channels → RGBA

    def add_white_outline(
        self, img: Image.Image, width: int | None = None
    ) -> Image.Image:
        """
        Add a die-cut style white outline around the character.
        Uses alpha channel dilation (MaxFilter) technique.

        This is a key post-processing step that also strengthens
        copyright claims on AI-generated art.
        """
        width = width or self.outline_width
        if width <= 0:
            return img

        # Extract alpha channel
        alpha = img.split()[3]

        # Dilate alpha to create outline mask
        # Apply MaxFilter repeatedly for thicker outlines
        outline_mask = alpha.copy()
        iterations = max(1, width // 2)
        for _ in range(iterations):
            outline_mask = outline_mask.filter(ImageFilter.MaxFilter(5))

        # Create white outline layer
        outline_layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
        white_img = Image.new("RGBA", img.size, (255, 255, 255, 255))
        outline_layer = Image.composite(white_img, outline_layer, outline_mask)

        # Paste original character on top of the white outline
        outline_layer.paste(img, (0, 0), img)
        return outline_layer

    # -------------------------------------------------------------------------
    # Font resolution for text overlay
    # -------------------------------------------------------------------------
    # Bundled fonts ship in the repo's fonts/ directory for portability.
    # Fallback chain: bundled → system → PIL default bitmap font.
    _FONTS_DIR = Path(__file__).resolve().parent.parent / "fonts"
    _FONT_PATHS = {
        "bold": [
            _FONTS_DIR
            / "FredokaOne-Regular.ttf",  # bundled OFL — rounded, thick, perfect for stickers
            _FONTS_DIR / "ArialRoundedBold.ttf",  # bundled — bubbly, thick
            Path("/System/Library/Fonts/Supplemental/Arial Rounded Bold.ttf"),
            _FONTS_DIR / "MarkerFelt.ttc",  # bundled — casual handwritten
        ],
        "regular": [
            _FONTS_DIR
            / "FredokaOne-Regular.ttf",  # bundled OFL — works well at regular weight too
            _FONTS_DIR / "ArialRoundedBold.ttf",  # still looks good at regular weight
            Path("/System/Library/Fonts/Supplemental/Arial Rounded Bold.ttf"),
        ],
    }

    @classmethod
    def _resolve_font(
        cls, style: str = "bold", size: int = 72
    ) -> ImageFont.FreeTypeFont:
        """Resolve a TrueType font from the fallback chain.

        Args:
            style: "bold" or "regular"
            size:  Point size

        Returns:
            ImageFont.FreeTypeFont, or PIL's default bitmap font as last resort.
        """
        for path in cls._FONT_PATHS.get(style, cls._FONT_PATHS["bold"]):
            if path.exists():
                try:
                    # .ttc files may have multiple faces; index=0 is the default
                    return ImageFont.truetype(str(path), size, index=0)
                except Exception:
                    continue
        # Last resort — PIL built-in (small bitmap, not great but won't crash)
        print("    WARNING: No TrueType font found, using PIL default bitmap font")
        return ImageFont.load_default()

    # -------------------------------------------------------------------------
    # Text overlay
    # -------------------------------------------------------------------------
    def add_text_overlay(
        self,
        img: Image.Image,
        text_config: dict | str,
    ) -> Image.Image:
        """
        Render text on top of a processed sticker image.

        Called AFTER add_white_outline() and BEFORE resize_to_spec(), so text
        is rendered at full resolution (typically 1024×1024) and scales cleanly
        for every target platform.

        Args:
            img:         RGBA image with outline already applied.
            text_config: Either a plain string (uses all defaults) or a dict:
                {
                    "content":      str,            # required — the text to show
                    "position":     str,            # "top" | "bottom" | "center" (default "bottom")
                    "font_size":    "auto" | int,   # "auto" fits ~80% width (default "auto")
                    "color":        str,            # hex fill color (default "#FFFFFF")
                    "stroke_color": str,            # hex stroke color (default "#4A3728")
                    "stroke_width": int,            # stroke px at render resolution (default 8)
                    "style":        str,            # "bold" | "regular" (default "bold")
                }

        Returns:
            New RGBA image with text composited on top.
        """
        # --- Normalize config ---------------------------------------------------
        if isinstance(text_config, str):
            text_config = {"content": text_config}

        content = text_config.get("content", "").strip()
        if not content:
            return img  # nothing to render

        position = text_config.get("position", "bottom")
        font_size_cfg = text_config.get("font_size", "auto")
        fill_color = text_config.get("color", "#FFFFFF")
        stroke_color = text_config.get("stroke_color", "#4A3728")
        stroke_width = int(text_config.get("stroke_width", 8))
        style = text_config.get("style", "bold")

        w, h = img.size

        # --- Resolve font size ---------------------------------------------------
        if font_size_cfg == "auto":
            # Binary-search for largest font size that fits ~80% of image width
            target_width = int(w * 0.80)
            lo, hi = 20, 300
            best_size = lo
            while lo <= hi:
                mid = (lo + hi) // 2
                test_font = self._resolve_font(style, mid)
                # Use textbbox for accurate measurement (Pillow ≥ 8.0)
                dummy_draw = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
                bbox = dummy_draw.textbbox(
                    (0, 0), content, font=test_font, stroke_width=stroke_width
                )
                text_w = bbox[2] - bbox[0]
                if text_w <= target_width:
                    best_size = mid
                    lo = mid + 1
                else:
                    hi = mid - 1
            font_size = best_size
        else:
            font_size = int(font_size_cfg)

        font = self._resolve_font(style, font_size)

        # --- Compute text position -----------------------------------------------
        draw = ImageDraw.Draw(img)
        bbox = draw.textbbox((0, 0), content, font=font, stroke_width=stroke_width)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]

        # Center horizontally
        tx = (w - text_w) // 2

        # Vertical placement
        if position == "top":
            ty = int(h * 0.05)
        elif position == "center":
            ty = (h - text_h) // 2
        else:  # "bottom" (default)
            ty = int(h * 0.82) - text_h // 2

        # Clamp to stay inside the image
        ty = max(4, min(ty, h - text_h - 4))

        # --- Render text onto the image ------------------------------------------
        # Draw stroke (outline) first, then fill — gives clean bordered text
        draw.text(
            (tx, ty),
            content,
            font=font,
            fill=fill_color,
            stroke_width=stroke_width,
            stroke_fill=stroke_color,
            anchor=None,
        )

        print(f'    Text overlay: "{content}" @ {position} (size={font_size})')
        return img

    def normalize_colors(
        self,
        img: Image.Image,
        saturation: float = 1.15,
        brightness: float = 1.05,
        contrast: float = 1.05,
    ) -> Image.Image:
        """
        Normalize colors for consistency across AI-generated batches.
        This counts as meaningful post-processing for copyright purposes.

        Args:
            saturation: > 1.0 boosts color vibrancy (kawaii style)
            brightness: > 1.0 makes slightly brighter
            contrast: > 1.0 makes outlines sharper
        """
        # Boost saturation for kawaii vibrancy
        img = ImageEnhance.Color(img).enhance(saturation)
        # Slight brightness bump
        img = ImageEnhance.Brightness(img).enhance(brightness)
        # Sharpen outlines slightly
        img = ImageEnhance.Contrast(img).enhance(contrast)
        return img

    def resize_to_spec(self, img: Image.Image, platform: str) -> Image.Image:
        """
        Resize image to platform spec.
        Tight-crops to visible content first, then scales to fill 90% of target canvas.
        """
        import numpy as np

        spec = self.SPECS[platform]
        target_w, target_h = spec["size"]

        # STEP 1: Tight-crop to visible content bounding box
        arr = np.array(img)
        if arr.shape[2] == 4:
            ys, xs = np.where(arr[:, :, 3] > 0)
            if len(ys) > 0:
                pad = 4
                x0 = max(0, int(xs.min()) - pad)
                y0 = max(0, int(ys.min()) - pad)
                x1 = min(img.width, int(xs.max()) + pad + 1)
                y1 = min(img.height, int(ys.max()) + pad + 1)
                img = img.crop((x0, y0, x1, y1))

        # STEP 2: Scale tight-cropped image to fit target canvas
        # Use per-platform fill_ratio if specified, otherwise default to 90%
        fill_ratio = spec.get("fill_ratio", 0.90)
        ratio = min(
            (target_w * fill_ratio) / img.width,
            (target_h * fill_ratio) / img.height,
        )
        new_w = max(1, int(img.width * ratio))
        new_h = max(1, int(img.height * ratio))

        resized = img.resize((new_w, new_h), Image.LANCZOS)

        # STEP 3: Center on transparent canvas
        canvas = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
        offset_x = (target_w - new_w) // 2
        offset_y = (target_h - new_h) // 2
        canvas.paste(resized, (offset_x, offset_y), resized)
        return canvas

    def save_optimized(self, img: Image.Image, output_path: str, platform: str) -> Path:
        """
        Save image with format and size optimization for target platform.
        For WebP: uses binary search on quality to fit under max_kb.
        For PNG: uses optimize flag and color quantization if needed.
        """
        spec = self.SPECS[platform]
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)

        fmt = spec["format"]
        max_kb = spec["max_kb"]

        if fmt == "WEBP":
            return self._save_webp_optimized(img, output, max_kb)
        elif fmt == "PNG":
            return self._save_png_optimized(img, output, max_kb)
        else:
            raise ValueError(f"Unsupported format: {fmt}")

    def _save_webp_optimized(
        self, img: Image.Image, output: Path, max_kb: int | None
    ) -> Path:
        """Save as WebP with quality optimization to fit size limit."""
        quality = 95

        while quality > 5:
            buffer = io.BytesIO()
            img.save(buffer, format="WEBP", quality=quality, method=6)
            size_kb = buffer.tell() / 1024

            if max_kb is None or size_kb <= max_kb:
                with open(output, "wb") as f:
                    f.write(buffer.getvalue())
                print(f"    {output.name}: {size_kb:.1f}KB (q={quality})")
                return output

            quality -= 5

        # Last resort: save at minimum quality
        buffer = io.BytesIO()
        img.save(buffer, format="WEBP", quality=5, method=6)
        size_kb = buffer.tell() / 1024

        if max_kb and size_kb > max_kb:
            # Try reducing image complexity
            img_reduced = img.quantize(colors=128, method=2).convert("RGBA")
            buffer = io.BytesIO()
            img_reduced.save(buffer, format="WEBP", quality=10, method=6)
            size_kb = buffer.tell() / 1024

        with open(output, "wb") as f:
            f.write(buffer.getvalue())

        if max_kb and size_kb > max_kb:
            print(
                f"    WARNING {output.name}: {size_kb:.1f}KB exceeds {max_kb}KB limit!"
            )
        else:
            print(f"    {output.name}: {size_kb:.1f}KB (q=min)")
        return output

    def _save_png_optimized(
        self, img: Image.Image, output: Path, max_kb: int | None
    ) -> Path:
        """Save as PNG with optimization."""
        buffer = io.BytesIO()
        img.save(buffer, format="PNG", optimize=True)
        size_kb = buffer.tell() / 1024

        if max_kb and size_kb > max_kb:
            # Reduce color depth to fit
            img_reduced = img.quantize(colors=256, method=2).convert("RGBA")
            buffer = io.BytesIO()
            img_reduced.save(buffer, format="PNG", optimize=True)
            size_kb = buffer.tell() / 1024

        with open(output, "wb") as f:
            f.write(buffer.getvalue())

        print(f"    {output.name}: {size_kb:.1f}KB")
        return output

    def process_single(
        self,
        input_path: str,
        output_dir: str,
        platforms: list[str],
        skip_bg_removal: bool = False,
        sticker_config: dict | None = None,
    ) -> dict[str, Path]:
        """
        Full pipeline for a single sticker image.

        Steps:
            1. Background removal (flood-fill from corners)
            2. Color normalization
            3. White outline addition
            4. Text overlay (optional — only if sticker_config has "text" key)
            5. Resize + save for each platform

        Args:
            input_path: Path to raw image (PNG/JPG)
            output_dir: Base output directory
            platforms: List of platform keys (from SPECS)
            skip_bg_removal: Set True if image already has transparent bg
            sticker_config: Optional per-sticker config dict. If it contains a
                "text" key (str or dict), text will be rendered on the sticker
                after the white outline step.

        Returns:
            Dict of {platform: output_path}
        """
        name = Path(input_path).stem
        print(f"\n  Processing: {name}")

        # Step 1: Background removal
        if skip_bg_removal:
            print("    Loading (skip bg removal)...")
            img = Image.open(input_path).convert("RGBA")
        else:
            print("    Removing background...")
            img = self.remove_background(input_path)

        # Step 2: Color normalization (copyright-strengthening post-processing)
        print("    Normalizing colors...")
        img = self.normalize_colors(img)

        # Step 3: Add white outline (conditional — some platforms like emoji skip it)
        # Split platforms into outline vs no-outline groups
        outline_platforms = [
            p
            for p in platforms
            if p in self.SPECS and self.SPECS[p].get("outline", True)
        ]
        no_outline_platforms = [
            p
            for p in platforms
            if p in self.SPECS and not self.SPECS[p].get("outline", True)
        ]

        if outline_platforms:
            print("    Adding white outline...")
            img_with_outline = self.add_white_outline(img)
        else:
            img_with_outline = None

        # Step 4: Text overlay (optional — applied only to outlined version)
        text_cfg = (sticker_config or {}).get("text")
        if text_cfg and img_with_outline is not None:
            img_with_outline = self.add_text_overlay(img_with_outline, text_cfg)

        # Step 5: Resize and save for each platform
        results = {}
        for platform in platforms:
            if platform not in self.SPECS:
                print(f"    Unknown platform: {platform}, skipping")
                continue

            spec = self.SPECS[platform]
            ext = spec["ext"]
            out_path = f"{output_dir}/{platform}/{name}{ext}"

            # Use the appropriate image version (with/without outline)
            source_img = img_with_outline if platform in outline_platforms else img
            resized = self.resize_to_spec(source_img, platform)
            results[platform] = self.save_optimized(resized, out_path, platform)

        return results

    def process_batch(
        self,
        input_dir: str,
        output_dir: str,
        platforms: list[str],
        skip_bg_removal: bool = False,
        sticker_configs: list[dict] | None = None,
    ) -> list[dict]:
        """
        Process all images in a directory.

        Args:
            input_dir: Directory containing raw PNG/JPG images
            output_dir: Base output directory (subdirs per platform)
            platforms: List of platform keys
            skip_bg_removal: Set True if images already have transparent bg
            sticker_configs: Optional list of per-sticker config dicts (one per
                image, matched by sorted filename order). Each dict may contain
                a "text" key to enable text overlay. If None or shorter than the
                image list, missing entries default to no text overlay.

        Returns:
            List of result dicts per image
        """
        input_path = Path(input_dir)
        images = sorted(
            list(input_path.glob("*.png"))
            + list(input_path.glob("*.jpg"))
            + list(input_path.glob("*.jpeg"))
            + list(input_path.glob("*.webp"))
        )

        if not images:
            print(f"No images found in {input_dir}")
            return []

        configs = sticker_configs or []
        text_count = sum(1 for c in configs if c.get("text"))

        print(f"\n{'=' * 60}")
        print(f"Processing {len(images)} images for {len(platforms)} platforms")
        print(f"Input:  {input_dir}")
        print(f"Output: {output_dir}")
        print(f"Platforms: {', '.join(platforms)}")
        if text_count:
            print(f"Text overlays: {text_count} stickers have text configured")
        print(f"{'=' * 60}")

        all_results = []
        for i, img_path in enumerate(images):
            print(f"\n[{i + 1}/{len(images)}]", end="")
            cfg = configs[i] if i < len(configs) else None
            result = self.process_single(
                str(img_path),
                output_dir,
                platforms,
                skip_bg_removal,
                sticker_config=cfg,
            )
            all_results.append({"source": str(img_path), "outputs": result})

        # Summary
        print(f"\n{'=' * 60}")
        print(f"Processing complete: {len(all_results)} stickers")
        for platform in platforms:
            out_dir = Path(output_dir) / platform
            if out_dir.exists():
                count = len(list(out_dir.iterdir()))
                print(f"  {platform}: {count} files in {out_dir}")
        print(f"{'=' * 60}")

        return all_results

    def process_animated(
        self,
        input_path: str,
        output_dir: str,
        animation_type: str = "bounce",
        formats: list[str] | None = None,
    ) -> dict[str, Path]:
        """
        Create animated/video stickers from a static (already processed) image.

        This runs AFTER the normal static processing pipeline, using the
        processed 512x512 PNG as input.

        Steps:
            1. Load processed sticker (transparent bg, outline already applied)
            2. Resize to 512x512 if needed
            3. Convert to TGS (animated Lottie) if "tgs" in formats
            4. Convert to WebM VP9 (video sticker) if "webm" in formats

        Args:
            input_path:      Path to a processed sticker PNG (512x512 preferred).
            output_dir:      Base output directory (subdirs per format).
            animation_type:  Preset name from animation_presets module.
            formats:         List of output formats: ["tgs", "webm"]. Default: both.

        Returns:
            Dict mapping format key to output Path, e.g.
            {"telegram_animated": Path(...), "telegram_video": Path(...)}.
        """
        from animated_converter import LottieAnimator, VideoConverter

        if formats is None:
            formats = ["tgs", "webm"]

        name = Path(input_path).stem
        results: dict[str, Path] = {}

        if "tgs" in formats:
            tgs_dir = Path(output_dir) / "telegram_animated"
            tgs_dir.mkdir(parents=True, exist_ok=True)
            tgs_out = tgs_dir / f"{name}.tgs"
            try:
                animator = LottieAnimator()
                animator.png_to_tgs(
                    input_path,
                    str(tgs_out),
                    animation_type=animation_type,
                )
                results["telegram_animated"] = tgs_out
                print(
                    f"    {tgs_out.name}: {tgs_out.stat().st_size / 1024:.1f}KB (TGS)"
                )
            except Exception as exc:
                print(f"    WARNING: TGS conversion failed for {name}: {exc}")

        if "webm" in formats:
            webm_dir = Path(output_dir) / "telegram_video"
            webm_dir.mkdir(parents=True, exist_ok=True)
            webm_out = webm_dir / f"{name}.webm"
            try:
                converter = VideoConverter()
                converter.png_to_webm(
                    input_path,
                    str(webm_out),
                    animation_type=animation_type,
                )
                results["telegram_video"] = webm_out
                print(
                    f"    {webm_out.name}: {webm_out.stat().st_size / 1024:.1f}KB (WebM)"
                )
            except Exception as exc:
                print(f"    WARNING: WebM conversion failed for {name}: {exc}")

        return results

    def process_batch_animated(
        self,
        input_dir: str,
        output_dir: str,
        animation_type: str = "bounce",
        formats: list[str] | None = None,
    ) -> list[dict]:
        """
        Generate animated/video stickers for all processed images in a directory.

        Expects input_dir to contain already-processed 512x512 PNGs
        (typically from the telegram/ output subdirectory, or any static
        processed output).

        Args:
            input_dir:       Directory of processed sticker PNGs.
            output_dir:      Base output directory.
            animation_type:  Animation preset name.
            formats:         ["tgs", "webm"] or subset.

        Returns:
            List of result dicts per image.
        """
        if formats is None:
            formats = ["tgs", "webm"]

        input_path = Path(input_dir)
        images = sorted(
            list(input_path.glob("*.png")) + list(input_path.glob("*.webp"))
        )

        if not images:
            print(f"No processed images found in {input_dir}")
            return []

        fmt_labels = ", ".join(f.upper() for f in formats)
        print(f"\n{'=' * 60}")
        print(f"Generating animated stickers: {len(images)} images")
        print(f"Animation preset: {animation_type}")
        print(f"Output formats: {fmt_labels}")
        print(f"{'=' * 60}")

        all_results = []
        for i, img_path in enumerate(images):
            print(f"\n[{i + 1}/{len(images)}] Animating: {img_path.stem}")
            result = self.process_animated(
                str(img_path),
                output_dir,
                animation_type=animation_type,
                formats=formats,
            )
            all_results.append({"source": str(img_path), "outputs": result})

        # Summary
        print(f"\n{'=' * 60}")
        print(f"Animated generation complete: {len(all_results)} stickers")
        for fmt_key in ["telegram_animated", "telegram_video"]:
            out_dir = Path(output_dir) / fmt_key
            if out_dir.exists():
                count = len(list(out_dir.iterdir()))
                print(f"  {fmt_key}: {count} files in {out_dir}")
        print(f"{'=' * 60}")

        return all_results

    def create_tray_icon(
        self,
        source_path: str,
        output_path: str,
        platform: str = "whatsapp_tray",
    ) -> Path:
        """
        Create a tray/tab icon from a sticker image.
        Typically uses the most iconic sticker in the pack.

        Args:
            source_path: Path to the best sticker image (already processed)
            output_path: Where to save the tray icon
            platform: "whatsapp_tray" (96x96) or "line_tab" (96x74)
        """
        img = Image.open(source_path).convert("RGBA")
        resized = self.resize_to_spec(img, platform)
        return self.save_optimized(resized, output_path, platform)


# =============================================================================
# CLI ENTRY POINT
# =============================================================================
if __name__ == "__main__":
    import importlib.util

    if len(sys.argv) < 2:
        print(
            "Usage: python sticker_processor.py <input_dir> [output_dir] [platforms...]"
        )
        print()
        print("Examples:")
        print("  python sticker_processor.py pack01_emotions_v1/raw")
        print("  python sticker_processor.py stickers/ output/ whatsapp telegram")
        print("  python sticker_processor.py stickers/ output/ --skip-bg")
        print(
            "  python sticker_processor.py stickers/ output/ --pack-config path/to/pack_config.py"
        )
        print()
        print("Available platforms:", ", ".join(StickerProcessor.SPECS.keys()))
        sys.exit(1)

    input_dir = sys.argv[1]
    output_dir = (
        sys.argv[2]
        if len(sys.argv) > 2 and not sys.argv[2].startswith("-")
        else f"{input_dir}/../final"
    )
    skip_bg = "--skip-bg" in sys.argv

    # Parse platforms from remaining args
    platforms = [
        a for a in sys.argv[2:] if not a.startswith("-") and a in StickerProcessor.SPECS
    ]
    if not platforms:
        platforms = ["whatsapp", "telegram", "imessage_large", "line", "print_etsy"]

    # Load sticker configs from pack_config.py if --pack-config is specified
    sticker_configs = None
    if "--pack-config" in sys.argv:
        idx = sys.argv.index("--pack-config")
        if idx + 1 < len(sys.argv):
            config_path = sys.argv[idx + 1]
            spec = importlib.util.spec_from_file_location("pack_config", config_path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            pack_cfg = getattr(mod, "PACK_CONFIG", None) or getattr(
                mod, "STICKER_PACK", None
            )
            if pack_cfg and "stickers" in pack_cfg:
                sticker_configs = pack_cfg["stickers"]
                text_count = sum(1 for s in sticker_configs if s.get("text"))
                print(
                    f"Loaded {len(sticker_configs)} sticker configs from {config_path}"
                )
                if text_count:
                    print(f"  {text_count} stickers have text overlay configured")
            else:
                print(f"WARNING: No PACK_CONFIG['stickers'] found in {config_path}")
        else:
            print("ERROR: --pack-config requires a path argument")
            sys.exit(1)

    processor = StickerProcessor(outline_width=10)
    processor.process_batch(
        input_dir,
        output_dir,
        platforms,
        skip_bg_removal=skip_bg,
        sticker_configs=sticker_configs,
    )
