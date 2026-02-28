"""
LINE Emoji Pack Configuration — Chubby Mochi Hamster Emoji Vol.1
================================================================
A round, squishy hamster with puffed cheeks and warm orange-brown fur.
Painted illustration style with thick outlines, optimized for LINE Emoji.

LINE Emoji specs:
  - 180x180 PNG, transparent background, max 1 MB
  - Chat thumbnail: 96x74 PNG
  - Regular emoji set: 40 images (001.png - 040.png)
  - No text overlays (too small at 180px)
  - Face/head close-up framing (fill the canvas)

40 emoji covering daily conversation expressions.
"""

# =============================================================================
# CHARACTER DEFINITION (reused from chubby-mochi-hamster sticker packs)
# =============================================================================
CHARACTER = {
    "name": "Mochi Hamster",
    "species": "round hamster",
    "body_color": "#E8A84C",  # warm orange-brown
    "blush_color": "#FF9999",  # soft pink
    "outline_color": "#333333",  # dark charcoal
    "eye_style": "large shiny black round eyes, expressive, with tiny white highlight dots",
    "accessory": None,
    "proportions": "chibi, extremely round body like a ball, tiny stubby legs, head is 55% of body height",
    # --- SDXL prompt field ---
    "body_description": (
        "cute round chubby hamster, warm orange-brown fur, "
        "white belly patch, large shiny black round eyes, "
        "tiny highlight dots in eyes, small pink nose, "
        "large round ears, extremely round ball-shaped body, "
        "puffed cheek pouches, tiny stubby paws, "
        "pink blush marks on cheeks"
    ),
    "features": [
        "round chubby body",
        "warm orange-brown fur",
        "white belly patch",
        "puffed cheek pouches",
        "large round ears",
        "shiny black eyes with highlights",
        "tiny stubby paws",
        "pink blush cheeks",
    ],
}

# =============================================================================
# ART STYLE — painted illustration, optimized for emoji (bolder, simpler)
# =============================================================================
STYLE = {
    "art_style": "painted_illustration",
    "outline_type": "thick black outlines, consistent 4-5px width",
    "coloring": "semi-realistic painting style, soft painterly shading, warm color palette",
    "background": "transparent background, no background elements",
    "extras": (
        "emoji illustration style, single centered expression, "
        "large head close-up fills the frame, "
        "bold expressive face, kawaii aesthetic"
    ),
}

# =============================================================================
# PACK: Chubby Mochi Hamster Emoji Vol.1 (40 emoji)
# =============================================================================
PACK_CONFIG = {
    "pack_id": "chubby-mochi-hamster-emoji-1",
    "pack_name": "Chubby Mochi Hamster Emoji",
    "publisher": "FHStudio",
    "character": CHARACTER,
    "style": STYLE,
    "text_defaults": None,  # No text for emoji (180px is too small)
    "product_type": "line_emoji",  # NEW: distinguishes from "line_sticker"
    "emoji_set_type": "regular",  # regular | letters_numbers | kana | etc.
    "emoji_count": 40,
    "stickers": [
        # =====================================================================
        # GREETINGS & FAREWELLS (5)
        # =====================================================================
        {
            "id": "001_hello",
            "emotion": "Hello / Cheerful greeting",
            "pose": "Facing forward, one paw raised high waving enthusiastically",
            "props": "Bright cheerful smile, small motion lines near waving paw",
            "emoji": "\U0001f44b",
        },
        {
            "id": "002_bye",
            "emotion": "Goodbye / See you later",
            "pose": "Turned slightly away, looking back over shoulder, waving paw behind",
            "props": "Gentle smile, small tear in one eye, motion lines near waving paw",
            "emoji": "\U0001f44b",
        },
        {
            "id": "003_good_morning",
            "emotion": "Sleepy morning / Just woke up",
            "pose": "Sitting upright, stretching with both paws up high, big yawn",
            "props": "Half-closed drowsy eyes, tiny sparkle near stretch, messy fur on head",
            "emoji": "\u2600\ufe0f",
        },
        {
            "id": "004_good_night",
            "emotion": "Sleepy / Good night",
            "pose": "Curled up in a ball, eyes peacefully closed",
            "props": "Three Zzz floating up, small crescent moon above, serene face",
            "emoji": "\U0001f319",
        },
        {
            "id": "005_sup",
            "emotion": "Casual greeting / Hey there",
            "pose": "Leaning back casually, lazy half-wave with one paw, relaxed posture",
            "props": "Cool half-smile, slightly lidded relaxed eyes",
            "emoji": "\u270c\ufe0f",
        },
        # =====================================================================
        # AFFIRMATIVE / AGREEING (5)
        # =====================================================================
        {
            "id": "006_ok",
            "emotion": "OK / Approval / Thumbs up",
            "pose": "Standing confidently, one paw giving thumbs up",
            "props": "Cheerful grin, sparkle near thumb, confident expression",
            "emoji": "\U0001f44d",
        },
        {
            "id": "007_yes",
            "emotion": "Excited agreement / Celebration",
            "pose": "Jumping with both paws pumping in the air, huge grin",
            "props": "Sparkle effects, confetti pieces, speed lines showing energy",
            "emoji": "\U0001f389",
        },
        {
            "id": "008_sure",
            "emotion": "Casual agreement / No problem",
            "pose": "Casual nod, one paw making OK hand sign",
            "props": "Relaxed smile, slight head tilt, easygoing expression",
            "emoji": "\U0001f44c",
        },
        {
            "id": "009_noted",
            "emotion": "Acknowledged / Roger that",
            "pose": "Standing straight, one paw to forehead in salute pose",
            "props": "Determined focused eyes, slight smile, military-style salute",
            "emoji": "\U0001fae1",
        },
        {
            "id": "010_lets_go",
            "emotion": "Pumped up / Motivated / Let's do this",
            "pose": "Fists clenched at sides, leaning forward with determination",
            "props": "Fire aura behind, sparkling eyes, intense determined expression",
            "emoji": "\U0001f525",
        },
        # =====================================================================
        # NEGATIVE / REFUSAL (3)
        # =====================================================================
        {
            "id": "011_nope",
            "emotion": "Refusal / No way / Hard no",
            "pose": "Arms crossed in X shape, head turned sideways",
            "props": "Stern closed eyes, definitive expression, small X marks",
            "emoji": "\u274c",
        },
        {
            "id": "012_no_way",
            "emotion": "Disbelief / Cannot believe it",
            "pose": "Leaning far backward, paws up in shock, dramatic faint pose",
            "props": "Wide eyes, mouth agape, sweat drops, dramatic action lines",
            "emoji": "\U0001f62e",
        },
        {
            "id": "013_ugh",
            "emotion": "Annoyed / Fed up / Exasperated",
            "pose": "One paw on face in face-palm, other paw hanging limp",
            "props": "Half-lidded tired eyes, visible frustration, small vein mark on head",
            "emoji": "\U0001f926",
        },
        # =====================================================================
        # EMOTIONS — HAPPY (4)
        # =====================================================================
        {
            "id": "014_lol",
            "emotion": "Laughing hard / Can't stop laughing",
            "pose": "Rolling on back laughing, paws on belly, body shaking",
            "props": "Eyes squeezed shut, wide laughing mouth, tears of joy",
            "emoji": "\U0001f602",
        },
        {
            "id": "015_love",
            "emotion": "Love / In love / Affectionate",
            "pose": "Both paws hugging a large pink heart against round body",
            "props": "Heart-shaped eyes, floating hearts above, extra pink blush",
            "emoji": "\u2764\ufe0f",
        },
        {
            "id": "016_hug",
            "emotion": "Want to hug / Come here / Comforting",
            "pose": "Arms stretched wide open reaching forward for a big hug",
            "props": "Warm gentle smile, sparkle effects, inviting expression",
            "emoji": "\U0001fac2",
        },
        {
            "id": "017_yay",
            "emotion": "Pure joy / Celebration / Hooray",
            "pose": "Star jump with all four paws spread wide, biggest grin possible",
            "props": "Sparkle effects everywhere, confetti, rainbow effects, maximum happiness",
            "emoji": "\U0001f929",
        },
        # =====================================================================
        # EMOTIONS — SAD / WORRIED (4)
        # =====================================================================
        {
            "id": "018_sad",
            "emotion": "Sad / Feeling down / Depressed",
            "pose": "Hunched over sitting, head drooping down, paws hanging",
            "props": "Small rain cloud above head, droopy ears, single tear",
            "emoji": "\U0001f622",
        },
        {
            "id": "019_sorry",
            "emotion": "Sorry / Apologetic / Feel bad",
            "pose": "Deep bow with body bent forward, looking up with guilty eyes",
            "props": "Large sweat drop on head, wavy guilt lines around body",
            "emoji": "\U0001f647",
        },
        {
            "id": "020_cry",
            "emotion": "Crying hard / Very upset / Bawling",
            "pose": "Sitting with paws over eyes, body trembling",
            "props": "Waterfall tears streaming from both eyes, puddle forming",
            "emoji": "\U0001f62d",
        },
        {
            "id": "021_nooo",
            "emotion": "Despair / Dramatic dismay / Noooo",
            "pose": "On knees, paws reaching up dramatically, head tilted back wailing",
            "props": "Waterfall tears, dramatic background lines, mouth wide open screaming",
            "emoji": "\U0001f631",
        },
        # =====================================================================
        # EMOTIONS — SURPRISED / CONFUSED (4)
        # =====================================================================
        {
            "id": "022_what",
            "emotion": "Shocked / Surprised / What?!",
            "pose": "Jumped back, paws up near face in shock, mouth wide open",
            "props": "Extremely wide eyes, question marks and exclamation marks floating",
            "emoji": "\U0001f633",
        },
        {
            "id": "023_omg",
            "emotion": "OMG / Jaw drop / Astonished",
            "pose": "Both paws pressed against cheeks, jaw dropped wide open",
            "props": "Maximum wide eyes, sparkle shock effects, dramatic lighting",
            "emoji": "\U0001f632",
        },
        {
            "id": "024_thinking",
            "emotion": "Thinking / Pondering / Hmm",
            "pose": "One paw on chin, looking upward, other paw behind back",
            "props": "Thought bubble floating above, slightly furrowed brows, curious expression",
            "emoji": "\U0001f914",
        },
        {
            "id": "025_wut",
            "emotion": "Dumbfounded / Processing / Error",
            "pose": "Frozen stiff, blank stare, completely still",
            "props": "Loading/buffering icon above head, empty eyes, question marks",
            "emoji": "\U0001f610",
        },
        # =====================================================================
        # DAILY ACTIVITIES (6)
        # =====================================================================
        {
            "id": "026_hungry",
            "emotion": "Hungry / Starving / Want food",
            "pose": "Standing with paws reaching forward, mouth wide open drooling",
            "props": "Drool drop from mouth, sparkling eyes, deflated cheek pouches",
            "emoji": "\U0001f924",
        },
        {
            "id": "027_sleepy",
            "emotion": "Drowsy / Sleepy / About to doze off",
            "pose": "Standing but swaying, eyes half-closed and drooping",
            "props": "Small Zzz floating, drowsy drooping eyes, yawning mouth",
            "emoji": "\U0001f634",
        },
        {
            "id": "028_busy",
            "emotion": "Busy / Working hard / In the zone",
            "pose": "Sitting at tiny laptop, paws typing rapidly, focused squinting eyes",
            "props": "Sweat drop on temple, speed lines near typing paws, determined face",
            "emoji": "\U0001f4bb",
        },
        {
            "id": "029_coffee",
            "emotion": "Need caffeine / Tired but trying / Coffee time",
            "pose": "Both paws clutching a large coffee mug, sipping",
            "props": "Steam rising from mug, tired but grateful eyes, slight smile",
            "emoji": "\u2615",
        },
        {
            "id": "030_eating",
            "emotion": "Eating happily / Munching / Nom nom",
            "pose": "Both paws stuffing food into cheeks, cheek pouches fully puffed",
            "props": "Food particles flying, maximum puffed cheeks, closed happy eyes",
            "emoji": "\U0001f60b",
        },
        {
            "id": "031_running",
            "emotion": "In a hurry / Running late / Gotta go",
            "pose": "Running at full speed, body tilted forward, legs in motion blur",
            "props": "Speed lines behind, dust cloud, panicked determined expression",
            "emoji": "\U0001f3c3",
        },
        # =====================================================================
        # SOCIAL / CHAT (5)
        # =====================================================================
        {
            "id": "032_thank_you",
            "emotion": "Thank you / Grateful / Appreciation",
            "pose": "Bowing forward at 45 degrees, both paws pressed together",
            "props": "Peaceful closed eyes, sparkle effects around head, gentle smile",
            "emoji": "\U0001f64f",
        },
        {
            "id": "033_please",
            "emotion": "Begging / Pretty please / I need this",
            "pose": "Sitting with paws pressed together in prayer position, big round puppy eyes",
            "props": "Sparkling watery puppy eyes, slight head tilt, tiny sweat drop",
            "emoji": "\U0001f97a",
        },
        {
            "id": "034_fighting",
            "emotion": "Encouraging / You can do it / Fighting!",
            "pose": "One fist punching upward, other paw on hip, determined stance",
            "props": "Headband on forehead, fire in eyes, motion lines from fist",
            "emoji": "\U0001f4aa",
        },
        {
            "id": "035_miss_you",
            "emotion": "Missing someone / Lonely / Thinking of you",
            "pose": "Hugging a phone close to chest, slightly hunched, looking down",
            "props": "Sad gentle eyes, single small heart floating above, melancholy aura",
            "emoji": "\U0001f614",
        },
        {
            "id": "036_waiting",
            "emotion": "Waiting impatiently / Bored / How much longer",
            "pose": "Standing with arms crossed, tapping one foot repeatedly",
            "props": "Half-lidded unamused eyes, small clock icon, tap-tap motion lines",
            "emoji": "\u23f0",
        },
        # =====================================================================
        # FUN / EXPRESSIVE (4)
        # =====================================================================
        {
            "id": "037_cool",
            "emotion": "Cool / Confident / Deal with it",
            "pose": "Swagger lean-back pose, sunglasses on",
            "props": "Sparkling sunglasses, confident smirk, cool aura effects",
            "emoji": "\U0001f60e",
        },
        {
            "id": "038_angry",
            "emotion": "Angry / Frustrated / Mad",
            "pose": "Standing with fists clenched at sides, puffed cheeks, leaning forward aggressively",
            "props": "Steam coming from ears, vein mark on forehead, red face",
            "emoji": "\U0001f621",
        },
        {
            "id": "039_peek",
            "emotion": "Shy / Peeking / Curious but nervous",
            "pose": "Peeking out from behind a wall or corner, only half of face visible",
            "props": "One eye visible, blushing, cautious curious expression",
            "emoji": "\U0001fae3",
        },
        {
            "id": "040_sparkle",
            "emotion": "Sparkling / Magical / Fabulous",
            "pose": "Standing tall with both paws up showing off, head tilted with confident smile",
            "props": "Maximum sparkle effects everywhere, magical aura, twinkling stars",
            "emoji": "\u2728",
        },
    ],
    "platforms": [
        "line_emoji",
    ],
}
