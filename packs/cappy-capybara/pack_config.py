"""
Sticker Pack Configuration — Cappy the Chill Capybara
=====================================================
A round, zen-like capybara with an orange on its head.
Targets the underserved capybara niche on LINE (<3K packs).

16 stickers covering essential daily-chat emotions.
Use with ChatGPT UI (two 2×4 composite sheets) or API pipeline.
"""

# =============================================================================
# CHARACTER DEFINITION
# =============================================================================
CHARACTER = {
    "name": "Cappy",
    "species": "round capybara",
    "body_color": "#C4956A",  # warm brown
    "blush_color": "#FFB4B4",  # soft pink
    "outline_color": "#4A3728",  # dark brown
    "eye_style": "small round black dot eyes, calm and content, slightly droopy for chill vibes",
    "accessory": "tiny orange (mikan) sitting on top of head — the iconic capybara meme",
    "proportions": "chibi, very round body like a potato, tiny stubby legs, head is 50% of body height",
    "extra_features": (
        "small rounded ears on top of head, "
        "short flat nose/snout, "
        "tiny tail (barely visible), "
        "soft gradient-free flat coloring"
    ),
}

# =============================================================================
# ART STYLE
# =============================================================================
STYLE = {
    "outline_type": "thick uniform dark brown outline, consistent 3-4px width",
    "coloring": "flat colors only, absolutely no gradients, no realistic shading",
    "background": "clean solid white background with no other elements",
    "extras": (
        "die-cut sticker style with a thick white outline border "
        "around the ENTIRE character. "
        "Kawaii aesthetic — simple, round, and expressive. "
        "Minimal detail, maximum cuteness."
    ),
}

# =============================================================================
# PACK: Cappy the Chill Capybara (16 stickers)
# =============================================================================
PACK_CONFIG = {
    "pack_id": "cappy-capybara",
    "pack_name": "Cappy the Chill Capybara",
    "publisher": "BobaStickers",
    "character": CHARACTER,
    "style": STYLE,
    "stickers": [
        # --- Sheet 1: Stickers 01–08 ---
        {
            "id": "01_good_morning",
            "emotion": "Good Morning",
            "pose": "Sitting up sleepily, one stubby arm rubbing eye, yawning with small open mouth",
            "props": "Small sun icon in top-right corner, orange slightly tilted on head",
            "emoji": "🌅",
        },
        {
            "id": "02_ok_thumbs_up",
            "emotion": "OK / Thumbs Up",
            "pose": "Standing facing forward, one stubby arm raised giving a thumbs up, confident lean",
            "props": "Sparkle near thumb, cheerful closed-eye smile",
            "emoji": "👍",
        },
        {
            "id": "03_thank_you",
            "emotion": "Thank You",
            "pose": "Bowing forward at 45 degrees, both stubby arms pressed together in front",
            "props": "Small sparkle effects around head, peaceful closed eyes, orange wobbling on head",
            "emoji": "🙏",
        },
        {
            "id": "04_lol",
            "emotion": "LOL / Laughing",
            "pose": "Leaning back, round body shaking, one arm on belly",
            "props": "Eyes squeezed shut in joy, wide open laughing mouth, single tear of joy, orange bouncing off head slightly",
            "emoji": "😂",
        },
        {
            "id": "05_love",
            "emotion": "Love / Heart",
            "pose": "Both stubby arms hugging a large pink heart against round body",
            "props": "Eyes closed blissfully, pink blush on cheeks, small floating hearts above",
            "emoji": "❤️",
        },
        {
            "id": "06_sleepy",
            "emotion": "Sleepy / Zzz",
            "pose": "Lying on side curled up in a ball, eyes closed, one arm tucked under cheek",
            "props": "Three Zzz bubbles floating up, small pillow under head, orange rolled off next to head",
            "emoji": "😴",
        },
        {
            "id": "07_hungry",
            "emotion": "Hungry",
            "pose": "Standing with both stubby arms reaching forward, mouth open drooling",
            "props": "Single drool drop from corner of mouth, eyes sparkling with anticipation, imaginary steam/aroma lines",
            "emoji": "🤤",
        },
        {
            "id": "08_working_hard",
            "emotion": "Working Hard / Busy",
            "pose": "Sitting at tiny laptop, stubby arms typing, focused squinting expression",
            "props": "Small sweat drop on temple, steam rising from coffee cup beside laptop, orange balanced on head",
            "emoji": "💻",
        },
        # --- Sheet 2: Stickers 09–16 ---
        {
            "id": "09_excited",
            "emotion": "Excited / Yay",
            "pose": "Jumping with both stubby arms thrown up, feet off ground, body stretched upward",
            "props": "Star-shaped sparkles around body, wide open happy mouth, orange flying up above head",
            "emoji": "🤩",
        },
        {
            "id": "10_sad",
            "emotion": "Sad",
            "pose": "Sitting hunched over, head down, ears drooping slightly",
            "props": "Single large blue teardrop on cheek, small rain cloud above head, orange sitting sadly on head",
            "emoji": "😢",
        },
        {
            "id": "11_angry",
            "emotion": "Angry / Frustrated",
            "pose": "Standing with stubby arms at sides clenched, leaning forward, cheeks puffed",
            "props": "Red puffed cheeks, steam lines from head, anger vein mark on forehead, orange trembling on head",
            "emoji": "😤",
        },
        {
            "id": "12_sorry",
            "emotion": "Sorry / Apologize",
            "pose": "Deep bow with body bent forward, stubby arms at sides, looking up with guilty eyes",
            "props": "Large sweat drop on head, wavy guilt lines around body, orange about to fall off head",
            "emoji": "🙇",
        },
        {
            "id": "13_bye",
            "emotion": "Bye Bye",
            "pose": "Walking away to the right, looking back over shoulder, one stubby arm waving",
            "props": "Small motion lines near feet, gentle smile looking back, orange secure on head",
            "emoji": "👋",
        },
        {
            "id": "14_thinking",
            "emotion": "Thinking / Hmm",
            "pose": "Standing with one stubby arm on chin, looking upward to the right",
            "props": "Three thought-bubble dots floating above, one eyebrow slightly raised, orange tilted on head",
            "emoji": "🤔",
        },
        {
            "id": "15_cheering",
            "emotion": "Cheering / You Can Do It",
            "pose": "Standing on tippy-toes, both stubby arms pumping in the air like cheerleader",
            "props": "Determined bright eyes, small sparkle effects, motion lines showing energy, orange bouncing",
            "emoji": "💪",
        },
        {
            "id": "16_good_night",
            "emotion": "Good Night",
            "pose": "Lying in a tiny round bed, eyes peacefully closed, blanket pulled up to chin",
            "props": "Small crescent moon and stars above, orange on bedside, calm serene expression",
            "emoji": "🌙",
        },
    ],
    "platforms": [
        "line",
        "telegram",
        "whatsapp",
        "imessage_large",
        "print_etsy",
    ],
}
