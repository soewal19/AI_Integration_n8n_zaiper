#!/usr/bin/env bash
set -euo pipefail
INTERVAL="${1:-60}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"
python monitor.py --watch --interval "$INTERVAL"

