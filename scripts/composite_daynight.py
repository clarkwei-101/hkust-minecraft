#!/usr/bin/env python3
"""Create a side-by-side day vs night composite."""
from PIL import Image, ImageDraw, ImageFont

WORKDIR = "/Users/yahweh/Desktop/ai应用社/hkust-minecraft"

day = Image.open(f"{WORKDIR}/worlds/final/hkust_topdown_v1.6.png")
night = Image.open(f"{WORKDIR}/previews/hkust-topdown-v1.6-lights.png")

# Match sizes
target_w = 800
day_w, day_h = day.size
night_w, night_h = night.size
day_resized = day.resize((target_w, int(day_h * target_w / day_w)))
night_resized = night.resize((target_w, int(night_h * target_w / night_w)))

# Stack vertically
total_h = day_resized.size[1] + night_resized.size[1] + 60
final = Image.new("RGB", (target_w, total_h), (20, 20, 30))
draw = ImageDraw.Draw(final)
final.paste(day_resized, (0, 25))
final.paste(night_resized, (0, day_resized.size[1] + 55))

# Add labels
try:
    font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 18)
except Exception:
    font = ImageFont.load_default()
draw.text((10, 3), "Day View (v1.6)", fill=(255, 255, 255), font=font)
draw.text((10, day_resized.size[1] + 30), "Night View (lighting system)", fill=(255, 230, 100), font=font)

out = f"{WORKDIR}/worlds/final/hkust_topdown_v1.6_daynight.png"
final.save(out)
print(f"Saved day/night composite: {out}")
