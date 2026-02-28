"""
Sticker.ly authentication and session management via AVD snapshots.

First run: Show emulator GUI -> user logs in manually -> save snapshot.
Subsequent runs: Load snapshot -> validate session -> proceed.
"""

from __future__ import annotations

import json
import time
from datetime import datetime
from pathlib import Path

import uiautomator2 as u2

from automation.stickerly.config import (
    APP_LAUNCH_TIMEOUT,
    ELEMENT_WAIT_TIMEOUT,
    LOGIN_TIMEOUT,
    SEL_HOME_INDICATOR,
    SEL_LOGIN_GOOGLE,
    SESSION_MARKER_PATH,
    SESSION_STATE_DIR,
    SNAPSHOT_NAME,
    STICKERLY_PACKAGE,
)
from automation.stickerly.emulator import EmulatorManager
from automation.stickerly.utils import EmulatorNotReady, SessionExpired


class StickerlyAuth:
    """Manage Sticker.ly authentication via Android emulator snapshots."""

    def __init__(self, emulator: EmulatorManager):
        self.emulator = emulator
        self.device: u2.Device | None = None

    def connect_device(self) -> u2.Device:
        """Connect to the running emulator via uiautomator2."""
        if self.device is not None:
            return self.device

        print("  Connecting to emulator via uiautomator2...")
        self.device = u2.connect()
        # Configure defaults
        self.device.implicitly_wait(ELEMENT_WAIT_TIMEOUT)
        self.device.settings["wait_timeout"] = ELEMENT_WAIT_TIMEOUT
        print(f"  Connected: {self.device.info.get('productName', 'emulator')}")
        return self.device

    def setup_first_run(self) -> u2.Device:
        """
        Interactive first-run setup: start emulator with GUI, let user log in,
        save snapshot for future headless runs.

        Returns:
            Connected uiautomator2 Device.
        """
        print("\n" + "=" * 60)
        print("  FIRST-TIME SETUP: Sticker.ly Login")
        print("=" * 60)

        # Start emulator with GUI
        self.emulator.start(headless=False)
        device = self.connect_device()

        # Install Sticker.ly if not present
        if not self._is_app_installed(device):
            print("\n  Sticker.ly is NOT installed on the emulator.")
            print("  Please install it manually:")
            print("    1. Open Google Play Store in the emulator")
            print('    2. Search for "Sticker.ly"')
            print("    3. Install the app")
            print("    4. Press Enter here when done...")
            input()

        # Launch Sticker.ly
        print("  Launching Sticker.ly...")
        device.app_start(STICKERLY_PACKAGE)
        time.sleep(APP_LAUNCH_TIMEOUT)

        # Check if already logged in
        if self._is_authenticated(device):
            print("  Already logged in!")
        else:
            # Wait for user to log in manually
            print("\n  Please log in to Sticker.ly in the emulator window:")
            print("    1. Tap 'Continue with Google' or 'Sign in'")
            print("    2. Complete the Google OAuth flow")
            print("    3. Wait until you see the Sticker.ly home screen")
            print("    4. Press Enter here when done...")
            input()

            # Verify login succeeded
            if not self._is_authenticated(device):
                raise SessionExpired(
                    "Login verification failed. Sticker.ly does not appear "
                    "to be on the home screen."
                )

        # Save snapshot
        print("  Saving emulator snapshot with logged-in state...")
        self.emulator.save_snapshot(SNAPSHOT_NAME)

        # Save session marker
        self._save_session_marker()
        print("  Session saved! Future runs will use headless mode.")

        return device

    def restore_session(self) -> u2.Device:
        """
        Restore a previously saved session via AVD snapshot.

        Returns:
            Connected uiautomator2 Device with authenticated Sticker.ly.

        Raises:
            SessionExpired: If session is no longer valid.
            EmulatorNotReady: If emulator fails to start.
        """
        if not self._has_session_marker():
            raise SessionExpired(
                "No saved session found. Run with --headful for first-time setup."
            )

        # Start emulator headless
        self.emulator.start(headless=True)
        device = self.connect_device()

        # Load saved snapshot
        if self.emulator.has_snapshot(SNAPSHOT_NAME):
            self.emulator.load_snapshot(SNAPSHOT_NAME)
            time.sleep(3)
        else:
            print("  WARNING: Snapshot not found, continuing without restore.")

        # Launch Sticker.ly
        device.app_start(STICKERLY_PACKAGE)
        time.sleep(APP_LAUNCH_TIMEOUT)

        # Validate session
        if not self._is_authenticated(device):
            raise SessionExpired("Session expired. Run with --headful to log in again.")

        print("  Session restored successfully.")
        return device

    def ensure_authenticated(self, device: u2.Device) -> bool:
        """
        Check if Sticker.ly is on an authenticated screen.
        Re-launches the app if needed.

        Returns:
            True if authenticated, raises SessionExpired otherwise.
        """
        current_pkg = device.app_current().get("package", "")
        if current_pkg != STICKERLY_PACKAGE:
            device.app_start(STICKERLY_PACKAGE)
            time.sleep(APP_LAUNCH_TIMEOUT)

        if not self._is_authenticated(device):
            raise SessionExpired(
                "Sticker.ly session expired. Run with --headful to log in again."
            )
        return True

    # -- Internal helpers -------------------------------------------------------

    def _is_app_installed(self, device: u2.Device) -> bool:
        """Check if Sticker.ly is installed on the device."""
        try:
            info = device.app_info(STICKERLY_PACKAGE)
            return info is not None
        except Exception:
            return False

    def _is_authenticated(self, device: u2.Device) -> bool:
        """
        Determine if Sticker.ly is showing an authenticated screen.
        Returns True if home screen elements are found, False if login screen.
        """
        # Check for login screen indicator (should NOT be present)
        try:
            el = device(**SEL_LOGIN_GOOGLE)
            if el.exists(timeout=2):
                return False
        except Exception:
            pass

        # Check for home screen indicator (SHOULD be present)
        try:
            el = device(**SEL_HOME_INDICATOR)
            if el.exists(timeout=3):
                return True
        except Exception:
            pass

        # Fallback: if we can't determine, assume authenticated
        # (user may be on a different screen within the app)
        current_pkg = device.app_current().get("package", "")
        return current_pkg == STICKERLY_PACKAGE

    def _save_session_marker(self) -> None:
        """Save a marker file indicating a valid session exists."""
        SESSION_STATE_DIR.mkdir(parents=True, exist_ok=True)
        marker = {
            "avd_name": self.emulator.avd_name,
            "snapshot_name": SNAPSHOT_NAME,
            "created_at": datetime.now().isoformat(),
            "package": STICKERLY_PACKAGE,
        }
        SESSION_MARKER_PATH.write_text(json.dumps(marker, indent=2))

    def _has_session_marker(self) -> bool:
        """Check if a session marker file exists."""
        return SESSION_MARKER_PATH.exists()
