#!/usr/bin/env python3
"""
v1.5-C: Add dynamic elements (vehicles).
- Minecart train near the bus terminus (3 cars)
- Boat at the waterfront
- Bus at bus terminus
- Helicopter on rooftop (decorative)
"""
import sys
from pathlib import Path
import shutil

WORKDIR = Path("/Users/yahweh/Desktop/ai应用社/hkust-minecraft")
SRC = WORKDIR / "worlds/working/v1.5d"
DST = WORKDIR / "worlds/working/v1.5e"

sys.path.insert(0, '/Users/yahweh/Library/Python/3.11/lib/python/site-packages')

from amulet import level as amulet_level
from amulet.api.block import Block


def B(ns, name):
    return Block(ns, name)


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
        if b and b[0].base_name not in ("air", "water"):
            return y
    return 60


def build_train(level, base_x, base_z):
    """Build a 3-car metro train."""
    placed = 0
    gy = get_ground_y(level, base_x, base_z)
    # Place rail at ground level
    rail = B("minecraft", "rail")
    powered_rail = B("minecraft", "powered_rail")
    activator_rail = B("minecraft", "activator_rail")
    # Rails along x-axis, 30 blocks long
    for x in range(base_x - 15, base_x + 16):
        place(level, x, gy, base_z, rail)
        placed += 1
    # 3 train cars (each 4 blocks long, 2 blocks wide, 2 blocks tall)
    car_color = B("minecraft", "gray_concrete")
    window = B("minecraft", "light_blue_stained_glass")
    for car_idx, car_x in enumerate([-10, -2, 6]):
        cx = base_x + car_x
        # Car body
        for dx in range(4):
            for dz in range(2):
                for dy in range(2):
                    place(level, cx + dx, gy + 1 + dy, base_z - 1 + dz, car_color)
                    placed += 1
        # Windows on sides
        for dx in range(1, 3):
            place(level, cx + dx, gy + 2, base_z - 2, window)
            place(level, cx + dx, gy + 2, base_z + 1, window)
            placed += 2
    return placed


def build_bus(level, base_x, base_z):
    """Build a red double-decker-style bus at bus terminus."""
    placed = 0
    gy = get_ground_y(level, base_x, base_z)
    body = B("minecraft", "red_concrete")
    window = B("minecraft", "light_blue_stained_glass")
    black = B("minecraft", "black_concrete")
    # Bus body: 8 long, 2 wide, 3 tall
    for dx in range(8):
        for dz in range(2):
            for dy in range(3):
                place(level, base_x + dx, gy + 1 + dy, base_z - 1 + dz, body)
                placed += 1
    # Windows on top 2 levels
    for dx in range(1, 7):
        place(level, base_x + dx, gy + 3, base_z - 2, window)
        place(level, base_x + dx, gy + 3, base_z + 1, window)
        placed += 2
    # Wheels
    for wx in [1, 6]:
        place(level, base_x + wx, gy + 1, base_z - 2, black)
        place(level, base_x + wx, gy + 1, base_z + 1, black)
        placed += 2
    return placed


def build_boat(level, base_x, base_z):
    """Build a small boat in the water near waterfront."""
    placed = 0
    # Boat: oak planks hull, white sail
    hull = B("minecraft", "oak_planks")
    sail = B("minecraft", "white_wool")
    mast = B("minecraft", "oak_fence")
    # Hull at water level (y around 60)
    for dx in range(5):
        for dz in range(2):
            for dy in range(2):
                place(level, base_x + dx, 60 + dy, base_z - 1 + dz, hull)
                placed += 1
    # Mast
    place(level, base_x + 2, 63, base_z, mast)
    place(level, base_x + 2, 64, base_z, mast)
    place(level, base_x + 2, 65, base_z, mast)
    placed += 3
    # Sail
    for dy in range(3):
        place(level, base_x + 2, 64 + dy, base_z - 1, sail)
        placed += 1
    return placed


def build_helicopter(level, base_x, base_z, base_y):
    """Build a helicopter on a roof (decorative)."""
    placed = 0
    body = B("minecraft", "light_gray_concrete")
    glass = B("minecraft", "light_blue_stained_glass")
    rotor = B("minecraft", "quartz_block")
    # Body
    for dx in range(3):
        for dz in range(3):
            for dy in range(2):
                place(level, base_x + dx, base_y + dy, base_z + dz, body)
                placed += 1
    # Cockpit window
    place(level, base_x + 2, base_y + 1, base_z + 1, glass)
    placed += 1
    # Rotor on top
    place(level, base_x + 1, base_y + 3, base_z + 1, rotor)
    place(level, base_x + 1, base_y + 4, base_z + 1, rotor)
    placed += 2
    return placed


def main():
    if DST.exists():
        shutil.rmtree(DST)
    shutil.copytree(SRC, DST)
    print(f"Loading {DST}")
    level = amulet_level.load_level(str(DST))

    total = 0
    print("\n=== Adding dynamic elements ===")
    total += build_train(level, 360, 410)
    print("  → Train at bus terminus")
    total += build_bus(level, 380, 410)
    print("  → Bus at bus terminus")
    total += build_boat(level, 70, 70)
    print("  → Boat at waterfront")
    # Helicopter on Sports Hall roof
    total += build_helicopter(level, 88, 228, 70)
    print("  → Helicopter on Sports Hall roof")

    level.close()
    print(f"\n=== Total dynamic blocks: ~{total} ===")
    print(f"Saved to: {DST}")


if __name__ == "__main__":
    main()
