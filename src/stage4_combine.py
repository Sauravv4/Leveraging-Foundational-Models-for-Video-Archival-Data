"""Stage 4 — Combine per-clip JSON checkpoints into one machine-readable CSV
(one row per clip, one column per metadata category) for the report appendix.

Run:
    python -m src.stage4_combine
"""
from __future__ import annotations

import argparse
import glob
import os
from typing import Dict, List

import pandas as pd

from .config import Config, load_config
from .utils import LOG, read_json


def flatten_record(rec: Dict) -> Dict:
    row: Dict[str, object] = {
        "clip_id": rec.get("clip_id"),
        "clip_path": rec.get("clip_path"),
        "source_video": rec.get("source_video"),
        "source_synopsis": rec.get("source_synopsis"),
        "start_sec": rec.get("start_sec"),
        "end_sec": rec.get("end_sec"),
        "duration_sec": rec.get("duration_sec"),
    }

    # One label + confidence column per CLIP category.
    for category, value in (rec.get("clip_categories") or {}).items():
        row[f"{category}__label"] = value.get("label")
        row[f"{category}__confidence"] = value.get("confidence")

    row["scene_description"] = rec.get("scene_description")
    row["transcript"] = rec.get("transcript")
    row["transcript_language"] = rec.get("transcript_language")

    ents = rec.get("named_entities") or []
    row["named_entities"] = "; ".join(f"{e['text']} ({e['label']})" for e in ents)
    for label in ("PERSON", "GPE", "ORG", "LOC", "FAC"):
        row[f"entities_{label}"] = "; ".join(
            e["text"] for e in ents if e.get("label") == label)

    row["visual_embedding_path"] = rec.get("visual_embedding_path")
    return row


def build_csv(cfg: Config) -> str:
    files = sorted(glob.glob(os.path.join(cfg.metadata_dir, "*.json")))
    if not files:
        LOG.error("No per-clip JSON found in %s. Run Stages 1-3 first.",
                  cfg.metadata_dir)
        return ""

    rows: List[Dict] = []
    for path in files:
        rec = read_json(path, default={})
        if rec:
            rows.append(flatten_record(rec))

    df = pd.DataFrame(rows).sort_values("clip_id").reset_index(drop=True)
    os.makedirs(os.path.dirname(cfg.combined_csv), exist_ok=True)
    df.to_csv(cfg.combined_csv, index=False)
    LOG.info("Wrote combined CSV with %d row(s), %d column(s) -> %s",
             len(df), len(df.columns), cfg.combined_csv)
    return cfg.combined_csv


def main(config_path: str | None = None) -> None:
    cfg = load_config(config_path)
    build_csv(cfg)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Stage 4: combine per-clip JSON into CSV")
    ap.add_argument("--config", default=None, help="path to config.yaml")
    args = ap.parse_args()
    main(args.config)
