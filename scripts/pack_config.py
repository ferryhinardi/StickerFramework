"""
Sticker Pack Configuration
Define your character, art style, and all stickers in a pack.
This config drives the entire generation + processing pipeline.

Supports:
- Single character packs (standard)
- Dual/couple character packs (set "characters" list + "relationship")
- Localization (set "localization" dict for multi-language titles)
- Emotion coverage validation (essential emotions are checked at pipeline start)
"""

# =============================================================================
# CHARACTER DEFINITION
# Change these to customize your character
# =============================================================================
CHARACTER = {
    "name": "Mochi",
    "species": "round cat",
    "body_color": "#FFB6C1",
    "blush_color": "#FF69B4",
    "outline_color": "#333333",
    "eye_style": "simple black oval eyes, no pupils, highly expressive",
    "accessory": "tiny gold star pin on left ear",
    "proportions": "chibi, head is 60% of total body height, stubby short limbs",
    # --- v2 fields (character-agnostic prompt building) ---
    "body_description": (
        "cute round chubby mochi cat, pink body, simple black oval eyes, "
        "tiny gold star pin on left ear, potato-shaped body, "
        "stubby short limbs, soft pink cheeks"
    ),
    "features": [
        "round chubby body",
        "pink fur",
        "black oval eyes",
        "gold star pin on left ear",
        "stubby limbs",
    ],
}

# =============================================================================
# ART STYLE
# =============================================================================
STYLE = {
    "outline_type": "thick uniform outline, consistent 3-4px width",
    "coloring": "flat colors only, absolutely no gradients, no realistic shading",
    "background": "clean solid white background with no other elements",
    "extras": (
        "die-cut sticker style with a thick white outline border "
        "around the ENTIRE character"
    ),
    # --- v2 field: controls prompt template and negative prompt selection ---
    # Options: "flat_vector" (default, original style) | "painted_illustration"
    "art_style": "flat_vector",
}

# =============================================================================
# PACK: EMOTIONS VOL. 1 (24 stickers)
# =============================================================================
PACK_CONFIG = {
    "pack_id": "pack01_emotions_v1",
    "pack_name": "Mochi Emotions Vol. 1",
    "publisher": "Your Brand Name",  # Change this
    "character": CHARACTER,
    "style": STYLE,
    # --- v2 field: pack-level text overlay defaults for TextCompositor ---
    # Per-sticker "text" fields can override these.  Omit entirely for
    # text-free packs (like cappy-capybara Vol. 1/2).
    "text_defaults": None,  # No text for this pack
    "stickers": [
        {
            "id": "01_happy",
            "emotion": "Happy",
            "pose": "Jumping with arms raised, feet off the ground",
            "props": "Small sparkle effects (4-pointed stars) around head",
            "emoji": "\U0001f60a",
            # Phase 2: Optional animation hints for animated/video stickers.
            # Supported types: bounce, shake, pulse, spin, wave, custom.
            # Omit this key entirely to use the default "bounce" preset.
            "animation": {
                "type": "bounce",
                "duration_ms": 2000,
                "loop": True,
            },
        },
        {
            "id": "02_love",
            "emotion": "In Love",
            "pose": "Hugging a large pink heart with both arms, eyes closed blissfully",
            "props": "Small floating hearts above head",
            "emoji": "\u2764\ufe0f",
        },
        {
            "id": "03_sad",
            "emotion": "Sad",
            "pose": "Sitting hunched over, head down, ears drooping",
            "props": "Single large blue teardrop on cheek, small rain cloud above",
            "emoji": "\U0001f622",
        },
        {
            "id": "04_angry",
            "emotion": "Angry",
            "pose": "Standing with fists clenched, leaning forward aggressively",
            "props": "Puffed red cheeks, steam lines rising from head, anger vein mark on forehead",
            "emoji": "\U0001f620",
        },
        {
            "id": "05_sleepy",
            "emotion": "Sleepy",
            "pose": "Curled up in a ball, eyes half-closed, one paw under cheek",
            "props": "Three Zzz bubbles floating up, small pillow underneath",
            "emoji": "\U0001f634",
        },
        {
            "id": "06_excited",
            "emotion": "Excited",
            "pose": "Standing on tip-toes, arms stretched upward wide open",
            "props": "Star-shaped eyes replacing normal eyes, speed lines radiating outward",
            "emoji": "\U0001f929",
        },
        {
            "id": "07_laughing",
            "emotion": "Laughing",
            "pose": "Leaning back, one paw on belly, body shaking",
            "props": "Eyes squeezed shut happily, wide open mouth, small tear of joy on one eye",
            "emoji": "\U0001f602",
        },
        {
            "id": "08_crying",
            "emotion": "Crying (comedic)",
            "pose": "Sitting on the ground, mouth wide open wailing",
            "props": "Exaggerated waterfall tears streaming from both eyes like fountains",
            "emoji": "\U0001f62d",
        },
        {
            "id": "09_surprised",
            "emotion": "Surprised",
            "pose": "Jumped back slightly, paws up near face in shock",
            "props": "Extremely wide circular eyes, tiny O-shaped mouth, exclamation mark above head",
            "emoji": "\U0001f632",
        },
        {
            "id": "10_thinking",
            "emotion": "Thinking",
            "pose": "Standing with one paw on chin, looking upward to the right",
            "props": "Three thought-bubble dots floating above head",
            "emoji": "\U0001f914",
        },
        {
            "id": "11_winking",
            "emotion": "Winking",
            "pose": "Standing playfully with slight hip tilt to one side",
            "props": "One eye closed in a wink, tongue sticking out slightly, sparkle near winking eye",
            "emoji": "\U0001f61c",
        },
        {
            "id": "12_confused",
            "emotion": "Confused",
            "pose": "Head tilted 15 degrees to the side, one ear flopped",
            "props": "Large question mark floating above head, one eyebrow raised",
            "emoji": "\u2753",
        },
        {
            "id": "13_blushing",
            "emotion": "Blushing / Shy",
            "pose": "Standing with paws pressed together in front of chest, looking down shyly",
            "props": "Extra-red enlarged blush marks on cheeks, small sweat drop on temple",
            "emoji": "\U0001f633",
        },
        {
            "id": "14_cool",
            "emotion": "Cool / Confident",
            "pose": "Leaning back casually with arms crossed or doing finger guns",
            "props": "Dark sunglasses on face, small sparkle effect near sunglasses",
            "emoji": "\U0001f60e",
        },
        {
            "id": "15_hungry",
            "emotion": "Hungry",
            "pose": "Standing with paws reaching out forward, mouth drooling",
            "props": "Single drool drop from mouth corner, fork and knife held in paws",
            "emoji": "\U0001f924",
        },
        {
            "id": "16_sick",
            "emotion": "Sick / Unwell",
            "pose": "Lying down on side, looking weak and pale",
            "props": "Slight green tint on face, thermometer in mouth, small cross-shaped bandaid",
            "emoji": "\U0001f912",
        },
        {
            "id": "17_celebrating",
            "emotion": "Celebrating",
            "pose": "Jumping high with arms thrown up, legs spread in a star jump",
            "props": "Colorful party hat on head, confetti pieces falling around, small party horn in paw",
            "emoji": "\U0001f389",
        },
        {
            "id": "18_tired",
            "emotion": "Tired / Exhausted",
            "pose": "Slouching forward, arms hanging limp, half-lidded eyes",
            "props": "Dark eye bags under eyes, holding a large coffee cup, steam rising from cup",
            "emoji": "\u2615",
        },
        {
            "id": "19_grateful",
            "emotion": "Grateful / Thankful",
            "pose": "Bowing forward deeply at 45 degrees, paws pressed together",
            "props": "Small sparkle effects around head, closed peaceful eyes",
            "emoji": "\U0001f64f",
        },
        {
            "id": "20_mischievous",
            "emotion": "Mischievous / Sneaky",
            "pose": "Side-eye glance to the left, body slightly turned away",
            "props": "One eyebrow raised high, sly smirk on mouth, small devil horns emerging",
            "emoji": "\U0001f60f",
        },
        {
            "id": "21_hello",
            "emotion": "Hello / Greeting",
            "pose": "Standing facing forward, one paw raised high waving enthusiastically",
            "props": "Bright cheerful smile, small motion lines near waving paw",
            "emoji": "\U0001f44b",
        },
        {
            "id": "22_bye",
            "emotion": "Goodbye",
            "pose": "Walking away toward the right, looking back over shoulder, waving one paw",
            "props": "Small motion lines indicating walking, gentle smile looking back",
            "emoji": "\U0001f44b",
        },
        {
            "id": "23_yes_ok",
            "emotion": "Yes / OK / Approval",
            "pose": "Standing confidently, one paw giving a big thumbs up",
            "props": "Big cheerful grin, sparkle near the thumb, slight confident lean",
            "emoji": "\U0001f44d",
        },
        {
            "id": "24_no",
            "emotion": "No / Rejection",
            "pose": "Standing with both paws crossed in a large X shape in front of body",
            "props": "Serious expression, slight head shake motion lines, large X mark effect",
            "emoji": "\U0001f645",
        },
    ],
    # Platforms to generate for
    "platforms": [
        "whatsapp",
        "telegram",
        "telegram_animated",  # Phase 2: Lottie TGS stickers
        "telegram_video",  # Phase 2: WebM VP9 video stickers
        "imessage_large",
        "whatsapp_native",  # Phase 3: WhatsApp native Android app
        "line",
        "print_etsy",
    ],
}


# =============================================================================
# EMOTION COVERAGE MATRIX
# Based on LINE Store marketplace analysis (March 2026).
# The essential set (8) is the minimum for a viable sticker pack.
# The extended set (24) covers all common conversational needs.
# =============================================================================
ESSENTIAL_EMOTIONS = [
    "happy",  # Joy, cheerful, smiling
    "love",  # Romance, hearts, affection
    "sad",  # Crying, disappointed, down
    "angry",  # Frustrated, mad, annoyed
    "laughing",  # LOL, funny, haha
    "surprised",  # Shocked, wow, unexpected
    "sleepy",  # Tired, zzz, yawning
    "ok",  # Thumbs up, approval, yes
]

EXTENDED_EMOTIONS = ESSENTIAL_EMOTIONS + [
    "grateful",  # Thank you, appreciation
    "sorry",  # Apologetic, regretful
    "confused",  # Thinking, questioning
    "proud",  # Accomplished, confident
    "shy",  # Blushing, embarrassed
    "hungry",  # Eating, food, drool
    "celebrating",  # Party, dancing, confetti
    "hello",  # Greeting, waving
    "goodbye",  # Farewell, bye-bye
    "sick",  # Unwell, fever, ill
    "working",  # Busy, focused, laptop
    "bored",  # Waiting, yawning
    "cool",  # Sunglasses, chill
    "scared",  # Frightened, hiding
    "encouraging",  # Fighting!, cheer up
    "goodnight",  # Sweet dreams, moon
]

# Aliases: map common sticker emotion names to canonical names above
_EMOTION_ALIASES = {
    "excited": "happy",
    "winking": "happy",
    "mischievous": "happy",
    "in love": "love",
    "crying": "sad",
    "crying (comedic)": "sad",
    "frustrated": "angry",
    "thinking": "confused",
    "blushing": "shy",
    "blushing / shy": "shy",
    "cool / confident": "cool",
    "tired": "sleepy",
    "tired / exhausted": "sleepy",
    "sick / unwell": "sick",
    "yes": "ok",
    "yes / ok / approval": "ok",
    "no": "ok",
    "no / rejection": "ok",
    "grateful / thankful": "grateful",
    "hello / greeting": "hello",
    "goodbye": "goodbye",
}


def validate_emotion_coverage(stickers: list[dict], level: str = "essential") -> dict:
    """
    Validate that a sticker pack covers the required emotional range.

    Args:
        stickers: List of sticker dicts from PACK_CONFIG["stickers"]
        level: "essential" (8 minimum) or "extended" (24 recommended)

    Returns:
        dict with keys: passed (bool), covered (list), missing (list),
                        coverage_pct (float), suggestions (list)
    """
    target = ESSENTIAL_EMOTIONS if level == "essential" else EXTENDED_EMOTIONS
    covered = set()

    for s in stickers:
        emotion = s.get("emotion", "").lower().strip()
        # Check direct match
        for target_emotion in target:
            if target_emotion in emotion:
                covered.add(target_emotion)
                break
        else:
            # Check aliases
            canonical = _EMOTION_ALIASES.get(emotion)
            if canonical and canonical in target:
                covered.add(canonical)

    missing = [e for e in target if e not in covered]
    coverage_pct = len(covered) / len(target) * 100 if target else 100.0

    suggestions = []
    if missing:
        suggestions.append(
            f"Add stickers for: {', '.join(missing)} "
            f"to improve conversational coverage."
        )
    if len(stickers) < 8:
        suggestions.append(
            "Pack has fewer than 8 stickers. Consider adding more "
            "for a competitive launch (8 minimum, 24 recommended)."
        )
    if len(stickers) == 8:
        suggestions.append(
            "8-sticker pack is viable for launch. Plan a 24-sticker "
            "expansion pack as a sequel for better marketplace performance."
        )

    return {
        "passed": len(missing) == 0,
        "covered": sorted(covered),
        "missing": missing,
        "coverage_pct": round(coverage_pct, 1),
        "suggestions": suggestions,
        "level": level,
        "total_stickers": len(stickers),
    }


# =============================================================================
# STICKER INTERACTION TYPES (for couple/pair packs)
# =============================================================================
INTERACTION_TYPES = [
    "shared_emotion",  # Both characters show same emotion (both happy)
    "complementary",  # Complementary emotions (one comforts the other)
    "interaction",  # Physical interaction (hugging, high-five, etc.)
    "solo_primary",  # Only primary character shown
    "solo_secondary",  # Only secondary character shown
]

RELATIONSHIP_TYPES = [
    "couple",  # Romantic pair (most popular on LINE Store)
    "friends",  # Friendship / buddy pair
    "family",  # Parent-child, siblings
    "rivals",  # Frenemies, competitive duo
]


# =============================================================================
# HELPER: Create additional pack configs easily
# =============================================================================
def create_pack_config(
    pack_id: str,
    pack_name: str,
    stickers: list[dict],
    platforms: list[str] | None = None,
    character: dict | None = None,
    characters: list[dict] | None = None,
    relationship: str | None = None,
    style: dict | None = None,
    publisher: str = "Your Brand Name",
    text_defaults: dict | None = None,
    localization: dict | None = None,
) -> dict:
    """
    Create a new pack config using the same character/style.

    Supports both single-character and dual-character (couple) packs.

    Args:
        pack_id: Unique pack identifier (kebab-case)
        pack_name: Display name (English)
        stickers: List of sticker definition dicts
        platforms: Target platforms list
        character: Single character dict (legacy, for single-char packs)
        characters: List of character dicts (for couple/pair packs)
            Each character dict should have a "role" field: "primary" or "secondary"
        relationship: Relationship type for couple packs (see RELATIONSHIP_TYPES)
        style: Art style dict
        publisher: Publisher name
        text_defaults: Text overlay defaults (None for no text)
        localization: Multi-language title/description dict, e.g.:
            {"id": {"title": "...", "description": "..."},
             "th": {"title": "...", "description": "..."},
             "ja": {"title": "...", "description": "..."}}

    Usage (single character):
        daily_life_pack = create_pack_config(
            pack_id="pack02_daily_life",
            pack_name="Mochi Daily Life",
            stickers=[
                {"id": "01_morning", "emotion": "Morning Stretch",
                 "pose": "...", "props": "...", "emoji": "..."},
                ...
            ]
        )

    Usage (couple pack):
        couple_pack = create_pack_config(
            pack_id="mochi-and-luna",
            pack_name="Mochi & Luna in Love",
            characters=[
                {"name": "Mochi", "role": "primary", "species": "cat", ...},
                {"name": "Luna", "role": "secondary", "species": "rabbit", ...},
            ],
            relationship="couple",
            stickers=[
                {"id": "01_hug", "emotion": "Love",
                 "interaction_type": "interaction",
                 "pose": "Mochi and Luna hugging each other tightly",
                 "props": "Floating hearts around them", "emoji": "..."},
                ...
            ]
        )
    """
    config = {
        "pack_id": pack_id,
        "pack_name": pack_name,
        "publisher": publisher,
        "style": style or STYLE,
        "text_defaults": text_defaults,
        "stickers": stickers,
        "platforms": platforms
        or [
            "whatsapp",
            "telegram",
            "telegram_animated",
            "telegram_video",
            "imessage_large",
            "line",
            "print_etsy",
        ],
    }

    # Support dual-character / couple packs
    if characters:
        config["characters"] = characters
        config["relationship"] = relationship or "couple"
        # Also set legacy "character" field to primary for backward compatibility
        primary = next(
            (c for c in characters if c.get("role") == "primary"), characters[0]
        )
        config["character"] = primary
    else:
        config["character"] = character or CHARACTER

    # Support localization for multi-market publishing
    if localization:
        config["localization"] = localization

    return config
