# Image Processing Pipeline

> Technical reference for `split_stickers.py` and `sticker_processor.py`.

## Overview

The image processing pipeline has two stages:

```
sticker_pack.png ──→ split_stickers.py ──→ sticker_processor.py ──→ LINE-ready images
  (composite)          (8x 512x512)          (370x320, 240x240, 96x74)
```

**Stage 1** splits a composite sheet into individual stickers.
**Stage 2** processes each sticker for LINE's exact specifications.

Both scripts are standalone CLI tools that can be used independently or as part of the full pipeline (`run_pipeline.py`).

---

## Stage 1: split_stickers.py

### Purpose

Splits a DALL-E composite sticker sheet into individual sticker PNGs using computer vision (connected-component analysis).

### Algorithm

```
Input: sticker_pack.png (composite sheet with white background)
                │
                ▼
    1. White Background Removal
       - Scan every pixel
       - If R > threshold AND G > threshold AND B > threshold → set alpha to 0
       - Default threshold: 240 (near-white)
       - Output: RGBA image with transparent background
                │
                ▼
    2. Connected-Component Analysis
       - Create binary mask from alpha channel (alpha > 0 → 1)
       - scipy.ndimage.label() finds connected regions
       - Each connected region = one potential sticker
       - Filter out regions smaller than min_size (noise)
                │
                ▼
    3. Bounding Box Extraction
       - For each labeled region, compute bounding box (x, y, w, h)
       - Filter boxes below minimum size threshold
                │
                ▼
    4. Row-Bucket Sorting
       - Group boxes by row: center_y / (image_height / grid_rows)
       - Within each row, sort left-to-right by center_x
       - Result: reading order (top-left → bottom-right)
                │
                ▼
    5. Crop & Resize
       - Crop each box with 10px padding
       - Resize to 512x512 maintaining aspect ratio (fit within 90%)
       - Center on transparent 512x512 canvas
                │
                ▼
Output: split/01_name.png, split/02_name.png, ... split/08_name.png
```

### Usage

```bash
# Set the pack name via environment variable
STICKER_PACK="boba-milo-5" python split_stickers.py
```

The script reads its configuration from the internal `PACKS` dictionary.

### Pack Registry Configuration

Each pack is defined in the `PACKS` dictionary inside `split_stickers.py`:

```python
PACKS = {
    "boba-milo-5": {
        "input_file": "packs/boba-milo-5/sticker_pack.png",
        "grid_rows": 4,          # Number of rows in the composite grid
        "threshold": 240,        # White detection threshold (0-255)
        "names": [               # Sticker names in reading order
            "01_marhaban_ya_ramadan",
            "02_sahur_time",
            "03_tadarus",
            "04_berbuka",
            "05_sholat_tarawih",
            "06_silaturahmi",
            "07_lebaran",
            "08_mudik",
        ],
    },
}
```

### Configuration Fields

| Field        | Type      | Required | Description                                                       |
| ------------ | --------- | -------- | ----------------------------------------------------------------- |
| `input_file` | str       | Yes      | Path to composite sheet PNG                                       |
| `grid_rows`  | int       | Yes      | Number of rows in the grid (4 for 2x4, 4 for 4x4)                 |
| `threshold`  | int       | No       | White detection threshold (default: 240). Lower = more aggressive |
| `names`      | list[str] | Yes      | Ordered sticker names (must match expected count)                 |

### Adding a New Pack

1. Save composite sheet: `packs/<pack-name>/sticker_pack.png`
2. Add entry to `PACKS` dictionary in `split_stickers.py`:

```python
"my-new-pack": {
    "input_file": "packs/my-new-pack/sticker_pack.png",
    "grid_rows": 4,
    "names": [
        "01_hello", "02_thanks", "03_sorry", "04_love",
        "05_angry", "06_sad", "07_happy", "08_bye",
    ],
},
```

3. Run: `STICKER_PACK="my-new-pack" python split_stickers.py`
4. Check output: `ls packs/my-new-pack/split/`

### Output

```
packs/<pack-name>/split/
├── 01_name.png    # 512x512, RGBA, transparent background
├── 02_name.png
├── ...
└── 08_name.png    # (or 16_name.png for 16-sticker packs)
```

### Troubleshooting

#### Stickers are merged (two stickers detected as one)

**Cause:** Sticker regions are touching in the composite sheet — connected-component analysis treats them as one region.

**Solutions:**

1. Regenerate the composite sheet with more spacing (see [DALL-E Guide](04-dalle-generation-guide.md))
2. Lower the `threshold` value (e.g., 230 instead of 240) to be more aggressive with white removal
3. Manually add white space between touching stickers in an image editor

#### Missing stickers (fewer detected than expected)

**Cause:** Sticker is too small (below min_size filter) or has very low contrast against the background.

**Solutions:**

1. Check the composite sheet — is the sticker actually there?
2. Lower the threshold to detect more faint colors
3. Adjust `min_size` parameter if available

#### Wrong sort order

**Cause:** `grid_rows` doesn't match the actual grid layout, causing row-bucket assignment to fail.

**Solutions:**

1. Count the actual rows in the composite sheet
2. Set `grid_rows` accordingly (4 for 2x4, 4 for 4x4)
3. If stickers aren't evenly distributed in rows, manual reordering may be needed

---

## Stage 2: sticker_processor.py

### Purpose

Processes individual sticker PNGs for specific platform requirements. For LINE, it handles color normalization, outline generation, resizing, and format optimization.

### Pipeline

```
Input: split/01_name.png (512x512, transparent)
                │
                ▼
    1. Background Removal (optional, --skip-bg to skip)
       - Uses rembg library (U2-Net AI model)
       - Removes any remaining background
       - Converts to RGBA
       - Skip if split_stickers.py already handled this
                │
                ▼
    2. Color Normalization
       - Saturation: 1.15x (slightly more vivid)
       - Brightness: 1.05x (slightly brighter)
       - Contrast: 1.05x (slightly more contrast)
       - Purpose: Consistency across AI-generated batches
                │
                ▼
    3. White Outline (Die-Cut Border)
       - Extract alpha channel
       - Dilate using PIL.ImageFilter.MaxFilter(outline_width * 2 + 1)
       - Create white silhouette from dilated alpha
       - Composite: white silhouette → original image on top
       - Default outline_width: 10px
       - Purpose: Visibility on dark chat backgrounds + brand consistency
                │
                ▼
    4. Resize to Platform Specs
       - Fit within 90% of target dimensions (preserving aspect ratio)
       - Center on transparent canvas at target dimensions
       - Enforce even-numbered width and height (LINE requirement)
       - The 10% margin provides the ~10px padding LINE requires
                │
                ▼
    5. Save Optimized
       - PNG: optimize=True, fallback to color quantization if > 1MB
       - File size verified against platform maximum
                │
                ▼
Output: final/line/01_name.png (370x320)
        final/line_main/01_name.png (240x240)
        final/line_tab/01_name.png (96x74)
```

### Usage

```bash
python sticker_processor.py <input_dir> <output_dir> <platforms...> [--skip-bg]
```

#### LINE-Specific Command

```bash
python sticker_processor.py \
    packs/boba-milo-5/split \
    packs/boba-milo-5/final \
    line line_main line_tab \
    --skip-bg
```

#### Arguments

| Argument     | Description                                               |
| ------------ | --------------------------------------------------------- |
| `input_dir`  | Directory containing source sticker PNGs                  |
| `output_dir` | Base output directory (subdirs created per platform)      |
| `platforms`  | Space-separated list of target platforms                  |
| `--skip-bg`  | Skip background removal (use when bg already transparent) |

### Platform Specs

The `StickerProcessor` class defines specs for all supported platforms:

| Platform ID       | Dimensions (WxH) | Format | Max Size | Use Case                 |
| ----------------- | ---------------- | ------ | -------- | ------------------------ |
| `line`            | 370 x 320        | PNG    | 1 MB     | LINE sticker images      |
| `line_main`       | 240 x 240        | PNG    | 1 MB     | LINE main/cover image    |
| `line_tab`        | 96 x 74          | PNG    | 1 MB     | LINE chat tab/tray icon  |
| `whatsapp`        | 512 x 512        | WebP   | 100 KB   | WhatsApp stickers        |
| `telegram`        | 512 x 512        | WebP   | 512 KB   | Telegram stickers        |
| `imessage_small`  | 300 x 300        | PNG    | -        | iMessage small stickers  |
| `imessage_medium` | 408 x 408        | PNG    | -        | iMessage medium stickers |
| `imessage_large`  | 618 x 618        | PNG    | -        | iMessage large stickers  |
| `print_etsy`      | 3000 x 3000      | PNG    | -        | Etsy print-ready         |

### Output Structure

```
packs/<pack-name>/final/
├── line/                      # LINE sticker images
│   ├── 01_name.png            # ≤370x320, even dimensions
│   └── ... (8 files)
├── line_main/                 # LINE main image
│   ├── 01_name.png            # Exactly 240x240
│   └── ... (8 files, use first for upload)
├── line_tab/                  # LINE tab icon
│   ├── 01_name.png            # Exactly 96x74
│   └── ... (8 files, use first for upload)
├── whatsapp/                  # (if requested)
├── telegram/                  # (if requested)
└── ...
```

**Note:** `line_main/` and `line_tab/` generate one file per input sticker. For LINE upload, use the **first file** (`01_*.png`) as the main image and tab icon.

### Main/Tab Image Selection

By default, the **first sticker** (alphabetically) from the input directory is used for both the main image and tab icon. To use a different sticker:

1. Process normally (all stickers get main/tab versions)
2. When uploading, select the desired file from `line_main/` and `line_tab/`

The `create_tray_icon()` method can also generate tab icons from any specific sticker:

```python
processor = StickerProcessor(outline_width=10)
processor.create_tray_icon(
    input_path="packs/boba-milo-5/split/03_lets_eat.png",
    output_path="packs/boba-milo-5/final/line_tab/tab.png",
    platform="line_tab"  # 96x74
)
```

### Full CLI Reference

```bash
# LINE only (most common)
python sticker_processor.py input/ output/ line line_main line_tab --skip-bg

# All platforms
python sticker_processor.py input/ output/ \
    line line_main line_tab \
    whatsapp telegram \
    imessage_large \
    print_etsy \
    --skip-bg

# With background removal (first-time processing of raw images)
python sticker_processor.py input/ output/ line line_main line_tab

# Custom outline width (default is 10)
# Edit StickerProcessor instantiation in the script:
# processor = StickerProcessor(outline_width=8)
```

---

## Complete Pipeline: run_pipeline.py

For automated end-to-end processing, `run_pipeline.py` chains all stages:

```bash
# Process-only mode (no DALL-E generation)
python run_pipeline.py --process-only --input packs/boba-milo-5

# Full pipeline (generate + process)
python run_pipeline.py --input packs/boba-milo-5

# Generate only (DALL-E, no processing)
python run_pipeline.py --generate-only

# With Telegram publishing
python run_pipeline.py --process-only --input packs/boba-milo-5 --telegram

# With iMessage Xcode project generation
python run_pipeline.py --process-only --input packs/boba-milo-5 --imessage
```

### Pipeline Stages

| Stage        | Script                     | Description                         | Skippable?        |
| ------------ | -------------------------- | ----------------------------------- | ----------------- |
| 1. Generate  | `image_generator.py`       | DALL-E 3 API generation             | `--process-only`  |
| 2. Process   | `sticker_processor.py`     | Resize, outline, optimize           | `--generate-only` |
| 3. Tray Icon | `sticker_processor.py`     | WhatsApp tray / LINE tab            | Auto              |
| 4. Metadata  | Internal                   | JSON metadata per platform          | Auto              |
| 5. Package   | `create_print_sheet.py`    | Print sheets, social previews, ZIPs | Auto              |
| 6. Telegram  | `telegram_publisher.py`    | Publish to Telegram                 | `--telegram` flag |
| 7. iMessage  | `prepare_imessage_pack.py` | Xcode project generation            | `--imessage` flag |

---

## Verification Commands

After processing, verify the output meets LINE requirements:

```bash
# Check file count (should be 8 for stickers)
ls packs/<pack>/final/line/ | wc -l

# Check dimensions of all sticker files (requires ImageMagick)
for f in packs/<pack>/final/line/*.png; do
    identify -format "%f: %wx%h\n" "$f"
done
# All should be ≤370x≤320 with even dimensions

# Check main image dimension
identify packs/<pack>/final/line_main/01_*.png
# Should be exactly 240x240

# Check tab image dimension
identify packs/<pack>/final/line_tab/01_*.png
# Should be exactly 96x74

# Check all files are under 1MB
ls -la packs/<pack>/final/line/
ls -la packs/<pack>/final/line_main/
ls -la packs/<pack>/final/line_tab/
# All file sizes should be < 1,048,576 bytes

# Check for transparency (alpha channel present)
identify -verbose packs/<pack>/final/line/01_*.png | grep -i "alpha"
# Should show "Alpha" channel
```
