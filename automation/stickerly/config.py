"""
Configuration constants for Sticker.ly Android emulator automation.

Package names, UI selectors, timeouts, storage paths, and tag templates.

UI selectors use uiautomator2 syntax:
  - resourceId: "com.snowcorp.stickerly.android:id/xxx"
  - text: Exact text match
  - description: Content description (accessibility)
  - className: Android view class name

All selectors verified via live UI dumps on Sticker.ly v3.x (Feb 2026).
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
EMULATOR_DNS = "8.8.8.8"  # required: default DNS doesn't resolve

# -- Remote paths on emulator ---------------------------------------------------
REMOTE_STICKER_DIR = "/sdcard/Pictures/Stickers"
REMOTE_SCREENSHOT_DIR = "/sdcard/Pictures/stickerly_screenshots"

# -- Timeouts (seconds) --------------------------------------------------------
APP_LAUNCH_TIMEOUT = 15
ELEMENT_WAIT_TIMEOUT = 10
STICKER_ADD_TIMEOUT = 15  # per sticker (includes file picker navigation)
PUBLISH_TIMEOUT = 30
LOGIN_TIMEOUT = 300  # 5 min for manual Google login

# ==============================================================================
# UI SELECTORS (verified via live UI dumps)
# ==============================================================================
PKG = "com.snowcorp.stickerly.android"

# -- Bottom navigation bar ------------------------------------------------------
SEL_NAV_HOME = {"resourceId": f"{PKG}:id/homeIconClickArea"}
SEL_NAV_SEARCH = {"resourceId": f"{PKG}:id/searchIconClickArea"}
SEL_NAV_CREATE = {"resourceId": f"{PKG}:id/addImageIconClickArea"}
SEL_NAV_FONTS = {"resourceId": f"{PKG}:id/unicodeIconClickArea"}
SEL_NAV_PROFILE = {"resourceId": f"{PKG}:id/myIconClickArea"}

# -- Profile tab ----------------------------------------------------------------
SEL_PROFILE_USERNAME = {"resourceId": f"{PKG}:id/userName"}
SEL_PROFILE_DISPLAY_NAME = {"resourceId": f"{PKG}:id/displayName"}
SEL_PROFILE_EDIT_BTN = {"resourceId": f"{PKG}:id/editProfileBtn"}
SEL_PROFILE_NEW_PACK = {"text": "New Pack"}
SEL_PROFILE_FOLLOWER_COUNT = {"resourceId": f"{PKG}:id/followerCount"}
SEL_PROFILE_FOLLOWING_COUNT = {"resourceId": f"{PKG}:id/followingCount"}

# -- Pack type selection bottom sheet (after clicking New Pack) -----------------
SEL_PACK_TYPE_TITLE = {"resourceId": f"{PKG}:id/packTypeTitle"}
SEL_PACK_TYPE_REGULAR = {"resourceId": f"{PKG}:id/regularText"}
SEL_PACK_TYPE_ANIMATED = {"resourceId": f"{PKG}:id/animatedText"}
SEL_PACK_TYPE_TEMPLATES = {"resourceId": f"{PKG}:id/templateText"}
SEL_PACK_TYPE_CANCEL = {"resourceId": f"{PKG}:id/cancelBtn"}

# -- New pack form (after choosing Regular) ------------------------------------
SEL_NEW_PACK_NAME_LABEL = {"resourceId": f"{PKG}:id/label_text"}
SEL_NEW_PACK_NAME_INPUT = {"resourceId": f"{PKG}:id/edit_text"}
SEL_NEW_PACK_PRIVATE_SWITCH = {"resourceId": f"{PKG}:id/private_switch"}
SEL_NEW_PACK_CREATE_BTN = {"resourceId": f"{PKG}:id/saveButton"}

# -- Private pack info dialog (appears after first pack creation) ---------------
SEL_DIALOG_OK = {"resourceId": "android:id/button1"}
SEL_DIALOG_MESSAGE = {"resourceId": "android:id/message"}

# -- Pack detail screen ---------------------------------------------------------
SEL_PACK_NAME_TEXT = {"resourceId": f"{PKG}:id/packNameText"}
SEL_PACK_CODE_TEXT = {"resourceId": f"{PKG}:id/packCodeText"}
SEL_PACK_CODE_COPY = {"resourceId": f"{PKG}:id/packCodeCopy"}
SEL_PACK_VIEWS = {"resourceId": f"{PKG}:id/viewsText"}
SEL_PACK_DOWNLOADS = {"resourceId": f"{PKG}:id/downloadedCountText"}
SEL_PACK_ADD_STICKER = {"text": "Add sticker"}
SEL_PACK_EXPORT_BTN = {"resourceId": f"{PKG}:id/exportBtn"}
SEL_PACK_WHATSAPP_TEXT = {"resourceId": f"{PKG}:id/whatsappText"}
SEL_PACK_REWARD_AD = {"resourceId": f"{PKG}:id/rewardAdText"}
SEL_PACK_SHARE_IMAGE = {"resourceId": f"{PKG}:id/shareImage"}
SEL_PACK_LAST_UPDATE = {"resourceId": f"{PKG}:id/lastUpdateInfo"}
# Overflow menu (3-dot) is an unnamed ImageView at ~[980,92][1054,181]
SEL_PACK_OVERFLOW_COORDS = (1017, 137)

# -- Pack overflow menu ---------------------------------------------------------
SEL_OVERFLOW_EDIT_ORDER = {"resourceId": f"{PKG}:id/reorder_pack"}
SEL_OVERFLOW_EDIT_PACK = {"resourceId": f"{PKG}:id/edit_pack"}
SEL_OVERFLOW_PRIVATE = {"resourceId": f"{PKG}:id/private_option"}
SEL_OVERFLOW_DELETE = {"resourceId": f"{PKG}:id/delete_pack"}

# -- Edit pack screen -----------------------------------------------------------
SEL_EDIT_PACK_NAME_INPUT = {"resourceId": f"{PKG}:id/edit_text"}
SEL_EDIT_PACK_PRIVATE_SWITCH = {"resourceId": f"{PKG}:id/private_switch"}
SEL_EDIT_PACK_DONE = {"text": "Done"}

# -- Delete confirmation dialog -------------------------------------------------
SEL_DELETE_TITLE = {"resourceId": f"{PKG}:id/alertTitle"}
SEL_DELETE_CANCEL = {"resourceId": "android:id/button2"}  # "CANCEL"
SEL_DELETE_CONFIRM = {"resourceId": "android:id/button1"}  # "DELETE"

# -- Sticker editor / gallery (after clicking "Add sticker") -------------------
SEL_EDITOR_GALLERY_LIST = {"resourceId": f"{PKG}:id/gallery_list"}
SEL_EDITOR_MULTI_SELECT_BTN = {"resourceId": f"{PKG}:id/multi_select_btn"}
SEL_EDITOR_MULTI_SELECT_TEXT = {"resourceId": f"{PKG}:id/multi_select_text"}
SEL_EDITOR_SELECT_NUM = {"resourceId": f"{PKG}:id/selectNumLayout"}
SEL_EDITOR_NEXT_BTN = {"resourceId": f"{PKG}:id/nextBtn"}
SEL_EDITOR_BACK_BTN = {"resourceId": f"{PKG}:id/backBtn"}
SEL_EDITOR_ALBUM_TITLE = {"text": "All Photos"}
SEL_EDITOR_AI_CUT = {"resourceId": f"{PKG}:id/autocutMotionLayout"}
SEL_EDITOR_CANVAS = {"resourceId": f"{PKG}:id/canvasView"}
SEL_EDITOR_TEMPLATES_BTN = {"resourceId": f"{PKG}:id/templateBtn"}
SEL_EDITOR_TAB_LIBRARY = {"description": "Library"}
SEL_EDITOR_TAB_GIF = {"description": "GIF"}

# Editor tool buttons
SEL_EDITOR_ADD_ICON = {"resourceId": f"{PKG}:id/galleryIcon"}
SEL_EDITOR_TEXT_ICON = {"resourceId": f"{PKG}:id/textIcon"}
SEL_EDITOR_EMOJI_ICON = {"resourceId": f"{PKG}:id/emojiIcon"}
SEL_EDITOR_STICKER_ICON = {"resourceId": f"{PKG}:id/stickerIcon"}
SEL_EDITOR_GIPHY_ICON = {"resourceId": f"{PKG}:id/giphyIcon"}
SEL_EDITOR_BG_ICON = {"resourceId": f"{PKG}:id/backgroundIcon"}

# -- "Save to..." screen (after selecting images and clicking Next) -------------
SEL_SAVE_STICKER_COUNT = {"resourceId": f"{PKG}:id/stickerCountText"}
SEL_SAVE_TITLE = {"resourceId": f"{PKG}:id/saveTitleText"}  # "Save to..."
SEL_SAVE_PACK_LIST = {"resourceId": f"{PKG}:id/packListView"}
SEL_SAVE_PACK_NAME = {"resourceId": f"{PKG}:id/packNameText"}  # in list items
SEL_SAVE_PACK_CHECK = {"resourceId": f"{PKG}:id/checkBtn"}
SEL_SAVE_TAG_INPUT = {"resourceId": f"{PKG}:id/tagText"}  # "Add Tags" EditText
SEL_SAVE_BUTTON = {"resourceId": f"{PKG}:id/saveButton"}  # "Save"

# -- Share bottom sheet (from pack detail share button) -------------------------
SEL_SHARE_BOTTOM_SHEET = {"resourceId": f"{PKG}:id/bottomSheetView"}
SEL_SHARE_TOUCH_OUTSIDE = {"resourceId": f"{PKG}:id/touch_outside"}
SEL_SHARE_ADD_TO_TITLE = {"resourceId": f"{PKG}:id/addToTitleText"}
SEL_SHARE_WHATSAPP_BTN = {"resourceId": f"{PKG}:id/whatsappTextBg"}
SEL_SHARE_COPY_CODE = {"text": "Copy code"}
SEL_SHARE_COPY_LINK = {"text": "Copy link"}
SEL_SHARE_MORE = {"text": "More"}

# -- Permission dialog (first time gallery access) -----------------------------
SEL_PERMISSION_ALLOW_ALL = {
    "resourceId": "com.android.permissioncontroller:id/permission_allow_all_button"
}
SEL_PERMISSION_DENY = {
    "resourceId": "com.android.permissioncontroller:id/permission_deny_button"
}

# -- Login/home detection -------------------------------------------------------
SEL_LOGIN_GOOGLE = {"text": "Continue with Google"}
SEL_HOME_INDICATOR = {"resourceId": f"{PKG}:id/homeIconClickArea"}

# ==============================================================================
# APP FLOW SUMMARY (verified)
# ==============================================================================
# 1. Profile tab -> "New Pack" -> Pack Type bottom sheet -> "Regular"
# 2. New Pack Form -> enter name -> "Create" -> (Private Pack info dialog -> OK)
# 3. Pack Detail screen (pack is LIVE immediately with a pack code)
# 4. "Add sticker" -> Editor/Gallery -> "Select" (multi-select) -> tap images
#    -> "Next" -> "Save to..." screen -> pick pack + add tags -> "Save"
# 5. Back on Pack Detail -> share button -> bottom sheet with Copy link/code
# 6. Share link format: https://sticker.ly/s/{PACK_CODE}
# 7. No separate "publish" step - packs are public by default on creation.
# 8. Edit pack: overflow menu (3-dot) -> "Edit pack" -> change name/private -> Done
# 9. Delete: overflow menu -> "Delete pack" -> confirmation dialog -> DELETE

# ==============================================================================
# CONFIGURATION
# ==============================================================================

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
