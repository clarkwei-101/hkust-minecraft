#!/usr/bin/env python3
"""Annotate v1.7 top-down with all features including NEW landmarks."""
from PIL import Image, ImageDraw, ImageFont

WORKDIR = "/Users/yahweh/Desktop/ai应用社/hkust-minecraft"

ANNOTATIONS = [
    # Existing landmarks
    {"x": 220, "z": 160, "label": "Academic Dome", "color": (255, 215, 0), "size": 28},
    {"x": 222, "z": 230, "label": "Sundial (RED 火鸟)", "color": (255, 80, 80), "size": 28},  # Changed to red
    {"x": 220, "z": 240, "label": "Fountain", "color": (255, 215, 0), "size": 22},
    {"x": 50, "z": 50, "label": "Seaview Walkway", "color": (135, 206, 250), "size": 32},
    {"x": 130, "z": 100, "label": "Library", "color": (255, 215, 0), "size": 28},
    {"x": 220, "z": 200, "label": "Atrium", "color": (255, 215, 0), "size": 22},

    # NEW landmarks
    {"x": 170, "z": 305, "label": "Armillary Sphere 浑天仪 (NEW)", "color": (255, 215, 0), "size": 24},
    {"x": 320, "z": 480, "label": "Shaw Auditorium 邵逸夫演艺中心 (NEW)", "color": (255, 215, 0), "size": 28},
    {"x": 550, "z": 60, "label": "Coastal Marine Lab 海岸海洋实验室 (NEW)", "color": (100, 200, 255), "size": 28},
    {"x": 470, "z": 290, "label": "Jockey Club Tower (UG VI enhanced)", "color": (255, 100, 100), "size": 12},

    # Major buildings
    {"x": 210, "z": 185, "label": "Academic Building", "color": (220, 220, 220), "size": 11},
    {"x": 230, "z": 220, "label": "LG Complex", "color": (220, 220, 220), "size": 10},
    {"x": 90, "z": 230, "label": "Sports Hall", "color": (220, 220, 220), "size": 11},
    {"x": 360, "z": 290, "label": "Dorms Row", "color": (220, 220, 220), "size": 9},
    {"x": 360, "z": 410, "label": "Bus Terminus", "color": (220, 220, 220), "size": 9},

    # Details
    {"x": 360, "z": 380, "label": "Main Road", "color": (100, 100, 100), "size": 8},
    {"x": 90, "z": 290, "label": "Main Road", "color": (100, 100, 100), "size": 8},
    {"x": 50, "z": 320, "label": "Soccer Field", "color": (50, 200, 50), "size": 9},
]


def main():
    src = f"{WORKDIR}/previews/hkust-topdown-v1.7.png"
    dst = f"{WORKDIR}/worlds/final/hkust_topdown_v1.7.png"
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
        ("Gold = Landmark", (255, 215, 0)),
        ("Red = Fixed Landmark / 火鸟 Sundial", (255, 80, 80)),
        ("Cyan = Waterfront Landmark", (100, 200, 255)),
        ("White = Building", (220, 220, 220)),
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
