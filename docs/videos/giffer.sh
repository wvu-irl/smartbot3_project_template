#!/usr/bin/env bash
set -euo pipefail

# Parse args
WIDTH=480
FILE=""

if [[ $# -gt 0 ]]; then
    if [[ "$1" =~ ^[0-9]+$ ]]; then
        WIDTH="$1"
        FILE="${2:-}"
    else
        FILE="$1"
        WIDTH="${2:-480}"
    fi
fi

# Determine file if not supplied
if [[ -z "$FILE" ]]; then
    FILE=$(ls -t *.webm *.mkv 2>/dev/null | head -n 1 || true)
fi

[[ -z "$FILE" ]] && { echo "No video found."; exit 1; }

base="${FILE%.*}"
gif="${base}.gif"

# Generate palette
ffmpeg -y -i "$FILE" \
    -vf "fps=10,scale=${WIDTH}:-1:flags=lanczos,palettegen=max_colors=64" \
    palette.png

# Apply palette
ffmpeg -y -i "$FILE" -i palette.png \
    -lavfi "fps=10,scale=${WIDTH}:-1:flags=lanczos,paletteuse=dither=bayer" \
    "$gif"

echo "Created: $gif"

