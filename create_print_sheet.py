#!/usr/bin/env python3
"""
Printable Sticker Sheet Generator - Create print-ready layouts for Etsy/Gumroad.

Generates:
1. Individual high-res PNGs (for digital planner use)
2. Print-ready sticker sheet (US Letter, 300 DPI)
3. A4 sticker sheet variant
4. Distribution ZIP with README

Usage:
    python create_print_sheet.py <sticker_dir> [output_dir]

    # Example:
    python create_print_sheet.py pack01_emotions_v1/final/print_etsy pack01_emotions_v1/dist
"""

import os
import sys
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


# Page sizes at 300 DPI
PAGE_SIZES = {
    "us_letter": (2550, 3300),  # 8.5 x 11 inches at 300 DPI
    "a4": (2480, 3508),  # 210 x 297 mm at 300 DPI
    "square_social": (3000, 3000),  # Social media preview
}


def create_sticker_sheet(
    sticker_dir: str,
    output_path: str,
    page_size: str = "us_letter",
    cols: int = 4,
    sticker_size: int = 500,
    padding: int = 40,
    dpi: int = 300,
    bg_color: tuple = (255, 255, 255, 255),
    title: str | None = None,
) -> Path:
    """
    Arrange stickers in a grid layout suitable for printing.

    Args:
        sticker_dir: Directory with high-res PNG stickers
        output_path: Output file path (.png)
        page_size: "us_letter", "a4", or "square_social"
        cols: Number of columns in the grid
        sticker_size: Max size per sticker cell in pixels
        padding: Padding between stickers in pixels
        dpi: Output DPI (300 for print, 72 for web)
        bg_color: Background RGBA tuple
        title: Optional title text at the top

    Returns:
        Path to saved sticker sheet
    """
    stickers = sorted(
        list(Path(sticker_dir).glob("*.png")) + list(Path(sticker_dir).glob("*.webp"))
    )

    if not stickers:
        print(f"No sticker images found in {sticker_dir}")
        return None

    sheet_w, sheet_h = PAGE_SIZES.get(page_size, PAGE_SIZES["us_letter"])
    rows = (len(stickers) + cols - 1) // cols

    # Title area
    title_height = 120 if title else 0

    # Calculate cell size to fit the page
    available_w = sheet_w - padding * (cols + 1)
    available_h = sheet_h - padding * (rows + 1) - title_height
    cell_w = available_w // cols
    cell_h = available_h // rows
    cell_size = min(cell_w, cell_h, sticker_size)

    # Create sheet
    sheet = Image.new("RGBA", (sheet_w, sheet_h), bg_color)
    draw = ImageDraw.Draw(sheet)

    # Add title if provided
    if title:
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 60)
        except (OSError, IOError):
            font = ImageFont.load_default()

        bbox = draw.textbbox((0, 0), title, font=font)
        text_w = bbox[2] - bbox[0]
        draw.text(
            ((sheet_w - text_w) // 2, padding),
            title,
            fill=(51, 51, 51, 255),
            font=font,
        )

    # Place stickers
    for i, sticker_path in enumerate(stickers):
        row = i // cols
        col = i % cols

        sticker = Image.open(sticker_path).convert("RGBA")

        # Resize maintaining aspect ratio
        ratio = min(cell_size / sticker.width, cell_size / sticker.height)
        new_w = int(sticker.width * ratio)
        new_h = int(sticker.height * ratio)
        sticker = sticker.resize((new_w, new_h), Image.LANCZOS)

        # Calculate position (centered in cell)
        x = padding + col * (cell_size + padding) + (cell_size - new_w) // 2
        y = (
            title_height
            + padding
            + row * (cell_size + padding)
            + (cell_size - new_h) // 2
        )

        sheet.paste(sticker, (x, y), sticker)

    # Save
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(str(output), dpi=(dpi, dpi))

    size_kb = output.stat().st_size / 1024
    print(
        f"  Sticker sheet: {output} ({sheet_w}x{sheet_h} @ {dpi}DPI, {size_kb:.0f}KB)"
    )
    return output


def create_social_preview(
    sticker_dir: str,
    output_path: str,
    title: str = "",
    subtitle: str = "",
) -> Path:
    """
    Create a social media preview image (for Etsy listing, Instagram, etc.)
    Shows a selection of stickers in an appealing layout.
    """
    stickers = sorted(Path(sticker_dir).glob("*.png"))[:9]  # Max 9 for 3x3 grid

    # Create a 3000x3000 preview
    size = 3000
    sheet = Image.new("RGBA", (size, size), (245, 240, 255, 255))  # Light purple bg
    draw = ImageDraw.Draw(sheet)

    cols = 3
    padding = 80
    sticker_size = (size - padding * (cols + 1)) // cols

    for i, sticker_path in enumerate(stickers):
        row = i // cols
        col = i % cols

        sticker = Image.open(sticker_path).convert("RGBA")
        ratio = min(sticker_size / sticker.width, sticker_size / sticker.height) * 0.85
        new_w = int(sticker.width * ratio)
        new_h = int(sticker.height * ratio)
        sticker = sticker.resize((new_w, new_h), Image.LANCZOS)

        x = padding + col * (sticker_size + padding) + (sticker_size - new_w) // 2
        y = padding + row * (sticker_size + padding) + (sticker_size - new_h) // 2

        sheet.paste(sticker, (x, y), sticker)

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(str(output))
    print(f"  Social preview: {output}")
    return output


def create_distribution_zip(
    pack_id: str,
    pack_name: str,
    sticker_dir: str,
    sheet_paths: list[str],
    output_path: str,
    publisher: str = "Your Brand Name",
) -> Path:
    """
    Create a complete distribution ZIP for Etsy/Gumroad.

    Contents:
    - Individual high-res PNG stickers
    - Print-ready sticker sheet(s)
    - README with usage instructions
    - License file
    """
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    sticker_files = sorted(
        list(Path(sticker_dir).glob("*.png")) + list(Path(sticker_dir).glob("*.webp"))
    )

    with zipfile.ZipFile(str(output), "w", zipfile.ZIP_DEFLATED) as zf:
        # Individual stickers
        for f in sticker_files:
            zf.write(str(f), f"stickers/{f.name}")

        # Sticker sheets
        for sheet_path in sheet_paths:
            sheet = Path(sheet_path)
            if sheet.exists():
                zf.write(str(sheet), f"print_sheets/{sheet.name}")

        # README
        readme = f"""# {pack_name}
# Created by {publisher}

Thank you for your purchase!

## What's Included
- {len(sticker_files)} individual PNG stickers (transparent background, high resolution)
- Print-ready sticker sheets (US Letter & A4 size, 300 DPI)

## How to Use

### Digital Planners (GoodNotes, Notability, etc.)
1. Import the individual PNG files into your planner app
2. Resize and place as needed
3. Each sticker has a transparent background for clean placement

### Printing
1. Open the sticker sheet file from the print_sheets/ folder
2. Print on sticker paper (matte or glossy, your preference)
3. Cut around each sticker with scissors or a cutting machine
4. Recommended: Use Cricut or Silhouette for precise cutting

### Social Media
- Feel free to use in your personal social media posts
- Credit is appreciated but not required for personal use

## License
- PERSONAL USE: Included with purchase
- COMMERCIAL USE: Please purchase the commercial license separately
- DO NOT: Resell, redistribute, or claim as your own creation

## Need Help?
Contact: [your email]
Shop: [your shop URL]

Enjoy your stickers! <3
"""
        zf.writestr("README.txt", readme)

        # License
        license_text = f"""PERSONAL USE LICENSE
{pack_name} by {publisher}

This license grants you the right to use these stickers for:
- Personal digital planners and journals
- Personal social media posts
- Personal printed stickers for your own use
- Personal gifts (not for sale)

This license does NOT permit:
- Selling products containing these stickers
- Redistributing the digital files
- Using in commercial products or marketing materials
- Claiming the artwork as your own
- Sublicensing to others

For commercial use, please purchase a Commercial License.

Copyright (c) {publisher}. All rights reserved.
"""
        zf.writestr("LICENSE.txt", license_text)

    size_mb = output.stat().st_size / (1024 * 1024)
    print(f"  Distribution ZIP: {output} ({size_mb:.1f}MB)")
    return output


# =============================================================================
# CLI ENTRY POINT
# =============================================================================
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(
            "Usage: python create_print_sheet.py <sticker_dir> [output_dir] [pack_name]"
        )
        print()
        print("Example:")
        print("  python create_print_sheet.py pack01_emotions_v1/final/print_etsy")
        print("  python create_print_sheet.py stickers/ dist/ 'Mochi Emotions Vol. 1'")
        sys.exit(1)

    sticker_dir = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "dist"
    pack_name = sys.argv[3] if len(sys.argv) > 3 else "Kawaii Sticker Pack"

    print(f"\nCreating print materials for: {pack_name}")
    print(f"{'=' * 60}")

    sheets = []

    # US Letter sheet
    sheet = create_sticker_sheet(
        sticker_dir,
        f"{output_dir}/sheets/sticker_sheet_letter.png",
        page_size="us_letter",
        title=pack_name,
    )
    if sheet:
        sheets.append(str(sheet))

    # A4 sheet
    sheet = create_sticker_sheet(
        sticker_dir,
        f"{output_dir}/sheets/sticker_sheet_a4.png",
        page_size="a4",
        title=pack_name,
    )
    if sheet:
        sheets.append(str(sheet))

    # Social media preview
    create_social_preview(
        sticker_dir,
        f"{output_dir}/social_preview.png",
        title=pack_name,
    )

    # Distribution ZIP
    create_distribution_zip(
        pack_id="pack01",
        pack_name=pack_name,
        sticker_dir=sticker_dir,
        sheet_paths=sheets,
        output_path=f"{output_dir}/{pack_name.replace(' ', '_').lower()}_digital_download.zip",
    )

    print(f"\n{'=' * 60}")
    print(f"All print materials created in {output_dir}/")
