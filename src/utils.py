"""Shared helpers used by every stage: logging, JSON I/O, ffprobe, keyframe
sampling, GPU cleanup and reproducibility."""
from __future__ import annotations

import gc
import json
import logging
import os
import random
import subprocess
from typing import Any, Dict, List, Optional

import numpy as np

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

def get_logger(name: str = "pipeline") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        fmt = logging.Formatter("%(asctime)s | %(levelname)-7s | %(message)s",
                                datefmt="%H:%M:%S")
        handler.setFormatter(fmt)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


LOG = get_logger()

# ---------------------------------------------------------------------------
# Reproducibility
# ---------------------------------------------------------------------------

def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)
    try:
        import torch

        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
    except ImportError:
        pass


# ---------------------------------------------------------------------------
# File helpers
# ---------------------------------------------------------------------------

def is_junk_file(name: str) -> bool:
    """macOS junk: AppleDouble files ("._foo.mp4") and ".DS_Store"."""
    base = os.path.basename(name)
    return base.startswith("._") or base == ".DS_Store"


def read_json(path: str, default: Any = None) -> Any:
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: str, data: Any) -> None:
    """Atomic write so an interrupted run never leaves half-written JSON."""
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(tmp, path)


def append_failure(failures_path: str, record: Dict[str, Any]) -> None:
    """Log a failure to failures.json instead of crashing the run."""
    failures = read_json(failures_path, default=[])
    failures.append(record)
    write_json(failures_path, failures)
    LOG.warning("Recorded failure: %s", record.get("error", record))


# ---------------------------------------------------------------------------
# ffmpeg / ffprobe
# ---------------------------------------------------------------------------

def get_duration_sec(path: str) -> float:
    """Return media duration in seconds via ffprobe."""
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        path,
    ]
    out = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


# ---------------------------------------------------------------------------
# Keyframe sampling
# ---------------------------------------------------------------------------

def sample_keyframes(video_path: str, num_frames: int):
    """Return up to `num_frames` evenly-spaced PIL frames from a clip.

    Uses OpenCV; the import is local so stages that don't need frames (e.g. the
    transcription stage) don't pay the import cost.
    """
    import cv2
    from PIL import Image

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Could not open video: {video_path}")

    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frames: List[Any] = []
    try:
        if total <= 0:
            # Fallback: read sequentially if frame count is unknown.
            ok, frame = cap.read()
            while ok and len(frames) < num_frames:
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frames.append(Image.fromarray(rgb))
                for _ in range(15):  # skip ahead a little
                    ok, frame = cap.read()
            return frames

        # Evenly spaced indices, avoiding the very first/last frame.
        n = min(num_frames, total)
        indices = np.linspace(0, total - 1, n + 2, dtype=int)[1:-1] if n >= 1 else []
        for idx in indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, int(idx))
            ok, frame = cap.read()
            if not ok:
                continue
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frames.append(Image.fromarray(rgb))
    finally:
        cap.release()

    if not frames:
        raise RuntimeError(f"No frames decoded from: {video_path}")
    return frames


# ---------------------------------------------------------------------------
# GPU memory management
# ---------------------------------------------------------------------------

def free_gpu(*objs) -> None:
    """Delete references and aggressively free GPU memory.

    Call this after the BLIP-2/CLIP visual stage and BEFORE loading Whisper so
    the two large models are never resident at the same time.
    """
    for obj in objs:
        try:
            del obj
        except Exception:
            pass
    gc.collect()
    try:
        import torch

        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()
    except ImportError:
        pass


def get_device() -> str:
    try:
        import torch

        return "cuda" if torch.cuda.is_available() else "cpu"
    except ImportError:
        return "cpu"
