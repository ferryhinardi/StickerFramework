"""
Sticker Pack Configuration — Jesus – Faith and Peace
=====================================================
A cute, chibi Jesus character spreading faith, peace, and blessings.
Warm pastel illustration style with thick outlines.

16 stickers matching the published LINE pack (LQu3ADYzrcqp2KCs).
Source images in split/. Text is composited in post-processing (Pillow).
"""

# =============================================================================
# CHARACTER DEFINITION
# =============================================================================
CHARACTER = {
    "name": "Jesus",
    "species": "human",
    "body_color": "#F5DEB3",  # warm wheat skin tone
    "blush_color": "#FFB6C1",  # light pink
    "outline_color": "#4A3728",  # warm dark brown
    "eye_style": "large, warm black oval eyes with gentle expression, no pupils, very expressive",
    "accessory": "simple white robe with light blue sash, small beard, shoulder-length brown hair",
    "proportions": "chibi, round face is 50% of body height, small hands, oversized head, cute stubby body",
    "body_description": (
        "cute chibi Jesus character, warm wheat skin, "
        "large gentle black oval eyes, small warm smile, "
        "short brown beard, shoulder-length wavy brown hair, "
        "simple flowing white robe with light blue sash, "
        "round chibi proportions, oversized head, stubby limbs, "
        "pink blush marks on cheeks, peaceful loving expression"
    ),
    "features": [
        "chibi proportions",
        "warm wheat skin",
        "gentle black oval eyes",
        "short brown beard",
        "wavy brown hair",
        "white robe with blue sash",
        "pink blush cheeks",
        "peaceful expression",
    ],
}

# =============================================================================
# ART STYLE — warm pastel illustration
# =============================================================================
STYLE = {
    "art_style": "painted_illustration",
    "outline_type": "thick warm brown outlines, consistent 3-4px width",
    "coloring": "warm pastel colors, soft watercolor-like shading, gentle light source from above",
    "background": "clean solid white background with no other elements",
    "extras": (
        "kawaii sticker illustration style, gentle peaceful poses, "
        "soft glow effects and small sparkles, "
        "warm comforting aesthetic with round soft shapes"
    ),
}

# =============================================================================
# TEXT DEFAULTS
# =============================================================================
TEXT_DEFAULTS = {
    "font": "FredokaOne-Regular.ttf",
    "font_size": 80,
    "outline_width": 6,
    "outline_color": "#3A2A1A",
    "shadow_offset": [4, 5],
    "shadow_color": "#00000066",
    "position": "top-center",
    "padding_top": 25,
}

# =============================================================================
# PACK: Jesus – Faith and Peace (16 stickers — matches LINE pack LQu3ADYzrcqp2KCs)
# =============================================================================
PACK_CONFIG = {
    "pack_id": "jesus-faith-and-peace",
    "pack_name": "Jesus – Faith and Peace",
    "publisher": "BobaStickers",
    "character": CHARACTER,
    "style": STYLE,
    "text_defaults": TEXT_DEFAULTS,
    "stickers": [
        {
            "id": "01_god_bless_you",
            "emotion": "Loving / Blessing",
            "pose": "Both hands raised gently outward, palms facing forward in a blessing gesture",
            "props": "Soft golden glow around hands, small sparkles, peaceful closed-eye smile",
            "emoji": "🙏",
            "text": {"content": "GOD BLESS YOU", "color": "#DAA520"},
        },
        {
            "id": "02_peace_be_with_you",
            "emotion": "Calm / Peaceful",
            "pose": "Standing peacefully with both arms open wide in welcoming gesture",
            "props": "Dove silhouette, olive branch, soft circular glow behind head",
            "emoji": "☮️",
            "text": {"content": "PEACE BE\nWITH YOU", "color": "#3CB371"},
        },
        {
            "id": "03_have_faith",
            "emotion": "Encouraging / Uplifting",
            "pose": "One hand on heart, the other reaching out warmly, confident gentle smile",
            "props": "Small heart near chest, warm sparkle effects, determined kind eyes",
            "emoji": "✨",
            "text": {"content": "HAVE FAITH", "color": "#4682B4"},
        },
        {
            "id": "04_praying_for_you",
            "emotion": "Compassionate / Prayerful",
            "pose": "Hands clasped together in prayer, head slightly bowed, eyes closed",
            "props": "Small rays of light above, serene peaceful expression, soft glow",
            "emoji": "🙏",
            "text": {"content": "PRAYING\nFOR YOU", "color": "#6A5ACD"},
        },
        {
            "id": "05_do_not_fear",
            "emotion": "Reassuring / Brave",
            "pose": "One hand raised open in a stop/reassurance gesture, calm strong expression",
            "props": "Shield symbol, gentle rays of light, strong but peaceful energy",
            "emoji": "🛡️",
            "text": {"content": "DO NOT\nFEAR", "color": "#B22222"},
        },
        {
            "id": "06_i_am_with_you",
            "emotion": "Comforting / Present",
            "pose": "Arms open wide as if offering a hug, warm gentle smile",
            "props": "Soft warm glow, small hearts, welcoming open posture",
            "emoji": "🤗",
            "text": {"content": "I AM\nWITH YOU", "color": "#8B008B"},
        },
        {
            "id": "07_trust_in_him",
            "emotion": "Reassuring / Comforting",
            "pose": "Sitting calmly with hands on knees, gentle warm smile, relaxed posture",
            "props": "Soft warm glow around body, small floating hearts, calm serene vibe",
            "emoji": "💙",
            "text": {"content": "TRUST\nIN HIM", "color": "#4169E1"},
        },
        {
            "id": "08_god_is_good",
            "emotion": "Joyful / Grateful",
            "pose": "Jumping slightly with both fists up in celebration, wide happy grin",
            "props": "Star sparkles around, confetti-like light particles, joyful energy",
            "emoji": "🌟",
            "text": {"content": "GOD IS GOOD", "color": "#FF8C00"},
        },
        {
            "id": "09_amen",
            "emotion": "Reverent / Agreement",
            "pose": "Hands clasped, gentle nod, serene closed-eye expression",
            "props": "Soft halo of light, tiny cross detail on robe, peaceful aura",
            "emoji": "🕊️",
            "text": {"content": "AMEN", "color": "#8B6914"},
        },
        {
            "id": "10_stay_strong",
            "emotion": "Encouraging / Powerful",
            "pose": "One fist raised upward in encouragement, determined confident smile",
            "props": "Burst of energy lines, small lightning sparks, strong uplifting vibe",
            "emoji": "💪",
            "text": {"content": "STAY\nSTRONG", "color": "#CC0000"},
        },
        {
            "id": "11_thank_you_lord",
            "emotion": "Grateful / Thankful",
            "pose": "Looking upward with both hands raised in gratitude, beaming smile",
            "props": "Rays of warm light from above, small golden sparkles, tears of joy",
            "emoji": "💛",
            "text": {"content": "THANK YOU\nLORD", "color": "#CD853F"},
        },
        {
            "id": "12_forgive",
            "emotion": "Gracious / Merciful",
            "pose": "Hands open and extended forward in a gesture of giving/offering, soft smile",
            "props": "Soft white light emanating from hands, gentle peaceful aura, small dove",
            "emoji": "🕊️",
            "text": {"content": "FORGIVE", "color": "#228B22"},
        },
        {
            "id": "13_love_one_another",
            "emotion": "Loving / Compassionate",
            "pose": "Hugging self with both arms, radiating warmth, eyes closed in joy",
            "props": "Pink and red hearts floating all around, rosy cheeks, warm pink glow",
            "emoji": "❤️",
            "text": {"content": "LOVE ONE\nANOTHER", "color": "#DC143C"},
        },
        {
            "id": "14_be_kind",
            "emotion": "Gentle / Sweet",
            "pose": "Offering a small flower or gift with one hand, gentle shy smile",
            "props": "Small colorful flowers, sparkles, warm yellow glow, soft kind energy",
            "emoji": "🌸",
            "text": {"content": "BE KIND", "color": "#FF69B4"},
        },
        {
            "id": "15_you_are_loved",
            "emotion": "Warm / Encouraging",
            "pose": "Pointing gently forward at the viewer with one hand, warm knowing smile",
            "props": "Heart-shaped sparkle near pointing hand, warm golden glow",
            "emoji": "🥰",
            "text": {"content": "YOU ARE\nLOVED", "color": "#E75480"},
        },
        {
            "id": "16_good_night",
            "emotion": "Gentle / Sleepy",
            "pose": "Eyes half-closed, one hand waving softly, slight sleepy tilt",
            "props": "Crescent moon, tiny stars, soft blue-purple night glow, zzz",
            "emoji": "🌙",
            "text": {"content": "GOOD NIGHT", "color": "#483D8B"},
        },
    ],
    "platforms": [
        "whatsapp",
        "telegram",
        "imessage_large",
        "print_etsy",
    ],
}
