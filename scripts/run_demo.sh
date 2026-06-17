#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [ ! -d ".venv" ]; then python3 -m venv .venv; fi
source .venv/bin/activate
pip install -r requirements.txt
export CAMERA_SOURCE=demo
export STATION_NAME="ESTACIÓN DEMO"
export STATION_LAT="-28.5700"
export STATION_LON="-70.7600"
python app.py
