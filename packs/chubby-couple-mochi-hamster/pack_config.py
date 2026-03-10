"""
Pack configuration for Chubby Couple Mochi Hamster sticker pack.

Updated to use the dual-character system with interaction types,
localization support, and full essential emotion coverage.
"""

import sys
import os

# Allow importing from scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "scripts"))

from pack_config import create_pack_config

# ---------------------------------------------------------------------------
# Character Definitions (Dual Character / Couple Pack)
# ---------------------------------------------------------------------------
HAMSTER_PRIMARY = {
    "name": "MochiPink",
    "role": "primary",
    "species": "hamster",
    "body_color": "cream white",
    "blush_color": "soft pink",
    "eye_style": "large glossy black dot eyes",
    "outline_color": "black",
    "accessory": "small pink bow on head",
    "proportions": "extra chubby mochi-round body, tiny stubby limbs, oversized head",
}

HAMSTER_SECONDARY = {
    "name": "MochiBlue",
    "role": "secondary",
    "species": "hamster",
    "body_color": "cream white",
    "blush_color": "soft pink",
    "eye_style": "large glossy black dot eyes",
    "outline_color": "black",
    "accessory": "tiny blue bowtie",
    "proportions": "extra chubby mochi-round body, tiny stubby limbs, oversized head",
}

# ---------------------------------------------------------------------------
# Style
# ---------------------------------------------------------------------------
STYLE = {
    "outline_type": "thick black outline, 4-6px uniform weight",
    "coloring": "flat pastel colors with a single soft shadow beneath each character",
    "background": "transparent background, no background elements",
    "art_style": "kawaii flat vector illustration",
    "extras": "Clean minimal linework, no gradients, suitable for sticker die-cut",
}

# ---------------------------------------------------------------------------
# Sticker Definitions — 24 stickers covering all essential emotions
# Uses interaction_type field for couple-specific pose guidance.
# ---------------------------------------------------------------------------
STICKERS = [
    # === Essential 8 emotions ===
    {
        "id": "01_happy",
        "emotion": "Happy",
        "interaction_type": "shared_emotion",
        "pose": "Both hamsters jumping together with arms raised, feet off the ground",
        "props": "Small sparkle effects (4-pointed stars) around both heads",
        "emoji": "\U0001f60a",
        "animation": {"type": "bounce", "duration_ms": 2000, "loop": True},
    },
    {
        "id": "02_love",
        "emotion": "Love",
        "interaction_type": "interaction",
        "pose": "MochiPink and MochiBlue holding a large pink heart together, eyes closed blissfully",
        "props": "Small floating hearts above both heads, rosy cheeks",
        "emoji": "\u2764\ufe0f",
        "animation": {"type": "heartbeat", "duration_ms": 2500, "loop": True},
    },
    {
        "id": "03_sad",
        "emotion": "Sad",
        "interaction_type": "complementary",
        "pose": "MochiPink crying with head down, MochiBlue patting her head gently to comfort",
        "props": "Blue teardrop on MochiPink's cheek, small rain cloud above",
        "emoji": "\U0001f622",
    },
    {
        "id": "04_angry",
        "emotion": "Angry",
        "interaction_type": "shared_emotion",
        "pose": "Both hamsters standing with fists clenched, leaning forward aggressively at each other",
        "props": "Puffed red cheeks, steam lines rising from heads, anger vein on foreheads",
        "emoji": "\U0001f620",
        "animation": {"type": "shake", "duration_ms": 1500, "loop": False},
    },
    {
        "id": "05_laughing",
        "emotion": "Laughing",
        "interaction_type": "shared_emotion",
        "pose": "Both hamsters leaning back, paws on bellies, wide open mouths laughing",
        "props": "Eyes squeezed shut happily, tear of joy on one eye each",
        "emoji": "\U0001f602",
        "animation": {"type": "jelly", "duration_ms": 2000, "loop": True},
    },
    {
        "id": "06_surprised",
        "emotion": "Surprised",
        "interaction_type": "shared_emotion",
        "pose": "Both hamsters jumped back slightly, paws up near faces in shock",
        "props": "Extremely wide circular eyes, tiny O-shaped mouths, exclamation marks above",
        "emoji": "\U0001f632",
        "animation": {"type": "pop_in", "duration_ms": 1000, "loop": False},
    },
    {
        "id": "07_sleepy",
        "emotion": "Sleepy",
        "interaction_type": "interaction",
        "pose": "Both hamsters curled up together in a ball, eyes half-closed, snuggling",
        "props": "Three Zzz bubbles floating up, small shared pillow underneath",
        "emoji": "\U0001f634",
    },
    {
        "id": "08_thumbsup",
        "emotion": "OK",
        "interaction_type": "shared_emotion",
        "pose": "Both hamsters standing upright, each giving a confident thumbs up",
        "props": "Small sparkles near thumbs, confident smiles",
        "emoji": "\U0001f44d",
    },
    # === Extended emotions for 24-sticker pack ===
    {
        "id": "09_grateful",
        "emotion": "Grateful",
        "interaction_type": "interaction",
        "pose": "MochiBlue presenting a small gift box to MochiPink, MochiPink clasping paws in delight",
        "props": "Sparkle effect on gift, happy tears, small bow on gift box",
        "emoji": "\U0001f64f",
        "animation": {"type": "tada", "duration_ms": 2000, "loop": False},
    },
    {
        "id": "10_sorry",
        "emotion": "Sorry",
        "interaction_type": "complementary",
        "pose": "MochiBlue bowing deeply in apology, MochiPink with arms crossed looking away slightly",
        "props": "Sweat drops on MochiBlue, small dark cloud above",
        "emoji": "\U0001f625",
    },
    {
        "id": "11_confused",
        "emotion": "Confused",
        "interaction_type": "shared_emotion",
        "pose": "Both hamsters tilting heads to the same side with one paw on chin",
        "props": "Question marks floating above both heads",
        "emoji": "\U0001f914",
    },
    {
        "id": "12_shy",
        "emotion": "Shy",
        "interaction_type": "interaction",
        "pose": "MochiPink hiding behind MochiBlue, peeking out shyly from one side",
        "props": "Intense blushing on MochiPink, small heart above",
        "emoji": "\U0001f633",
    },
    {
        "id": "13_hungry",
        "emotion": "Hungry",
        "interaction_type": "interaction",
        "pose": "Both hamsters sitting at a tiny table, cheeks stuffed full with seeds",
        "props": "Pile of sunflower seeds on table, drool drops, happy cheek pouches",
        "emoji": "\U0001f60b",
    },
    {
        "id": "14_celebrating",
        "emotion": "Celebrating",
        "interaction_type": "interaction",
        "pose": "Both hamsters throwing confetti in the air, standing on tippy toes",
        "props": "Colorful confetti and streamers, party hats on both",
        "emoji": "\U0001f389",
        "animation": {"type": "tada", "duration_ms": 2000, "loop": False},
    },
    {
        "id": "15_hello",
        "emotion": "Hello",
        "interaction_type": "shared_emotion",
        "pose": "Both hamsters waving cheerfully with one paw raised high",
        "props": "Speech bubble with 'Hi!' text, sparkles",
        "emoji": "\U0001f44b",
        "animation": {"type": "wave", "duration_ms": 2000, "loop": True},
    },
    {
        "id": "16_goodbye",
        "emotion": "Goodbye",
        "interaction_type": "complementary",
        "pose": "MochiBlue walking away waving, MochiPink waving back with a small tear",
        "props": "Waving motion lines, small heart trail between them",
        "emoji": "\U0001f44b",
    },
    {
        "id": "17_sick",
        "emotion": "Sick",
        "interaction_type": "complementary",
        "pose": "MochiPink in bed with thermometer in mouth, MochiBlue holding a bowl of soup",
        "props": "Small blanket, red cheeks (fever), steam from soup bowl",
        "emoji": "\U0001f912",
    },
    {
        "id": "18_working",
        "emotion": "Working",
        "interaction_type": "shared_emotion",
        "pose": "Both hamsters sitting at tiny laptops side by side, focused expressions",
        "props": "Small coffee cups beside them, concentrated eyebrows",
        "emoji": "\U0001f4bb",
    },
    {
        "id": "19_bored",
        "emotion": "Bored",
        "interaction_type": "shared_emotion",
        "pose": "Both hamsters lying flat on ground, arms out, staring blankly upward",
        "props": "Flat eyes, deflated body language, small spirals above heads",
        "emoji": "\U0001f611",
    },
    {
        "id": "20_cool",
        "emotion": "Cool",
        "interaction_type": "shared_emotion",
        "pose": "Both hamsters wearing tiny sunglasses, leaning back confidently with arms crossed",
        "props": "Sparkle on sunglasses lens, slight smirk",
        "emoji": "\U0001f60e",
    },
    {
        "id": "21_scared",
        "emotion": "Scared",
        "interaction_type": "interaction",
        "pose": "MochiPink and MochiBlue hugging each other tightly in fear, both trembling",
        "props": "Wide eyes, sweat drops, jagged fear lines around them",
        "emoji": "\U0001f631",
        "animation": {"type": "shake", "duration_ms": 1500, "loop": True},
    },
    {
        "id": "22_encouraging",
        "emotion": "Encouraging",
        "interaction_type": "complementary",
        "pose": "MochiBlue cheering with a small flag, MochiPink flexing tiny arm muscles",
        "props": "Flag says 'Go!', fire aura around MochiPink, sparkles",
        "emoji": "\U0001f4aa",
    },
    {
        "id": "23_goodnight",
        "emotion": "Goodnight",
        "interaction_type": "interaction",
        "pose": "Both hamsters sleeping together under a tiny blanket, peaceful smiles",
        "props": "Crescent moon and stars above, Zzz bubbles, soft glow",
        "emoji": "\U0001f319",
    },
    {
        "id": "24_kiss",
        "emotion": "Love",
        "interaction_type": "interaction",
        "pose": "MochiBlue giving MochiPink a tiny kiss on the cheek, MochiPink blushing",
        "props": "Large pink heart explosion between them, sparkle effects",
        "emoji": "\U0001f618",
        "animation": {"type": "heartbeat", "duration_ms": 2500, "loop": True},
    },
]

# ---------------------------------------------------------------------------
# Localization — multi-language titles for regional LINE Store publishing
# ---------------------------------------------------------------------------
LOCALIZATION = {
    "id": {
        "title": "Mochi Hamster Pasangan Lucu",
        "description": "Stiker pasangan hamster mochi yang lucu dan menggemaskan",
    },
    "th": {
        "title": "\u0e2b\u0e21\u0e39\u0e42\u0e21\u0e08\u0e34\u0e04\u0e39\u0e48\u0e23\u0e31\u0e01",
        "description": "\u0e2a\u0e15\u0e34\u0e4a\u0e01\u0e40\u0e01\u0e2d\u0e23\u0e4c\u0e2b\u0e21\u0e39\u0e42\u0e21\u0e08\u0e34\u0e04\u0e39\u0e48\u0e23\u0e31\u0e01\u0e19\u0e48\u0e32\u0e23\u0e31\u0e01",
    },
    "ja": {
        "title": "\u3082\u3061\u3082\u3061\u30cf\u30e0\u30b9\u30bf\u30fc\u30ab\u30c3\u30d7\u30eb",
        "description": "\u304b\u308f\u3044\u3044\u30cf\u30e0\u30b9\u30bf\u30fc\u30ab\u30c3\u30d7\u30eb\u306e\u30b9\u30bf\u30f3\u30d7",
    },
    "zh_TW": {
        "title": "\u9ebb\u7cec\u5009\u9f20\u60c5\u4fb6",
        "description": "\u53ef\u611b\u7684\u9ebb\u7cec\u5009\u9f20\u60c5\u4fb6\u8cbc\u5716",
    },
}

# ---------------------------------------------------------------------------
# Build PACK_CONFIG using the new create_pack_config helper
# ---------------------------------------------------------------------------
PACK_CONFIG = create_pack_config(
    pack_id="chubby-couple-mochi-hamster",
    pack_name="Chubby Couple Mochi Hamster",
    publisher="StickerFramework",
    characters=[HAMSTER_PRIMARY, HAMSTER_SECONDARY],
    relationship="couple",
    style=STYLE,
    stickers=STICKERS,
    platforms=[
        "line",
        "line_animated",
        "telegram",
        "telegram_animated",
        "telegram_video",
        "whatsapp",
        "imessage_large",
        "print_etsy",
    ],
    localization=LOCALIZATION,
)
