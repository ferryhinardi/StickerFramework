# Module Reference

Detailed API reference for every module in StickerFramework.

---

## `run_pipeline.py`

**Purpose**: Master orchestrator that coordinates all pipeline stages.

### Functions

#### `stage_generate(config, output_dir, quality)`
Generates raw sticker images using DALL-E 3.

| Parameter | Type | Description |
|-----------|------|-------------|
| `config` | dict | Pack configuration from `pack_config.py` |
| `output_dir` | str | Path to output directory |
| `quality` | str | `"hd"` or `"standard"` |

**Returns**: Path to `raw/` directory containing generated PNGs.

#### `stage_process(raw_dir, output_dir, platforms, skip_bg)`
Processes raw images into platform-ready stickers.

| Parameter | Type | Description |
|-----------|------|-------------|
| `raw_dir` | str | Path to raw images |
| `output_dir` | str | Path to output base directory |
| `platforms` | list | Target platforms (e.g., `["whatsapp", "telegram"]`) |
| `skip_bg` | bool | Skip background removal |

**Returns**: Path to `final/` directory.

#### `stage_tray_icon(final_dir, output_dir)`
Creates 96x96 tray/tab icons from the first sticker.

#### `stage_metadata(config, final_dir, output_dir)`
Generates JSON metadata files for WhatsApp, Telegram, LINE, and a pack summary.

#### `stage_package(config, final_dir, output_dir)`
Creates print sheets (US Letter + A4), social preview image, and distribution ZIP.

### CLI Entry Point

```
python run_pipeline.py [--process-only] [--generate-only] [--input DIR]
                       [--skip-bg] [--standard] [--telegram] [--imessage]
```

---

## `image_generator.py`

**Purpose**: Generates sticker images using OpenAI's DALL-E 3 API.

### Class: `StickerGenerator`

#### `__init__(api_key: str)`
Initializes the generator with an OpenAI API key.

| Parameter | Type | Description |
|-----------|------|-------------|
| `api_key` | str | OpenAI API key |

#### `build_prompt(character: dict, style: dict, sticker: dict) -> str`
Constructs a structured DALL-E prompt from config components.

**Prompt structure:**
```
CHARACTER: {species}, {colors}, {eye_style}, {proportions}
THIS STICKER: {emotion}, {pose}, {props}
MANDATORY STYLE RULES: {outline}, {colors}, {background}, {format}
```

**Returns**: A detailed prompt string optimized for consistent character generation.

#### `generate_sticker(character, style, sticker, output_dir, size, quality, max_retries) -> str`
Generates a single sticker image.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `character` | dict | - | Character definition |
| `style` | dict | - | Style rules |
| `sticker` | dict | - | Individual sticker config |
| `output_dir` | str | - | Output path |
| `size` | str | `"1024x1024"` | Image dimensions |
| `quality` | str | `"hd"` | `"hd"` ($0.08) or `"standard"` ($0.04) |
| `max_retries` | int | `3` | Max retry attempts |

**Returns**: Path to the saved PNG file.

**Error handling**:
- Rate limiting: Waits and retries
- Content policy: Logs and skips
- Download failure: Retries up to `max_retries`

**Side effects**: Also saves `<sticker_id>_prompt.txt` with original and DALL-E revised prompts.

#### `generate_pack(config: dict, delay_between: int, quality: str) -> list`
Generates all stickers in a pack with rate-limit delays.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `config` | dict | - | Full pack configuration |
| `delay_between` | int | `12` | Seconds between API calls |
| `quality` | str | `"hd"` | Image quality |

**Returns**: List of paths to generated images.

#### `generate_reference_sheet(character: dict, output_path: str) -> str`
Creates a 1792x1024 character reference sheet showing 6 poses. Useful for verifying character consistency before a full generation run.

---

## `sticker_processor.py`

**Purpose**: Multi-platform image processing pipeline.

### Class: `StickerProcessor`

#### Platform Specifications (`SPECS`)

```python
SPECS = {
    "whatsapp":       {"size": (512, 512),  "format": "WEBP", "max_kb": 100},
    "whatsapp_tray":  {"size": (96, 96),    "format": "WEBP", "max_kb": 50},
    "telegram":       {"size": (512, 512),  "format": "WEBP", "max_kb": 256},
    "imessage_small": {"size": (300, 300),  "format": "PNG",  "max_kb": 500},
    "imessage_medium":{"size": (408, 408),  "format": "PNG",  "max_kb": 500},
    "imessage_large": {"size": (618, 618),  "format": "PNG",  "max_kb": 500},
    "line":           {"size": (370, 320),  "format": "PNG",  "max_kb": 1000},
    "line_main":      {"size": (240, 240),  "format": "PNG",  "max_kb": 1000},
    "line_tab":       {"size": (96, 74),    "format": "PNG",  "max_kb": 1000},
    "print_etsy":     {"size": (2048, 2048),"format": "PNG",  "max_kb": None},
}
```

#### `remove_background(input_path: str) -> PIL.Image`
AI-powered background removal using rembg (U2-Net model).

| Parameter | Type | Description |
|-----------|------|-------------|
| `input_path` | str | Path to input image |

**Returns**: PIL Image with transparent background (RGBA mode).

**Note**: First run downloads the U2-Net model (~170MB).

#### `add_white_outline(img: PIL.Image, width: int) -> PIL.Image`
Creates a die-cut style white border using alpha channel dilation.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `img` | PIL.Image | - | RGBA image |
| `width` | int | `8` | Outline width in pixels |

**Algorithm**: Applies `MaxFilter` iteratively to the alpha channel to expand it, then composites the original image on top of the white-filled expanded region.

**Returns**: Image with white outline border.

#### `normalize_colors(img: PIL.Image, saturation, brightness, contrast) -> PIL.Image`
Adjusts color properties for consistent kawaii vibrancy.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `img` | PIL.Image | - | Input image |
| `saturation` | float | `1.15` | Saturation multiplier |
| `brightness` | float | `1.05` | Brightness multiplier |
| `contrast` | float | `1.05` | Contrast multiplier |

**Returns**: Color-adjusted image.

#### `resize_to_spec(img: PIL.Image, platform: str) -> PIL.Image`
Resizes image to platform dimensions with transparent padding.

**Behavior**: Fits image to 90% of target dimensions (maintaining aspect ratio), then centers on a transparent canvas of the exact platform dimensions.

#### `save_optimized(img: PIL.Image, output_path: str, platform: str) -> str`
Format-specific optimization and saving.

**WebP optimization**: Uses binary search on quality (1-95) to find the highest quality that fits under `max_kb`.

**PNG optimization**: Uses Pillow's `optimize=True` flag. If still over `max_kb`, applies color quantization (256 colors).

#### `process_single(input_path, output_dir, platforms, skip_bg_removal) -> dict`
Full 4-step pipeline for one image.

**Pipeline steps**:
1. `remove_background()` (unless `skip_bg_removal=True`)
2. `normalize_colors()`
3. `add_white_outline()`
4. `resize_to_spec()` + `save_optimized()` for each platform

**Returns**: Dictionary mapping platform names to output file paths.

#### `process_batch(input_dir, output_dir, platforms, skip_bg_removal) -> list`
Processes all PNG/JPG/JPEG/WebP images in a directory.

**Returns**: List of result dicts from `process_single()`.

#### `create_tray_icon(source_path, output_path, platform) -> str`
Creates a tray/tab icon from an existing processed sticker.

---

## `pack_config.py`

**Purpose**: Central configuration defining character, style, and sticker pack contents.

### Constants

#### `CHARACTER` (dict)
Character definition with the following keys:

| Key | Type | Example | Description |
|-----|------|---------|-------------|
| `name` | str | `"Mochi"` | Character name |
| `species` | str | `"Round cat"` | Species description |
| `body_color` | str | `"#FFB6C1"` | Primary body color |
| `blush_color` | str | `"#FF69B4"` | Blush accent color |
| `outline_color` | str | `"#333333"` | Outline color |
| `eye_style` | str | `"Simple black oval..."` | Eye description |
| `accessory` | str | `"Tiny gold star pin..."` | Accessory description |
| `proportions` | str | `"Chibi, head is 60%..."` | Body proportions |

#### `STYLE` (dict)
Art direction rules:

| Key | Type | Description |
|-----|------|-------------|
| `outline` | str | Outline weight and style |
| `colors` | str | Color mode (flat, no gradients) |
| `background` | str | Background requirement |
| `format` | str | Output format rules |

#### `PACK_CONFIG` (dict)
Pack metadata:

| Key | Type | Description |
|-----|------|-------------|
| `pack_id` | str | Unique identifier (e.g., `"pack01_emotions_v1"`) |
| `pack_name` | str | Display name |
| `publisher` | str | Publisher/brand name |
| `character` | dict | Reference to CHARACTER |
| `style` | dict | Reference to STYLE |
| `stickers` | list | List of 24 sticker definitions |
| `platforms` | list | Target platforms |

#### Sticker Definition (each item in `stickers` list)

| Key | Type | Description |
|-----|------|-------------|
| `id` | str | Sticker identifier (e.g., `"01_happy"`) |
| `emotion` | str | Emotion name |
| `pose` | str | Body pose description |
| `props` | str | Props and visual effects |
| `emoji` | str | Associated emoji |

### Functions

#### `create_pack_config() -> dict`
Factory function to create additional pack configs reusing the same character and style definitions. Returns a new config dictionary.

---

## `create_print_sheet.py`

**Purpose**: Creates print-ready layouts and distribution packages.

### Functions

#### `create_sticker_sheet(sticker_dir, output_path, page_size, cols, sticker_size, padding, dpi, bg_color, title) -> str`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `sticker_dir` | str | - | Directory of sticker images |
| `output_path` | str | - | Output file path |
| `page_size` | str | `"letter"` | `"letter"` (2550x3300) or `"a4"` (2480x3508) |
| `cols` | int | `4` | Number of columns |
| `sticker_size` | int | `None` | Override sticker size (auto if None) |
| `padding` | int | `40` | Padding between stickers (px) |
| `dpi` | int | `300` | Output DPI |
| `bg_color` | str | `"white"` | Background color |
| `title` | str | `None` | Optional title text |

**Returns**: Path to the generated sheet image.

#### `create_social_preview(sticker_dir, output_path, title, subtitle) -> str`
Creates a 3000x3000 social media preview with a 3x3 sticker grid on a light purple (#F5F0FF) background. Suitable for Etsy listings and Instagram.

#### `create_distribution_zip(pack_id, pack_name, sticker_dir, sheet_paths, output_path, publisher) -> str`
Creates a ZIP file containing:
- `stickers/` - Individual sticker files
- `print_sheets/` - Print-ready layouts
- `README.txt` - Usage instructions
- `LICENSE.txt` - Personal use license

---

## `prepare_imessage_pack.py`

**Purpose**: Generates Xcode Sticker Pack Application project structure.

### Functions

#### `prepare_imessage_assets(processed_dir, xcode_stickerpack_dir, grid_size) -> int`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `processed_dir` | str | - | Directory of processed PNG stickers |
| `xcode_stickerpack_dir` | str | - | Xcode `.stickerpack` directory path |
| `grid_size` | str | `"regular"` | `"small"` (300px), `"regular"` (408px), `"large"` (618px) |

**Returns**: Number of stickers added.

**Creates**: For each sticker, a `.sticker/` subdirectory containing the image and a `Contents.json` manifest.

#### `create_xcode_project(project_name, sticker_dir, bundle_id_prefix, output_dir) -> str`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `project_name` | str | - | Xcode project name |
| `sticker_dir` | str | - | Directory of processed stickers |
| `bundle_id_prefix` | str | `"com.yourbrand"` | Bundle ID prefix |
| `output_dir` | str | - | Output directory |

**Returns**: Path to the created Xcode project.

**Creates**:
- `<name>.xcodeproj/project.pbxproj`
- `Stickers.xcstickers/` with icon set and sticker pack
- `Info.plist` with StickerPackExtension configuration

**Manual steps required after generation**:
1. Open project in Xcode
2. Add app icons (various sizes)
3. Configure signing (Apple Developer account)
4. Archive and submit to App Store Connect

---

## `telegram_publisher.py`

**Purpose**: Publishes sticker packs to Telegram via Bot API.

### Class: `TelegramStickerPublisher`

#### `__init__(bot_token: str)`
Initialize with a Telegram Bot token from `@BotFather`.

#### `get_bot_info() -> dict`
Verifies bot token validity. Returns bot info dict.

#### `create_sticker_set(user_id, name, title, sticker_paths, emojis_list, sticker_format) -> bool`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `user_id` | int | - | Telegram user ID |
| `name` | str | - | Sticker set short name |
| `title` | str | - | Sticker set display title |
| `sticker_paths` | list | - | List of WebP file paths |
| `emojis_list` | list | - | List of emoji strings per sticker |
| `sticker_format` | str | `"static"` | `"static"` or `"animated"` |

**Returns**: `True` on success.

**Behavior**: 
- Automatically appends `_by_<botname>` to the set name (Telegram requirement)
- Tries batch creation first
- Falls back to sequential creation (first sticker creates set, remaining added one-by-one)

#### `delete_sticker_set(name: str) -> bool`
Deletes an entire sticker set. Useful for recreating sets during development.

### Helper Functions

#### `load_emojis_from_config(pack_config: dict) -> list`
Extracts ordered emoji list from pack configuration. Returns list of emoji strings.

---

## `split_stickers.py`

**Purpose**: Standalone utility to split a multi-sticker sheet image into individual PNGs.

### Functions

#### `remove_white_background(img: PIL.Image, threshold: int) -> PIL.Image`
Converts white/near-white pixels to transparent.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `img` | PIL.Image | - | Input image |
| `threshold` | int | `240` | RGB threshold (pixels above this become transparent) |

#### `find_sticker_bboxes(img: PIL.Image, min_size: int) -> list`
Detects individual sticker regions using connected component analysis.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `img` | PIL.Image | - | Image with transparent background |
| `min_size` | int | `50` | Minimum region size to be considered a sticker |

**Algorithm**: Uses `scipy.ndimage.label` on non-transparent pixels, filters by size, sorts top-to-bottom then left-to-right.

**Returns**: List of bounding box tuples `(x1, y1, x2, y2)`.

#### `crop_and_resize(img: PIL.Image, bbox: tuple, target_size: int, padding: int) -> PIL.Image`
Crops a sticker region and resizes to standard dimensions.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `img` | PIL.Image | - | Source image |
| `bbox` | tuple | - | Bounding box `(x1, y1, x2, y2)` |
| `target_size` | int | `512` | Target canvas size |
| `padding` | int | `10` | Padding around the sticker |

**Returns**: 512x512 PNG with the sticker centered on a transparent background.
