"""
Configuration constants for LINE Creator Market automation.

URLs, timeouts, default submission values, selectors, and storage paths.
All selectors are verified against the live LINE Creator Market as of Feb 2026.
"""

from pathlib import Path

# ─── Repo root ──────────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).resolve().parent.parent

# ─── URLs ────────────────────────────────────────────────────────────────────
BASE_URL = "https://creator.line.me"
LOGIN_AUTH_URL = f"{BASE_URL}/signup/line_auth"  # Redirects to access.line.me OAuth
# Creator-specific paths (Creator ID: 5964498, URL path: LQu3ADYzrcqp2KCs)
CREATOR_PATH = "LQu3ADYzrcqp2KCs"
MY_STICKERS_URL = f"{BASE_URL}/my/{CREATOR_PATH}/sticker/"
CREATE_URL = f"{BASE_URL}/my/{CREATOR_PATH}/sticker/create"

# ─── Emoji URLs ──────────────────────────────────────────────────────────────
MY_EMOJI_URL = f"{BASE_URL}/my/{CREATOR_PATH}/emoji/"
EMOJI_CREATE_URL = f"{BASE_URL}/my/{CREATOR_PATH}/emoji/register"


def emoji_url(emoji_id: str) -> str:
    """Management page: /my/{creator}/emoji/{id}"""
    return f"{BASE_URL}/my/{CREATOR_PATH}/emoji/{emoji_id}"


def emoji_update_url(emoji_id: str) -> str:
    """Edit form: /my/{creator}/emoji/{id}/update"""
    return f"{BASE_URL}/my/{CREATOR_PATH}/emoji/{emoji_id}/update"


def emoji_image_url(emoji_id: str) -> str:
    """Image edit page: /my/{creator}/emoji/{id}/image"""
    return f"{BASE_URL}/my/{CREATOR_PATH}/emoji/{emoji_id}/image"


def emoji_price_url(emoji_id: str) -> str:
    """Price page: /my/{creator}/emoji/{id}/price (if separate from management)"""
    return f"{BASE_URL}/my/{CREATOR_PATH}/emoji/{emoji_id}/price"


def sticker_url(sticker_id: str) -> str:
    """Management page: /my/{creator}/sticker/{id}"""
    return f"{BASE_URL}/my/{CREATOR_PATH}/sticker/{sticker_id}"


def sticker_update_url(sticker_id: str) -> str:
    """Edit form: /my/{creator}/sticker/{id}/update"""
    return f"{BASE_URL}/my/{CREATOR_PATH}/sticker/{sticker_id}/update"


def sticker_image_url(sticker_id: str) -> str:
    """Image edit page: /my/{creator}/sticker/{id}/image"""
    return f"{BASE_URL}/my/{CREATOR_PATH}/sticker/{sticker_id}/image"


# ─── Timeouts (milliseconds) ────────────────────────────────────────────────
PAGE_LOAD_TIMEOUT = 60_000
UPLOAD_TIMEOUT = 60_000
SELECTOR_TIMEOUT = 10_000
SAVE_TIMEOUT = 15_000
LOGIN_TIMEOUT = 300_000  # 5 min for manual verification-code-in-app flow

# ─── Login selectors (access.line.me OAuth page) ────────────────────────────
SEL_LOGIN_LINK = 'a.mdGHD02Signup[href="/signup/line_auth"]'
SEL_LOGIN_EMAIL = 'input[name="tid"]'
SEL_LOGIN_PASSWORD = 'input[name="tpasswd"]'
SEL_LOGIN_SUBMIT = "button.MdBtn01"

# ─── Create / Update form selectors ─────────────────────────────────────────
# Named inputs
SEL_TITLE = 'input[name="meta[en][title]"]'
SEL_DESCRIPTION = 'textarea[name="meta[en][description]"]'
SEL_COPYRIGHT = 'input[name="copyright"]'
SEL_STICKER_TYPE = 'input[name="sticker_type"]'  # add [value="static"] etc.
SEL_AI_GENERATED = 'input[name="is_ai_generated"]'  # [value="true"|"false"]
SEL_AREA_GROUP = 'input[name="area_group"]'  # [value="all"|"lgbt"|"customized"]
SEL_AUTO_RELEASE = 'input[name="is_auto_release"]'  # [value="true"|"false"]
SEL_LICENSE_CERT = 'input[name="attachments[]"]'
SEL_DESIGN_URL = 'input[name="design_url"]'
SEL_REQUEST_COMMENT = 'textarea[name="request_comment"]'
SEL_XSRF_TOKEN = 'input[name="XSRF-TOKEN"]'

# Unnamed form radios — identified by section order (parent context needed)
# Privacy: unnamed, value="true" (Show) / "false" (Hide)
# Premium: unnamed, value="true" (Join) / "false" (Not interested)
# Sticker Arranging: unnamed, value="true" (Participate) / "false" (Not interested)
# Trial Promotions: unnamed, value="true" (Participate) / "false" (Not interested)
# Includes Photos: unnamed, value="false" (Does not include) / "true" (Does include)

# Selects (no name attrs — use positional index or data-test on edit page)
# Index 0: Language selector (ja, zh-Hant, etc.)
# Index 1: Style category (1=Cute, 18=Gorgeous, 2=Cool, etc.)
# Index 2: Character category (10=Cats, 11=Rabbits, etc.)
STYLE_CATEGORIES = {
    "cute": "1",
    "gorgeous": "18",
    "cool": "2",
    "warm_fuzzy": "3",
    "dialects_slang": "4",
    "wacky_weird": "5",
    "humorous": "6",
    "stylish": "7",
    "reserved": "8",
    "otaku": "9",
    "sporty": "10",
    "scary": "11",
    "pop_culture": "12",
}
# CHARACTER_CATEGORIES: maps our keys → display label text.
# Used with select_option(label=...) for robustness against value changes.
# Verified against live LINE Creator Market form (Feb 2026).
CHARACTER_CATEGORIES = {
    "male": "Male Characters",
    "female": "Female Characters",
    "families_couples": "Families & Couples",
    "cats": "Cats",
    "rabbits": "Rabbits",
    "dogs": "Dogs",
    "bears": "Bears",
    "birds": "Birds",
    "pandas": "Pandas",
    "seals": "Seals",
    "other_animals": "Other",  # LINE has no "Other Animals" — capybaras go under "Other"
    "food": "Food",
    "names": "Names",
    "other": "Other",
}

# Save button + confirmation dialog
SEL_SAVE_LABEL = 'label.mdBtnLabel:has-text("Save")'
SEL_SAVE_INPUT = '[data-test="btn-save"]'
SEL_CONFIRM_OK = '.cm-modal[aria-modal="true"] [data-test="dialog-btn-ok"]'
SEL_CONFIRM_OK_FALLBACK = "button.cm-confirm-button-primary:visible"
SEL_CONFIRM_CANCEL = '[data-test="dialog-btn-cancel"]'
SEL_CAMPAIGN_POPUP_CLOSE = "button.FnCloseDialogBtn"

# ─── Management page selectors (read-only summary + tab navigation) ─────────
SEL_TAB_DISPLAY_INFO = '[data-test="tab-detail-information"]'
SEL_TAB_STICKER_IMAGES = '[data-test="tab-image"]'
SEL_TAB_TAG_SETTINGS = '[data-test="tab-tag"]'
SEL_TAB_PRICE_TIER = '[data-test="tab-price"]'
SEL_STATUS_BADGE = '[data-test="product-status"]'
SEL_REQUEST_BTN = '[data-test="detail-btn-request"]'
SEL_PREVIEW_BTN = '[data-test="preview-button"]'
SEL_CONSENT_PART = '[data-test="consent-part"]'

# ─── Image edit page selectors (/sticker/{id}/image) ────────────────────────
SEL_IMAGE_AMOUNT = '[data-test="select-image-amount"]'  # <select>: 8,16,24,32,40
SEL_IMAGE_BG_COLOR = "select:not([data-test])"  # 2nd select: MdBgGray, MdBgWhite, etc.
SEL_ZIP_UPLOAD_INPUT = 'input[name="file"]'  # visible, wraps in label.mdBtnLabel
SEL_DELETE_ALL = '[data-test="delete-all-button"]'
SEL_IMAGE_LIST_ITEM = '[data-test="product-images-list-item"]'
SEL_IMAGE_KEY = '[data-test="product-image-key"]'
SEL_IMAGE_PLACEHOLDER = '[data-test="no-product-image"]'
SEL_IMAGE_BACK = '[data-test="btn-back"]'


def sel_upload_button(key: str) -> str:
    """Per-slot Upload button. key: 'main', 'tab', '01'-'40'."""
    return f"#upload-button-{key}"


def sel_upload_file_input(key: str) -> str:
    """Per-slot hidden file input. key: 'main', 'tab', '01'-'40'."""
    return f"#upload-file-input-{key}"


def sel_delete_button(key: str) -> str:
    """Per-slot Delete button — NOT an id, use within list item context."""
    return f'[data-test="product-images-list-item"]:has([data-test="product-image-key"]:text("{key}")) [data-test="btn-delete"]'


# ─── Price tier selectors ───────────────────────────────────────────────────
SEL_PRICE_TIER = '[data-test="select-price-tier"]'  # <select>
SEL_PRICE_SAVE = '[data-test="button-save"]'  # Save button on price tab
PRICE_TIERS = {
    "7200": "10006",  # Rp7.200+
    "12000": "1",  # Rp12.000+
    "23000": "2",  # Rp23.000+
    "35000": "3",  # Rp35.000+
    "45000": "4",  # Rp45.000+
    "59000": "5",  # Rp59.000+
}

# ─── Submission defaults ─────────────────────────────────────────────────────
DEFAULTS = {
    "sticker_type": "static",
    "sticker_count": 8,
    "language": "en",
    "ai_used": True,
    "style_category": "cute",
    "character_category": "cats",
    "privacy": True,  # True = Show in LINE STORE
    "premium": True,  # True = Join
    "sale_region": "all",
    "sticker_arranging": True,
    "trial_promotions": True,
    "auto_release": True,
    "includes_photos": False,
    "copyright": "FHStudio",
    "price_tier": "23000",  # maps to select value "2" via PRICE_TIERS
}

# ─── Emoji-specific selectors (best-effort, verified at integration) ─────────
# The emoji registration form is expected to be similar to stickers but with
# differences in URL paths, slot key format, and absence of "main image".
#
# Emoji form fields — assumed same named inputs as sticker form:
SEL_EMOJI_TITLE = SEL_TITLE  # 'input[name="meta[en][title]"]'
SEL_EMOJI_DESCRIPTION = SEL_DESCRIPTION  # 'textarea[name="meta[en][description]"]'
SEL_EMOJI_COPYRIGHT = SEL_COPYRIGHT  # 'input[name="copyright"]'

# Emoji image page — emoji uses 3-digit slot keys (001-040) vs sticker 2-digit (01-40)
SEL_EMOJI_IMAGE_AMOUNT = (
    '[data-test="select-image-amount"]'  # same selector, different page
)


def sel_emoji_upload_file_input(key: str) -> str:
    """Per-slot hidden file input for emoji. key: 'tab', '001'-'040'.

    Emoji slots use 3-digit zero-padded keys (001, 002, ..., 040).
    No 'main' slot for emoji (stickers have main image, emoji do not).
    """
    return f"#upload-file-input-{key}"


def sel_emoji_upload_button(key: str) -> str:
    """Per-slot Upload button for emoji. key: 'tab', '001'-'040'."""
    return f"#upload-button-{key}"


def sel_emoji_delete_button(key: str) -> str:
    """Per-slot Delete button for emoji."""
    return (
        f'[data-test="product-images-list-item"]'
        f':has([data-test="product-image-key"]:text("{key}")) '
        f'[data-test="btn-delete"]'
    )


def emoji_slot_key(index: int) -> str:
    """Convert 0-based index to 3-digit emoji slot key: 0 → '001', 39 → '040'."""
    return f"{index + 1:03d}"


# Emoji price tiers — actual values from LINE Creator Market emoji form
# (discovered via dry-run DOM inspection, Feb 2026).
EMOJI_PRICE_TIERS = {
    "16000": "10014",  # Rp16.000+ (cheapest tier)
    "23000": "2",  # Rp23.000+
    "35000": "3",  # Rp35.000+
    "45000": "4",  # Rp45.000+
    "59000": "5",  # Rp59.000+
}

# ─── Emoji submission defaults ───────────────────────────────────────────────
EMOJI_DEFAULTS = {
    "emoji_type": "static",  # static or animated (APNG)
    "emoji_count": 40,  # target count (8, 16, 24, 32, or 40)
    "language": "en",
    "ai_used": True,
    "style_category": "cute",
    "character_category": "other_animals",  # hamster → Other
    "privacy": True,  # Show in LINE STORE
    "sale_region": "all",
    "auto_release": True,
    "copyright": "FHStudio",
    "price_tier": "16000",  # Rp16.000+ — cheapest available tier
}

# ─── Storage paths ───────────────────────────────────────────────────────────
SESSION_STATE_DIR = Path.home() / ".line-sticker-automation"
SESSION_STATE_PATH = SESSION_STATE_DIR / "storage_state.json"
PROGRESS_STATE_PATH = SESSION_STATE_DIR / "progress.json"
EMOJI_PROGRESS_STATE_PATH = SESSION_STATE_DIR / "emoji_progress.json"
SCREENSHOT_DIR = REPO_ROOT / "automation" / "screenshots"
