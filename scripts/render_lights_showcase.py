#!/usr/bin/env python3
"""
Render a 'lighting showcase' — zoomed-in top-down that highlights lights at scale 1:1.
Limits to the central campus area for clarity.
"""
import sys
from pathlib import Path

sys.path.insert(0, '/Users/yahweh/Library/Python/3.11/lib/python/site-packages')

from amulet import level as amulet_level
import numpy as np
from PIL import Image, ImageDraw, ImageFont

WORKDIR = Path("/Users/yahweh/Desktop/ai应用社/hkust-minecraft")

LIGHT_BLOCKS = {
    "sea_lantern", "glowstone", "lantern", "shroomlight",
    "redstone_lamp", "torch", "soul_torch", "end_rod",
}


def block_to_color(b):
    name = b[0].base_name if b else ""
    if name in LIGHT_BLOCKS:
        return (255, 230, 100)
    if "glass" in name:
        return (140, 180, 220)
    if name in ("oak_fence", "oak_log"):
        return (90, 60, 30)
    if name in ("stone_bricks", "smooth_stone", "stone", "quartz_block"):
        return (60, 60, 70)
    if name in ("grass_block", "dirt"):
        return (40, 70, 40)
    if name in ("sand"):
        return (120, 110, 80)
    if name in ("water"):
        return (15, 35, 70)
    if name in ("air"):
        return (0, 0, 0)
    if "concrete" in name:
        return (80, 80, 95)
    if "leaves" in name:
        return (20, 50, 20)
    if "wool" in name:
        return (200, 200, 220)
    if "planks" in name:
        return (120, 80, 40)
    return (50, 50, 60)


def render(world_path, output_path, x_min=0, z_min=0, x_max=650, z_max=480):
    print(f"Loading {world_path}")
    level = amulet_level.load_level(str(world_path))
    dim = "minecraft:overworld"
    ver = ("bedrock", (1, 21, 40))

    print(f"Rendering campus area x=[{x_min}, {x_max}], z=[{z_min}, {z_max}]")

    width = x_max - x_min
    height = z_max - z_min

    img = np.zeros((height, width, 3), dtype=np.uint8)

    # First pass: base colors
    print("Pass 1: base colors")
    for x in range(x_min, x_max):
        if x % 50 == 0:
            print(f"  x={x}/{x_max}")
        for z in range(z_min, z_max):
            cx = x - x_min
            cz = z_max - z - 1
            for y in range(120, 30, -1):
                b = level.get_version_block(x, y, z, dim, ver)
                if b and b[0].base_name != "air":
                    color = block_to_color(b)
                    img[cz, cx] = color
                    break

    print("Pass 2: scanning for lights")
    lights = []
    for x in range(x_min, x_max):
        for z in range(z_min, z_max):
            for y in range(120, 30, -1):
                b = level.get_version_block(x, y, z, dim, ver)
                if b and b[0].base_name == "air":
                    continue
                if b[0].base_name in LIGHT_BLOCKS:
                    lights.append((x, y, z, b[0].base_name))
                break

    print(f"Found {len(lights)} light sources")

    # Add glow halos for each light
    print("Pass 3: adding glow halos")
    for lx, ly, lz, ltype in lights:
        cx = lx - x_min
        cz = z_max - lz - 1
        # Add bright dot
        if 0 <= cx < width and 0 <= cz < height:
            img[cz, cx] = (255, 230, 100)
        # Glow halo (small radius)
        for dx in [-1, 0, 1]:
            for dz in [-1, 0, 1]:
                nx, nz = cx + dx, cz + dz
                if 0 <= nx < width and 0 <= nz < height:
                    cur = img[nz, nx]
                    # Brighten if currently dark
                    if max(cur) < 200:
                        # Add glow
                        blended = np.minimum(cur.astype(np.int32) + np.array([100, 80, 30]), 255).astype(np.uint8)
                        img[nz, nx] = blended

    print(f"Saving to {output_path}")
    img_out = Image.fromarray(img)
    img_out.save(output_path)
    print("Done!")
    level.close()


if __name__ == "__main__":
    src = WORKDIR / "worlds/working/v1.6"
    dst = WORKDIR / "previews/hkust-topdown-v1.6-lights.png"
    render(str(src), str(dst), x_min=0, z_min=0, x_max=650, z_max=480)
