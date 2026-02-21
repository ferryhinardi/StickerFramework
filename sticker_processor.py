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

from PIL import Image, ImageEnhance, ImageFilter


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
        "print_etsy": {
            "size": (2048, 2048),
            "format": "PNG",
            "max_kb": None,
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
        Remove background using rembg (U2-Net AI model).
        Returns RGBA image with transparent background.
        """
        try:
            from rembg import remove
        except ImportError:
            print("Error: rembg not installed. Run: pip install rembg onnxruntime")
            sys.exit(1)

        with open(input_path, "rb") as f:
            input_bytes = f.read()

        output_bytes = remove(input_bytes)
        return Image.open(io.BytesIO(output_bytes)).convert("RGBA")

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
        Maintains aspect ratio and centers on transparent canvas with padding.
        """
        spec = self.SPECS[platform]
        target_w, target_h = spec["size"]

        # Calculate resize to fit within 90% of target (leaving padding)
        ratio = min(
            (target_w * 0.9) / img.width,
            (target_h * 0.9) / img.height,
        )
        new_w = int(img.width * ratio)
        new_h = int(img.height * ratio)

        resized = img.resize((new_w, new_h), Image.LANCZOS)

        # Center on transparent canvas
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
    ) -> dict[str, Path]:
        """
        Full pipeline for a single sticker image.

        Steps:
            1. Background removal (rembg)
            2. Color normalization
            3. White outline addition
            4. Resize + save for each platform

        Args:
            input_path: Path to raw image (PNG/JPG)
            output_dir: Base output directory
            platforms: List of platform keys (from SPECS)
            skip_bg_removal: Set True if image already has transparent bg

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

        # Step 3: Add white outline
        print("    Adding white outline...")
        img = self.add_white_outline(img)

        # Step 4: Resize and save for each platform
        results = {}
        for platform in platforms:
            if platform not in self.SPECS:
                print(f"    Unknown platform: {platform}, skipping")
                continue

            spec = self.SPECS[platform]
            ext = spec["ext"]
            out_path = f"{output_dir}/{platform}/{name}{ext}"

            resized = self.resize_to_spec(img, platform)
            results[platform] = self.save_optimized(resized, out_path, platform)

        return results

    def process_batch(
        self,
        input_dir: str,
        output_dir: str,
        platforms: list[str],
        skip_bg_removal: bool = False,
    ) -> list[dict]:
        """
        Process all images in a directory.

        Args:
            input_dir: Directory containing raw PNG/JPG images
            output_dir: Base output directory (subdirs per platform)
            platforms: List of platform keys
            skip_bg_removal: Set True if images already have transparent bg

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

        print(f"\n{'=' * 60}")
        print(f"Processing {len(images)} images for {len(platforms)} platforms")
        print(f"Input:  {input_dir}")
        print(f"Output: {output_dir}")
        print(f"Platforms: {', '.join(platforms)}")
        print(f"{'=' * 60}")

        all_results = []
        for i, img_path in enumerate(images):
            print(f"\n[{i + 1}/{len(images)}]", end="")
            result = self.process_single(
                str(img_path), output_dir, platforms, skip_bg_removal
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
    if len(sys.argv) < 2:
        print(
            "Usage: python sticker_processor.py <input_dir> [output_dir] [platforms...]"
        )
        print()
        print("Examples:")
        print("  python sticker_processor.py pack01_emotions_v1/raw")
        print("  python sticker_processor.py stickers/ output/ whatsapp telegram")
        print("  python sticker_processor.py stickers/ output/ --skip-bg")
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

    processor = StickerProcessor(outline_width=10)
    processor.process_batch(input_dir, output_dir, platforms, skip_bg_removal=skip_bg)
