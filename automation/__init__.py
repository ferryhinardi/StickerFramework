"""
LINE Creator Market automation via Playwright.

Modules:
    config      — URLs, selectors, timeouts, submission defaults
    utils       — Shared helpers (safe_click, retry, screenshot)
    line_auth   — Login and session management
    line_create_submission — Create new sticker submission (fills all display info)
    line_upload_images     — Image edit page automation (per-slot upload)
    line_set_metadata      — Tag Settings tab automation
    line_set_price         — Price Tier tab automation
    line_submit            — Final review and submission (consent + Request)
"""

from automation.config import (
    BASE_URL,
    CREATE_URL,
    DEFAULTS,
    LOGIN_AUTH_URL,
    MY_STICKERS_URL,
    PAGE_LOAD_TIMEOUT,
    SCREENSHOT_DIR,
    SELECTOR_TIMEOUT,
)
from automation.line_auth import LineAuth
from automation.line_create_submission import LineCreateSubmission
from automation.line_set_metadata import LineSetMetadata
from automation.line_set_price import LinePriceTier
from automation.line_submit import LineSubmit
from automation.line_upload_images import LineStickerUpload

__all__ = [
    "LineAuth",
    "LineCreateSubmission",
    "LineStickerUpload",
    "LineSetMetadata",
    "LinePriceTier",
    "LineSubmit",
]
