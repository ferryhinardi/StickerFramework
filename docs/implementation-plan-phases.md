# StickerFramework — Phased Implementation Plan

> Three-phase expansion: iMessage full automation, Telegram animated/video stickers, WhatsApp native app.

---

## Table of Contents

- [Phase 0: Shared Infrastructure](#phase-0-shared-infrastructure)
- [Phase 1: iMessage Full Automation (Fastlane)](#phase-1-imessage-full-automation-fastlane)
- [Phase 2: Telegram Animated & Video Stickers](#phase-2-telegram-animated--video-stickers)
- [Phase 3: WhatsApp Native App](#phase-3-whatsapp-native-app)
- [Dependency Graph](#dependency-graph)
- [Timeline Summary](#timeline-summary)

---

## Phase 0: Shared Infrastructure

**Goal:** Prepare shared config, env vars, and pack_config extensions that all three phases need.

**Estimated Complexity:** Simple

### 0.1 Extend `.env.example` with new variables

**File:** `.env.example` (modify)

Add:

```dotenv
# ─── Phase 1: iMessage / Fastlane ───
APPLE_ID=your-apple-id@example.com
APPLE_TEAM_ID=XXXXXXXXXX
APPLE_APP_SPECIFIC_PASSWORD=xxxx-xxxx-xxxx-xxxx
MATCH_GIT_URL=https://github.com/yourorg/certificates.git
MATCH_PASSWORD=your-match-encryption-password
BUNDLE_ID_PREFIX=com.yourbrand

# ─── Phase 2: Telegram Animated ───
# (uses existing TELEGRAM_BOT_TOKEN / TELEGRAM_USER_ID)
FFMPEG_PATH=ffmpeg

# ─── Phase 3: WhatsApp Server ───
WHATSAPP_SERVER_URL=https://stickers.yourdomain.com
WHATSAPP_SERVER_API_KEY=your-api-key
```

### 0.2 Extend `pack_config.py` with per-sticker animation hints

**File:** `scripts/pack_config.py` (modify)

Add an optional `animation` dict to each sticker entry:

```python
# In each sticker dict, add (optional — ignored if not doing animated):
{
    "id": "01_happy",
    "emotion": "Happy",
    "pose": "...",
    "props": "...",
    "emoji": "😊",
    # NEW — Phase 2 animation hints
    "animation": {
        "type": "bounce",          # bounce, shake, pulse, spin, wave, custom
        "duration_ms": 2000,       # max 3000
        "loop": True,
    },
}
```

Also add platform flags to the top-level config:

```python
PACK_CONFIG = {
    ...
    "platforms": [
        "whatsapp",
        "telegram",
        "telegram_animated",   # NEW
        "telegram_video",      # NEW
        "imessage_large",
        "line",
        "print_etsy",
    ],
}
```

### 0.3 Add new platform specs to `sticker_processor.py`

**File:** `scripts/sticker_processor.py` (modify)

Add these entries to `StickerProcessor.SPECS`:

```python
"telegram_animated": {
    "size": (512, 512),
    "format": "TGS",       # Lottie JSON gzipped
    "max_kb": 64,
    "ext": ".tgs",
},
"telegram_video": {
    "size": (512, 512),
    "format": "WEBM",      # VP9, no audio
    "max_kb": 256,
    "ext": ".webm",
},
"whatsapp_native": {
    "size": (512, 512),
    "format": "WEBP",
    "max_kb": 100,
    "ext": ".webp",
},
"whatsapp_native_tray": {
    "size": (96, 96),
    "format": "PNG",        # WhatsApp native app uses PNG tray
    "max_kb": 50,
    "ext": ".png",
},
```

### 0.4 Update `requirements.txt`

**File:** `requirements.txt` (modify)

Add:

```
# Phase 1: iMessage Fastlane (Ruby gem, not pip — documented here for reference)
# gem install fastlane

# Phase 2: Telegram animated/video
lottie-py>=0.4.0         # Lottie animation creation
cairosvg>=2.7.0          # SVG rendering for Lottie frames

# Phase 3: WhatsApp server
fastapi>=0.104.0
uvicorn>=0.24.0
python-multipart>=0.0.6
```

### 0.5 Verification

- Run `python -c "from scripts.sticker_processor import StickerProcessor; print(list(StickerProcessor.SPECS.keys()))"` — confirm new specs appear.
- Validate `.env.example` loads without errors.

---

## Phase 1: iMessage Full Automation (Fastlane)

**Goal:** Take the current `prepare_imessage_pack.py` (generates Xcode directory structure) and extend it into a fully automated pipeline: generate project → build → code-sign → upload → submit to App Store.

**Estimated Complexity:** Complex

**Current state:** `scripts/prepare_imessage_pack.py` (270 lines) creates `.xcstickers`, `.stickerpack`, `Contents.json`, and `Info.plist` — but the Xcode project file (`project.pbxproj`) is an empty directory. Building requires opening Xcode manually.

### 1.0 Prerequisites & Setup

#### 1.0.1 Apple Developer Account (manual, one-time)

1. Go to https://developer.apple.com/programs/
2. Enroll in Apple Developer Program ($99/year)
3. Complete identity verification (may take 24–48 hours)
4. After approval, note your **Team ID** from https://developer.apple.com/account/#/membership
5. Create an **App-Specific Password** at https://appleid.apple.com/account/manage → Security → App-Specific Passwords
6. Set env vars:
   ```bash
   export APPLE_ID="you@example.com"
   export APPLE_TEAM_ID="XXXXXXXXXX"
   export APPLE_APP_SPECIFIC_PASSWORD="xxxx-xxxx-xxxx-xxxx"
   ```

#### 1.0.2 Install Fastlane

```bash
# Option A: Homebrew (recommended on macOS)
brew install fastlane

# Option B: RubyGems
sudo gem install fastlane -NV

# Verify
fastlane --version
```

#### 1.0.3 Create a certificates Git repo (for Fastlane Match)

1. Create a **private** GitHub repo: `github.com/yourorg/certificates`
2. Set env vars:
   ```bash
   export MATCH_GIT_URL="https://github.com/yourorg/certificates.git"
   export MATCH_PASSWORD="a-strong-encryption-passphrase"
   ```

#### 1.0.4 Register App ID on Apple Developer Portal

This is automated by Fastlane `produce`, but needs initial setup:

```bash
fastlane produce create \
  --app_identifier "com.yourbrand.packname.StickerPackExtension" \
  --app_name "Mochi Emotions Stickers" \
  --team_id "$APPLE_TEAM_ID" \
  --username "$APPLE_ID" \
  --sku "mochi-emotions-stickers-001"
```

> **Note:** iMessage sticker packs are distributed as the extension of a containing app. You need **two** bundle IDs: `com.yourbrand.packname` (containing app) and `com.yourbrand.packname.StickerPackExtension` (extension).

### 1.1 New Files to Create

#### 1.1.1 `fastlane/Gemfile`

**Path:** `fastlane/Gemfile`

```ruby
source "https://rubygems.org"

gem "fastlane", "~> 2.220"

plugins_path = File.join(File.dirname(__FILE__), 'fastlane', 'Pluginfile')
eval_gemfile(plugins_path) if File.exist?(plugins_path)
```

#### 1.1.2 `fastlane/Pluginfile`

**Path:** `fastlane/Pluginfile`

```ruby
# No plugins needed for basic sticker pack workflow
```

#### 1.1.3 `fastlane/Appfile`

**Path:** `fastlane/Appfile`

```ruby
app_identifier ENV["BUNDLE_ID"] || "com.yourbrand.stickers"
apple_id ENV["APPLE_ID"]
team_id ENV["APPLE_TEAM_ID"]
```

#### 1.1.4 `fastlane/Matchfile`

**Path:** `fastlane/Matchfile`

```ruby
git_url ENV["MATCH_GIT_URL"]
storage_mode "git"
type "appstore"
app_identifier [
  ENV["BUNDLE_ID"] || "com.yourbrand.stickers",
  "#{ENV['BUNDLE_ID'] || 'com.yourbrand.stickers'}.StickerPackExtension"
]
username ENV["APPLE_ID"]
team_id ENV["APPLE_TEAM_ID"]
```

#### 1.1.5 `fastlane/Fastfile`

**Path:** `fastlane/Fastfile`

```ruby
default_platform(:ios)

platform :ios do
  desc "Sync code signing certificates via match"
  lane :certs do
    match(type: "appstore", readonly: true)
  end

  desc "Build the iMessage sticker pack"
  lane :build do |options|
    project_path = options[:project] || ENV["XCODE_PROJECT"]

    unless project_path
      UI.user_error!("Pass project: path or set XCODE_PROJECT env var")
    end

    match(type: "appstore", readonly: true)

    gym(
      project: project_path,
      scheme: File.basename(project_path, ".xcodeproj"),
      export_method: "app-store",
      output_directory: "./build",
      output_name: "StickerPack.ipa",
      clean: true,
      include_bitcode: false,
      xcargs: "-allowProvisioningUpdates"
    )
  end

  desc "Upload to App Store Connect (without submitting for review)"
  lane :upload do
    deliver(
      ipa: "./build/StickerPack.ipa",
      skip_metadata: false,
      skip_screenshots: false,
      force: true,                      # Skip HTML report verification
      submit_for_review: false,         # Upload only, don't submit
      automatic_release: false,
      precheck_include_in_app_purchases: false,
      metadata_path: "./fastlane/metadata",
      screenshots_path: "./fastlane/screenshots"
    )
  end

  desc "Submit for App Store review"
  lane :submit do
    deliver(
      skip_binary_upload: true,
      skip_metadata: true,
      skip_screenshots: true,
      submit_for_review: true,
      automatic_release: true,
      submission_information: {
        add_id_info_uses_idfa: false
      }
    )
  end

  desc "Full pipeline: certs → build → upload → submit"
  lane :publish do |options|
    certs
    build(options)
    upload
    submit
  end
end
```

#### 1.1.6 `fastlane/metadata/en-US/` directory tree

**Path:** Create directory `fastlane/metadata/en-US/` with these template files:

| File | Content |
|------|---------|
| `name.txt` | `{pack_name} Stickers` |
| `subtitle.txt` | `Cute sticker pack for iMessage` |
| `description.txt` | Template with pack description |
| `keywords.txt` | `stickers,imessage,cute,kawaii,emoji,chat` |
| `privacy_url.txt` | `https://yourdomain.com/privacy` |
| `support_url.txt` | `https://yourdomain.com/support` |
| `marketing_url.txt` | `https://yourdomain.com` |
| `release_notes.txt` | `Initial release with {N} stickers.` |

#### 1.1.7 `templates/imessage_metadata.json`

**Path:** `templates/imessage_metadata.json`

```json
{
  "app_name": "{pack_name} Stickers",
  "subtitle": "Cute sticker pack for iMessage",
  "description": "Express yourself with {sticker_count} adorable {character_name} stickers! Perfect for everyday conversations.\n\nFeatures:\n• {sticker_count} unique stickers\n• Transparent backgrounds\n• Works in iMessage conversations\n• High-quality PNG format",
  "keywords": "stickers,imessage,cute,kawaii,emoji,chat,{character_name}",
  "category": "Stickers",
  "price_tier": "0",
  "primary_locale": "en-US",
  "privacy_url": "https://yourdomain.com/privacy",
  "support_url": "https://yourdomain.com/support"
}
```

#### 1.1.8 `scripts/imessage_publisher.py` — The main automation script

**Path:** `scripts/imessage_publisher.py` (new, ~350 lines)

This is the core deliverable. It orchestrates the full pipeline:

```
generate Xcode project (existing) → generate pbxproj → generate metadata
    → generate app icons → run fastlane build → upload → submit
```

**Responsibilities:**

1. **Generate a real `project.pbxproj`** — The current `prepare_imessage_pack.py` creates an empty `.xcodeproj` dir. This script must generate a valid `.pbxproj` file for a Sticker Pack Application target. Use the `pbxproj` Python library (`pip install pbxproj`) or template a known-good pbxproj.

2. **Generate App Icons** — Resize the first sticker (or a dedicated icon image) into all required icon sizes (29x29@2x, 60x45@2x, 60x45@3x, 67x50@2x, 74x55@2x, 27x20@2x, 27x20@3x, 1024x768@1x) and populate `iMessage App Icon.stickersiconset/Contents.json`.

3. **Populate `fastlane/metadata/`** — Fill template files from `imessage_metadata.json` + pack_config.

4. **Generate screenshots** — Create composite images showing stickers in an iMessage conversation mockup (6.7" iPhone, 6.5" iPhone, and iPad sizes as required by App Store).

5. **Invoke Fastlane** — Call `fastlane publish` via subprocess.

**Key implementation detail — `project.pbxproj` generation:**

The simplest reliable approach is to use a **template pbxproj**. iMessage Sticker Pack apps have a minimal, predictable project structure. The script will:

1. Start from a template `project.pbxproj` stored at `templates/imessage_project.pbxproj.template`
2. Replace placeholders: `{{PROJECT_NAME}}`, `{{BUNDLE_ID}}`, `{{TEAM_ID}}`, `{{STICKER_FILES}}`
3. Generate the file reference and build file entries for each `.sticker` directory

**Alternative approach:** Use `xcodegen` (a tool that generates Xcode projects from a YAML spec). Install via `brew install xcodegen`.

#### 1.1.9 `templates/imessage_project.yml` (for xcodegen approach)

**Path:** `templates/imessage_project.yml`

```yaml
name: "{{PROJECT_NAME}}"
options:
  bundleIdPrefix: "{{BUNDLE_ID_PREFIX}}"
  deploymentTarget:
    iOS: "16.0"
settings:
  DEVELOPMENT_TEAM: "{{TEAM_ID}}"
targets:
  "{{PROJECT_NAME}} StickerPackExtension":
    type: com.apple.product-type.app-extension.messages-sticker-pack
    platform: iOS
    sources:
      - path: Stickers.xcstickers
    settings:
      INFOPLIST_FILE: Info.plist
      PRODUCT_BUNDLE_IDENTIFIER: "{{BUNDLE_ID}}.StickerPackExtension"
      ASSETCATALOG_COMPILER_STICKER_PACK_IDENTIFIER_PREFIX: "{{BUNDLE_ID}}.StickerPackExtension.StickerPack"
      CODE_SIGN_STYLE: Manual
      PROVISIONING_PROFILE_SPECIFIER: "match AppStore {{BUNDLE_ID}}.StickerPackExtension"
  "{{PROJECT_NAME}}":
    type: application
    platform: iOS
    settings:
      INFOPLIST_FILE: Info.plist
      PRODUCT_BUNDLE_IDENTIFIER: "{{BUNDLE_ID}}"
      CODE_SIGN_STYLE: Manual
      PROVISIONING_PROFILE_SPECIFIER: "match AppStore {{BUNDLE_ID}}"
    dependencies:
      - target: "{{PROJECT_NAME}} StickerPackExtension"
```

### 1.2 Existing Files to Modify

| File | Change |
|------|--------|
| `scripts/prepare_imessage_pack.py` | Add `generate_app_icons()` function; refactor `create_xcode_project()` to accept icon source path; add xcodegen YAML generation |
| `scripts/run_pipeline.py` | Add `--imessage-publish` flag that calls `imessage_publisher.py` full pipeline |
| `.gitignore` | Add `build/`, `fastlane/report.xml`, `*.ipa`, `*.dSYM.zip` |
| `requirements.txt` | Add `pbxproj>=4.0` (if using pbxproj approach) |

### 1.3 Dependencies & Tools

| Tool | Install | Purpose |
|------|---------|---------|
| Xcode (15+) | Mac App Store | Build toolchain |
| Fastlane | `brew install fastlane` | Build, sign, upload |
| xcodegen | `brew install xcodegen` | Generate .xcodeproj from YAML |
| Pillow (existing) | Already in requirements | Icon resizing |

### 1.4 Implementation Steps (Ordered)

1. **Set up Apple Developer Account** — Enroll, wait for approval, get Team ID
2. **Create certificates repo** — Private GitHub repo for Fastlane Match
3. **Create `fastlane/` directory** — Gemfile, Appfile, Matchfile, Fastfile
4. **Create metadata templates** — `fastlane/metadata/en-US/*.txt`, `templates/imessage_metadata.json`
5. **Create `templates/imessage_project.yml`** — xcodegen spec template
6. **Install xcodegen** — `brew install xcodegen`
7. **Modify `prepare_imessage_pack.py`** — Add `generate_app_icons()`, add xcodegen YAML output, add `--full` flag
8. **Create `scripts/imessage_publisher.py`** — Main orchestrator:
   - Accept pack config + sticker dir
   - Call `prepare_imessage_pack.create_xcode_project()` (existing)
   - Generate xcodegen YAML from template → run `xcodegen generate`
   - Generate app icons via Pillow
   - Populate fastlane metadata from pack config
   - Generate App Store screenshots (sticker grid composite)
   - Run `fastlane publish`
9. **Wire into `run_pipeline.py`** — Add `--imessage-publish` flag
10. **Test with a real pack** — Build, sign, upload to TestFlight first

### 1.5 Verification & Testing

| Test | How |
|------|-----|
| Xcode project builds | `xcodebuild -project Pack.xcodeproj -scheme Pack build` |
| Match fetches certs | `fastlane certs` — should download/create profiles |
| IPA builds | `fastlane build project:Pack.xcodeproj` — produces `build/StickerPack.ipa` |
| Upload succeeds | `fastlane upload` — check App Store Connect for the build |
| Metadata appears | Log into App Store Connect → verify name, description, screenshots |
| End-to-end | `python imessage_publisher.py packs/pack01/final/imessage_large "MochiEmotions"` |
| Icon sizes correct | Inspect generated icons — all 9 sizes present in `.stickersiconset` |

### 1.6 Risk & Mitigation

| Risk | Mitigation |
|------|------------|
| `project.pbxproj` generation is fragile | Use xcodegen instead of raw pbxproj templating |
| Apple review rejection | Include proper privacy policy URL, avoid trademark issues |
| Code signing failures | Use `match` with `readonly: true` after initial setup |
| First-time Fastlane auth is interactive | Document the one-time `fastlane spaceauth` session |

---

## Phase 2: Telegram Animated & Video Stickers

**Goal:** Extend the current `telegram_publisher.py` (static WebP only) to support animated (TGS/Lottie) and video (WebM VP9) sticker formats.

**Estimated Complexity:** Medium

**Current state:** `scripts/telegram_publisher.py` (301 lines) uses `createNewStickerSet` and `addStickerToSet` with `sticker_format="static"`. The `sticker_format` parameter already exists in the code and accepts `"animated"` or `"video"` — but no conversion utilities exist.

### 2.0 Prerequisites

#### 2.0.1 Install ffmpeg

```bash
# macOS
brew install ffmpeg

# Verify VP9/WebM support
ffmpeg -encoders 2>/dev/null | grep vp9
# Should show: V..... libvpx-vp9
```

#### 2.0.2 Install Python dependencies

```bash
pip install lottie-py cairosvg
```

#### 2.0.3 Telegram format reference

| Format | File Ext | Codec | Max Size | Dimensions | Duration | FPS |
|--------|----------|-------|----------|------------|----------|-----|
| Static | `.webp` | WebP | 256 KB | 512x512 | — | — |
| Animated | `.tgs` | Lottie+gzip | 64 KB | 512x512 | 3 sec | 60 |
| Video | `.webm` | VP9 | 256 KB | 512x512 | 3 sec | 30 |

### 2.1 New Files to Create

#### 2.1.1 `scripts/animated_converter.py` (~300 lines)

**Path:** `scripts/animated_converter.py`

This module provides two conversion pipelines:

**A) Static PNG → TGS (animated Lottie):**

```python
class LottieAnimator:
    """Convert static sticker PNGs into animated TGS (Lottie) files."""

    # Predefined animation presets
    PRESETS = {
        "bounce": {...},   # Vertical bounce with squash/stretch
        "shake": {...},    # Horizontal wiggle
        "pulse": {...},    # Scale up/down heartbeat
        "spin": {...},     # 360° rotation
        "wave": {...},     # Sine wave wobble
        "pop_in": {...},   # Scale from 0 to 100% with overshoot
        "float": {...},    # Gentle up/down floating
    }

    def png_to_tgs(
        self,
        png_path: str,
        output_path: str,
        animation_type: str = "bounce",
        duration_ms: int = 2000,
        loop: bool = True,
    ) -> Path:
        """
        Convert a static PNG sticker to animated TGS format.

        Process:
        1. Trace PNG alpha channel to vector paths (simplified)
        2. OR: Embed PNG as base64 image asset in Lottie
        3. Apply animation transform (position, scale, rotation keyframes)
        4. Serialize to Lottie JSON
        5. Gzip compress (must be ≤64KB)

        The most reliable approach for photographic/AI-generated stickers:
        - Embed the rasterized image as a Lottie image asset
        - Animate the transform properties (position, scale, opacity, rotation)
        - This avoids lossy vectorization of complex artwork
        """
        ...

    def _build_lottie_json(
        self, image_data: bytes, w: int, h: int,
        keyframes: list[dict], duration_frames: int, fps: int = 60,
    ) -> dict:
        """Build a complete Lottie JSON structure with embedded image."""
        ...

    def _compress_to_tgs(self, lottie_json: dict, output_path: str) -> Path:
        """Gzip compress Lottie JSON to .tgs, verify ≤64KB."""
        ...
```

**B) Static PNG/GIF/MP4 → WebM VP9 (video sticker):**

```python
class VideoConverter:
    """Convert images/videos to Telegram video sticker format (WebM VP9)."""

    def png_to_webm(
        self,
        png_path: str,
        output_path: str,
        animation_type: str = "bounce",
        duration_sec: float = 2.0,
        fps: int = 30,
    ) -> Path:
        """
        Convert static PNG to animated WebM video sticker.

        Process:
        1. Generate animation frames (apply transform per frame)
        2. Encode frames as WebM VP9 via ffmpeg
        3. Verify: ≤256KB, ≤3s, 512x512, VP9, no audio

        Uses ffmpeg subprocess:
            ffmpeg -framerate 30 -i frames/%04d.png \
                   -c:v libvpx-vp9 -pix_fmt yuva420p \
                   -b:v 400k -minrate 100k -maxrate 500k \
                   -an -t 3 -s 512x512 \
                   output.webm
        """
        ...

    def gif_to_webm(self, gif_path: str, output_path: str) -> Path:
        """Convert animated GIF to WebM VP9 video sticker."""
        ...

    def mp4_to_webm(self, mp4_path: str, output_path: str) -> Path:
        """Convert MP4 video to WebM VP9 video sticker."""
        ...

    def _verify_webm(self, path: str) -> dict:
        """Verify WebM meets Telegram requirements. Returns info dict or raises."""
        ...
```

#### 2.1.2 `scripts/animation_presets.py` (~150 lines)

**Path:** `scripts/animation_presets.py`

Lottie keyframe definitions for each animation type:

```python
"""
Animation preset keyframes for Lottie/video sticker generation.
Each preset returns a list of (time_pct, transform) tuples.
Transforms: {"x": float, "y": float, "scale": float, "rotation": float, "opacity": float}
"""

def bounce(duration_frames: int, amplitude: float = 30.0) -> list[dict]:
    """Vertical bounce with squash/stretch easing."""
    ...

def shake(duration_frames: int, intensity: float = 15.0) -> list[dict]:
    """Horizontal wiggle with decreasing amplitude."""
    ...

def pulse(duration_frames: int, scale_range: tuple = (0.9, 1.1)) -> list[dict]:
    """Heartbeat-style scale pulse."""
    ...

def pop_in(duration_frames: int) -> list[dict]:
    """Scale from 0 → overshoot 1.15 → settle 1.0."""
    ...
```

### 2.2 Existing Files to Modify

#### 2.2.1 `scripts/sticker_processor.py`

Add a new method `process_animated()` to `StickerProcessor`:

```python
def process_animated(
    self,
    input_path: str,
    output_dir: str,
    animation_type: str = "bounce",
    formats: list[str] = None,  # ["tgs", "webm"] or both
) -> dict[str, Path]:
    """
    Full pipeline for creating animated/video stickers from a static image.

    Steps:
        1. Load processed static sticker (already has outline, transparent bg)
        2. Resize to 512x512 (Telegram requirement)
        3. Convert to TGS (Lottie animated) if requested
        4. Convert to WebM VP9 (video) if requested
    """
    ...
```

Also update `process_batch()` to handle animated formats when `telegram_animated` or `telegram_video` is in the platforms list.

#### 2.2.2 `scripts/telegram_publisher.py`

Extend the `create_sticker_set()` and `_create_set_sequential()` methods:

```python
def create_sticker_set(
    self,
    user_id: int,
    name: str,
    title: str,
    sticker_paths: list[str],
    emojis_list: list[str],
    sticker_format: str = "static",   # Already exists! "static" | "animated" | "video"
) -> str:
    ...
```

The existing code already passes `sticker_format` through — the main change is ensuring it works correctly with `.tgs` and `.webm` files. The Telegram Bot API `sticker` field accepts:
- Static: PNG/WebP file
- Animated: TGS file
- Video: WebM file

**Changes needed:**
1. Detect format from file extension if `sticker_format` not specified
2. Set correct MIME types in file upload (`application/x-tgs` for TGS)
3. Add validation: file size checks per format before upload

Add a new convenience method:

```python
def create_animated_sticker_set(
    self,
    user_id: int,
    name: str,
    title: str,
    sticker_dir: str,
    emojis_list: list[str],
    format: str = "animated",  # "animated" (TGS) or "video" (WebM)
) -> str:
    """Create an animated or video sticker set from a directory of TGS/WebM files."""
    ext = ".tgs" if format == "animated" else ".webm"
    sticker_files = sorted(Path(sticker_dir).glob(f"*{ext}"))
    ...
```

#### 2.2.3 `scripts/run_pipeline.py`

Add animated processing to the pipeline:

```python
def stage_process_animated(config: dict):
    """Stage 2b: Create animated/video versions of stickers."""
    from animated_converter import LottieAnimator, VideoConverter
    ...

# In main():
parser.add_argument(
    "--telegram-animated",
    action="store_true",
    help="Also create and publish animated Telegram stickers (TGS)",
)
parser.add_argument(
    "--telegram-video",
    action="store_true",
    help="Also create and publish video Telegram stickers (WebM)",
)
```

### 2.3 Dependencies & Tools

| Tool | Install | Purpose |
|------|---------|---------|
| ffmpeg | `brew install ffmpeg` | WebM VP9 encoding |
| lottie-py | `pip install lottie-py` | Lottie JSON generation |
| cairosvg | `pip install cairosvg` | SVG support for Lottie |
| Pillow (existing) | Already installed | Frame generation |

### 2.4 Implementation Steps (Ordered)

1. **Install ffmpeg** — Verify VP9 encoder available
2. **Install Python deps** — `pip install lottie-py cairosvg`
3. **Create `scripts/animation_presets.py`** — Define keyframe presets
4. **Create `scripts/animated_converter.py`** — `LottieAnimator` + `VideoConverter` classes:
   - Implement `LottieAnimator.png_to_tgs()` first (hardest part)
   - Implement `VideoConverter.png_to_webm()` using ffmpeg
   - Implement `VideoConverter.gif_to_webm()` and `mp4_to_webm()`
   - Add size verification for both formats
5. **Update `sticker_processor.py`** — Add specs, add `process_animated()` method
6. **Update `telegram_publisher.py`** — Add format detection, MIME type handling, `create_animated_sticker_set()`
7. **Update `run_pipeline.py`** — Wire in `--telegram-animated` and `--telegram-video` flags
8. **Test TGS generation** — Verify file ≤64KB, plays correctly in Telegram
9. **Test WebM generation** — Verify ≤256KB, VP9, no audio, ≤3 seconds
10. **Test end-to-end** — Create animated sticker set via bot API

### 2.5 Verification & Testing

| Test | How |
|------|-----|
| TGS file valid | `python -c "import gzip, json; json.loads(gzip.open('test.tgs').read())"` — parses as valid Lottie JSON |
| TGS size | `ls -la test.tgs` — must be ≤64KB (65,536 bytes) |
| WebM valid | `ffprobe -v error -show_format -show_streams test.webm` — codec=vp9, duration≤3, no audio stream |
| WebM size | `ls -la test.webm` — must be ≤256KB (262,144 bytes) |
| Bot API accepts TGS | `create_sticker_set(..., sticker_format="animated")` succeeds |
| Bot API accepts WebM | `create_sticker_set(..., sticker_format="video")` succeeds |
| Sticker plays in Telegram | Open `https://t.me/addstickers/<name>` → sticker animates |
| Pipeline integration | `python run_pipeline.py --process-only --telegram-animated` |

### 2.6 Technical Notes

**TGS (Lottie) strategy for AI-generated stickers:**

The challenge is that AI-generated sticker art is rasterized (PNG), not vector. True Lottie animations use vector paths. Two approaches:

1. **Embedded image + transform animation (recommended):** Embed the PNG as a base64 image asset inside the Lottie JSON, then animate transform properties (position, scale, rotation). This preserves the original artwork quality. The 64KB compressed limit is tight — the image must be aggressively optimized (reduced palette, lower resolution internally, heavy JPEG compression within the Lottie asset).

2. **Auto-vectorization (experimental):** Trace the PNG outlines to SVG paths using `potrace` or `vtracer`, then animate the vector paths. This produces smaller files but loses detail in complex artwork.

**Recommendation:** Start with approach 1. If 64KB is too tight for embedded images, offer approach 2 as a fallback with a quality warning.

**WebM VP9 strategy:**

This is more straightforward — generate animation frames as temporary PNGs, then encode with ffmpeg. The 256KB limit is generous for a 512x512, 2-second, 30fps video.

```bash
# Core ffmpeg command for video stickers
ffmpeg -framerate 30 \
  -i /tmp/frames/%04d.png \
  -c:v libvpx-vp9 \
  -pix_fmt yuva420p \
  -b:v 0 -crf 40 \
  -an \
  -t 3 \
  -vf "scale=512:512" \
  -row-mt 1 \
  output.webm
```

Key flags:
- `-pix_fmt yuva420p` — VP9 with alpha channel (transparency)
- `-b:v 0 -crf 40` — Constant quality mode (adjust CRF 30–50 to fit 256KB)
- `-an` — No audio (Telegram requirement)

---

## Phase 3: WhatsApp Native App

**Goal:** Build a custom Android app that integrates with WhatsApp's native sticker API (ContentProvider protocol), plus a server component for dynamic pack loading.

**Estimated Complexity:** Complex

**Current state:** WhatsApp stickers are currently uploaded manually via Sticker.ly. The pipeline already generates WhatsApp-compatible WebP files (512x512, ≤100KB) and `whatsapp_contents.json` metadata.

### 3.0 Prerequisites

#### 3.0.1 Android Development Setup

```bash
# Install Android Studio (includes SDK, emulator, adb)
# https://developer.android.com/studio

# Or SDK-only via Homebrew (for CI/headless builds)
brew install --cask android-commandlinetools
sdkmanager "platforms;android-34" "build-tools;34.0.0"

# Verify
adb version
```

#### 3.0.2 WhatsApp Sticker Integration Specs

WhatsApp uses a **ContentProvider** pattern. The sticker app:
1. Exposes sticker pack data via `ContentProvider`
2. WhatsApp queries the provider for pack metadata + sticker images
3. User taps "Add to WhatsApp" → Android Intent fires
4. WhatsApp presents confirmation dialog (mandatory, cannot be skipped)
5. User confirms → stickers available in WhatsApp keyboard

**Required ContentProvider URIs:**

| URI | Purpose |
|-----|---------|
| `content://<authority>/metadata` | List all sticker packs |
| `content://<authority>/stickers/<pack_id>` | List stickers in a pack |
| `content://<authority>/stickers_asset/<pack_id>/<sticker_name>` | Get sticker image bytes |

### 3.1 New Files to Create

#### 3.1.1 Android App: `whatsapp-sticker-app/` directory

**Path:** `whatsapp-sticker-app/` (new directory at repo root)

Project structure:

```
whatsapp-sticker-app/
├── app/
│   ├── build.gradle.kts
│   ├── src/
│   │   └── main/
│   │       ├── AndroidManifest.xml
│   │       ├── java/com/yourbrand/stickers/
│   │       │   ├── StickerContentProvider.java
│   │       │   ├── StickerPack.java
│   │       │   ├── Sticker.java
│   │       │   ├── StickerPackLoader.java
│   │       │   ├── StickerPackListActivity.java
│   │       │   ├── StickerPackDetailsActivity.java
│   │       │   ├── AddStickerPackActivity.java
│   │       │   └── StickerPackValidator.java
│   │       ├── res/
│   │       │   ├── layout/
│   │       │   │   ├── activity_sticker_pack_list.xml
│   │       │   │   ├── activity_sticker_pack_details.xml
│   │       │   │   └── item_sticker_pack.xml
│   │       │   ├── values/
│   │       │   │   ├── strings.xml
│   │       │   │   └── styles.xml
│   │       │   └── drawable/
│   │       └── assets/
│   │           └── contents.json         ← Generated by Python script
│   └── proguard-rules.pro
├── build.gradle.kts
├── settings.gradle.kts
├── gradle.properties
└── gradle/
    └── wrapper/
        ├── gradle-wrapper.jar
        └── gradle-wrapper.properties
```

#### 3.1.2 `whatsapp-sticker-app/app/src/main/AndroidManifest.xml`

```xml
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.yourbrand.stickers">

    <uses-permission android:name="android.permission.INTERNET" />

    <application
        android:allowBackup="true"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:theme="@style/AppTheme"
        android:networkSecurityConfig="@xml/network_security_config">

        <activity
            android:name=".StickerPackListActivity"
            android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>

        <activity android:name=".StickerPackDetailsActivity" />
        <activity android:name=".AddStickerPackActivity" />

        <provider
            android:name=".StickerContentProvider"
            android:authorities="${applicationId}.stickercontentprovider"
            android:exported="true"
            android:readPermission="com.whatsapp.sticker.READ" />
    </application>
</manifest>
```

#### 3.1.3 `StickerContentProvider.java` (core)

This is the heart of WhatsApp integration. Key implementation:

```java
public class StickerContentProvider extends ContentProvider {

    static final String AUTHORITY = BuildConfig.APPLICATION_ID + ".stickercontentprovider";

    // URI matcher patterns
    static final int METADATA = 1;
    static final int METADATA_SINGLE = 2;
    static final int STICKERS = 3;
    static final int STICKERS_ASSET = 4;

    private static final UriMatcher URI_MATCHER = new UriMatcher(UriMatcher.NO_MATCH);
    static {
        URI_MATCHER.addURI(AUTHORITY, "metadata", METADATA);
        URI_MATCHER.addURI(AUTHORITY, "metadata/*", METADATA_SINGLE);
        URI_MATCHER.addURI(AUTHORITY, "stickers/*", STICKERS);
        URI_MATCHER.addURI(AUTHORITY, "stickers_asset/*/*", STICKERS_ASSET);
    }

    @Override
    public Cursor query(Uri uri, ...) {
        switch (URI_MATCHER.match(uri)) {
            case METADATA:
                return getPackListCursor();      // All packs
            case METADATA_SINGLE:
                return getSinglePackCursor(uri);  // One pack's metadata
            case STICKERS:
                return getStickersCursor(uri);    // Stickers in a pack
            case STICKERS_ASSET:
                // This shouldn't be reached via query — use openFile
                return null;
        }
    }

    @Override
    public ParcelFileDescriptor openFile(Uri uri, String mode) {
        // Return sticker image bytes for stickers_asset URIs
        // Load from assets/ folder or download from server
    }
}
```

**Required Cursor columns for metadata:**

| Column | Type | Description |
|--------|------|-------------|
| `sticker_pack_identifier` | String | Unique pack ID |
| `sticker_pack_name` | String | Display name |
| `sticker_pack_publisher` | String | Publisher name |
| `sticker_pack_icon` | String | Tray icon filename |
| `android_play_store_link` | String | Play Store URL (can be empty) |
| `ios_app_store_link` | String | App Store URL (can be empty) |
| `publisher_website` | String | Website URL |
| `privacy_policy_website` | String | Privacy policy URL |
| `license_agreement_website` | String | License URL |
| `image_data_version` | String | Version string (for cache invalidation) |
| `avoid_cache` | int | 0 or 1 |

**Required Cursor columns for stickers:**

| Column | Type | Description |
|--------|------|-------------|
| `sticker_file_name` | String | Filename of the sticker WebP |
| `sticker_emoji` | String | Comma-separated emoji associations |

#### 3.1.4 Intent to add sticker pack to WhatsApp

```java
public static void addStickerPackToWhatsApp(Activity activity, String packId, String packName) {
    Intent intent = new Intent();
    intent.setAction("com.whatsapp.intent.action.ENABLE_STICKER_PACK");
    intent.putExtra("sticker_pack_id", packId);
    intent.putExtra("sticker_pack_authority",
        activity.getPackageName() + ".stickercontentprovider");
    intent.putExtra("sticker_pack_name", packName);
    try {
        activity.startActivityForResult(intent, ADD_PACK_REQUEST_CODE);
    } catch (ActivityNotFoundException e) {
        // WhatsApp not installed
        Toast.makeText(activity, "WhatsApp is not installed", Toast.LENGTH_SHORT).show();
    }
}
```

#### 3.1.5 Server Component: `server/whatsapp_api.py` (~200 lines)

**Path:** `server/whatsapp_api.py`

A FastAPI server that serves sticker pack metadata + images so the Android app can dynamically load new packs without app updates.

```python
"""
WhatsApp Sticker Pack API Server.

Serves sticker pack metadata and images for the Android sticker app.
The app fetches packs from this server on startup, enabling dynamic
pack updates without publishing new app versions.

Endpoints:
    GET  /api/v1/packs                    → List all available packs
    GET  /api/v1/packs/{pack_id}          → Single pack metadata
    GET  /api/v1/packs/{pack_id}/stickers → List stickers in a pack
    GET  /api/v1/stickers/{pack_id}/{filename} → Download sticker image
    POST /api/v1/packs/{pack_id}/publish  → Upload/update a pack (auth required)
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import FileResponse
from fastapi.security import HTTPBearer
import json
from pathlib import Path

app = FastAPI(title="WhatsApp Sticker API")

PACKS_DIR = Path("./sticker_packs")  # Configured via env

@app.get("/api/v1/packs")
async def list_packs():
    """Return metadata for all available sticker packs."""
    ...

@app.get("/api/v1/packs/{pack_id}")
async def get_pack(pack_id: str):
    """Return metadata for a single pack."""
    ...

@app.get("/api/v1/stickers/{pack_id}/{filename}")
async def get_sticker_image(pack_id: str, filename: str):
    """Serve a sticker image file."""
    path = PACKS_DIR / pack_id / filename
    if not path.exists():
        raise HTTPException(404)
    return FileResponse(path, media_type="image/webp")

@app.post("/api/v1/packs/{pack_id}/publish")
async def publish_pack(pack_id: str, ...):
    """Upload a new sticker pack (called by the Python export script)."""
    ...
```

#### 3.1.6 `scripts/whatsapp_exporter.py` (~250 lines)

**Path:** `scripts/whatsapp_exporter.py`

Prepares sticker packs in WhatsApp-native format and pushes to the server:

```python
"""
WhatsApp Native Sticker Exporter.

Prepares sticker packs in the exact format required by WhatsApp's
ContentProvider protocol and optionally pushes them to the API server
for dynamic loading by the Android app.

Usage:
    # Export pack to local directory (for bundling in APK assets/)
    python whatsapp_exporter.py export <pack_dir> --output whatsapp-sticker-app/app/src/main/assets/

    # Export and push to remote server
    python whatsapp_exporter.py push <pack_dir> --server https://stickers.yourdomain.com

    # Validate a pack against WhatsApp requirements
    python whatsapp_exporter.py validate <pack_dir>
"""

class WhatsAppExporter:
    """Export sticker packs in WhatsApp ContentProvider format."""

    # WhatsApp requirements (strict)
    MAX_STICKERS_PER_PACK = 30
    MIN_STICKERS_PER_PACK = 3
    STICKER_SIZE = (512, 512)
    STICKER_MAX_KB = 100
    TRAY_SIZE = (96, 96)
    TRAY_MAX_KB = 50
    STICKER_FORMAT = "WEBP"

    def export_pack(
        self,
        pack_config: dict,
        sticker_dir: str,
        output_dir: str,
    ) -> Path:
        """
        Export a complete WhatsApp sticker pack.

        Creates:
            <output_dir>/<pack_id>/
            ├── contents.json           ← WhatsApp metadata
            ├── tray_icon.png           ← 96x96 tray icon
            ├── 01_happy.webp           ← Sticker files
            ├── 02_love.webp
            └── ...

        The contents.json follows the WhatsApp Sticker Pack schema.
        """
        ...

    def validate_pack(self, pack_dir: str) -> list[str]:
        """Validate pack meets all WhatsApp requirements. Returns list of errors."""
        errors = []
        # Check: 3-30 stickers
        # Check: all WebP, 512x512, ≤100KB
        # Check: tray icon exists, 96x96, ≤50KB
        # Check: contents.json valid
        return errors

    def push_to_server(self, pack_dir: str, server_url: str, api_key: str):
        """Upload pack to the WhatsApp sticker API server."""
        ...
```

#### 3.1.7 `server/Dockerfile`

**Path:** `server/Dockerfile`

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "whatsapp_api:app", "--host", "0.0.0.0", "--port", "8080"]
```

#### 3.1.8 `server/requirements.txt`

```
fastapi>=0.104.0
uvicorn>=0.24.0
python-multipart>=0.0.6
```

### 3.2 Existing Files to Modify

| File | Change |
|------|--------|
| `scripts/run_pipeline.py` | Add `--whatsapp-native` flag that calls `whatsapp_exporter.py` |
| `scripts/sticker_processor.py` | Already has `whatsapp` and `whatsapp_tray` specs — add `whatsapp_native` and `whatsapp_native_tray` |
| `.gitignore` | Add `whatsapp-sticker-app/build/`, `whatsapp-sticker-app/.gradle/`, `server/__pycache__/` |
| `docs/platform-specs.md` | Update WhatsApp section with native app integration details |
| `.env.example` | Add server-related env vars (already covered in Phase 0) |

### 3.3 Dependencies & Tools

| Tool | Install | Purpose |
|------|---------|---------|
| Android Studio / SDK | https://developer.android.com/studio | Build the Android app |
| Gradle 8.x | Bundled with Android project wrapper | Build system |
| Java 17+ | `brew install openjdk@17` | Android compilation |
| FastAPI | `pip install fastapi uvicorn` | Server API |
| Docker (optional) | `brew install docker` | Server deployment |

### 3.4 Implementation Steps (Ordered)

1. **Set up Android development environment** — Install Android Studio or SDK CLI tools
2. **Create `whatsapp-sticker-app/` project** — Initialize Gradle project with basic Activity
3. **Implement data models** — `StickerPack.java`, `Sticker.java`
4. **Implement `StickerContentProvider.java`** — Core WhatsApp integration:
   - `query()` for metadata, stickers list
   - `openFile()` for sticker image bytes
   - Load from local assets initially
5. **Implement `StickerPackLoader.java`** — Load packs from assets/ or server
6. **Implement UI Activities** — Pack list, pack details, "Add to WhatsApp" button
7. **Implement `AddStickerPackActivity.java`** — Intent to WhatsApp
8. **Implement `StickerPackValidator.java`** — Runtime validation before adding
9. **Create `scripts/whatsapp_exporter.py`** — Python pack export + validation
10. **Create `server/whatsapp_api.py`** — FastAPI sticker serving API
11. **Wire into `run_pipeline.py`** — Add `--whatsapp-native` flag
12. **Test on Android emulator** — Install app, verify WhatsApp integration
13. **Test on physical device** — Confirm stickers appear in WhatsApp keyboard
14. **Add server dynamic loading** — App fetches new packs from server at startup

### 3.5 Verification & Testing

| Test | How |
|------|-----|
| App builds | `./gradlew assembleDebug` in `whatsapp-sticker-app/` |
| App installs | `adb install app/build/outputs/apk/debug/app-debug.apk` |
| ContentProvider responds | `adb shell content query --uri content://com.yourbrand.stickers.stickercontentprovider/metadata` |
| Sticker images serve | Query `stickers_asset` URI — verify image bytes returned |
| Add to WhatsApp | Tap "Add to WhatsApp" → WhatsApp confirmation dialog appears |
| Stickers in keyboard | After confirming, stickers visible in WhatsApp sticker drawer |
| Pack validation | `python whatsapp_exporter.py validate packs/pack01/final/whatsapp/` |
| Server serves packs | `curl http://localhost:8080/api/v1/packs` returns JSON |
| Dynamic loading | Add new pack to server → restart app → new pack appears |
| Export pipeline | `python run_pipeline.py --process-only --whatsapp-native` |

### 3.6 WhatsApp Integration Constraints

These are hard constraints from WhatsApp's design — **cannot be bypassed**:

1. **User confirmation is always required.** WhatsApp shows a system confirmation dialog when adding sticker packs. This is a security feature. Your app can open this dialog, but the user must explicitly tap "Add."

2. **ContentProvider must be exported.** WhatsApp queries your app's ContentProvider — it must have `android:exported="true"` and the correct read permission.

3. **Stickers must be self-contained.** Each sticker image must be fully renderable — no references to external resources in the sticker data itself.

4. **Pack limits are strict.** Exactly 3–30 stickers per pack, exactly 512x512 WebP, exactly 96x96 tray icon. WhatsApp validates these at add-time and will reject non-conforming packs silently.

---

## Dependency Graph

```
Phase 0 (Shared Infrastructure)
    │
    ├──► Phase 1 (iMessage Fastlane)      ← Independent
    │       Depends on: Apple Developer Account, Xcode, Fastlane
    │
    ├──► Phase 2 (Telegram Animated)       ← Independent
    │       Depends on: ffmpeg, lottie-py
    │
    └──► Phase 3 (WhatsApp Native)         ← Independent
            Depends on: Android SDK, FastAPI
```

All three phases are independent of each other after Phase 0. They can be executed in parallel or in any order. The recommended order (1 → 2 → 3) is based on:

- **Phase 1** has the longest lead time (Apple Developer Account approval: 24–48 hours)
- **Phase 2** has the most immediate impact (Telegram is your most automated platform)
- **Phase 3** is the largest engineering effort (Android app + server)

---

## Timeline Summary

| Phase | Effort | Calendar Time | Key Blocker |
|-------|--------|---------------|-------------|
| Phase 0 | 2–3 hours | Day 1 | None |
| Phase 1 | 3–5 days | Week 1–2 | Apple Developer Account approval (24–48h) |
| Phase 2 | 2–3 days | Week 2–3 | TGS 64KB size constraint (may need iteration) |
| Phase 3 | 5–8 days | Week 3–5 | Android app development + WhatsApp testing |

**Total estimated effort:** 12–19 developer-days

---

## File Summary: What Gets Created / Modified

### New Files (17)

| File | Phase | Purpose |
|------|-------|---------|
| `fastlane/Gemfile` | 1 | Ruby dependency management |
| `fastlane/Pluginfile` | 1 | Fastlane plugins |
| `fastlane/Appfile` | 1 | Apple ID / Team config |
| `fastlane/Matchfile` | 1 | Code signing config |
| `fastlane/Fastfile` | 1 | Build/upload/submit lanes |
| `fastlane/metadata/en-US/*.txt` (7 files) | 1 | App Store metadata templates |
| `templates/imessage_metadata.json` | 1 | Metadata template for iMessage packs |
| `templates/imessage_project.yml` | 1 | xcodegen project spec template |
| `scripts/imessage_publisher.py` | 1 | Full iMessage automation orchestrator |
| `scripts/animated_converter.py` | 2 | TGS (Lottie) + WebM VP9 converters |
| `scripts/animation_presets.py` | 2 | Keyframe animation definitions |
| `scripts/whatsapp_exporter.py` | 3 | WhatsApp native format export |
| `server/whatsapp_api.py` | 3 | Sticker pack API server |
| `server/Dockerfile` | 3 | Server container |
| `server/requirements.txt` | 3 | Server dependencies |
| `whatsapp-sticker-app/` (entire project) | 3 | Android WhatsApp sticker app |

### Modified Files (7)

| File | Phase(s) | Changes |
|------|----------|---------|
| `.env.example` | 0 | Add Apple, WhatsApp server env vars |
| `scripts/pack_config.py` | 0 | Add animation hints, new platform flags |
| `scripts/sticker_processor.py` | 0, 2 | Add new specs; add `process_animated()` |
| `scripts/telegram_publisher.py` | 2 | Format detection, MIME types, animated set method |
| `scripts/run_pipeline.py` | 1, 2, 3 | New CLI flags for each phase |
| `scripts/prepare_imessage_pack.py` | 1 | App icon generation, xcodegen integration |
| `requirements.txt` | 0 | Add lottie-py, cairosvg, fastapi, uvicorn |
| `.gitignore` | 1, 3 | Add build artifacts |
| `docs/platform-specs.md` | 3 | WhatsApp native integration docs |
