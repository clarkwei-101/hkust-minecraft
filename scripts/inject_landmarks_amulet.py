#!/usr/bin/env python3
"""
HKUST Minecraft v1.1 - Landmark Injector (amulet-based)
=======================================================
Injects hand-built landmark schematics into a Bedrock LevelDB world.

Uses amulet's set_version_block() which works with Arnis-generated chunks
after applying the compatibility patches.

Requirements:
    pip install amulet-core leveldb

Usage:
    # Dry run - scan terrain and print placements
    python3 inject_landmarks_amulet.py --world /path/to/world --dry-run

    # Inject landmarks
    python3 inject_landmarks_amulet.py --world /path/to/world

    # Inject to extracted mcworld
    python3 inject_landmarks_amulet.py --world /tmp/hkust_noextend
"""

import argparse
import math
import struct
import sys
import os
import shutil
import zipfile
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional

# Add local amulet patches path
sys.path.insert(0, '/Users/yahweh/Library/Python/3.11/lib/python/site-packages')

import amulet
from amulet.api.block import Block

# =============================================================================
# BLOCK DEFINITIONS
# =============================================================================

@dataclass
class BlockSpec:
    """A named block with optional states."""
    namespace: str
    name: str
    states: Dict[str, any] = field(default_factory=dict)

    def to_amulet(self) -> Block:
        return Block(self.namespace, self.name)

    def __repr__(self):
        if self.states:
            s = ','.join(f'{k}={v}' for k, v in self.states.items())
            return f"{self.namespace}:{self.name}[{s}]"
        return f"{self.namespace}:{self.name}"


# Material palette
CONCRETE_WHITE = BlockSpec("minecraft", "white_concrete")
CONCRETE_BLUE = BlockSpec("minecraft", "blue_concrete")
CONCRETE_BLACK = BlockSpec("minecraft", "black_concrete")
POLISHED_GRANITE = BlockSpec("minecraft", "polished_granite")
POLISHED_DIORITE = BlockSpec("minecraft", "polished_diorite")
POLISHED_ANDESITE = BlockSpec("minecraft", "polished_andesite")
SMOOTH_STONE = BlockSpec("minecraft", "smooth_stone")
GLASS = BlockSpec("minecraft", "glass")
GLASS_LIGHT_BLUE = BlockSpec("minecraft", "light_blue_stained_glass")
SEA_LANTERN = BlockSpec("minecraft", "sea_lantern")
QUARTZ_PILLAR = BlockSpec("minecraft", "quartz_pillar", {"axis": "y"})
DARK_OAK_FENCE = BlockSpec("minecraft", "dark_oak_fence")
OAK_SLAB = BlockSpec("minecraft", "oak_slab", {"top_slot_bit": False})
WATER = BlockSpec("minecraft", "water")
BRICK = BlockSpec("minecraft", "brick_block")
GOLD_BLOCK = BlockSpec("minecraft", "gold_block")


# =============================================================================
# SCHEMATIC BUILDERS
# =============================================================================

@dataclass
class LandmarkSchematic:
    """A landmark schematic definition."""
    name: str
    display_name: str
    blocks: List[Tuple[int, int, int, BlockSpec]]  # (rx, ry, rz, block)

    @property
    def size(self) -> Tuple[int, int, int]:
        xs = [b[0] for b in self.blocks]
        ys = [b[1] for b in self.blocks]
        zs = [b[2] for b in self.blocks]
        return (max(xs) - min(xs) + 1, max(ys) - min(ys) + 1, max(zs) - min(zs) + 1)


def build_academic_dome() -> LandmarkSchematic:
    """Academic Building Dome — hemisphere radius 20, height 25."""
    blocks = []
    R = 20
    H = 25

    for x in range(-R, R + 1):
        for z in range(-R, R + 1):
            r = math.sqrt(x * x + z * z)
            if r > R:
                continue

            # Foundation floor
            blocks.append((x, 0, z, POLISHED_GRANITE))

            # Columns (y 1-8) — outer ring
            if R - 2 <= r <= R:
                for y in range(1, 9):
                    blocks.append((x, y, z, POLISHED_ANDESITE))

            # Dome hemisphere (y 9-25)
            for y in range(9, H + 1):
                dy = y - 9
                max_r = math.sqrt(R * R - dy * dy)
                if r <= max_r:
                    if r >= max_r - 1.5:
                        blocks.append((x, y, z, CONCRETE_WHITE))
                    elif r < R - 2 and y == 9:
                        blocks.append((x, y, z, POLISHED_DIORITE))

            # Skylight (y = 24, center)
            if r < 4:
                blocks.append((x, 24, z, GLASS_LIGHT_BLUE))

    return LandmarkSchematic(
        name="academic-dome",
        display_name="Academic Building Dome",
        blocks=blocks,
    )


def build_circle_of_time() -> LandmarkSchematic:
    """Circle of Time sundial plaza — radius 10."""
    blocks = []
    R = 10

    for x in range(-R, R + 1):
        for z in range(-R, R + 1):
            r = math.sqrt(x * x + z * z)
            if r > R:
                continue

            # Plaza floor
            blocks.append((x, 0, z, POLISHED_DIORITE))

            # Raised platform center (r < 4)
            if r < 4:
                blocks.append((x, 1, z, POLISHED_GRANITE))

            # Gnomon (sundial pointer) at center
            if abs(x) <= 0 and abs(z) <= 0:
                for gy in range(1, 7):
                    blocks.append((0, gy, 0, CONCRETE_BLACK))

            # Compass hour markers (12, 3, 6, 9 o'clock)
            for angle_deg in [0, 90, 180, 270]:
                rad = math.radians(angle_deg)
                hx = round(R * 0.85 * math.sin(rad))
                hz = round(R * 0.85 * math.cos(rad))
                hr = math.sqrt(hx * hx + hz * hz)
                if hr <= R and hr >= R - 2:
                    blocks.append((hx, 1, hz, QUARTZ_PILLAR))

            # Decorative border rings
            if abs(r - (R - 1)) < 1:
                blocks.append((x, 0, z, SMOOTH_STONE))

    return LandmarkSchematic(
        name="circle-of-time",
        display_name="Circle of Time Sundial",
        blocks=blocks,
    )


def build_one_world_fountain() -> LandmarkSchematic:
    """One-World Fountain — radius 8."""
    blocks = []
    R = 8

    for x in range(-R, R + 1):
        for z in range(-R, R + 1):
            r = math.sqrt(x * x + z * z)
            if r > R:
                continue

            # Basin floor
            blocks.append((x, 0, z, POLISHED_GRANITE))

            # Basin wall (outer ring)
            if r >= R - 1:
                blocks.append((x, 1, z, CONCRETE_BLUE))
                blocks.append((x, 2, z, CONCRETE_BLUE))

            # Inner decorative ring
            if R - 3 <= r <= R - 1:
                blocks.append((x, 1, z, POLISHED_ANDESITE))

            # Central pillar with water
            if r < 1:
                blocks.append((0, 1, 0, SEA_LANTERN))
                blocks.append((0, 2, 0, SEA_LANTERN))
                blocks.append((0, 3, 0, GOLD_BLOCK))  # top ornament

            # Water surface (r < R - 2)
            if r < R - 2 and r >= 1:
                blocks.append((x, 2, z, WATER))

    return LandmarkSchematic(
        name="one-world-fountain",
        display_name="One-World Fountain",
        blocks=blocks,
    )


def build_seaview_walkway() -> LandmarkSchematic:
    """Seaview walkway with railings — length 80."""
    blocks = []
    L = 80

    for i in range(L):
        # Floor (oak slabs)
        blocks.append((i, 0, 0, OAK_SLAB))
        blocks.append((i, 0, 1, OAK_SLAB))
        blocks.append((i, 0, 2, OAK_SLAB))

        # Railings
        blocks.append((i, 1, 0, DARK_OAK_FENCE))
        blocks.append((i, 2, 0, DARK_OAK_FENCE))
        blocks.append((i, 1, 3, DARK_OAK_FENCE))
        blocks.append((i, 2, 3, DARK_OAK_FENCE))

        # Pillars every 8 blocks
        if i % 8 == 0:
            blocks.append((i, 1, 0, BRICK))
            blocks.append((i, 2, 0, BRICK))
            blocks.append((i, 3, 0, BRICK))
            blocks.append((i, 1, 3, BRICK))
            blocks.append((i, 2, 3, BRICK))
            blocks.append((i, 3, 3, BRICK))

    return LandmarkSchematic(
        name="seaview-walkway",
        display_name="Seaview Walkway",
        blocks=blocks,
    )


def build_library_landmark() -> LandmarkSchematic:
    """HKUST Library — tall rectangular glass building."""
    blocks = []
    W, H, D = 24, 18, 18

    for x in range(W):
        for z in range(D):
            for y in range(H):
                # Exterior walls
                if x == 0 or x == W - 1 or z == 0 or z == D - 1:
                    if y < H - 2:
                        blocks.append((x, y, z, GLASS))
                    else:
                        blocks.append((x, y, z, CONCRETE_WHITE))
                # Floor and ceiling
                elif y == 0 or y == H - 1:
                    blocks.append((x, y, z, POLISHED_DIORITE))
                # Interior columns
                elif y % 5 == 0 and x % 6 == 0 and z % 6 == 0:
                    blocks.append((x, y, z, POLISHED_ANDESITE))

    return LandmarkSchematic(
        name="library",
        display_name="HKUST Library",
        blocks=blocks,
    )


# =============================================================================
# WORLD SCANNER & LANDMARK PLACEMENTS
# =============================================================================

# HKUST landmark world positions (verified from terrain scan)
# Format: (landmark_name, world_x, world_z, description)
# Heights will be auto-detected by terrain scanning

LANDMARK_DEFINITIONS = [
    # 1. Academic Building Dome — on high plateau (terrain ~Y=126)
    # Matches OSM location, verified on smooth stone plateau
    dict(name="academic-dome",   world_x=200, world_z=500, description="Academic Building Dome on plateau"),
    # 2. Circle of Time Sundial — adjacent south, on same plateau
    dict(name="circle-of-time",  world_x=185, world_z=530, description="Circle of Time sundial plaza"),
    # 3. One-World Fountain — in front of Academic, on grass area (terrain ~Y=77, concrete)
    dict(name="one-world-fountain", world_x=279, world_z=663, description="One-World Fountain"),
    # 4. Seaview Walkway — along the east coast
    dict(name="seaview-walkway",  world_x=480, world_z=380, description="Seaview walkway along coast"),
    # 5. Library — north campus
    dict(name="library",          world_x=130, world_z=580, description="HKUST Library building"),
]


# =============================================================================
# AMULET-BASED INJECTION
# =============================================================================

def find_ground_height(level, wx: int, wz: int, dim: str, ver) -> int:
    """Scan downward from Y=200 to find first non-air block."""
    for by in range(200, 0, -1):
        try:
            b = level.get_version_block(wx, by, wz, dim, ver)
            if b[0].base_name != 'air':
                return by
        except Exception:
            break
    return 64


def inject_landmark(
    level,
    schematic: LandmarkSchematic,
    wx: int, wz: int,
    dim: str,
    ver,
    dry_run: bool = False,
) -> int:
    """Inject a landmark schematic into the world at given XZ position.

    Returns the number of blocks placed.
    """
    # Find ground height
    ground_y = find_ground_height(level, wx, wz, dim, ver)
    wy_base = ground_y + 1  # place on top of ground

    print(f"  {schematic.display_name}: base=({wx}, {wy_base}, {wz}), ground={ground_y}")

    placed = 0
    for rx, ry, rz, block_spec in schematic.blocks:
        bx = wx + rx
        by = wy_base + ry
        bz = wz + rz

        if dry_run:
            if placed < 5:
                print(f"    [DRY] {block_spec} at ({bx}, {by}, {bz})")
        else:
            try:
                amulet_block = block_spec.to_amulet()
                level.set_version_block(bx, by, bz, dim, ver, amulet_block)
                placed += 1
            except Exception as e:
                print(f"    ERROR placing {block_spec} at ({bx},{by},{bz}): {e}")

    if not dry_run:
        print(f"  Placed {placed} blocks")

    return placed


def main():
    parser = argparse.ArgumentParser(
        description='Inject HKUST landmarks into Bedrock world (amulet-based)'
    )
    parser.add_argument('--world', '-w', required=True,
                        help='Path to unzipped Bedrock world directory')
    parser.add_argument('--dry-run', '-n', action='store_true',
                        help='Scan terrain and print placements without modifying')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Verbose output')
    args = parser.parse_args()

    world_path = Path(args.world)
    if not (world_path / 'db').exists():
        print(f"ERROR: Not a Bedrock world (no db/ at {world_path})")
        sys.exit(1)

    print(f"Loading world: {world_path}")
    level = amulet.load_level(str(world_path))
    dim = 'minecraft:overworld'
    ver = ('bedrock', (1, 21, 40))

    # Build schematics
    schematics = {
        "academic-dome": build_academic_dome(),
        "circle-of-time": build_circle_of_time(),
        "one-world-fountain": build_one_world_fountain(),
        "seaview-walkway": build_seaview_walkway(),
        "library": build_library_landmark(),
    }

    print(f"\nSchematics built:")
    for name, sch in schematics.items():
        print(f"  {sch.display_name}: {len(sch.blocks)} blocks")

    # Build placements
    placements = []
    for defn in LANDMARK_DEFINITIONS:
        sch = schematics.get(defn['name'])
        if sch:
            placements.append({
                'schematic': sch,
                'x': defn['world_x'],
                'z': defn['world_z'],
                'desc': defn['description'],
            })

    print(f"\nLandmark placements:")
    for p in placements:
        gy = find_ground_height(level, p['x'], p['z'], dim, ver)
        print(f"  {p['schematic'].display_name}: ({p['x']}, {gy+1}, {p['z']}) — {p['desc']}")

    if args.dry_run:
        print("\n[DRY RUN] No changes written.")
        level.close()
        return

    print("\nInjecting landmarks...")
    total = 0
    for p in placements:
        n = inject_landmark(level, p['schematic'], p['x'], p['z'], dim, ver)
        total += n

    print(f"\nSaving world ({total} blocks placed)...")
    level.save()
    level.close()
    print("Done!")


if __name__ == '__main__':
    main()
