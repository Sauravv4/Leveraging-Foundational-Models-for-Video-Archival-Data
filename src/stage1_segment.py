"""Stage 1 — Segmentation.

Split every source video into fixed 30-second clips using ffmpeg segment muxing
(stream copy, no re-encode, reset timestamps) and write a manifest.json.

Run:
    python -m src.stage1_segment            # uses config.yaml
    python -m src.stage1_segment --config my.yaml
"""
from __future__ import annotations

import argparse
import os
import subprocess
from typing import Dict, List

from .config import Config, ensure_output_dirs, load_config
from .utils import (
    LOG,
    append_failure,
    get_duration_sec,
    is_junk_file,
    set_seed,
    write_json,
)


def find_videos(cfg: Config) -> List[str]:
    """Recursively collect source videos, skipping macOS junk files."""
    videos: List[str] = []
    for root, _dirs, files in os.walk(cfg.dataset_dir):
        for name in files:
            if is_junk_file(name):
                continue
            if os.path.splitext(name)[1].lower() in cfg.video_extensions:
                videos.append(os.path.join(root, name))
    return sorted(videos)


def find_sidecar_txt(video_path: str) -> str | None:
    """Return a matching .txt synopsis/transcript (same basename) if present."""
    cand = os.path.splitext(video_path)[0] + ".txt"
    if os.path.exists(cand) and not is_junk_file(cand):
        return cand
    return None


def segment_video(cfg: Config, video_path: str) -> List[Dict]:
    """Segment a single video into 30s clips; return its manifest entries."""
    stem = os.path.splitext(os.path.basename(video_path))[0]
    out_dir = os.path.join(cfg.clips_dir, stem)
    os.makedirs(out_dir, exist_ok=True)

    pattern = os.path.join(out_dir, f"{stem}_%04d.mp4")
    cmd = [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-i", video_path,
        # Map only the primary video + any audio tracks. We deliberately do NOT
        # use "-map 0": archival MP4s often carry a data/timecode track (codec
        # "none") that cannot be stream-copied into the segmented container and
        # would abort ffmpeg. "0:a?" makes audio optional (video-only clips OK).
        "-map", "0:v:0",
        "-map", "0:a?",
        "-dn",                              # drop data streams
        "-sn",                              # drop subtitle streams
        "-c", "copy",                       # stream copy: no re-encode
        "-f", "segment",
        "-segment_time", str(cfg.clip_length_sec),
        "-reset_timestamps", "1",
        pattern,
    ]
    subprocess.run(cmd, check=True)

    synopsis = find_sidecar_txt(video_path)

    entries: List[Dict] = []
    clip_files = sorted(
        f for f in os.listdir(out_dir)
        if f.startswith(stem + "_") and f.endswith(".mp4") and not is_junk_file(f)
    )
    for idx, fname in enumerate(clip_files):
        clip_path = os.path.join(out_dir, fname)
        try:
            duration = round(get_duration_sec(clip_path), 3)
        except Exception:
            duration = float(cfg.clip_length_sec)
        start = idx * cfg.clip_length_sec
        entries.append({
            "clip_id": os.path.splitext(fname)[0],
            "clip_path": clip_path,
            "source_video": video_path,
            "source_synopsis": synopsis,
            "start_sec": float(start),
            "end_sec": round(start + duration, 3),
            "duration_sec": duration,
        })
    return entries


def main(config_path: str | None = None) -> None:
    cfg = load_config(config_path)
    set_seed(cfg.seed)
    ensure_output_dirs(cfg)

    videos = find_videos(cfg)
    LOG.info("Found %d source video(s) in %s", len(videos), cfg.dataset_dir)
    if not videos:
        LOG.warning("No videos found. Check paths.dataset_dir in your config.")

    manifest: List[Dict] = []
    for video_path in videos:
        LOG.info("Segmenting: %s", video_path)
        try:
            manifest.extend(segment_video(cfg, video_path))
        except Exception as exc:  # never crash the whole run on one bad file
            append_failure(cfg.failures_path, {
                "stage": "segment",
                "source_video": video_path,
                "error": repr(exc),
            })

    write_json(cfg.manifest_path, manifest)
    LOG.info("Wrote manifest with %d clip(s) -> %s",
             len(manifest), cfg.manifest_path)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Stage 1: segment videos into 30s clips")
    ap.add_argument("--config", default=None, help="path to config.yaml")
    args = ap.parse_args()
    main(args.config)
