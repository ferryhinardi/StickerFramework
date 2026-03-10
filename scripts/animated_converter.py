#!/usr/bin/env python3
"""
Animated sticker converter for Telegram and LINE.

Three conversion pipelines:
  A) LottieAnimator  — Static PNG → animated TGS (Lottie gzip, ≤64 KB)
  B) VideoConverter   — Static PNG / GIF / MP4 → WebM VP9 video sticker (≤256 KB)
  C) APNGAnimator     — Static PNG → animated APNG for LINE (≤1 MB, 5-20 frames)

TGS approach for AI-generated / photographic stickers:
  - Embed the rasterised image as a base64 Lottie image asset
  - Animate transform properties (position, scale, rotation, opacity)
  - Gzip the resulting JSON (must stay ≤64 KB)

WebM VP9 approach:
  - Render animation frames via Pillow transforms
  - Pipe frames to ffmpeg  (-c:v libvpx-vp9 -pix_fmt yuva420p)
  - Verify output: ≤256 KB, ≤3 s, 512×512, VP9 codec, no audio

LINE APNG approach:
  - Render animation frames via Pillow transforms (reuses VideoConverter._render_frame)
  - Assemble frames into APNG using Pillow's save_all
  - Verify output: ≤1 MB, ≤4 s, 320×270, 5-20 frames, all frames distinct
"""

from __future__ import annotations

import base64
import gzip
import json
import logging
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# Ensure sibling scripts are importable regardless of CWD
_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from PIL import Image

from animation_presets import generate_keyframes

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Telegram limits (match telegram_publisher.py FORMAT_MAX_SIZE values)
# ---------------------------------------------------------------------------
TGS_MAX_BYTES = 64_000  # 64 KB compressed (Telegram API limit)
WEBM_MAX_BYTES = 256_000  # 256 KB (Telegram API limit)
STICKER_SIZE = 512  # px
LOTTIE_FPS = 60
LOTTIE_MAX_DURATION_SEC = 3
WEBM_FPS = 30
WEBM_MAX_DURATION_SEC = 3

FFMPEG_PATH = os.environ.get("FFMPEG_PATH", "ffmpeg")


# ═══════════════════════════════════════════════════════════════════════════
# A) LottieAnimator  —  PNG → TGS
# ═══════════════════════════════════════════════════════════════════════════


class LottieAnimator:
    """Convert static sticker PNGs into animated TGS (Lottie) files."""

    def png_to_tgs(
        self,
        png_path: str,
        output_path: str,
        animation_type: str = "bounce",
        duration_ms: int = 2000,
        loop: bool = True,
    ) -> Path:
        """
        Convert a static PNG sticker to animated TGS format.

        Steps:
          1. Load PNG, resize to 512×512 (with alpha)
          2. Encode image as base64 for Lottie embedding
          3. Generate animation keyframes from preset
          4. Build Lottie JSON with embedded image + keyframes
          5. Gzip compress → .tgs (must be ≤ 64 KB)

        Args:
            png_path:        Source PNG file (ideally 512×512 with transparency).
            output_path:     Destination .tgs file path.
            animation_type:  Preset name (bounce, shake, pulse, pop_in, spin, wave, float).
            duration_ms:     Animation duration in milliseconds (max 3000).
            loop:            Whether the animation loops.

        Returns:
            Path to the generated .tgs file.

        Raises:
            ValueError:  If output exceeds 64 KB or duration > 3 s.
            FileNotFoundError: If png_path does not exist.
        """
        png_path = Path(png_path)
        output_path = Path(output_path)
        if not png_path.exists():
            raise FileNotFoundError(f"Source PNG not found: {png_path}")

        duration_ms = min(duration_ms, LOTTIE_MAX_DURATION_SEC * 1000)
        duration_frames = max(1, int(LOTTIE_FPS * duration_ms / 1000))

        # 1. Load & resize
        img = Image.open(png_path).convert("RGBA")
        img = img.resize((STICKER_SIZE, STICKER_SIZE), Image.LANCZOS)

        # 2. Encode as base64 PNG
        import io

        buf = io.BytesIO()
        img.save(buf, format="PNG")
        image_data = buf.getvalue()

        # 3. Generate keyframes
        keyframes = generate_keyframes(animation_type, duration_frames)

        # 4. Build Lottie JSON
        lottie = self._build_lottie_json(
            image_data=image_data,
            w=STICKER_SIZE,
            h=STICKER_SIZE,
            keyframes=keyframes,
            duration_frames=duration_frames,
            fps=LOTTIE_FPS,
            loop=loop,
        )

        # 5. Compress to .tgs
        return self._compress_to_tgs(lottie, str(output_path))

    # -----------------------------------------------------------------------

    def _build_lottie_json(
        self,
        image_data: bytes,
        w: int,
        h: int,
        keyframes: list[dict],
        duration_frames: int,
        fps: int = 60,
        loop: bool = True,
    ) -> dict:
        """
        Build a complete Lottie JSON structure with an embedded PNG image.

        The image is stored as a base64-encoded asset.  A single layer
        references it and carries the animation keyframes on its transform
        (position, scale, rotation, opacity).
        """
        b64 = base64.b64encode(image_data).decode("ascii")

        # --- asset ---------------------------------------------------------
        asset = {
            "id": "img_0",
            "w": w,
            "h": h,
            "u": "",
            "p": f"data:image/png;base64,{b64}",
            "e": 1,  # embedded
        }

        # --- keyframe helpers ---------------------------------------------
        def _kf_value(values: list[tuple]) -> list[dict]:
            """Convert [(frame, value), ...] to Lottie keyframe array."""
            result = []
            for idx, (f, v) in enumerate(values):
                entry: dict = {"t": f}
                if isinstance(v, (list, tuple)):
                    entry["s"] = list(v)
                else:
                    entry["s"] = [v]
                # For all but the last keyframe, set end values
                if idx < len(values) - 1:
                    nv = values[idx + 1][1]
                    if isinstance(nv, (list, tuple)):
                        entry["e"] = list(nv)
                    else:
                        entry["e"] = [nv]
                result.append(entry)
            return result

        # Extract per-property keyframe lists
        scale_kf = [(kf["frame"], kf.get("scale", 1.0) * 100) for kf in keyframes]
        rot_kf = [(kf["frame"], kf.get("rotation", 0.0)) for kf in keyframes]
        opacity_kf = [(kf["frame"], kf.get("opacity", 1.0) * 100) for kf in keyframes]

        # Combine position x/y into [cx+x, cy+y] pairs
        cx, cy = w / 2, h / 2
        pos_kf = [
            (kf["frame"], [cx + kf.get("x", 0.0), cy + kf.get("y", 0.0)])
            for kf in keyframes
        ]

        # Down-sample keyframes to reduce JSON size (keep every Nth frame)
        step = max(1, len(keyframes) // 30)  # ~30 keyframes max for size
        pos_kf = pos_kf[::step]
        scale_kf = scale_kf[::step]
        rot_kf = rot_kf[::step]
        opacity_kf = opacity_kf[::step]

        # Ensure last keyframe is always included
        last = len(keyframes) - 1
        if pos_kf[-1][0] != last:
            kf_last = keyframes[-1]
            pos_kf.append(
                (last, [cx + kf_last.get("x", 0.0), cy + kf_last.get("y", 0.0)])
            )
            scale_kf.append((last, kf_last.get("scale", 1.0) * 100))
            rot_kf.append((last, kf_last.get("rotation", 0.0)))
            opacity_kf.append((last, kf_last.get("opacity", 1.0) * 100))

        # --- layer ---------------------------------------------------------
        layer = {
            "ddd": 0,
            "ind": 0,
            "ty": 2,  # image layer
            "nm": "sticker",
            "refId": "img_0",
            "sr": 1,
            "ks": {
                "o": {  # opacity
                    "a": 1,
                    "k": _kf_value(opacity_kf),
                },
                "r": {  # rotation
                    "a": 1,
                    "k": _kf_value(rot_kf),
                },
                "p": {  # position
                    "a": 1,
                    "k": _kf_value(pos_kf),
                },
                "a": {  # anchor point (center)
                    "a": 0,
                    "k": [w / 2, h / 2, 0],
                },
                "s": {  # scale (uniform x,y)
                    "a": 1,
                    "k": _kf_value([(f, [v, v]) for f, v in scale_kf]),
                },
            },
            "ao": 0,
            "ip": 0,
            "op": duration_frames,
            "st": 0,
            "bm": 0,
        }

        # --- root ----------------------------------------------------------
        lottie = {
            "v": "5.7.4",
            "fr": fps,
            "ip": 0,
            "op": duration_frames,
            "w": w,
            "h": h,
            "nm": "sticker",
            "ddd": 0,
            "assets": [asset],
            "layers": [layer],
        }

        return lottie

    # -----------------------------------------------------------------------

    def _compress_to_tgs(self, lottie_json: dict, output_path: str) -> Path:
        """
        Gzip compress Lottie JSON to .tgs file.

        Raises ValueError if the result exceeds 64 KB.
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Compact JSON — no extra whitespace
        raw = json.dumps(lottie_json, separators=(",", ":")).encode("utf-8")
        compressed = gzip.compress(raw, compresslevel=9)

        if len(compressed) > TGS_MAX_BYTES:
            # Try reducing image quality: re-encode the base64 asset as JPEG
            compressed = self._recompress_with_jpeg(lottie_json)
            if len(compressed) > TGS_MAX_BYTES:
                raise ValueError(
                    f"TGS file is {len(compressed):,} bytes, exceeds "
                    f"{TGS_MAX_BYTES:,} byte limit. Try a simpler animation "
                    f"or smaller source image."
                )

        output_path.write_bytes(compressed)
        logger.info(
            "Created TGS: %s (%d bytes, %.1f%% of limit)",
            output_path,
            len(compressed),
            len(compressed) / TGS_MAX_BYTES * 100,
        )
        return output_path

    def _recompress_with_jpeg(self, lottie_json: dict) -> bytes:
        """
        Attempt to shrink the embedded image by converting PNG → JPEG.

        JPEG is significantly smaller but drops the alpha channel.
        This is a last-resort size reduction.
        """
        import io

        for asset in lottie_json.get("assets", []):
            p = asset.get("p", "")
            if p.startswith("data:image/png;base64,"):
                b64_data = p.split(",", 1)[1]
                png_bytes = base64.b64decode(b64_data)
                img = Image.open(io.BytesIO(png_bytes)).convert("RGBA")

                # Composite onto white background (JPEG has no alpha)
                bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
                composite = Image.alpha_composite(bg, img).convert("RGB")

                for quality in (60, 40, 20):
                    buf = io.BytesIO()
                    composite.save(buf, format="JPEG", quality=quality)
                    jpg_b64 = base64.b64encode(buf.getvalue()).decode("ascii")
                    asset["p"] = f"data:image/jpeg;base64,{jpg_b64}"

                    raw = json.dumps(lottie_json, separators=(",", ":")).encode("utf-8")
                    compressed = gzip.compress(raw, compresslevel=9)
                    if len(compressed) <= TGS_MAX_BYTES:
                        return compressed

                # Return best effort even if still too large
                raw = json.dumps(lottie_json, separators=(",", ":")).encode("utf-8")
                return gzip.compress(raw, compresslevel=9)

        raw = json.dumps(lottie_json, separators=(",", ":")).encode("utf-8")
        return gzip.compress(raw, compresslevel=9)


# ═══════════════════════════════════════════════════════════════════════════
# B) VideoConverter  —  PNG / GIF / MP4 → WebM VP9
# ═══════════════════════════════════════════════════════════════════════════


class VideoConverter:
    """Convert images/videos to Telegram video sticker format (WebM VP9)."""

    def __init__(self, ffmpeg_path: str | None = None):
        self.ffmpeg = ffmpeg_path or FFMPEG_PATH
        self._check_ffmpeg()

    def _check_ffmpeg(self) -> None:
        """Verify ffmpeg is available."""
        path = shutil.which(self.ffmpeg)
        if path is None:
            raise RuntimeError(
                f"ffmpeg not found at '{self.ffmpeg}'. Install ffmpeg or set "
                f"FFMPEG_PATH in .env"
            )
        logger.debug("Using ffmpeg: %s", path)

    # -----------------------------------------------------------------------
    # Public API
    # -----------------------------------------------------------------------

    def png_to_webm(
        self,
        png_path: str,
        output_path: str,
        animation_type: str = "bounce",
        duration_sec: float = 2.0,
        fps: int = WEBM_FPS,
    ) -> Path:
        """
        Convert static PNG to animated WebM video sticker.

        Steps:
          1. Load PNG, resize to 512×512 (RGBA)
          2. Generate animation keyframes
          3. Render each frame by applying transforms
          4. Pipe frames to ffmpeg → WebM VP9
          5. Verify output meets Telegram limits

        Returns:
            Path to the generated .webm file.
        """
        png_path = Path(png_path)
        output_path = Path(output_path)
        if not png_path.exists():
            raise FileNotFoundError(f"Source PNG not found: {png_path}")

        output_path.parent.mkdir(parents=True, exist_ok=True)
        duration_sec = min(duration_sec, WEBM_MAX_DURATION_SEC)
        total_frames = max(1, int(fps * duration_sec))

        # 1. Load & resize
        img = Image.open(png_path).convert("RGBA")
        img = img.resize((STICKER_SIZE, STICKER_SIZE), Image.LANCZOS)

        # 2. Keyframes
        keyframes = generate_keyframes(animation_type, total_frames)

        # 3. Render frames to temp directory
        with tempfile.TemporaryDirectory(prefix="sticker_frames_") as tmpdir:
            for i, kf in enumerate(keyframes):
                frame = self._render_frame(img, kf)
                frame.save(os.path.join(tmpdir, f"{i:04d}.png"), format="PNG")

            # 4. ffmpeg encode
            pattern = os.path.join(tmpdir, "%04d.png")
            self._encode_webm(pattern, str(output_path), fps, duration_sec)

        # 5. Verify
        self._verify_webm(str(output_path))
        return output_path

    def gif_to_webm(self, gif_path: str, output_path: str) -> Path:
        """
        Convert animated GIF to WebM VP9 video sticker.

        Extracts frames from GIF, resizes to 512×512, re-encodes as WebM.
        """
        gif_path = Path(gif_path)
        output_path = Path(output_path)
        if not gif_path.exists():
            raise FileNotFoundError(f"Source GIF not found: {gif_path}")

        output_path.parent.mkdir(parents=True, exist_ok=True)

        # ffmpeg can handle GIF → WebM directly
        cmd = [
            self.ffmpeg,
            "-y",
            "-i",
            str(gif_path),
            "-c:v",
            "libvpx-vp9",
            "-pix_fmt",
            "yuva420p",
            "-b:v",
            "400k",
            "-minrate",
            "100k",
            "-maxrate",
            "500k",
            "-an",  # no audio
            "-t",
            str(WEBM_MAX_DURATION_SEC),
            "-vf",
            f"scale={STICKER_SIZE}:{STICKER_SIZE}:force_original_aspect_ratio=decrease,"
            f"pad={STICKER_SIZE}:{STICKER_SIZE}:(ow-iw)/2:(oh-ih)/2:color=0x00000000",
            str(output_path),
        ]
        self._run_ffmpeg(cmd)
        self._verify_webm(str(output_path))
        return output_path

    def mp4_to_webm(self, mp4_path: str, output_path: str) -> Path:
        """
        Convert MP4 video to WebM VP9 video sticker.

        Re-encodes with VP9, strips audio, clips to 3 s, resizes to 512×512.
        """
        mp4_path = Path(mp4_path)
        output_path = Path(output_path)
        if not mp4_path.exists():
            raise FileNotFoundError(f"Source MP4 not found: {mp4_path}")

        output_path.parent.mkdir(parents=True, exist_ok=True)

        cmd = [
            self.ffmpeg,
            "-y",
            "-i",
            str(mp4_path),
            "-c:v",
            "libvpx-vp9",
            "-pix_fmt",
            "yuva420p",
            "-b:v",
            "400k",
            "-minrate",
            "100k",
            "-maxrate",
            "500k",
            "-an",
            "-t",
            str(WEBM_MAX_DURATION_SEC),
            "-vf",
            f"scale={STICKER_SIZE}:{STICKER_SIZE}:force_original_aspect_ratio=decrease,"
            f"pad={STICKER_SIZE}:{STICKER_SIZE}:(ow-iw)/2:(oh-ih)/2:color=0x00000000",
            str(output_path),
        ]
        self._run_ffmpeg(cmd)
        self._verify_webm(str(output_path))
        return output_path

    # -----------------------------------------------------------------------
    # Internal helpers
    # -----------------------------------------------------------------------

    @staticmethod
    def _render_frame(base_img: Image.Image, kf: dict) -> Image.Image:
        """
        Apply a single keyframe's transform to the base image.

        Transforms applied on a transparent 512×512 canvas:
          - translate (x, y)
          - scale (uniform)
          - rotate (degrees)
          - opacity
        """
        size = base_img.size[0]  # 512
        canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))

        # Scale
        s = max(0.01, kf.get("scale", 1.0))
        new_size = int(size * s)
        if new_size < 1:
            return canvas
        scaled = base_img.resize((new_size, new_size), Image.LANCZOS)

        # Rotate
        rotation = kf.get("rotation", 0.0)
        if abs(rotation) > 0.01:
            scaled = scaled.rotate(-rotation, resample=Image.BICUBIC, expand=True)

        # Position on canvas (centered + offset)
        ox = kf.get("x", 0.0)
        oy = kf.get("y", 0.0)
        paste_x = int((size - scaled.size[0]) / 2 + ox)
        paste_y = int((size - scaled.size[1]) / 2 + oy)

        # Opacity
        opacity = max(0.0, min(1.0, kf.get("opacity", 1.0)))
        if opacity < 1.0:
            # Multiply alpha channel
            r, g, b, a = scaled.split()
            a = a.point(lambda p: int(p * opacity))
            scaled = Image.merge("RGBA", (r, g, b, a))

        canvas.paste(scaled, (paste_x, paste_y), scaled)
        return canvas

    def _encode_webm(
        self,
        frame_pattern: str,
        output_path: str,
        fps: int,
        duration_sec: float,
    ) -> None:
        """Encode PNG frame sequence to WebM VP9 via ffmpeg."""
        cmd = [
            self.ffmpeg,
            "-y",
            "-framerate",
            str(fps),
            "-i",
            frame_pattern,
            "-c:v",
            "libvpx-vp9",
            "-pix_fmt",
            "yuva420p",
            "-b:v",
            "400k",
            "-minrate",
            "100k",
            "-maxrate",
            "500k",
            "-an",
            "-t",
            str(min(duration_sec, WEBM_MAX_DURATION_SEC)),
            "-s",
            f"{STICKER_SIZE}x{STICKER_SIZE}",
            output_path,
        ]
        self._run_ffmpeg(cmd)

    def _run_ffmpeg(self, cmd: list[str]) -> None:
        """Execute an ffmpeg command, raise on failure."""
        logger.debug("ffmpeg command: %s", " ".join(cmd))
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"ffmpeg failed (exit {result.returncode}):\n{result.stderr[-2000:]}"
            )

    def _verify_webm(self, path: str) -> dict:
        """
        Verify a WebM file meets Telegram video sticker requirements.

        Checks:
          - File size ≤ 256 KB
          - Duration ≤ 3 s
          - Resolution = 512×512
          - Codec = VP9
          - No audio stream

        Returns:
            Info dict with size, duration, width, height, codec.

        Raises:
            ValueError on any failed check.
        """
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"WebM not found: {path}")

        file_size = p.stat().st_size
        if file_size > WEBM_MAX_BYTES:
            raise ValueError(
                f"WebM is {file_size:,} bytes, exceeds {WEBM_MAX_BYTES:,} byte limit"
            )

        # Probe with ffprobe (derive path from ffmpeg binary basename only)
        ffmpeg_path = Path(self.ffmpeg)
        ffprobe_path = str(
            ffmpeg_path.parent / ffmpeg_path.name.replace("ffmpeg", "ffprobe")
        )
        probe_cmd = [
            ffprobe_path,
            "-v",
            "quiet",
            "-print_format",
            "json",
            "-show_streams",
            "-show_format",
            str(path),
        ]
        try:
            result = subprocess.run(
                probe_cmd,
                capture_output=True,
                text=True,
                timeout=30,
            )
            probe = json.loads(result.stdout)
        except (subprocess.SubprocessError, json.JSONDecodeError) as exc:
            logger.warning("ffprobe failed, skipping deep verification: %s", exc)
            return {"size": file_size, "verified": False}

        info: dict = {"size": file_size, "verified": True}

        # Parse streams
        video_stream = None
        has_audio = False
        for stream in probe.get("streams", []):
            if stream.get("codec_type") == "video":
                video_stream = stream
            elif stream.get("codec_type") == "audio":
                has_audio = True

        if has_audio:
            raise ValueError("WebM contains audio stream (not allowed)")

        if video_stream:
            info["codec"] = video_stream.get("codec_name", "unknown")
            info["width"] = int(video_stream.get("width", 0))
            info["height"] = int(video_stream.get("height", 0))

            duration_str = video_stream.get("duration") or probe.get("format", {}).get(
                "duration", "0"
            )
            info["duration"] = float(duration_str)

            if info["codec"] != "vp9":
                raise ValueError(f"Expected VP9 codec, got '{info['codec']}'")
            if info["duration"] > WEBM_MAX_DURATION_SEC + 0.1:
                raise ValueError(
                    f"Duration {info['duration']:.1f}s exceeds {WEBM_MAX_DURATION_SEC}s limit"
                )
            # Width/height check — allow slight deviation from ffmpeg scaling
            if (
                abs(info["width"] - STICKER_SIZE) > 2
                or abs(info["height"] - STICKER_SIZE) > 2
            ):
                raise ValueError(
                    f"Resolution {info['width']}x{info['height']} != "
                    f"{STICKER_SIZE}x{STICKER_SIZE}"
                )

        logger.info(
            "Verified WebM: %s (%d bytes, %.1fs)",
            path,
            file_size,
            info.get("duration", 0),
        )
        return info


# ═══════════════════════════════════════════════════════════════════════════
# C) APNGAnimator  —  PNG → APNG (LINE animated stickers)
# ═══════════════════════════════════════════════════════════════════════════

# LINE animated sticker limits
LINE_APNG_MAX_BYTES = 1_000_000  # 1 MB
LINE_APNG_WIDTH = 320
LINE_APNG_HEIGHT = 270
LINE_APNG_MIN_FRAMES = 5
LINE_APNG_MAX_FRAMES = 20
LINE_APNG_MAX_LOOPS = 4
LINE_APNG_MAX_DURATION_SEC = 4
LINE_APNG_FPS = 10  # 10 fps × 20 frames = 2 sec, good default


class APNGAnimator:
    """
    Convert static sticker PNGs into animated APNG files for LINE.

    LINE animated sticker requirements:
      - Format: APNG (with .png extension)
      - Dimensions: up to 320×270, one side must be ≥270px
      - Frame count: 5–20 frames
      - Loops: 1–4
      - Max playback: 4 seconds
      - Max file size: 1 MB
      - All frames must be visually distinct

    Uses Pillow's native APNG support (save_all=True) for assembly
    and the same _render_frame() logic as VideoConverter for transforms.
    """

    def png_to_apng(
        self,
        png_path: str,
        output_path: str,
        animation_type: str = "bounce",
        duration_ms: int = 2000,
        loop: int = 0,
        num_frames: int | None = None,
    ) -> Path:
        """
        Convert static PNG to animated APNG for LINE.

        Args:
            png_path: Path to source PNG (any resolution).
            output_path: Path for output .png (APNG) file.
            animation_type: Animation preset name (bounce, heartbeat, etc.).
            duration_ms: Total animation duration in milliseconds (max 4000).
            loop: Number of loops. 0 = infinite, 1-4 for LINE compliance.
                  LINE requires 1-4 loops; 0 will be clamped to 1 at verify.
            num_frames: Number of frames to render. If None, auto-calculated
                        from duration and fps (clamped to 5-20).

        Returns:
            Path to the generated APNG file.
        """
        png_path = Path(png_path)
        output_path = Path(output_path)
        if not png_path.exists():
            raise FileNotFoundError(f"Source PNG not found: {png_path}")

        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Clamp duration to LINE limit
        duration_ms = min(duration_ms, LINE_APNG_MAX_DURATION_SEC * 1000)
        duration_sec = duration_ms / 1000.0

        # Calculate frame count
        if num_frames is None:
            num_frames = max(
                LINE_APNG_MIN_FRAMES,
                min(LINE_APNG_MAX_FRAMES, int(LINE_APNG_FPS * duration_sec)),
            )
        num_frames = max(LINE_APNG_MIN_FRAMES, min(LINE_APNG_MAX_FRAMES, num_frames))

        per_frame_ms = int(duration_ms / num_frames)

        # Clamp loop count for LINE compliance (1-4; 0=infinite is non-compliant)
        if loop <= 0 or loop > LINE_APNG_MAX_LOOPS:
            loop = 1

        logger.info(
            "APNG: %s → %s | preset=%s duration=%dms frames=%d loop=%d",
            png_path.name,
            output_path.name,
            animation_type,
            duration_ms,
            num_frames,
            loop,
        )

        # 1. Load source image and resize to LINE dimensions (320×270)
        img = Image.open(png_path).convert("RGBA")
        img = self._resize_to_line(img)

        # 2. Generate keyframes from animation preset
        keyframes = generate_keyframes(animation_type, num_frames)

        # 3. Render individual frames
        frames = []
        for kf in keyframes:
            frame = self._render_frame(img, kf)
            frames.append(frame)

        # 4. Ensure all frames are visually distinct (LINE requirement)
        frames = self._ensure_distinct_frames(frames)

        # 5. Assemble APNG using Pillow
        self._save_apng(frames, output_path, per_frame_ms, loop)

        # 6. Verify file size and optimize if needed
        self._verify_and_optimize(frames, output_path, per_frame_ms, loop)

        file_size = output_path.stat().st_size
        logger.info(
            "APNG created: %s (%s bytes, %d frames, %d loops)",
            output_path,
            f"{file_size:,}",
            len(frames),
            loop,
        )
        return output_path

    # -----------------------------------------------------------------------
    # Internal helpers
    # -----------------------------------------------------------------------

    @staticmethod
    def _resize_to_line(img: Image.Image) -> Image.Image:
        """
        Resize image to fit within LINE's 320×270 canvas.

        Maintains aspect ratio, ensures at least one side is 270px,
        and centers on a transparent 320×270 canvas.
        """
        target_w, target_h = LINE_APNG_WIDTH, LINE_APNG_HEIGHT

        # Scale to fit within bounds while maintaining aspect ratio
        w, h = img.size
        scale = min(target_w / w, target_h / h)
        new_w = max(1, int(w * scale))
        new_h = max(1, int(h * scale))
        img = img.resize((new_w, new_h), Image.LANCZOS)

        # Center on transparent canvas
        canvas = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
        offset_x = (target_w - new_w) // 2
        offset_y = (target_h - new_h) // 2
        canvas.paste(img, (offset_x, offset_y), img)
        return canvas

    @staticmethod
    def _render_frame(base_img: Image.Image, kf: dict) -> Image.Image:
        """
        Apply a single keyframe's transform to the base image.

        Same logic as VideoConverter._render_frame() but operates
        on 320×270 canvas instead of 512×512.
        """
        w, h = base_img.size  # 320, 270
        canvas = Image.new("RGBA", (w, h), (0, 0, 0, 0))

        # Scale
        s = max(0.01, kf.get("scale", 1.0))
        new_w = max(1, int(w * s))
        new_h = max(1, int(h * s))
        scaled = base_img.resize((new_w, new_h), Image.LANCZOS)

        # Rotate
        rotation = kf.get("rotation", 0.0)
        if abs(rotation) > 0.01:
            scaled = scaled.rotate(-rotation, resample=Image.BICUBIC, expand=True)

        # Position on canvas (centered + offset)
        ox = kf.get("x", 0.0)
        oy = kf.get("y", 0.0)
        paste_x = int((w - scaled.size[0]) / 2 + ox)
        paste_y = int((h - scaled.size[1]) / 2 + oy)

        # Opacity
        opacity = max(0.0, min(1.0, kf.get("opacity", 1.0)))
        if opacity < 1.0:
            r, g, b, a = scaled.split()
            a = a.point(lambda p: int(p * opacity))
            scaled = Image.merge("RGBA", (r, g, b, a))

        canvas.paste(scaled, (paste_x, paste_y), scaled)
        return canvas

    @staticmethod
    def _ensure_distinct_frames(frames: list[Image.Image]) -> list[Image.Image]:
        """
        Ensure all frames are visually distinct (LINE upload rejects
        identical consecutive frames). Adds a 1px transparent nudge
        to any frame that is identical to its predecessor.
        """
        import hashlib

        distinct = [frames[0]]
        prev_hash = hashlib.md5(frames[0].tobytes()).hexdigest()

        for frame in frames[1:]:
            curr_hash = hashlib.md5(frame.tobytes()).hexdigest()
            if curr_hash == prev_hash:
                # Nudge: shift 1px right to create a visual difference
                nudged = Image.new("RGBA", frame.size, (0, 0, 0, 0))
                nudged.paste(frame, (1, 0), frame)
                distinct.append(nudged)
                curr_hash = hashlib.md5(nudged.tobytes()).hexdigest()
            else:
                distinct.append(frame)
            prev_hash = curr_hash

        return distinct

    @staticmethod
    def _save_apng(
        frames: list[Image.Image],
        output_path: Path,
        per_frame_ms: int,
        loop: int,
    ) -> None:
        """Assemble frames into APNG using Pillow's native support."""
        frames[0].save(
            str(output_path),
            format="PNG",
            save_all=True,
            append_images=frames[1:],
            duration=per_frame_ms,
            loop=loop,
            optimize=True,
        )

    def _verify_and_optimize(
        self,
        frames: list[Image.Image],
        output_path: Path,
        per_frame_ms: int,
        loop: int,
    ) -> None:
        """
        Verify APNG meets LINE size limit. If over 1 MB, attempt:
          1. Reduce to 256 colors (per frame)
          2. Reduce frame count to minimum (5)
        """
        file_size = output_path.stat().st_size
        if file_size <= LINE_APNG_MAX_BYTES:
            return

        logger.warning(
            "APNG too large (%s bytes > %s). Attempting color quantization...",
            f"{file_size:,}",
            f"{LINE_APNG_MAX_BYTES:,}",
        )

        # Strategy 1: quantize to 256 colors per frame
        quantized = [f.quantize(colors=256, method=2).convert("RGBA") for f in frames]
        self._save_apng(quantized, output_path, per_frame_ms, loop)
        file_size = output_path.stat().st_size
        if file_size <= LINE_APNG_MAX_BYTES:
            logger.info("Quantization succeeded: %s bytes", f"{file_size:,}")
            return

        # Strategy 2: reduce frame count to minimum
        if len(frames) > LINE_APNG_MIN_FRAMES:
            logger.warning(
                "Still too large. Reducing to %d frames...", LINE_APNG_MIN_FRAMES
            )
            step = max(1, len(quantized) // LINE_APNG_MIN_FRAMES)
            reduced = quantized[::step][:LINE_APNG_MIN_FRAMES]
            new_per_frame = int(per_frame_ms * len(frames) / len(reduced))
            self._save_apng(reduced, output_path, new_per_frame, loop)
            file_size = output_path.stat().st_size
            if file_size <= LINE_APNG_MAX_BYTES:
                logger.info(
                    "Frame reduction succeeded: %s bytes, %d frames",
                    f"{file_size:,}",
                    len(reduced),
                )
                return

        logger.error(
            "APNG still exceeds 1 MB (%s bytes) after optimization. "
            "Consider using a simpler animation preset or smaller source image.",
            f"{file_size:,}",
        )


# ═══════════════════════════════════════════════════════════════════════════
# CLI entry point
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import argparse

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    parser = argparse.ArgumentParser(
        description="Convert stickers to animated formats (Telegram TGS/WebM, LINE APNG).",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # --- tgs sub-command ---
    tgs_p = sub.add_parser("tgs", help="PNG → TGS (animated Lottie)")
    tgs_p.add_argument("input", help="Source PNG file")
    tgs_p.add_argument("output", help="Output .tgs file")
    tgs_p.add_argument(
        "--animation", default="bounce", help="Preset name (default: bounce)"
    )
    tgs_p.add_argument(
        "--duration", type=int, default=2000, help="Duration ms (default: 2000)"
    )
    tgs_p.add_argument("--no-loop", action="store_true", help="Disable looping")

    # --- webm sub-command ---
    webm_p = sub.add_parser("webm", help="PNG/GIF/MP4 → WebM VP9")
    webm_p.add_argument("input", help="Source file (PNG, GIF, or MP4)")
    webm_p.add_argument("output", help="Output .webm file")
    webm_p.add_argument(
        "--animation", default="bounce", help="Preset name for PNG (default: bounce)"
    )
    webm_p.add_argument(
        "--duration",
        type=float,
        default=2.0,
        help="Duration sec for PNG (default: 2.0)",
    )
    webm_p.add_argument("--fps", type=int, default=30, help="Frame rate (default: 30)")

    # --- apng sub-command ---
    apng_p = sub.add_parser("apng", help="PNG → APNG (LINE animated sticker)")
    apng_p.add_argument("input", help="Source PNG file")
    apng_p.add_argument("output", help="Output .png (APNG) file")
    apng_p.add_argument(
        "--animation", default="bounce", help="Preset name (default: bounce)"
    )
    apng_p.add_argument(
        "--duration",
        type=int,
        default=2000,
        help="Duration ms (default: 2000, max: 4000)",
    )
    apng_p.add_argument(
        "--frames",
        type=int,
        default=None,
        help="Frame count (default: auto, range: 5-20)",
    )
    apng_p.add_argument(
        "--loops", type=int, default=1, help="Loop count (default: 1, LINE allows 1-4)"
    )

    args = parser.parse_args()

    if args.command == "tgs":
        animator = LottieAnimator()
        out = animator.png_to_tgs(
            args.input,
            args.output,
            animation_type=args.animation,
            duration_ms=args.duration,
            loop=not args.no_loop,
        )
        print(f"Created TGS: {out} ({out.stat().st_size:,} bytes)")

    elif args.command == "webm":
        converter = VideoConverter()
        ext = Path(args.input).suffix.lower()
        if ext == ".gif":
            out = converter.gif_to_webm(args.input, args.output)
        elif ext == ".mp4":
            out = converter.mp4_to_webm(args.input, args.output)
        else:
            out = converter.png_to_webm(
                args.input,
                args.output,
                animation_type=args.animation,
                duration_sec=args.duration,
                fps=args.fps,
            )
        print(f"Created WebM: {out} ({out.stat().st_size:,} bytes)")

    elif args.command == "apng":
        animator = APNGAnimator()
        out = animator.png_to_apng(
            args.input,
            args.output,
            animation_type=args.animation,
            duration_ms=args.duration,
            num_frames=args.frames,
            loop=args.loops,
        )
        print(f"Created APNG: {out} ({out.stat().st_size:,} bytes)")
