"""
Download all required models before first run.
Run once: python setup_models.py

Downloads:
  - SAM (vit_h) checkpoint (~2.4 GB)
  - SD inpainting + ControlNet (~4 GB, cached by diffusers)

Total: ~6-7 GB
"""
import os
import urllib.request
from pathlib import Path


MODELS_DIR = Path("./models")
MODELS_DIR.mkdir(exist_ok=True)


SAM_MODELS = {
    "vit_h": {
        "filename": "sam_vit_h_4b8939.pth",
        "url": "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth",
        "size_gb": 2.4,
    },
    "vit_b": {
        "filename": "sam_vit_b_01ec64.pth",
        "url": "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth",
        "size_gb": 0.37,
    },
}


def download_sam(model_type: str = "vit_b"):
    """Download SAM checkpoint. vit_b is faster (375MB), vit_h is best quality (2.4GB)."""
    info = SAM_MODELS[model_type]
    dest = MODELS_DIR / info["filename"]

    if dest.exists():
        print(f"[SAM] {dest.name} already downloaded.")
        return str(dest)

    print(f"[SAM] Downloading {dest.name} ({info['size_gb']} GB)...")
    urllib.request.urlretrieve(info["url"], dest, reporthook=_progress_hook)
    print(f"\n[SAM] Saved to {dest}")
    return str(dest)


def download_diffusion_models(cache_dir: str = "./models"):
    """Pre-download SD + ControlNet via diffusers (handles caching automatically)."""
    import torch
    from diffusers import ControlNetModel, StableDiffusionControlNetInpaintPipeline

    dtype = torch.float16 if torch.cuda.is_available() else torch.float32

    print("[Diffusers] Downloading ControlNet (lllyasviel/control_v11p_sd15_openpose)...")
    ControlNetModel.from_pretrained(
        "lllyasviel/control_v11p_sd15_openpose",
        torch_dtype=dtype,
        cache_dir=cache_dir,
    )

    print("[Diffusers] Downloading SD inpainting (runwayml/stable-diffusion-inpainting)...")
    StableDiffusionControlNetInpaintPipeline.from_pretrained(
        "runwayml/stable-diffusion-inpainting",
        torch_dtype=dtype,
        cache_dir=cache_dir,
    )

    print("[Diffusers] All diffusion models cached.")


def _progress_hook(block_num, block_size, total_size):
    downloaded = block_num * block_size
    pct = min(downloaded / total_size * 100, 100)
    mb = downloaded / 1e6
    total_mb = total_size / 1e6
    print(f"\r  {pct:.1f}%  {mb:.0f}/{total_mb:.0f} MB", end="", flush=True)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Download models for HandVid")
    parser.add_argument(
        "--sam", choices=["vit_b", "vit_h"], default="vit_b",
        help="SAM model size: vit_b (375MB, fast) or vit_h (2.4GB, best quality)"
    )
    parser.add_argument(
        "--skip-diffusion", action="store_true",
        help="Skip downloading diffusion models (they download on first use)"
    )
    args = parser.parse_args()

    sam_path = download_sam(args.sam)

    if not args.skip_diffusion:
        download_diffusion_models()

    print("\n✓ All models ready. Run: python app.py")
    print(f"  SAM checkpoint: {sam_path}")
