# Supporting Materials

**Reliability-Aware Multi-Model Metadata Generation for Archival Community Television**
NVTV public archive · MSc Artificial Intelligence · Queen's University Belfast

> Companion to `docs/paper/conference_paper.md`. Single-column technical report. The paper carries
> the claim and its evidence; this document carries everything that supports the claim but does not
> fit — the full literature review, the lifecycle, the verification work, the tooling, the
> reflection and the appendices. Structure follows the exemplar supporting-materials documents in
> `docs/references/exemplars/`. Outstanding items are marked **`[TO FILL]`**.

---

## Contents

1. Extended Literature and Context
2. Project Lifecycle
3. Verification and Validation
4. Tooling and Environment
5. Reflection
6. Responsible AI
7. Appendices

---

## 1. Extended Literature and Context

### 1.1 Scope and Method

The paper's related-work section is held to approximately one page and cites only what the
contribution directly stands on. This section widens it across five areas: archival and broadcast
video indexing; foundation models as zero-shot annotators; consensus and weak supervision;
reliability and agreement estimation; and vision-language models for video description.

Sources were identified through Google Scholar, IEEE Xplore, the ACM Digital Library and the ACL
Anthology, using combinations of *archival video*, *audiovisual metadata*, *video retrieval*,
*zero-shot annotation*, *weak supervision*, *model consensus*, *inter-annotator agreement*,
*vision-language model* and *hallucination*, supplemented by forward and backward citation tracing
from the primary model papers. Priority was given to peer-reviewed work; model releases from 2024
onwards are cited from technical reports and model cards where no peer-reviewed version exists,
which is noted as a limitation of the citation base rather than glossed over.

### 1.2 Archival and Broadcast Video Indexing

**Benchmark infrastructure.** TRECVid [1] defined the task vocabulary this project inherits — shot
boundary detection, semantic concept annotation, ad-hoc search — and with it the methodological
expectation that systems be scored against human-annotated references. That infrastructure was
built for research collections with annotation budgets. The structural problem for working
archives is that the collections most in need of description are the least likely to attract such
a budget, so the evaluation apparatus the field standardised on is unavailable exactly where the
technology is most needed.

**Cultural-heritage and community archives.** **`[TO FILL: 4–6 sources. Search terms that work:
"audiovisual archive automatic metadata", "cultural heritage video access", "community archive
digitisation AI". Look for EUscreen, the Netherlands Institute for Sound and Vision's published
work, and BBC R&D archive-indexing output. For each, record: the collection, whether a human
reference was collected, and what reliability signal (if any) accompanied the published metadata.
The claim this section must support is that per-field reliability signals are rare in this
literature — verify that claim rather than assuming it.]`**

**The gap this project addresses.** Automatic description of archives is well established;
publishing it *with an auditable per-field reliability estimate* is not. The distinction matters
operationally: an archivist can triage a record that flags its own weak fields, and cannot triage
one that presents every field with identical confidence.

### 1.3 Foundation Models as Zero-Shot Annotators

Contrastive image–text pretraining [2] removed the requirement for task-specific training data in
visual labelling, turning annotation into a matter of writing a label vocabulary. Large-scale
weakly supervised speech recognition [3] did the same for transcription. BLIP [4] and ViLT [5]
brought open-ended visual question answering, and end-to-end set-prediction detection [6] supplies
an architecturally unrelated route to counting.

The property this project exploits is not accuracy but **failure-mode heterogeneity**. CLIP's
errors are ranking errors within a label space it was never calibrated on. A VQA model's errors
are answer-prior errors — it answers "two" often because "two" is a common answer. A detector's
errors are missed small or occluded instances. These three mechanisms are not correlated, so
concurrence between them is informative in a way that concurrence between two checkpoints of one
architecture is not. This is also the origin of one of the project's own limitations: CLIP
ViT-B/32 and ViT-L/14 *do* share a mechanism, so their agreement is worth less than the equal-
weighting scheme implicitly assumes (§3.6, and RQ4 in the paper).

### 1.4 Consensus, Weak Supervision and Silver Standards

Programmatic weak supervision [7] formalised combining noisy, correlated labelling sources of
unknown accuracy into probabilistic labels, learning source accuracies from agreement patterns
without ground truth. That last property is what makes it relevant here, and its central
assumption — that sources are conditionally independent given the true label — is precisely the
assumption two CLIP variants violate.

This project deliberately stops short of the full weak-supervision machinery. A learned generative
model over source accuracies would produce a number that *looks* like a probability of
correctness, and publishing such a number for an archive catalogue, with no human reference
anywhere in the system to validate it against, would misrepresent what was measured. The project
instead publishes raw corroboration and states repeatedly what it is not. That is a weaker output
and a more defensible one; §5.2 revisits the decision.

**Silver standards.** The term is established in biomedical NLP for references built by automatic
system agreement rather than human annotation, along with the accompanying caution that systems
sharing training resources agree in correlated ways. This project adopts both the term and the
caution: the JSON header identifies the artefact as an automated multi-model silver standard.

### 1.5 Reliability and Agreement Estimation

Corpus linguistics has quantified annotation trustworthiness for decades [8]. The useful import is
conceptual: agreement statistics measure the *reliability* of an annotation process, which is a
precondition for validity but is not validity. High agreement among consistently biased annotators
is high reliability and zero validity.

Two design rules follow directly, and both are implemented. First, self-similarity is excluded
from every agreement computation — an annotator cannot corroborate itself, so a value is never
scored against the source that produced it. Second, empty output is never promoted: unanimous
absence is recorded as `not_detected`, never as high agreement, which prevents the degenerate
optimum of a system that detects nothing and reports perfect corroboration. On a corpus with many
low-text, low-motion clips, that failure mode is not hypothetical.

**Reported thresholds.** The tier boundaries (high ≥ 0.75, moderate ≥ 0.50, low < 0.50) are
conventional, chosen before the evaluation split was examined, and are **not** derived from this
corpus. They are a presentation convenience, not a calibrated result, and the underlying continuous
score is retained in every artefact so any downstream user can re-bin.

### 1.6 Vision-Language Models for Video Description

Open-weight multimodal models — Qwen3-VL [9], InternVL3 [10] — accept interleaved image sequences
and emit schema-constrained JSON, making a single-prompt replacement for a multi-component
pipeline architecturally plausible. Two concerns motivated benchmarking them rather than adopting
them.

The first is hallucination [11]: fluent description of content that is not present. For a
catalogue record this is worse than omission, because it is indistinguishable from a correct
record without checking the footage.

The second is the modality gap. None of these models accepts audio. A pipeline component that
transcribes speech cannot be replaced by a model that cannot hear it — a claim that is obvious
stated plainly and that the benchmark nonetheless quantifies (0.000–0.034 ROUGE-L; 613 of 615
predictions empty for Qwen3-VL-4B-Instruct), because "obvious" is not a result and a reviewer is
entitled to the number.

### 1.7 Comparative Literature Matrix

| Work | Domain | Reference standard | Reliability signal published | Modalities | What it leaves open |
|---|---|---|---|---|---|
| TRECVid [1] | Broadcast video | Human annotation | System scores only | Visual, some ASR | Assumes an annotation budget exists |
| CLIP [2] | General images | Zero-shot, benchmark datasets | Softmax ranking scores | Image + text | Scores are not calibrated probabilities |
| Whisper [3] | Speech | Human transcripts | None per-utterance | Audio | No per-segment reliability estimate |
| Snorkel [7] | Text/structured | None required | Learned source accuracies | Text | Assumes conditional source independence |
| Artstein & Poesio [8] | Annotated corpora | Multiple human coders | Chance-corrected agreement | Text | Human coders, not model families |
| Qwen3-VL [9] / InternVL3 [10] | General multimodal | Benchmark suites | None | Image + text | No audio; hallucination unquantified per field |
| **This work** | Archival community TV | **None available** | **Per-field status + agreement + support set** | Audio, visual, OCR, text | **Corroboration ≠ correctness; unvalidated** |

### 1.8 Synthesis and Positioning

Three threads converge. Archival AV description rarely publishes per-field reliability. Consensus
methods are mature for single-label classification but rarely applied to the heterogeneous field
types a catalogue record actually contains — free text, ranked sets, closed-vocabulary multi-label,
integers — each of which needs its own agreement measure. And where no human reference can be
collected at all, there is little methodological guidance on what may legitimately be reported.

This project's position is to build the corroboration machinery, report it honestly as
corroboration, and treat the resulting limits on what can be claimed as a finding rather than an
apology. The strongest evidence that the position is the right one is RQ4: the hosted annotator
rewrites 49.0% of visual-tag sets while agreeing with the local consensus 42% of the time, and the
project's own instrumentation makes that visible *and* makes clear it cannot be adjudicated
without the human reference the project did not have.

---

## 2. Project Lifecycle

### 2.1 Planning and Scoping

The initiating constraint was a requirement excluding manual annotation of the NVTV material. That
single constraint determined the project's shape: with no gold standard obtainable, "how accurate
is the metadata" became unanswerable, and the answerable question became "how strongly do
independent sources corroborate each field, and what follows from that". Reframing the deliverable
from an accurate catalogue to a *triaged* catalogue was the decision the rest of the project
depended on, and it was taken at the start rather than discovered late.

Five fields were fixed early — transcript, on-screen text, keywords, visual tags, people count —
on the criterion that each must be generable by **at least two architecturally unrelated model
families**. Fields failing that test were excluded no matter how useful they would have been: a
single-source field cannot be corroborated, so it cannot carry the signal the project exists to
produce.

### 2.2 Data Acquisition and Preparation

47 programmes were supplied as MP4 with optional matching synopsis text. Preparation:
recursive discovery with deterministic sorting; exclusion of macOS sidecar files; FFprobe
inspection before segmentation; 30-second segmentation with a 2.0-second minimum for the trailing
fragment; per-clip duration validation; atomic publication.

**Source-level splitting** was chosen over clip-level: 9 programmes to calibration, 38 to
evaluation. Clip-level splitting would have leaked, because consecutive clips from one programme
share a studio, a caption template, a speaker and a lighting setup. Only the calibration split was
inspected while choosing the sampling policy and thresholds.

### 2.3 Implementation

Built as three notebooks (`notebooks/`):

| Notebook | Role |
|---|---|
| `01_metadata_pipeline.ipynb` | Clip creation, all five fields, verifier phases, hosted annotator, ablations, robustness, agreement scoring, focused export, Flask browser |
| `02_vlm_benchmark_run.ipynb` | Runs seven VLMs over the clips, one at a time, checkpointed and resumable |
| `03_vlm_benchmark_comparison.ipynb` | Loads cached predictions only; scores and builds the comparison tables. Loads no models |

The third notebook exists because of a lesson learned the hard way (§5.3): separating scoring from
inference means the comparison tables can be rebuilt in seconds without a GPU, and a model with no
cache appears as zero coverage instead of crashing the run.

Two implementation constraints shaped the code. **GPU memory**: models are loaded in phases —
primary models, then released; verifier ASR, then released; verifier visual; and in the benchmark,
exactly one VLM resident at a time. **Concurrency**: CPU OCR runs bounded-parallel while shared-model
GPU inference is serialised, because the model objects are not thread-safe and CUDA contention
produced non-deterministic failures.

### 2.4 Experimentation

Four experiments, all specified before results were inspected: the frame-sampling ablation
(calibration subset, *n* = 8); perturbation robustness (*n* = 5); the hosted-annotator contribution
ablation (*n* = 626); and the VLM benchmark (*n* = 615, 21,140 scores).

The ablation and robustness sample sizes were set by runtime, and both are underpowered. They were
run on the calibration split specifically so that a policy could be chosen without inspecting
evaluation material — a real methodological gain that does not offset the low *n*, and both are
reported with sample sizes in the table captions so no reader can mistake their weight.

### 2.5 Evaluation and Iteration

Per-clip checkpointing made iteration cheap: a change to the agreement rules re-ran scoring without
re-running inference. Failures were recorded against clip identifiers rather than suppressed —
the final pipeline run recorded 626 successes and 0 failures, and the benchmark recorded which
clips each model was actually scored on (615/615 on every field except people count at 560/615)
so that a score computed from fewer clips is visible rather than hidden.

---

## 3. Verification and Validation

Nothing in this section measures correctness against human judgement — none is available. It
verifies that the system does what it is specified to do.

### 3.1 Clip Creation

- **Duration validation.** Every clip's duration is FFprobe-verified after writing; a clip failing
  validation is not published. 626/626 passed.
- **Atomic publication.** Each worker writes a uniquely named partial file and renames on success,
  so an interrupted run cannot leave a truncated MP4 that a later run would treat as complete.
- **Order independence.** The manifest is sorted deterministically after collection, so thread
  completion order cannot affect dataset ordering or the source-level split.
- **`[TO FILL: boundary check.]`** Sample 10 clips, confirm that clip *n* starts exactly where clip
  *n*−1 ends and that the reported `start_sec` matches the source timecode. Report the maximum
  observed drift. This is the check that catches a timestamp-reset bug, and it has not been run.

### 3.2 Split Integrity

- No source contributes clips to both splits (enforced at source level, verifiable from the
  manifest).
- **`[TO FILL]`** Confirm programmatically that the intersection of source IDs across splits is
  empty, and report the clip counts per split.

### 3.3 Determinism and Resumability

- Seeds fixed for `random`, `numpy` and `torch`; greedy decoding throughout the benchmark.
- Model revisions resolved to commit hashes and recorded — e.g. CLIP `32bd6428…`, ViLT `d0a1f6ab…`,
  DETR `70120ba8…`, MiniLM `1110a243…` — so a re-run can be pinned to identical weights.
- **`[TO FILL: resume equivalence test.]`** Run 20 clips uninterrupted; run the same 20 with a
  forced interruption at clip 10 and a resume; diff the resulting JSON. They must be identical.
  This is the single most valuable unrun check in this document: the entire pipeline is built on
  checkpoint-and-resume, and that property is currently assumed rather than demonstrated.

### 3.4 Agreement-Machinery Verification

The agreement code embodies three rules that are worth testing directly, because a silent failure
in any of them would inflate every reported score:

1. **Self-similarity exclusion.** A field with one source must return `agreement_score = null` and
   `agreement_tier = not_scored`, never 1.0.
2. **No empty-output promotion.** A field where all sources return empty must be `not_detected`
   with a null score.
3. **Equal family weight.** Sampling more frames must not change a family's total vote weight.

**`[TO FILL]`** Assert each of the three on constructed inputs and report the result. Rule 3 is the
one most likely to break silently under a future change to the sampling policy.

### 3.5 OCR Veto Verification

The strict dual-engine rule was verified empirically, not just by inspection: the hosted annotator
proposed on-screen text on 38.5% of clips (626 clips) and the **exact output-change rate was
0.0000**. The veto holds across the whole corpus. This is reported as a result in the paper
(Table V) because it is one — a specified safety property, tested at corpus scale and confirmed.

### 3.6 Source-Independence Audit

The equal-weight scheme assumes independent families. Two pairs are not independent:

| Pair | Shared | Consequence |
|---|---|---|
| CLIP ViT-B/32 / ViT-L/14 | Architecture, training objective, data distribution | Visual-tag agreement overstated |
| Whisper-small / -turbo | Architecture, training data | Transcript agreement overstated |

**`[TO FILL]`** Quantify this: report mean agreement within the correlated pair against mean
agreement between an unrelated pair (e.g. Tesseract/EasyOCR, or BLIP-VQA/DETR). If the correlated
pairs score systematically higher, the size of that gap is the inflation factor, and it belongs in
the paper's limitations with a number attached rather than as a qualitative caveat.

### 3.7 Artefact Verification

- Every JSON artefact is written atomically (partial file + `os.replace`).
- The exported ground truth is schema-validated.
- The API key is never written to any artefact; only provenance metadata is recorded.
- Prediction caches carry a `prompt_version`; a cache whose version does not match is ignored
  rather than silently mixed with current results — this is checked at load time in
  `03_vlm_benchmark_comparison.ipynb`.
- **`[TO FILL]`** Confirm that clip IDs in `ground_truth_metadata_615.json`, the embeddings/frames
  on disk and the prediction caches are a three-way exact match, and reconcile 626 generated
  against 615 scored.

---

## 4. Tooling and Environment

### 4.1 Compute

| | Pipeline | VLM benchmark |
|---|---|---|
| Platform | Google Colab | Kelvin2 HPC (QUB) |
| GPU | NVIDIA A100-SXM4-40GB | A100 MIG `2g.20gb` slice |
| CPUs | 12 | **`[TO FILL]`** |
| Python | 3.13.15 | **`[TO FILL]`** |
| PyTorch | 2.11.0+cu128 | 2.7.1+cu118 |
| Persistence | Google Drive | `~/sharedscratch` |

### 4.2 Pinned Packages

`transformers==4.50.3`, `openai-whisper==20250625`, `sentence-transformers==3.4.1`,
`keybert==0.9.0`, `jiwer==4.0.0`, `pytesseract==0.3.13`, `easyocr==1.7.2`, `yake==0.6.0`,
`scenedetect==0.7.1`, `jsonschema==4.26.0`, `flask==3.1.3`, `pydantic==2.12.5`,
`google-genai==2.17.0`, `seaborn==0.13.2`, `rouge-score==0.1.2`. System: FFmpeg, Tesseract via
`apt`.

### 4.3 Models

| Role | Model | Notes |
|---|---|---|
| ASR (primary) | `whisper-small` | Also performs language ID |
| ASR (verifier) | `whisper-turbo` | Deterministic output published |
| OCR | Tesseract; EasyOCR | Both required for publication |
| Visual tags (primary) | `openai/clip-vit-base-patch32` | 34-label vocabulary |
| Visual tags (verifier) | `openai/clip-vit-large-patch14` | Prompt: "a photograph of {label}" |
| People count | `Salesforce/blip-vqa-base`; `dandelin/vilt-b32-finetuned-vqa`; `facebook/detr-resnet-50` | Three families |
| Keywords | KeyBERT (`all-MiniLM-L6-v2`); YAKE; TF-IDF | Top *k* = 5 |
| Hosted annotator | `gemini-3.6-flash` | Optional; ≤ 5 frames; one family vote |
| Benchmark | Qwen3-VL 2B/4B/8B (Instruct, Thinking); InternVL3-2B/-8B | 8B models int4 |

### 4.4 Tool-Driven Constraints

Four reported design choices are hardware artefacts, not scientific ones, and are labelled as such
wherever they appear:

1. **4-frame benchmark budget.** 6 frames caused OOM for Qwen3-VL-8B-Instruct on the 20 GB MIG
   slice. The whole benchmark therefore runs at 4 frames, and not at the pipeline's scene-aware
   policy.
2. **int4 quantisation for both 8B models.** bf16 8.77B parameters (~17.5 GB) left no headroom on a
   20 GB slice. This confounds the scale comparison and is disclosed at every mention.
3. **32B, FP8 and GGUF checkpoints excluded entirely** — memory, driver-dependent tensor-core
   support and a separate inference stack respectively. Excluded for capacity, never tested and
   dropped, which is a different and weaker statement than "did not perform well".
4. **Sequential model loading.** Says nothing about concurrent multi-model serving performance.

---

## 5. Reflection

### 5.1 Divergence from the Original Specification

**No human annotation of NVTV material.** The requirement excluded it. Consequence: no accuracy
measurement anywhere in the project, and the reframing described in §2.1. **`[TO FILL: confirm this
was supervisor-approved and state when, as the exemplars do for their own scope changes.]`**

**Fine-tuning not reported.** The pipeline notebook's methodological-rules cell describes LoRA
fine-tuning of CLIP's vision tower and BLIP-VQA's answer decoder on calibration-split human labels
(its Sections 18B–18E). **Those sections are not present in the executed notebook and no
fine-tuning result exists.** The paper therefore reports a fully zero-shot system. **`[TO FILL:
either remove the fine-tuning language from the notebook's rules cell so the artefact matches what
was run, or run those sections and add the results. The current mismatch between the notebook's
stated method and its executed content is the kind of discrepancy an examiner will notice, and it
is better resolved than explained.]`**

**Two corpus sizes.** The pipeline generated 626 clips; the benchmark scored 615. **`[TO FILL:
reconcile, and state the reason in both documents.]`**

### 5.2 Design Rationale

**Why corroboration rather than a learned reliability model.** Weak supervision could have produced
a per-field probability. With no human reference anywhere in the system, that probability could
never have been validated, and publishing an unvalidated probability in an archive catalogue would
mislead exactly the users the project is for. Raw corroboration with an explicit disclaimer is
weaker output and honest output. If a human reference is collected later, the artefacts retain
everything needed to fit such a model retrospectively.

**Why a dual-engine OCR veto.** On-screen text is the field where a hallucination is most damaging
— an invented name or headline entering a catalogue is indistinguishable from a real one without
checking the footage. The veto trades recall for precision deliberately, and §3.5 confirms it
holds at corpus scale.

**Why equal family weights.** The neutral default absent measured reliability, with a provenance
file so measured weights can replace them. RQ4 shows the cost: on visual tags, where two of three
families are correlated, the neutral default lets a third family rewrite half the output.

**Why fixed 30-second clips.** Uniform, content-independent boundaries make clip identity stable
across pipeline versions. Shot-boundary segmentation would produce clips better aligned to content
but would make every clip ID version-dependent, breaking cached predictions on every change to the
detector.

### 5.3 Lessons Learned

1. **Separate inference from scoring.** The third notebook — scoring only, loads no models — was
   the highest-value structural decision in the project. Comparison tables rebuild in seconds
   without a GPU, and a missing cache degrades to zero coverage rather than crashing a run.
2. **Version the prompt, and check the version at load.** Prediction caches carry a
   `prompt_version`; mismatched caches are ignored. Without this, a prompt change silently mixes
   incomparable results into one table — an error that produces plausible numbers and is almost
   undetectable afterwards.
3. **Record failures against identifiers.** Coverage tables that show what was actually scored are
   worth more than clean-looking means over unknown denominators.
4. **Decide what the metric cannot see, before running it.** Writing §4.2 of the paper before
   the experiments prevented the multi-label-accuracy trap: 0.87 looks strong until it is noticed
   that predicting nothing scores ≈ 0.85 over 34 labels.
5. **Underpowered experiments should be run anyway and labelled honestly.** The *n* = 5 robustness
   study produced the clearest mechanistic finding in the project (13-fold field-dependence). Its
   sample size is in the caption, and it still earns its place.

### 5.4 Evaluation of the Outcome

**Delivered.** A resumable, checkpointed, provenance-tracked pipeline; 626 clips at zero failures;
five fields per clip from heterogeneous families; explicit per-field status and agreement; four
experiments; a 7-model, 21,140-score benchmark; a read-only browser exposing the evidence.

**Not delivered.** Any validity measurement (structurally impossible without a human reference);
RQ2's agreement distribution **`[TO FILL]`**; adequately powered ablations; retrieval evaluation;
the fine-tuning the notebook's rules cell describes.

**Honest self-assessment.** The engineering is solid and the instrumentation is genuinely better
than the norm for this kind of project. The scientific claim is correspondingly narrow, and that
narrowness is a consequence of the no-annotation constraint rather than a failure of execution.
The most valuable single follow-up is small: a few hundred human-labelled clips would convert
every agreement number here into a validity measurement and settle the RQ4 visual-tag question,
which is currently the most interesting unresolved result in the project.

---

## 6. Responsible AI

### 6.1 Bias

The 34-label vocabulary was authored by one person for one corpus. It encodes a particular view of
what is worth recording about community life in Belfast in 2016 — it contains `protest`, `police`,
`politician` and `firefighter`, and what it omits is as consequential as what it includes, because
a concept outside the list cannot be expressed by any model in the system. Underlying models carry
their own web-scale training biases, which this project does not measure. **`[TO FILL: report tag
frequency across the corpus. A label that never fires, or one that fires on most clips, is
evidence about the vocabulary rather than about the footage.]`**

### 6.2 Privacy

The footage shows identifiable members of the public in public settings, recorded for broadcast.
Controls: no identity inference anywhere in the pipeline, and the hosted annotator is explicitly
prompted against it; people count published as an integer only, never demographic attributes; the
hosted API is optional and gated on licence and data-governance approval, with full local-only
operation supported; API keys never written to artefacts. **`[TO FILL: NVTV licence terms; QUB
ethics/data-governance reference; whether the reported run used the hosted API.]`**

### 6.3 Fairness

Whisper's accuracy varies by accent, and this corpus is predominantly Northern Irish English — a
distribution under-represented in training data relative to General American. Transcript quality is
therefore likely to be systematically lower here than published WER figures suggest, and *that
error is not random*: it will fall hardest on speakers with the strongest regional accents, who in
a community archive are often the community members the archive exists to represent. The project
does not measure this, which is a real gap rather than a formality. **`[TO FILL: if the SYNOPSES
folder contains any human transcript, compare WER on those clips against Whisper's published
English WER and report the difference.]`**

### 6.4 Transparency

Every published field carries its status, the models that supported it, the weights applied and
their provenance. Artefact headers identify the output as an automated multi-model silver
standard. The agreement score is documented as corroboration and never as a probability of
correctness — in the paper, in the notebook's rules cell, and in the browser.

### 6.5 Accountability and Human Oversight

The browser is read-only by design: it displays evidence and does not let a user endorse a value
in a way that would make automatic output look human-verified. The intended workflow is triage —
`needs_caution` records first — with a human cataloguer retaining the decision. No output of this
system should enter a public catalogue as verified without that step.

### 6.6 AI Assistance and Student Responsibility

**`[TO FILL: state which AI tools were used, for what — code scaffolding, debugging, drafting —
and confirm that all experimental design, execution, interpretation and the claims made are the
author's own and have been verified. Both exemplars carry this section; QUB requires it.]`**

---

## 7. Appendices

### Appendix A — Configuration

| Parameter | Value |
|---|---|
| `clip_seconds` / `minimum_final_clip_seconds` | 30.0 / 2.0 |
| `clip_workers` × `ffmpeg_threads_per_worker` | 2 × 1 |
| `frame_sampling_policy` | `scene_aware` |
| `frame_fractions` (fallback) | 0.20, 0.50, 0.80 |
| `max_scene_frames` | 5 |
| `scene_adaptive_threshold` / `scene_min_length` | 3.0 / 0.6 s |
| `tesseract_min_word_confidence` | 60.0 |
| `easyocr_min_confidence` | 0.50 |
| `ocr_within_frame_similarity` | 0.88 |
| `ocr_temporal_similarity` | 0.82 |
| `ocr_min_frame_occurrences` | 2 |
| `ocr_cross_engine_similarity` | 0.80 |
| `ocr_probe_interval_seconds` / `max_frames` / `edge_offset` | 2.5 s / 12 / 0.5 s |
| `tag_top_k` | 5 |
| `calibration_fraction` | 0.20 |
| `gemini_max_frames` / `gemini_model` | 5 / `gemini-3.6-flash` |
| `ablation_max_clips` / `robustness_max_clips` | 8 / 5 |
| Agreement tiers | high ≥ 0.75, moderate ≥ 0.50, low < 0.50 |
| Benchmark frames / decoding | 4 / greedy (`do_sample=False`) |
| Benchmark `max_new_tokens` | 700 Instruct, 1400 Thinking |

### Appendix B — Visual-Tag Vocabulary (34 labels)

`news studio`, `interview`, `press conference`, `public meeting`, `panel discussion`,
`person speaking`, `crowd of people`, `protest`, `indoor scene`, `outdoor scene`, `city street`,
`building exterior`, `office`, `stage`, `podium`, `fire engine`, `emergency services`, `police`,
`hospital`, `school`, `graphic or title card`, `text on screen`, `logo`, `presentation slide`,
`landscape`, `rural countryside`, `vehicle`, `road`, `sign or banner`, `audience`, `reporter`,
`politician`, `firefighter`, `uniform`.

### Appendix C — Source Programmes

47 programmes, NVTV, 2016. Subjects span festival launches, a fire-service industrial dispute,
protest and parade footage, blue-plaque unveilings, political panels, arts and community-health
programming, education and youth forums. Clips per programme range 10–22.
**`[TO FILL: full table — title, duration, clip count, split.]`**

### Appendix D — Full Result Tables

- **D.1** Frame-sampling ablation — paper Table III (*n* = 8).
- **D.2** Perturbation robustness — paper Table IV (*n* = 5).
- **D.3** Hosted-annotator ablation — paper Table V (*n* = 626).
- **D.4** VLM benchmark — paper Table VI (*n* = 615, 21,140 scores).
- **D.5** Per-field agreement distribution — **`[TO FILL]`**.
- **D.6** Benchmark coverage — 615/615 all fields except people count 560/615, all seven models.
- **D.7** Transcript-field breakdown, Qwen3-VL-4B-Instruct — mean 0.00014347; 613/615 empty
  predictions; 1 non-zero score; maximum 0.0882.

### Appendix E — Qualitative Spot-Checks

**`[TO FILL: 5–8 clips, each with the reference metadata alongside every model's prediction, and
one sentence on what the example shows. Include at least one clip where the hosted annotator
changed the visual tags, since that is the paper's most consequential unresolved result — the
qualitative evidence is what a reader will want when the quantitative evidence cannot settle it.
Section 12 of `02_vlm_benchmark_run.ipynb` produces these.]`**

### Appendix F — Reproduction

```
notebooks/01_metadata_pipeline.ipynb          # clips, metadata, experiments, browser
notebooks/02_vlm_benchmark_run.ipynb          # seven VLMs, checkpointed, resumable
notebooks/03_vlm_benchmark_comparison.ipynb   # scoring and tables only, no GPU needed
```

Run 01 top to bottom on a GPU runtime with the Drive layout in its header cell; run 02 on a GPU
node; run 03 anywhere. All three are resumable and skip completed work.
