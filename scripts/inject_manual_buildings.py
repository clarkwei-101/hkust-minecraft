#!/usr/bin/env python3
"""
HKUST Minecraft v1.3 - Manual Building Injector
================================================

Injects hand-curated buildings from data/manual_buildings.json with
verified MC coordinates.
"""

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, '/Users/yahweh/Library/Python/3.11/lib/python/site-packages')

try:
    import amulet
    from amulet.api.block import Block
except ImportError as e:
    print(f"ERROR: amulet-core not available: {e}")
    sys.exit(1)


@dataclass
class BlockSpec:
    namespace: str
    name: str
    states: dict = field(default_factory=dict)

    def to_amulet(self):
        return Block(self.namespace, self.name)


# Materials
QUARTZ_BLOCK = BlockSpec("minecraft", "quartz_block")
CONCRETE_WHITE = BlockSpec("minecraft", "white_concrete")
CONCRETE_GRAY = BlockSpec("minecraft", "gray_concrete")
CONCRETE_LIGHT_GRAY = BlockSpec("minecraft", "light_gray_concrete")
CONCRETE_RED = BlockSpec("minecraft", "red_concrete")
GLASS = BlockSpec("minecraft", "glass")
SMOOTH_STONE = BlockSpec("minecraft", "smooth_stone")


MATERIAL_MAP = {
    'white_concrete': CONCRETE_WHITE,
    'gray_concrete': CONCRETE_GRAY,
    'light_gray_concrete': CONCRETE_LIGHT_GRAY,
    'red_concrete': CONCRETE_RED,
}


def build_box_schematic(height_m, footprint_w, footprint_l, wall_block, top_block, accent_block):
    """Build a box building schematic centered at local origin (0, 0)."""
    blocks = []
    half_w = footprint_w // 2
    half_l = footprint_l // 2

    for y in range(height_m + 1):
        is_top = (y == height_m)
        is_foundation = (y == 0)
        is_window_band = (y >= 2 and y < height_m and (y % 3 == 0))

        for x in range(-half_w, half_w + 1):
            for z in range(-half_l, half_l + 1):
                if is_foundation:
                    blocks.append((x, 0, z, QUARTZ_BLOCK))
                elif abs(x) == half_w or abs(z) == half_l:
                    # Wall
                    if is_top:
                        blocks.append((x, y, z, top_block))
                    elif is_window_band:
                        blocks.append((x, y, z, accent_block))
                    else:
                        blocks.append((x, y, z, wall_block))
                elif is_top:
                    # Roof
                    blocks.append((x, y, z, top_block))
    return blocks


def find_ground_height(level, wx, wz, dim, ver):
    """Scan downward from Y=200 to find first non-air block."""
    for by in range(200, 0, -1):
        try:
            b = level.get_version_block(wx, by, wz, dim, ver)
            if b[0].base_name != 'air':
                return by
        except Exception:
            break
    return 60


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--world', '-w', required=True)
    parser.add_argument('--data', '-d', default='data/manual_buildings.json')
    parser.add_argument('--dry-run', '-n', action='store_true')
    parser.add_argument('--verbose', '-v', action='store_true')
    args = parser.parse_args()

    world_path = Path(args.world)
    if not (world_path / 'db').exists():
        print(f"ERROR: Not a Bedrock world at {world_path}")
        sys.exit(1)

    data_path = Path(__file__).parent.parent / args.data
    with open(data_path) as f:
        buildings = json.load(f)

    print(f"Loaded {len(buildings)} manual buildings from {data_path}")

    print(f"\nLoading world: {world_path}")
    level = amulet.load_level(str(world_path))
    dim = 'minecraft:overworld'
    ver = ('bedrock', (1, 21, 40))

    print(f"\nBuilding placements:")
    total_blocks = 0
    skipped = []

    for b in buildings:
        ft_w, ft_l = b['footprint']
        gy = find_ground_height(level, b['mc_x'], b['mc_z'], dim, ver)

        if gy < 30:
            skipped.append((b['name'], gy))
            continue

        material = MATERIAL_MAP.get(b['material'], CONCRETE_GRAY)
        roof = CONCRETE_WHITE if b['material'] != 'red_concrete' else CONCRETE_RED
        accent = GLASS

        blocks = build_box_schematic(
            height_m=int(b['height_m']),
            footprint_w=ft_w,
            footprint_l=ft_l,
            wall_block=material,
            top_block=roof,
            accent_block=accent,
        )
        total_blocks += len(blocks)

        if args.verbose:
            print(f"  {b['name'][:35]:35} MC=({b['mc_x']:3},{gy+1:3},{b['mc_z']:3}) "
                  f"h={b['height_m']:.0f}m ft={ft_w}x{ft_l} blocks={len(blocks)}")

        if not args.dry_run:
            for rx, ry, rz, bs in blocks:
                bx = b['mc_x'] + rx
                by = (gy + 1) + ry
                bz = b['mc_z'] + rz
                try:
                    amulet_block = bs.to_amulet()
                    level.set_version_block(bx, by, bz, dim, ver, amulet_block)
                except Exception as e:
                    if args.verbose:
                        print(f"    ERROR at ({bx},{by},{bz}): {e}")

    if skipped:
        print(f"\nSkipped {len(skipped)} buildings (ground too low / ocean):")
        for name, gy in skipped:
            print(f"  {name}: gy={gy}")

    if args.dry_run:
        print(f"\n[DRY RUN] Would place {total_blocks} blocks for {len(buildings) - len(skipped)} buildings")
        level.close()
        return

    print(f"\nInjecting complete: {total_blocks} blocks for {len(buildings) - len(skipped)} buildings")
    print(f"Saving world...")
    level.save()
    level.close()
    print(f"Done!")


if __name__ == '__main__':
    main()