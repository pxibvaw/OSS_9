"""
⚠️ 과제 제출용 - 실제 실행은 막아 둔 CCTV 인입 스크립트
-----------------------------------------------------------------
이 파일은 **RTSP(또는 HTTP) CCTV 스트림**에서 프레임을 주기적으로 캡처해
`realheatmap/images/` 폴더에 JPG로 저장하고, 기존 객체 탐지 루프가
새 이미지를 소비하도록 하는 예시 코드입니다.
"""

from __future__ import annotations

import os
import cv2  # type: ignore
import time
from pathlib import Path
from datetime import datetime
from itertools import cycle

from tqdm import tqdm  # progress bar

# 설정값
PROJECT_ROOT = Path(__file__).resolve().parent.parent  # OSS_9-main
IMG_DIR = PROJECT_ROOT / "realheatmap" / "images"
IMG_DIR.mkdir(parents=True, exist_ok=True)

# 예시 RTSP/HTTP 스트림 URL 리스트 (가짜 주소)
RTSP_URLS = [
    "rtsp://username:password@192.168.1.101/stream1",
    "rtsp://username:password@192.168.1.102/stream1",
]

# 프레임 캡처 간격(초) & 저장 해상도
CAPTURE_INTERVAL = 5
SAVE_WIDTH = 1280
SAVE_HEIGHT = 720


def grab_frame(rtsp_url: str) -> tuple[bool, "numpy.ndarray | None"]:  # noqa: F821
    """RTSP 스트림에서 한 프레임을 읽어 반환."""
    cap = cv2.VideoCapture(rtsp_url)
    if not cap.isOpened():
        print(f"[❌ 연결 실패] {rtsp_url}")
        return False, None

    success, frame = cap.read()
    cap.release()
    if not success:
        print(f"[⚠️ 프레임 읽기 실패] {rtsp_url}")
        return False, None

    frame = cv2.resize(frame, (SAVE_WIDTH, SAVE_HEIGHT))
    return True, frame


def save_frame(frame, cam_name: str) -> Path:  # type: ignore
    """이미지 파일 저장 및 경로 반환."""
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    file_path = IMG_DIR / f"frame_{ts}_{cam_name}.jpg"
    cv2.imwrite(str(file_path), frame)
    return file_path


# 주기적 캡처 루프

def capture_loop():
    print("[▶️ CCTV 캡처 시작] Ctrl+C 로 중단")
    cam_cycle = cycle(enumerate(RTSP_URLS, start=1))

    try:
        for cam_idx, url in tqdm(cam_cycle, unit="frame"):
            ok, frame = grab_frame(url)
            if ok and frame is not None:
                save_path = save_frame(frame, f"cam{cam_idx}")
                print(f"[💾 저장] {save_path.relative_to(PROJECT_ROOT)}")
            time.sleep(CAPTURE_INTERVAL)
    except KeyboardInterrupt:
        print("\n[🛑 중단] capture_loop() 종료")


# 자동 실행 방지를 위해 전체 주석 처리
"""
if __name__ == "__main__":
    capture_loop()
"""

