# HKUST in Minecraft

A 1:1 Minecraft Bedrock Edition recreation of the Hong Kong University of Science and Technology (HKUST) Clear Water Bay campus, generated from real-world OpenStreetMap data using [Arnis v3.0.0](https://github.com/louis-e/arnis).

![Annotated Top-Down](previews/hkust-topdown-annotated.png)

---

## What's inside

- **`worlds/final/HKUST-2026-Bedrock.mcworld`** — Ready-to-load Bedrock Edition world (~3 MB). Drop it into Minecraft Bedrock on Windows / iOS / Android / Xbox / PlayStation.
- **`landmarks/`** — Four Sponge Schematic files for HKUST's most iconic landmarks that Arnis doesn't model semantically:
  - `01-academic-dome.schem` (41×26×41, 3210 blocks) — the round academic dome
  - `02-circle-of-time-sundial.schem` (9×8×9, 183 blocks) — Red Bird sundial at North Gate
  - `03-one-world-fountain.schem` (13×6×13, 343 blocks) — One-World Fountain at Central Piazza
  - `04-seaview-railings.schem` (601×3×5, 1852 blocks) — 600 m balustrade along Clear Water Bay
- **`previews/`** — Top-down PNG previews of the generated map, annotated with the 4 hand-built landmarks.
- **`osm/hkust-overpass.json`** — Offline-cached Overpass API dump for reproducible builds.
- **`scripts/`** — Generation + annotation Python / shell scripts.
- **`arnis/`** — Arnis v3.0.0 macOS universal binary (`arnis-mac-universal`, 107 MB).

---

## Coverage

| | |
|---|---|
| Bounding box | `22.3317768,114.2617409,22.3404248,114.2695826` |
| OSM relation | way `40664120` (amenity=university) |
| Scale | 1 block per meter (1:1) |
| Generation | ~6 seconds on M-series Mac, ~1.5 GB peak RAM |
| Output format | Bedrock `.mcworld` with ±512 build-height behavior pack (requires Minecraft 1.21.40+) |

---

## How it was built

### 1. Cache OSM data (one-time, offline-reusable)

```bash
./arnis/arnis-mac-universal \
  --bbox="22.3317768,114.2617409,22.3404248,114.2695826" \
  --save-json-file=osm/hkust-overpass.json \
  --aws-only-elevation
```

### 2. Generate the world

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
  --fillground
```

### 3. Hand-build the landmarks

`python3 landmarks/generate_schems.py` produces the four Sponge Schematic files. Load each with WorldEdit BE in the Bedrock client:

```
//schem load 01-academic-dome
//schem paste
```

Detailed coordinates and material guides are in `landmarks/README.md`.

### 4. Render the annotated preview

```bash
python3 scripts/annotate_preview.py
```

---

## Requirements

- macOS Apple Silicon or Intel (the `arnis-mac-universal` binary works on both)
- Minecraft Bedrock Edition 1.21.40 or newer (for the extended build-height behavior pack)
- For schematic rebuilding: WorldEdit BE addon (optional)

---

## Embed on a website

The annotated top-down PNG is included as `previews/hkust-topdown-annotated.png`. The HKUST AI Applications Society admission-letter site embeds it at `src/app/content/minecraft/page.tsx` with a download link to `HKUST-2026-Bedrock.mcworld`.

---

## Credits

- Data: [OpenStreetMap contributors](https://www.openstreetmap.org/copyright) (ODbL)
- Elevation: Mapterhorn + AWS Terrain Tiles + regional high-res providers
- Building enrichment: [Overture Maps](https://overturemaps.org/)
- Generation: [Arnis](https://github.com/louis-e/arnis) by [@louis-e](https://github.com/louis-e) and contributors (Apache-2.0)
- Project: HKUST AI Application Society · Cyber Foundation · 2026

---

## License

The HKUST campus data is derived from OpenStreetMap (ODbL). The generated Minecraft world, schematics, and annotated previews are released under CC BY-SA 4.0 by the HKUST AI Application Society.
