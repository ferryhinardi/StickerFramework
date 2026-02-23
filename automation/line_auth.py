"""
LINE Creator Market authentication module.

Handles login via access.line.me OAuth (email + password → verification code
displayed in browser → user enters code in LINE mobile app), and session
persistence via Playwright's ``storage_state()``.

Confirmed login flow (Feb 2026):
1. Navigate to /signup/line_auth → redirects to access.line.me
2. Fill email (input[name="tid"]) + password (input[name="tpasswd"]) → submit
3. Browser shows a verification code — user manually enters it in LINE app
4. After verification, redirects to /my/{creator}/sticker/
5. Session saved to ~/.line-sticker-automation/storage_state.json
"""

from __future__ import annotations

import json
from pathlib import Path

from playwright.async_api import (
    Browser,
    BrowserContext,
    Page,
    TimeoutError as PlaywrightTimeout,
)

from automation.config import (
    BASE_URL,
    LOGIN_AUTH_URL,
    LOGIN_TIMEOUT,
    MY_STICKERS_URL,
    SEL_LOGIN_EMAIL,
    SEL_LOGIN_PASSWORD,
    SEL_LOGIN_SUBMIT,
    SESSION_STATE_PATH,
)
from automation.utils import SessionNotFound, human_delay


class LineAuth:
    """Manages LINE Creator Market authentication and session persistence."""

    def __init__(self, storage_path: str | Path | None = None):
        self.storage_path = Path(storage_path or SESSION_STATE_PATH).expanduser()
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

    # ── Public API ────────────────────────────────────────────────────────

    async def login(self, page: Page, email: str = "", password: str = "") -> None:
        """
        Navigate to LINE login and authenticate.

        If *email* and *password* are provided, fills them automatically and
        waits for the user to complete the verification-code-in-app step.
        Otherwise shows the login page for fully manual interaction.

        The browser window must be visible (headful mode).
        """
        await page.goto(LOGIN_AUTH_URL, wait_until="networkidle")
        await human_delay(1000, 2000)

        # Already logged in? (restored session still valid)
        if await self._is_authenticated(page):
            print("Already authenticated.")
            await self._save_session(page.context)
            return

        # If we landed on the access.line.me login form, fill credentials
        if "access.line.me" in page.url and email and password:
            print("Filling login credentials...")
            await page.fill(SEL_LOGIN_EMAIL, email)
            await human_delay(300, 600)
            await page.fill(SEL_LOGIN_PASSWORD, password)
            await human_delay(300, 600)
            await page.click(SEL_LOGIN_SUBMIT)
            await human_delay(1000, 2000)

        print()
        print("=" * 60)
        print("  A verification code is shown in the browser.")
        print("  Enter this code in your LINE mobile app to log in.")
        print("  Waiting up to 5 minutes...")
        print("=" * 60)
        print()

        # Block until the browser redirects to the dashboard
        await page.wait_for_url(
            f"{BASE_URL}/my/**",
            timeout=LOGIN_TIMEOUT,
        )

        await self._save_session(page.context)
        print("Session saved successfully.")

    async def restore_session(self, browser: Browser) -> BrowserContext:
        """
        Create a new BrowserContext pre-loaded with saved cookies/localStorage.

        Raises:
            SessionNotFound: If no saved session file exists on disk.
        """
        if not self.storage_path.exists():
            raise SessionNotFound(
                f"No saved session at {self.storage_path}. "
                "Run with --headful to log in interactively."
            )

        context = await browser.new_context(
            storage_state=str(self.storage_path),
        )
        return context

    async def ensure_authenticated(self, page: Page) -> None:
        """
        Verify the current session is still valid.

        If the session has expired (redirected to login page), triggers an
        interactive login flow and saves the new session.
        """
        if not await self._check_session_valid(page):
            print("Session expired — re-authenticating...")
            await self.login(page)

    # ── Private helpers ───────────────────────────────────────────────────

    async def _is_authenticated(self, page: Page) -> bool:
        """Return True if the current URL indicates a logged-in state."""
        return f"{BASE_URL}/my/" in page.url

    async def _check_session_valid(self, page: Page) -> bool:
        """Navigate to a protected page; return False if redirected to login."""
        await page.goto(MY_STICKERS_URL, wait_until="domcontentloaded")
        await human_delay(1000, 2000)
        return "login" not in page.url.lower() and "access.line.me" not in page.url

    async def _save_session(self, context: BrowserContext) -> None:
        """Persist cookies + localStorage to disk."""
        state = await context.storage_state()
        self.storage_path.write_text(json.dumps(state, indent=2))
