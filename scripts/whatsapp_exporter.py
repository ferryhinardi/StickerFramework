#!/usr/bin/env python3
"""
WhatsApp Native Sticker Exporter.

Prepares sticker packs in the exact format required by WhatsApp's
ContentProvider protocol and optionally pushes them to the API server
for dynamic loading by the Android app.

Creates output in the WhatsApp sticker pack structure:
    <output_dir>/<pack_id>/
    +-- contents.json           <- WhatsApp metadata
    +-- tray_icon.webp          <- 96x96 tray icon
    +-- 01_happy.webp           <- Sticker files (512x512)
    +-- 02_love.webp
    +-- ...

Usage:
    # Export pack to local directory (for bundling in APK assets/)
    python whatsapp_exporter.py export <pack_dir> \\
        --output whatsapp-sticker-app/app/src/main/assets/

    # Export and push to remote server
    python whatsapp_exporter.py push <pack_dir> \\
        --server https://stickers.yourdomain.com

    # Validate a pack against WhatsApp requirements
    python whatsapp_exporter.py validate <pack_dir>
"""

import argparse
import json
import os
import shutil
import sys
from pathlib import Path

from PIL import Image

# ---------------------------------------------------------------------------
# Ensure sibling scripts are importable regardless of CWD
# ---------------------------------------------------------------------------
_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

REPO_ROOT = _SCRIPTS_DIR.parent


class WhatsAppExporter:
    """Export sticker packs in WhatsApp ContentProvider format."""

    # WhatsApp requirements (strict)
    MAX_STICKERS_PER_PACK = 30
    MIN_STICKERS_PER_PACK = 3
    STICKER_SIZE = (512, 512)
    STICKER_MAX_KB = 100
    TRAY_SIZE = (96, 96)
    TRAY_MAX_KB = 50
    STICKER_FORMAT = "WEBP"

    def export_pack(
        self,
        pack_config: dict,
        sticker_dir: str,
        output_dir: str,
    ) -> Path:
        """
        Export a complete WhatsApp sticker pack.

        Args:
            pack_config: Pack configuration dict (from pack_config.py).
            sticker_dir: Directory containing processed whatsapp_native stickers.
            output_dir: Base output directory (pack subdir is created inside).

        Returns:
            Path to the created pack directory.
        """
        pack_id = pack_config["pack_id"]
        pack_dir = Path(output_dir) / pack_id
        pack_dir.mkdir(parents=True, exist_ok=True)

        sticker_src = Path(sticker_dir)
        if not sticker_src.exists():
            raise FileNotFoundError(f"Sticker directory not found: {sticker_src}")

        # --- Collect & copy sticker files -----------------------------------
        sticker_files = sorted(sticker_src.glob("*.webp"))
        # Exclude tray icon from sticker list if it ended up here
        sticker_files = [f for f in sticker_files if "tray" not in f.stem.lower()]

        if len(sticker_files) < self.MIN_STICKERS_PER_PACK:
            raise ValueError(
                f"Need at least {self.MIN_STICKERS_PER_PACK} stickers, "
                f"found {len(sticker_files)}"
            )
        if len(sticker_files) > self.MAX_STICKERS_PER_PACK:
            print(
                f"  WARNING: {len(sticker_files)} stickers found, "
                f"truncating to {self.MAX_STICKERS_PER_PACK}"
            )
            sticker_files = sticker_files[: self.MAX_STICKERS_PER_PACK]

        copied_stickers: list[dict] = []
        for src_file in sticker_files:
            dst_file = pack_dir / src_file.name
            shutil.copy2(src_file, dst_file)
            # Validate size while copying
            size_kb = dst_file.stat().st_size / 1024
            if size_kb > self.STICKER_MAX_KB:
                print(
                    f"  WARNING: {src_file.name} is {size_kb:.1f}KB "
                    f"(max {self.STICKER_MAX_KB}KB) — re-compressing"
                )
                self._recompress(dst_file, self.STICKER_MAX_KB)

            # Map sticker to emoji from config
            emoji = self._find_emoji(pack_config, src_file.stem)
            copied_stickers.append(
                {
                    "image_file": src_file.name,
                    "emojis": [emoji],
                }
            )

        # --- Tray icon ------------------------------------------------------
        tray_icon = self._prepare_tray_icon(pack_config, sticker_src, pack_dir)

        # --- contents.json --------------------------------------------------
        # Build pack metadata; omit optional URL fields if not configured
        # to avoid stricter SDK validation failures on empty strings.
        pack_entry = {
            "identifier": pack_id,
            "name": pack_config["pack_name"],
            "publisher": pack_config.get("publisher", "Sticker Studio"),
            "tray_image_file": tray_icon.name,
            "image_data_version": "1",
            "avoid_cache": False,
            "stickers": copied_stickers,
        }
        # Only include optional URL fields when they have real values
        for key in (
            "publisher_website",
            "privacy_policy_website",
            "license_agreement_website",
        ):
            value = pack_config.get(key, "")
            if value:
                pack_entry[key] = value

        contents = {"sticker_packs": [pack_entry]}
        contents_path = pack_dir / "contents.json"
        contents_path.write_text(json.dumps(contents, indent=2))

        print(f"  Exported {len(copied_stickers)} stickers to {pack_dir}")
        return pack_dir

    def validate_pack(self, pack_dir: str) -> list[str]:
        """Validate pack meets all WhatsApp requirements. Returns list of errors."""
        errors: list[str] = []
        pd = Path(pack_dir)

        # Check contents.json exists
        contents_path = pd / "contents.json"
        if not contents_path.exists():
            errors.append("Missing contents.json")
            return errors

        try:
            data = json.loads(contents_path.read_text())
        except json.JSONDecodeError as e:
            errors.append(f"Invalid contents.json: {e}")
            return errors

        packs = data.get("sticker_packs", [])
        if not packs:
            errors.append("contents.json has no sticker_packs")
            return errors

        pack = packs[0]

        # Required metadata fields
        for field in ("identifier", "name", "publisher", "tray_image_file"):
            if not pack.get(field):
                errors.append(f"Missing required field: {field}")

        stickers = pack.get("stickers", [])

        # Sticker count
        if len(stickers) < self.MIN_STICKERS_PER_PACK:
            errors.append(
                f"Too few stickers: {len(stickers)} (min {self.MIN_STICKERS_PER_PACK})"
            )
        if len(stickers) > self.MAX_STICKERS_PER_PACK:
            errors.append(
                f"Too many stickers: {len(stickers)} (max {self.MAX_STICKERS_PER_PACK})"
            )

        # Validate tray icon
        tray_file = pd / pack.get("tray_image_file", "")
        if tray_file.exists():
            try:
                img = Image.open(tray_file)
                if img.size != self.TRAY_SIZE:
                    errors.append(f"Tray icon is {img.size}, must be {self.TRAY_SIZE}")
                img.close()
            except Exception as e:
                errors.append(f"Cannot open tray icon: {e}")
            size_kb = tray_file.stat().st_size / 1024
            if size_kb > self.TRAY_MAX_KB:
                errors.append(f"Tray icon {size_kb:.1f}KB exceeds {self.TRAY_MAX_KB}KB")
        else:
            errors.append(f"Tray icon file not found: {tray_file.name}")

        # Validate each sticker
        for entry in stickers:
            fname = entry.get("image_file", "")
            fpath = pd / fname
            if not fpath.exists():
                errors.append(f"Sticker file missing: {fname}")
                continue
            try:
                img = Image.open(fpath)
                if img.size != self.STICKER_SIZE:
                    errors.append(
                        f"{fname}: size {img.size}, must be {self.STICKER_SIZE}"
                    )
                img.close()
            except Exception as e:
                errors.append(f"{fname}: cannot open — {e}")
            size_kb = fpath.stat().st_size / 1024
            if size_kb > self.STICKER_MAX_KB:
                errors.append(
                    f"{fname}: {size_kb:.1f}KB exceeds {self.STICKER_MAX_KB}KB"
                )

            # Emoji check
            emojis = entry.get("emojis", [])
            if not emojis:
                errors.append(f"{fname}: no emoji association")

        return errors

    def push_to_server(
        self, pack_dir: str, server_url: str, api_key: str | None = None
    ):
        """Upload pack to the WhatsApp sticker API server."""
        import requests

        pd = Path(pack_dir)
        contents_path = pd / "contents.json"
        if not contents_path.exists():
            raise FileNotFoundError(f"No contents.json in {pack_dir}")

        data = json.loads(contents_path.read_text())
        pack_meta = data["sticker_packs"][0]
        pack_id = pack_meta["identifier"]

        server_url = server_url.rstrip("/")
        headers: dict[str, str] = {}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        # Upload metadata via publish endpoint
        publish_url = f"{server_url}/api/v1/packs/{pack_id}/publish"
        print(f"  Pushing pack '{pack_id}' to {server_url} ...")

        # Collect file handles so we can close them after upload
        open_handles = []
        try:
            # Send contents.json and all sticker files as multipart
            contents_fh = contents_path.open("rb")
            open_handles.append(contents_fh)
            files_to_upload = [
                ("contents", ("contents.json", contents_fh, "application/json")),
            ]
            # Add tray icon
            tray_path = pd / pack_meta["tray_image_file"]
            if tray_path.exists():
                tray_fh = tray_path.open("rb")
                open_handles.append(tray_fh)
                files_to_upload.append(
                    ("files", (tray_path.name, tray_fh, "image/webp"))
                )
            # Add sticker files
            for sticker in pack_meta.get("stickers", []):
                fpath = pd / sticker["image_file"]
                if fpath.exists():
                    sticker_fh = fpath.open("rb")
                    open_handles.append(sticker_fh)
                    files_to_upload.append(
                        ("files", (fpath.name, sticker_fh, "image/webp"))
                    )

            resp = requests.post(publish_url, files=files_to_upload, headers=headers)
            resp.raise_for_status()
            # Guard against non-JSON responses (e.g. HTML 502 from proxy)
            content_type = resp.headers.get("Content-Type", "")
            if "application/json" in content_type:
                print(f"  Server responded: {resp.status_code} — {resp.json()}")
            else:
                print(f"  Server responded: {resp.status_code} — {resp.text[:200]}")
        finally:
            for fh in open_handles:
                fh.close()

    # -----------------------------------------------------------------------
    # Private helpers
    # -----------------------------------------------------------------------

    def _find_emoji(self, config: dict, sticker_stem: str) -> str:
        """Look up the emoji for a sticker by its stem name from pack config."""
        for s in config.get("stickers", []):
            if s["id"] == sticker_stem:
                return s.get("emoji", "\u2b50")
        # Fallback
        return "\u2b50"

    def _prepare_tray_icon(
        self, config: dict, sticker_src: Path, pack_dir: Path
    ) -> Path:
        """Find or generate the 96x96 tray icon."""
        # Look for an existing tray icon in whatsapp_native_tray output
        pack_id = config["pack_id"]
        tray_candidates = [
            sticker_src.parent / "whatsapp_native_tray" / "tray_icon.webp",
            sticker_src / "tray_icon.webp",
            REPO_ROOT
            / "packs"
            / pack_id
            / "final"
            / "whatsapp_tray"
            / "tray_icon.webp",
        ]
        for candidate in tray_candidates:
            if candidate.exists():
                dst = pack_dir / "tray_icon.webp"
                shutil.copy2(candidate, dst)
                size_kb = dst.stat().st_size / 1024
                if size_kb > self.TRAY_MAX_KB:
                    self._recompress(dst, self.TRAY_MAX_KB)
                return dst

        # Generate from first sticker
        first_sticker = sorted(sticker_src.glob("*.webp"))
        if not first_sticker:
            raise FileNotFoundError("No sticker files to create tray icon from")
        first_sticker = [f for f in first_sticker if "tray" not in f.stem.lower()]
        if not first_sticker:
            raise FileNotFoundError("No sticker files to create tray icon from")

        img = Image.open(first_sticker[0])
        img.thumbnail(self.TRAY_SIZE, Image.Resampling.LANCZOS)
        tray_path = pack_dir / "tray_icon.webp"
        img.save(tray_path, "WEBP", quality=80)
        img.close()

        size_kb = tray_path.stat().st_size / 1024
        if size_kb > self.TRAY_MAX_KB:
            self._recompress(tray_path, self.TRAY_MAX_KB)

        print(f"  Generated tray icon from {first_sticker[0].name}")
        return tray_path

    def _recompress(self, file_path: Path, max_kb: int):
        """Re-compress a WebP image to fit within size limit."""
        img = Image.open(file_path)
        quality = 80
        while quality >= 10:
            img.save(file_path, "WEBP", quality=quality)
            if file_path.stat().st_size / 1024 <= max_kb:
                break
            quality -= 10
        img.close()
        final_kb = file_path.stat().st_size / 1024
        if final_kb > max_kb:
            print(
                f"  WARNING: {file_path.name} still {final_kb:.1f}KB "
                f"after max recompression (limit {max_kb}KB)"
            )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="WhatsApp Native Sticker Exporter",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Export pack to local directory:
  python whatsapp_exporter.py export packs/pack01_emotions_v1/final/whatsapp_native \\
      --output whatsapp-sticker-app/app/src/main/assets/

  # Push to remote server:
  python whatsapp_exporter.py push packs/pack01_emotions_v1/final/whatsapp_native \\
      --server https://stickers.yourdomain.com

  # Validate an exported pack:
  python whatsapp_exporter.py validate output/pack01_emotions_v1/
""",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- export -------------------------------------------------------------
    sp_export = subparsers.add_parser("export", help="Export pack to local directory")
    sp_export.add_argument(
        "pack_dir", help="Directory with processed whatsapp_native stickers"
    )
    sp_export.add_argument(
        "--output",
        "-o",
        default=str(
            REPO_ROOT / "whatsapp-sticker-app" / "app" / "src" / "main" / "assets"
        ),
        help="Output base directory (default: Android app assets/)",
    )

    # --- push ---------------------------------------------------------------
    sp_push = subparsers.add_parser("push", help="Export and push pack to server")
    sp_push.add_argument(
        "pack_dir", help="Directory with processed whatsapp_native stickers"
    )
    sp_push.add_argument(
        "--server",
        "-s",
        default=os.environ.get("WHATSAPP_SERVER_URL", "http://localhost:8080"),
        help="Server URL (default: $WHATSAPP_SERVER_URL or http://localhost:8080)",
    )
    sp_push.add_argument("--api-key", default=os.environ.get("WHATSAPP_API_KEY"))
    sp_push.add_argument(
        "--output",
        "-o",
        default=str(REPO_ROOT / "output" / "whatsapp_native"),
        help="Local output directory before pushing",
    )

    # --- validate -----------------------------------------------------------
    sp_validate = subparsers.add_parser("validate", help="Validate an exported pack")
    sp_validate.add_argument("pack_dir", help="Exported pack directory to validate")

    args = parser.parse_args()
    exporter = WhatsAppExporter()

    if args.command == "export":
        from pack_config import PACK_CONFIG

        pack_dir = exporter.export_pack(PACK_CONFIG, args.pack_dir, args.output)
        errors = exporter.validate_pack(str(pack_dir))
        if errors:
            print("\n  Validation warnings:")
            for e in errors:
                print(f"    - {e}")
        else:
            print("  Validation passed!")

    elif args.command == "push":
        from pack_config import PACK_CONFIG

        pack_dir = exporter.export_pack(PACK_CONFIG, args.pack_dir, args.output)
        errors = exporter.validate_pack(str(pack_dir))
        if errors:
            print("\n  Validation errors (aborting push):")
            for e in errors:
                print(f"    - {e}")
            sys.exit(1)
        exporter.push_to_server(str(pack_dir), args.server, args.api_key)

    elif args.command == "validate":
        errors = exporter.validate_pack(args.pack_dir)
        if errors:
            print(f"\n  {len(errors)} validation error(s):")
            for e in errors:
                print(f"    - {e}")
            sys.exit(1)
        else:
            print("  Pack is valid!")


if __name__ == "__main__":
    main()
