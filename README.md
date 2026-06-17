# OpenCV Sci-Tech HUD RTSP + Open-Meteo

Proyecto completo para mostrar una transmisión de cámara real RTSP con un marco sci-tech y datos meteorológicos por coordenadas.

## 1. Instalación rápida

```bash
unzip opencv_sci_tech_hud_rtsp_openmeteo_20260614_0227.zip
cd opencv_sci_tech_hud_rtsp_openmeteo_20260614_0227

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
python app.py
```

Abrir:

```text
http://127.0.0.1:5000
```

## 2. Cámara real RTSP en .env

El archivo `.env.example` ya viene preparado para RTSP:

```env
CAMERA_SOURCE=rtsp://usuario:password@192.168.1.50:554/Streaming/Channels/101
```

Solo cambia usuario, password e IP.

Para Hikvision/Ezviz:

```text
Main stream: rtsp://usuario:password@IP:554/Streaming/Channels/101
Sub stream:  rtsp://usuario:password@IP:554/Streaming/Channels/102
```

Para dashboard web, normalmente conviene usar el substream:

```env
CAMERA_SOURCE=rtsp://usuario:password@192.168.1.50:554/Streaming/Channels/102
```

## 3. RTSP estable por TCP

En `.env` queda incluido:

```env
OPENCV_FFMPEG_CAPTURE_OPTIONS=rtsp_transport;tcp|stimeout;5000000|max_delay;500000
```

## 4. Probar RTSP antes de levantar la web

```bash
source .venv/bin/activate
python tools/test_rtsp.py \
  --url "rtsp://usuario:password@192.168.1.50:554/Streaming/Channels/101" \
  --seconds 10 \
  --save rtsp_test_frame.jpg
```

## 5. Modo demo sin cámara

```bash
./scripts/run_demo.sh
```

O en `.env`:

```env
CAMERA_SOURCE=demo
```

## 6. Coordenadas para clima

```env
STATION_NAME=ESTACIÓN VALLENAR
STATION_LAT=-28.5700
STATION_LON=-70.7600
APP_TZ=America/Santiago
```

## 7. Endpoints

```bash
curl "http://127.0.0.1:5000/api/health"
curl "http://127.0.0.1:5000/api/stats"
curl "http://127.0.0.1:5000/api/stats?lat=-28.5700&lon=-70.7600"
```

## 8. HUD web vs HUD quemado

HUD web recomendado:

```text
http://127.0.0.1:5000/video_feed
```

HUD dibujado dentro del frame con OpenCV:

```text
http://127.0.0.1:5000/video_feed?burn=true
```

## 9. Docker

```bash
cp .env.example .env
docker compose up --build
```

## 10. Troubleshooting RTSP

Verificar puerto 554:

```bash
nc -vz 192.168.1.50 554
```

Probar con ffplay:

```bash
ffplay -rtsp_transport tcp "rtsp://usuario:password@192.168.1.50:554/Streaming/Channels/101"
```

Si hay cortes, usa substream 102 y baja JPEG_QUALITY a 70.
