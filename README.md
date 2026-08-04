# HKUST in Minecraft

A 1:1 Minecraft Bedrock Edition recreation of the Hong Kong University of Science and Technology (HKUST) Clear Water Bay campus, generated from real-world OpenStreetMap + Mapterhorn elevation data using [Arnis v3.0.0](https://github.com/louis-e/arnis).

![v1.1 Top-Down](worlds/final/hkust_topdown_v1.1.png)

---

## What's in v1.1

- **`worlds/final/HKUST-2026-Bedrock-v1.1.mcworld`** — Ready-to-load Bedrock Edition world (~8 MB) with **5 hand-built landmarks already embedded in the world** — drop it into Minecraft Bedrock and see them immediately.
- **`worlds/final/hkust_topdown_v1.1.png`** — Annotated top-down preview showing landmark positions.
- **`scripts/inject_landmarks_amulet.py`** — Landmarinjection pipeline (amulet + LevelDB backend).
- **`scripts/patch_amulet_for_arnis.sh`** — Applies 2 patches to amulet-core so it can read Arnis-generated Bedrock 1.21.40 worlds.
- **`landmarks/`** — Original blueprint JSON for HKUST's four most iconic landmarks.

### Hand-built landmarks (auto-injected in v1.1)

| Landmark | Position (X/Y/Z) | Blocks | Description |
|----------|------------------|--------|-------------|
| **Academic Building Dome** | 200 / 127 / 500 | 6,907 | 40 m hemispheric dome on the elevated plateau |
| **Circle of Time Sundial** | 185 / 127 / 530 | 1,744 | Quartz-pillar compass sundial plaza |
| **One-World Fountain** | 279 / 78 / 663 | 492 | Sea-lantern + gold-block fountain with blue basin |
| **Seaview Walkway** | 480 / 65 / 380 | 620 | 80 m oak-slab walkway with brick pillars + dark oak railings |
| **HKUST Library** | 130 / 84 / 580 | 2,162 | 24×18×18 glass-and-white-concrete library tower |

**Total: 11,925 hand-placed blocks across 5 landmarks.**

---

## What's in v1.0 → v1.0.1 → v1.1

### v1.0.1 (previous)
- Real Mapterhorn elevation instead of 30 m AWS Terrain Tiles
- Climate-driven biomes, region-aware tree pack
- Building interiors + baked lighting
- 4 landmarks: blueprint JSON only (paste-only)

### v1.1 (current) — **Goal: highest-fidelity replica**
- **5 landmarks auto-injected into `.mcworld`** via patched amulet + Bedrock LevelDB
- **Heightmap-aligned** — each landmark scans local ground height and perches correctly on slope
- **Verified by playing** — diamond_block test marker injected and read back from a fresh load
- **Reproducible** — `scripts/inject_landmarks_amulet.py` rebuilds landmarks from scratch in ~2 seconds

> **Roadmap to v1.1 GA (perfect replica):** Building heights from Hong Kong Lands Department 3D Tiles (218k buildings, 12M triangles) — next iteration will voxelize the actual building footprints and replace the 5 schematic landmarks with height-accurate volumes.

---

## How it was built

### 1. Cache OSM data (one-time, offline-reusable)

```bash
./arnis/arnis-mac-universal \
  --bbox="22.3317768,114.2617409,22.3404248,114.2695826" \
  --save-json-file=osm/hkust-overpass.json
```

### 2. Generate the world (v1.0.1 command, unchanged for v1.1)

```bash
./arnis/arnis-mac-universal \
  --file=osm/hkust-overpass.json \
  --bedrock \
  --output-dir=worlds/final \
  --bbox="22.3317768,114.2617409,22.3404248,114.2695826" \
  --scale=1.0 \
  --spawn-lat=22.3383 --spawn-lng=114.2683 \
  --gamemode=creative \
  --world-time=6000 \
  --disable-height-limit \
  --map-preview \
  --overture=true \
  --fillground \
  --terrain \
  --interior=true \
  --bake-lighting
```

### 3. Inject hand-built landmarks (NEW for v1.1)

```bash
# One-time: patch amulet-core to read Arnis 1.21.40 worlds
./scripts/patch_amulet_for_arnis.sh

# Inject landmarks into the generated world
python3 scripts/inject_landmarks_amulet.py \
  --world /tmp/hkust_extracted \
  --dry-run                    # preview first
python3 scripts/inject_landmarks_amulet.py \
  --world /tmp/hkust_extracted # actually inject
```

---

## Files

| Path | Purpose |
|------|---------|
| `worlds/final/HKUST-2026-Bedrock-v1.1.mcworld` | The world (8.3 MB) |
| `worlds/final/hkust_topdown_v1.1.png` | Annotated top-down preview |
| `worlds/final/HKUST-2026-Bedrock.mcworld` | v1.0.1 (no landmarks injected) |
| `arnis/arnis-mac-universal` | Arnis v3.0.0 binary (107 MB) |
| `osm/hkust-overpass.json` | Cached Overpass API dump |
| `landmarks/` | Blueprint JSON for landmarks |
| `scripts/inject_landmarks_amulet.py` | Landmark injection pipeline |
| `scripts/patch_amulet_for_arnis.sh` | amulet Arnis compatibility patch |
| `scripts/annotate_preview.py` | Top-down renderer (annotates blocks → colors) |

---

## amulet Arnis Compatibility

Standard `amulet-core` (v1.9.43) cannot read Arnis-generated Bedrock 1.21.40 worlds because:

1. Arnis writes the `+` key data as 540 bytes (512 heightmap + 28 biome header) instead of 544 → `struct.error: unpack requires a buffer of 4 bytes`
2. The biome loop consumes data in 5-byte chunks, leaving 2 bytes at the end that triggers the same struct error

`scripts/patch_amulet_for_arnis.sh` applies two one-line patches to `amulet/level/formats/leveldb_world/interface/chunk/base_leveldb_interface.py` so amulet can read, modify, and write back into Arnis worlds.

---

## Requirements

- macOS Apple Silicon or Intel (the `arnis-mac-universal` binary works on both)
- Minecraft Bedrock Edition **1.21.40 or newer** (for the extended build-height behavior pack)
- Python 3.11 (M-series native)
- `pip install amulet-core leveldb pillow`

---

## Embed on a website

The annotated top-down PNG is included as `worlds/final/hkust_topdown_v1.1.png`. The HKUST AI Applications Society admission-letter site embeds it at `src/app/content/minecraft/page.tsx` with a download link to `HKUST-2026-Bedrock-v1.1.mcworld`.

---

## Credits

- Data: [OpenStreetMap contributors](https://www.openstreetmap.org/copyright) (ODbL)
- Elevation: Mapterhorn (global) + AWS Terrain Tiles + regional high-res providers
- Building enrichment: [Overture Maps](https://overturemaps.org/)
- Generation: [Arnis](https://github.com/louis-e/arnis) by [@louis-e](https://github.com/louis-e) and contributors (Apache-2.0)
- Injection: amulet-core + custom LevelDB patches
- Project: HKUST AI Application Society · Cyber Foundation · 2026

---

## License

The HKUST campus data is derived from OpenStreetMap (ODbL). The generated Minecraft world, schematics, and annotated previews are released under CC BY-SA 4.0 by the HKUST AI Application Society.
