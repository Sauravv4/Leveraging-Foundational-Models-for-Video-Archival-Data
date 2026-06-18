"""Stage 3 — Transcription + named entities.

For every clip:
  * transcribe speech with Whisper ("small" by default, configurable to
    "large-v3"),
  * extract named entities (PERSON, GPE, ORG, LOC, FAC) from the transcript
    with spaCy en_core_web_sm.

This stage loads ONLY Whisper + spaCy. Run it after Stage 2 has finished and
released the visual models, so the two large models never co-reside on the GPU.

Checkpointing: skips clips whose JSON already has `transcript_done: true`.

Run:
    python -m src.stage3_transcribe
    python -m src.stage3_transcribe --config my.yaml
"""
from __future__ import annotations

import argparse
import os
from typing import Dict, List

from .config import Config, ensure_output_dirs, load_config
from .utils import (
    LOG,
    append_failure,
    free_gpu,
    get_device,
    read_json,
    set_seed,
    write_json,
)


def metadata_path(cfg: Config, clip_id: str) -> str:
    return os.path.join(cfg.metadata_dir, f"{clip_id}.json")


def load_whisper(cfg: Config):
    import whisper

    LOG.info("Loading Whisper: %s", cfg.whisper_size)
    return whisper.load_model(cfg.whisper_size)


def load_spacy(cfg: Config):
    import spacy

    LOG.info("Loading spaCy: %s", cfg.spacy_model)
    try:
        return spacy.load(cfg.spacy_model)
    except OSError as exc:
        raise RuntimeError(
            f"spaCy model '{cfg.spacy_model}' not installed. Run:\n"
            f"    python -m spacy download {cfg.spacy_model}"
        ) from exc


def extract_entities(nlp, text: str, keep_labels: List[str]) -> List[Dict]:
    if not text.strip():
        return []
    doc = nlp(text)
    seen = set()
    ents: List[Dict] = []
    for ent in doc.ents:
        if ent.label_ not in keep_labels:
            continue
        key = (ent.text.strip(), ent.label_)
        if key in seen or not key[0]:
            continue
        seen.add(key)
        ents.append({"text": ent.text.strip(), "label": ent.label_})
    return ents


def main(config_path: str | None = None) -> None:
    cfg = load_config(config_path)
    set_seed(cfg.seed)
    ensure_output_dirs(cfg)

    manifest = read_json(cfg.manifest_path, default=[])
    if not manifest:
        LOG.error("Empty/missing manifest at %s. Run Stage 1 first.",
                  cfg.manifest_path)
        return

    todo: List[Dict] = []
    for entry in manifest:
        existing = read_json(metadata_path(cfg, entry["clip_id"]), default={})
        if existing.get("transcript_done"):
            continue
        todo.append(entry)
    LOG.info("Transcribe stage: %d/%d clip(s) to process",
             len(todo), len(manifest))
    if not todo:
        return

    device = get_device()
    whisper_model = load_whisper(cfg)
    nlp = load_spacy(cfg)
    fp16 = device == "cuda"

    for i, entry in enumerate(todo, 1):
        clip_id = entry["clip_id"]
        LOG.info("[%d/%d] transcribe: %s", i, len(todo), clip_id)
        try:
            result = whisper_model.transcribe(entry["clip_path"], fp16=fp16)
            transcript = result.get("text", "").strip()
            language = result.get("language")
            entities = extract_entities(nlp, transcript, cfg.entity_labels)

            record = read_json(metadata_path(cfg, clip_id), default={})
            # Ensure base manifest fields exist even if Stage 2 was skipped.
            record.setdefault("clip_id", clip_id)
            record.setdefault("clip_path", entry["clip_path"])
            record.setdefault("source_video", entry["source_video"])
            record.setdefault("source_synopsis", entry.get("source_synopsis"))
            record.setdefault("start_sec", entry["start_sec"])
            record.setdefault("end_sec", entry["end_sec"])
            record.setdefault("duration_sec", entry["duration_sec"])
            record.update({
                "transcript": transcript,
                "transcript_language": language,
                "named_entities": entities,
                "transcript_done": True,
            })
            write_json(metadata_path(cfg, clip_id), record)
        except Exception as exc:
            append_failure(cfg.failures_path, {
                "stage": "transcribe",
                "clip_id": clip_id,
                "clip_path": entry.get("clip_path"),
                "error": repr(exc),
            })

    free_gpu(whisper_model, nlp)
    LOG.info("Transcription stage complete.")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Stage 3: Whisper transcript + spaCy NER")
    ap.add_argument("--config", default=None, help="path to config.yaml")
    args = ap.parse_args()
    main(args.config)
