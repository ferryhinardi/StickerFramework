#!/usr/bin/env python3
"""
Verify Telegram credentials and sticker assets.

Exit 0 = OK. Exit 1 = error.

Usage: check_telegram_env.py
       check_telegram_assets.py <pack_id> <format>
       (format: static | animated | video)
"""

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]

FORMAT_DIRS = {
    "static": ("telegram", (".webp", ".png"), 256_000),
    "animated": ("telegram_animated", (".tgs",), 64_000),
    "video": ("telegram_video", (".webm",), 256_000),
}


def check_env() -> list[str]:
    errors = []
    for var in ("TELEGRAM_BOT_TOKEN", "TELEGRAM_USER_ID"):
        if not os.environ.get(var):
            # also try loading from .env
            env_file = REPO_ROOT / ".env"
            found = False
            if env_file.exists():
                for line in env_file.read_text().splitlines():
                    if line.startswith(f"{var}=") and line.split("=", 1)[1].strip():
                        found = True
                        break
            if not found:
                errors.append(f"{var} is not set in environment or .env")
    return errors


def check_assets(pack_id: str, fmt: str) -> list[str]:
    errors = []
    if fmt not in FORMAT_DIRS:
        errors.append(f"Unknown format '{fmt}'. Choose: static, animated, video.")
        return errors

    subdir, exts, max_bytes = FORMAT_DIRS[fmt]
    d = REPO_ROOT / "packs" / pack_id / "final" / subdir
    if not d.exists():
        errors.append(
            f"packs/{pack_id}/final/{subdir}/ does not exist. "
            f"Run process-pipeline with the appropriate flag first."
        )
        return errors

    files = [f for f in d.iterdir() if f.suffix in exts and f.name != ".gitkeep"]
    if not files:
        errors.append(f"No {exts} files found in final/{subdir}/")
        return errors

    for f in files:
        size = f.stat().st_size
        if size > max_bytes:
            errors.append(
                f"{f.name}: {size / 1024:.1f} KB exceeds "
                f"{max_bytes / 1024:.0f} KB Telegram limit."
            )

    print(f"Found {len(files)} file(s) in final/{subdir}/")
    return errors


if __name__ == "__main__":
    if len(sys.argv) == 1:
        # env check mode
        errs = check_env()
    elif len(sys.argv) == 3:
        errs = check_env() + check_assets(sys.argv[1], sys.argv[2])
    else:
        print("Usage: check_telegram_env.py [<pack_id> <format>]", file=sys.stderr)
        sys.exit(2)

    if errs:
        for e in errs:
            print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    print("Telegram check passed.")
