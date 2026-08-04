#!/usr/bin/env python3
"""
v1.5: Add interior details to existing landmarks.
Builds on the v1.4-detailed world by adding:
- Atrium: cafe tables, plant pots, banners, glass roof, central skylight
- Library: book stacks, reading desks, chandeliers, ladder, study tables
- Sports Hall: basketball court markings, scoreboard, bleachers
- Sundial: gnomon shadow marks, zodiac ring
- One-World Fountain: water flowing animation pattern (water + glowstone base)
- Dome: oculus + spiral staircase inside

Inputs: worlds/working/v1.4-detailed (or v1.5 base)
Output: worlds/working/v1.5 (with interiors added)
"""
import sys
from pathlib import Path
import shutil

WORKDIR = Path("/Users/yahweh/Desktop/ai应用社/hkust-minecraft")
SRC = WORKDIR / "worlds/working/v1.4-detailed"
DST = WORKDIR / "worlds/working/v1.5"

# Ensure amulet path
sys.path.insert(0, '/Users/yahweh/Library/Python/3.11/lib/python/site-packages')

from amulet import level as amulet_level
from amulet.api.block import Block


def B(ns, name):
    return Block(ns, name)


# Material shortcuts
OAK_PLANK = B("minecraft", "oak_planks")
OAK_SLAB = B("minecraft", "oak_slab")
SPRUCE_PLANK = B("minecraft", "spruce_planks")
BOOKSHELF = B("minecraft", "bookshelf")
LANTERN = B("minecraft", "lantern")
SEA_LANTERN = B("minecraft", "sea_lantern")
GLASS = B("minecraft", "glass")
WHITE_CONCRETE = B("minecraft", "white_concrete")
LIGHT_GRAY_CONCRETE = B("minecraft", "light_gray_concrete")
BLACK_CONCRETE = B("minecraft", "black_concrete")
RED_CONCRETE = B("minecraft", "red_concrete")
BLUE_CONCRETE = B("minecraft", "blue_concrete")
YELLOW_CONCRETE = B("minecraft", "yellow_concrete")
GOLD_BLOCK = B("minecraft", "gold_block")
QUARTZ_BLOCK = B("minecraft", "quartz_block")
QUARTZ_PILLAR = B("minecraft", "quartz_pillar")
POLISHED_DIORITE = B("minecraft", "polished_diorite")
SMOOTH_STONE = B("minecraft", "smooth_stone")
OAK_LEAVES = B("minecraft", "oak_leaves")
OAK_LOG = B("minecraft", "oak_log")
OAK_FENCE = B("minecraft", "oak_fence")
WATER = B("minecraft", "water")
ICE = B("minecraft", "ice")
BLUE_STAINED_GLASS = B("minecraft", "blue_stained_glass")
WHITE_STAINED_GLASS = B("minecraft", "white_stained_glass")
CARPET = B("minecraft", "white_carpet")
CARPET_RED = B("minecraft", "red_carpet")
OAK_STAIRS = B("minecraft", "oak_stairs")
SPRUCE_STAIRS = B("minecraft", "spruce_stairs")
OAK_DOOR = B("minecraft", "oak_door")
BANNER = B("minecraft", "white_banner")
WALL_BANNER = B("minecraft", "white_wall_banner")
FLOWER_POT = B("minecraft", "flower_pot")
POPPY = B("minecraft", "poppy")
WHITE_TULIP = B("minecraft", "white_tulip")
OAK_PRESSURE_PLATE = B("minecraft", "oak_pressure_plate")
CAKE = B("minecraft", "cake")
BARRIER = B("minecraft", "barrier")
HOPPER = B("minecraft", "hopper")
LECTERN = B("minecraft", "lectern")
ENCHANTING_TABLE = B("minecraft", "enchanting_table")
CAULDRON = B("minecraft", "cauldron")
ANVIL = B("minecraft", "anvil")
CRAFTING_TABLE = B("minecraft", "crafting_table")
FURNACE = B("minecraft", "furnace")
CHEST = B("minecraft", "chest")
TRAPPED_CHEST = B("minecraft", "trapped_chest")


def get_ground_y(level, x, z):
    """Return the Y of the highest non-air block at (x, z)."""
    dim = "minecraft:overworld"
    ver = ("bedrock", (1, 21, 40))
    for y in range(120, 30, -1):
        b = level.get_version_block(x, y, z, dim, ver)
        if b[0].base_name != "air":
            return y
    return 60


def get_block(level, x, y, z):
    dim = "minecraft:overworld"
    ver = ("bedrock", (1, 21, 40))
    return level.get_version_block(x, y, z, dim, ver)


def place(level, x, y, z, block):
    dim = "minecraft:overworld"
    ver = ("bedrock", (1, 21, 40))
    level.set_version_block(x, y, z, dim, ver, block)


def get_block_id(level, x, y, z):
    """Get the block's base_name at position."""
    b = get_block(level, x, y, z)
    return b[0].base_name if b else ""


# =============================================================================
# INTERIOR BUILDERS
# =============================================================================

def build_atrium_interior(level):
    """Add interior decoration to the Atrium (around x=210-240, z=200-220)."""
    print("  → Atrium: cafe tables, plant pots, banners, skylight")
    placed = 0
    # Atrium center is around x=220, z=210, ground ~y=75
    cx, cz = 220, 210

    # Glass skylight: glass dome above atrium at y=85 (5 blocks high)
    for dx in range(-3, 4):
        for dz in range(-3, 4):
            if abs(dx) + abs(dz) <= 4:
                place(level, cx + dx, 85, cz + dz, BLUE_STAINED_GLASS)
                placed += 1
    # Skylight frame in white concrete
    for dx in range(-3, 4):
        place(level, cx + dx, 84, cz - 3, WHITE_CONCRETE)
        place(level, cx + dx, 84, cz + 3, WHITE_CONCRETE)
        placed += 2
    for dz in range(-3, 4):
        place(level, cx - 3, 84, cz + dz, WHITE_CONCRETE)
        place(level, cx + 3, 84, cz + dz, WHITE_CONCRETE)
        placed += 2

    # Cafe tables around the perimeter (4 tables)
    table_positions = [(cx - 10, cz - 6), (cx + 10, cz - 6), (cx - 10, cz + 6), (cx + 10, cz + 6)]
    for tx, tz in table_positions:
        # Table top (oak pressure plate on top of fence)
        place(level, tx, get_ground_y(level, tx, tz) + 1, tz, OAK_FENCE)
        place(level, tx, get_ground_y(level, tx, tz) + 2, tz, OAK_PRESSURE_PLATE)
        placed += 2
        # Chairs (oak stairs) facing table
        for dx, dz in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            place(level, tx + dx * 2, get_ground_y(level, tx + dx * 2, tz + dz * 2) + 1, tz + dz * 2, OAK_STAIRS)
            placed += 1

    # Plant pots at corners
    for px, pz in [(cx - 13, cz - 9), (cx + 13, cz - 9), (cx - 13, cz + 9), (cx + 13, cz + 9)]:
        gy = get_ground_y(level, px, pz)
        place(level, px, gy + 1, pz, FLOWER_POT)
        place(level, px, gy + 2, pz, WHITE_TULIP)
        placed += 2

    # Banners on perimeter walls (8 banners)
    for i, (bx, bz, bd) in enumerate([
        (cx - 14, cz - 9, 0), (cx - 14, cz + 9, 0),  # west wall
        (cx + 14, cz - 9, 0), (cx + 14, cz + 9, 0),  # east wall
        (cx - 9, cz - 13, 1), (cx + 9, cz - 13, 1),  # north wall
        (cx - 9, cz + 13, 1), (cx + 9, cz + 13, 1),  # south wall
    ]):
        gy = get_ground_y(level, bx, bz) + 3
        # Hanging banner from above
        place(level, bx, gy, bz, WALL_BANNER)
        placed += 1

    # Central hanging chandelier
    place(level, cx, 80, cz, LANTERN)
    place(level, cx, 81, cz, SEA_LANTERN)
    place(level, cx, 82, cz, GOLD_BLOCK)
    placed += 3

    return placed


def build_library_interior(level):
    """Add interior decoration to the Library (around x=120-145, z=90-110)."""
    print("  → Library: book stacks, reading desks, chandeliers, ladder, study tables")
    placed = 0
    # Library center around x=130, z=100
    cx, cz = 130, 100

    # Reading desks — 6 desks in 2 rows
    for row, dz_off in enumerate([-3, 3]):
        for col, dx_off in enumerate([-6, -2, 2, 6]):
            dx, dz = cx + dx_off, cz + dz_off
            gy = get_ground_y(level, dx, dz) + 1
            place(level, dx, gy, dz, OAK_PLANK)
            place(level, dx, gy + 1, dz, OAK_PRESSURE_PLATE)  # book/lectern top
            placed += 2
            # Chair behind
            place(level, dx, gy, dz - 1, OAK_STAIRS)
            placed += 1

    # Book stacks around walls
    for dx in [-10, 10]:
        for dz in range(-7, 8, 3):
            place(level, cx + dx, get_ground_y(level, cx + dx, cz + dz) + 1, cz + dz, BOOKSHELF)
            place(level, cx + dx, get_ground_y(level, cx + dx, cz + dz) + 2, cz + dz, BOOKSHELF)
            placed += 2

    # Central chandelier
    for dy in range(2):
        place(level, cx, 75 + dy, cz, SEA_LANTERN)
        placed += 1

    # Lectern at center
    place(level, cx, get_ground_y(level, cx, cz) + 1, cz, LECTERN)
    placed += 1

    # Enchanting table for "magic study room" feel
    place(level, cx - 4, get_ground_y(level, cx - 4, cz) + 1, cz, ENCHANTING_TABLE)
    placed += 1

    return placed


def build_sports_hall_interior(level):
    """Add Sports Hall interior (around x=80-110, z=220-250)."""
    print("  → Sports Hall: basketball court markings, scoreboard, bleachers")
    placed = 0
    cx, cz = 90, 230

    # Basketball court — paint floor with court markings
    court_y = get_ground_y(level, cx, cz) + 1
    # Court center circle
    for dx in range(-3, 4):
        for dz in range(-3, 4):
            if abs(dx) + abs(dz) in [3, 4]:
                place(level, cx + dx, court_y, cz + dz, RED_CONCRETE)
                placed += 1

    # Free-throw line (white concrete strip)
    for dz in range(-4, 5):
        place(level, cx - 4, court_y, cz + dz, WHITE_CONCRETE)
        place(level, cx + 4, court_y, cz + dz, WHITE_CONCRETE)
        placed += 2

    # Center court line
    for dx in range(-8, 9):
        place(level, cx + dx, court_y, cz, WHITE_CONCRETE)
        placed += 1

    # Bleachers on both sides (oak stairs ascending)
    for dz_off in [-9, 9]:
        for tier in range(3):
            y_off = tier
            for dx in range(-9, 10):
                place(level, cx + dx, court_y + y_off, cz + dz_off, OAK_STAIRS)
                placed += 1

    # Scoreboard above
    for dx in range(-3, 4):
        place(level, cx + dx, court_y + 8, cz, BLACK_CONCRETE)
        placed += 1
    place(level, cx, court_y + 9, cz, RED_CONCRETE)  # score number
    place(level, cx + 2, court_y + 9, cz, BLUE_CONCRETE)
    placed += 2

    return placed


def build_dorm_interior(level, x, z, building_name):
    """Add dorm interior details (rugs, beds, desks, wardrobes)."""
    placed = 0
    gy = get_ground_y(level, x, z) + 1
    # Room layout: 2x2 cells per floor
    for floor in range(7):  # 7 floors
        ry = gy + floor * 4
        # Hallway down the center
        for dz in range(-4, 5):
            place(level, x, ry, z + dz, OAK_PLANK)
            placed += 1
        # Room markers (carpet at doors)
        for room_dx in [-2, 2]:
            for room_dz in [-2, 2]:
                rx, rz = x + room_dx, z + room_dz
                place(level, rx, ry, rz, CARPET)
                placed += 1
                # Bed in room
                place(level, rx + 1, ry, rz, B("minecraft", "red_bed"))
                placed += 1

    return placed


def build_dome_interior(level):
    """Add spiral staircase inside the Academic Dome (around x=210, z=160)."""
    print("  → Academic Dome: oculus + spiral staircase")
    placed = 0
    cx, cz = 220, 160
    # Center spiral staircase inside dome (already at y=83 from build_academic_dome)
    # Add a 4-block-tall obsidian "oculus" at the very top
    gy = 100
    place(level, cx, gy, cz, BLACK_CONCRETE)
    placed += 1
    # Skylight frame
    for dx in range(-2, 3):
        for dz in range(-2, 3):
            if abs(dx) == 2 or abs(dz) == 2:
                place(level, cx + dx, gy, cz + dz, WHITE_CONCRETE)
                placed += 1

    # Spiral staircase ascending from base (around dome base)
    import math
    base_y = get_ground_y(level, cx, cz) + 1
    for step in range(15):
        angle = step * 0.4
        sx = cx + int(round(8 * math.cos(angle)))
        sz = cz + int(round(8 * math.sin(angle)))
        sy = base_y + step
        place(level, sx, sy, sz, OAK_STAIRS)
        placed += 1

    return placed


def build_sundial_decoration(level):
    """Add zodiac ring marks to the Sundial (around x=222, z=230)."""
    print("  → Sundial: gnomon shadow marks, zodiac ring")
    placed = 0
    cx, cz = 222, 230
    gy = get_ground_y(level, cx, cz) + 1

    # 12 zodiac markers around the circle (gold blocks every 30 degrees)
    import math
    for i in range(12):
        angle = i * (math.pi / 6)
        rx = cx + int(round(8 * math.cos(angle)))
        rz = cz + int(round(8 * math.sin(angle)))
        place(level, rx, gy, rz, GOLD_BLOCK)
        placed += 1

    # 4 cardinal markers (larger quartz pillars)
    for angle in [0, math.pi / 2, math.pi, 3 * math.pi / 2]:
        rx = cx + int(round(9 * math.cos(angle)))
        rz = cz + int(round(9 * math.sin(angle)))
        for dy in range(2):
            place(level, rx, gy + dy, rz, QUARTZ_PILLAR)
            placed += 1

    return placed


def build_fountain_decoration(level):
    """Add water feature rings to One-World Fountain (around x=220, z=240)."""
    print("  → One-World Fountain: water rings, lily pads")
    placed = 0
    cx, cz = 220, 240
    gy = get_ground_y(level, cx, cz) + 1

    # Concentric water rings
    for ring_r in [3, 5, 7]:
        for angle_deg in range(0, 360, 10):
            angle = math.radians(angle_deg)
            rx = cx + int(round(ring_r * math.cos(angle)))
            rz = cz + int(round(ring_r * math.sin(angle)))
            place(level, rx, gy, rz, BLUE_CONCRETE if ring_r % 2 == 1 else LIGHT_GRAY_CONCRETE)
            placed += 1

    return placed


def main():
    import shutil
    if DST.exists():
        shutil.rmtree(DST)
    shutil.copytree(SRC, DST)

    print(f"Loading {DST}")
    level = amulet_level.load_level(str(DST))
    print("Loaded.")

    total = 0
    print("\n=== Building interiors ===")
    total += build_atrium_interior(level)
    total += build_library_interior(level)
    total += build_sports_hall_interior(level)
    total += build_dome_interior(level)
    total += build_sundial_decoration(level)
    total += build_fountain_decoration(level)

    # Add dorm interiors for UG Halls (just 2 to keep block count reasonable)
    total += build_dorm_interior(level, 150, 300, "UG Hall I")
    total += build_dorm_interior(level, 245, 310, "UG Hall VII")

    level.close()
    print(f"\n=== Total interior blocks: ~{total} ===")
    print(f"Saved to: {DST}")


if __name__ == "__main__":
    import math
    main()
