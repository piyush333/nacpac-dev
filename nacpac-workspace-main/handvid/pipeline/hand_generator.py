"""
AI hand generation using Stable Diffusion Inpainting + ControlNet (OpenPose).

Takes:
  - original frame (RGB PIL Image)
  - inpaint mask (PIL Image, white = fill)
  - pose image (RGB PIL Image with OpenPose skeleton)

Returns:
  - composite frame (RGB PIL Image) with natural AI hands
"""
import torch
import numpy as np
from PIL import Image
from typing import Optional


_pipe = None
_device = None


def load_pipeline(model_cache_dir: str = "./models"):
    """
    Load SD inpainting + ControlNet pipeline.
    Call once at startup — takes ~30s on first run (downloads ~6GB).
    """
    global _pipe, _device

    from diffusers import (
        StableDiffusionControlNetInpaintPipeline,
        ControlNetModel,
        UniPCMultistepScheduler,
    )

    _device = "cuda" if torch.cuda.is_available() else "cpu"
    dtype = torch.float16 if _device == "cuda" else torch.float32

    print(f"[hand_generator] Loading ControlNet on {_device}...")
    controlnet = ControlNetModel.from_pretrained(
        "lllyasviel/control_v11p_sd15_openpose",
        torch_dtype=dtype,
        cache_dir=model_cache_dir,
    )

    print("[hand_generator] Loading SD inpainting pipeline...")
    _pipe = StableDiffusionControlNetInpaintPipeline.from_pretrained(
        "runwayml/stable-diffusion-inpainting",
        controlnet=controlnet,
        torch_dtype=dtype,
        cache_dir=model_cache_dir,
    )
    _pipe.scheduler = UniPCMultistepScheduler.from_config(_pipe.scheduler.config)
    _pipe = _pipe.to(_device)

    # Memory optimizations
    if _device == "cuda":
        _pipe.enable_xformers_memory_efficient_attention()

    print("[hand_generator] Pipeline ready.")
    return _pipe


def generate_hands(
    frame_rgb: np.ndarray,
    mask: np.ndarray,
    pose_img: np.ndarray,
    skin_tone: str = "medium",
    num_inference_steps: int = 25,
    guidance_scale: float = 7.5,
    controlnet_conditioning_scale: float = 0.9,
    seed: Optional[int] = 42,
) -> np.ndarray:
    """
    Generate natural AI hands via SD inpainting + ControlNet.

    Args:
        frame_rgb: (H, W, 3) uint8 original frame
        mask: (H, W) uint8 — 255 where hands should appear
        pose_img: (H, W, 3) uint8 OpenPose skeleton
        skin_tone: "light" | "medium" | "dark" — adjusts prompt
        num_inference_steps: SD denoising steps (20-30 is a good balance)
        guidance_scale: prompt adherence (7-9 works well)
        controlnet_conditioning_scale: how closely to follow pose (0.8-1.0)
        seed: for reproducibility across frames

    Returns:
        result: (H, W, 3) uint8 composite with hands
    """
    if _pipe is None:
        raise RuntimeError("Pipeline not loaded. Call load_pipeline() first.")

    skin_descriptions = {
        "light": "fair skin, light complexion",
        "medium": "medium skin tone, natural complexion",
        "dark": "dark skin, deep complexion",
    }
    skin_desc = skin_descriptions.get(skin_tone, "natural skin tone")

    prompt = (
        f"photorealistic human hands gently cradling and holding a product, "
        f"{skin_desc}, well-manicured, studio lighting, sharp focus, "
        f"natural pose, 8k, high detail"
    )
    negative_prompt = (
        "extra fingers, missing fingers, deformed hands, mutated, bad anatomy, "
        "cartoon, anime, painting, blurry, low quality, watermark, text, "
        "gloves, robot, CGI, 3d render, plastic"
    )

    h, w = frame_rgb.shape[:2]

    # Convert to PIL
    pil_image = Image.fromarray(frame_rgb).convert("RGB")
    pil_mask = Image.fromarray(mask).convert("L")
    pil_pose = Image.fromarray(pose_img).convert("RGB")

    # SD works best at 512x512 or 768x768 — resize if needed
    target_size = _get_target_size(w, h)
    pil_image_r = pil_image.resize(target_size, Image.LANCZOS)
    pil_mask_r  = pil_mask.resize(target_size, Image.NEAREST)
    pil_pose_r  = pil_pose.resize(target_size, Image.LANCZOS)

    generator = torch.Generator(device=_device).manual_seed(seed) if seed is not None else None

    with torch.autocast(_device):
        result = _pipe(
            prompt=prompt,
            negative_prompt=negative_prompt,
            image=pil_image_r,
            mask_image=pil_mask_r,
            control_image=pil_pose_r,
            num_inference_steps=num_inference_steps,
            guidance_scale=guidance_scale,
            controlnet_conditioning_scale=controlnet_conditioning_scale,
            generator=generator,
        ).images[0]

    # Resize back to original resolution
    if result.size != (w, h):
        result = result.resize((w, h), Image.LANCZOS)

    # Composite: only replace the masked region in the original
    result_np = np.array(result)
    mask_3ch = np.stack([mask, mask, mask], axis=-1).astype(np.float32) / 255.0

    # Soft blend at mask edges for natural look
    from scipy.ndimage import gaussian_filter
    mask_soft = gaussian_filter(mask.astype(np.float32), sigma=3) / 255.0
    mask_soft_3ch = np.stack([mask_soft, mask_soft, mask_soft], axis=-1)

    composite = (result_np * mask_soft_3ch + frame_rgb * (1 - mask_soft_3ch)).astype(np.uint8)
    return composite


def _get_target_size(w: int, h: int) -> tuple:
    """Return SD-friendly (width, height) — multiple of 8, max 768."""
    max_dim = 768
    scale = min(max_dim / max(w, h), 1.0)
    tw = ((int(w * scale)) // 8) * 8
    th = ((int(h * scale)) // 8) * 8
    return (max(tw, 8), max(th, 8))
