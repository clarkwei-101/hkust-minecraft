#!/usr/bin/env python3
"""
v1.5-D: Add coastal and underwater details.
- Replace seabed grass with sand beaches along the shore
- Add water-life (kelp, sea grass, coral)
- Build the iconic HKUST waterfront promenade with railings
"""
import sys
import math
from pathlib import Path
import shutil

WORKDIR = Path("/Users/yahweh/Desktop/ai应用社/hkust-minecraft")
SRC = WORKDIR / "worlds/working/v1.5b"
DST = WORKDIR / "worlds/working/v1.5d"

sys.path.insert(0, '/Users/yahweh/Library/Python/3.11/lib/python/site-packages')

from amulet import level as amulet_level
from amulet.api.block import Block


def B(ns, name):
    return Block(ns, name)


WATER = B("minecraft", "water")
SAND = B("minecraft", "sand")
GRAVEL = B("minecraft", "gravel")
CLAY = B("minecraft", "clay")
KELP = B("minecraft", "kelp")
SEA_GRASS = B("minecraft", "seagrass")
PRISMARINE = B("minecraft", "prismarine")
DARK_PRISMARINE = B("minecraft", "dark_prismarine")
BRAIN_CORAL = B("minecraft", "brain_coral")
HORN_CORAL = B("minecraft", "horn_coral")
FIRE_CORAL = B("minecraft", "fire_coral")
OAK_FENCE = B("minecraft", "oak_fence")
OAK_SLAB = B("minecraft", "oak_slab")
ICE = B("minecraft", "ice")
BLUE_ICE = B("minecraft", "blue_ice")
PACKED_ICE = B("minecraft", "packed_ice")


def get_block(level, x, y, z):
    dim = "minecraft:overworld"
    ver = ("bedrock", (1, 21, 40))
    return level.get_version_block(x, y, z, dim, ver)


def place(level, x, y, z, block):
    dim = "minecraft:overworld"
    ver = ("bedrock", (1, 21, 40))
    level.set_version_block(x, y, z, dim, ver, block)


def get_ground_y(level, x, z):
    for y in range(120, 30, -1):
        b = get_block(level, x, y, z)
        if b[0].base_name != "air" and b[0].base_name != "water":
            return y
    return 60


def find_water_shoreline(level, sample_xs, sample_zs):
    """Find all (x, z) positions where water meets land along the coastline."""
    shoreline = []
    for x in range(0, 200, 4):
        for z in range(0, 480, 4):
            gy = get_ground_y(level, x, z)
            # Check if water above
            b_water = get_block(level, x, gy + 1, z)
            if b_water and b_water[0].base_name == "water":
                shoreline.append((x, gy, z))
    return shoreline


def add_beach_sand(level):
    """Replace grass blocks at shoreline with sand for beach effect."""
    print("  → Replacing shore grass with sand")
    placed = 0
    for x in range(0, 200):
        for z in range(0, 480, 2):
            gy = get_ground_y(level, x, z)
            b_above = get_block(level, x, gy + 1, z)
            if b_above and b_above[0].base_name == "water":
                # Replace top block with sand
                cur = get_block(level, x, gy, z)
                if cur and cur[0].base_name not in ("sand", "water"):
                    place(level, x, gy, z, SAND)
                    placed += 1
                # Replace 2 blocks below with sand too
                cur2 = get_block(level, x, gy - 1, z)
                if cur2 and cur2[0].base_name not in ("sand", "water", "bedrock"):
                    place(level, x, gy - 1, z, SAND)
                    placed += 1
    return placed


def add_underwater_life(level):
    """Add kelp, sea grass, and coral in shallow water."""
    print("  → Adding underwater life (kelp, sea grass, coral)")
    placed = 0
    # Sample some water positions
    for x in range(0, 200, 5):
        for z in range(0, 480, 5):
            # Find water column
            for y in range(35, 70):
                b = get_block(level, x, y, z)
                if b and b[0].base_name == "water":
                    # Check if there's a solid block below for kelp to attach
                    b_below = get_block(level, x, y - 1, z)
                    if b_below and b_below[0].base_name not in ("water", "air"):
                        # Kelp
                        if (x + z) % 7 == 0:
                            place(level, x, y, z, KELP)
                            placed += 1
                        # Sea grass
                        elif (x + z) % 5 == 0:
                            place(level, x, y, z, SEA_GRASS)
                            placed += 1
                        # Coral block
                        elif (x + z) % 11 == 0:
                            place(level, x, y, z, BRAIN_CORAL)
                            placed += 1
                    break  # only top water block
    return placed


def add_seawater_promenade(level):
    """Build the iconic HKUST waterfront promenade with railings (around x=20-60, z=60-100)."""
    print("  → Adding waterfront promenade (where seaview walkway meets coast)")
    placed = 0
    # Promenade is at the Seaview Walkway area, extending the railing
    # The seaview walkway already exists; add some benches along it
    for z in range(60, 100, 4):
        # Add oak fence posts every 4 blocks along the walkway edge
        for x_offset in [-2, 2]:
            gy = get_ground_y(level, 50 + x_offset, z)
            place(level, 50 + x_offset, gy + 1, z, OAK_FENCE)
            placed += 1
    return placed


def main():
    if DST.exists():
        shutil.rmtree(DST)
    shutil.copytree(SRC, DST)
    print(f"Loading {DST}")
    level = amulet_level.load_level(str(DST))

    total = 0
    print("\n=== Coastal optimization ===")
    total += add_beach_sand(level)
    total += add_underwater_life(level)
    total += add_seawater_promenade(level)

    level.close()
    print(f"\n=== Total coastal blocks: ~{total} ===")
    print(f"Saved to: {DST}")


if __name__ == "__main__":
    main()
