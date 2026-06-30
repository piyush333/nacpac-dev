"""
Product segmentation using Segment Anything Model (SAM).
Detects the main product in the frame and returns its mask + bounding box.
"""
import numpy as np
import cv2
import torch
from PIL import Image
from typing import Tuple, Optional


_sam_predictor = None


def load_sam(checkpoint_path: str, model_type: str = "vit_h"):
    """Load SAM predictor (call once at startup)."""
    global _sam_predictor
    from segment_anything import sam_model_registry, SamPredictor

    sam = sam_model_registry[model_type](checkpoint=checkpoint_path)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    sam.to(device=device)
    _sam_predictor = SamPredictor(sam)
    return _sam_predictor


def segment_product(
    frame_bgr: np.ndarray,
    point: Optional[Tuple[int, int]] = None,
    use_center: bool = True
) -> Tuple[np.ndarray, Tuple[int, int, int, int]]:
    """
    Segment the product in the frame.

    Args:
        frame_bgr: BGR image from OpenCV
        point: (x, y) click point to seed SAM. If None, uses image center.
        use_center: if True, seeds SAM at center of image

    Returns:
        mask: binary mask (H, W) uint8 — 255 where product is
        bbox: (x1, y1, x2, y2) bounding box of the product
    """
    if _sam_predictor is None:
        raise RuntimeError("SAM not loaded. Call load_sam() first.")

    frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
    _sam_predictor.set_image(frame_rgb)

    h, w = frame_bgr.shape[:2]

    if point is None and use_center:
        point = (w // 2, h // 2)

    input_point = np.array([[point[0], point[1]]])
    input_label = np.array([1])  # 1 = foreground

    masks, scores, _ = _sam_predictor.predict(
        point_coords=input_point,
        point_labels=input_label,
        multimask_output=True,
    )

    # Pick highest-confidence mask
    best_idx = np.argmax(scores)
    mask = (masks[best_idx] * 255).astype(np.uint8)

    # Bounding box from mask
    coords = cv2.findNonZero(mask)
    x, y, mw, mh = cv2.boundingRect(coords)
    bbox = (x, y, x + mw, y + mh)

    return mask, bbox


def fallback_bbox(frame_bgr: np.ndarray, margin: float = 0.15) -> Tuple[int, int, int, int]:
    """
    Fallback: assume product occupies the center portion of the frame.
    Used if SAM is not available or fails.
    """
    h, w = frame_bgr.shape[:2]
    x1 = int(w * margin)
    y1 = int(h * margin)
    x2 = int(w * (1 - margin))
    y2 = int(h * (1 - margin))
    return (x1, y1, x2, y2)


def get_product_bbox(frame_bgr: np.ndarray, sam_point: Optional[Tuple[int, int]] = None) -> Tuple[int, int, int, int]:
    """
    Get product bounding box, falling back gracefully if SAM unavailable.
    """
    try:
        if _sam_predictor is not None:
            _, bbox = segment_product(frame_bgr, point=sam_point)
            return bbox
    except Exception as e:
        print(f"[segmenter] SAM failed: {e}, using fallback bbox")

    return fallback_bbox(frame_bgr)
