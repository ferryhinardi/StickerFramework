"""
Sticker.ly pack creation and sticker upload automation.

Handles creating a new WhatsApp sticker pack and adding individual stickers
through the Sticker.ly mobile app UI via uiautomator2.
"""

from __future__ import annotations

import time
from pathlib import Path

import uiautomator2 as u2

from automation.stickerly.config import (
    ELEMENT_WAIT_TIMEOUT,
    REMOTE_STICKER_DIR,
    SEL_ADD_STICKER,
    SEL_CREATE_BUTTON,
    SEL_CROP_DONE,
    SEL_CROP_NEXT,
    SEL_FILE_PICKER_DOWNLOADS,
    SEL_FILE_PICKER_MENU,
    SEL_FILE_PICKER_STICKERLY_DIR,
    SEL_TRAY_ICON,
    SEL_WHATSAPP_STICKER_TYPE,
    STICKER_ADD_TIMEOUT,
)
from automation.stickerly.utils import (
    ElementNotFound,
    StickerUploadError,
    find_element,
    human_delay,
    safe_click,
    screenshot_on_failure,
)


class StickerlyCreatePack:
    """Create a sticker pack and add stickers in the Sticker.ly app."""

    def __init__(self, device: u2.Device):
        self.device = device

    def create_new_pack(self) -> None:
        """
        Navigate to create a new WhatsApp sticker pack.

        Taps the Create button on the bottom nav, then selects
        'WhatsApp Stickers' as the pack type.
        """
        print("  Creating new sticker pack...")

        with screenshot_on_failure(self.device, "create_new_pack"):
            # Tap Create / + button
            safe_click(self.device, SEL_CREATE_BUTTON)
            human_delay(1000, 2000)

            # Select WhatsApp Stickers type
            safe_click(self.device, SEL_WHATSAPP_STICKER_TYPE)
            human_delay(1000, 2000)

        print("  New pack creation started.")

    def add_sticker(
        self,
        device: u2.Device,
        remote_file_path: str,
        sticker_name: str,
        index: int,
    ) -> None:
        """
        Add a single sticker to the current pack via the file picker.

        Args:
            device: uiautomator2 Device instance.
            remote_file_path: Full path to the WEBP file on the emulator.
            sticker_name: Human-readable name for logging.
            index: Sticker index (1-based) for logging.
        """
        with screenshot_on_failure(device, f"add_sticker_{index:02d}"):
            print(f"    [{index}] Adding: {sticker_name}")

            # Tap "Add Sticker"
            safe_click(device, SEL_ADD_STICKER)
            human_delay(1000, 2000)

            # Navigate file picker to select the sticker file
            self._select_file_in_picker(device, remote_file_path)
            human_delay(1000, 2000)

            # Confirm / Done on the crop/editor screen
            self._confirm_sticker_edit(device)
            human_delay(500, 1500)

            print(f"    [{index}] Added: {sticker_name}")

    def add_all_stickers(
        self,
        device: u2.Device,
        pack_id: str,
        sticker_files: list[Path],
    ) -> int:
        """
        Add all stickers from the file list to the current pack.

        Args:
            device: uiautomator2 Device instance.
            pack_id: Pack identifier (matches remote directory name).
            sticker_files: Sorted list of local .webp sticker file paths
                          (excluding tray_icon.webp).

        Returns:
            Number of stickers successfully added.
        """
        remote_dir = f"{REMOTE_STICKER_DIR}/{pack_id}"
        added = 0

        print(f"  Adding {len(sticker_files)} stickers...")
        for i, local_file in enumerate(sticker_files, 1):
            remote_path = f"{remote_dir}/{local_file.name}"
            try:
                self.add_sticker(device, remote_path, local_file.stem, i)
                added += 1
            except (ElementNotFound, StickerUploadError) as exc:
                print(f"    [{i}] FAILED: {exc}")
                # Continue with remaining stickers
                continue

        print(f"  Added {added}/{len(sticker_files)} stickers.")
        return added

    def set_tray_icon(self, device: u2.Device, pack_id: str) -> None:
        """
        Set the pack tray icon from the pushed files.

        Args:
            device: uiautomator2 Device instance.
            pack_id: Pack identifier.
        """
        remote_tray = f"{REMOTE_STICKER_DIR}/{pack_id}/tray_icon.webp"

        with screenshot_on_failure(device, "set_tray_icon"):
            print("  Setting tray icon...")

            # Tap tray icon area
            safe_click(device, SEL_TRAY_ICON)
            human_delay(1000, 2000)

            # Select tray icon file
            self._select_file_in_picker(device, remote_tray)
            human_delay(1000, 2000)

            # Confirm
            self._confirm_sticker_edit(device)
            human_delay(500, 1000)

            print("  Tray icon set.")

    # -- File picker navigation -------------------------------------------------

    def _select_file_in_picker(self, device: u2.Device, remote_path: str) -> None:
        """
        Navigate the Android file picker to select a specific file.

        Strategy:
        1. Open the hamburger menu / navigation drawer.
        2. Select "Downloads" from the sidebar.
        3. Navigate to the stickerly_upload subdirectory.
        4. Tap the target file by name.

        If the standard file picker flow fails, falls back to using
        ADB intent to directly open the file.
        """
        filename = remote_path.rsplit("/", 1)[-1]
        pack_dir = remote_path.rsplit("/", 2)[-2] if "/" in remote_path else ""

        try:
            # Try to navigate to Downloads > stickerly_upload > pack_dir
            # Open sidebar/navigation
            try:
                safe_click(device, SEL_FILE_PICKER_MENU, timeout=3)
                human_delay(500, 1000)
            except ElementNotFound:
                pass  # Menu may already be open or not needed

            # Tap Downloads
            try:
                safe_click(device, SEL_FILE_PICKER_DOWNLOADS, timeout=3)
                human_delay(500, 1000)
            except ElementNotFound:
                # May already be in Downloads
                pass

            # Navigate to stickerly_upload directory
            try:
                safe_click(device, SEL_FILE_PICKER_STICKERLY_DIR, timeout=3)
                human_delay(500, 1000)
            except ElementNotFound:
                pass

            # Navigate to pack subdirectory if present
            if pack_dir:
                try:
                    el = device(text=pack_dir)
                    if el.wait(timeout=3):
                        el.click()
                        human_delay(500, 1000)
                except Exception:
                    pass

            # Select the target file
            el = device(text=filename)
            if not el.wait(timeout=ELEMENT_WAIT_TIMEOUT):
                # Try partial match
                el = device(textContains=filename.replace(".webp", ""))
                if not el.wait(timeout=3):
                    raise ElementNotFound(f"File '{filename}' not found in file picker")
            el.click()

        except ElementNotFound:
            # Fallback: try scrolling to find the file
            device(scrollable=True).scroll.to(text=filename)
            el = device(text=filename)
            if el.wait(timeout=3):
                el.click()
            else:
                raise ElementNotFound(
                    f"Cannot find file '{filename}' in file picker after scroll"
                )

    def _confirm_sticker_edit(self, device: u2.Device) -> None:
        """Confirm/save on the sticker edit/crop screen."""
        # Try "Done" first, then "Next", then "Save"
        for sel_group in [SEL_CROP_DONE, SEL_CROP_NEXT]:
            try:
                safe_click(device, sel_group, timeout=3)
                return
            except ElementNotFound:
                continue

        # If no confirmation button found, the sticker may have been
        # added directly without an edit screen
        print("    (No edit confirmation screen detected, continuing...)")
