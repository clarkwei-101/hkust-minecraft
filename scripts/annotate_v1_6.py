#!/usr/bin/env python3
"""Annotate v1.6 top-down with lighting features."""
from PIL import Image, ImageDraw, ImageFont

WORKDIR = "/Users/yahweh/Desktop/ai应用社/hkust-minecraft"

ANNOTATIONS = [
    {"x": 220, "z": 160, "label": "Dome (4 floodlights)", "color": (255, 215, 0), "size": 30},
    {"x": 222, "z": 230, "label": "Sundial (4 accent lights)", "color": (255, 215, 0), "size": 25},
    {"x": 220, "z": 240, "label": "Fountain (4 lights)", "color": (255, 215, 0), "size": 25},
    {"x": 50, "z": 50, "label": "Seaview Walkway (lanterns)", "color": (135, 206, 250), "size": 30},
    {"x": 220, "z": 200, "label": "Atrium Chandelier", "color": (255, 215, 0), "size": 25},
    {"x": 130, "z": 100, "label": "Library Chandelier", "color": (255, 215, 0), "size": 25},
    {"x": 90, "z": 230, "label": "Sports Hall Lights", "color": (255, 215, 0), "size": 25},
    # Major buildings (windows glow)
    {"x": 210, "z": 185, "label": "Academic Bldg (lit)", "color": (255, 230, 100), "size": 11},
    {"x": 230, "z": 220, "label": "LG Complex (lit)", "color": (255, 230, 100), "size": 10},
    {"x": 360, "z": 290, "label": "Dorms (lit)", "color": (255, 230, 100), "size": 9},
    {"x": 360, "z": 410, "label": "Bus Terminus (lit)", "color": (255, 230, 100), "size": 9},
    # Path lights
    {"x": 275, "z": 200, "label": "Streetlight", "color": (255, 200, 50), "size": 7},
    {"x": 360, "z": 380, "label": "Main Road (streetlights)", "color": (255, 200, 50), "size": 7},
    {"x": 90, "z": 290, "label": "Main Road (streetlights)", "color": (255, 200, 50), "size": 7},
]


def main():
    src = f"{WORKDIR}/previews/hkust-topdown-v1.6.png"
    dst = f"{WORKDIR}/worlds/final/hkust_topdown_v1.6.png"
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

    legend = [
        ("Gold = Landmark + Lighting", (255, 215, 0)),
        ("Yellow = Lit Building", (255, 230, 100)),
        ("Orange = Streetlight", (255, 200, 50)),
    ]
    y_off = 5
    for label, color in legend:
        draw.rectangle([5, y_off, 14, y_off + 9], fill=color)
        draw.text((20, y_off), label, fill=(255, 255, 255), font=font_small)
        y_off += 12

    for ann in ANNOTATIONS:
        x, z = ann["x"], ann["z"]
        rz = 480 - z
        rx = x
        size = ann["size"]
        label = ann["label"]
        color = ann["color"]
        draw.ellipse([rx - size // 2, rz - size // 2, rx + size // 2, rz + size // 2],
                     outline=color, width=2)
        font = font_large if size >= 25 else font_med if size >= 12 else font_small
        draw.text((rx + size, rz - 6), label, fill=color, font=font)

    img.save(dst)
    print(f"Annotated top-down saved to: {dst}")


if __name__ == "__main__":
    main()
