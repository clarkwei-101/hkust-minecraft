#!/usr/bin/env python3.11
"""
HKUST Minecraft v1.9 - Missing Buildings Injector
=================================================
Closes the gap between v1.8 and the official HKUST IAS Map (ver 202601) by
injecting the *buildings that exist in the official campus map but were
never placed in our Minecraft world* — even though some of them are listed
as "BUILT ✅" in the v1.7/v1.8 README. This script makes the docs honest.

Source: HKUST IAS Map v202601.pdf (Path Advisor), Wikipedia HKUST page,
        HKUST official photo gallery.

Missing landmarks (v1.9):
  * Lo Kwee-Seong Building (罗桂祥楼) — sports/PE building, distinctive
    sloped roof (v1.8 had nothing here even though OSM had it).
  * Chia-Wei Woo Academic Concourse (吴家玮学术长廊) — covered elevated
    walkway joining the Academic Building to LG and Library.
  * Tin Ka Ping Hall (田家炳楼) — large lecture theatre building south of
    Atrium.
  * President's Lodge (校长邸) — discreet mansion on coastal slope.
  * Library Extension (图书馆新翼) — additional library stacks at north end.
  * High Performance Computational Facility (高性能计算设施) — tower on
    east side of campus.
  * Indoor Swimming Pool (室内泳池) — next to Fok Ying Tung pool.
  * Multi-storey Car Park (多层停车场) — at south tip.
  * Bridge Link network — 6 elevated footbridges + lift shafts connecting
    the terraces.
  * Jockey Club i-Village — innovation hub south of Lee Shau Kee Campus.
  * Annex Building — annex at Lo Ka Chung.
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


# Block shorthands
QUARTZ = B("minecraft", "quartz_block")
QUARTZ_PILLAR = B("minecraft", "quartz_pillar", {"axis": "y"})
WHITE = B("minecraft", "white_concrete")
GRAY = B("minecraft", "gray_concrete")
LGRAY = B("minecraft", "light_gray_concrete")
DGRAY = B("minecraft", "dark_gray_concrete" if False else "gray_concrete")
STONE = B("minecraft", "stone")
BRICK = B("minecraft", "bricks")
SMOOTH_STONE = B("minecraft", "smooth_stone")
POLISHED_DIORITE = B("minecraft", "polished_diorite")
POLISHED_GRANITE = B("minecraft", "polished_granite")
GLASS = B("minecraft", "light_blue_stained_glass")
GLASS_CLEAR = B("minecraft", "glass")
GLASS_PANE = B("minecraft", "light_gray_stained_glass_pane")
IRON = B("minecraft", "iron_block")
COPPER = B("minecraft", "oxidized_copper" if False else "copper_block")
DARK_OAK = B("minecraft", "dark_oak_log")
DARK_OAK_PLANK = B("minecraft", "dark_oak_planks")
OAK_PLANK = B("minecraft", "oak_planks")
GOLD = B("minecraft", "gold_block")
WATER = B("minecraft", "water")
SANDSTONE = B("minecraft", "sandstone")
RED_SANDSTONE = B("minecraft", "red_sandstone")
TERRACOTTA = B("minecraft", "light_gray_terracotta")
AIR = B("minecraft", "air")
STONE_BRICKS = B("minecraft", "stone_bricks")


def build_box(level, x1, y1, z1, x2, y2, z2, fill):
    """Fill the box from x1..x2, y1..y2, z1..z2 (inclusive) with `fill` block."""
    p = 0
    for x in range(x1, x2 + 1):
        for y in range(y1, y2 + 1):
            for z in range(z1, z2 + 1):
                place(level, x, y, z, fill)
                p += 1
    return p


def build_hollow_box(level, x1, y1, z1, x2, y2, z2, wall, floor=None, roof=None):
    p = 0
    for x in range(x1, x2 + 1):
        for y in range(y1, y2 + 1):
            for z in range(z1, z2 + 1):
                on_edge = (x == x1 or x == x2 or z == z1 or z == z2 or y == y1 or y == y2)
                if on_edge:
                    place(level, x, y, z, wall)
                    p += 1
                elif floor is not None and y == y1 + 1:
                    place(level, x, y, z, floor)
                    p += 1
                elif roof is not None and y == y2:
                    place(level, x, y, z, roof)
                    p += 1
    return p


def build_rect_building(level, cx, cz, w, d, h, wall=QUARTZ, roof=QUARTZ, glass=GLASS,
                        ground_offset=1, include_floor=True, base=None):
    """Build a rectangular building centred on (cx, cz). w/d in blocks, h in blocks tall.
    Includes windows along long sides."""
    placed = 0
    gy = ground_y(level, cx, cz)
    base_y = gy + ground_offset
    x1, x2 = cx - w // 2, cx + w // 2
    z1, z2 = cz - d // 2, cz + d // 2
    if base:
        placed += build_box(level, x1 - 1, base_y - 1, z1 - 1, x2 + 1, base_y - 1, z2 + 1, base)
    # floor
    if include_floor:
        placed += build_box(level, x1, base_y, z1, x2, base_y, z2, wall)
    # walls + windows
    for y in range(base_y + 1, base_y + h):
        # North/South walls
        for x in range(x1, x2 + 1):
            for z in (z1, z2):
                win = (y - base_y) % 4 == 2 and x % 4 == 2
                blk = glass if win else wall
                place(level, x, y, z, blk); placed += 1
        # East/West walls
        for z in range(z1 + 1, z2):
            for x in (x1, x2):
                win = (y - base_y) % 4 == 2 and z % 4 == 2
                blk = glass if win else wall
                place(level, x, y, z, blk); placed += 1
    # roof
    placed += build_box(level, x1, base_y + h, z1, x2, base_y + h, z2, roof)
    return placed


def build_pagoda(level, cx, cz, levels=3, base_w=12, base_d=12, total_h=14):
    """Multi-tier pagoda (Lo Kwee-Seong / Tin Ka Ping style) with stepped roof."""
    placed = 0
    gy = ground_y(level, cx, cz)
    for i in range(levels):
        tier_h = total_h // levels
        tier_w = max(4, base_w - i * 2)
        tier_d = max(4, base_d - i * 2)
        x1 = cx - tier_w // 2
        z1 = cz - tier_d // 2
        x2 = x1 + tier_w - 1
        z2 = z1 + tier_d - 1
        y_base = gy + 1 + i * tier_h
        # tier walls
        placed += build_hollow_box(level, x1, y_base, z1, x2, y_base + tier_h - 1, z2, STONE_BRICKS, GLASS)
        # roof slab (overhang)
        roof_y = y_base + tier_h
        placed += build_box(level, x1 - 1, roof_y, z1 - 1, x2 + 1, roof_y, z2 + 1, RED_SANDSTONE)
        # roof corners (eave spikes)
        for ex, ez in [(x1 - 1, z1 - 1), (x2 + 1, z1 - 1), (x1 - 1, z2 + 1), (x2 + 1, z2 + 1)]:
            place(level, ex, roof_y + 1, ez, STONE_BRICKS); placed += 1
    return placed


# =============================================================================
# 1. LO KWEE-SEONG BUILDING (罗桂祥楼) — sports/PE complex with curved roof
# =============================================================================
def build_lo_kwee_seong(level):
    print("\n[1] Lo Kwee-Seong Building (罗桂祥楼) — Sports Complex")
    cx, cz = 360, 337
    gy = ground_y(level, cx, cz)
    placed = 0

    # Main curved-roof hall (rectangle with rounded gable ends)
    w, d, h = 24, 16, 9
    placed += build_rect_building(level, cx, cz, w, d, h, wall=WHITE, roof=GRAY, glass=GLASS)
    # Pitched roof: build two slopes
    y_roof = gy + 1 + h
    # Apex ridge along the X-axis (length)
    for x in range(cx - w // 2, cx + w // 2 + 1):
        for z in range(cz - d // 2, cz + d // 2 + 1):
            dz = abs(z - cz)
            apex_y = y_roof + (d // 2 - dz)
            for y in range(y_roof, apex_y + 1):
                place(level, x, y, z, RED_SANDSTONE); placed += 1
    # Side entrance canopy
    placed += build_box(level, cx - 3, gy + 1, cz - d // 2 - 1, cx + 3, gy + 1, cz - d // 2 - 1, SANDSTONE)
    placed += build_box(level, cx - 4, gy + 2, cz - d // 2 - 1, cx + 4, gy + 2, cz - d // 2 - 1, SANDSTONE)
    placed += build_box(level, cx - 4, gy + 3, cz - d // 2 - 1, cx + 4, gy + 3, cz - d // 2 - 1, AIR)
    # Sports field signage: blue wall behind
    placed += build_box(level, cx - 7, gy + 1, cz - d // 2 - 2, cx + 7, gy + 5, cz - d // 2 - 2, LGRAY)
    print(f"   placed {placed} blocks")
    return placed


# =============================================================================
# 2. CHIA-WEI WOO ACADEMIC CONCOURSE (吴家玮学术长廊) — covered walkway
# Real: Elevated, glass-canopied walkway from Atrium up to LG complex.
# =============================================================================
def build_chia_wei_woo_concourse(level):
    print("\n[2] Chia-Wei Woo Academic Concourse (吴家玮学术长廊)")
    placed = 0
    # From Atrium (220, 240) up to LG (240, 220) — short elevated corridor.
    # Build a 5-block wide elevated walk along Z direction, between two
    # already-built structures.
    x_start, z_start, x_end, z_end = 215, 215, 250, 245
    # Use quartz slab + glass canopy
    # Determine start elevation
    y_mid = ground_y(level, 232, 230) + 6
    for z in range(z_start, z_end + 1):
        for x in range(x_start, x_end + 1):
            # floor
            place(level, x, y_mid, z, QUARTZ); placed += 1
            # side walls (low) — only at the extreme edges
            if x == x_start or x == x_end:
                place(level, x, y_mid + 1, z, QUARTZ); placed += 1
            # glass canopy top
            if x % 3 == 0 and (z - z_start) % 2 == 0:
                place(level, x, y_mid + 5, z, IRON); placed += 1
            # canopy glass on top 4-block strip
            if x % 2 == 0 and z % 2 == 0:
                place(level, x, y_mid + 4, z, GLASS); placed += 1
    # Support columns every 8 blocks along Z
    for z in range(z_start, z_end + 1, 8):
        for x_off in (0, 5, 10, 15):
            x = x_start + x_off
            gy = ground_y(level, x, z)
            for y in range(gy + 1, y_mid):
                place(level, x, y, z, QUARTZ_PILLAR); placed += 1
    print(f"   placed {placed} blocks")
    return placed


# =============================================================================
# 3. TIN KA PING HALL (田家炳楼) — large lecture theatre building
# =============================================================================
def build_tin_ka_ping_hall(level):
    print("\n[3] Tin Ka Ping Hall (田家炳楼)")
    cx, cz = 200, 320
    gy = ground_y(level, cx, cz)
    placed = 0
    # Big lecture hall - tiered auditorium box
    w, d, h = 22, 18, 11
    placed += build_rect_building(level, cx, cz, w, d, h, wall=STONE_BRICKS, roof=GRAY, glass=GLASS)
    # Tiered steps outside (front entrance)
    for step in range(3):
        step_w = w - step * 4
        placed += build_box(
            level, cx - step_w // 2, gy + 1 + step, cz - d // 2 - 2 - step,
            cx + step_w // 2, gy + 1 + step, cz - d // 2 - 2 - step, STONE_BRICKS
        )
    print(f"   placed {placed} blocks")
    return placed


# =============================================================================
# 4. PRESIDENT'S LODGE (校长邸) — discreet mansion on coastal slope
# =============================================================================
def build_presidents_lodge(level):
    print("\n[4] President's Lodge (校长邸)")
    cx, cz = 580, 870
    gy = ground_y(level, cx, cz)
    placed = 0
    # Main house — low 2-story white mansion
    w, d, h = 16, 12, 6
    placed += build_rect_building(level, cx, cz, w, d, h, wall=WHITE, roof=DGRAY, glass=GLASS)
    # Garden walls (granite, 1 block tall)
    for dx in range(-12, 13):
        place(level, cx + dx, gy + 1, cz - 9, POLISHED_GRANITE); placed += 1
        place(level, cx + dx, gy + 1, cz + 9, POLISHED_GRANITE); placed += 1
    for dz in range(-8, 9):
        place(level, cx - 12, gy + 1, cz + dz, POLISHED_GRANITE); placed += 1
        place(level, cx + 12, gy + 1, cz + dz, POLISHED_GRANITE); placed += 1
    # Gate pillars
    for dx in (-1, 1):
        for y in range(gy + 2, gy + 5):
            place(level, cx + dx, y, cz - 9, POLISHED_GRANITE); placed += 1
    # Driveway
    for z in range(cz + 9, cz + 18):
        place(level, cx, gy + 1, z, STONE); placed += 1
    print(f"   placed {placed} blocks")
    return placed


# =============================================================================
# 5. LIBRARY EXTENSION (图书馆新翼)
# =============================================================================
def build_library_extension(level):
    print("\n[5] Library Extension (图书馆新翼)")
    cx, cz = 264, 18
    gy = ground_y(level, cx, cz)
    placed = 0
    # Glass-extension style — slightly smaller than main library
    w, d, h = 18, 14, 14
    placed += build_rect_building(level, cx, cz, w, d, h, wall=GRAY, roof=QUARTZ, glass=GLASS)
    # Connector bridge to main library
    for x in range(cx + w // 2, cx + w // 2 + 10):
        for y_off in range(6, 10):
            place(level, x, gy + y_off, cz, QUARTZ); placed += 1
    print(f"   placed {placed} blocks")
    return placed


# =============================================================================
# 6. HIGH PERFORMANCE COMPUTATIONAL FACILITY (高性能计算设施)
# =============================================================================
def build_hpc_facility(level):
    print("\n[6] High Performance Computational Facility (高性能计算中心)")
    cx, cz = 530, 200
    gy = ground_y(level, cx, cz)
    placed = 0
    # Tower-like structure with cooling fins
    w, d, h = 14, 14, 22
    placed += build_rect_building(level, cx, cz, w, d, h, wall=LGRAY, roof=IRON, glass=GLASS_CLEAR)
    # Cooling fins (blue stained glass fins on east wall)
    for y in range(gy + 3, gy + h + 1):
        if y % 2 == 0:
            place(level, cx + w // 2, y, cz, B("minecraft", "blue_stained_glass")); placed += 1
    # Antenna on top
    for y in range(gy + h + 1, gy + h + 6):
        place(level, cx, y, cz, IRON); placed += 1
    place(level, cx, gy + h + 6, cz, B("minecraft", "redstone_block")); placed += 1
    print(f"   placed {placed} blocks")
    return placed


# =============================================================================
# 7. INDOOR SWIMMING POOL (室内泳池)
# =============================================================================
def build_indoor_pool(level):
    print("\n[7] Indoor Swimming Pool (室内泳池)")
    cx, cz = 670, 290
    gy = ground_y(level, cx, cz)
    placed = 0
    # Big dome-shaped hall
    w, d, h = 20, 14, 8
    placed += build_rect_building(level, cx, cz, w, d, h, wall=WHITE, roof=LGRAY, glass=GLASS)
    # Pool inside (water)
    pool_x1 = cx - w // 2 + 3
    pool_x2 = cx + w // 2 - 3
    pool_z1 = cz - d // 2 + 3
    pool_z2 = cz + d // 2 - 3
    for x in range(pool_x1, pool_x2 + 1):
        for z in range(pool_z1, pool_z2 + 1):
            place(level, x, gy + 2, z, B("minecraft", "blue_concrete")); placed += 1
            place(level, x, gy + 3, z, WATER); placed += 1
            place(level, x, gy + 4, z, WATER); placed += 1
    # Diving board at south end
    for dz in range(2):
        place(level, cx, gy + 6, pool_z1 - 1 - dz, OAK_PLANK); placed += 1
    # Lane markers every 5 blocks
    for x in range(pool_x1, pool_x2 + 1, 5):
        for z in (pool_z1 + 2, pool_z2 - 2):
            place(level, x, gy + 4, z, WHITE); placed += 1
    print(f"   placed {placed} blocks")
    return placed


# =============================================================================
# 8. MULTI-STOREY CAR PARK (多层停车场)
# =============================================================================
def build_car_park(level):
    print("\n[8] HKUST Multi-storey Car Park (多层停车场)")
    cx, cz = 354, 13
    gy = ground_y(level, cx, cz)
    placed = 0
    # Open-deck parking — concrete with metal posts
    w, d = 28, 16
    for tier in range(4):
        y = gy + 1 + tier * 3
        # deck slab
        for x in range(cx - w // 2, cx + w // 2 + 1):
            for z in range(cz - d // 2, cz + d // 2 + 1):
                place(level, x, y, z, GRAY); placed += 1
        # perimeter
        if tier < 3:
            for x in range(cx - w // 2, cx + w // 2 + 1):
                place(level, x, y + 1, cz - d // 2, LGRAY); placed += 1
                place(level, x, y + 1, cz + d // 2, LGRAY); placed += 1
            for z in range(cz - d // 2, cz + d // 2 + 1):
                place(level, cx - w // 2, y + 1, z, LGRAY); placed += 1
                place(level, cx + w // 2, y + 1, z, LGRAY); placed += 1
    # Support pillars at corners + centre
    for px in (cx - w // 2 + 1, cx + w // 2 - 1, cx):
        for pz in (cz - d // 2 + 1, cz + d // 2 - 1, cz):
            for y in range(gy + 1, gy + 13):
                place(level, px, y, pz, IRON); placed += 1
    # "P" parking signs every 4 spaces
    for x in range(cx - w // 2 + 4, cx + w // 2 - 2, 4):
        for z in range(cz - d // 2 + 2, cz + d // 2 - 2, 6):
            place(level, x, gy + 2, z, B("minecraft", "blue_concrete")); placed += 1
    print(f"   placed {placed} blocks")
    return placed


# =============================================================================
# 9. BRIDGE LINK network — 6 elevated footbridges + lift shafts
# =============================================================================
def build_bridge_link(level):
    print("\n[9] Bridge Link network — elevated footbridges + lift shafts")
    placed = 0

    # Define bridges: (start_x, start_z, end_x, end_z, height_offset)
    bridges = [
        # Academic Building atrium → LG complex
        (220, 250, 250, 220, 0),
        # LG → Library
        (260, 220, 270, 200, 0),
        # Library → Wong Check She
        (380, 200, 380, 240, 0),
        # Library → Lo Ka Chung
        (250, 380, 220, 380, 4),
        # Academic Building → Li Dak Sum Conference Lodge
        (60, 290, 50, 320, 6),
        # LSK Business → Innovation Building
        (180, 600, 240, 540, 4),
    ]
    for x1, z1, x2, z2, y_off in bridges:
        try:
            # Mid-point ground
            cx, cz = (x1 + x2) // 2, (z1 + z2) // 2
            gy = ground_y(level, cx, cz)
            bridge_y = gy + 5 + y_off
            # Build along the axis with the greater span
            if abs(x2 - x1) >= abs(z2 - z1):
                # horizontal
                for x in range(min(x1, x2), max(x1, x2) + 1):
                    # floor
                    place(level, x, bridge_y, cz, QUARTZ); placed += 1
                    # railings (low)
                    place(level, x, bridge_y + 1, cz - 1, QUARTZ_PILLAR); placed += 1
                    place(level, x, bridge_y + 1, cz + 1, QUARTZ_PILLAR); placed += 1
            else:
                for z in range(min(z1, z2), max(z1, z2) + 1):
                    place(level, cx, bridge_y, z, QUARTZ); placed += 1
                    place(level, cx - 1, bridge_y + 1, z, QUARTZ_PILLAR); placed += 1
                    place(level, cx + 1, bridge_y + 1, z, QUARTZ_PILLAR); placed += 1
        except Exception as e:
            print(f"   bridge err: {e}")

    # Lift shafts (4 — distinctive red roof)
    lift_positions = [
        (235, 245, "Bridge lift 1"),
        (260, 230, "Bridge lift 2"),
        (220, 380, "Bridge lift 3"),
        (180, 540, "Bridge lift 4"),
    ]
    for x, z, label in lift_positions:
        try:
            gy = ground_y(level, x, z)
            for y in range(gy + 1, gy + 11):
                place(level, x, y, z, GRAY); placed += 1
                place(level, x + 1, y, z, GRAY); placed += 1
                place(level, x, y, z + 1, GRAY); placed += 1
                place(level, x + 1, y, z + 1, GRAY); placed += 1
            # Red roof
            for dx in (-1, 0, 1, 2):
                for dz in (-1, 0, 1, 2):
                    place(level, x + dx, gy + 12, z + dz, B("minecraft", "red_concrete")); placed += 1
            # Glass on the side
            for y in range(gy + 2, gy + 10):
                place(level, x, y, z - 1, GLASS); placed += 1
                place(level, x + 2, y, z, GLASS); placed += 1
        except Exception as e:
            print(f"   lift err: {e}")
    print(f"   placed {placed} blocks")
    return placed


# =============================================================================
# 10. JOCKEY CLUB i-VILLAGE — innovation hub south of Lee Shau Kee Campus
# =============================================================================
def build_jc_ivillage(level):
    print("\n[10] Jockey Club i-Village (赛马会创新村)")
    cx, cz = 190, 700
    gy = ground_y(level, cx, cz)
    placed = 0
    # 3 connected modern pavilions
    for i, off in enumerate([(0, 0), (12, 0), (24, 0)]):
        ox, oz = off
        # Pavilion
        w, d, h = 10, 8, 7
        placed += build_rect_building(level, cx + ox, cz + oz, w, d, h, wall=WHITE, roof=LGRAY, glass=GLASS)
        # Connecting corridor (low)
        if i < 2:
            for z in range(cz + oz - d // 2, cz + oz + d // 2 + 1):
                for y in range(gy + 2, gy + 4):
                    place(level, cx + ox + w // 2, y, z, QUARTZ); placed += 1
    # Plaza with L shape
    for dx in range(-3, 35):
        for dz in range(-6, 7):
            place(level, cx + dx, gy, cz + dz, POLISHED_GRANITE); placed += 1
    print(f"   placed {placed} blocks")
    return placed


# =============================================================================
# 11. ANNEX BUILDING (新翼大楼) — annex at Lo Ka Chung
# =============================================================================
def build_annex_building(level):
    print("\n[11] Annex Building (新翼大楼)")
    cx, cz = 267, 367
    placed = build_rect_building(level, cx, cz, 14, 10, 7, wall=GRAY, roof=LGRAY, glass=GLASS)
    print(f"   placed {placed} blocks")
    return placed


# =============================================================================
# 12. ALUMNI COMMONS (校友中心)
# =============================================================================
def build_alumni_commons(level):
    print("\n[12] Alumni Commons (校友中心)")
    cx, cz = 320, 540
    gy = ground_y(level, cx, cz)
    placed = 0
    # Low rectangular hall with courtyard
    w, d, h = 18, 14, 6
    placed += build_rect_building(level, cx, cz, w, d, h, wall=LGRAY, roof=STONE_BRICKS, glass=GLASS)
    # Open courtyard in middle
    place(level, cx, gy + 1, cz, AIR); placed += 1
    place(level, cx + 1, gy + 1, cz, AIR); placed += 1
    place(level, cx - 1, gy + 1, cz, AIR); placed += 1
    place(level, cx, gy + 1, cz + 1, AIR); placed += 1
    place(level, cx, gy + 1, cz - 1, AIR); placed += 1
    # HKUST logo pole (gold pillar)
    for y in range(gy + 2, gy + 12):
        place(level, cx, y, cz, GOLD); placed += 1
    print(f"   placed {placed} blocks")
    return placed


# =============================================================================
# 13. UNDER-CONSTRUCTION buildings (Daniel Yu / School of Medicine)
# Real: scaffolding + concrete shell — distinctive yellow/black stripes
# =============================================================================
def build_under_construction(level):
    print("\n[13] Under-construction (Daniel & Mayce Yu / School of Medicine)")
    placed = 0
    sites = [
        (320, 380, 18, 12, 12, "Daniel & Mayce Yu Research Building"),
        (440, 460, 22, 14, 14, "School of Medicine Building"),
    ]
    for cx, cz, w, d, h, name in sites:
        try:
            gy = ground_y(level, cx, cz)
            # Concrete shell
            placed += build_hollow_box(level, cx - w // 2, gy + 1, cz - d // 2, cx + w // 2, gy + h, cz + d // 2, GRAY, GRAY, GRAY)
            # Yellow/black hazard stripes around perimeter
            for y in range(gy + 1, gy + h + 1):
                for x in range(cx - w // 2 - 1, cx + w // 2 + 2):
                    if (x + y) % 2 == 0:
                        place(level, x, y, cz - d // 2 - 1, B("minecraft", "yellow_concrete")); placed += 1
                        place(level, x, y, cz + d // 2 + 1, B("minecraft", "yellow_concrete")); placed += 1
                    else:
                        place(level, x, y, cz - d // 2 - 1, B("minecraft", "black_concrete")); placed += 1
                        place(level, x, y, cz + d // 2 + 1, B("minecraft", "black_concrete")); placed += 1
            # Crane (yellow pillar + jib)
            crane_x = cx + w // 2 + 4
            for y in range(gy + 1, gy + 25):
                place(level, crane_x, y, cz, B("minecraft", "yellow_concrete")); placed += 1
            for x_off in range(-8, 9):
                place(level, crane_x + x_off, gy + 24, cz, B("minecraft", "yellow_concrete")); placed += 1
            # Scaffolding on top
            for x in range(cx - w // 2, cx + w // 2 + 1):
                for z in range(cz - d // 2, cz + d // 2 + 1):
                    if (x + z) % 3 == 0:
                        place(level, x, gy + h + 1, z, B("minecraft", "scaffolding")); placed += 1
        except Exception as e:
            print(f"   {name} err: {e}")
    print(f"   placed {placed} blocks")
    return placed


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
    total += build_lo_kwee_seong(level)
    total += build_chia_wei_woo_concourse(level)
    total += build_tin_ka_ping_hall(level)
    total += build_presidents_lodge(level)
    total += build_library_extension(level)
    total += build_hpc_facility(level)
    total += build_indoor_pool(level)
    total += build_car_park(level)
    total += build_bridge_link(level)
    total += build_jc_ivillage(level)
    total += build_annex_building(level)
    total += build_alumni_commons(level)
    total += build_under_construction(level)
    print(f"\n=== v1.9 Total blocks placed: {total} ===")
    level.save()
    level.close()
    print("Saved!")


if __name__ == "__main__":
    main()