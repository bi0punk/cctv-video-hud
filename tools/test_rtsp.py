#!/usr/bin/env python3
import argparse
import os
import time
import cv2


def main():
    parser = argparse.ArgumentParser(description="Prueba una cámara RTSP con OpenCV.")
    parser.add_argument("--url", required=True, help="URL RTSP completa")
    parser.add_argument("--seconds", type=int, default=10)
    parser.add_argument("--save", default="rtsp_test_frame.jpg")
    args = parser.parse_args()
    os.environ.setdefault("OPENCV_FFMPEG_CAPTURE_OPTIONS", "rtsp_transport;tcp|stimeout;5000000|max_delay;500000")
    cap = cv2.VideoCapture(args.url, cv2.CAP_FFMPEG)
    if not cap.isOpened():
        raise SystemExit("ERROR: no se pudo abrir la cámara RTSP. Revisa URL, usuario, password, red y puerto 554.")
    start = time.time()
    frames = 0
    last_frame = None
    while time.time() - start < args.seconds:
        ok, frame = cap.read()
        if not ok or frame is None:
            print("WARN: frame no leído")
            time.sleep(0.2)
            continue
        frames += 1
        last_frame = frame
    cap.release()
    elapsed = time.time() - start
    fps = frames / elapsed if elapsed > 0 else 0
    print(f"OK: frames={frames}, seconds={elapsed:.1f}, fps_aprox={fps:.2f}")
    if last_frame is not None:
        cv2.imwrite(args.save, last_frame)
        print(f"Evidencia guardada en: {args.save}")


if __name__ == "__main__":
    main()
