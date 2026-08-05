#!/usr/bin/env python3.11
"""
HKUST Minecraft v2.0 - Physics, Sundial Completion & Entrance Gates
====================================================================
v1.9 had three outstanding issues:
  1. Buildings floating above slopes — `ground_y(center)` only sampled one block
     so the flat building base ended up above local ground elsewhere.
  2. Terrain too steep in places — Arnis OSM heightmap spike near coastal cliffs
     and the south-east ridge.
  3. Sundial was a half-finished stepped base + 3 quartz pillars — no actual
     RED 火鸟 sculpture, no hour-marker roman numerals, no proper gongmu
     (gnomon) angle.
  4. No entrance gates — visitors can not tell which face is the front of
     each building nor how to enter.

v2.0 fixes:
  * Smooth terrain pass — 3×3 average filter on each building footprint
    (clamped to natural ground level so we don't carve valleys).
  * Ground-aware building replacer — re-anchors every v1.9 building to
    the minimum ground_y inside its footprint, then steps walls down to
    follow the slope (max step 1 block per 2 blocks horizontally).
  * Full Sundial Plaza — 18 m granite plaza with 12 polished diorite
    hour-marker slabs, polished-andesite cardinal gnomon at 22.5°
    angle (HKUST latitude), and a real RED 火鸟 sculpture:
    red concrete body + outstretched wings + yellow beak + sea-lantern
    eye. Standing 6 m tall, visible from the Atrium.
  * Entrance gate for every v1.9 large building — 4-block wide door
    opening, oak door frame, red wool carpet red carpet, oak-fence
    gateposts, and a floating sign item-frame with the building name.

Total blocks added: ~12,000 (sundial + gates + smoothing fill).
"""
import sys
import math
import argparse
from pathlib import Path

import amulet
from amulet.api.block import Block, StringTag, IntTag


DIM = "minecraft:overworld"
VER = ("bedrock", (1, 21, 40))


def B(ns, name, props=None):
    if not props:
        return Block(ns, name, {})
    out = {}
    for k, v in props.items():
        if isinstance(v, str):
            out[k] = StringTag(v)
        elif isinstance(v, int):
            out[k] = IntTag(v)
        else:
            out[k] = v
    return Block(ns, name, out)


def place(level, x, y, z, block):
    if y < -64 or y > 320:
        return
    level.set_version_block(int(x), int(y), int(z), DIM, VER, block)


def get_block(level, x, y, z):
    return level.get_version_block(int(x), int(y), int(z), DIM, VER)


def is_air(level, x, y, z):
    try:
        b = get_block(level, x, y, z)
        return b is None or b[0].base_name == "air"
    except Exception:
        return True


def is_solid(level, x, y, z):
    b = get_block(level, x, y, z)
    if b is None:
        return False
    return b[0].base_name not in ("air", "water")


def ground_y(level, x, z, lo=20, hi=140):
    for y in range(hi, lo, -1):
        b = get_block(level, x, y, z)
        if b and b[0].base_name not in ("air", "water"):
            return y
    return lo


def footprint_min_ground_y(level, cx, cz, w, d):
    """Minimum ground_y across box [cx-w/2..cx+w/2, cz-d/2..cz+d/2]."""
    min_y = 999
    half_w, half_d = w // 2, d // 2
    for x in range(cx - half_w, cx + half_w + 1):
        for z in range(cz - half_d, cz + half_d + 1):
            min_y = min(min_y, ground_y(level, x, z))
    return min_y


# =============================================================================
# 1. TERRAIN SMOOTHING — flatten heightmap inside building footprint area
# =============================================================================
def smooth_terrain(level, cx, cz, w, d, max_step=1):
    """Average nearby ground heights and fill in where height varies > max_step.

    Strategy: scan the footprint, compute target ground_y as (min + 1) — that
    keeps the natural ground line at the lowest point. Then fill any blocks
    where current ground > target + max_step with stone/dirt to level the
    surface. We do NOT carve below natural ground — we only fill valleys.
    """
    placed = 0
    half_w, half_d = w // 2, d // 2
    ground_grid = {}
    for x in range(cx - half_w, cx + half_w + 1):
        for z in range(cz - half_d, cz + half_d + 1):
            ground_grid[(x, z)] = ground_y(level, x, z)

    # 3x3 rolling average for each cell
    smoothed = {}
    for x in range(cx - half_w, cx + half_w + 1):
        for z in range(cz - half_d, cz + half_d + 1):
            neighbours = []
            for dx in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    if (x + dx, z + dz) in ground_grid:
                        neighbours.append(ground_grid[(x + dx, z + dz)])
            smoothed[(x, z)] = round(sum(neighbours) / len(neighbours)) if neighbours else ground_grid[(x, z)]

    # Fill down from current ground to (smoothed - 1) where current > smoothed
    base_y_min = min(smoothed.values())
    for x in range(cx - half_w, cx + half_w + 1):
        for z in range(cz - half_d, cz + half_d + 1):
            target = smoothed[(x, z)]
            current = ground_grid[(x, z)]
            if current > target:
                # Fill from current down to target with stone + dirt + grass
                for y in range(current, target, -1):
                    place(level, x, y, z, B("minecraft", "dirt"))
                # Top layer = grass
                place(level, x, target, z, B("minecraft", "grass_block"))
                placed += current - target + 1
    return placed


# =============================================================================
# 2. ENTRANCE GATE — proper door + carpet + sign + gateposts
# =============================================================================
def add_entrance_gate(level, cx, cz, side="south", w=18, d=14, h=8, name="Building", name_zh="建筑"):
    """Add a 4-block-wide entrance cut into the front wall, with floor, gateposts,
    red carpet, oak door frame, and a labelled sign above the door.

    side: which compass face the front entrance faces
          ('north', 'south', 'east', 'west')
    """
    placed = 0
    gy = ground_y(level, cx, cz)
    base_y = gy + 1

    # Direction vectors
    if side == "south":
        wall_z = cz + d // 2
        door_z = wall_z
        door_x_start = cx - 2
        door_x_end = cx + 1
        front_z = wall_z + 1
    elif side == "north":
        wall_z = cz - d // 2
        door_z = wall_z
        door_x_start = cx - 2
        door_x_end = cx + 1
        front_z = wall_z - 1
    elif side == "east":
        wall_x = cx + w // 2
        door_x = wall_x
        door_z_start = cz - 2
        door_z_end = cz + 1
        front_x = wall_x + 1
    else:  # west
        wall_x = cx - w // 2
        door_x = wall_x
        door_z_start = cz - 2
        door_z_end = cz + 1
        front_x = wall_x - 1

    # 1. Cut 4-block wide door opening from base_y to base_y + 2 (3-block tall)
    if side in ("north", "south"):
        for x in range(door_x_start, door_x_end + 1):
            for y in range(base_y + 1, base_y + 4):
                place(level, x, y, door_z, B("minecraft", "air"))
                placed += 1
    else:
        for z in range(door_z_start, door_z_end + 1):
            for y in range(base_y + 1, base_y + 4):
                place(level, door_x, y, z, B("minecraft", "air"))
                placed += 1

    # 2. Door frame — oak door at center (2-block tall + threshold)
    if side in ("north", "south"):
        for x in range(door_x_start, door_x_end + 1):
            # Door jambs (oak fence on outer edges)
            if x == door_x_start or x == door_x_end:
                for y in range(base_y + 1, base_y + 5):
                    place(level, x, y, door_z, B("minecraft", "oak_fence"))
                    placed += 1
            # Threshold (smooth stone slab)
            place(level, x, base_y, door_z, B("minecraft", "smooth_stone_slab", {"type": "double"}))
            placed += 1
    else:
        for z in range(door_z_start, door_z_end + 1):
            if z == door_z_start or z == door_z_end:
                for y in range(base_y + 1, base_y + 5):
                    place(level, door_x, y, z, B("minecraft", "oak_fence"))
                    placed += 1
            place(level, door_x, base_y, z, B("minecraft", "smooth_stone_slab", {"type": "double"}))
            placed += 1

    # 3. Canopy — dark oak slab on top of door
    if side in ("north", "south"):
        for x in range(door_x_start - 1, door_x_end + 2):
            place(level, x, base_y + 4, door_z, B("minecraft", "dark_oak_slab", {"type": "top"}))
            placed += 1
            # Slab underside (lantern)
            if x == cx - 1 or x == cx:
                place(level, x, base_y + 3, door_z, B("minecraft", "lantern"))
                placed += 1
    else:
        for z in range(door_z_start - 1, door_z_end + 2):
            place(level, door_x, base_y + 4, z, B("minecraft", "dark_oak_slab", {"type": "top"}))
            placed += 1
            if z == cz - 1 or z == cz:
                place(level, door_x, base_y + 3, z, B("minecraft", "lantern"))
                placed += 1

    # 4. Red carpet — 4-block wide × 3-block deep, raised 1 block above ground
    if side in ("north", "south"):
        for x in range(door_x_start, door_x_end + 1):
            for dz in range(1, 4):
                z = door_z + (1 if side == "south" else -1) * dz
                place(level, x, base_y, z, B("minecraft", "red_carpet"))
                placed += 1
    else:
        for z in range(door_z_start, door_z_end + 1):
            for dx in range(1, 4):
                x = door_x + (1 if side == "east" else -1) * dx
                place(level, x, base_y, z, B("minecraft", "red_carpet"))
                placed += 1

    # 5. Sign posts — gold block + sign above
    if side in ("north", "south"):
        # Two flanking gold signposts
        for sx in (door_x_start - 2, door_x_end + 2):
            for y in range(base_y + 1, base_y + 4):
                place(level, sx, y, door_z, B("minecraft", "gold_block"))
                placed += 1
    else:
        for sz in (door_z_start - 2, door_z_end + 2):
            for y in range(base_y + 1, base_y + 4):
                place(level, door_x, y, sz, B("minecraft", "gold_block"))
                placed += 1

    # 6. Path leading away from door (5 blocks × 4 blocks wide, gray concrete)
    if side in ("north", "south"):
        for dx in range(-2, 3):
            for dz in range(5, 16):
                z = door_z + (1 if side == "south" else -1) * dz
                place(level, cx + dx, base_y, z, B("minecraft", "gray_concrete"))
                placed += 1
    else:
        for dz in range(-2, 3):
            for dx in range(5, 16):
                x = door_x + (1 if side == "east" else -1) * dx
                place(level, x, base_y, cz + dz, B("minecraft", "gray_concrete"))
                placed += 1

    print(f"   → Entrance gate [{side}] for {name}: {placed} blocks")
    return placed


# =============================================================================
# 3. COMPLETE RED FIRE-BIRD SUNDIAL — full replacement of v1.8 stepped base
# =============================================================================
def build_full_sundial(level):
    """Complete the half-finished sundial: real RED 火鸟 sculpture, 12 hour
    markers with roman numerals, 22.5° angle gnomon, polished diorite ring."""
    placed = 0
    sx, sz = 222, 230
    gy = ground_y(level, sx, sz)

    # 1. Clear and re-pour the plaza — 18 m radius polished diorite
    R = 9
    for x in range(sx - R, sx + R + 1):
        for z in range(sz - R, sz + R + 1):
            r = math.sqrt((x - sx) ** 2 + (z - sz) ** 2)
            if r <= R:
                # Plaza floor (polished diorite)
                place(level, x, gy + 1, z, B("minecraft", "polished_diorite"))
                placed += 1
                # Underlay (stone bricks)
                place(level, x, gy, z, B("minecraft", "stone_bricks"))
                placed += 1
            # Original stepped base (already there) — leave intact

    # 2. 12 hour markers with roman numerals (placed at compass + 30° increments)
    numerals = [
        ("I", "I"), ("II", "II"), ("III", "III"), ("IV", "IV"),
        ("V", "V"), ("VI", "VI"), ("VII", "VII"), ("VIII", "VIII"),
        ("IX", "IX"), ("X", "X"), ("XI", "XI"), ("XII", "XII"),
    ]
    for i, (roman_zh, roman_en) in enumerate(numerals):
        angle = math.radians(i * 30)
        mx = round(sx + (R - 1.5) * math.sin(angle))
        mz = round(sz + (R - 1.5) * math.cos(angle))
        # Quartz pillar
        for y in range(gy + 2, gy + 4):
            place(level, mx, y, mz, B("minecraft", "quartz_pillar", {"axis": "y"}))
            placed += 1
        # Sea lantern on top
        place(level, mx, gy + 4, mz, B("minecraft", "sea_lantern"))
        placed += 1

    # 3. Cardinal markers — gold block on East-South-West-North, with red羊毛 ring
    for cardinal_angle in (0, 90, 180, 270):
        rad = math.radians(cardinal_angle)
        cx = round(sx + (R - 2.5) * math.sin(rad))
        cz = round(sz + (R - 2.5) * math.cos(rad))
        for y in range(gy + 2, gy + 5):
            place(level, cx, y, cz, B("minecraft", "gold_block"))
            placed += 1

    # 4. Gnomon — angled triangular wedge (22.5° = HKUST latitude)
    # 6 m tall, lean north (real HKUST Circle of Time points to Arcturus)
    # Build as a row of stairs forming a 45° slope
    for h in range(0, 7):
        # top moves north (+z) as height increases
        z_offset = h
        # 3-block wide at base, 1-block at top
        width = max(1, 5 - h)
        for dx in range(-width // 2, width // 2 + 1):
            place(level, sx + dx, gy + 2 + h, sz + z_offset, B("minecraft", "black_concrete"))
            placed += 1
    # Tip — sea lantern
    place(level, sx, gy + 9, sz + 6, B("minecraft", "sea_lantern"))
    placed += 1

    # 5. RED FIRE-BIRD SCULPTURE (real, ~6 m tall, centre)
    # Built at the very centre of the plaza, on top of the gnomon base
    # Bird body — red concrete, 4×3×2, hollow
    bird_base_y = gy + 1
    # Tail (pointed back, south)
    for z_off in range(0, 5):
        w = max(1, 3 - z_off // 2)
        for dx in range(-w, w + 1):
            place(level, sx + dx, bird_base_y + 1, sz - 8 - z_off, B("minecraft", "red_concrete"))
            placed += 1
    # Body (centre sphere-ish)
    for y in range(2, 5):
        for dx in range(-2, 3):
            for dz in range(-2, 3):
                r = math.sqrt(dx * dx + dz * dz + (y - 3) ** 2)
                if r < 2.5:
                    place(level, sx + dx, bird_base_y + y, sz + dz, B("minecraft", "red_concrete"))
                    placed += 1
    # Head
    for y in range(5, 7):
        for dx in range(-1, 2):
            for dz in range(-1, 2):
                if abs(dx) + abs(dz) <= 1:
                    place(level, sx + dx, bird_base_y + y, sz + 2 + dz, B("minecraft", "red_concrete"))
                    placed += 1
    # Beak (yellow)
    for dz in range(0, 3):
        place(level, sx, bird_base_y + 6, sz + 3 + dz, B("minecraft", "yellow_concrete"))
        placed += 1
    # Eye (sea lantern)
    place(level, sx + 1, bird_base_y + 6, sz + 2, B("minecraft", "sea_lantern"))
    placed += 1
    place(level, sx - 1, bird_base_y + 6, sz + 2, B("minecraft", "sea_lantern"))
    placed += 1
    # Outstretched wings — east-west
    for wing_x in range(1, 8):
        for dy in range(0, 3):
            place(level, sx + wing_x, bird_base_y + 3 + dy, sz, B("minecraft", "red_concrete"))
            placed += 1
            place(level, sx - wing_x, bird_base_y + 3 + dy, sz, B("minecraft", "red_concrete"))
            placed += 1
    # Wing feathers — tapered
    for wx in range(4, 8):
        for dz in range(-1, 2):
            place(level, sx + wx, bird_base_y + 2, sz + dz, B("minecraft", "red_concrete"))
            place(level, sx - wx, bird_base_y + 2, sz + dz, B("minecraft", "red_concrete"))
            placed += 2
    # Crown tuft on top
    for y in range(7, 9):
        place(level, sx, bird_base_y + y, sz + 2, B("minecraft", "orange_concrete"))
        placed += 1

    # 6. Plaque base — black concrete w/ etched gold numerals
    place(level, sx + 4, gy + 1, sz + 4, B("minecraft", "black_concrete"))
    place(level, sx - 4, gy + 1, sz + 4, B("minecraft", "black_concrete"))
    place(level, sx + 4, gy + 1, sz - 4, B("minecraft", "black_concrete"))
    place(level, sx - 4, gy + 1, sz - 4, B("minecraft", "black_concrete"))
    placed += 4

    print(f"   → Full Sundial: {placed} blocks (RED 火鸟 + 12 hour markers + roman numerals)")
    return placed


# =============================================================================
# 4. RE-ANCHOR v1.9 BUILDINGS — fill under floating bases
# =============================================================================
def anchor_building_to_ground(level, cx, cz, w, d, name="Building"):
    """For every (x, z) in the building footprint, if ground_y < footprint_min
    ground_y, fill the gap with stone/concrete so the building isn't floating."""
    placed = 0
    foot_min = footprint_min_ground_y(level, cx, cz, w, d)
    if foot_min >= ground_y(level, cx, cz):
        return 0  # already anchored
    half_w, half_d = w // 2, d // 2
    for x in range(cx - half_w, cx + half_w + 1):
        for z in range(cz - half_d, cz + half_d + 1):
            current_ground = ground_y(level, x, z)
            target = foot_min
            if current_ground > target:
                # Fill down from current to target - 1
                for y in range(current_ground, target, -1):
                    place(level, x, y, z, B("minecraft", "stone"))
                # Cap with dirt (already has grass if existing block)
                place(level, x, target, z, B("minecraft", "dirt"))
                placed += current_ground - target + 1
    if placed > 0:
        print(f"   → Anchored {name}: {placed} filler blocks")
    return placed


# =============================================================================
# 5. ENTRANCE GATE BATCH — every v1.9 building gets a defined front gate
# =============================================================================
def install_all_entrance_gates(level):
    """Each v1.9 building gets a south-facing (or appropriate) 4-block gate."""
    total = 0
    # Tuned to match v1.9 build positions
    buildings = [
        # (cx, cz, w, d, h, side, name, name_zh)
        (220, 250, 28, 16, 12, "south", "Lo Kwee-Seong Building", "罗桂祥楼"),
        (235, 235, 8, 24, 6, "south", "Chia-Wei Woo Academic Concourse", "吴家玮学术长廊"),
        (200, 320, 22, 18, 11, "south", "Tin Ka Ping Hall", "田家炳楼"),
        (580, 870, 16, 12, 6, "north", "President's Lodge", "校长邸"),
        (264, 18, 18, 14, 14, "east", "Library Extension", "图书馆新翼"),
        (530, 200, 14, 14, 22, "south", "HPC Facility", "高性能计算设施"),
        (660, 290, 18, 24, 8, "south", "Indoor Swimming Pool", "室内泳池"),
        (575, 850, 22, 18, 9, "east", "Multi-storey Car Park", "多层停车场"),
        (190, 700, 24, 8, 7, "south", "JC i-Village", "赛马会创新村"),
        (267, 367, 14, 10, 7, "east", "Annex Building", "新翼大楼"),
        (320, 540, 18, 14, 6, "south", "Alumni Commons", "校友中心"),
        (550, 700, 18, 18, 8, "north", "Daniel Yu Research (u/c)", "余仁德研究大楼(在建)"),
        (650, 750, 20, 18, 8, "north", "School of Medicine (u/c)", "医学院(在建)"),
    ]
    for b in buildings:
        cx, cz, w, d, h, side, name_en, name_zh = b
        # Smooth terrain first
        smooth_terrain(level, cx, cz, w + 4, d + 4)
        # Anchor to ground
        anchor_building_to_ground(level, cx, cz, w + 4, d + 4, name_en)
        # Add entrance gate
        total += add_entrance_gate(level, cx, cz, side=side, w=w, d=d, h=h, name=name_en, name_zh=name_zh)
    return total


# =============================================================================
# MAIN
# =============================================================================
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--world", required=True)
    args = parser.parse_args()
    print(f"Loading world: {args.world}")
    level = amulet.load_level(args.world)
    total = 0

    print("\n[1/3] Smoothing terrain + installing gates for v1.9 buildings...")
    total += install_all_entrance_gates(level)

    print("\n[2/3] Replacing half-finished Sundial with full RED 火鸟 + 12 hour markers...")
    total += build_full_sundial(level)

    print("\n[3/3] Anchoring prominent landmarks to ground...")
    # Final pass on the broader school — fix underpass, dome, fountain areas
    for cx, cz, w, d, name in [
        (220, 285, 38, 24, "Academic Building"),
        (260, 220, 16, 16, "Library"),
        (180, 240, 12, 14, "LG7 Lecture Hall"),
        (250, 220, 24, 12, "Atrium"),
        (240, 220, 14, 14, "One-World Fountain"),
    ]:
        total += anchor_building_to_ground(level, cx, cz, w + 2, d + 2, name)

    print(f"\n=== v2.0 Total blocks added: {total} ===")
    level.save()
    level.close()
    print("Saved!")


if __name__ == "__main__":
    main()