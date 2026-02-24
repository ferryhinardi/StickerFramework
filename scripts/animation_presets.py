#!/usr/bin/env python3
"""
Animation preset keyframes for Lottie/video sticker generation.

Each preset returns a list of keyframe dicts with:
    - "frame": int (absolute frame number)
    - "x": float (horizontal offset from center, px)
    - "y": float (vertical offset from center, px)
    - "scale": float (1.0 = 100%)
    - "rotation": float (degrees)
    - "opacity": float (0.0-1.0)

Presets are designed for 512x512 Telegram stickers.
Default parameters produce subtle, appealing animations.
"""

from __future__ import annotations

import math
from typing import Callable


def _default_transform() -> dict:
    """Return a neutral (identity) transform dict."""
    return {"x": 0.0, "y": 0.0, "scale": 1.0, "rotation": 0.0, "opacity": 1.0}


def _lerp(a: float, b: float, t: float) -> float:
    """Linear interpolation between a and b."""
    return a + (b - a) * t


def _ease_out_bounce(t: float) -> float:
    """Bounce easing function (deceleration)."""
    if t < 1 / 2.75:
        return 7.5625 * t * t
    elif t < 2 / 2.75:
        t -= 1.5 / 2.75
        return 7.5625 * t * t + 0.75
    elif t < 2.5 / 2.75:
        t -= 2.25 / 2.75
        return 7.5625 * t * t + 0.9375
    else:
        t -= 2.625 / 2.75
        return 7.5625 * t * t + 0.984375


def _ease_out_elastic(t: float) -> float:
    """Elastic easing function for overshoot/settle effects."""
    if t == 0 or t == 1:
        return t
    p = 0.3
    s = p / 4
    return math.pow(2, -10 * t) * math.sin((t - s) * (2 * math.pi) / p) + 1


# ---------------------------------------------------------------------------
# Presets
# ---------------------------------------------------------------------------


def bounce(duration_frames: int, amplitude: float = 30.0) -> list[dict]:
    """
    Vertical bounce with squash/stretch easing.

    The sticker drops down then bounces back up 2-3 times with decreasing
    amplitude, simulating a rubber ball.
    """
    keyframes = []
    for i in range(duration_frames):
        t = i / max(duration_frames - 1, 1)
        tf = _default_transform()

        # Bounce envelope: 3 bounces with decreasing amplitude
        bounce_t = _ease_out_bounce(t)
        tf["y"] = -amplitude * (1.0 - bounce_t)

        # Squash/stretch at bottom of bounce
        if tf["y"] > -amplitude * 0.1:
            squash = 1.0 + 0.08 * (1.0 - abs(tf["y"]) / max(amplitude, 1))
            tf["scale"] = 1.0 / squash  # Compress vertically = wider
        tf["frame"] = i
        keyframes.append(tf)
    return keyframes


def shake(duration_frames: int, intensity: float = 15.0) -> list[dict]:
    """
    Horizontal wiggle with decreasing amplitude.

    Mimics a head-shake or vibration that gradually settles.
    """
    keyframes = []
    for i in range(duration_frames):
        t = i / max(duration_frames - 1, 1)
        tf = _default_transform()

        # Decreasing sinusoidal oscillation
        decay = 1.0 - t
        tf["x"] = intensity * decay * math.sin(t * 6 * math.pi)
        tf["rotation"] = 3.0 * decay * math.sin(t * 6 * math.pi)
        tf["frame"] = i
        keyframes.append(tf)
    return keyframes


def pulse(duration_frames: int, scale_range: tuple = (0.9, 1.1)) -> list[dict]:
    """
    Heartbeat-style scale pulse.

    Two quick pulses then settle, mimicking a beating heart.
    """
    keyframes = []
    lo, hi = scale_range
    for i in range(duration_frames):
        t = i / max(duration_frames - 1, 1)
        tf = _default_transform()

        # Double-beat: fast pulse at 0.15 and 0.35, then settle
        if t < 0.15:
            p = t / 0.15
            tf["scale"] = _lerp(1.0, hi, p)
        elif t < 0.25:
            p = (t - 0.15) / 0.10
            tf["scale"] = _lerp(hi, lo, p)
        elif t < 0.35:
            p = (t - 0.25) / 0.10
            tf["scale"] = _lerp(lo, hi * 0.95, p)
        elif t < 0.50:
            p = (t - 0.35) / 0.15
            tf["scale"] = _lerp(hi * 0.95, 1.0, p)
        else:
            tf["scale"] = 1.0

        tf["frame"] = i
        keyframes.append(tf)
    return keyframes


def pop_in(duration_frames: int) -> list[dict]:
    """
    Scale from 0 -> overshoot 1.15 -> settle 1.0.

    Classic pop/appear animation with elastic overshoot.
    """
    keyframes = []
    for i in range(duration_frames):
        t = i / max(duration_frames - 1, 1)
        tf = _default_transform()

        elastic = _ease_out_elastic(t)
        tf["scale"] = elastic
        tf["opacity"] = min(1.0, t * 4)  # Fade in quickly
        tf["frame"] = i
        keyframes.append(tf)
    return keyframes


def spin(duration_frames: int, revolutions: float = 1.0) -> list[dict]:
    """
    Full 360-degree rotation with ease-in-out.

    Spins the sticker smoothly with acceleration and deceleration.
    """
    keyframes = []
    for i in range(duration_frames):
        t = i / max(duration_frames - 1, 1)
        tf = _default_transform()

        # Ease-in-out cubic
        if t < 0.5:
            eased = 4 * t * t * t
        else:
            eased = 1 - pow(-2 * t + 2, 3) / 2

        tf["rotation"] = 360.0 * revolutions * eased
        tf["frame"] = i
        keyframes.append(tf)
    return keyframes


def wave(duration_frames: int, amplitude: float = 10.0) -> list[dict]:
    """
    Sine wave wobble — gentle rocking motion.

    Combines slight rotation and vertical movement for a
    playful wobble effect.
    """
    keyframes = []
    for i in range(duration_frames):
        t = i / max(duration_frames - 1, 1)
        tf = _default_transform()

        # Continuous sine wave
        phase = t * 4 * math.pi  # 2 full cycles
        tf["y"] = amplitude * math.sin(phase)
        tf["rotation"] = 5.0 * math.sin(phase)
        tf["frame"] = i
        keyframes.append(tf)
    return keyframes


def float_up(duration_frames: int, amplitude: float = 12.0) -> list[dict]:
    """
    Gentle up/down floating motion.

    Smooth, continuous hovering effect like a balloon.
    """
    keyframes = []
    for i in range(duration_frames):
        t = i / max(duration_frames - 1, 1)
        tf = _default_transform()

        # Smooth sine float
        phase = t * 2 * math.pi  # 1 full cycle
        tf["y"] = amplitude * math.sin(phase)
        tf["x"] = amplitude * 0.3 * math.sin(phase * 2)  # Slight horizontal drift
        tf["frame"] = i
        keyframes.append(tf)
    return keyframes


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

PRESETS: dict[str, Callable] = {
    "bounce": bounce,
    "shake": shake,
    "pulse": pulse,
    "pop_in": pop_in,
    "spin": spin,
    "wave": wave,
    "float": float_up,
}


def get_preset(name: str) -> Callable:
    """Get a preset function by name. Raises ValueError if not found."""
    if name not in PRESETS:
        available = ", ".join(sorted(PRESETS.keys()))
        raise ValueError(f"Unknown animation preset '{name}'. Available: {available}")
    return PRESETS[name]


def list_presets() -> list[str]:
    """Return sorted list of available preset names."""
    return sorted(PRESETS.keys())


def generate_keyframes(
    preset_name: str,
    duration_frames: int = 60,
    **kwargs,
) -> list[dict]:
    """
    Generate keyframes for a named preset.

    Args:
        preset_name: One of the registered preset names.
        duration_frames: Total frames in the animation.
        **kwargs: Additional parameters passed to the preset function.

    Returns:
        List of keyframe dicts with frame, x, y, scale, rotation, opacity.
    """
    preset_fn = get_preset(preset_name)
    return preset_fn(duration_frames, **kwargs)
