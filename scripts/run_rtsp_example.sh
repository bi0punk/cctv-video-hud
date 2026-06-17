#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [ ! -d ".venv" ]; then python3 -m venv .venv; fi
source .venv/bin/activate
pip install -r requirements.txt
export CAMERA_SOURCE="rtsp://usuario:password@192.168.1.50:554/Streaming/Channels/101"
export OPENCV_FFMPEG_CAPTURE_OPTIONS="rtsp_transport;tcp|stimeout;5000000|max_delay;500000"
export STATION_NAME="CÁMARA NORTE"
export STATION_LAT="-28.5700"
export STATION_LON="-70.7600"
python app.py
