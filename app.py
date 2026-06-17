#!/usr/bin/env python3
import logging
import time

from flask import Flask, Response, jsonify, render_template, request

from burned_overlay import burn_hud
from camera import CameraStream
from config import settings
from telemetry import build_stats_payload

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s | %(message)s")
log = logging.getLogger("opencv-hud")
app = Flask(__name__)
camera = CameraStream(settings.camera_source)
camera.start()


def _parse_float_arg(name: str):
    value = request.args.get(name)
    if value is None or value == "":
        return None
    return float(value)


def current_stats_from_request():
    lat = _parse_float_arg("lat")
    lon = _parse_float_arg("lon")
    return build_stats_payload(camera_fps=camera.fps_estimated, lat=lat, lon=lon)


def generate_mjpeg(burn: bool = False):
    while True:
        frame = camera.get_frame()
        if frame is None:
            time.sleep(0.1)
            continue
        if burn:
            try:
                stats = build_stats_payload(camera_fps=camera.fps_estimated)
                frame = burn_hud(frame, stats)
            except Exception as exc:
                log.warning("No se pudo quemar HUD: %s", exc)
        jpg = camera.get_jpeg(frame)
        if jpg is None:
            time.sleep(0.05)
            continue
        yield b"--frame\r\nContent-Type: image/jpeg\r\nCache-Control: no-cache\r\n\r\n" + jpg + b"\r\n"


@app.route("/")
def index():
    return render_template("index.html", station_name=settings.station_name, station_lat=settings.station_lat, station_lon=settings.station_lon, burn_default=str(settings.burn_hud_in_frame).lower())


@app.route("/video_feed")
def video_feed():
    burn = request.args.get("burn", str(settings.burn_hud_in_frame)).lower() in {"1", "true", "yes", "on"}
    return Response(generate_mjpeg(burn=burn), mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route("/api/stats")
def api_stats():
    try:
        return jsonify(current_stats_from_request())
    except Exception as exc:
        log.exception("Error en /api/stats")
        return jsonify({"status": "ERROR", "stream_state": "ERROR", "error": str(exc)}), 500


@app.route("/api/health")
def api_health():
    return jsonify({"ok": True, "camera": camera.health(), "station_name": settings.station_name, "station_lat": settings.station_lat, "station_lon": settings.station_lon, "weather_enabled": settings.weather_enabled, "burn_hud_in_frame": settings.burn_hud_in_frame})


@app.route("/api/config")
def api_config():
    return jsonify({"station_name": settings.station_name, "station_lat": settings.station_lat, "station_lon": settings.station_lon, "timezone": settings.app_tz, "weather_ttl_seconds": settings.weather_ttl_seconds, "camera_source": settings.camera_source})


if __name__ == "__main__":
    log.info("Iniciando OpenCV HUD en %s:%s", settings.app_host, settings.app_port)
    log.info("Camera source: %s", settings.camera_source)
    try:
        app.run(host=settings.app_host, port=settings.app_port, debug=settings.app_debug, threaded=True)
    finally:
        camera.stop()
