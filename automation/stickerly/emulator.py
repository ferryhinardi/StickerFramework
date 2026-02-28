"""
Android emulator lifecycle management for Sticker.ly automation.

Handles starting/stopping the emulator, waiting for boot, AVD snapshots,
and pushing sticker files to emulator storage.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import time
from pathlib import Path

from automation.stickerly.config import (
    ADB_DEVICE_TIMEOUT,
    DEFAULT_AVD_NAME,
    EMULATOR_BOOT_TIMEOUT,
    REMOTE_STICKER_DIR,
    SNAPSHOT_NAME,
)
from automation.stickerly.utils import EmulatorNotReady, adb_push, adb_shell


class EmulatorManager:
    """Manage Android emulator lifecycle for Sticker.ly automation."""

    def __init__(self, avd_name: str = DEFAULT_AVD_NAME):
        self.avd_name = avd_name
        self._emulator_proc: subprocess.Popen | None = None

    # -- Emulator lifecycle -----------------------------------------------------

    def start(self, headless: bool = True, wipe_data: bool = False) -> None:
        """
        Launch the Android emulator.

        Args:
            headless: If True, run without GUI window (for automated runs).
                      If False, show GUI (for first-time login).
            wipe_data: If True, wipe user data on start.
        """
        if self.is_running():
            print("  Emulator already running, reusing existing instance.")
            return

        emulator_bin = self._find_emulator()
        cmd = [emulator_bin, "-avd", self.avd_name]

        if headless:
            cmd.extend(["-no-window", "-no-audio"])
        if wipe_data:
            cmd.append("-wipe-data")

        # GPU acceleration for Apple Silicon
        cmd.extend(["-gpu", "host"])

        print(f"  Starting emulator: {self.avd_name} (headless={headless})...")
        self._emulator_proc = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        self._wait_for_boot()
        print("  Emulator booted successfully.")

    def stop(self) -> None:
        """Stop the running emulator."""
        if self._emulator_proc:
            print("  Stopping emulator...")
            try:
                subprocess.run(
                    ["adb", "emu", "kill"],
                    capture_output=True,
                    timeout=10,
                )
            except Exception:
                pass
            try:
                self._emulator_proc.terminate()
                self._emulator_proc.wait(timeout=10)
            except Exception:
                self._emulator_proc.kill()
            self._emulator_proc = None
            print("  Emulator stopped.")
        else:
            # Try killing via ADB anyway (emulator may have been started externally)
            try:
                subprocess.run(
                    ["adb", "emu", "kill"],
                    capture_output=True,
                    timeout=10,
                )
            except Exception:
                pass

    def is_running(self) -> bool:
        """Check if an emulator device is connected via ADB."""
        try:
            result = subprocess.run(
                ["adb", "devices"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            lines = result.stdout.strip().split("\n")[1:]  # Skip header
            for line in lines:
                if "emulator" in line and "device" in line:
                    return True
            return False
        except Exception:
            return False

    # -- Snapshot management ----------------------------------------------------

    def save_snapshot(self, name: str = SNAPSHOT_NAME) -> None:
        """Save the current emulator state as a snapshot."""
        print(f"  Saving emulator snapshot: {name}")
        result = subprocess.run(
            ["adb", "emu", "avd", "snapshot", "save", name],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode != 0:
            raise RuntimeError(f"Failed to save snapshot: {result.stderr.strip()}")
        print(f"  Snapshot '{name}' saved.")

    def load_snapshot(self, name: str = SNAPSHOT_NAME) -> None:
        """Load a previously saved emulator snapshot."""
        print(f"  Loading emulator snapshot: {name}")
        result = subprocess.run(
            ["adb", "emu", "avd", "snapshot", "load", name],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode != 0:
            raise RuntimeError(f"Failed to load snapshot: {result.stderr.strip()}")
        # Wait a moment for snapshot to fully restore
        time.sleep(3)
        print(f"  Snapshot '{name}' loaded.")

    def has_snapshot(self, name: str = SNAPSHOT_NAME) -> bool:
        """Check if a named snapshot exists."""
        try:
            result = subprocess.run(
                ["adb", "emu", "avd", "snapshot", "list"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            return name in result.stdout
        except Exception:
            return False

    # -- File management --------------------------------------------------------

    def push_stickers(self, local_dir: str | Path, pack_id: str) -> str:
        """
        Push sticker files from local directory to emulator storage.

        Args:
            local_dir: Path to local directory with .webp sticker files.
            pack_id: Pack identifier (used as subdirectory name).

        Returns:
            Remote directory path where files were pushed.
        """
        local_dir = Path(local_dir)
        remote_dir = f"{REMOTE_STICKER_DIR}/{pack_id}"

        # Create remote directory
        adb_shell(f"mkdir -p {remote_dir}")

        # Push all .webp files
        webp_files = sorted(local_dir.glob("*.webp"))
        if not webp_files:
            raise FileNotFoundError(f"No .webp files found in {local_dir}")

        print(f"  Pushing {len(webp_files)} sticker files to emulator...")
        for f in webp_files:
            adb_push(str(f), f"{remote_dir}/{f.name}")

        # Trigger media scan so files appear in file picker
        adb_shell(
            f"am broadcast -a android.intent.action.MEDIA_SCANNER_SCAN_FILE "
            f'-d "file://{remote_dir}"'
        )
        # Also scan individual files
        for f in webp_files:
            adb_shell(
                f"am broadcast -a android.intent.action.MEDIA_SCANNER_SCAN_FILE "
                f'-d "file://{remote_dir}/{f.name}"'
            )

        print(f"  Files pushed to: {remote_dir}")
        return remote_dir

    def clean_remote_stickers(self, pack_id: str | None = None) -> None:
        """Remove sticker files from emulator storage."""
        if pack_id:
            adb_shell(f"rm -rf {REMOTE_STICKER_DIR}/{pack_id}")
        else:
            adb_shell(f"rm -rf {REMOTE_STICKER_DIR}")

    # -- Internal helpers -------------------------------------------------------

    def _wait_for_boot(self) -> None:
        """Poll until emulator is fully booted."""
        start = time.time()
        while time.time() - start < EMULATOR_BOOT_TIMEOUT:
            try:
                # Wait for ADB device
                result = subprocess.run(
                    ["adb", "wait-for-device"],
                    capture_output=True,
                    timeout=ADB_DEVICE_TIMEOUT,
                )
                # Check boot completion
                boot = adb_shell("getprop sys.boot_completed")
                if boot.strip() == "1":
                    # Extra wait for system services
                    time.sleep(5)
                    return
            except Exception:
                pass
            time.sleep(2)
        raise EmulatorNotReady(f"Emulator did not boot within {EMULATOR_BOOT_TIMEOUT}s")

    def _find_emulator(self) -> str:
        """Locate the Android emulator binary."""
        # Check ANDROID_HOME
        android_home = os.environ.get("ANDROID_HOME") or os.environ.get(
            "ANDROID_SDK_ROOT"
        )
        if android_home:
            emu = Path(android_home) / "emulator" / "emulator"
            if emu.exists():
                return str(emu)

        # Check PATH
        emu_path = shutil.which("emulator")
        if emu_path:
            return emu_path

        raise FileNotFoundError(
            "Android emulator not found. Set ANDROID_HOME or add emulator to PATH."
        )
