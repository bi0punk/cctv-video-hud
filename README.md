# OpenCV Sci-Tech HUD RTSP + Open-Meteo

[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0%2B-000000?logo=flask)](https://flask.palletsprojects.com/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.10%2B-5C3EE8?logo=opencv)](https://opencv.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker)](https://www.docker.com/)
[![CI](https://github.com/drbash/cctv-video-hud/actions/workflows/ci.yml/badge.svg)](https://github.com/drbash/cctv-video-hud/actions)

Proyecto completo para mostrar una transmisión de cámara RTSP real con un marco **sci-tech HUD** y datos meteorológicos en tiempo real vía Open-Meteo.

## Contenido

- [Características](#caracter%C3%ADsticas)
- [Stack](#stack)
- [Estructura](#estructura)
- [Requisitos](#requisitos)
- [Instalación](#instalaci%C3%B3n)
- [Uso](#uso)
- [API](#api)
- [Tests](#tests)
- [Configuración](#configuraci%C3%B3n)
- [CI/CD](#cicd)
- [Docker](#docker)
- [Troubleshooting RTSP](#troubleshooting-rtsp)
- [Limitaciones / Roadmap](#limitaciones--roadmap)
- [Licencia](#licencia)

## Características

- **Streaming RTSP** con transporte TCP para estabilidad
- **HUD sci-tech overlay**: datos de cámara + clima en tiempo real
- **Open-Meteo**: datos meteorológicos por coordenadas (gratis, sin API key)
- **HUD web vs HUD quemado**: overlay en navegador o directamente en el frame
- **Modo demo** sin cámara para desarrollo/pruebas
- **Docker listo**: `docker compose up --build`
- **Fallos resilientes**: reconexión automática con backoff

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

## Estructura

```
cctv-video-hud/
├── app.py                  # Aplicación Flask
├── camera.py               # Captura RTSP con OpenCV
├── config.py               # Config desde .env + args
├── telemetry.py            # Clima + métricas del sistema
├── burned_overlay.py       # HUD quemado en frame OpenCV
├── static/                 # Assets frontend
├── templates/
│   └── index.html          # Interfaz web
├── scripts/
│   └── run_demo.sh         # Demo sin cámara
├── tools/
│   └── test_rtsp.py        # Probador RTSP CLI
├── systemd/                # Unidad systemd opcional
├── Dockerfile
├── docker-compose.yml
├── tests/
├── .env.example
├── .github/workflows/ci.yml
├── pyproject.toml
└── README.md
```

## Requisitos

- Python 3.11+
- Cámara RTSP (Hikvision, Dahua, Ezviz, etc.) o demo
- Conexión a internet (para API Open-Meteo)
- Docker (opcional)

## Instalación

```bash
git clone https://github.com/drbash/cctv-video-hud.git
cd cctv-video-hud
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python app.py
```

Abrir: [http://127.0.0.1:5000](http://127.0.0.1:5000)

## Uso

### Cámara real RTSP

```env
CAMERA_SOURCE=rtsp://usuario:password@192.168.1.50:554/Streaming/Channels/101
```

Para Hikvision: main stream = `/101`, sub stream = `/102`

### Modo demo sin cámara

```bash
./scripts/run_demo.sh
```

O en `.env`: `CAMERA_SOURCE=demo`

### Probar RTSP antes de levantar la web

```bash
python tools/test_rtsp.py --url "rtsp://usuario:password@IP:554/..." --seconds 10 --save test.jpg
```

### HUD web vs HUD quemado

- HUD web: [http://127.0.0.1:5000/video_feed](http://127.0.0.1:5000/video_feed)
- HUD quemado: [http://127.0.0.1:5000/video_feed?burn=true](http://127.0.0.1:5000/video_feed?burn=true)

## API

| Ruta | Descripción |
|---|---|
| `/api/health` | Healthcheck |
| `/api/stats` | Métricas + clima (JSON) |
| `/api/stats?lat=X&lon=Y` | Clima en coordenadas personalizadas |
| `/video_feed` | Stream MJPEG |
| `/video_feed?burn=true` | Stream con HUD quemado |

## Tests

```bash
pip install pytest
pytest tests/ -v
```

## Configuración

Variables de entorno (ver `.env.example`):

| Variable | Default | Descripción |
|---|---|---|
| `CAMERA_SOURCE` | `demo` | URL RTSP o `demo` |
| `STATION_NAME` | `ESTACIÓN VALLENAR` | Nombre de estación |
| `STATION_LAT` | `-28.5700` | Latitud para clima |
| `STATION_LON` | `-70.7600` | Longitud para clima |
| `APP_TZ` | `America/Santiago` | Zona horaria |
| `OPENCV_FFMPEG_CAPTURE_OPTIONS` | — | Opciones RTSP TCP |
| `JPEG_QUALITY` | `85` | Calidad JPEG (0-100) |
| `BURN_HUD_IN_FRAME` | `false` | HUD quemado por defecto |

## CI/CD

GitHub Actions ejecuta lint (Ruff) y tests (pytest) en cada push/PR.

## Docker

```bash
cp .env.example .env
docker compose up --build
```

## Troubleshooting RTSP

```bash
# Verificar puerto 554
nc -vz 192.168.1.50 554

# Probar con ffplay
ffplay -rtsp_transport tcp "rtsp://usuario:password@IP:554/..."

# Si hay cortes, usar substream 102 y bajar JPEG_QUALITY a 70
```

## Limitaciones / Roadmap

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

MIT
