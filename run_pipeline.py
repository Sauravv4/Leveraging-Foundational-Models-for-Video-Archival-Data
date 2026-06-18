"""End-to-end orchestrator: run all stages in the correct order.

Memory-safe ordering is enforced here:
    Stage 1  segment
    Stage 2  visual metadata (CLIP + BLIP-2)  -> frees GPU when done
    Stage 3  transcribe (Whisper + spaCy)     -> loaded only after Stage 2
    Stage 4  combine -> CSV

Run the whole thing:
    python run_pipeline.py
Or a subset:
    python run_pipeline.py --stages segment visual
    python run_pipeline.py --config my.yaml
"""
from __future__ import annotations

import argparse

from src import (
    stage1_segment,
    stage2_visual,
    stage3_transcribe,
    stage4_combine,
)
from src.utils import LOG

STAGES = {
    "segment": stage1_segment.main,
    "visual": stage2_visual.main,
    "transcribe": stage3_transcribe.main,
    "combine": stage4_combine.main,
}


def main() -> None:
    ap = argparse.ArgumentParser(description="Run the NVTV metadata pipeline")
    ap.add_argument("--config", default=None, help="path to config.yaml")
    ap.add_argument("--stages", nargs="+", default=list(STAGES.keys()),
                    choices=list(STAGES.keys()),
                    help="subset of stages to run, in order")
    args = ap.parse_args()

    for stage in args.stages:
        LOG.info("=" * 60)
        LOG.info("STAGE: %s", stage)
        LOG.info("=" * 60)
        STAGES[stage](args.config)


if __name__ == "__main__":
    main()
