"""
Sticker Pack Configuration — Cappy the Chill Capybara Vol.2: Sassy Replies
==========================================================================
Same beloved Cappy, now with 16 sassy daily-reply stickers.
Fills the gaps v1 didn't cover — high-frequency chat reactions
popular across Asian markets (LINE Japan/Thailand/Indonesia/Taiwan).

Strategy:
  - Reuse v1 character for brand continuity (fans buy the sequel)
  - "Reply" stickers get 3-5x more daily sends than emotion stickers
  - Sassy + cute tone is the #1 selling style on LINE
  - "Noted", "Fighting!", "Hug", "Side-eye tea" are proven top performers
"""

# =============================================================================
# CHARACTER DEFINITION  (identical to v1 — brand consistency)
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
    # v2 fields — used by comfyui_generator for character-agnostic prompts
    "body_description": (
        "a single cute round chibi capybara character, warm brown fur, "
        "small round black dot eyes, calm and content expression, "
        "tiny orange mikan fruit sitting on top of head, "
        "very round potato-shaped body, tiny stubby legs, "
        "small rounded ears, short flat snout, "
        "thick dark brown outline, flat colors, no gradients"
    ),
    "features": [
        "small rounded ears on top of head",
        "short flat nose/snout",
        "tiny tail (barely visible)",
        "soft gradient-free flat coloring",
    ],
    # legacy field kept for backward compatibility
    "extra_features": (
        "small rounded ears on top of head, "
        "short flat nose/snout, "
        "tiny tail (barely visible), "
        "soft gradient-free flat coloring"
    ),
}

# =============================================================================
# ART STYLE  (identical to v1 — visual consistency)
# =============================================================================
STYLE = {
    "art_style": "flat_vector",  # v2 field — controls prompt template selection
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
# PACK: Cappy the Chill Capybara Vol.2 — Sassy Replies (16 stickers)
#
# Theme rationale:
#   v1 covered basic emotions (happy, sad, angry, love, etc.)
#   v2 covers REACTIONS — things you send AS a reply in chat.
#   These get the highest daily-send rates on messaging platforms.
# =============================================================================
PACK_CONFIG = {
    "pack_id": "cappy-capybara-2",
    "pack_name": "Cappy the Chill Capybara Vol.2",
    "publisher": "BobaStickers",
    "character": CHARACTER,
    "style": STYLE,
    "text_defaults": {  # v2 field — pack-level Pillow text styling
        "font_size": "auto",
        "color": "#FFFFFF",
        "stroke_color": "#4A3728",
        "stroke_width": 8,
        "position": "bottom",
    },
    # -----------------------------------------------------------------
    # TEXT OVERLAY (optional per sticker)
    #
    # The "text" field is optional. Two forms:
    #   Simple:  "text": "NOTED!"       — uses all defaults
    #   Full:    "text": {
    #       "content":      "NOTED!",   # required — the text to show
    #       "position":     "bottom",   # "top" | "bottom" | "center"
    #       "font_size":    "auto",     # "auto" or int
    #       "color":        "#FFFFFF",  # hex fill
    #       "stroke_color": "#4A3728",  # hex outline
    #       "stroke_width": 8,          # stroke px
    #       "style":        "bold",     # "bold" | "regular"
    #   }
    #
    # Text is rendered AFTER bg-removal + outline, BEFORE resize.
    # If omitted, no text is added (the sticker speaks for itself).
    # -----------------------------------------------------------------
    "stickers": [
        # --- Sheet 1: Stickers 01-08  (Quick Replies) ---
        {
            "id": "01_omg",
            "emotion": "OMG / Shocked",
            "pose": "Standing upright, stubby arms pressed against cheeks, body leaning back slightly",
            "props": "Jaw dropped wide open, eyes huge perfect circles, orange popping off head in surprise, exclamation marks above",
            "emoji": "\U0001f631",
            "text": "OMG!",  # simple form — white text, dark brown stroke, bottom
        },
        {
            "id": "02_no_way",
            "emotion": "No Way / Disbelief",
            "pose": "Dramatically fainting backward, one stubby arm on forehead, body tilted 45 degrees",
            "props": "Eyes spiraling dizzy swirls, orange flying off head, small impact star where body will land",
            "emoji": "\U0001f635",
            "text": "NO WAY",
        },
        {
            "id": "03_noted",
            "emotion": "Noted / Roger That",
            "pose": "Standing at attention like a soldier, one stubby arm doing a crisp salute at forehead",
            "props": "Serious determined eyes, small notepad in other arm, orange sitting perfectly straight on head",
            "emoji": "\U0001fae1",
            "text": "NOTED!",
        },
        {
            "id": "04_brb",
            "emotion": "BRB / Be Right Back",
            "pose": "Running to the right at full speed, stubby legs in motion blur, body stretched forward",
            "props": "Dust cloud behind feet, speed lines trailing body, orange barely hanging on head, determined expression",
            "emoji": "\U0001f3c3",
            "text": "BRB",
        },
        {
            "id": "05_wait_what",
            "emotion": "Wait What / Double Take",
            "pose": "Head snapped to look back over shoulder, body still facing forward, one ear perked up",
            "props": "One eyebrow raised high, question mark and exclamation mark both above head, orange tilted sideways",
            "emoji": "\U0001f928",
            "text": "WAIT WHAT",
        },
        {
            "id": "06_lmao",
            "emotion": "LMAO / Rolling on Floor",
            "pose": "Lying on back rolling side to side, stubby arms and legs flailing in the air",
            "props": "Eyes squeezed shut tears streaming, wide open laughing mouth, orange rolled away on floor, impact lines showing shaking",
            "emoji": "\U0001f923",
            "text": "LMAO",
        },
        {
            "id": "07_yay",
            "emotion": "Yay / Celebrating",
            "pose": "Jumping high with stubby arms thrown up, small party hat on head next to orange",
            "props": "Colorful confetti falling around, star-shaped sparkles, wide open happy mouth, feet off ground",
            "emoji": "\U0001f389",
            "text": "YAY!",
        },
        {
            "id": "08_send_help",
            "emotion": "Send Help / Overwhelmed",
            "pose": "Buried under a pile of papers and books, only head and one stubby arm visible poking out",
            "props": "Swirly exhausted eyes, sweat drops, orange squished flat on head, arm reaching out desperately",
            "emoji": "\U0001f635\u200d\U0001f4ab",
            "text": {  # full dict form — custom colors for drama
                "content": "HELP",
                "position": "top",
                "color": "#FF6B6B",
                "stroke_color": "#8B0000",
            },
        },
        # --- Sheet 2: Stickers 09-16  (Mood Reactions) ---
        {
            "id": "09_dead_tired",
            "emotion": "So Tired / Dead Inside",
            "pose": "Lying completely flat face-down on the ground, limbs spread out like a pancake",
            "props": "Translucent ghost-Cappy floating up from body (soul leaving), orange sitting next to collapsed body, X eyes",
            "emoji": "\U0001faa6",
            # no text — the ghost says it all
        },
        {
            "id": "10_jealous",
            "emotion": "Jealous / Want That",
            "pose": "Pressing face against invisible glass wall, stubby arms spread on glass, body squished forward",
            "props": "Sparkling envious eyes, drool from corner of mouth, steamy breath marks on glass, orange squished against glass",
            "emoji": "\U0001f924",
            # no text — expression speaks
        },
        {
            "id": "11_judging",
            "emotion": "Judging You / Side Eye",
            "pose": "Sitting cross-legged to the side, one stubby arm holding a tiny teacup near mouth, sipping",
            "props": "Extreme side-eye glance, one eyebrow raised, smug knowing smirk, orange tilted sassily on head",
            "emoji": "\U0001f928",
            # no text — the side-eye IS the message
        },
        {
            "id": "12_hug",
            "emotion": "Hug / Come Here",
            "pose": "Standing facing forward, both stubby arms stretched wide open, leaning forward invitingly",
            "props": "Warm gentle smile, sparkly soft eyes, small pink hearts floating around, orange wobbling on head",
            "emoji": "\U0001f917",
            "text": "HUG?",
        },
        {
            "id": "13_oops",
            "emotion": "Oops / My Bad",
            "pose": "Standing stiffly, one stubby arm behind head scratching nervously, slight lean to one side",
            "props": "Awkward forced grin, three large sweat drops, nervous squiggly lines around body, orange crooked on head",
            "emoji": "\U0001f605",
            "text": "OOPS",
        },
        {
            "id": "14_deal_with_it",
            "emotion": "Deal With It / Cool",
            "pose": "Walking confidently to the left, slight swagger lean, one stubby arm in pocket pose",
            "props": "Dark pixel sunglasses on face, sparkle glint on glasses, cool smirk, orange wearing tiny matching sunglasses",
            "emoji": "\U0001f60e",
            "text": "DEAL WITH IT",
        },
        {
            "id": "15_fighting",
            "emotion": "Fighting! / You Got This",
            "pose": "Standing on tiptoes, one stubby arm punching upward to the sky with clenched fist",
            "props": "Red headband tied on forehead with tails flowing, fire in eyes, determination blush, rising sun burst behind, orange secure on head above headband",
            "emoji": "\U0001f4aa",
            "text": "FIGHTING!",
        },
        {
            "id": "16_miss_you",
            "emotion": "Miss You / Lonely",
            "pose": "Sitting alone hugging a phone to chest with both stubby arms, knees pulled up",
            "props": "Single tear on cheek, soft sad eyes looking at phone screen glowing, small broken heart above, orange drooping sadly on head",
            "emoji": "\U0001f97a",
            # no text — the emotion is the sticker
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
