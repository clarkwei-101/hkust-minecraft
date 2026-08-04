#!/usr/bin/env python3
"""
HKUST Minecraft v1.4 - Enhanced Building Injector
==================================================

Builds more realistic buildings with:
- Real windows (glass strips every 3 floors)
- Roof variations (flat, dome, pitched)
- Doors at ground level
- Foundation with brick base
- Inter-floor divisions
"""

import argparse
import json
import math
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
SMOOTH_STONE = BlockSpec("minecraft", "smooth_stone")
STONE_BRICKS = BlockSpec("minecraft", "stone_bricks")
BRICKS = BlockSpec("minecraft", "bricks")
CONCRETE_WHITE = BlockSpec("minecraft", "white_concrete")
CONCRETE_GRAY = BlockSpec("minecraft", "gray_concrete")
CONCRETE_LIGHT_GRAY = BlockSpec("minecraft", "light_gray_concrete")
CONCRETE_RED = BlockSpec("minecraft", "red_concrete")
CONCRETE_BLACK = BlockSpec("minecraft", "black_concrete")
GLASS = BlockSpec("minecraft", "glass")
GLASS_LIGHT_BLUE = BlockSpec("minecraft", "light_blue_stained_glass")
GLASS_GRAY = BlockSpec("minecraft", "gray_stained_glass")
SEA_LANTERN = BlockSpec("minecraft", "sea_lantern")
OAK_DOOR = BlockSpec("minecraft", "oak_door")
DARK_OAK_DOOR = BlockSpec("minecraft", "dark_oak_door")
IRON_DOOR = BlockSpec("minecraft", "iron_door")
OAK_SLAB = BlockSpec("minecraft", "oak_slab")
STONE_SLAB = BlockSpec("minecraft", "stone_slab")
DARK_OAK_LOG = BlockSpec("minecraft", "dark_oak_log")
OAK_LOG = BlockSpec("minecraft", "oak_log")
ACACIA_PLANKS = BlockSpec("minecraft", "acacia_planks")

MATERIAL_MAP = {
    'white_concrete': CONCRETE_WHITE,
    'gray_concrete': CONCRETE_GRAY,
    'light_gray_concrete': CONCRETE_LIGHT_GRAY,
    'red_concrete': CONCRETE_RED,
}


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


def build_dormitory_schematic(ft_w, ft_l, height_m, wall_block, accent_color, door_block):
    """Build a detailed dormitory with windows, floor dividers, and doors."""
    blocks = []
    half_w = ft_w // 2
    half_l = ft_l // 2

    # Foundation (2 blocks of stone bricks)
    for x in range(-half_w - 1, half_w + 2):
        for z in range(-half_l - 1, half_l + 2):
            blocks.append((x, 0, z, STONE_BRICKS))
            if y := 0:  # second row of foundation
                blocks.append((x, 1, z, STONE_BRICKS))

    # Building structure
    for y in range(2, height_m + 1):
        is_top = (y == height_m)
        # Floor divisions every 4 levels (visible from outside as horizontal lines)
        is_floor_line = (y % 4 == 0)

        for x in range(-half_w, half_w + 1):
            for z in range(-half_l, half_l + 1):
                on_perimeter = (abs(x) == half_w or abs(z) == half_l)
                on_corner = (abs(x) == half_w and abs(z) == half_l)

                if is_top:
                    # Roof - flat with slight parapet
                    blocks.append((x, y, z, wall_block))
                elif on_perimeter and not on_corner:
                    # Wall with window placement
                    if is_floor_line:
                        # Horizontal floor divider (concrete)
                        blocks.append((x, y, z, wall_block))
                    elif (y % 3) == 0:
                        # Window row - glass strip
                        blocks.append((x, y, z, GLASS_LIGHT_BLUE))
                    else:
                        blocks.append((x, y, z, wall_block))
                elif on_corner:
                    # Corner pillars - slightly different material
                    blocks.append((x, y, z, QUARTZ_BLOCK))
                else:
                    # Interior - hollow (air)
                    pass

    # Door at ground level (south-facing)
    door_x = half_w // 2
    door_z = half_l
    blocks.append((door_x, 2, door_z, door_block))
    blocks.append((door_x - 1, 2, door_z, door_block))
    blocks.append((door_x + 1, 2, door_z, door_block))

    return blocks


def build_academic_schematic(ft_w, ft_l, height_m, wall_block, roof_color, door_block):
    """Build academic building with central courtyard (atrium) and detailed roof."""
    blocks = []
    half_w = ft_w // 2
    half_l = ft_l // 2

    # Foundation
    for x in range(-half_w - 1, half_w + 2):
        for z in range(-half_l - 1, half_l + 2):
            blocks.append((x, 0, z, STONE_BRICKS))
            blocks.append((x, 1, z, STONE_BRICKS))

    # Walls with windows
    for y in range(2, height_m + 1):
        is_top = (y == height_m)
        is_window_row = (y >= 3 and y < height_m and (y % 3) == 0)

        for x in range(-half_w, half_w + 1):
            for z in range(-half_l, half_l + 1):
                on_perimeter = (abs(x) == half_w or abs(z) == half_l)

                if is_top:
                    # Roof - flat with border
                    blocks.append((x, y, z, roof_color))
                elif on_perimeter:
                    if is_window_row:
                        blocks.append((x, y, z, GLASS_LIGHT_BLUE))
                    else:
                        blocks.append((x, y, z, wall_block))

    # Central atrium (hollow middle)
    # Skip - already hollow

    # Entrance (large door)
    door_z = half_l
    for dx in range(-2, 3):
        blocks.append((dx, 2, door_z, IRON_DOOR))
        blocks.append((dx, 3, door_z, IRON_DOOR))

    # Roof rim (slightly raised)
    for x in range(-half_w - 1, half_w + 2):
        for z in [-half_l - 1, half_l + 1]:
            blocks.append((x, height_m + 1, z, CONCRETE_BLACK))
    for z in range(-half_l - 1, half_l + 2):
        for x in [-half_w - 1, half_w + 1]:
            blocks.append((x, height_m + 1, z, CONCRETE_BLACK))

    return blocks


def build_sports_hall_schematic(ft_w, ft_l, height_m, wall_block, roof_block, door_block):
    """Build a sports hall with dome-like roof."""
    blocks = []
    half_w = ft_w // 2
    half_l = ft_l // 2
    center_x = 0
    center_z = 0
    max_radius = min(half_w, half_l)

    # Foundation
    for x in range(-half_w - 1, half_w + 2):
        for z in range(-half_l - 1, half_l + 2):
            blocks.append((x, 0, z, STONE_BRICKS))
            blocks.append((x, 1, z, STONE_BRICKS))

    # Walls
    wall_height = height_m - 5  # Lower walls, dome on top
    for y in range(2, wall_height + 1):
        is_window_row = (y % 3) == 0 and y >= 3

        for x in range(-half_w, half_w + 1):
            for z in range(-half_l, half_l + 1):
                on_perimeter = (abs(x) == half_w or abs(z) == half_l)
                if on_perimeter:
                    if is_window_row:
                        blocks.append((x, y, z, GLASS_LIGHT_BLUE))
                    else:
                        blocks.append((x, y, z, wall_block))

    # Dome roof (hemisphere)
    for y in range(wall_height + 1, height_m + 1):
        dy = y - wall_height - 1
        max_r = math.sqrt(max_radius * max_radius - dy * dy)
        if max_r < 0:
            break
        for x in range(-half_w, half_w + 1):
            for z in range(-half_l, half_l + 1):
                r = math.sqrt(x * x + z * z)
                if r <= max_r:
                    if r >= max_r - 1.5:
                        blocks.append((x, y, z, roof_block))
                    elif r == 0:
                        # Center skylight
                        blocks.append((x, y, z, GLASS_LIGHT_BLUE))

    # Entrance
    door_z = half_l
    for dx in range(-2, 3):
        blocks.append((dx, 2, door_z, door_block))
        blocks.append((dx, 3, door_z, door_block))

    return blocks


def build_lg_complex_schematic(ft_w, ft_l, height_m, wall_block, door_block):
    """Build lecture hall complex (LG1-LG7) - long building with multiple sections."""
    blocks = []
    half_w = ft_w // 2
    half_l = ft_l // 2

    # Foundation
    for x in range(-half_w - 1, half_w + 2):
        for z in range(-half_l - 1, half_l + 2):
            blocks.append((x, 0, z, STONE_BRICKS))
            blocks.append((x, 1, z, STONE_BRICKS))

    # Walls
    for y in range(2, height_m + 1):
        is_top = (y == height_m)
        is_window_row = (y >= 3 and y < height_m and (y % 3) == 0)

        for x in range(-half_w, half_w + 1):
            for z in range(-half_l, half_l + 1):
                on_perimeter = (abs(x) == half_w or abs(z) == half_l)

                if is_top:
                    blocks.append((x, y, z, CONCRETE_BLACK))  # Dark roof
                elif on_perimeter:
                    if is_window_row:
                        blocks.append((x, y, z, GLASS_GRAY))
                    else:
                        blocks.append((x, y, z, wall_block))

    # Multiple entrances (every ft_w/5 along the length)
    section_w = ft_w // 5
    door_z = half_l
    for i in range(5):
        dx = -half_w + section_w * (i + 1) // 2 + section_w // 2
        blocks.append((dx, 2, door_z, door_block))

    return blocks


def build_bus_terminus_schematic(ft_w, ft_l, height_m, wall_block, door_block):
    """Build bus terminus - low shed with curved roof."""
    blocks = []
    half_w = ft_w // 2
    half_l = ft_l // 2

    # Foundation
    for x in range(-half_w - 1, half_w + 2):
        for z in range(-half_l - 1, half_l + 2):
            blocks.append((x, 0, z, STONE_BRICKS))

    # Open sides - just roof support pillars
    for x in [-half_w, 0, half_w]:
        for z in range(-half_l, half_l + 1):
            for y in range(1, height_m):
                blocks.append((x, y, z, wall_block))

    # Curved roof
    for x in range(-half_w, half_w + 1):
        for z in range(-half_l, half_l + 1):
            # Slope: y is higher in center
            y_offset = int((half_l - abs(z)) * 0.5)
            blocks.append((x, height_m + y_offset, z, GLASS_LIGHT_BLUE))
            blocks.append((x, height_m + y_offset - 1, z, CONCRETE_WHITE))

    return blocks


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
        roof_color = CONCRETE_WHITE
        accent_color = GLASS_LIGHT_BLUE
        door_block = OAK_DOOR

        name_lower = b['name'].lower()
        if 'sports' in name_lower or 'hall' in name_lower:
            blocks = build_sports_hall_schematic(ft_w, ft_l, int(b['height_m']), material, material, door_block)
        elif 'lecture' in name_lower or 'lg' in name_lower:
            blocks = build_lg_complex_schematic(ft_w, ft_l, int(b['height_m']), material, door_block)
        elif 'bus' in name_lower or 'terminus' in name_lower:
            blocks = build_bus_terminus_schematic(ft_w, ft_l, int(b['height_m']), material, door_block)
        elif 'hall' in name_lower or 'dormitory' in name_lower or 'ug' in name_lower or 'pg' in name_lower:
            blocks = build_dormitory_schematic(ft_w, ft_l, int(b['height_m']), material, accent_color, door_block)
        else:
            # Academic building (default)
            blocks = build_academic_schematic(ft_w, ft_l, int(b['height_m']), material, roof_color, door_block)

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