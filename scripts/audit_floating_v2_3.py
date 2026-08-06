#!/usr/bin/env python3.11
"""
HKUST Minecraft v2.3 — Comprehensive Physics Audit (FIXED)
"""
import sys, json, time
from collections import defaultdict
import amulet

DIM = 'minecraft:overworld'
VER = ('bedrock', (1, 21, 40))

# Anything below we treat as "ground/terrain"
TERRAIN = {
    'stone', 'dirt', 'grass_block', 'sand', 'gravel', 'sandstone',
    'bedrock', 'lava', 'coal_ore', 'iron_ore', 'gold_ore', 'redstone_ore',
    'diamond_ore', 'emerald_ore', 'granite', 'diorite', 'andesite',
    'obsidian', 'cobblestone', 'clay', 'clay_block', 'hardened_clay',
    'terracotta', 'podzol', 'mycelium', 'coarse_dirt', 'rooted_dirt',
    'moss_block', 'moss_carpet', 'farmland', 'mud', 'mud_bricks',
    'packed_mud', 'soul_sand', 'soul_soil', 'basalt', 'blackstone',
    'magma_block', 'tuff', 'calcite', 'deepslate', 'cobbled_deepslate',
    'dirt_path', 'snow_block', 'powder_snow', 'ice', 'packed_ice',
    'blue_ice', 'red_sand', 'red_sandstone', 'snow', 'snow_layer',
    'short_grass', 'tall_grass', 'poppy', 'dandelion', 'blue_orchid',
    'azure_bluet', 'allium', 'cornflower', 'lily_of_the_valley',
    'oxeye_daisy', 'poppy', 'red_tulip', 'orange_tulip', 'white_tulip',
    'pink_tulip', 'fern', 'large_fern', 'sunflower', 'lilac',
    'rose_bush', 'peony', 'pitcher_plant', 'torchflower',
    'jungle_leaves', 'oak_leaves', 'spruce_leaves', 'acacia_leaves',
    'dark_oak_leaves', 'birch_leaves', 'mangrove_leaves', 'azalea_leaves',
    'cherry_leaves', 'flowering_azalea_leaves', 'jungle_log', 'oak_log',
    'spruce_log', 'acacia_log', 'dark_oak_log', 'birch_log',
    'mangrove_log', 'cherry_log', 'crimson_stem', 'warped_stem',
    'kelp', 'kelp_plant', 'seagrass', 'tall_seagrass', 'lily_pad',
    'bubble_coral', 'brain_coral', 'fire_coral', 'horn_coral',
    'tube_coral', 'sea_pickle', 'dead_bubble_coral', 'dead_brain_coral',
    'dead_fire_coral', 'dead_horn_coral', 'dead_tube_coral',
    'lantern', 'redstone_wire', 'rail', 'powered_rail', 'detector_rail',
    'activator_rail', 'chain', 'iron_bars', 'vine',
    'wall_torch', 'torch', 'soul_torch', 'soul_lantern',
    'redstone_torch', 'soul_fire', 'fire',
}

# Building blocks (NOT in terrain — these are buildings)
BUILDING = {
    'white_concrete', 'gray_concrete', 'light_gray_concrete',
    'black_concrete', 'red_concrete', 'blue_concrete', 'yellow_concrete',
    'green_concrete', 'orange_concrete', 'purple_concrete', 'pink_concrete',
    'cyan_concrete', 'magenta_concrete', 'lime_concrete', 'brown_concrete',
    'light_blue_concrete', 'glass', 'white_stained_glass', 'light_blue_stained_glass',
    'gray_stained_glass', 'black_stained_glass', 'red_stained_glass',
    'blue_stained_glass', 'cyan_stained_glass', 'quartz_block', 'smooth_stone',
    'brick_block', 'sea_lantern', 'gold_block', 'iron_block', 'redstone_block',
    'smooth_quartz', 'chiseled_quartz_block', 'quartz_pillar', 'quartz_stairs',
    'polished_diorite', 'polished_andesite', 'polished_granite', 'polished_blackstone',
    'stone_bricks', 'mossy_stone_bricks', 'cracked_stone_bricks',
    'smooth_stone_slab', 'stone_brick_slab', 'quartz_slab',
    'oak_planks', 'spruce_planks', 'dark_oak_planks', 'birch_planks',
    'jungle_planks', 'acacia_planks', 'mangrove_planks', 'cherry_planks',
    'oak_stairs', 'spruce_stairs', 'dark_oak_stairs', 'birch_stairs',
    'oak_fence', 'spruce_fence', 'dark_oak_fence', 'birch_fence',
    'oak_fence_gate', 'spruce_fence_gate', 'dark_oak_fence_gate',
    'oak_door', 'spruce_door', 'dark_oak_door', 'birch_door',
    'oak_sign', 'spruce_sign', 'dark_oak_sign', 'birch_sign',
    'red_carpet', 'blue_carpet', 'white_carpet', 'yellow_carpet',
    'green_carpet', 'black_carpet', 'gray_carpet', 'light_gray_carpet',
    'purple_carpet', 'pink_carpet', 'orange_carpet', 'cyan_carpet',
    'magenta_carpet', 'lime_carpet', 'brown_carpet', 'light_blue_carpet',
    'bookshelf', 'crafting_table', 'furnace', 'smoker', 'blast_furnace',
    'brewing_stand', 'enchanting_table', 'anvil', 'lectern',
    'note_block', 'jukebox', 'chest', 'trapped_chest', 'ender_chest',
    'shulker_box', 'barrel', 'loom', 'cartography_table', 'smithing_table',
    'grindstone', 'stonecutter', 'bell', 'smoking_pipe', 'honeycomb_block',
    'bed', 'white_bed', 'red_bed', 'blue_bed', 'green_bed', 'black_bed',
    'painting', 'item_frame', 'flower_pot', 'armor_stand',
    'water', 'lava', 'cobweb', 'ladder', 'scaffolding',
    'iron_trapdoor', 'oak_trapdoor', 'spruce_trapdoor',
    'iron_door', 'acacia_door', 'jungle_door', 'mangrove_door',
    'bell', 'lantern', 'soul_lantern', 'shroomlight', 'glowstone',
    'end_rod', 'sea_lantern', 'redstone_lamp', 'beacon',
    'ender_chest', 'enchanting_table',
    # Arnis tall building block
    'polished_deepslate',
}

def get_block(level, x, y, z):
    try:
        b = level.get_version_block(x, y, z, DIM, VER)
        return b[0].base_name if b else 'null'
    except Exception:
        return 'err'

def ground_y(level, x, z, lo=0, hi=200):
    """Find the y of the topmost non-air block at (x, z)."""
    for y in range(hi, lo, -1):
        b = get_block(level, x, y, z)
        if b not in ('air', 'null', 'err'):
            return y
    return lo

def is_building(name):
    """Is this a hand-placed building block (not terrain)?"""
    if name in TERRAIN:
        return False
    if name in ('air', 'null', 'err'):
        return False
    if name == 'water':  # pool water = building
        return True
    return True

def main():
    world = sys.argv[1] if len(sys.argv) > 1 else 'worlds/working/v2.3'
    print(f"Loading {world}...")
    level = amulet.load_level(world)

    print("Phase 1: Scanning hand-placed blocks (every 2 blocks)...")
    t0 = time.time()
    placed = defaultdict(list)  # cell -> [(x,y,z,name)]
    for x in range(0, 806, 2):
        for z in range(0, 961, 2):
            for y in range(20, 200):
                b = get_block(level, x, y, z)
                if not is_building(b):
                    continue
                placed[(x//30, z//30)].append((x, y, z, b))
    print(f"  Done in {time.time()-t0:.1f}s, {sum(len(v) for v in placed.values())} blocks")

    candidates = [(c, len(v)) for c, v in placed.items() if len(v) > 200]
    candidates.sort(key=lambda x: -x[1])
    print(f"  {len(candidates)} candidate cells (>200 blocks)")

    print("\nPhase 2: Detecting floating blocks...")
    floating_clusters = []
    for cell, _ in candidates:
        cx_min, cz_min = cell[0]*30, cell[1]*30
        blocks = placed[cell]
        cell_floating = []
        for (x, y, z, name) in blocks:
            gy = ground_y(level, x, z)
            gap = y - gy
            if gap > 1:
                cell_floating.append((x, y, z, name, gy, gap))
        if cell_floating:
            cell_floating.sort(key=lambda b: -b[5])
            cx_c = (cx_min + cx_min + 30) // 2
            cz_c = (cz_min + cz_min + 30) // 2
            # Get diagnostic info
            block_names = defaultdict(int)
            for _, _, _, n, _, _ in cell_floating:
                block_names[n] += 1
            floating_clusters.append({
                'cell': cell,
                'center': (cx_c, cz_c),
                'block_count': len(blocks),
                'floating_count': len(cell_floating),
                'block_names': dict(block_names),
                'worst': cell_floating[:8],
            })

    # Sort by max gap
    floating_clusters.sort(key=lambda c: -max(b[5] for b in c['worst']))

    print(f"\nFLOATING BUILDINGS (sorted by max gap):")
    for c in floating_clusters:
        cx, cz = c['center']
        avg_b = c['block_count']
        max_gap = max(b[5] for b in c['worst'])
        print(f"  ({cx},{cz}) {avg_b} blocks, {c['floating_count']} floating, max_gap={max_gap}")
        print(f"    types: {list(c['block_names'].items())[:5]}")
        for wb in c['worst'][:5]:
            print(f"    → ({wb[0]},{wb[1]},{wb[2]}) {wb[3]} gap={wb[5]} gy={wb[4]}")

    level.close()

    # Save
    with open('/tmp/v2_audit/floating_report.json', 'w') as f:
        json.dump(floating_clusters, f, indent=2, default=str)

    print(f"\nDone. {len(floating_clusters)} floating clusters found.")
    print(f"Total floating blocks: {sum(c['floating_count'] for c in floating_clusters)}")

if __name__ == '__main__':
    main()
