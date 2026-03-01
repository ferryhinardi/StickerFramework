#!/usr/bin/env python3
"""
Collect diagnostic snapshot for a pack to help debug pipeline failures.

Prints a structured report to stdout. Exit 0 always (diagnostic only).

Usage: diagnose.py <pack_id>
"""

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]

ENV_VARS = [
    "OPENAI_API_KEY",
    "LINE_EMAIL",
    "LINE_PASSWORD",
    "TELEGRAM_BOT_TOKEN",
    "TELEGRAM_USER_ID",
    "APPLE_ID",
    "WHATSAPP_SERVER_URL",
]


def _present(val: str | None) -> str:
    if not val:
        return "MISSING"
    return f"SET ({val[:6]}...)" if len(val) > 8 else "SET"


def diagnose(pack_id: str) -> None:
    pack_dir = REPO_ROOT / "packs" / pack_id
    final_dir = pack_dir / "final"

    print(f"\n{'=' * 60}")
    print(f"  DIAGNOSTIC REPORT — pack: {pack_id}")
    print(f"{'=' * 60}\n")

    # --- Pack directory ---
    print("[ Pack Directory ]")
    print(f"  packs/{pack_id}/           exists={pack_dir.exists()}")
    print(
        f"  pack_config.py             exists={(pack_dir / 'pack_config.py').exists()}"
    )

    for sub in ("raw", "split", "final"):
        d = pack_dir / sub
        count = (
            len([f for f in d.iterdir() if f.is_file() and f.name != ".gitkeep"])
            if d.exists()
            else 0
        )
        print(f"  {sub:<12}                exists={d.exists()}, files={count}")

    # --- Final outputs ---
    print("\n[ Final Outputs ]")
    if final_dir.exists():
        for sub in final_dir.iterdir():
            if sub.is_dir():
                files = [
                    f for f in sub.iterdir() if f.is_file() and f.name != ".gitkeep"
                ]
                print(f"  {sub.name:<28} {len(files):>3} file(s)")
    else:
        print("  final/ directory does not exist — pipeline has not run.")

    # --- Session state ---
    print("\n[ LINE Session ]")
    session = Path.home() / ".line-sticker-automation" / "storage_state.json"
    progress = Path.home() / ".line-sticker-automation" / "progress.json"
    print(f"  session saved:   {session.exists()} ({session})")
    print(f"  progress saved:  {progress.exists()} ({progress})")

    # --- Environment variables ---
    print("\n[ Environment Variables ]")
    # load .env if present
    env_file = REPO_ROOT / ".env"
    env_vals: dict[str, str] = {}
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            if "=" in line and not line.startswith("#"):
                k, _, v = line.partition("=")
                env_vals[k.strip()] = v.strip()
    for var in ENV_VARS:
        val = os.environ.get(var) or env_vals.get(var)
        print(f"  {var:<35} {_present(val)}")

    # --- Python packages ---
    print("\n[ Key Python Packages ]")
    for pkg in ("playwright", "PIL", "rembg", "requests", "lottie"):
        try:
            mod = __import__(pkg if pkg != "PIL" else "PIL")
            ver = getattr(mod, "__version__", "installed")
            print(f"  {pkg:<20} {ver}")
        except ImportError:
            print(f"  {pkg:<20} NOT INSTALLED")

    print(f"\n{'=' * 60}\n")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: diagnose.py <pack_id>", file=sys.stderr)
        sys.exit(2)
    diagnose(sys.argv[1])
