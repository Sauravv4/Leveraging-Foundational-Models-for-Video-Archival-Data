# Leveraging Foundational Models for Video Archival Data

Segment-level metadata for the NVTV public archive, generated entirely by pretrained
models, where **every published field carries an auditable estimate of how strongly
independent sources corroborate it**.

MSc Artificial Intelligence · ECS8056 Themed Research Project
Saurav Kumar Vellattuparambil Vijayakumar · 40490925
Supervisor: Dr Awais Rauf · School of EEECS, Queen's University Belfast

No model in this repository is trained or fine-tuned. Every checkpoint runs zero-shot
at its published revision.

---

## What is here

Two independent tracks share one corpus.

**Track A — the main pipeline** (notebooks 01–03) segments each programme on a fixed
30-second grid, annotates five fields from at least two unrelated model families each,
and publishes a consensus record per clip with an evidence status and an agreement
score. The three RQ1–RQ5 experiments reported in the paper all come from this track.

**Track B — the scene-based comparison** (the three scripts) segments on detected shot
boundaries instead, then annotates those scenes twice — once with a hosted model and
once with local models, writing the same JSON shape both times so the two can be
compared scene by scene. This isolates the annotator from the segmentation.

| # | File | Role | Runs on |
|---|---|---|---|
| 1 | `01_metadata_pipeline.ipynb` | **Track A.** Clip creation, five-field annotation, consensus and agreement scoring, artefact export, review dashboard | Colab, A100 GPU |
| 2 | `02_vlm_benchmark.ipynb` | **Track A.** Seven open-weight vision-language models over every clip; checkpointed and resumable | Kelvin2, A100 MIG slice |
| 3 | `03_vlm_benchmark.ipynb` | **Track A.** Scoring and comparison tables only — loads no models | Anywhere, CPU |
| 4 | `detect_scenes_1_before_fix.py` | **Track B.** Shot-boundary detection over the source programmes | CPU, ~30× realtime |
| 5 | `annotation_with_gemni_1.py` | **Track B.** Hosted annotation of each detected scene | CPU + network |
| 6 | `annotation_with_local_models.py` | **Track B.** Local annotation of the same scenes, same output shape | GPU preferred |

---

## Track A — the main pipeline

### 1. `01_metadata_pipeline.ipynb`

Run top to bottom on a GPU runtime. The Drive layout is set in the header cell.

**Stages.** Source discovery and SHA-256 hashing → source-level calibration/evaluation
split (seeded, so no programme appears in both) → fixed 30-second clip cutting with
FFmpeg stream copy, FFprobe duration validation, atomic rename → scene-aware frame
sampling → five-field annotation → consensus and agreement scoring → artefact export →
a Flask dashboard that serves each clip beside its record.

**The five fields and their evidence families**

| Field | Families | Why these |
|---|---|---|
| `transcript` | Whisper small, Whisper turbo | Two decoder configurations; the weakest independence pair in the system, and reported as such |
| `on_screen_text` | Tesseract, EasyOCR | A classical line recogniser and a neural detection-plus-recognition stack — deliberately unrelated |
| `keywords` | KeyBERT, YAKE, TF-IDF | Three ranking functions, but over one transcript; the paper treats this as a design fault |
| `visual_tags` | CLIP ViT-B/32, CLIP ViT-L/14 | Capacity difference rather than mechanism difference; inflates this field's agreement |
| `people_count` | BLIP-VQA, ViLT-VQA, DETR | A captioning VQA model, a transformer VQA model and a convolutional detector — three unrelated routes to one integer |

An optional hosted Gemini annotator contributes one further family vote to visual tags
and people count. Its contribution to on-screen text is **diagnostic only** and cannot
override the dual-engine veto.

**Three rules that make the agreement score honest**

1. **Self-similarity excluded** — a source never corroborates itself.
2. **Empty output is never promoted** — if every source agrees nothing is present, the
   field is `not_detected`, never high agreement. Without this, a corpus of quiet,
   low-text clips would report near-perfect reliability.
3. **Strict dual-engine OCR veto** — a string publishes only if both engines find it
   (Tesseract ≥ 60, EasyOCR ≥ 0.50), it persists across ≥ 2 frames at ≥ 0.82, and the
   engines agree at ≥ 0.80. A hallucinated name in a catalogue is the most damaging
   error available here, so this field is deliberately conservative.

**Key outputs** — `clip_manifest.csv`, `ground_truth_metadata.json` (full records with
evidence, per-source candidates and the hosted-annotator ablation diagnostic),
`ground_truth_metadata_focused.json` (the five flattened values used by the benchmark),
`gemini_ablation_{detail,summary}.csv`, `pipeline_config.json`.

### 2. `02_vlm_benchmark.ipynb`

Seven models — Qwen3-VL 2B/4B/8B in Instruct and Thinking variants, InternVL3-2B and
-8B — run zero-shot over every clip under one protocol: 4 uniformly sampled frames,
identical prompt, greedy decoding, the same 34-label vocabulary. Both 8B models run
int4 on the 20 GB MIG slice, which confounds the scale comparison and is disclosed
wherever those rows appear.

Writes one `predictions_<model>.json` cache per model. **Resumable** — a re-run loads
the cache, retries only failed records, and skips completed ones, so an interrupted
job costs nothing. Each cache carries a `prompt_version`; a cache whose version does
not match the current prompt is ignored rather than silently mixed into current
results.

### 3. `03_vlm_benchmark.ipynb`

Scoring only. Loads no models and needs no GPU, so comparison tables rebuild in
seconds. Reads the focused ground truth and the prediction caches; reports per-model,
per-field agreement with coverage denominators alongside every mean, so a clean-looking
average over an unknown number of clips is not possible.

---

## Track B — scene-based comparison

### 4. `detect_scenes_1_before_fix.py`

```
python detect_scenes_1_before_fix.py /path/to/VIDEO_FILES
```

PySceneDetect `ContentDetector`, threshold 27.0, minimum scene length 10 s. CPU-only
and roughly 30× realtime; writes timestamps, never clips, so nothing is re-encoded and
the source media is untouched. Produces `_all_scenes.csv` with one row per scene:
`video, scene, start_sec, end_sec, length_sec`.

This file is also what supports the segmentation diagnostic in the supporting
materials: 72.2% of the fixed 30-second clips span at least one detected shot cut.

### 5. `annotation_with_gemni_1.py`

```
export GEMINI_API_KEY="..."         # never commit a key
python annotation_with_gemni_1.py /path/to/VIDEO_FILES _all_scenes.csv scene_metadata.json
```

Samples each detected scene at 1 fps with **no frame cap** and asks a hosted multimodal
model for a schema-constrained JSON record. The schema is wider than the pipeline's
five fields: on-screen text, visual tags from the same 34-label vocabulary, people
count, a short factual description, geographic location, activity, shot type, content
type, and uncertainty notes.

The prompt forbids identity inference, forbids inferring audio, intent or unseen
events, and forbids completing cropped or blurred text. `people_count_numeric` uses
`-1` as an explicit abstention for uncountable crowds — it is a sentinel, not a count,
and must not be averaged. Decoding is at `temperature=0.0`. Results are written after
every scene, so a quota failure part-way through loses nothing.

### 6. `annotation_with_local_models.py`

```
python annotation_with_local_models.py /path/to/VIDEO_FILES _all_scenes.csv scene_metadata_local_models.json
```

The same scenes, annotated by local models only, in the same output shape so the two
JSON files line up scene by scene. Whisper small for transcript, Tesseract over three
enhanced image variants for on-screen text, KeyBERT for keywords, CLIP ViT-B/32 for
visual tags, BLIP-VQA for people count.

**Resumable** — a re-run skips finished scenes and retries failed ones, and each save
goes through a temporary file and an atomic rename.

One deliberate difference from the notebook is recorded in the source: Whisper's
language is pinned to `en` rather than auto-detected. Auto-detection misreads
music-only intros as Welsh and loops, and the archive is English throughout. The
consequences of the un-pinned behaviour are discussed under fairness in the supporting
materials — three keyword extractors carried the spurious tokens into the published
field, because all three read the same transcript and nothing in the system could
dissent.

---

## Order of execution

```
Track A:  01_metadata_pipeline  →  02_vlm_benchmark  →  03_vlm_benchmark
Track B:  detect_scenes  →  annotation_with_gemni  and  annotation_with_local_models
```

Track B's two annotators are independent of each other and can run in either order;
both require `_all_scenes.csv` first.

---

## Environment

```bash
# Track A notebooks (Colab / Kelvin2)
pip install torch transformers openai-whisper sentence-transformers keybert yake \
            pytesseract easyocr scenedetect jiwer rouge-score jsonschema pydantic \
            google-genai flask seaborn
apt-get install -y tesseract-ocr ffmpeg

# Track B scripts
pip install google-genai opencv-python pydantic          # script 5
pip install torch openai-whisper transformers sentence-transformers keybert \
            pytesseract opencv-python pillow numpy       # script 6
```

Exact pinned versions, the compute used for each stage, and the rationale for every
package and model choice are in Section 4 of the supporting materials.

---

## Reproducibility

Seeds fixed; model revisions resolved and recorded; manifest ordering deterministic;
per-clip checkpointing throughout; failures recorded against their clip identifier
rather than suppressed; artefacts written atomically via a partial-file-and-rename
discipline, so an interrupted run cannot leave truncated JSON. GPU inference on shared
models is serialised while CPU OCR runs bounded-parallel, preventing CUDA contention
and non-thread-safe model use.

---

## Notes for a reader

- **Corroboration is not accuracy.** No human reference exists for this corpus. Every
  number these programs produce measures agreement between automatic sources.
- **Two source pairs are correlated.** The two CLIP variants and the two Whisper
  checkpoints share an architecture, so their agreement is worth less than the
  equal-weight scheme assumes. This is measured where the artefacts allow and declared
  where they do not.
- **Corroboration is blind to upstream error.** If speech recognition fails, all three
  keyword extractors agree on the same wrong text.
- **No secret belongs in this repository.** The hosted annotator reads its key from
  the environment; keep it there.
