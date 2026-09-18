"""
Reproduce Section 3.8 of docs/report/supporting_materials.md.

Reads the scene CSV written by scripts/detect_scenes.py, reconstructs the
production fixed 30-second grid over the same programmes, and reports how far
the two partitions diverge — in particular, what fraction of published clips
span at least one detected shot cut.

CPU only, no model, no ground truth. Deterministic.

Usage:
    python scripts/segmentation_diagnostic.py _all_scenes.csv
"""

import csv
import statistics as st
import sys
from collections import Counter, defaultdict
from pathlib import Path

CLIP_SEC = 30.0  # production segmentation, config.yaml: clip_duration_sec


def load(csv_path: Path):
    """Group scene rows by programme, sorted by start time."""
    by_video = defaultdict(list)
    with open(csv_path, newline="") as f:
        for r in csv.DictReader(f):
            by_video[r["video"]].append((float(r["start_sec"]), float(r["end_sec"])))
    for scenes in by_video.values():
        scenes.sort()
    return by_video


def fixed_grid(length_sec: float):
    """The production 30 s grid over a programme of this length, last clip short."""
    n = int(length_sec // CLIP_SEC) + (1 if length_sec % CLIP_SEC > 0 else 0)
    return [(i * CLIP_SEC, min((i + 1) * CLIP_SEC, length_sec)) for i in range(n)]


def main():
    csv_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("_all_scenes.csv")
    if not csv_path.is_file():
        sys.exit(f"Scene CSV not found: {csv_path}")

    by_video = load(csv_path)
    lengths = [e - s for scenes in by_video.values() for s, e in scenes]

    n_clips = 0
    cuts_per_clip = Counter()
    n_cuts = 0
    scenes_split = 0
    tail_short = 0

    for scenes in by_video.values():
        duration = scenes[-1][1]                  # end of last scene = programme length
        cuts = [s for s, _ in scenes[1:]]         # internal shot boundaries
        n_cuts += len(cuts)

        for a, b in fixed_grid(duration):
            n_clips += 1
            cuts_per_clip[sum(1 for c in cuts if a < c < b)] += 1

        for i, (s, e) in enumerate(scenes):
            if int(s // CLIP_SEC) != int((e - 1e-9) // CLIP_SEC):
                scenes_split += 1
            if e - s < 10.0 and i == len(scenes) - 1:
                tail_short += 1

    n_scenes = len(lengths)
    impure = n_clips - cuts_per_clip[0]
    two_plus = sum(v for k, v in cuts_per_clip.items() if k >= 2)

    print(f"programmes                    {len(by_video)}")
    print(f"scenes detected               {n_scenes}")
    print(f"internal shot cuts            {n_cuts}")
    print(f"fixed clips (reconstructed)   {n_clips}")
    print(f"total duration                {sum(lengths) / 3600:.2f} h\n")

    print("scene length (s): mean %.2f  median %.2f  sd %.2f  min %.2f  max %.2f"
          % (st.mean(lengths), st.median(lengths), st.pstdev(lengths),
             min(lengths), max(lengths)))
    print("  <10 s %d (tail remainders: %d)   >60 s %d   >120 s %d\n"
          % (sum(1 for x in lengths if x < 10), tail_short,
             sum(1 for x in lengths if x > 60), sum(1 for x in lengths if x > 120)))

    print("fixed clips containing >=1 shot cut   %4d / %d  (%.1f%%)"
          % (impure, n_clips, 100 * impure / n_clips))
    print("fixed clips containing >=2 shot cuts  %4d / %d  (%.1f%%)"
          % (two_plus, n_clips, 100 * two_plus / n_clips))
    print("fixed clips wholly inside one shot    %4d / %d  (%.1f%%)"
          % (cuts_per_clip[0], n_clips, 100 * cuts_per_clip[0] / n_clips))
    print("scenes split by a fixed boundary      %4d / %d  (%.1f%%)"
          % (scenes_split, n_scenes, 100 * scenes_split / n_scenes))
    print("\ncuts-per-fixed-clip histogram: %s"
          % dict(sorted(cuts_per_clip.items())))


if __name__ == "__main__":
    main()
