"""
Detect shot/scene boundaries for every video in a folder and write them all to
one CSV.

Cheap: uses PySceneDetect's content detector (auto-downscales, CPU-only,
~30x realtime). No re-encoding — it only writes timestamps, not clips.

Usage:
    python detect_scenes.py                          # uses defaults below
    python detect_scenes.py /path/to/videos          # override the videos folder
    python detect_scenes.py /path/to/videos out.csv  # also set the output CSV

Output: a single CSV with one row per scene, columns:
    video, scene, start_sec, end_sec, length_sec
"""

import csv
import os
import sys
from pathlib import Path

from scenedetect import open_video, SceneManager, ContentDetector

# ---- settings you can tweak ------------------------------------------------
VIDEO_DIR = Path(os.environ.get("NVTV_VIDEO_DIR", "data/VIDEO FILES"))
OUT_FILE  = Path(__file__).with_name("_all_scenes.csv")
THRESHOLD = 27.0   # lower = more cuts (more sensitive), higher = fewer cuts
MIN_SCENE_SEC = 10.0  # merge cuts closer than this -> coherent "scenes"
# ----------------------------------------------------------------------------


def detect_one(video_path: Path):
    """Return a list of (scene_no, start_sec, end_sec, length_sec) for one video."""
    video = open_video(str(video_path))
    fps = video.frame_rate
    sm = SceneManager()
    sm.add_detector(
        ContentDetector(threshold=THRESHOLD,
                        min_scene_len=round(MIN_SCENE_SEC * fps))
    )
    sm.detect_scenes(video, show_progress=True)

    rows = []
    for i, (start, end) in enumerate(sm.get_scene_list(), start=1):
        s, e = start.seconds, end.seconds
        rows.append((i, round(s, 3), round(e, 3), round(e - s, 3)))
    return rows


def main():
    video_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else VIDEO_DIR
    out_file = Path(sys.argv[2]) if len(sys.argv) > 2 else OUT_FILE

    if not video_dir.is_dir():
        sys.exit(f"Video folder not found: {video_dir}")
    videos = sorted(video_dir.glob("*.mp4"))
    if not videos:
        sys.exit(f"No .mp4 files found in {video_dir}")

    out_file.parent.mkdir(parents=True, exist_ok=True)
    total_scenes = 0

    with open(out_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["video", "scene", "start_sec", "end_sec", "length_sec"])

        for n, video_path in enumerate(videos, start=1):
            name = video_path.stem
            print(f"[{n}/{len(videos)}] {name}")
            rows = detect_one(video_path)

            for scene, s, e, length in rows:
                writer.writerow([name, scene, s, e, length])
            total_scenes += len(rows)

            total_sec = rows[-1][2] if rows else 0.0  # end of last scene = video length
            mins, secs = divmod(total_sec, 60)
            print(f"    -> {len(rows)} clips, total {int(mins):d}m{secs:04.1f}s "
                  f"({total_sec:.1f}s)")

    print(f"\nDone. {total_scenes} scenes from {len(videos)} videos written to {out_file}")


if __name__ == "__main__":
    main()
