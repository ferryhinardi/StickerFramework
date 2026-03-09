"""
LINE Creator Market automation via Playwright.

Modules:
    config      — URLs, selectors, timeouts, submission defaults
    utils       — Shared helpers (safe_click, retry, screenshot)
    line_auth   — Login and session management

  Sticker modules:
    line_create_submission — Create new sticker submission (fills all display info)
    line_upload_images     — Image edit page automation (per-slot upload)
    line_animated_upload   — Animated sticker (APNG) image upload (8/16/24 slots)
    line_set_metadata      — Tag Settings tab automation
    line_set_price         — Price Tier tab automation
    line_submit            — Final review and submission (consent + Request)

  Emoji modules:
    line_emoji_create        — Create new emoji submission
    line_emoji_upload        — Emoji image upload (3-digit slot keys)
    line_emoji_price_submit  — Emoji price tier + final submission
"""

from automation.config import (
    ANIMATED_DEFAULTS,
    ANIMATED_VALID_COUNTS,
    BASE_URL,
    CREATE_URL,
    DEFAULTS,
    EMOJI_CREATE_URL,
    EMOJI_DEFAULTS,
    LOGIN_AUTH_URL,
    MY_EMOJI_URL,
    MY_STICKERS_URL,
    PAGE_LOAD_TIMEOUT,
    SCREENSHOT_DIR,
    SELECTOR_TIMEOUT,
)
from automation.line_animated_upload import LineAnimatedUpload
from automation.line_auth import LineAuth
from automation.line_create_submission import LineCreateSubmission
from automation.line_emoji_create import LineEmojiCreate
from automation.line_emoji_price_submit import LineEmojiPrice, LineEmojiSubmit
from automation.line_emoji_upload import LineEmojiUpload
from automation.line_set_metadata import LineSetMetadata
from automation.line_set_price import LinePriceTier
from automation.line_submit import LineSubmit
from automation.line_upload_images import LineStickerUpload

__all__ = [
    # Auth
    "LineAuth",
    # Sticker (static)
    "LineCreateSubmission",
    "LineStickerUpload",
    "LineSetMetadata",
    "LinePriceTier",
    "LineSubmit",
    # Sticker (animated)
    "LineAnimatedUpload",
    # Emoji
    "LineEmojiCreate",
    "LineEmojiUpload",
    "LineEmojiPrice",
    "LineEmojiSubmit",
]
