import cv2
import numpy as np


def draw_panel(frame, x, y, w, h, alpha=0.56):
    overlay = frame.copy()
    cv2.rectangle(overlay, (x, y), (x + w, y + h), (8, 22, 36), -1)
    cv2.rectangle(overlay, (x, y), (x + w, y + h), (0, 220, 255), 1)
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
    return frame


def put(frame, text, x, y, scale=0.55, color=(235, 250, 255), thickness=1):
    cv2.putText(frame, str(text), (x, y), cv2.FONT_HERSHEY_SIMPLEX, scale, color, thickness, cv2.LINE_AA)


def burn_hud(frame: np.ndarray, stats: dict) -> np.ndarray:
    h, w = frame.shape[:2]
    out = frame.copy()
    cyan = (0, 230, 255)
    white = (235, 250, 255)
    green = (70, 255, 110)
    orange = (50, 200, 255)
    blue = (255, 168, 42)

    cv2.rectangle(out, (18, 18), (w - 18, h - 18), cyan, 2)
    cv2.line(out, (18, 72), (w - 18, 72), cyan, 1)
    cv2.line(out, (18, h - 92), (w - 18, h - 92), cyan, 1)

    draw_panel(out, 32, 28, 380, 34)
    put(out, "TRANSMISION EN VIVO", 46, 52, 0.65, white, 2)
    draw_panel(out, int(w / 2 - 180), 28, 360, 34)
    put(out, stats.get("location", "ESTACION"), int(w / 2 - 145), 52, 0.65, cyan, 2)
    draw_panel(out, w - 300, 28, 250, 34)
    put(out, stats.get("status", "EN LINEA"), w - 282, 52, 0.65, green, 2)

    left_x = 32
    rows = [
        ("FECHA", stats.get("date", "--")),
        ("HORA", stats.get("time", "--")),
        ("HUMEDAD", f'{stats.get("humidity", "--")} %'),
        ("TEMP", f'{stats.get("temperature", "--")} C'),
        ("SENS TERM", f'{stats.get("apparent_temperature", "--")} C'),
        ("PRESION", f'{stats.get("pressure", "--")} hPa'),
    ]
    for i, (label, value) in enumerate(rows):
        y = 92 + i * 52
        draw_panel(out, left_x, y, 255, 44)
        put(out, label, left_x + 14, y + 16, 0.42, cyan, 1)
        put(out, value, left_x + 14, y + 37, 0.62, white, 2)

    right_x = w - 287
    rows_r = [
        ("SENAL", f'{stats.get("signal", "--")} %'),
        ("FPS", stats.get("fps", "--")),
        ("VIENTO", stats.get("wind", "--")),
        ("AIRE", stats.get("air_quality", "--")),
        ("AQI", stats.get("us_aqi", "--")),
        ("UV", stats.get("uv_index", "--")),
    ]
    for i, (label, value) in enumerate(rows_r):
        y = 92 + i * 52
        draw_panel(out, right_x, y, 255, 44)
        put(out, label, right_x + 14, y + 16, 0.42, cyan, 1)
        put(out, value, right_x + 14, y + 37, 0.62, white, 2)

    draw_panel(out, 32, h - 78, 360, 48)
    put(out, f'CLIMA: {stats.get("weather", "--")}', 48, h - 50, 0.52, white, 2)
    draw_panel(out, 420, h - 78, 200, 48)
    put(out, f'NUBES: {stats.get("cloud_cover", "--")}%', 435, h - 50, 0.52, cyan, 2)
    draw_panel(out, 645, h - 78, 240, 48)
    put(out, f'PRECIP: {stats.get("precipitation", "--")}mm', 660, h - 50, 0.52, white, 2)
    draw_panel(out, w - 410, h - 78, 370, 48)
    put(out, f'MODO: {stats.get("telemetry_mode", "--")}', w - 394, h - 50, 0.52, cyan, 2)

    return out
