#!/usr/bin/env python3
"""
LINE Pre-flight Checklist — Screens sticker packs for LINE guideline violations.

Checks pack_metadata.json and sticker filenames/text for content that would
violate LINE Creators Market guidelines, particularly:
  - 3.13: Religious content (images designed to solicit or spread religion)

Usage:
    # Check a specific pack:
    python scripts/line_preflight_check.py --pack-dir packs/boba-milo-5

    # Check all packs:
    python scripts/line_preflight_check.py --all

    # Strict mode (fail on warnings too):
    python scripts/line_preflight_check.py --pack-dir packs/boba-milo-3 --strict
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# ─── Religious content keyword lists ─────────────────────────────────────────
# These keywords in sticker filenames, titles, or descriptions may trigger
# LINE guideline 3.13 rejection.

RELIGIOUS_KEYWORDS_HIGH = [
    # Islamic
    "ramadan",
    "ramadhan",
    "eid",
    "idul fitri",
    "idul adha",
    "marhaban",
    "alhamdulillah",
    "subhanallah",
    "bismillah",
    "insya allah",
    "insyaallah",
    "inshallah",
    "astaghfirullah",
    "tarawih",
    "taraweeh",
    "sahur",
    "suhoor",
    "iftar",
    "berbuka",
    "puasa",
    "fasting",
    "mosque",
    "masjid",
    "quran",
    "sholat",
    "salat",
    "prayer",
    "doa",
    "hijab",
    "muharam",
    "muharram",
    "mohon maaf lahir batin",
    "lebaran",
    "ketupat",
    # Christian
    "christmas",
    "easter",
    "church",
    "bible",
    "jesus",
    "christ",
    "baptism",
    "communion",
    "gospel",
    "hallelujah",
    "psalm",
    "nativity",
    "advent",
    "lent",
    "pentecost",
    # Buddhist
    "buddha",
    "dharma",
    "sangha",
    "nirvana",
    "vesak",
    "waisak",
    "meditation",
    "temple",
    # Hindu
    "diwali",
    "deepavali",
    "ganesh",
    "krishna",
    "shiva",
    "puja",
    "mandir",
    "hindu",
    # Jewish
    "hanukkah",
    "chanukah",
    "synagogue",
    "torah",
    "shabbat",
    "passover",
    "yom kippur",
    "rosh hashanah",
    # General religious
    "pray",
    "blessing",
    "blessed",
    "holy",
    "sacred",
    "divine",
    "worship",
    "faith",
    "scripture",
    "religious",
    "spiritual",
    "god",
    "allah",
    "yahweh",
]

RELIGIOUS_KEYWORDS_MEDIUM = [
    # Words that might be religious in context but have secular uses too
    "berkah",
    "thankful",
    "grateful",
    "peace",
    "sabar",
    "patience",
    "forgive",
    "forgiveness",
    "angel",
    "heaven",
    "soul",
    "spirit",
    "crescent",
    "star and crescent",
    "cross",
]

# ─── Result types ────────────────────────────────────────────────────────────


class CheckResult:
    def __init__(self):
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.info: list[str] = []
        self.passed = True

    def error(self, msg: str):
        self.errors.append(msg)
        self.passed = False

    def warn(self, msg: str):
        self.warnings.append(msg)

    def add_info(self, msg: str):
        self.info.append(msg)


# ─── Checks ──────────────────────────────────────────────────────────────────


def check_metadata_file(pack_dir: Path, result: CheckResult) -> dict | None:
    """Check if pack_metadata.json exists and LINE is enabled."""
    metadata_path = pack_dir / "pack_metadata.json"
    if not metadata_path.exists():
        result.warn(
            f"No pack_metadata.json found in {pack_dir.name} — cannot verify platform compatibility"
        )
        return None

    with open(metadata_path) as f:
        metadata = json.load(f)

    line_config = metadata.get("platforms", {}).get("line", {})
    if not line_config.get("enabled", True):
        reason = line_config.get("disabled_reason", "No reason specified")
        result.error(f"LINE is DISABLED for this pack: {reason}")
        return metadata

    content_flags = metadata.get("content_flags", {})
    if content_flags.get("contains_religious_content", False):
        result.error(
            "Pack metadata flags contains_religious_content=true — cannot submit to LINE"
        )

    risk = content_flags.get("line_guideline_3_13_risk", "none")
    if risk == "high":
        result.error(f"Pack metadata flags line_guideline_3_13_risk={risk}")
    elif risk == "medium":
        result.warn(
            f"Pack metadata flags line_guideline_3_13_risk={risk} — review carefully"
        )

    result.add_info(f"Pack: {metadata.get('pack_name', 'Unknown')}")
    result.add_info(f"Theme: {metadata.get('theme', 'Unknown')}")
    return metadata


def check_sticker_filenames(pack_dir: Path, result: CheckResult):
    """Scan sticker filenames for religious keywords."""
    # Check split/ and final/line/ directories
    dirs_to_check = [
        pack_dir / "split",
        pack_dir / "final" / "line",
        pack_dir / "final" / "line_main",
        pack_dir / "final" / "line_tab",
    ]

    all_names: set[str] = set()
    for d in dirs_to_check:
        if d.exists():
            for f in d.iterdir():
                if f.suffix in (".png", ".webp", ".jpg"):
                    all_names.add(f.stem.lower())

    if not all_names:
        result.warn("No sticker image files found to check")
        return

    result.add_info(f"Checking {len(all_names)} sticker filename(s)")

    for name in sorted(all_names):
        # Check high-risk keywords
        for keyword in RELIGIOUS_KEYWORDS_HIGH:
            if keyword in name.replace("_", " "):
                result.error(
                    f"RELIGIOUS KEYWORD in filename '{name}': "
                    f"contains '{keyword}' (guideline 3.13 HIGH risk)"
                )
        # Check medium-risk keywords
        for keyword in RELIGIOUS_KEYWORDS_MEDIUM:
            if keyword in name.replace("_", " "):
                result.warn(
                    f"Potentially religious keyword in filename '{name}': "
                    f"contains '{keyword}' (review context)"
                )


def check_title_description(
    title: str | None, description: str | None, result: CheckResult
):
    """Check title and description for religious keywords."""
    for label, text in [("title", title), ("description", description)]:
        if not text:
            continue
        text_lower = text.lower()
        for keyword in RELIGIOUS_KEYWORDS_HIGH:
            if keyword in text_lower:
                result.error(
                    f"RELIGIOUS KEYWORD in {label} '{text}': "
                    f"contains '{keyword}' (guideline 3.13 HIGH risk)"
                )
        for keyword in RELIGIOUS_KEYWORDS_MEDIUM:
            if keyword in text_lower:
                result.warn(
                    f"Potentially religious keyword in {label} '{text}': "
                    f"contains '{keyword}' (review context)"
                )


def check_theme(metadata: dict | None, result: CheckResult):
    """Check if the pack theme is religious."""
    if not metadata:
        return
    theme = metadata.get("theme", "").lower()
    religious_themes = [
        "ramadan",
        "eid",
        "christmas",
        "easter",
        "diwali",
        "vesak",
        "hanukkah",
        "religious",
        "islamic",
        "christian",
        "buddhist",
        "hindu",
        "jewish",
        "ramadan-eid",
    ]
    for rt in religious_themes:
        if rt in theme:
            result.error(
                f"Pack theme '{theme}' is religious — not compatible with LINE guideline 3.13"
            )
            return


# ─── Main runner ─────────────────────────────────────────────────────────────


def run_preflight(pack_dir: Path, strict: bool = False) -> bool:
    """Run all pre-flight checks for a pack. Returns True if passed."""
    print(f"\n{'=' * 60}")
    print(f"  LINE PRE-FLIGHT CHECK: {pack_dir.name}")
    print(f"{'=' * 60}\n")

    result = CheckResult()

    # 1. Check metadata
    metadata = check_metadata_file(pack_dir, result)

    # 2. Check sticker filenames
    check_sticker_filenames(pack_dir, result)

    # 3. Check title/description from metadata
    if metadata:
        line_config = metadata.get("platforms", {}).get("line", {})
        check_title_description(
            line_config.get("title"),
            line_config.get("description"),
            result,
        )
        check_theme(metadata, result)

    # Print results
    for msg in result.info:
        print(f"  INFO: {msg}")
    print()

    if result.errors:
        for msg in result.errors:
            print(f"  FAIL: {msg}")
        print()

    if result.warnings:
        for msg in result.warnings:
            print(f"  WARN: {msg}")
        print()

    passed = result.passed and (not strict or len(result.warnings) == 0)

    if passed:
        print("  RESULT: PASSED — Pack is eligible for LINE submission")
    else:
        print("  RESULT: FAILED — Pack has issues that will cause LINE rejection")
        if result.errors:
            print(
                f"           {len(result.errors)} error(s), {len(result.warnings)} warning(s)"
            )

    print()
    return passed


def main():
    parser = argparse.ArgumentParser(
        description="LINE pre-flight checklist for sticker packs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--pack-dir",
        type=str,
        help="Path to pack directory (e.g., packs/boba-milo-3)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Check all packs in packs/ directory",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail on warnings too (not just errors)",
    )
    parser.add_argument(
        "--title",
        type=str,
        help="Override title to check (instead of reading from pack_metadata.json)",
    )
    parser.add_argument(
        "--description",
        type=str,
        help="Override description to check",
    )

    args = parser.parse_args()

    if not args.pack_dir and not args.all:
        parser.error("--pack-dir or --all is required")

    all_passed = True

    if args.all:
        packs_dir = REPO_ROOT / "packs"
        for pack in sorted(packs_dir.iterdir()):
            if pack.is_dir() and not pack.name.startswith("."):
                passed = run_preflight(pack, args.strict)
                if not passed:
                    all_passed = False
    else:
        pack_path = Path(args.pack_dir)
        if not pack_path.is_absolute():
            pack_path = REPO_ROOT / pack_path

        if not pack_path.exists():
            print(f"ERROR: Pack directory not found: {pack_path}")
            sys.exit(1)

        # If --title/--description provided, also check those
        result = CheckResult()
        if args.title or args.description:
            check_title_description(args.title, args.description, result)
            if result.errors:
                for msg in result.errors:
                    print(f"  FAIL: {msg}")
                all_passed = False

        all_passed = run_preflight(pack_path, args.strict) and all_passed

    # Summary
    print(f"{'=' * 60}")
    if all_passed:
        print("  ALL CHECKS PASSED")
    else:
        print("  SOME CHECKS FAILED — Review errors above before submitting to LINE")
    print(f"{'=' * 60}")

    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
