# Configuration Guide

How to define characters, styles, and sticker packs in StickerFramework.

---

## Overview

All pack configuration lives in `pack_config.py`. This single file defines:
1. **Character** - Visual identity (species, colors, proportions)
2. **Style** - Art direction rules (outlines, color mode, background)
3. **Stickers** - Individual sticker definitions (emotions, poses, props)
4. **Pack metadata** - Pack ID, name, publisher, target platforms

The pipeline reads this config and uses it to generate prompts, process images, and create metadata for each platform.

---

## Character Definition

The `CHARACTER` dictionary defines the visual identity of your sticker character.

```python
CHARACTER = {
    "name": "Mochi",
    "species": "Round cat",
    "body_color": "#FFB6C1",      # Soft pink
    "blush_color": "#FF69B4",      # Hot pink
    "outline_color": "#333333",    # Dark gray
    "eye_style": "Simple black oval, no pupils, highly expressive",
    "accessory": "Tiny gold star pin on left ear",
    "proportions": "Chibi, head is 60% of body height, stubby limbs",
}
```

### Character Fields

| Field | Required | Description | Example |
|-------|----------|-------------|---------|
| `name` | Yes | Character name, used in prompts and metadata | `"Mochi"` |
| `species` | Yes | Species/form description | `"Round cat"`, `"Chubby penguin"` |
| `body_color` | Yes | Primary body color (hex) | `"#FFB6C1"` |
| `blush_color` | Yes | Accent/blush color (hex) | `"#FF69B4"` |
| `outline_color` | Yes | Outline color (hex) | `"#333333"` |
| `eye_style` | Yes | Detailed eye description | `"Large sparkly anime eyes"` |
| `accessory` | No | Distinctive accessory | `"Red bow on head"` |
| `proportions` | Yes | Body proportions guide | `"Chibi, head is 60% of body"` |

### Tips for Character Design
- **Consistency**: Use specific hex colors so DALL-E reproduces them reliably
- **Simplicity**: Simpler characters generate more consistently across stickers
- **Distinctiveness**: Include one unique accessory for brand recognition
- **Proportions**: Chibi (oversized head) works best for small sticker formats

---

## Style Definition

The `STYLE` dictionary controls the art direction applied to every sticker.

```python
STYLE = {
    "outline": "Thick uniform outline, 3-4px weight",
    "colors": "Flat colors only, no gradients, no realistic shading",
    "background": "Clean solid white background",
    "format": "Die-cut sticker style with thick white border",
}
```

### Style Fields

| Field | Required | Description |
|-------|----------|-------------|
| `outline` | Yes | Outline weight and consistency rules |
| `colors` | Yes | Color rendering rules (flat, gradient, realistic) |
| `background` | Yes | Background specification |
| `format` | Yes | Overall format/style description |

### Recommended Style Settings

For **kawaii/cute** stickers (best for messaging apps):
```python
STYLE = {
    "outline": "Thick uniform outline, 3-4px weight",
    "colors": "Flat colors only, no gradients",
    "background": "Clean solid white background",
    "format": "Die-cut sticker style with thick white border",
}
```

For **watercolor/soft** stickers:
```python
STYLE = {
    "outline": "Thin delicate outline, 1-2px weight",
    "colors": "Soft watercolor palette with gentle gradients",
    "background": "Clean solid white background",
    "format": "Rounded sticker with soft shadow",
}
```

For **bold/graphic** stickers:
```python
STYLE = {
    "outline": "Heavy black outline, 5-6px weight",
    "colors": "Saturated flat colors, high contrast",
    "background": "Clean solid white background",
    "format": "Bold die-cut sticker with thick black border",
}
```

---

## Sticker Definitions

Each sticker is a dictionary with emotion, pose, and prop details.

```python
{
    "id": "01_happy",
    "emotion": "Happy",
    "pose": "Jumping with both paws up, eyes squeezed shut smiling",
    "props": "Three sparkles floating around, small rainbow above",
    "emoji": "😊",
}
```

### Sticker Fields

| Field | Required | Description | Used In |
|-------|----------|-------------|---------|
| `id` | Yes | Unique identifier (used as filename) | File naming, metadata |
| `emotion` | Yes | Primary emotion label | Prompt, metadata |
| `pose` | Yes | Detailed pose description | DALL-E prompt |
| `props` | Yes | Visual props and effects | DALL-E prompt |
| `emoji` | Yes | Associated emoji | Telegram, metadata |

### Writing Effective Sticker Descriptions

**Pose guidelines:**
- Be specific about body position: "Jumping", "Sitting", "Lying down"
- Describe facial expression: "Eyes squeezed shut", "One eye winking"
- Include limb positions: "Both paws up", "Arms crossed"

**Props guidelines:**
- Keep props simple and recognizable at small sizes
- Use universal symbols: hearts, stars, sparkles, music notes
- Avoid text (stickers should work internationally)
- Limit to 2-3 props per sticker

**Emotion coverage for a balanced pack (24 stickers):**

| Category | Emotions | Count |
|----------|----------|-------|
| Positive | Happy, Love, Excited, Laughing, Celebrating, Grateful | 6 |
| Negative | Sad, Angry, Crying, Sick, Tired | 5 |
| Neutral | Thinking, Confused, Surprised, Sleepy | 4 |
| Expressive | Winking, Blushing, Cool, Mischievous, Hungry | 5 |
| Greetings | Hello, Bye, Yes/OK, No | 4 |

---

## Pack Configuration

The `PACK_CONFIG` ties everything together.

```python
PACK_CONFIG = {
    "pack_id": "pack01_emotions_v1",
    "pack_name": "Mochi Emotions Vol. 1",
    "publisher": "Your Brand Name",
    "character": CHARACTER,
    "style": STYLE,
    "stickers": [
        # ... 24 sticker definitions
    ],
    "platforms": ["whatsapp", "telegram", "imessage_large", "line", "print_etsy"],
}
```

### Pack Config Fields

| Field | Required | Description |
|-------|----------|-------------|
| `pack_id` | Yes | Unique ID, used for output directory and filenames |
| `pack_name` | Yes | Human-readable pack name |
| `publisher` | Yes | Publisher/brand name for metadata |
| `character` | Yes | Character definition dict |
| `style` | Yes | Style definition dict |
| `stickers` | Yes | List of sticker definition dicts |
| `platforms` | Yes | List of target platform identifiers |

### Available Platforms

| Platform ID | Description | Output Format |
|-------------|-------------|---------------|
| `whatsapp` | WhatsApp / Sticker.ly | 512x512 WEBP, <100KB |
| `telegram` | Telegram Stickers | 512x512 WEBP, <256KB |
| `imessage_small` | iMessage (small grid) | 300x300 PNG |
| `imessage_medium` | iMessage (medium grid) | 408x408 PNG |
| `imessage_large` | iMessage (large grid) | 618x618 PNG |
| `line` | LINE Creators Market | 370x320 PNG |
| `print_etsy` | High-res for print/Etsy | 2048x2048 PNG |

---

## Creating a New Pack

### Step 1: Copy and Modify the Config

```python
# In pack_config.py, define a new character or reuse existing one

NEW_CHARACTER = {
    "name": "Boba",
    "species": "Round bubble tea cup with face",
    "body_color": "#DEB887",
    "blush_color": "#FF69B4",
    "outline_color": "#333333",
    "eye_style": "Large sparkly anime eyes with star highlights",
    "accessory": "Striped straw sticking out of head",
    "proportions": "Chibi, cylindrical body, small arms and legs",
}
```

### Step 2: Define Your Stickers

```python
NEW_STICKERS = [
    {
        "id": "01_sipping",
        "emotion": "Content",
        "pose": "Sitting cross-legged, sipping through own straw",
        "props": "Steam wisps, content smile, closed eyes",
        "emoji": "😌",
    },
    # ... add 23 more stickers
]
```

### Step 3: Create the Pack Config

```python
NEW_PACK_CONFIG = {
    "pack_id": "pack02_boba_v1",
    "pack_name": "Boba Emotions Vol. 1",
    "publisher": "Your Brand Name",
    "character": NEW_CHARACTER,
    "style": STYLE,  # Reuse the existing style
    "stickers": NEW_STICKERS,
    "platforms": ["whatsapp", "telegram", "imessage_large", "line", "print_etsy"],
}
```

### Step 4: Update `PACK_CONFIG` Reference

Either replace `PACK_CONFIG` in `pack_config.py` or modify `run_pipeline.py` to accept a pack config argument.

---

## Naming Conventions

### Pack IDs
Format: `pack<number>_<theme>_v<version>`
Examples: `pack01_emotions_v1`, `pack02_food_v1`, `pack03_holidays_v2`

### Sticker IDs
Format: `<number>_<emotion>`
Examples: `01_happy`, `02_love`, `15_hungry`

### Pack Names
Format: `<Character Name> <Theme> Vol. <Number>`
Examples: `"Mochi Emotions Vol. 1"`, `"Mochi Holiday Special Vol. 1"`

---

## Brand Kit Integration

The `brand_kit.md` file serves as the visual identity reference. Key elements to maintain across packs:

- **Color palette**: Consistent body color, blush color, outline color
- **Typography**: Rounded sans-serif (Nunito Bold) for external branding
- **No text in stickers**: Ensures international market compatibility
- **Consistent accessory**: The gold star pin on Mochi's left ear appears in every sticker
- **Expression guide**: Standardized ways to show emotions (blue teardrops, steam for anger, etc.)
