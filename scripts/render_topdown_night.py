#!/usr/bin/env python3
"""
Render a 'night-mode' top-down that highlights all light sources.
Uses the same render pipeline as render_topdown.py but with custom
block coloring that emphasizes glowing blocks.
"""
import sys
from pathlib import Path

sys.path.insert(0, '/Users/yahweh/Library/Python/3.11/lib/python/site-packages')

from amulet import level as amulet_level
from amulet.utils import block_coords_to_chunk_coords
import numpy as np
from PIL import Image, ImageDraw, ImageFont

WORKDIR = Path("/Users/yahweh/Desktop/ai应用社/hkust-minecraft")

# Light blocks (emit light) — color them as bright yellow glow
LIGHT_BLOCKS = {
    "sea_lantern", "glowstone", "lantern", "shroomlight",
    "redstone_lamp", "torch", "soul_torch", "end_rod",
    "fire", "jack_o_lantern", "beacon", "conduit",
}

# Map blocks to RGB for night mode
def block_to_color(b):
    name = b[0].base_name if b else ""
    if name in LIGHT_BLOCKS:
        return (255, 230, 100)  # bright yellow glow
    if name in ("glass", "stained_glass"):
        return (140, 180, 220)  # cyan glass
    if "stained_glass" in name:
        return (140, 180, 220)
    if name in ("oak_fence", "oak_log"):
        return (90, 60, 30)
    if name in ("stone_bricks", "smooth_stone", "stone"):
        return (60, 60, 70)
    if name in ("grass_block", "dirt"):
        return (30, 50, 30)  # dark green for night
    if name in ("sand"):
        return (120, 110, 80)
    if name in ("water"):
        return (10, 30, 60)  # very dark blue
    if name in ("air"):
        return (0, 0, 0)
    if "concrete" in name:
        return (80, 80, 95)
    if "leaves" in name:
        return (15, 40, 15)
    if "wool" in name:
        return (200, 200, 220)
    if "planks" in name:
        return (120, 80, 40)
    return (50, 50, 60)


def render_night(world_path, output_path, scale=2):
    print(f"Loading {world_path}")
    level = amulet_level.load_level(str(world_path))
    dim = "minecraft:overworld"
    ver = ("bedrock", (1, 21, 40))

    # Limit to actual campus area (avoid full world bounds)
    bounds = level.bounds(dim)
    print(f"Bounds: x=[{bounds.min_x}, {bounds.max_x}], z=[{bounds.min_z}, {bounds.max_z}]")
    # Use realistic campus bounds (most action is within 0..650)
    min_x, min_z = 0, 0
    max_x, max_z = 650, 480

    width = (max_x - min_x) // scale
    height = (max_z - min_z) // scale
    print(f"Rendering {width}x{height} (scale 1:{scale}) night view...")

    img = np.zeros((height, width, 3), dtype=np.uint8)
    light_glow = np.zeros((height, width, 3), dtype=np.uint8)
    light_count = 0

    # First pass: base colors (top non-air block)
    for x in range(min_x, max_x, scale):
        for z in range(min_z, max_z, scale):
            cx = (x - min_x) // scale
            cz = (max_z - z) // scale - 1
            if cz < 0 or cz >= height or cx < 0 or cx >= width:
                continue
            for y in range(120, 30, -1):
                b = level.get_version_block(x, y, z, dim, ver)
                if b and b[0].base_name != "air":
                    color = block_to_color(b)
                    img[cz, cx] = color
                    break

    # Second pass: find light blocks and add glow
    for x in range(min_x, max_x, scale):
        for z in range(min_z, max_z, scale):
            cx = (x - min_x) // scale
            cz = (max_z - z) // scale - 1
            if cz < 0 or cz >= height or cx < 0 or cx >= width:
                continue
            for y in range(120, 30, -1):
                b = level.get_version_block(x, y, z, dim, ver)
                if b and b[0].base_name == "air":
                    continue
                if b[0].base_name in LIGHT_BLOCKS:
                    light_count += 1
                    light_glow[cz, cx] = (255, 230, 100)
                    # Glow halo
                    for dx in [-2, -1, 0, 1, 2]:
                        for dz in [-2, -1, 0, 1, 2]:
                            dist = abs(dx) + abs(dz)
                            if dist > 3:
                                continue
                            nx, nz = cx + dx, cz + dz
                            if 0 <= nx < width and 0 <= nz < height:
                                if tuple(light_glow[nz, nx]) == (0, 0, 0):
                                    intensity = max(60, 200 - dist * 60)
                                    light_glow[nz, nx] = (intensity, int(intensity * 0.8), int(intensity * 0.4))
                    break

    print(f"Found {light_count} light sources")
    base_dark = (img.astype(np.float32) * 0.5).astype(np.uint8)
    final = np.maximum(base_dark, light_glow)
    img_out = Image.fromarray(final)
    img_out.save(output_path)
    print(f"Saved night view: {output_path}")

    level.close()


if __name__ == "__main__":
    src = WORKDIR / "worlds/working/v1.6"
    dst = WORKDIR / "previews/hkust-topdown-v1.6-night.png"
    # Use scale=1 to capture all light detail
    render_night(str(src), str(dst), scale=1)
