#!/usr/bin/env python3
"""
Split a sticker sheet into individual stickers with transparent backgrounds.
Each sticker is saved as a separate 512x512 PNG file.
"""

import os
import numpy as np
from PIL import Image


def remove_white_background(img, threshold=240):
    """Convert white/near-white pixels to transparent."""
    img = img.convert("RGBA")
    data = np.array(img)

    # Find pixels where R, G, B are all above the threshold (white-ish)
    white_mask = (
        (data[:, :, 0] > threshold)
        & (data[:, :, 1] > threshold)
        & (data[:, :, 2] > threshold)
    )

    # Set alpha to 0 for white pixels
    data[white_mask, 3] = 0

    return Image.fromarray(data)


def find_sticker_bboxes(img, min_size=50):
    """
    Find bounding boxes of individual stickers by detecting connected
    non-transparent regions.
    """
    data = np.array(img)
    # Create a binary mask of non-transparent pixels
    mask = data[:, :, 3] > 0

    from scipy import ndimage

    labeled, num_features = ndimage.label(mask)

    bboxes = []
    for i in range(1, num_features + 1):
        ys, xs = np.where(labeled == i)
        if len(ys) < min_size * min_size:
            # Skip tiny fragments/noise
            continue
        bbox = (xs.min(), ys.min(), xs.max(), ys.max())
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        if w > min_size and h > min_size:
            bboxes.append(bbox)

    # Sort: top row first (by y), then left to right (by x)
    bboxes.sort(key=lambda b: (b[1] // (img.height // 3), b[0]))
    return bboxes


def crop_and_resize(img, bbox, target_size=512, padding=10):
    """Crop a sticker from the image and resize to target_size x target_size."""
    x1, y1, x2, y2 = bbox
    # Add small padding
    x1 = max(0, x1 - padding)
    y1 = max(0, y1 - padding)
    x2 = min(img.width, x2 + padding)
    y2 = min(img.height, y2 + padding)

    cropped = img.crop((x1, y1, x2, y2))

    # Resize while keeping aspect ratio, then paste on a square canvas
    w, h = cropped.size
    scale = min(target_size / w, target_size / h) * 0.9  # 90% to leave margin
    new_w = int(w * scale)
    new_h = int(h * scale)
    cropped = cropped.resize((new_w, new_h), Image.LANCZOS)

    # Center on a transparent 512x512 canvas
    canvas = Image.new("RGBA", (target_size, target_size), (0, 0, 0, 0))
    offset_x = (target_size - new_w) // 2
    offset_y = (target_size - new_h) // 2
    canvas.paste(cropped, (offset_x, offset_y), cropped)

    return canvas


def main():
    input_path = os.path.expanduser(
        "~/Desktop/ChatGPT Image Feb 21, 2026, 01_32_01 PM.png"
    )
    output_dir = os.path.expanduser("~/Desktop/stickers")
    os.makedirs(output_dir, exist_ok=True)

    print(f"Loading image: {input_path}")
    img = Image.open(input_path)
    print(f"Image size: {img.size}")

    # Step 1: Remove white background
    print("Removing white background...")
    img_transparent = remove_white_background(img, threshold=240)

    # Step 2: Find individual stickers
    print("Finding individual stickers...")
    bboxes = find_sticker_bboxes(img_transparent, min_size=80)
    print(f"Found {len(bboxes)} stickers")

    # Step 3: Crop, resize, and save each sticker
    sticker_names = [
        "01_excited_girl",
        "02_crying_boy",
        "03_angry_devil",
        "04_lol_dog",
        "05_love_girl",
        "06_confused_cat",
        "07_thumbsup_frog",
        "08_sleepy_panda",
        "09_shocked_bird",
        "10_hi_bunny",
    ]

    for i, bbox in enumerate(bboxes):
        name = sticker_names[i] if i < len(sticker_names) else f"sticker_{i + 1:02d}"
        sticker = crop_and_resize(img_transparent, bbox)
        output_path = os.path.join(output_dir, f"{name}.png")
        sticker.save(output_path, "PNG")
        print(f"  Saved: {output_path}")

    print(f"\nDone! {len(bboxes)} stickers saved to {output_dir}")


if __name__ == "__main__":
    main()
