"""
Video → frames → video conversion using OpenCV + FFmpeg.
"""
import os
import cv2
import subprocess
import numpy as np
from pathlib import Path
from typing import List, Tuple


def extract_frames(video_path: str, output_dir: str, every_n: int = 1) -> Tuple[List[str], float, Tuple[int, int]]:
    """
    Extract frames from a video file.

    Returns:
        frame_paths: sorted list of saved frame file paths
        fps: original video fps
        size: (width, height)
    """
    os.makedirs(output_dir, exist_ok=True)
    cap = cv2.VideoCapture(video_path)

    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    frame_paths = []
    idx = 0
    saved = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if idx % every_n == 0:
            path = os.path.join(output_dir, f"frame_{saved:05d}.png")
            cv2.imwrite(path, frame)
            frame_paths.append(path)
            saved += 1
        idx += 1

    cap.release()
    return sorted(frame_paths), fps / every_n, (width, height)


def compose_video(frame_dir: str, output_path: str, fps: float, audio_source: str = None) -> str:
    """
    Stitch frames back into a video, optionally copying audio from original.
    """
    frame_pattern = os.path.join(frame_dir, "frame_%05d.png")

    cmd = [
        "ffmpeg", "-y",
        "-framerate", str(fps),
        "-i", frame_pattern,
    ]

    if audio_source:
        cmd += ["-i", audio_source, "-c:a", "aac", "-shortest"]

    cmd += [
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-crf", "18",
        output_path
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        # Try without audio if audio failed
        cmd_no_audio = [
            "ffmpeg", "-y",
            "-framerate", str(fps),
            "-i", frame_pattern,
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-crf", "18",
            output_path
        ]
        subprocess.run(cmd_no_audio, check=True)

    return output_path


def resize_frame(frame: np.ndarray, max_dim: int = 768) -> Tuple[np.ndarray, float]:
    """Resize frame so longest side <= max_dim. Returns (resized, scale)."""
    h, w = frame.shape[:2]
    scale = min(max_dim / max(h, w), 1.0)
    if scale < 1.0:
        new_w = int(w * scale)
        new_h = int(h * scale)
        # SD requires dimensions divisible by 8
        new_w = (new_w // 8) * 8
        new_h = (new_h // 8) * 8
        frame = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)
    return frame, scale
