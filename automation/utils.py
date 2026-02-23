"""
Shared utility functions for LINE Creator Market automation.

Provides resilient selector clicks, form fills, retry logic,
screenshot-on-failure context manager, and human-like delays.
"""

from __future__ import annotations

import asyncio
import random
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import Any

from playwright.async_api import Page, TimeoutError as PlaywrightTimeout

from automation.config import SCREENSHOT_DIR, SELECTOR_TIMEOUT


# ─── Exceptions ──────────────────────────────────────────────────────────────


class SelectorNotFound(Exception):
    """Raised when none of the candidate selectors match an element."""


class UploadVerificationError(Exception):
    """Raised when uploaded file count doesn't match expected."""


class SessionNotFound(Exception):
    """Raised when no saved session file exists."""


# ─── Resilient selector click ────────────────────────────────────────────────


async def safe_click(
    page: Page,
    selectors: list[str],
    timeout: int = SELECTOR_TIMEOUT,
) -> None:
    """
    Try multiple selectors in order; click the first one that resolves.

    Args:
        page: Playwright Page instance.
        selectors: Ordered list of CSS / text selectors to try.
        timeout: Max wait per selector in ms.

    Raises:
        SelectorNotFound: If none of the selectors match within timeout.
    """
    errors: list[str] = []
    for selector in selectors:
        try:
            await page.click(selector, timeout=timeout)
            return
        except PlaywrightTimeout as exc:
            errors.append(f"  {selector}: {exc}")
    raise SelectorNotFound(f"None of these selectors found:\n" + "\n".join(errors))


# ─── Resilient fill ──────────────────────────────────────────────────────────


async def safe_fill(
    page: Page,
    selector: str,
    value: str,
    clear_first: bool = True,
    timeout: int = SELECTOR_TIMEOUT,
) -> None:
    """
    Wait for an input and fill it with *value*, optionally clearing first.

    Args:
        page: Playwright Page instance.
        selector: CSS selector for the input element.
        value: Text to type.
        clear_first: Whether to clear existing content before filling.
        timeout: Max wait for element in ms.
    """
    element = await page.wait_for_selector(selector, timeout=timeout)
    if element is None:
        raise SelectorNotFound(f"Element not found: {selector}")
    if clear_first:
        await element.fill("")
    await element.fill(value)


# ─── Retry with exponential backoff ──────────────────────────────────────────


async def retry_with_backoff(
    func: Any,
    max_retries: int = 3,
    base_delay: float = 1.0,
) -> Any:
    """
    Call an async callable, retrying on failure with exponential backoff.

    Args:
        func: An async callable (no args) to execute.
        max_retries: Total attempts before giving up.
        base_delay: Delay in seconds for the first retry (doubles each time).

    Returns:
        The return value of *func* on success.

    Raises:
        The last exception if all retries fail.
    """
    for attempt in range(max_retries):
        try:
            return await func()
        except Exception as exc:
            if attempt == max_retries - 1:
                raise
            delay = base_delay * (2**attempt)
            print(
                f"  Attempt {attempt + 1}/{max_retries} failed: {exc}. "
                f"Retrying in {delay:.1f}s..."
            )
            await asyncio.sleep(delay)


# ─── Screenshot on failure ───────────────────────────────────────────────────


@asynccontextmanager
async def screenshot_on_failure(page: Page, action_name: str):
    """
    Async context manager that captures a full-page screenshot on exception.

    Usage::

        async with screenshot_on_failure(page, "upload_main"):
            await uploader.upload_main_image(page, path)
    """
    try:
        yield
    except Exception:
        SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = SCREENSHOT_DIR / f"{timestamp}_{action_name}.png"
        try:
            await page.screenshot(path=str(path), full_page=True)
            print(f"  Screenshot saved: {path}")
        except Exception as ss_err:
            print(f"  Failed to save screenshot: {ss_err}")
        raise


# ─── Human-like delays ───────────────────────────────────────────────────────


async def human_delay(min_ms: int = 500, max_ms: int = 2000) -> None:
    """Sleep for a random duration to simulate human interaction speed."""
    delay = random.randint(min_ms, max_ms) / 1000
    await asyncio.sleep(delay)


# ─── Tab navigation helper ───────────────────────────────────────────────────


async def navigate_to_tab(page: Page, tab_name: str) -> None:
    """
    Click a tab by its visible text.

    Tries ``<a>`` links first, then ARIA tab roles, then generic tab classes.
    """
    await safe_click(
        page,
        [
            f"a:has-text('{tab_name}')",
            f"[role='tab']:has-text('{tab_name}')",
            f".tab-item:has-text('{tab_name}')",
        ],
    )
    await page.wait_for_load_state("networkidle")


# ─── Progress persistence ────────────────────────────────────────────────────

import json


def save_progress(progress: dict, path: Path | None = None) -> None:
    """Write progress dict to JSON file."""
    from automation.config import PROGRESS_STATE_PATH

    dest = path or PROGRESS_STATE_PATH
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(progress, indent=2, default=str))


def load_progress(path: Path | None = None) -> dict | None:
    """Load progress dict from JSON file, or None if absent."""
    from automation.config import PROGRESS_STATE_PATH

    src = path or PROGRESS_STATE_PATH
    if not src.exists():
        return None
    return json.loads(src.read_text())
