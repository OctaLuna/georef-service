#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DATA_DIR="$SCRIPT_DIR/../data"

mkdir -p "$DATA_DIR"

echo "Downloading GADM 4.1 Bolivia level 2 (departments + municipalities)..."
curl -L "https://geodata.ucdavis.edu/gadm/gadm4.1/json/gadm41_BOL_2.json" \
     -o "$DATA_DIR/bolivia.geojson"

SIZE=$(wc -c < "$DATA_DIR/bolivia.geojson")
echo "Downloaded $SIZE bytes -> $DATA_DIR/bolivia.geojson"
