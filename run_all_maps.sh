#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

mapfile -t maps < <(find "./maps" -type f -name "*.txt" | sort)

if [[ ${#maps[@]} -eq 0 ]]; then
    echo "No map files found under ./maps"
    exit 1
fi

echo "Found ${#maps[@]} map(s). Running one by one..."

for map in "${maps[@]}"; do
    echo
    echo "=== Running map: $map ==="
    make run ARGS="--map=$map"
done

echo
echo "All maps completed successfully."
