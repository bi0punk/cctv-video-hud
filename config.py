import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


def bool_env(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


@dataclass(frozen=True)
class Settings:
    app_host: str = os.getenv("APP_HOST", "0.0.0.0")
    app_port: int = int(os.getenv("APP_PORT", "5000"))
    app_tz: str = os.getenv("APP_TZ", "America/Santiago")
    app_debug: bool = bool_env("APP_DEBUG", False)

    camera_source: str = os.getenv("CAMERA_SOURCE", "demo")
    frame_width: int = int(os.getenv("FRAME_WIDTH", "1280"))
    frame_height: int = int(os.getenv("FRAME_HEIGHT", "720"))
    jpeg_quality: int = int(os.getenv("JPEG_QUALITY", "82"))
    frame_sleep_ms: int = int(os.getenv("FRAME_SLEEP_MS", "10"))

    station_name: str = os.getenv("STATION_NAME", "ESTACIÓN VALLENAR")
    station_lat: float = float(os.getenv("STATION_LAT", "-28.5700"))
    station_lon: float = float(os.getenv("STATION_LON", "-70.7600"))

    weather_enabled: bool = bool_env("WEATHER_ENABLED", True)
    weather_ttl_seconds: int = int(os.getenv("WEATHER_TTL_SECONDS", "300"))
    open_meteo_timeout_seconds: int = int(os.getenv("OPEN_METEO_TIMEOUT_SECONDS", "8"))
    allow_simulated_fallback: bool = bool_env("ALLOW_SIMULATED_FALLBACK", True)

    burn_hud_in_frame: bool = bool_env("BURN_HUD_IN_FRAME", False)


settings = Settings()
