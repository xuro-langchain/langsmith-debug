#!/usr/bin/env bash
set -euo pipefail

# Resolve project root based on this script's directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

docker volume create n8n_data

python3 "$PROJECT_ROOT/db.py"


