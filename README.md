# Component 1 — NVTV Archival Video Metadata Pipeline

MSc Video-Retrieval Project · Queen's University Belfast · ECS8056

This is **Component 1** of a two-part project. It ingests long-form archival TV
programmes from **NVTV** (a Belfast community broadcaster), splits each video
into **fixed 30-second clips**, and generates **at least 10 metadata fields per
clip** using foundational models. The output is saved in a clean,
machine-readable form (per-clip JSON + one combined CSV) that the Component 2
retrieval system will consume.

---

## What it produces (per clip)

| # | Field | Source |
|---|-------|--------|
| 1 | `clip_categories` — **10** zero-shot categories, each a chosen label + confidence | CLIP `clip-vit-base-patch32` |
| 2 | `scene_description` — natural-language caption | BLIP-2 `blip2-opt-2.7b` (8-bit) |
| 3 | `transcript` — speech transcript | Whisper (`small`, configurable `large-v3`) |
| 4 | `named_entities` — PERSON / GPE / ORG / LOC / FAC | spaCy `en_core_web_sm` |
| + | `visual_embedding` — mean-pooled CLIP embedding (`.npy`) | CLIP |
| + | manifest fields: `clip_id`, `clip_path`, `source_video`, `start_sec`, `end_sec`, `duration_sec` | ffmpeg/ffprobe |

The 10 CLIP categories: `visual_type`, `scene_environment`, `subject_topic`,
`on_screen_text`, `event_activity`, `physical_objects`, `weather_conditions`,
`crowd_density`, `infrastructure`, `architecture` (candidate labels are defined
in `config.yaml`).

---

## Project layout

```
config.yaml              # ALL paths, clip length, model names, categories
requirements.txt
run_pipeline.py          # orchestrator (runs stages in memory-safe order)
src/
  config.py              # loads + validates config.yaml
  utils.py               # logging, JSON I/O, ffprobe, keyframes, GPU cleanup, seeds
  stage1_segment.py      # ffmpeg 30s segment muxing -> manifest.json
  stage2_visual.py       # CLIP zero-shot + embedding + BLIP-2 caption
  stage3_transcribe.py   # Whisper transcript + spaCy NER
  stage4_combine.py      # per-clip JSON -> combined CSV
notebooks/
  colab_pipeline.ipynb   # one-click Colab runner
```

### Outputs (under `output/`)
```
output/
  clips/<video>/<video>_0000.mp4 ...   # 30s clips
  metadata/<clip_id>.json              # one checkpoint per clip (all fields)
  embeddings/<clip_id>.npy             # mean-pooled CLIP embedding
  manifest.json                        # all clips + timing
  failures.json                        # per-clip failures (run never crashes)
  metadata_combined.csv                # one row per clip, one col per category
```

---

## Write-up

The research paper and supporting-materials report are planned in
[`docs/WRITING_GUIDE.md`](docs/WRITING_GUIDE.md), built from the exemplar
submissions and the IEEE conference template kept in
[`docs/references/`](docs/references/README.md).

---

## Setup

### Prerequisites
- **ffmpeg / ffprobe** on `PATH` (segmentation + audio decode)
  - Linux: `sudo apt-get install ffmpeg` · macOS: `brew install ffmpeg`
- A CUDA GPU (~16 GB) is recommended. BLIP-2 8-bit needs a GPU; the code falls
  back to CPU but it will be slow.

### Install
```bash
python -m venv .venv && source .venv/bin/activate      # optional
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

---

## Running locally

1. Put your data somewhere and point the config at it. Edit `config.yaml`:
   ```yaml
   paths:
     dataset_dir: "/full/path/to/your/nvtv/videos"   # <-- your video folder
   ```
   The folder is searched **recursively** for `.mp4` (and `.mov/.mkv/.avi/.m4v`).
   macOS junk files (`._*`, `.DS_Store`) are skipped. A matching `.txt`
   (same basename as a video) is recorded as `source_synopsis`.

2. Run everything:
   ```bash
   python run_pipeline.py
   ```
   Or run stages individually (each is independently runnable + resumable):
   ```bash
   python -m src.stage1_segment       # split into 30s clips -> manifest.json
   python -m src.stage2_visual        # CLIP + BLIP-2 visual metadata
   python -m src.stage3_transcribe    # Whisper + spaCy
   python -m src.stage4_combine       # build combined CSV
   ```
   Subset via the orchestrator:
   ```bash
   python run_pipeline.py --stages segment visual
   ```

3. Use a different config without touching the default:
   ```bash
   python run_pipeline.py --config my_config.yaml
   # or: export PIPELINE_CONFIG=/path/to/my_config.yaml
   ```

---

## Running on Google Colab

Open `notebooks/colab_pipeline.ipynb` in Colab (**Runtime → Change runtime
type → GPU**, T4/16 GB is fine), then run the cells top to bottom. The notebook:

1. installs dependencies + the spaCy model,
2. lets you **upload your `.mp4` files directly** into a `/content/videos`
   folder (Files pane or the upload cell),
3. writes a Colab-specific config pointing `dataset_dir` at that folder,
4. runs all four stages and previews `metadata_combined.csv`,
5. (optional) zips `output/` so you can download the results.

> No dataset path is hardcoded for Colab — you upload the videos and the
> notebook points the config at the upload folder.

---

## Design notes (mapping to the requirements)

- **Segmentation** uses ffmpeg segment muxing with `-c copy` (stream copy, no
  re-encode), `-f segment -segment_time 30 -reset_timestamps 1`. No scene
  detection. See `src/stage1_segment.py`.
- **CLIP zero-shot** samples 6 evenly-spaced keyframes, averages the per-frame
  softmax probabilities **before** picking the top label per category. The
  visual embedding is the mean-pooled, re-normalised CLIP image embedding.
- **BLIP-2** is loaded in 8-bit via
  `BitsAndBytesConfig(load_in_8bit=True)` + `device_map="auto"` — the
  quantisation is passed through `quantization_config`, **never** the removed
  `load_in_8bit` kwarg to `from_pretrained`.
- **Memory management**: Stage 2 loads CLIP + BLIP-2, processes all clips, then
  deletes both and calls `gc.collect()` + `torch.cuda.empty_cache()`. Whisper is
  only ever loaded in Stage 3, so the two large models never co-reside.
- **Checkpointing**: one JSON per clip with `visual_done` / `transcript_done`
  flags; already-completed clips are skipped, so any stage resumes after
  interruption.
- **Config-driven**: paths, clip length, model names, Whisper size and the
  category label sets all live in `config.yaml`.
- **Robust I/O**: every per-clip operation is wrapped in try/except; failures
  are appended to `output/failures.json` instead of crashing the run.
- **Reproducibility**: `set_seed()` seeds `random`, `numpy` and `torch`.
