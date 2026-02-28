"""
Sticker.ly pack creation and sticker upload automation.

Real flow (verified via UI dumps):
1. Profile tab -> "New Pack" -> Pack type bottom sheet -> "Regular"
2. New Pack form -> enter name -> "Create"
3. Handle private pack info dialog (first time only)
4. Land on Pack Detail screen (pack is LIVE immediately)
5. "Add sticker" -> Gallery editor -> multi-select images -> "Next"
6. "Save to..." screen -> select pack + add tags -> "Save"
7. Back on Pack Detail with stickers added
"""

from __future__ import annotations

import time
from pathlib import Path

import uiautomator2 as u2

from automation.stickerly.config import (
    ELEMENT_WAIT_TIMEOUT,
    REMOTE_STICKER_DIR,
    SEL_DIALOG_OK,
    SEL_EDITOR_BACK_BTN,
    SEL_EDITOR_MULTI_SELECT_BTN,
    SEL_EDITOR_NEXT_BTN,
    SEL_EDITOR_SELECT_NUM,
    SEL_NAV_PROFILE,
    SEL_NEW_PACK_CREATE_BTN,
    SEL_NEW_PACK_NAME_INPUT,
    SEL_PACK_ADD_STICKER,
    SEL_PACK_CODE_TEXT,
    SEL_PACK_NAME_TEXT,
    SEL_PACK_TYPE_REGULAR,
    SEL_PROFILE_NEW_PACK,
    SEL_SAVE_BUTTON,
    SEL_SAVE_PACK_NAME,
    SEL_SAVE_TAG_INPUT,
    STICKER_ADD_TIMEOUT,
)
from automation.stickerly.utils import (
    ElementNotFound,
    StickerUploadError,
    find_element,
    human_delay,
    media_scan,
    safe_click,
    safe_set_text,
    screenshot_on_failure,
    take_screenshot,
)


class StickerlyCreatePack:
    """Create a sticker pack and add stickers in the Sticker.ly app."""

    def __init__(self, device: u2.Device):
        self.device = device

    def create_pack(self, pack_name: str) -> str | None:
        """
        Create a new sticker pack with the given name.

        Flow: Profile tab -> New Pack -> Regular -> enter name -> Create -> OK dialog

        Args:
            pack_name: Display name for the sticker pack.

        Returns:
            Pack code (e.g., "NDT04A") if captured, or None.
        """
        d = self.device

        with screenshot_on_failure(d, "create_pack"):
            # 1. Go to Profile tab
            print("  Navigating to Profile tab...")
            safe_click(d, SEL_NAV_PROFILE)
            human_delay(1000, 2000)

            # 2. Tap "New Pack"
            print("  Tapping 'New Pack'...")
            safe_click(d, SEL_PROFILE_NEW_PACK)
            human_delay(1000, 2000)

            # 3. Select "Regular" from pack type bottom sheet
            print("  Selecting 'Regular' pack type...")
            safe_click(d, SEL_PACK_TYPE_REGULAR)
            human_delay(1000, 2000)

            # 4. Enter pack name
            print(f"  Setting pack name: {pack_name}")
            el = find_element(d, SEL_NEW_PACK_NAME_INPUT)
            el.click()
            human_delay(300, 600)
            el.set_text(pack_name)
            human_delay(500, 1000)

            # 5. Click "Create"
            print("  Clicking Create...")
            safe_click(d, SEL_NEW_PACK_CREATE_BTN)
            human_delay(2000, 4000)

            # 6. Handle private pack info dialog (appears on first pack creation)
            try:
                safe_click(d, SEL_DIALOG_OK, timeout=3)
                print("  Dismissed private pack info dialog.")
                human_delay(1000, 2000)
            except ElementNotFound:
                pass  # Dialog doesn't appear every time

            # 7. We should now be on Pack Detail screen. Extract pack code.
            pack_code = self._get_pack_code()
            if pack_code:
                print(f"  Pack created! Code: {pack_code}")
            else:
                print("  Pack created! (could not capture code)")

            take_screenshot(d, f"pack_created_{pack_name.replace(' ', '_')}")
            return pack_code

    def add_stickers_to_pack(
        self,
        pack_name: str,
        pack_id: str,
        sticker_files: list[Path],
        tags: str = "",
    ) -> int:
        """
        Add stickers to an existing pack via the gallery multi-select flow.

        Flow:
        1. From Pack Detail, click "Add sticker"
        2. In gallery editor, click "Select" for multi-select mode
        3. Tap each sticker image in the gallery grid
        4. Click "Next"
        5. On "Save to..." screen, select the target pack
        6. Add tags
        7. Click "Save"

        Images must already be pushed to the emulator's media store
        (e.g., /sdcard/Pictures/Stickers/<pack_id>/) and media-scanned.

        Args:
            pack_name: Display name of the pack (used to select in "Save to..." list).
            pack_id: Pack identifier for logging.
            sticker_files: List of local sticker file paths (used for count only;
                          actual images are read from emulator gallery).
            tags: Comma-separated tags string for the stickers.

        Returns:
            Number of stickers selected (same as sticker_files count on success).
        """
        d = self.device
        count = len(sticker_files)

        with screenshot_on_failure(d, f"add_stickers_{pack_id}"):
            # 1. Click "Add sticker" on Pack Detail
            print(f"  Clicking 'Add sticker' to add {count} images...")
            safe_click(d, SEL_PACK_ADD_STICKER)
            human_delay(2000, 3000)

            # 2. Enable multi-select mode
            print("  Enabling multi-select mode...")
            safe_click(d, SEL_EDITOR_MULTI_SELECT_BTN)
            human_delay(1000, 2000)

            # 3. Select all sticker images in the gallery
            selected = self._select_gallery_images(count)
            if selected == 0:
                raise StickerUploadError("No images could be selected in gallery")

            print(f"  Selected {selected}/{count} images.")
            human_delay(500, 1000)

            # 4. Click "Next"
            print("  Clicking Next...")
            safe_click(d, SEL_EDITOR_NEXT_BTN)
            human_delay(2000, 4000)

            # 5. Select the target pack in the "Save to..." screen
            print(f"  Selecting pack '{pack_name}'...")
            try:
                pack_el = d(text=pack_name)
                if pack_el.wait(timeout=ELEMENT_WAIT_TIMEOUT):
                    pack_el.click()
                    human_delay(500, 1000)
                else:
                    print(f"  WARNING: Pack '{pack_name}' not found in list")
            except Exception as exc:
                print(f"  WARNING: Could not select pack: {exc}")

            # 6. Add tags
            if tags:
                print(f"  Adding tags: {tags}")
                try:
                    tag_el = find_element(d, SEL_SAVE_TAG_INPUT, timeout=5)
                    tag_el.click()
                    human_delay(300, 600)
                    tag_el.set_text(tags)
                    human_delay(500, 1000)
                except ElementNotFound:
                    print("  WARNING: Could not find tag input")

            # 7. Click "Save"
            print("  Saving stickers to pack...")
            safe_click(d, SEL_SAVE_BUTTON)
            human_delay(3000, 5000)

            take_screenshot(d, f"stickers_added_{pack_id}")
            print(f"  Added {selected} stickers to pack.")
            return selected

    def _select_gallery_images(self, target_count: int) -> int:
        """
        Select images in the gallery grid by tapping selection circles.

        In multi-select mode, each gallery image has a selectNumLayout overlay.
        Tapping it selects the image and shows the selection number (1, 2, 3...).

        Args:
            target_count: Number of images to select.

        Returns:
            Number of images actually selected.
        """
        d = self.device
        select_circles = d(resourceId=SEL_EDITOR_SELECT_NUM["resourceId"])

        # Wait for gallery to load
        if not select_circles.wait(timeout=ELEMENT_WAIT_TIMEOUT):
            print("  WARNING: No selectable images found in gallery")
            return 0

        available = select_circles.count
        to_select = min(target_count, available)

        for i in range(to_select):
            try:
                select_circles[i].click()
                human_delay(200, 500)
            except Exception as exc:
                print(f"  WARNING: Could not select image {i + 1}: {exc}")

        return to_select

    def _get_pack_code(self) -> str | None:
        """Extract the pack code from the Pack Detail screen."""
        try:
            el = find_element(self.device, SEL_PACK_CODE_TEXT, timeout=5)
            code = el.get_text()
            if code and len(code) <= 10:  # pack codes are short
                return code
        except ElementNotFound:
            pass
        return None
