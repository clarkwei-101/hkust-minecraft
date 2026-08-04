#!/usr/bin/env python3
"""
Annotate v1.4-detailed top-down with landmarks, buildings, and details.
"""
import json
from PIL import Image, ImageDraw, ImageFont

WORKDIR = "/Users/yahweh/Desktop/ai应用社/hkust-minecraft"

# Same annotations as v1.4 (buildings + landmarks)
ANNOTATIONS = [
    # Landmarks
    {"x": 220, "z": 160, "label": "Academic Dome", "color": (255, 215, 0), "size": 30},
    {"x": 222, "z": 230, "label": "Sundial", "color": (255, 215, 0), "size": 25},
    {"x": 220, "z": 240, "label": "One-World Fountain", "color": (255, 215, 0), "size": 25},
    {"x": 50, "z": 50, "label": "Seaview Walkway", "color": (135, 206, 250), "size": 35},
    {"x": 130, "z": 100, "label": "Library Landmark", "color": (255, 215, 0), "size": 30},
    {"x": 220, "z": 200, "label": "Atrium", "color": (255, 215, 0), "size": 25},
    {"x": 250, "z": 230, "label": "LG7", "color": (255, 215, 0), "size": 25},
    {"x": 250, "z": 250, "label": "Underpass", "color": (255, 215, 0), "size": 25},
    # Buildings
    {"x": 210, "z": 185, "label": "Academic Building", "color": (220, 220, 220), "size": 12},
    {"x": 230, "z": 220, "label": "LG Complex", "color": (220, 220, 220), "size": 10},
    {"x": 130, "z": 100, "label": "Library Extension", "color": (220, 220, 220), "size": 12},
    {"x": 90, "z": 230, "label": "S.H. Ho Sports Hall", "color": (220, 220, 220), "size": 12},
    {"x": 280, "z": 240, "label": "Wong Check She Center", "color": (220, 220, 220), "size": 8},
    {"x": 150, "z": 300, "label": "UG Hall I", "color": (220, 220, 220), "size": 9},
    {"x": 195, "z": 310, "label": "UG Hall II", "color": (220, 220, 220), "size": 9},
    {"x": 245, "z": 310, "label": "UG Hall VII", "color": (220, 220, 220), "size": 9},
    {"x": 280, "z": 290, "label": "PG Hall I", "color": (220, 220, 220), "size": 9},
    {"x": 320, "z": 310, "label": "PG Hall II", "color": (220, 220, 220), "size": 9},
    {"x": 360, "z": 290, "label": "UG Hall III", "color": (220, 220, 220), "size": 9},
    {"x": 410, "z": 290, "label": "UG Hall IV", "color": (220, 220, 220), "size": 9},
    {"x": 470, "z": 290, "label": "UG Hall VI", "color": (220, 220, 220), "size": 9},
    {"x": 530, "z": 290, "label": "UG Hall VIII", "color": (220, 220, 220), "size": 9},
    {"x": 590, "z": 290, "label": "UG Hall IX", "color": (220, 220, 220), "size": 9},
    {"x": 360, "z": 410, "label": "Bus Terminus", "color": (220, 220, 220), "size": 9},
    # Details
    {"x": 360, "z": 380, "label": "Main E-W Road", "color": (100, 100, 100), "size": 8},
    {"x": 90, "z": 290, "label": "Main N-S Road", "color": (100, 100, 100), "size": 8},
    {"x": 290, "z": 185, "label": "AB Parking", "color": (150, 150, 150), "size": 7},
    {"x": 110, "z": 90, "label": "Library Parking", "color": (150, 150, 150), "size": 7},
    {"x": 50, "z": 320, "label": "Soccer Field", "color": (50, 200, 50), "size": 9},
    {"x": 145, "z": 290, "label": "Tennis Courts", "color": (50, 100, 200), "size": 7},
]


def main():
    src = f"{WORKDIR}/previews/hkust-topdown-v1.4-detailed.png"
    dst = f"{WORKDIR}/worlds/final/hkust_topdown_v1.4-detailed.png"
    img = Image.open(src)
    draw = ImageDraw.Draw(img)

    try:
        font_large = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 13)
        font_med = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 11)
        font_small = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 9)
    except Exception:
        font_large = ImageFont.load_default()
        font_med = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # Legend
    legend = [
        ("Gold = Landmark", (255, 215, 0)),
        ("White = Building", (220, 220, 220)),
        ("Gray = Road/Parking", (150, 150, 150)),
        ("Green/Blue = Field", (50, 200, 50)),
    ]
    y_off = 5
    for label, color in legend:
        draw.rectangle([5, y_off, 14, y_off + 9], fill=color)
        draw.text((20, y_off), label, fill=(255, 255, 255), font=font_small)
        y_off += 12

    for ann in ANNOTATIONS:
        x, z = ann["x"], ann["z"]
        # Flip Z to match render orientation
        rz = 480 - z
        rx = x
        size = ann["size"]
        label = ann["label"]
        color = ann["color"]
        # Marker dot
        draw.ellipse([rx - size // 2, rz - size // 2, rx + size // 2, rz + size // 2],
                     outline=color, width=2)
        # Label
        font = font_large if size >= 25 else font_med if size >= 12 else font_small
        draw.text((rx + size, rz - 6), label, fill=color, font=font)

    img.save(dst)
    print(f"Annotated top-down saved to: {dst}")


if __name__ == "__main__":
    main()
