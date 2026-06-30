"""
Orchestrates the full per-frame pipeline:
  extract → segment → pose → generate → composite

Also handles temporal smoothing so hands don't jump between frames.
"""
import os
import cv2
import numpy as np
from tqdm import tqdm
from typing import List, Optional, Tuple, Callable

from pipeline.segmenter import get_product_bbox
from pipeline.hand_poser import generate_cradle_pose, create_inpaint_mask, get_pose_keypoints
from pipeline.hand_generator import generate_hands
from pipeline.video_processor import extract_frames, compose_video, resize_frame


def process_video(
    input_path: str,
    output_path: str,
    temp_dir: str,
    skin_tone: str = "medium",
    hand_scale: float = 0.18,
    curl: float = 0.35,
    every_n_frames: int = 1,
    inference_steps: int = 25,
    seed: int = 42,
    progress_cb: Optional[Callable[[float, str], None]] = None,
    sam_point: Optional[Tuple[int, int]] = None,
) -> str:
    """
    Full pipeline: input video → output video with AI hands.

    Args:
        input_path: path to source video
        output_path: where to write the result
        temp_dir: scratch directory for frames
        skin_tone: "light" | "medium" | "dark"
        hand_scale: hand size relative to product width (0.1–0.3)
        curl: finger curl 0=flat 1=fist (0.3–0.5 looks natural)
        every_n_frames: process every Nth frame (1=every frame, 2=half)
        inference_steps: SD steps per frame (20-30)
        seed: fixed seed for consistency across frames
        progress_cb: callback(fraction 0-1, status_msg)
        sam_point: optional (x, y) to seed SAM product detection

    Returns:
        output_path
    """
    def _progress(frac, msg):
        if progress_cb:
            progress_cb(frac, msg)
        else:
            print(f"[{frac:.0%}] {msg}")

    _progress(0.0, "Extracting frames...")
    frames_dir = os.path.join(temp_dir, "frames_in")
    out_dir = os.path.join(temp_dir, "frames_out")
    os.makedirs(frames_dir, exist_ok=True)
    os.makedirs(out_dir, exist_ok=True)

    frame_paths, fps, (orig_w, orig_h) = extract_frames(input_path, frames_dir, every_n=every_n_frames)
    n_frames = len(frame_paths)

    if n_frames == 0:
        raise ValueError("No frames extracted from video.")

    _progress(0.05, f"Processing {n_frames} frames...")

    # Cache bbox from first frame to keep hands stable across video
    first_frame = cv2.imread(frame_paths[0])
    first_frame_small, scale = resize_frame(first_frame)
    cached_bbox = get_product_bbox(first_frame_small, sam_point)

    # Scale bbox back to full res
    cached_bbox = tuple(int(v / scale) for v in cached_bbox)

    for i, fp in enumerate(frame_paths):
        frac = 0.05 + (i / n_frames) * 0.90
        _progress(frac, f"Frame {i+1}/{n_frames} — generating hands...")

        frame_bgr = cv2.imread(fp)
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)

        h, w = frame_rgb.shape[:2]

        # Slightly re-detect bbox every 30 frames in case product moves
        if i % 30 == 0 and i > 0:
            try:
                frame_small, sc = resize_frame(frame_bgr)
                bbox = get_product_bbox(frame_small, sam_point)
                cached_bbox = tuple(int(v / sc) for v in bbox)
            except Exception:
                pass  # keep previous bbox

        bbox = cached_bbox

        # Generate pose skeleton
        pose_img = generate_cradle_pose(
            image_shape=(h, w),
            product_bbox=bbox,
            hand_scale_factor=hand_scale,
            curl=curl,
        )

        # Generate inpaint mask
        pts_r, pts_l = get_pose_keypoints((h, w), bbox, hand_scale_factor=hand_scale, curl=curl)
        mask = create_inpaint_mask((h, w), bbox, pts_r, pts_l)

        # Generate hands with SD + ControlNet
        # Use same seed per frame so hands stay consistent (vary slightly by frame idx)
        frame_seed = seed + i
        result_rgb = generate_hands(
            frame_rgb=frame_rgb,
            mask=mask,
            pose_img=pose_img,
            skin_tone=skin_tone,
            num_inference_steps=inference_steps,
            seed=frame_seed,
        )

        # Save output frame
        out_frame_bgr = cv2.cvtColor(result_rgb, cv2.COLOR_RGB2BGR)
        out_path = os.path.join(out_dir, f"frame_{i:05d}.png")
        cv2.imwrite(out_path, out_frame_bgr)

    _progress(0.95, "Composing output video...")
    compose_video(out_dir, output_path, fps=fps, audio_source=input_path)

    _progress(1.0, "Done!")
    return output_path
