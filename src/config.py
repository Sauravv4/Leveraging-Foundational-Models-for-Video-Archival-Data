"""Load and validate the pipeline configuration (config.yaml).

Every stage imports `load_config()` so that paths, clip length, model names and
the CLIP category lists live in exactly one place.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any, Dict, List

import yaml

# Default location: config.yaml in the project root (one level up from src/).
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CONFIG_PATH = os.path.join(PROJECT_ROOT, "config.yaml")


@dataclass
class Config:
    raw: Dict[str, Any]

    # --- paths ---
    dataset_dir: str = ""
    output_dir: str = ""
    clips_dir: str = ""
    metadata_dir: str = ""
    embeddings_dir: str = ""
    manifest_path: str = ""
    failures_path: str = ""
    combined_csv: str = ""

    # --- segmentation ---
    clip_length_sec: int = 30
    video_extensions: List[str] = field(default_factory=list)

    # --- models ---
    clip_model: str = ""
    blip2_model: str = ""
    whisper_size: str = ""
    spacy_model: str = ""

    # --- visual ---
    num_keyframes: int = 6
    blip2_max_new_tokens: int = 40

    entity_labels: List[str] = field(default_factory=list)
    seed: int = 42
    categories: Dict[str, List[str]] = field(default_factory=dict)


def _abspath(path: str) -> str:
    """Resolve relative paths against the project root so the pipeline behaves
    the same regardless of the current working directory."""
    if not path:
        return path
    path = os.path.expanduser(path)
    if os.path.isabs(path):
        return path
    return os.path.normpath(os.path.join(PROJECT_ROOT, path))


def load_config(path: str | None = None) -> Config:
    path = path or os.environ.get("PIPELINE_CONFIG", DEFAULT_CONFIG_PATH)
    with open(path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    paths = raw["paths"]
    seg = raw["segmentation"]
    models = raw["models"]
    visual = raw["visual"]

    cfg = Config(
        raw=raw,
        dataset_dir=_abspath(paths["dataset_dir"]),
        output_dir=_abspath(paths["output_dir"]),
        clips_dir=_abspath(paths["clips_dir"]),
        metadata_dir=_abspath(paths["metadata_dir"]),
        embeddings_dir=_abspath(paths["embeddings_dir"]),
        manifest_path=_abspath(paths["manifest_path"]),
        failures_path=_abspath(paths["failures_path"]),
        combined_csv=_abspath(paths["combined_csv"]),
        clip_length_sec=int(seg["clip_length_sec"]),
        video_extensions=[e.lower() for e in seg["video_extensions"]],
        clip_model=models["clip_model"],
        blip2_model=models["blip2_model"],
        whisper_size=models["whisper_size"],
        spacy_model=models["spacy_model"],
        num_keyframes=int(visual["num_keyframes"]),
        blip2_max_new_tokens=int(visual["blip2_max_new_tokens"]),
        entity_labels=list(raw["entity_labels"]),
        seed=int(raw["seed"]),
        categories=dict(raw["categories"]),
    )
    return cfg


def ensure_output_dirs(cfg: Config) -> None:
    for d in (cfg.output_dir, cfg.clips_dir, cfg.metadata_dir, cfg.embeddings_dir):
        os.makedirs(d, exist_ok=True)
