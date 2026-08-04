#!/usr/bin/env python3
"""
Generate a top-down preview of the HKUST Minecraft world by reading
block data from the Bedrock LevelDB via amulet.
"""
import argparse
import sys
import math
from pathlib import Path
import numpy as np
from PIL import Image

sys.path.insert(0, '/Users/yahweh/Library/Python/3.11/lib/python/site-packages')
import amulet

# Material colors (top-down view)
MATERIAL_COLORS = {
    'water': (60, 90, 180),
    'sand': (240, 220, 160),
    'dirt': (130, 90, 50),
    'grass_block': (60, 140, 60),
    'stone': (120, 120, 120),
    'granite': (140, 110, 100),
    'andesite': (180, 180, 180),
    'diorite': (200, 200, 200),
    'gravel': (140, 130, 110),
    'oak_leaves': (50, 130, 30),
    'spruce_leaves': (40, 90, 30),
    'dark_oak_leaves': (30, 80, 20),
    'jungle_leaves': (40, 110, 30),
    'acacia_leaves': (60, 140, 40),
    'mangrove_leaves': (50, 100, 30),
    'azalea_leaves': (70, 140, 50),
    'birch_leaves': (90, 150, 70),
    'oak_log': (110, 80, 50),
    'spruce_log': (60, 50, 30),
    'dark_oak_log': (60, 40, 20),
    'jungle_log': (130, 90, 50),
    'mangrove_log': (100, 70, 40),
    'birch_log': (200, 180, 140),
    'white_concrete': (240, 240, 240),
    'gray_concrete': (130, 130, 130),
    'light_gray_concrete': (180, 180, 180),
    'black_concrete': (30, 30, 30),
    'red_concrete': (200, 70, 70),
    'blue_concrete': (70, 100, 200),
    'glass': (200, 230, 240),
    'quartz_block': (240, 235, 220),
    'smooth_stone': (170, 170, 170),
    'brick_block': (180, 100, 80),
    'sea_lantern': (240, 240, 200),
    'gold_block': (240, 200, 50),
    'air': (200, 230, 255),  # sky color
}


def get_color(block_name):
    """Map a block's base_name to RGB color."""
    if not block_name:
        return (200, 200, 200)
    for key, color in MATERIAL_COLORS.items():
        if key in block_name:
            return color
    # Default: hash by name
    h = hash(block_name)
    return (h % 256, (h >> 8) % 256, (h >> 16) % 256)


def render(world_path: Path, output: Path, x_range=(0, 816), z_range=(0, 976), scale=1):
    """Render a top-down view of the world."""
    print(f"Loading world: {world_path}")
    level = amulet.load_level(str(world_path))
    dim = 'minecraft:overworld'
    ver = ('bedrock', (1, 21, 40))

    min_x, max_x = x_range
    min_z, max_z = z_range

    width = max_x - min_x
    height = max_z - min_z

    # Create image (downsampled)
    img = np.zeros((height // scale, width // scale, 3), dtype=np.uint8)
    img[:] = (200, 230, 255)  # sky blue background

    print(f"Rendering {width}x{height} blocks (scale 1:{scale})...")

    for sx in range(0, width, scale):
        for sz in range(0, height, scale):
            wx = min_x + sx
            wz = min_z + sz
            # Find highest non-air block
            for wy in range(200, 0, -1):
                try:
                    b = level.get_version_block(wx, wy, wz, dim, ver)
                    name = b[0].base_name
                    if name != 'air':
                        color = get_color(name)
                        img[sz // scale, sx // scale] = color
                        break
                except Exception:
                    continue

    level.close()

    # Save
    Image.fromarray(img).save(output)
    print(f"Saved {output}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--world', '-w', required=True, help='World directory path')
    parser.add_argument('--output', '-o', required=True, help='Output PNG path')
    parser.add_argument('--scale', '-s', type=int, default=2, help='Downsample factor')
    args = parser.parse_args()

    render(Path(args.world), Path(args.output), scale=args.scale)


if __name__ == '__main__':
    main()