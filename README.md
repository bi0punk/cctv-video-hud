# OpenCV Sci-Tech HUD RTSP + Open-Meteo

Proyecto completo para mostrar una transmisión de cámara RTSP real con un marco sci-tech HUD y datos meteorológicos en tiempo real vía Open-Meteo. Aplicación web Flask con OpenCV + Gunicorn.

[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0%2B-000000?logo=flask)](https://flask.palletsprojects.com/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.10%2B-5C3EE8?logo=opencv)](https://opencv.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker)](https://www.docker.com/)
[![CI](https://github.com/bi0punk/cctv-video-hud/actions/workflows/ci.yml/badge.svg)](https://github.com/bi0punk/cctv-video-hud/actions/workflows/ci.yml)

## Contenido

- [Características](#características)
- [Arquitectura](#arquitectura)
- [Stack](#stack)
- [Estructura del repositorio](#estructura-del-repositorio)
- [Requisitos](#requisitos)
- [Instalación](#instalación)
- [Uso](#uso)
- [Configuración](#configuración)
- [API](#api)
- [Tests / CI](#tests--ci)
- [Docker](#docker)
- [Roadmap](#roadmap)
- [Licencia](#licencia)

## Características

- Streaming RTSP con transporte TCP para estabilidad.
- HUD sci-tech overlay: datos de cámara + clima en tiempo real.
- Open-Meteo: datos meteorológicos por coordenadas (gratis, sin API key).
- HUD web vs HUD quemado: overlay en navegador o directamente en el frame.
- Modo demo sin cámara para desarrollo/pruebas.
- Docker listo: `docker compose up --build`.
- Fallos resilientes: reconexión automática con backoff.
- Unidad systemd opcional.
- Herramienta CLI para probar el RTSP antes de la web.

## Arquitectura

```mermaid
flowchart TD
  SRC[CAMERA_SOURCE: RTSP / webcam / demo] --> CAM[CameraStream camera.py]
  CAM --> APP[app.py Flask]
  TM[telemetry.py Open-Meteo] --> APP
  APP --> HUD1[HUD web CSS sobre MJPEG]
  APP --> HUD2[BURN_HUD_IN_FRAME: overlay quemado con OpenCV]
  HUD1 --> WEB[Navegador :5000]
  HUD2 --> WEB
  APP --> API1[/api/health/]
  APP --> API2[/api/stats/]
  APP --> API3[/video_feed/]
```

- **CameraStream**: captura RTSP con OpenCV y opciones TCP para estabilidad.
- **telemetry.py**: caché TTL de Open-Meteo con fallback simulado si la API no responde.
- **app.py**: sirve MJPEG (`/video_feed`), HUD CSS por defecto o overlay quemado con `?burn=true`, y endpoints JSON.

## Stack

| Componente | Tecnología |
|---|---|
| Backend | Python 3.11+, Flask 3.0+ |
| Visión | OpenCV 4.10+, NumPy |
| Clima | Open-Meteo API (gratuita) |
| Frontend | HTML5, CSS3, JavaScript |
| Contenedor | Docker + docker-compose |
| Servidor | Gunicorn (producción) |
| Testing | pytest |

## Estructura del repositorio

```
cctv-video-hud/
├── app.py                  # Aplicación Flask
├── camera.py               # Captura RTSP con OpenCV
├── config.py               # Config desde .env + args
├── telemetry.py            # Clima + métricas del sistema
├── burned_overlay.py       # HUD quemado en frame OpenCV
├── static/                 # css/js
├── templates/              # index.html, simple.html
├── scripts/                # run_demo.sh, run_dev.sh, run_rtsp_example.sh
├── tools/                  # test_rtsp.py, test_openmeteo.py (CLI)
├── systemd/                # Unidad systemd opcional
├── tests/                  # test_smoke.py
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── .env.rtsp.example       # Config mínima solo RTSP
├── .github/workflows/ci.yml
└── README.md
```

## Requisitos

- Python 3.11+
- Cámara RTSP (Hikvision, Dahua, Ezviz, etc.) o modo demo.
- Conexión a internet (para API Open-Meteo).
- Docker (opcional).

## Instalación

```bash
git clone https://github.com/bi0punk/cctv-video-hud.git
cd cctv-video-hud
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python app.py
```

Abrir: `http://127.0.0.1:5000`

## Uso

### Cámara real RTSP

```env
CAMERA_SOURCE=rtsp://usuario:password@192.168.1.50:554/Streaming/Channels/101
```

Para Hikvision: main stream = `/101`, sub stream = `/102`.

### Modo demo sin cámara

```bash
./scripts/run_demo.sh
```

O en `.env`: `CAMERA_SOURCE=demo`.

### Probar RTSP antes de levantar la web

```bash
python tools/test_rtsp.py --url "rtsp://usuario:password@IP:554/..." --seconds 10 --save test.jpg
```

### HUD web vs HUD quemado

- HUD web: `http://127.0.0.1:5000/video_feed`
- HUD quemado: `http://127.0.0.1:5000/video_feed?burn=true`

## Configuración

Variables de entorno (ver `.env.example`):

| Variable | Default | Descripción |
|---|---|---|
| `CAMERA_SOURCE` | `demo` | URL RTSP, `0` (webcam USB) o `demo` |
| `STATION_NAME` | `ESTACIÓN VALLENAR` | Nombre de estación en el HUD |
| `STATION_LAT` / `STATION_LON` | `-28.5700` / `-70.7600` | Coordenadas para Open-Meteo |
| `APP_TZ` | `America/Santiago` | Zona horaria |
| `APP_HOST` / `APP_PORT` | `0.0.0.0` / `5000` | Bind del servidor |
| `FRAME_WIDTH` / `FRAME_HEIGHT` | `1280` / `720` | Resolución del frame |
| `JPEG_QUALITY` | `82` | Calidad JPEG (0-100) |
| `OPENCV_FFMPEG_CAPTURE_OPTIONS` | — | Opciones RTSP TCP |
| `WEATHER_ENABLED` | `true` | Habilita Open-Meteo |
| `WEATHER_TTL_SECONDS` | `300` | Caché del clima |
| `ALLOW_SIMULATED_FALLBACK` | `true` | Fallback simulado si la API falla |
| `BURN_HUD_IN_FRAME` | `false` | HUD quemado por defecto |

## API

| Ruta | Descripción |
|---|---|
| `/` | Vista principal (HUD) |
| `/simple` | Vista simple sin HUD |
| `/video_feed` | Stream MJPEG |
| `/video_feed?burn=true` | Stream con HUD quemado |
| `/api/stats` | Métricas + clima (JSON) |
| `/api/health` | Healthcheck |
| `/api/config` | Configuración activa (JSON) |
| `/api/frame` | Frame único (JPEG) |

## Tests / CI

```bash
pip install pytest
pytest tests/ -v
```

GitHub Actions: lint (Ruff) + tests (pytest) en cada push/PR sobre Python 3.11.

## Docker

```bash
cp .env.example .env
docker compose up --build
```

Para cámara web USB local en Linux, descomenta el bloque `devices` en `docker-compose.yml`.

## Roadmap

- [x] Streaming RTSP con overlay HUD sci-tech
- [x] Clima en tiempo real con Open-Meteo
- [x] Modo demo y Docker
- [ ] Grabación programada (DVR)
- [ ] Detección de movimiento con OpenCV
- [ ] Múltiples cámaras simultáneas
- [ ] Historial de métricas meteorológicas
- [ ] Autenticación básica para la web
- [ ] HTTPS con certificados Let's Encrypt

## Licencia

MIT — ver [LICENSE](LICENSE).