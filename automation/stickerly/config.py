"""
Configuration constants for Sticker.ly Android emulator automation.

Package names, UI selectors, timeouts, storage paths, and tag templates.

UI selectors use uiautomator2 syntax:
  - resourceId: "com.snowcorp.stickerly.android:id/xxx"
  - text: Exact text match
  - description: Content description (accessibility)
  - className: Android view class name
  - xpath: XPath for complex selectors

NOTE: Selectors are initial best-guesses based on typical Android app patterns.
      They will need to be verified and updated during the first interactive run
      using `uiautomator2`'s device inspector or `adb shell uiautomator dump`.
      Run: `python -m uiautomator2 init && python -m uiautomator2 weditor`
"""

from pathlib import Path

# -- Repo root -----------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# -- Android package ------------------------------------------------------------
STICKERLY_PACKAGE = "com.snowcorp.stickerly.android"
STICKERLY_MAIN_ACTIVITY = (
    "com.snowcorp.stickerly.android.ui.splash.SplashScreenActivity"
)

# -- Emulator -------------------------------------------------------------------
DEFAULT_AVD_NAME = "Medium_Phone_API_36.1"
SNAPSHOT_NAME = "stickerly-logged-in"
EMULATOR_BOOT_TIMEOUT = 120  # seconds to wait for emulator boot
ADB_DEVICE_TIMEOUT = 30  # seconds to wait for adb to find device

# -- Remote paths on emulator ---------------------------------------------------
REMOTE_STICKER_DIR = "/sdcard/Download/stickerly_upload"
REMOTE_SCREENSHOT_DIR = "/sdcard/Pictures/stickerly_screenshots"

# -- Timeouts (seconds) --------------------------------------------------------
APP_LAUNCH_TIMEOUT = 15
ELEMENT_WAIT_TIMEOUT = 10
STICKER_ADD_TIMEOUT = 15  # per sticker (includes file picker navigation)
PUBLISH_TIMEOUT = 30
LOGIN_TIMEOUT = 300  # 5 min for manual Google login

# -- UI selectors (uiautomator2 format) ----------------------------------------
# These are initial patterns; update after first interactive inspection.

# Home / navigation
SEL_CREATE_BUTTON = {
    "description": "Create button on bottom nav or FAB",
    "selectors": [
        {"text": "Create"},
        {"description": "Create"},
        {"resourceIdMatches": ".*create.*|.*fab.*|.*add.*"},
    ],
}

SEL_WHATSAPP_STICKER_TYPE = {
    "description": "WhatsApp Stickers option in creation menu",
    "selectors": [
        {"text": "WhatsApp Stickers"},
        {"textContains": "WhatsApp"},
        {"textContains": "Sticker Pack"},
    ],
}

# Pack editor
SEL_ADD_STICKER = {
    "description": "Add sticker button in pack editor",
    "selectors": [
        {"text": "Add Sticker"},
        {"textContains": "Add"},
        {"description": "Add Sticker"},
        {"resourceIdMatches": ".*add.*sticker.*"},
    ],
}

SEL_TRAY_ICON = {
    "description": "Tray icon area in pack editor",
    "selectors": [
        {"description": "Tray icon"},
        {"descriptionContains": "tray"},
        {"resourceIdMatches": ".*tray.*icon.*"},
    ],
}

# Image editor / crop screen
SEL_CROP_DONE = {
    "description": "Done/Save button on crop/edit screen",
    "selectors": [
        {"text": "Done"},
        {"text": "Save"},
        {"text": "OK"},
        {"description": "Done"},
        {"resourceIdMatches": ".*done.*|.*save.*|.*confirm.*"},
    ],
}

SEL_CROP_NEXT = {
    "description": "Next button on crop/edit screen",
    "selectors": [
        {"text": "Next"},
        {"text": "NEXT"},
        {"description": "Next"},
    ],
}

# File picker
SEL_FILE_PICKER_MENU = {
    "description": "Hamburger menu or navigation in file picker",
    "selectors": [
        {"description": "Show roots"},
        {"description": "Show navigation"},
        {"className": "android.widget.ImageButton", "index": 0},
    ],
}

SEL_FILE_PICKER_DOWNLOADS = {
    "description": "Downloads folder in file picker sidebar",
    "selectors": [
        {"text": "Downloads"},
        {"textContains": "Download"},
    ],
}

SEL_FILE_PICKER_STICKERLY_DIR = {
    "description": "stickerly_upload directory in file picker",
    "selectors": [
        {"text": "stickerly_upload"},
    ],
}

# Metadata fields
SEL_PACK_NAME_INPUT = {
    "description": "Pack name input field",
    "selectors": [
        {"resourceIdMatches": ".*pack.*name.*|.*title.*"},
        {"className": "android.widget.EditText", "index": 0},
    ],
}

SEL_AUTHOR_INPUT = {
    "description": "Author/Creator name input field",
    "selectors": [
        {"resourceIdMatches": ".*author.*|.*creator.*"},
        {"className": "android.widget.EditText", "index": 1},
    ],
}

SEL_TAG_INPUT = {
    "description": "Tag input field",
    "selectors": [
        {"resourceIdMatches": ".*tag.*"},
        {"textContains": "Add tag"},
    ],
}

# Publish
SEL_PUBLISH_BUTTON = {
    "description": "Publish / Save and Publish button",
    "selectors": [
        {"text": "Publish"},
        {"textContains": "Publish"},
        {"text": "Save & Publish"},
        {"textContains": "Save"},
    ],
}

SEL_PUBLISH_CONFIRM = {
    "description": "Confirmation dialog OK button after publish",
    "selectors": [
        {"text": "OK"},
        {"text": "Yes"},
        {"text": "Confirm"},
        {"resourceIdMatches": ".*ok.*|.*confirm.*|.*positive.*"},
    ],
}

# Login detection
SEL_LOGIN_SCREEN = {
    "description": "Elements that indicate login/onboarding screen",
    "selectors": [
        {"text": "Sign in"},
        {"text": "Log in"},
        {"text": "Continue with Google"},
        {"textContains": "Sign"},
        {"textContains": "Log in"},
    ],
}

SEL_HOME_SCREEN = {
    "description": "Elements that indicate authenticated home screen",
    "selectors": [
        {"text": "Home"},
        {"text": "My Stickers"},
        {"text": "Trending"},
        {"resourceIdMatches": ".*bottom.*nav.*|.*home.*"},
    ],
}

# -- Default metadata -----------------------------------------------------------
DEFAULTS = {
    "publisher": "BobaStickers",
    "tags_base": [
        "kawaii",
        "cute",
        "stickers",
        "whatsapp stickers",
        "emoji",
        "reaction",
        "daily",
        "expression",
        "chibi",
        "funny",
    ],
}

# -- Tag templates (merged with pack-specific keywords) -------------------------
TAG_TEMPLATES = {
    "cat": ["cat", "kitten", "neko", "cute cat", "kawaii cat", "anime cat"],
    "panda": ["panda", "bear", "bamboo", "cute panda", "kawaii panda"],
    "capybara": ["capybara", "capy", "chill", "cute capybara", "animal"],
    "hamster": ["hamster", "hammy", "cute hamster", "kawaii hamster", "rodent"],
    "otter": ["otter", "cute otter", "sea otter", "river otter"],
    "default": ["animal", "character", "cute animal"],
}

# -- Storage paths --------------------------------------------------------------
SESSION_STATE_DIR = Path.home() / ".stickerly-automation"
PROGRESS_STATE_PATH = SESSION_STATE_DIR / "progress.json"
SESSION_MARKER_PATH = SESSION_STATE_DIR / "session.json"
PUBLISHED_PACKS_PATH = SESSION_STATE_DIR / "published_packs.json"
SCREENSHOT_DIR = REPO_ROOT / "automation" / "stickerly" / "screenshots"
