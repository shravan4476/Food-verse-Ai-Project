#!/usr/bin/env bash
# Epic 1 - environment setup
set -euo pipefail
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements-core.txt
[ -f .env ] || cp .env.example .env
echo "Core environment ready. For full vision stack run: pip install -r requirements.txt"
