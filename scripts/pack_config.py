"""
Sticker Pack Configuration
Define your character, art style, and all stickers in a pack.
This config drives the entire generation + processing pipeline.
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
    "stickers": [
        {
            "id": "01_happy",
            "emotion": "Happy",
            "pose": "Jumping with arms raised, feet off the ground",
            "props": "Small sparkle effects (4-pointed stars) around head",
            "emoji": "\U0001f60a",
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
        "imessage_large",
        "line",
        "print_etsy",
    ],
}


# =============================================================================
# HELPER: Create additional pack configs easily
# =============================================================================
def create_pack_config(
    pack_id: str,
    pack_name: str,
    stickers: list[dict],
    platforms: list[str] | None = None,
    character: dict | None = None,
    style: dict | None = None,
    publisher: str = "Your Brand Name",
) -> dict:
    """
    Create a new pack config using the same character/style.

    Usage:
        daily_life_pack = create_pack_config(
            pack_id="pack02_daily_life",
            pack_name="Mochi Daily Life",
            stickers=[
                {"id": "01_morning", "emotion": "Morning Stretch",
                 "pose": "...", "props": "...", "emoji": "..."},
                ...
            ]
        )
    """
    return {
        "pack_id": pack_id,
        "pack_name": pack_name,
        "publisher": publisher,
        "character": character or CHARACTER,
        "style": style or STYLE,
        "stickers": stickers,
        "platforms": platforms
        or ["whatsapp", "telegram", "imessage_large", "line", "print_etsy"],
    }
