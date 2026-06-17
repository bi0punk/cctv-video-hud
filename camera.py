import math
import os
import threading
import time
from typing import Optional, Union

import cv2
import numpy as np

from config import settings


class CameraStream:
    def __init__(self, source: str):
        self.raw_source = str(source)
        self.demo_mode = self.raw_source.lower() == "demo"
        self.source: Union[int, str] = int(source) if str(source).isdigit() else source
        self.cap = None
        self.frame: Optional[np.ndarray] = None
        self.lock = threading.Lock()
        self.running = False
        self.fps_estimated = 0.0
        self.last_error = None
        self.last_frame_ts = 0.0

    def start(self):
        self.running = True
        thread = threading.Thread(target=self._reader, daemon=True)
        thread.start()

    def _open(self):
        if self.demo_mode:
            return None
        ffmpeg_opts = os.getenv("OPENCV_FFMPEG_CAPTURE_OPTIONS")
        if ffmpeg_opts:
            try:
                cap = cv2.VideoCapture(self.source, cv2.CAP_FFMPEG)
                cap.set(cv2.CAP_PROP_OPENCV_FFMPEG_CAPTURE_OPTIONS, ffmpeg_opts)
            except Exception:
                pass
        else:
            cap = cv2.VideoCapture(self.source, cv2.CAP_FFMPEG)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, settings.frame_width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, settings.frame_height)
        try:
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 2)
        except Exception:
            pass
        return cap

    def _reader(self):
        if not self.demo_mode:
            self.cap = self._open()
        last_t = time.time()
        frames = 0
        while self.running:
            if self.demo_mode:
                frame = self._demo_frame()
                time.sleep(settings.frame_sleep_ms / 1000)
            else:
                if self.cap is None or not self.cap.isOpened():
                    self.last_error = "Cámara no disponible o RTSP no conecta. Reintentando."
                    time.sleep(1)
                    self.cap = self._open()
                    continue
                ok, frame = self.cap.read()
                if not ok or frame is None:
                    self.last_error = "No se pudo leer frame RTSP. Reabriendo cámara."
                    try:
                        self.cap.release()
                    except Exception:
                        pass
                    self.cap = None
                    time.sleep(1)
                    continue
            frames += 1
            now = time.time()
            self.last_frame_ts = now
            if now - last_t >= 1.0:
                self.fps_estimated = frames / (now - last_t)
                frames = 0
                last_t = now
            with self.lock:
                self.frame = frame

    def _demo_frame(self) -> np.ndarray:
        w = settings.frame_width
        h = settings.frame_height
        t = time.time()
        frame = np.zeros((h, w, 3), dtype=np.uint8)
        frame[:] = (10, 16, 24)
        for x in range(0, w, 64):
            cv2.line(frame, (x, 0), (x, h), (24, 42, 58), 1)
        for y in range(0, h, 64):
            cv2.line(frame, (0, y), (w, y), (24, 42, 58), 1)
        cx = int(w / 2 + math.sin(t / 2) * 170)
        cy = int(h / 2 + math.cos(t / 2.7) * 80)
        cv2.circle(frame, (cx, cy), 90, (40, 120, 160), -1)
        cv2.circle(frame, (cx, cy), 94, (0, 220, 255), 2)
        cv2.putText(frame, "DEMO VIDEO SOURCE", (int(w * 0.36), int(h * 0.50)), cv2.FONT_HERSHEY_SIMPLEX, 1.1, (230, 250, 255), 2, cv2.LINE_AA)
        cv2.putText(frame, "Edit .env CAMERA_SOURCE=rtsp://user:pass@ip:554/...", (int(w * 0.25), int(h * 0.56)), cv2.FONT_HERSHEY_SIMPLEX, 0.72, (80, 220, 255), 2, cv2.LINE_AA)
        return frame

    def get_frame(self) -> Optional[np.ndarray]:
        with self.lock:
            if self.frame is None:
                return None
            return self.frame.copy()

    def get_jpeg(self, frame: Optional[np.ndarray] = None) -> Optional[bytes]:
        if frame is None:
            frame = self.get_frame()
        if frame is None:
            return None
        ok, buffer = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), settings.jpeg_quality])
        if not ok:
            return None
        return buffer.tobytes()

    def health(self) -> dict:
        age = time.time() - self.last_frame_ts if self.last_frame_ts else None
        return {
            "source": self.raw_source,
            "demo_mode": self.demo_mode,
            "fps": round(self.fps_estimated, 2),
            "last_error": self.last_error,
            "last_frame_age_seconds": round(age, 2) if age is not None else None,
            "has_frame": self.frame is not None,
        }

    def stop(self):
        self.running = False
        if self.cap is not None:
            try:
                self.cap.release()
            except Exception:
                pass
