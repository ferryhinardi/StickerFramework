"""
Shared utility functions for Sticker.ly emulator automation.

Provides ADB helpers, screenshot capture, progress persistence,
human-like delays, and resilient UI element interaction.
"""

from __future__ import annotations

import json
import random
import subprocess
import time
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any

from automation.stickerly.config import (
    ELEMENT_WAIT_TIMEOUT,
    SCREENSHOT_DIR,
    SESSION_STATE_DIR,
)


# -- Exceptions ----------------------------------------------------------------


class ElementNotFound(Exception):
    """Raised when none of the candidate selectors match a UI element."""


class SessionExpired(Exception):
    """Raised when Sticker.ly session is no longer valid (login screen detected)."""


class EmulatorNotReady(Exception):
    """Raised when emulator fails to boot or ADB cannot connect."""


class StickerUploadError(Exception):
    """Raised when a sticker upload fails validation or times out."""


# -- Human-like delays ---------------------------------------------------------


def human_delay(min_ms: int = 500, max_ms: int = 2000) -> None:
    """Sleep for a random duration to simulate human interaction speed."""
    delay = random.randint(min_ms, max_ms) / 1000
    time.sleep(delay)


# -- Resilient UI interaction --------------------------------------------------


def find_element(device, selector_group: dict, timeout: float = ELEMENT_WAIT_TIMEOUT):
    """
    Try multiple selectors in order; return the first element found.

    Args:
        device: uiautomator2.Device instance.
        selector_group: Dict with 'description' and 'selectors' (list of
            uiautomator2 selector kwargs).
        timeout: Max wait per selector in seconds.

    Returns:
        uiautomator2 UiObject that matched.

    Raises:
        ElementNotFound: If none of the selectors match within timeout.
    """
    errors = []
    desc = selector_group.get("description", "unknown element")
    for sel_kwargs in selector_group["selectors"]:
        try:
            el = device(**sel_kwargs)
            if el.wait(timeout=timeout):
                return el
            errors.append(f"  {sel_kwargs}: timed out after {timeout}s")
        except Exception as exc:
            errors.append(f"  {sel_kwargs}: {exc}")
    raise ElementNotFound(f"Cannot find '{desc}'. Tried:\n" + "\n".join(errors))


def safe_click(
    device, selector_group: dict, timeout: float = ELEMENT_WAIT_TIMEOUT
) -> None:
    """Find element using selector group and click it."""
    el = find_element(device, selector_group, timeout)
    el.click()


def safe_set_text(
    device,
    selector_group: dict,
    text: str,
    clear_first: bool = True,
    timeout: float = ELEMENT_WAIT_TIMEOUT,
) -> None:
    """Find element using selector group and set its text."""
    el = find_element(device, selector_group, timeout)
    if clear_first:
        el.clear_text()
    el.set_text(text)


# -- Retry with backoff --------------------------------------------------------


def retry_with_backoff(
    func: Any,
    max_retries: int = 3,
    base_delay: float = 1.0,
) -> Any:
    """
    Call a callable, retrying on failure with exponential backoff.

    Args:
        func: Callable (no args) to execute.
        max_retries: Total attempts before giving up.
        base_delay: Delay in seconds for the first retry (doubles each time).

    Returns:
        The return value of *func* on success.

    Raises:
        The last exception if all retries fail.
    """
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as exc:
            if attempt == max_retries - 1:
                raise
            delay = base_delay * (2**attempt)
            print(
                f"  Attempt {attempt + 1}/{max_retries} failed: {exc}. "
                f"Retrying in {delay:.1f}s..."
            )
            time.sleep(delay)


# -- Screenshot on failure -----------------------------------------------------


@contextmanager
def screenshot_on_failure(device, action_name: str):
    """
    Context manager that captures an emulator screenshot on exception.

    Usage::

        with screenshot_on_failure(device, "add_sticker_03"):
            add_sticker(device, sticker_path)
    """
    try:
        yield
    except Exception:
        SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = SCREENSHOT_DIR / f"{timestamp}_{action_name}.png"
        try:
            device.screenshot(str(path))
            print(f"  Screenshot saved: {path}")
        except Exception as ss_err:
            print(f"  Failed to save screenshot: {ss_err}")
        raise


# -- ADB helpers ---------------------------------------------------------------


def adb_shell(cmd: str, timeout: int = 30) -> str:
    """Run an ADB shell command and return stdout."""
    result = subprocess.run(
        ["adb", "shell", cmd],
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    if result.returncode != 0:
        raise RuntimeError(f"adb shell '{cmd}' failed: {result.stderr.strip()}")
    return result.stdout.strip()


def adb_push(local_path: str, remote_path: str) -> None:
    """Push a local file to the emulator."""
    result = subprocess.run(
        ["adb", "push", local_path, remote_path],
        capture_output=True,
        text=True,
        timeout=60,
    )
    if result.returncode != 0:
        raise RuntimeError(f"adb push failed: {result.stderr.strip()}")


def adb_pull(remote_path: str, local_path: str) -> None:
    """Pull a file from the emulator to local."""
    result = subprocess.run(
        ["adb", "pull", remote_path, local_path],
        capture_output=True,
        text=True,
        timeout=60,
    )
    if result.returncode != 0:
        raise RuntimeError(f"adb pull failed: {result.stderr.strip()}")


# -- Progress persistence ------------------------------------------------------


def save_progress(progress: dict, path: Path | None = None) -> None:
    """Write progress dict to JSON file."""
    from automation.stickerly.config import PROGRESS_STATE_PATH

    dest = path or PROGRESS_STATE_PATH
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(progress, indent=2, default=str))


def load_progress(path: Path | None = None) -> dict | None:
    """Load progress dict from JSON file, or None if absent."""
    from automation.stickerly.config import PROGRESS_STATE_PATH

    src = path or PROGRESS_STATE_PATH
    if not src.exists():
        return None
    return json.loads(src.read_text())


def save_published_pack(pack_id: str, share_link: str | None = None) -> None:
    """Append a published pack entry to the published packs log."""
    from automation.stickerly.config import PUBLISHED_PACKS_PATH

    PUBLISHED_PACKS_PATH.parent.mkdir(parents=True, exist_ok=True)
    packs = {}
    if PUBLISHED_PACKS_PATH.exists():
        packs = json.loads(PUBLISHED_PACKS_PATH.read_text())
    packs[pack_id] = {
        "share_link": share_link,
        "published_at": datetime.now().isoformat(),
    }
    PUBLISHED_PACKS_PATH.write_text(json.dumps(packs, indent=2))
