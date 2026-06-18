"""Stage 2 — Visual metadata.

For every clip in the manifest:
  * sample ~6 evenly-spaced keyframes,
  * run CLIP zero-shot over the 10 categories (mean per-frame probabilities,
    then pick the top label + confidence per category),
  * compute a mean-pooled CLIP visual embedding,
  * generate a BLIP-2 caption (8-bit).

CLIP and BLIP-2 are loaded together, used for ALL clips, then deleted and the
GPU freed so Whisper (Stage 3) never shares memory with them.

Checkpointing: one JSON per clip in metadata_dir; a clip whose JSON already has
`visual_done: true` is skipped, so the stage resumes after interruption.

Run:
    python -m src.stage2_visual
"""
from __future__ import annotations

import argparse
import os
from typing import Dict, List

import numpy as np

from .config import Config, ensure_output_dirs, load_config
from .utils import (
    LOG,
    append_failure,
    free_gpu,
    get_device,
    read_json,
    sample_keyframes,
    set_seed,
    write_json,
)


def metadata_path(cfg: Config, clip_id: str) -> str:
    return os.path.join(cfg.metadata_dir, f"{clip_id}.json")


# ---------------------------------------------------------------------------
# Model loading
# ---------------------------------------------------------------------------

def load_clip(cfg: Config, device: str):
    from transformers import CLIPModel, CLIPProcessor

    LOG.info("Loading CLIP: %s", cfg.clip_model)
    model = CLIPModel.from_pretrained(cfg.clip_model).to(device).eval()
    processor = CLIPProcessor.from_pretrained(cfg.clip_model)
    return model, processor


def load_blip2(cfg: Config, device: str):
    """Load BLIP-2 in 8-bit. Note: quantisation is passed via
    `quantization_config`, NOT the removed `load_in_8bit` kwarg."""
    from transformers import (
        Blip2ForConditionalGeneration,
        Blip2Processor,
        BitsAndBytesConfig,
    )

    LOG.info("Loading BLIP-2 (8-bit): %s", cfg.blip2_model)
    processor = Blip2Processor.from_pretrained(cfg.blip2_model)
    if device == "cuda":
        quant = BitsAndBytesConfig(load_in_8bit=True)
        model = Blip2ForConditionalGeneration.from_pretrained(
            cfg.blip2_model,
            quantization_config=quant,
            device_map="auto",
        )
    else:
        # CPU fallback (slow) — 8-bit needs a GPU.
        LOG.warning("No GPU detected; loading BLIP-2 on CPU (will be slow).")
        model = Blip2ForConditionalGeneration.from_pretrained(cfg.blip2_model)
    model.eval()
    return model, processor


# ---------------------------------------------------------------------------
# CLIP zero-shot classification + embedding
# ---------------------------------------------------------------------------

def precompute_text_features(cfg: Config, clip_model, clip_processor, device):
    """Encode every candidate label once, grouped by category."""
    import torch

    text_features: Dict[str, "torch.Tensor"] = {}
    with torch.no_grad():
        for category, labels in cfg.categories.items():
            prompts = [f"a photo of {label}" for label in labels]
            inputs = clip_processor(text=prompts, return_tensors="pt",
                                    padding=True).to(device)
            feats = clip_model.get_text_features(**inputs)
            feats = feats / feats.norm(p=2, dim=-1, keepdim=True)
            text_features[category] = feats
    return text_features


def classify_clip(cfg: Config, frames, clip_model, clip_processor,
                  text_features, device):
    """Return (per-category {label, confidence}, mean-pooled embedding list)."""
    import torch

    with torch.no_grad():
        img_inputs = clip_processor(images=frames, return_tensors="pt").to(device)
        img_feats = clip_model.get_image_features(**img_inputs)
        img_feats = img_feats / img_feats.norm(p=2, dim=-1, keepdim=True)  # [F, D]

        logit_scale = clip_model.logit_scale.exp()

        results: Dict[str, Dict] = {}
        for category, labels in cfg.categories.items():
            txt = text_features[category]                       # [L, D]
            logits = logit_scale * img_feats @ txt.t()          # [F, L]
            probs = logits.softmax(dim=-1).mean(dim=0)          # [L] mean over frames
            best = int(probs.argmax().item())
            results[category] = {
                "label": labels[best],
                "confidence": round(float(probs[best].item()), 4),
            }

        # Mean-pooled, re-normalised visual embedding.
        embedding = img_feats.mean(dim=0)
        embedding = embedding / embedding.norm(p=2)
        embedding_list = embedding.cpu().numpy().astype(np.float32)

    return results, embedding_list


# ---------------------------------------------------------------------------
# BLIP-2 caption
# ---------------------------------------------------------------------------

def caption_clip(cfg: Config, frames, blip_model, blip_processor, device):
    import torch

    # Use the middle keyframe as a representative frame.
    frame = frames[len(frames) // 2]
    inputs = blip_processor(images=frame, return_tensors="pt")
    # Match BLIP-2's compute dtype/device (device_map="auto" places it on GPU).
    target_device = next(blip_model.parameters()).device
    inputs = {k: v.to(target_device) for k, v in inputs.items()}
    with torch.no_grad():
        out = blip_model.generate(**inputs,
                                  max_new_tokens=cfg.blip2_max_new_tokens)
    caption = blip_processor.batch_decode(out, skip_special_tokens=True)[0].strip()
    return caption


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(config_path: str | None = None) -> None:
    cfg = load_config(config_path)
    set_seed(cfg.seed)
    ensure_output_dirs(cfg)

    manifest = read_json(cfg.manifest_path, default=[])
    if not manifest:
        LOG.error("Empty/missing manifest at %s. Run Stage 1 first.",
                  cfg.manifest_path)
        return

    # Determine which clips still need visual metadata (checkpoint resume).
    todo: List[Dict] = []
    for entry in manifest:
        existing = read_json(metadata_path(cfg, entry["clip_id"]), default={})
        if existing.get("visual_done"):
            continue
        todo.append(entry)
    LOG.info("Visual stage: %d/%d clip(s) to process",
             len(todo), len(manifest))
    if not todo:
        return

    device = get_device()
    clip_model, clip_processor = load_clip(cfg, device)
    text_features = precompute_text_features(cfg, clip_model, clip_processor, device)
    blip_model, blip_processor = load_blip2(cfg, device)

    for i, entry in enumerate(todo, 1):
        clip_id = entry["clip_id"]
        LOG.info("[%d/%d] visual: %s", i, len(todo), clip_id)
        try:
            frames = sample_keyframes(entry["clip_path"], cfg.num_keyframes)
            cats, embedding = classify_clip(
                cfg, frames, clip_model, clip_processor, text_features, device)
            caption = caption_clip(cfg, frames, blip_model, blip_processor, device)

            # Save embedding separately to keep JSON small.
            emb_path = os.path.join(cfg.embeddings_dir, f"{clip_id}.npy")
            np.save(emb_path, embedding)

            record = read_json(metadata_path(cfg, clip_id), default={})
            record.update({
                "clip_id": clip_id,
                "clip_path": entry["clip_path"],
                "source_video": entry["source_video"],
                "source_synopsis": entry.get("source_synopsis"),
                "start_sec": entry["start_sec"],
                "end_sec": entry["end_sec"],
                "duration_sec": entry["duration_sec"],
                "clip_categories": cats,
                "scene_description": caption,
                "visual_embedding_path": emb_path,
                "visual_embedding_dim": int(embedding.shape[0]),
                "visual_done": True,
            })
            write_json(metadata_path(cfg, clip_id), record)
        except Exception as exc:
            append_failure(cfg.failures_path, {
                "stage": "visual",
                "clip_id": clip_id,
                "clip_path": entry.get("clip_path"),
                "error": repr(exc),
            })

    # Free BLIP-2 + CLIP BEFORE Whisper is ever loaded.
    LOG.info("Releasing CLIP + BLIP-2 from GPU memory.")
    free_gpu(blip_model, blip_processor, clip_model, clip_processor, text_features)
    LOG.info("Visual stage complete.")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Stage 2: CLIP + BLIP-2 visual metadata")
    ap.add_argument("--config", default=None, help="path to config.yaml")
    args = ap.parse_args()
    main(args.config)
