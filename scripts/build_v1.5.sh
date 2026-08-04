#!/usr/bin/env bash
# v1.5: Combined pipeline — interiors + more buildings + coastal + dynamic
set -e
cd /Users/yahweh/Desktop/ai应用社/hkust-minecraft
echo "=== Stage 1: Interiors ==="
python3.11 scripts/inject_interiors.py 2>&1 | tail -10
echo ""
echo "=== Stage 2: More buildings ==="
python3.11 scripts/inject_more_buildings.py 2>&1 | tail -10
echo ""
echo "=== Stage 3: Coastal ==="
python3.11 scripts/inject_coastal.py 2>&1 | tail -10
echo ""
echo "=== Stage 4: Dynamic elements ==="
python3.11 scripts/inject_dynamic.py 2>&1 | tail -10
echo ""
echo "=== Final result: worlds/working/v1.5e ==="
ls -la worlds/working/v1.5e 2>&1 | head -3
