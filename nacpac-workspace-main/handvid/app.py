"""
HandVid — Desktop GUI
Gradio app for adding AI-generated hands to product videos.

Run: python app.py
"""
import os
import uuid
import shutil
import threading
import gradio as gr
from pathlib import Path


TEMP_DIR = "./temp"
OUTPUT_DIR = "./outputs"
MODELS_DIR = "./models"

os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)

# Global pipeline state
_pipeline_ready = False
_sam_loaded = False


def _ensure_pipeline(sam_model: str = "vit_b"):
    global _pipeline_ready, _sam_loaded
    if not _pipeline_ready:
        from pipeline.hand_generator import load_pipeline
        load_pipeline(model_cache_dir=MODELS_DIR)
        _pipeline_ready = True

    if not _sam_loaded:
        sam_path = _find_sam_checkpoint(sam_model)
        if sam_path:
            from pipeline.segmenter import load_sam
            model_type = "vit_h" if "vit_h" in sam_path else "vit_b"
            load_sam(sam_path, model_type=model_type)
            _sam_loaded = True
        else:
            print("[app] SAM checkpoint not found — using fallback bbox detection")


def _find_sam_checkpoint(model_type: str = "vit_b") -> str:
    """Find SAM checkpoint in models dir."""
    names = {
        "vit_h": "sam_vit_h_4b8939.pth",
        "vit_b": "sam_vit_b_01ec64.pth",
    }
    target = names.get(model_type, names["vit_b"])
    path = os.path.join(MODELS_DIR, target)
    return path if os.path.exists(path) else None


def process_video_gradio(
    video_file,
    skin_tone: str,
    hand_size: float,
    finger_curl: float,
    inference_steps: int,
    sam_model: str,
    seed: int,
    progress=gr.Progress(track_tqdm=True),
):
    """Main handler called by Gradio."""
    if video_file is None:
        return None, "Please upload a video first."

    job_id = uuid.uuid4().hex[:8]
    job_temp = os.path.join(TEMP_DIR, job_id)
    os.makedirs(job_temp, exist_ok=True)

    output_path = os.path.join(OUTPUT_DIR, f"handvid_{job_id}.mp4")

    try:
        progress(0, desc="Loading AI models (first run may take a few minutes)...")
        _ensure_pipeline(sam_model)

        from pipeline.composer import process_video

        def _cb(frac, msg):
            progress(frac, desc=msg)

        process_video(
            input_path=video_file,
            output_path=output_path,
            temp_dir=job_temp,
            skin_tone=skin_tone,
            hand_scale=hand_size,
            curl=finger_curl,
            every_n_frames=1,
            inference_steps=inference_steps,
            seed=seed,
            progress_cb=_cb,
        )

        return output_path, f"Done! Saved to {output_path}"

    except Exception as e:
        import traceback
        msg = f"Error: {e}\n{traceback.format_exc()}"
        print(msg)
        return None, msg
    finally:
        shutil.rmtree(job_temp, ignore_errors=True)


def preview_pose(
    video_file,
    hand_size: float,
    finger_curl: float,
):
    """Preview the hand pose skeleton on the first frame — no SD, instant."""
    import cv2
    import numpy as np
    from PIL import Image
    from pipeline.segmenter import get_product_bbox
    from pipeline.hand_poser import generate_cradle_pose, get_pose_keypoints, create_inpaint_mask
    from pipeline.video_processor import resize_frame

    if video_file is None:
        return None

    cap = cv2.VideoCapture(video_file)
    ret, frame = cap.read()
    cap.release()
    if not ret:
        return None

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    h, w = frame_rgb.shape[:2]

    frame_small, scale = resize_frame(frame)
    bbox_small = get_product_bbox(frame_small)
    bbox = tuple(int(v / scale) for v in bbox_small)

    pose = generate_cradle_pose((h, w), bbox, hand_scale_factor=hand_size, curl=finger_curl)
    pts_r, pts_l = get_pose_keypoints((h, w), bbox, hand_scale_factor=hand_size, curl=finger_curl)
    mask = create_inpaint_mask((h, w), bbox, pts_r, pts_l)

    # Overlay pose + mask on original frame
    overlay = frame_rgb.copy()
    mask_vis = cv2.cvtColor(mask, cv2.COLOR_GRAY2RGB)
    # Tint mask region in blue
    tint = np.zeros_like(overlay)
    tint[mask > 128] = [0, 100, 255]
    overlay = cv2.addWeighted(overlay, 0.7, tint, 0.3, 0)
    # Draw pose skeleton on top
    overlay = cv2.addWeighted(overlay, 1.0, pose, 0.9, 0)

    # Draw product bbox
    x1, y1, x2, y2 = bbox
    cv2.rectangle(overlay, (x1, y1), (x2, y2), (0, 255, 0), 2)

    return Image.fromarray(overlay)


# ─── Gradio UI ────────────────────────────────────────────────────────────────

with gr.Blocks(
    title="HandVid — AI Product Hands",
    theme=gr.themes.Soft(),
    css="""
        .container { max-width: 1100px; margin: auto; }
        footer { display: none !important; }
    """,
) as demo:

    gr.Markdown(
        """
        # HandVid — AI Product Hands
        Upload a product video and get natural AI-generated hands cradling it.
        **First run downloads ~6 GB of models — subsequent runs are instant.**
        """
    )

    with gr.Row():
        # ── Left column: inputs ──
        with gr.Column(scale=1):
            video_input = gr.Video(
                label="Product Video",
                sources=["upload"],
            )

            gr.Markdown("### Hand Settings")
            skin_tone = gr.Radio(
                choices=["light", "medium", "dark"],
                value="medium",
                label="Skin Tone",
            )
            hand_size = gr.Slider(
                minimum=0.10, maximum=0.35, value=0.18, step=0.01,
                label="Hand Size  (relative to product)",
            )
            finger_curl = gr.Slider(
                minimum=0.1, maximum=0.8, value=0.35, step=0.05,
                label="Finger Curl  (0=flat, 0.8=cupped)",
            )

            gr.Markdown("### Quality Settings")
            inference_steps = gr.Slider(
                minimum=10, maximum=50, value=25, step=5,
                label="Inference Steps  (more = better quality, slower)",
            )
            seed = gr.Number(value=42, precision=0, label="Seed (for reproducibility)")

            gr.Markdown("### Detection Model")
            sam_model = gr.Radio(
                choices=["vit_b", "vit_h"],
                value="vit_b",
                label="SAM Model  (vit_b=fast 375MB · vit_h=best 2.4GB)",
            )

            with gr.Row():
                preview_btn = gr.Button("Preview Pose", variant="secondary")
                generate_btn = gr.Button("Generate Video", variant="primary")

        # ── Right column: outputs ──
        with gr.Column(scale=1):
            pose_preview = gr.Image(
                label="Pose Preview (green box=product, blue=hand region, skeleton=pose)",
                type="pil",
            )
            video_output = gr.Video(label="Output Video")
            status_text = gr.Textbox(label="Status", interactive=False, lines=3)

    # ── Event bindings ──
    preview_btn.click(
        fn=preview_pose,
        inputs=[video_input, hand_size, finger_curl],
        outputs=[pose_preview],
    )

    generate_btn.click(
        fn=process_video_gradio,
        inputs=[
            video_input,
            skin_tone,
            hand_size,
            finger_curl,
            inference_steps,
            sam_model,
            seed,
        ],
        outputs=[video_output, status_text],
    )

    gr.Markdown(
        """
        ---
        **Tips**
        - Click **Preview Pose** first to check hand placement before generating.
        - Increase **Inference Steps** to 30-40 for product shots — slower but cleaner hands.
        - If hands are too large/small adjust **Hand Size**.
        - For consistent hands across all frames keep the same **Seed**.
        - Run `python setup_models.py` to pre-download models before first use.
        """
    )


if __name__ == "__main__":
    demo.launch(
        server_name="127.0.0.1",
        server_port=7860,
        inbrowser=True,
        share=False,
    )
