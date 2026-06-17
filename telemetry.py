import math
import random
import threading
import time
from datetime import datetime
from zoneinfo import ZoneInfo

import requests

from config import settings


class TTLCache:
    def __init__(self, ttl_seconds: int):
        self.ttl_seconds = ttl_seconds
        self._lock = threading.Lock()
        self._data = None
        self._ts = 0.0

    def get(self):
        with self._lock:
            if self._data is None:
                return None
            if time.time() - self._ts > self.ttl_seconds:
                return None
            return self._data

    def set(self, data: dict):
        with self._lock:
            self._data = data
            self._ts = time.time()

    def age_seconds(self) -> float:
        with self._lock:
            if self._data is None:
                return -1
            return max(0.0, time.time() - self._ts)


_weather_cache = TTLCache(settings.weather_ttl_seconds)


def weather_code_to_text(code) -> str:
    if code is None:
        return "SIN DATOS"
    mapping = {
        0: "DESPEJADO", 1: "MAYORMENTE DESPEJADO", 2: "PARCIALMENTE NUBLADO", 3: "NUBLADO",
        45: "NIEBLA", 48: "NIEBLA ESCARCHADA", 51: "LLOVIZNA LEVE", 53: "LLOVIZNA",
        55: "LLOVIZNA INTENSA", 61: "LLUVIA LEVE", 63: "LLUVIA", 65: "LLUVIA INTENSA",
        71: "NIEVE LEVE", 73: "NIEVE", 75: "NIEVE INTENSA", 80: "CHUBASCOS LEVES",
        81: "CHUBASCOS", 82: "CHUBASCOS INTENSOS", 95: "TORMENTA", 96: "TORMENTA CON GRANIZO",
        99: "TORMENTA FUERTE",
    }
    return mapping.get(int(code), f"CÓDIGO {code}")


def aqi_to_label(us_aqi) -> str:
    if us_aqi is None:
        return "SIN DATOS"
    value = float(us_aqi)
    if value <= 50:
        return "BUENA"
    if value <= 100:
        return "MODERADA"
    if value <= 150:
        return "MALA SENSIBLES"
    if value <= 200:
        return "MALA"
    if value <= 300:
        return "MUY MALA"
    return "PELIGROSA"


def wind_direction_to_cardinal(degrees) -> str:
    if degrees is None:
        return "--"
    dirs = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSO", "SO", "OSO", "O", "ONO", "NO", "NNO"]
    idx = int((float(degrees) + 11.25) / 22.5) % 16
    return dirs[idx]


def _fetch_json(url: str, params: dict, timeout: int) -> dict:
    response = requests.get(url, params=params, timeout=timeout)
    response.raise_for_status()
    return response.json()


def fetch_openmeteo(lat: float, lon: float) -> dict:
    weather_url = "https://api.open-meteo.com/v1/forecast"
    air_url = "https://air-quality-api.open-meteo.com/v1/air-quality"
    weather_params = {
        "latitude": lat,
        "longitude": lon,
        "current": ",".join([
            "temperature_2m", "relative_humidity_2m", "apparent_temperature", "precipitation",
            "rain", "weather_code", "cloud_cover", "pressure_msl", "surface_pressure",
            "wind_speed_10m", "wind_direction_10m", "wind_gusts_10m",
        ]),
        "timezone": settings.app_tz,
        "temperature_unit": "celsius",
        "wind_speed_unit": "kmh",
        "precipitation_unit": "mm",
    }
    air_params = {
        "latitude": lat,
        "longitude": lon,
        "current": ",".join(["us_aqi", "pm10", "pm2_5", "carbon_monoxide", "nitrogen_dioxide", "ozone", "uv_index"]),
        "timezone": settings.app_tz,
    }
    timeout = settings.open_meteo_timeout_seconds
    weather_data = _fetch_json(weather_url, weather_params, timeout)
    air_data = _fetch_json(air_url, air_params, timeout)
    cw = weather_data.get("current", {})
    ca = air_data.get("current", {})
    wind_speed = cw.get("wind_speed_10m")
    wind_dir = cw.get("wind_direction_10m")
    if wind_speed is not None and wind_dir is not None:
        wind_text = f"{round(float(wind_speed), 1)} km/h · {wind_direction_to_cardinal(wind_dir)}"
    elif wind_speed is not None:
        wind_text = f"{round(float(wind_speed), 1)} km/h"
    else:
        wind_text = "SIN DATOS"
    return {
        "source": "open-meteo",
        "temperature": cw.get("temperature_2m"),
        "apparent_temperature": cw.get("apparent_temperature"),
        "humidity": cw.get("relative_humidity_2m"),
        "pressure": cw.get("surface_pressure"),
        "pressure_msl": cw.get("pressure_msl"),
        "precipitation": cw.get("precipitation"),
        "rain": cw.get("rain"),
        "weather_code": cw.get("weather_code"),
        "weather": weather_code_to_text(cw.get("weather_code")),
        "cloud_cover": cw.get("cloud_cover"),
        "wind_speed": wind_speed,
        "wind_direction": wind_dir,
        "wind": wind_text,
        "wind_gusts": cw.get("wind_gusts_10m"),
        "air_quality": aqi_to_label(ca.get("us_aqi")),
        "us_aqi": ca.get("us_aqi"),
        "pm10": ca.get("pm10"),
        "pm2_5": ca.get("pm2_5"),
        "co": ca.get("carbon_monoxide"),
        "no2": ca.get("nitrogen_dioxide"),
        "ozone": ca.get("ozone"),
        "uv_index": ca.get("uv_index"),
    }


def simulated_external_data() -> dict:
    t = time.time()
    return {
        "source": "simulated",
        "temperature": round(22.0 + math.sin(t / 60) * 1.5 + random.uniform(-0.2, 0.2), 1),
        "apparent_temperature": round(22.4 + math.sin(t / 55) * 1.3, 1),
        "humidity": round(63 + math.sin(t / 80) * 8 + random.uniform(-1, 1), 1),
        "pressure": round(1012 + math.sin(t / 120) * 3, 0),
        "pressure_msl": round(1015 + math.sin(t / 120) * 3, 0),
        "precipitation": 0,
        "rain": 0,
        "weather_code": 2,
        "weather": "PARCIALMENTE NUBLADO",
        "cloud_cover": round(38 + math.sin(t / 90) * 18, 0),
        "wind_speed": round(12 + math.sin(t / 70) * 3, 1),
        "wind_direction": 45,
        "wind": "12 km/h · NE",
        "wind_gusts": round(18 + math.sin(t / 50) * 4, 1),
        "air_quality": "BUENA",
        "us_aqi": round(34 + math.sin(t / 65) * 8, 0),
        "pm10": round(24 + math.sin(t / 75) * 5, 1),
        "pm2_5": round(11 + math.sin(t / 85) * 3, 1),
        "co": 140,
        "no2": 8,
        "ozone": 64,
        "uv_index": 2,
    }


def get_weather_data(lat: float, lon: float) -> tuple[dict, str]:
    cached = _weather_cache.get()
    if cached is not None:
        return cached, "cache"
    if not settings.weather_enabled:
        data = simulated_external_data()
        _weather_cache.set(data)
        return data, "simulated-disabled"
    try:
        data = fetch_openmeteo(lat, lon)
        _weather_cache.set(data)
        return data, "live"
    except Exception as exc:
        if settings.allow_simulated_fallback:
            data = simulated_external_data()
            data["source_error"] = str(exc)
            _weather_cache.set(data)
            return data, "fallback"
        raise


def build_stats_payload(camera_fps: float, lat: float | None = None, lon: float | None = None) -> dict:
    lat = settings.station_lat if lat is None else lat
    lon = settings.station_lon if lon is None else lon
    now = datetime.now(ZoneInfo(settings.app_tz))
    weather, mode = get_weather_data(lat, lon)
    signal = round(96 + random.uniform(-2, 2), 0)
    latency = round(28 + random.uniform(-6, 8), 0)
    cpu = round(34 + random.uniform(-8, 8), 0)
    status = "EN LÍNEA" if mode in {"live", "cache"} else "DEGRADADO"
    return {
        "date": now.strftime("%d %b %Y").upper(), "time": now.strftime("%H:%M:%S"), "timestamp_iso": now.isoformat(),
        "location": settings.station_name, "latitude": lat, "longitude": lon, "status": status,
        "telemetry_mode": mode, "cache_age_seconds": round(_weather_cache.age_seconds(), 1),
        "humidity": weather.get("humidity"), "temperature": weather.get("temperature"),
        "apparent_temperature": weather.get("apparent_temperature"), "pressure": weather.get("pressure"),
        "pressure_msl": weather.get("pressure_msl"), "weather": weather.get("weather"),
        "weather_code": weather.get("weather_code"), "cloud_cover": weather.get("cloud_cover"),
        "precipitation": weather.get("precipitation"), "rain": weather.get("rain"),
        "wind": weather.get("wind"), "wind_speed": weather.get("wind_speed"),
        "wind_direction": weather.get("wind_direction"), "wind_gusts": weather.get("wind_gusts"),
        "air_quality": weather.get("air_quality"), "us_aqi": weather.get("us_aqi"),
        "pm10": weather.get("pm10"), "pm2_5": weather.get("pm2_5"), "co": weather.get("co"),
        "no2": weather.get("no2"), "ozone": weather.get("ozone"), "uv_index": weather.get("uv_index"),
        "signal": signal, "fps": round(camera_fps, 1), "cpu": cpu, "latency": latency, "stream_state": "OK",
    }
