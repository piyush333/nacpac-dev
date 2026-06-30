"""
Generates OpenPose-format hand skeleton images for a cradling/holding pose.

The hands are positioned to cradle the product from below — two hands
meeting at the bottom of the product with palms facing up and fingers
gently curled inward.
"""
import numpy as np
import cv2
from typing import Tuple, List


# MediaPipe / OpenPose 21-keypoint hand order:
#  0: wrist
#  1-4: thumb  (CMC → MCP → IP → TIP)
#  5-8: index  (MCP → PIP → DIP → TIP)
#  9-12: middle (MCP → PIP → DIP → TIP)
# 13-16: ring  (MCP → PIP → DIP → TIP)
# 17-20: pinky (MCP → PIP → DIP → TIP)

HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),       # thumb
    (0, 5), (5, 6), (6, 7), (7, 8),       # index
    (0, 9), (9, 10), (10, 11), (11, 12),  # middle
    (0, 13), (13, 14), (14, 15), (15, 16),# ring
    (0, 17), (17, 18), (18, 19), (19, 20),# pinky
    (5, 9), (9, 13), (13, 17),            # palm
]

# Distinct colors per finger for OpenPose visualization
FINGER_COLORS = [
    (255, 0, 0),    # thumb - red
    (255, 128, 0),  # index - orange
    (255, 255, 0),  # middle - yellow
    (0, 255, 0),    # ring - green
    (0, 128, 255),  # pinky - blue
]

PALM_COLOR = (255, 255, 255)


def _make_cradle_keypoints(
    wrist_x: float, wrist_y: float,
    hand_scale: float,
    is_right: bool,
    curl: float = 0.4
) -> np.ndarray:
    """
    Build 21 (x, y) keypoints for one hand in a palm-up cradling pose.

    Args:
        wrist_x, wrist_y: wrist anchor in image coordinates
        hand_scale: pixel length of an average finger
        is_right: True for right hand, False for left
        curl: how much fingers curl inward (0=flat, 1=fully curled)

    Returns:
        pts: (21, 2) float array of keypoints
    """
    s = hand_scale
    flip = 1 if is_right else -1  # mirror for left hand

    # palm-up: fingers point upward, slightly inward
    # Relative offsets from wrist (normalized to hand_scale)
    # Format: (dx, dy) — dy negative = up in image coords
    raw = [
        # wrist (0)
        (0.0, 0.0),
        # thumb (1-4): goes outward
        (flip * 0.35, -0.10),
        (flip * 0.60, -0.25),
        (flip * 0.75, -0.40),
        (flip * 0.85, -0.52),
        # index (5-8)
        (flip * 0.20, -0.55),
        (flip * 0.22, -0.80),
        (flip * 0.23, -1.00 + curl * 0.30),
        (flip * 0.23, -1.15 + curl * 0.55),
        # middle (9-12)
        (flip * 0.05, -0.60),
        (flip * 0.05, -0.87),
        (flip * 0.04, -1.08 + curl * 0.30),
        (flip * 0.04, -1.25 + curl * 0.55),
        # ring (13-16)
        (-flip * 0.12, -0.57),
        (-flip * 0.13, -0.82),
        (-flip * 0.14, -1.02 + curl * 0.30),
        (-flip * 0.14, -1.18 + curl * 0.55),
        # pinky (17-20)
        (-flip * 0.27, -0.50),
        (-flip * 0.30, -0.70),
        (-flip * 0.32, -0.88 + curl * 0.30),
        (-flip * 0.33, -1.02 + curl * 0.55),
    ]

    pts = np.array([[wrist_x + dx * s, wrist_y + dy * s] for dx, dy in raw], dtype=np.float32)
    return pts


def generate_cradle_pose(
    image_shape: Tuple[int, int],
    product_bbox: Tuple[int, int, int, int],
    hand_scale_factor: float = 0.18,
    skin_tone: str = "medium",
    curl: float = 0.35,
) -> np.ndarray:
    """
    Generate an OpenPose-style visualization with two hands cradling a product.

    Args:
        image_shape: (H, W)
        product_bbox: (x1, y1, x2, y2)
        hand_scale_factor: hand size relative to product width
        skin_tone: unused here (controls SD prompt, not skeleton)
        curl: finger curl amount (0=flat, 1=fully closed fist)

    Returns:
        pose_img: (H, W, 3) uint8 RGB image with skeleton drawn on black background
    """
    H, W = image_shape[:2]
    x1, y1, x2, y2 = product_bbox

    prod_w = x2 - x1
    prod_h = y2 - y1
    prod_cx = (x1 + x2) / 2
    prod_cy = (y1 + y2) / 2

    hand_scale = prod_w * hand_scale_factor * 5  # pixel length of average finger

    # Wrist positions: hands come from below the product
    # Right hand: wrist slightly right of center, below product
    # Left hand: wrist slightly left of center, below product
    wrist_y = y2 + hand_scale * 0.15

    wrist_r_x = prod_cx + prod_w * 0.18
    wrist_l_x = prod_cx - prod_w * 0.18

    pts_right = _make_cradle_keypoints(wrist_r_x, wrist_y, hand_scale, is_right=True, curl=curl)
    pts_left  = _make_cradle_keypoints(wrist_l_x, wrist_y, hand_scale, is_right=False, curl=curl)

    pose_img = np.zeros((H, W, 3), dtype=np.uint8)

    for pts, is_right in [(pts_right, True), (pts_left, False)]:
        _draw_hand_skeleton(pose_img, pts)

    return pose_img


def _draw_hand_skeleton(canvas: np.ndarray, pts: np.ndarray, thickness: int = 3):
    """Draw a single hand skeleton on canvas."""
    H, W = canvas.shape[:2]

    def clamp(p):
        return (int(np.clip(p[0], 0, W - 1)), int(np.clip(p[1], 0, H - 1)))

    # Draw connections
    finger_ranges = [(1, 4), (5, 8), (9, 12), (13, 16), (17, 20)]

    for conn in HAND_CONNECTIONS:
        i, j = conn
        # Determine color by which finger
        color = PALM_COLOR
        for fi, (start, end) in enumerate(finger_ranges):
            if start <= i <= end or start <= j <= end:
                color = FINGER_COLORS[fi]
                break
        p1 = clamp(pts[i])
        p2 = clamp(pts[j])
        cv2.line(canvas, p1, p2, color, thickness, cv2.LINE_AA)

    # Draw keypoint dots
    for i, pt in enumerate(pts):
        cv2.circle(canvas, clamp(pt), thickness + 1, (255, 255, 255), -1, cv2.LINE_AA)


def create_inpaint_mask(
    image_shape: Tuple[int, int],
    product_bbox: Tuple[int, int, int, int],
    pose_pts_right: np.ndarray,
    pose_pts_left: np.ndarray,
    expand_px: int = 25,
) -> np.ndarray:
    """
    Build the inpainting mask: white (255) = region to fill with AI hands.

    Covers the area below the product where hands will appear.

    Returns:
        mask: (H, W) uint8 — 255 in the hand region, 0 elsewhere
    """
    H, W = image_shape[:2]
    x1, y1, x2, y2 = product_bbox
    mask = np.zeros((H, W), dtype=np.uint8)

    # Convex hull of all hand keypoints → fill that region
    all_pts = np.vstack([pose_pts_right, pose_pts_left])
    all_pts = np.clip(all_pts, [0, 0], [W - 1, H - 1]).astype(np.int32)

    hull = cv2.convexHull(all_pts)
    cv2.fillConvexPoly(mask, hull, 255)

    # Also include a band just below the product bottom to blend seamlessly
    band_y1 = max(0, y2 - 10)
    band_y2 = min(H, y2 + expand_px)
    mask[band_y1:band_y2, max(0, x1 - expand_px):min(W, x2 + expand_px)] = 255

    # Dilate for smoother edges
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (expand_px, expand_px))
    mask = cv2.dilate(mask, kernel)

    # Never paint over the product itself
    mask[y1:y2, x1:x2] = 0

    return mask


def get_pose_keypoints(
    image_shape: Tuple[int, int],
    product_bbox: Tuple[int, int, int, int],
    hand_scale_factor: float = 0.18,
    curl: float = 0.35,
) -> Tuple[np.ndarray, np.ndarray]:
    """Return (right_pts, left_pts) keypoints for use in mask creation."""
    H, W = image_shape[:2]
    x1, y1, x2, y2 = product_bbox
    prod_w = x2 - x1
    prod_cx = (x1 + x2) / 2
    hand_scale = prod_w * hand_scale_factor * 5
    wrist_y = y2 + hand_scale * 0.15
    wrist_r_x = prod_cx + prod_w * 0.18
    wrist_l_x = prod_cx - prod_w * 0.18

    pts_right = _make_cradle_keypoints(wrist_r_x, wrist_y, hand_scale, is_right=True, curl=curl)
    pts_left  = _make_cradle_keypoints(wrist_l_x, wrist_y, hand_scale, is_right=False, curl=curl)
    return pts_right, pts_left
