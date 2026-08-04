#!/usr/bin/env python3
"""
HKUST Minecraft v1.3 - OSM Building Injector
=============================================

Injects real-world building heights from OpenStreetMap into the HKUST world.
Uses OSM building=* tags with height/levels to create proportional block buildings.

Usage:
    # Dry run - print placement summary
    python3 inject_osm_buildings.py --world /path/to/world --dry-run

    # Inject all OSM buildings
    python3 inject_osm_buildings.py --world /path/to/world

Requirements:
    - HKUST OSM buildings JSON at data/hkust_osm_buildings_mc.json
    - Patched amulet-core (see patch_amulet_for_arnis.sh)
"""

import argparse
import math
import sys
from dataclasses import dataclass, field
from pathlib import Path

# Add local amulet patches path
sys.path.insert(0, '/Users/yahweh/Library/Python/3.11/lib/python/site-packages')

try:
    import amulet
    from amulet.api.block import Block
except ImportError as e:
    print(f"ERROR: amulet-core not available: {e}")
    print("Apply patch_amulet_for_arnis.sh first")
    sys.exit(1)

import json


# =============================================================================
# BLOCK SPECIFICATION
# =============================================================================

@dataclass
class BlockSpec:
    """Specification of a Minecraft block."""
    namespace: str
    name: str
    states: dict = field(default_factory=dict)

    def to_amulet(self):
        return Block(self.namespace, self.name)


# Material palette
QUARTZ_BLOCK = BlockSpec("minecraft", "quartz_block")
CONCRETE_GREY = BlockSpec("minecraft", "gray_concrete")
CONCRETE_WHITE = BlockSpec("minecraft", "white_concrete")
CONCRETE_BLUE = BlockSpec("minecraft", "blue_concrete")
CONCRETE_LIGHT_GRAY = BlockSpec("minecraft", "light_gray_concrete")
SMOOTH_STONE = BlockSpec("minecraft", "smooth_stone")
BRICK = BlockSpec("minecraft", "brick_block")
GLASS = BlockSpec("minecraft", "glass")
SEA_LANTERN = BlockSpec("minecraft", "sea_lantern")


# =============================================================================
# FOOTPRINT ESTIMATION
# =============================================================================

def get_building_footprint_size(btype: str, height_m: float, levels: int) -> tuple:
    """Estimate footprint dimensions (W, L) based on building type and height."""
    # High-rise dormitories (12+ levels) — narrow tower
    if btype == 'dormitory':
        if levels and int(levels) >= 10:
            return (10, 24)
        return (12, 26)
    # House
    if btype == 'house':
        return (5, 8)
    # University building — wider footprint
    if btype == 'university':
        return (40, 60)
    # Default
    if levels and int(levels) >= 10:
        return (10, 22)
    return (12, 18)


# =============================================================================
# BOX BUILDING GENERATOR
# =============================================================================

def build_box_schematic(
    height_m: int,
    footprint_w: int,
    footprint_l: int,
    wall_block: BlockSpec,
    top_block: BlockSpec,
    accent_block: BlockSpec,
    base_block: BlockSpec = None,
):
    """Build a box building schematic centered at local origin (0, 0)."""
    blocks = []
    if base_block is None:
        base_block = QUARTZ_BLOCK

    half_w = footprint_w // 2
    half_l = footprint_l // 2

    for y in range(height_m + 1):
        is_top = (y == height_m)
        is_foundation = (y == 0)
        # Window bands every 3 levels
        is_window_band = (
            y >= 2 and
            y < height_m and
            (y % 3 == 0)
        )

        for x in range(-half_w, half_w + 1):
            for z in range(-half_l, half_l + 1):
                # Foundation (always full footprint)
                if is_foundation:
                    blocks.append((x, 0, z, base_block))
                    continue

                # Walls (perimeter only)
                on_perimeter = (abs(x) == half_w or abs(z) == half_l)
                if on_perimeter:
                    if is_top:
                        blocks.append((x, y, z, top_block))
                    elif is_window_band:
                        blocks.append((x, y, z, accent_block))
                    else:
                        blocks.append((x, y, z, wall_block))
                    continue

                # Interior: roof top, otherwise empty
                if is_top:
                    blocks.append((x, y, z, top_block))

    return blocks


# =============================================================================
# MAIN INJECTION LOGIC
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Inject OSM HKUST buildings into Bedrock world'
    )
    parser.add_argument('--world', '-w', required=True,
                        help='Path to unzipped Bedrock world directory')
    parser.add_argument('--data', '-d', default='data/hkust_osm_buildings_mc.json',
                        help='Path to OSM buildings JSON (relative to project root)')
    parser.add_argument('--dry-run', '-n', action='store_true',
                        help='Print placements without modifying')
    parser.add_argument('--min-height', type=float, default=10.0,
                        help='Minimum building height in m to inject')
    parser.add_argument('--verbose', '-v', action='store_true')
    args = parser.parse_args()

    world_path = Path(args.world)
    if not (world_path / 'db').exists():
        print(f"ERROR: Not a Bedrock world (no db/ at {world_path})")
        sys.exit(1)

    # Load OSM data
    data_path = Path(__file__).parent.parent / args.data
    if not data_path.exists():
        print(f"ERROR: OSM data file not found: {data_path}")
        sys.exit(1)

    with open(data_path) as f:
        osm_data = json.load(f)

    buildings = osm_data['buildings']
    print(f"Loaded {len(buildings)} OSM buildings from {data_path}")

    # Filter by minimum height
    buildings = [b for b in buildings if b['height_m'] >= args.min_height]
    print(f"After min-height filter (>= {args.min_height}m): {len(buildings)}")

    if not buildings:
        print("No buildings to inject")
        return

    # Load world
    print(f"\nLoading world: {world_path}")
    level = amulet.load_level(str(world_path))
    dim = 'minecraft:overworld'
    ver = ('bedrock', (1, 21, 40))

    # Find ground height
    def find_ground_height(wx, wz):
        for by in range(200, 0, -1):
            try:
                b = level.get_version_block(wx, by, wz, dim, ver)
                if b[0].base_name != 'air':
                    return by
            except Exception:
                break
        return 60  # default

    print(f"\nBuilding placements:")
    total_blocks = 0
    skipped = []

    for b in buildings:
        # Determine footprint
        ft_w, ft_l = get_building_footprint_size(b['building_type'], b['height_m'], b['levels'])

        # Find ground
        gy = find_ground_height(b['mc_x'], b['mc_z'])

        # Skip if too low (likely ocean)
        if gy < 40:
            skipped.append((b['name'], gy, b['mc_x'], b['mc_z']))
            continue

        # Determine material
        name = b.get('name', '')
        if 'Hall' in name or '宿舍' in name or 'Tower' in name or '研究生' in name or 'Stud' in name:
            material = CONCRETE_LIGHT_GRAY
            roof = CONCRETE_WHITE
            accent = GLASS
        elif b['building_type'] == 'house':
            material = BRICK
            roof = BRICK
            accent = GLASS
        else:
            material = CONCRETE_GREY
            roof = SMOOTH_STONE
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
            print(f"  {name[:40]:40} MC=({b['mc_x']}, {gy+1}, {b['mc_z']}) "
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
        print(f"\nSkipped {len(skipped)} buildings (likely ocean, gy<40):")
        for name, gy, wx, wz in skipped:
            print(f"  {name[:40]:40} gy={gy} MC=({wx},{wz})")

    if args.dry_run:
        print(f"\n[DRY RUN] Would place {total_blocks} blocks for {len(buildings) - len(skipped)} buildings")
        level.close()
        return

    print(f"\nInjecting complete: {total_blocks} blocks for {len(buildings)} buildings")
    print(f"Saving world...")
    level.save()
    level.close()
    print(f"Done!")


if __name__ == '__main__':
    main()