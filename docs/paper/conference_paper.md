# Reliability-Aware Multi-Model Metadata Generation for Archival Community Television

> **Draft for the IEEE conference template** (`docs/references/ieee-conference-template-letter.docx`).
> Style names to apply are given in `[square brackets]` at each heading. Every number below is
> taken from the executed notebooks in `notebooks/`; anything not yet measured is marked
> **`[TO FILL]`** rather than estimated. Structure follows the exemplar submissions in
> `docs/references/exemplars/` — see `docs/WRITING_GUIDE.md`.

---

**Title** `[papertitle]`
Reliability-Aware Multi-Model Metadata Generation for Archival Community Television

**Authors** `[Author]`
Saurav Vijay · School of Electronics, Electrical Engineering and Computer Science · Queen's University Belfast

---

## Abstract `[Abstract]`

Community-television archives hold thousands of hours of programming with no segment-level
index, so nothing inside a programme is searchable. Automatic description is the obvious remedy,
but hand annotation was excluded for this corpus, and single-model pipelines publish output with
no indication of which fields can be trusted. This work builds a metadata pipeline for the NVTV
public archive that publishes corroboration between independent model families alongside the
metadata itself. Forty-seven archival programmes were segmented into 626 fixed 30-second clips
and annotated across five fields by heterogeneous pretrained families — Whisper-small and
Whisper-turbo for speech; Tesseract and EasyOCR for on-screen text; KeyBERT, YAKE and TF-IDF for
keywords; CLIP ViT-B/32 and ViT-L/14 for a 34-label controlled vocabulary; BLIP-VQA, ViLT-VQA and
DETR for people count — with a hosted Gemini annotator as an optional additional family. Every
field carries an evidence status, its supporting models, and an agreement score that excludes
self-similarity. Scene-aware sampling recovered 23.0 on-screen-text items per clip against 14.5
for the centre frame yet agreed with that baseline only 0.53 of the time; under blur, visual-tag
stability held at 0.96 while text stability fell to 0.07; the hosted annotator rewrote 49.0% of
visual-tag sets while agreeing with the local consensus 0.42 of the time, and changed 0.0% of
on-screen text, which strict dual-engine consensus vetoes by design. Across seven open-weight
vision-language models — Qwen3-VL 2B/4B/8B in Instruct and Thinking variants, InternVL3-2B and
-8B — and 21,489 scores, InternVL3-2B led three of five fields and every model scored at or near
zero on transcript. Reliability is a per-field property, and corroboration is reported as
corroboration, not correctness.

**Keywords** `[Keywords]` — video archives; multimodal metadata; model consensus; vision-language
models; silver standard; reliability estimation.

---

## I. INTRODUCTION `[Heading1]`

### A. Problem and Context `[Heading2]`

Northern Visions Television (NVTV) is a Belfast community broadcaster whose public archive
holds long-form programming — launches, protests, panel discussions, public meetings, blue-plaque
unveilings — from across the city's civic life. The corpus used here spans 47 programmes recorded
during 2016. Each programme carries a title and, in some cases, a short synopsis; nothing
describes what happens *inside* it. An archivist looking for the moment a particular speaker
addresses a particular topic must watch the programme.

Segment-level description is what makes such a collection usable, and generating it by hand does
not scale. Foundation models trained on web-scale data can now caption frames, transcribe speech,
read on-screen text and assign visual labels without any domain-specific training, which makes
automatic description of an archive like this technically feasible for the first time.

Feasible is not the same as trustworthy. A pipeline that emits a caption and a label set for
every clip emits them with uniform confidence regardless of whether three independent models
concurred or one model guessed. For an archive, this matters more than average accuracy: an
archivist can work with a field marked uncertain, but a confidently wrong field silently corrupts
the catalogue. The project requirement additionally excluded manual annotation of the NVTV
material, removing the conventional route to a gold standard and forcing the question of what a
generated catalogue can honestly claim about itself.

### B. Research Aim and Objectives `[Heading2]`

**Aim.** To produce segment-level descriptive metadata for an archival community-television
corpus using only pretrained models, and to attach to every published field an explicit,
auditable estimate of how strongly independent evidence sources corroborate it.

**Objectives.**

1. Segment 47 long-form programmes into fixed 30-second clips with frame-accurate, resumable,
   verifiable clip creation.
2. Generate five metadata fields per clip — transcript, on-screen text, keywords, visual tags,
   people count — from at least two independent model families per field.
3. Define and implement an evidence-status and agreement-scoring scheme that excludes
   self-similarity, refuses to promote empty output, and records which models supported each
   published value.
4. Quantify the effect of temporal frame sampling on coverage and stability under a
   pre-registered ablation on a frozen calibration subset.
5. Quantify robustness to realistic visual degradation (blur, brightness loss, JPEG compression).
6. Quantify what an optional hosted multimodal annotator adds, separating *agreement with* the
   local consensus from *change to* the published output.
7. Benchmark seven open-weight vision-language models against the pipeline's consensus on the
   same clips and fields, under a protocol held constant across models.

### C. Scope and Boundaries `[Heading2]`

The following are deliberately outside this work, and results should not be read as claims about
them.

- **No human gold standard for the NVTV material.** The project requirement excluded manual
  annotation of this corpus. Every number reported here measures either internal corroboration
  between automatic sources or agreement between an external model and that consensus. None of
  them measures factual correctness.
- **No training of the metadata models.** Every model is used zero-shot at its published
  checkpoint. No fine-tuning contributes to any result reported in this paper.
- **Fixed 30-second segmentation.** Clip boundaries are uniform and content-independent; shot
  boundaries are used only to choose *frames within* a clip, never to choose clip boundaries.
- **English-language speech.** Whisper performs language identification but no non-English
  branch is evaluated.
- **Closed visual vocabulary.** Visual tags are restricted to 34 labels chosen for this corpus.
  A concept outside that list cannot be expressed, by any model, by construction.
- **No temporal localisation within a clip.** Every field is published at clip granularity: the
  record states that a caption, a speaker or an activity is present in a given 30 seconds, never
  where inside it. The underlying timing is computed and retained in the prediction records —
  Whisper segments carry start and end times, and each accepted on-screen-text string carries the
  frame indices it was detected in — but the published five-field record does not expose it.
- **No speaker attribution.** Whisper produces one undifferentiated transcript per clip. No
  diarisation, speaker counting or voice identification is attempted, so on the panel discussions
  and interviews that make up much of this corpus the record cannot say who said what.

### D. Research Questions `[Heading2]`

**RQ1.** How does scene-aware temporal sampling affect metadata coverage and cross-frame
stability relative to centre-frame and fixed three-frame sampling?

**RQ2.** How strongly do independent evidence sources agree, field by field, once self-similarity
and empty-output inflation are removed?

**RQ3.** How robust is the generated metadata to realistic visual degradation, and is robustness
uniform across fields?

**RQ4.** How often does a hosted multimodal annotator corroborate the local model families, and
how often does adding it change the selected output?

**RQ5.** How do current open-weight vision-language models compare against the pipeline's
consensus on the same clips and fields, and does model scale predict agreement?

### E. Methodology Overview and Paper Organisation `[Heading2]`

Section II positions the work against archival video indexing, weak supervision and
vision-language description. Section III describes the corpus, the evidence sources, the sampling
and consensus rules, and the reproducibility and ethical controls. Section IV reports the
environment, the metrics and their limits, and one subsection per research question, closing with
a comparison of anticipated against actual results. Section V interprets the findings and states
limitations; Section VI concludes.

---

## II. RELATED WORK `[Heading1]`

### A. Access to Archival and Broadcast Video `[Heading2]`

Segment-level indexing of broadcast material is a long-standing problem, and the evaluation
infrastructure built around TRECVid [1] established both the task shapes — shot boundary
detection, semantic concept annotation, ad-hoc video search — and the expectation that systems be
compared against human-annotated references. That expectation is precisely what a working archive
usually cannot satisfy: annotation budgets are the binding constraint, and the collections most in
need of description are the ones least likely to receive it. Work on cultural-heritage and
community archives has consequently leaned on automatic description, generally reporting
system output without a companion estimate of per-field reliability. **`[TO FILL: 2–3 citations
specific to cultural-heritage or community-archive AV description — search "audiovisual archive
automatic metadata" in the QUB library and cite the closest two.]`**

### B. Foundation Models as Zero-Shot Annotators `[Heading2]`

Contrastive image–text pretraining [2] made open-vocabulary visual labelling possible without
task-specific training, and the same shift reached speech with large-scale weakly supervised
recognition [3] and vision-language question answering with BLIP [4] and ViLT [5]. End-to-end
set-prediction detection [6] supplies a third, architecturally unrelated route to counting people
in a frame. The property this work exploits is not any single model's accuracy but the
*heterogeneity* of their failure modes: CLIP's ranking errors, a VQA model's answer-prior bias and
a detector's missed small objects are not the same errors, so concurrence between them carries
information that concurrence between two checkpoints of one architecture does not.

### C. Consensus, Weak Supervision and Silver Standards `[Heading2]`

Treating multiple noisy automatic sources as votes to be combined rather than outputs to be chosen
between is the core idea of programmatic weak supervision [7], where labelling functions of
unknown accuracy are aggregated into probabilistic labels. The corpus-linguistics tradition
supplies the complementary framing: inter-annotator agreement statistics [8] quantify how much a
set of annotations can be relied upon, independently of whether any annotator is correct. This
work applies that framing to machine annotators, with one deliberate restriction — agreement is
reported as corroboration and never reinterpreted as a calibrated probability of correctness.

### D. Vision-Language Models for Video Description `[Heading2]`

Recent open-weight multimodal models — the Qwen3-VL family [9] and InternVL3 [10] — accept
interleaved image sequences and emit schema-constrained text, making them plausible single-model
replacements for a multi-component pipeline. Their known failure mode is object hallucination
[11]: fluent output describing content that is not present. Reasoning-trace ("Thinking") variants
are marketed as mitigating this through deliberation. Neither claim has, to our knowledge, been
tested on archival community-television footage, which differs from the web video these models
were trained on in resolution, framing, lighting and subject matter.

### E. Gap `[Heading2]`

Three gaps meet in this work. Automatic archival description is rarely accompanied by per-field
reliability signals. Multi-model consensus is well developed for classification labels but is
rarely applied to the heterogeneous field types — free text, ranked sets, closed-vocabulary
multi-label, integers — that a real catalogue record contains. And where no human reference can be
collected, the literature offers little guidance on what may legitimately be reported. This paper
addresses all three, and treats the resulting limits on what can be claimed as part of the result
rather than as a caveat to it.

---

## III. METHOD `[Heading1]`

### A. Corpus and Clip Construction `[Heading2]`

The corpus is 47 NVTV programmes from 2016, supplied as MP4 with optional matching synopsis text
files. Subjects include a children's festival launch, a fire-service industrial dispute, protest
and parade footage, blue-plaque unveilings, political panel discussions, arts programming and
community-health features — a spread that exercises studio, street and event conditions.

Each programme is segmented into fixed 30-second clips with FFmpeg, discarding any final fragment
shorter than 2.0 s, producing **626 clips with zero failures**. Clip jobs run in a bounded thread
pool (2 workers × 1 FFmpeg thread on a 12-CPU runtime); each worker writes to a unique partial
file, validates the resulting duration and atomically publishes it, so completed clips are reused
on re-runs and task completion order cannot perturb the dataset. The manifest is sorted
deterministically before splitting.

Sources — not clips — are split, 9 programmes (123 clips) to calibration and 38 (503 clips) to
evaluation, so no programme contributes clips to both sides. The split is a seeded permutation of
the sorted source identifiers at a configured calibration fraction of 0.20, and is therefore
deterministic across runs. The calibration split is the only material inspected while
choosing sampling policy and thresholds.

TABLE I. `[tablehead]` CORPUS AND SEGMENTATION

| Property | Value |
|---|---|
| Source programmes | 47 |
| Clip length | 30.0 s (final fragment ≥ 2.0 s retained) |
| Clips generated | 626 |
| Clip creation failures | 0 |
| Calibration / evaluation programmes | 9 / 38 |
| Calibration / evaluation clips | 123 / 503 (19.6% / 80.4%) |
| Clips scored in the VLM benchmark | 626 |
| Clips per programme | 8 – 22 (mean 13.3, median 12, SD 3.1) |
| Total clip duration | ≈ 5.2 h (upper bound) |

> **`[TO FILL: exact corpus duration. 626 × 30 s = 5.22 h is an upper bound, because the final
> fragment of each of the 47 programmes may be shorter than 30 s (a 2.0 s floor is retained), so
> the true figure lies between 4.85 h and 5.22 h. Sum the ffprobe durations of the source files
> for the exact value.]`**

### B. Fields and Evidence Sources `[Heading2]`

Five fields are published per clip, each from at least two independent families.

TABLE II. `[tablehead]` EVIDENCE SOURCES AND SELECTION RULES

| Field | Evidence families | Selection rule |
|---|---|---|
| Transcript | Whisper-small, Whisper-turbo | Turbo deterministic output published; inter-model WER converted to agreement as 1 − min(WER, 1) |
| On-screen text | Tesseract, EasyOCR | Publish only temporally persistent fuzzy matches supported by **both** engines |
| Keywords | KeyBERT (MiniLM), YAKE, TF-IDF | Weighted ranked-set consensus, top *k* = 5 |
| Visual tags | CLIP ViT-B/32, CLIP ViT-L/14, (Gemini) | Closed 34-label vocabulary; ≥ 2 families must support a published tag |
| People count | BLIP-VQA, ViLT-VQA, DETR, (Gemini) | One numeric vote per family; weighted mode with median tie-break |

Two structural rules apply throughout. Each *family* receives equal total weight after
within-family aggregation, so sampling more frames cannot manufacture additional independent
voters. And self-similarity is excluded from every agreement computation: a value is never
corroborated by the source that produced it.

### C. Scene-Aware Temporal Sampling `[Heading2]`

The production policy detects shot boundaries with an adaptive rolling-content detector
(threshold 3.0, minimum scene length 0.6 s) [12], samples scene midpoints, always includes the
temporal centre, and caps the result at 5 scene frames. Where detection fails or yields too few
scenes, fixed frames at 20/50/80% of clip duration are added. On-screen text uses a separate,
denser probe — every 2.5 s to a maximum of 12 frames, offset 0.5 s from the clip edges — because
captions and lower-thirds appear and disappear on a timescale shorter than the visual sampling
interval.

### D. Strict Dual-Engine OCR `[Heading2]`

On-screen text is the only field with a hard veto, because a hallucinated name or headline in a
catalogue record is the most damaging error available to this system. A candidate string is
published only if it (i) exceeds per-engine confidence (Tesseract word confidence ≥ 60, EasyOCR
≥ 0.50), (ii) persists across at least 2 sampled frames at fuzzy similarity ≥ 0.82, and
(iii) is matched across engines at similarity ≥ 0.80. A candidate satisfying none of these routes
yields an empty field or a `conflict` status. No other source — including the hosted annotator —
can override this decision.

### E. Evidence Status and Agreement Scoring `[Heading2]`

Every field carries a status drawn from `observed`, `not_detected`, `not_applicable`, `conflict`
or `error`, together with the supporting model list, the per-source weights and their provenance.
An agreement score is computed only when at least two non-empty sources exist; otherwise the score
is `null` and `needs_caution` is set. Scores are binned as **high** (≥ 0.75), **moderate**
(≥ 0.50) and **low** (< 0.50), with `not_scored` for the single-source case. Set-valued fields use
mean pairwise set-F1 across sources, transcripts use 1 − min(WER, 1), and numeric fields use
per-family voting.

Empty output is never promoted: a field on which every source agrees that nothing is present is
recorded as `not_detected`, never as high agreement. This one rule prevents the degenerate
outcome — a pipeline that detects nothing and reports perfect internal agreement — that would
otherwise dominate a corpus with many low-text, low-motion clips.

### F. Optional Hosted Multimodal Annotator `[Heading2]`

A hosted multimodal model (`gemini-3.6-flash`, ≤ 5 frames per clip, schema-constrained JSON)
contributes **one family vote** to visual tags and people count. Its on-screen text is retained as
a diagnostic only. The prompt forbids identity inference, inference of off-screen context, and
completion of unreadable text; requests are sequential, rate-limited, retried with bounded
exponential backoff, cached and provenance-tracked, and the API key is never written to an
artefact. Its role is deliberately bounded: an additional voter, never an authority.

### G. Reproducibility Controls `[Heading2]`

Seeds are fixed; model revisions are resolved and recorded as commit hashes; the manifest ordering
is deterministic; per-clip checkpointing makes every stage resumable; failures are recorded
against their clip identifier rather than suppressed; and all artefacts are written atomically via
a partial-file-and-rename discipline so an interrupted run cannot leave a truncated JSON. GPU
inference on shared models is serialised while CPU OCR runs bounded-parallel, preventing CUDA
contention and non-thread-safe model use.

### H. Ethical Considerations `[Heading2]`

The footage shows identifiable members of the public in public settings, recorded for broadcast.
Four controls follow from this. The published record contains no identity inference: the pipeline
does not attempt to name individuals, and the hosted annotator is explicitly instructed not to.
People count is published as an integer, never as demographic attributes. Sending frames to a
hosted API is a disclosure of archive content to a third party and is gated on the licence and on
institutional data-governance approval, with local-only operation fully supported. And the
34-label vocabulary was authored by one person for one corpus: it encodes a particular view of
what is worth recording about a community, which is a limitation of the catalogue it produces, not
a neutral technical detail.

> **`[TO FILL: NVTV licence terms and the QUB ethics/data-governance reference under which the
> hosted-API calls were made. State the approval explicitly or state that only local models were
> used for the final reported run.]`**

---

## IV. EXPERIMENTATION AND RESULTS `[Heading1]`

### A. Hardware and Software Environment `[Heading2]`

The pipeline ran on Google Colab with an **NVIDIA A100-SXM4-40GB**, 12 CPUs, Python 3.13.15 and
PyTorch 2.11.0+cu128. The VLM benchmark ran on the Kelvin2 HPC facility on a **single A100 MIG
`2g.20gb` slice**, which is the binding constraint on that experiment: it sets the 4-frame budget
and forces int4 quantisation for the 8B models. Package versions are pinned
(transformers 4.50.3, openai-whisper 20250625, easyocr 1.7.2, scenedetect 0.7.1, jiwer 4.0.0,
rouge-score 0.1.2); full manifests are in the supporting materials.

### B. Evaluation Metrics and Their Limits `[Heading2]`

**Agreement score** — mean pairwise set-F1 (set fields), 1 − min(WER, 1) (transcript), or weighted
family voting (numeric). *Limit:* corroboration, not correctness. Models sharing a training
distribution can agree while both being wrong, and the two CLIP variants are not fully
independent.

**Coverage** — items published per clip. *Limit:* rewards recall with no precision counterpart; a
policy that emits more OCR strings scores higher whether or not the extra strings are real.

**Stability** — set-F1 or exact match between a perturbed or resampled run and its baseline.
*Limit:* a consistently wrong system is perfectly stable.

**ROUGE-L recall** (benchmark, free-text fields) — how much of the reference content the model
recovers. *Limit:* no precision term, so verbosity is not penalised; and an honestly empty
prediction scores 0.0 against a non-empty reference, exactly like a confident wrong one.

**Multi-label accuracy** (benchmark, visual tags) — Hamming accuracy over the 34-label vocabulary.
*Limit:* with at most 5 labels selected from 34, predicting nothing already scores ≈ 0.85. Absolute
values in this column are not meaningful in isolation; only differences between models are.

The reference for the benchmark is the pipeline's own consensus, not human judgement. Every
benchmark number is therefore **agreement between automatic systems**.

### C. RQ1: Frame-Sampling Ablation `[Heading2]`

Three policies were compared on the frozen 8-clip calibration subset. The experiment measures
coverage, change from the centre-frame baseline and cross-frame stability; it does not measure
accuracy.

TABLE III. `[tablehead]` FRAME-SAMPLING ABLATION (CALIBRATION SUBSET, *n* = 8)

| Policy | Mean frames | OCR items / clip | OCR set-F1 vs centre | Tag set-F1 vs centre | People-count stability | Mean stability |
|---|---|---|---|---|---|---|
| Centre frame | 1.000 | 14.5 | 1.0000 | 1.000 | 1.0000 | 1.0000 |
| Fixed 20/50/80% | 3.000 | 3.0 | 0.3027 | 0.650 | 0.6879 | 0.5469 |
| **Scene-aware** | 4.375 | **23.0** | 0.3115 | 0.675 | 0.6089 | 0.5318 |

Set-F1 columns are symmetric set overlap against the centre-frame baseline; people-count
stability is exp(−|Δ|), so 1.0 is an identical count and 0.368 is a disagreement of one. The
centre-frame row is 1.0 throughout by construction.

The OCR counts are **not like-for-like, and the reason is the finding.** `aggregate_temporal_ocr`
sets its persistence threshold from the number of frames it is given: one frame requires one
occurrence, so the centre-frame policy publishes every raw OCR line unfiltered, which is what
produces 14.5. Fixed three-frame sampling requires two occurrences out of three widely spaced
frames, which almost nothing survives — 3.0 items. The scene-aware policy draws its text from the
dense probe instead, up to 12 frames at 2.5 s spacing, so the same two-occurrence rule has twelve
chances to be satisfied and the sampling is fine enough to catch short-lived lower-thirds: 23.0
items. **Against the only like-for-like comparison — both filtered at two occurrences —
scene-aware publishes roughly eight times the text of fixed three-frame sampling.** The
centre-frame figure is higher than fixed three's only because no filter is applied to it, and
should not be read as coverage.

Two further findings cut against a simple "more frames is better" reading. Scene-aware agrees with
the centre baseline slightly more closely than fixed three-frame does on both OCR (0.3115 vs
0.3027) and tags (0.675 vs 0.650), despite sampling more frames — so the added frames are not
simply pulling the output away from the baseline. But mean stability is *lowest* for scene-aware
(0.5318 against 0.5469), driven by people count (0.6089 against 0.6879): looking at more of the
clip finds more people than the centre frame shows, and changes the published count accordingly.
Coverage and agreement-with-baseline trade directly, and choosing scene-aware buys the former at
the cost of the latter.

The subset is 8 clips. This is an underpowered ablation and no significance is claimed; it was
sized to permit policy selection without inspecting evaluation material, which it does.

### D. RQ2: Agreement Structure Across Fields `[Heading2]`

> **`[TO FILL — this subsection has no numbers yet.]` Re-run Section 14 of
> `notebooks/01_metadata_pipeline.ipynb` and capture the per-field agreement report. Report, for
> each of the five fields over all 626 clips: the distribution over `observed` / `not_detected` /
> `not_applicable` / `conflict` / `error`; the distribution over agreement tiers
> (`high` ≥ 0.75, `moderate` ≥ 0.50, `low` < 0.50, `not_scored`); the mean agreement score; and
> the proportion with `needs_caution = true`. This is the central RQ2 table and the paper cannot
> be submitted without it.**

Two properties of this table are predictable from the design and should be stated when it is
produced. On-screen text will show an elevated `not_detected` and `conflict` rate, because the
dual-engine veto in III-D is deliberately conservative. And single-source fields will appear as
`not_scored` rather than as low agreement, because one source cannot establish corroboration.

### E. RQ3: Perturbation Robustness `[Heading2]`

Five calibration clips were degraded and the visual verifier re-run against its original
centre-frame evidence.

TABLE IV. `[tablehead]` STABILITY UNDER VISUAL DEGRADATION (*n* = 5)

| Perturbation | OCR stability | Tag stability | People-count stability | Mean |
|---|---|---|---|---|
| Gaussian blur | **0.0714** | **0.96** | 0.5742 | 0.5760 |
| JPEG quality 25 | 0.1111 | 0.80 | 0.6207 | 0.5421 |
| Low brightness | 0.3000 | 0.84 | 0.5742 | 0.6303 |

Robustness is not a property of the pipeline; it is a property of each field. Under blur, visual
tagging is almost unaffected (0.96) while OCR retains 7% of its output — a 13-fold difference in
sensitivity to the same perturbation. This is mechanistically unsurprising: CLIP scores global
scene semantics that survive low-pass filtering, whereas character recognition depends on
high-frequency detail that blur removes and the dual-engine consensus rule then vetoes whatever
survives. People count sits between the two (0.57–0.62), consistent with detection of person-sized
regions degrading gracefully.

The practical consequence is a deployment rule: **on degraded source material, the scene-level
fields remain usable and the text field should be treated as absent rather than as evidence of
absence.** The pipeline's own `not_detected` status cannot distinguish "no text present" from "text
present but unreadable", and this experiment quantifies how often that distinction is being lost.

*n* = 5 clips. Directionally clear, statistically weak.

### F. RQ4: Hosted-Annotator Contribution Ablation `[Heading2]`

Two distinct quantities are separated here: how often the hosted annotator *agrees with* the
local-only consensus, and how often adding it *changes* the published output. Neither is accuracy.

TABLE V. `[tablehead]` HOSTED-ANNOTATOR ABLATION (*n* = 626)

| Field | Candidate coverage | Exact output-change rate | Mean candidate vs local agreement | Local vs augmented stability |
|---|---|---|---|---|
| On-screen text | 0.3850 | **0.0000** | 0.5468 | 1.0000 |
| People count | 0.6054 | 0.0176 | 0.8445 | 0.9883 |
| Visual tags | 1.0000 | **0.4904** | 0.4194 | 0.9029 |

Three results. **On-screen text: coverage 0.385, change rate exactly 0.0.** The annotator proposed
text on 38.5% of clips and changed the published field on none of them — the dual-engine OCR veto
of III-D working exactly as specified, verified empirically rather than assumed. **People count:
high agreement (0.8445), negligible change (1.8%).** Four families converge on integer counts, and
the hosted vote is nearly always redundant. **Visual tags: the annotator disagrees with the local
consensus more often than it agrees (0.4194) yet changes the published tag set on 49.0% of clips.**

That last row is the important one, and it is uncomfortable. A source that agrees with the
existing consensus less than half the time is rewriting half of all published tag sets. Under the
equal-family-weight scheme, a third voter that systematically differs from two correlated voters —
CLIP ViT-B/32 and ViT-L/14 share an architecture and training objective — will break ties in its
own favour at scale. Whether that is a correction or a corruption **cannot be determined from
these numbers**, because no independent reference exists for this corpus. What can be said is that
the equal-weight assumption is doing more work on visual tags than anywhere else in the system,
and that a deployment which cannot tolerate that should run local-only, which the design permits.

### G. RQ5: Open-Weight VLM Benchmark `[Heading2]`

Seven models were run zero-shot over all 626 clips under a protocol held constant across models:
4 uniformly sampled frames, identical prompt, greedy decoding, the same 34-label vocabulary,
producing **21,489 (model, clip, field) scores**. Thinking variants received a larger token budget
(1400 vs 700) to accommodate their reasoning trace, and both 8B models ran int4-quantised.

TABLE VI. `[tablehead]` VLM AGREEMENT WITH THE PIPELINE CONSENSUS (*n* = 626)

| Model | On-screen text (R-L) | Keywords (R-L) | Visual tags (acc.) | People count (acc.) | Transcript (R-L) |
|---|---|---|---|---|---|
| Qwen3-VL-2B-Instruct | 0.383 | 0.039 | 0.871 | 0.233 | **0.034** |
| Qwen3-VL-2B-Thinking | 0.384 | 0.028 | 0.874 | 0.323 | 0.018 |
| Qwen3-VL-4B-Instruct | 0.456 | 0.030 | 0.880 | 0.241 | 0.000 |
| Qwen3-VL-4B-Thinking | 0.389 | **0.040** | 0.873 | 0.315 | 0.019 |
| Qwen3-VL-8B-Instruct † | 0.431 | 0.036 | 0.876 | 0.232 | 0.000 |
| **InternVL3-2B** | **0.544** | 0.031 | **0.890** | **0.417** | 0.000 |
| InternVL3-8B † | 0.416 | 0.027 | 0.883 | 0.366 | 0.013 |

† int4-quantised; not on equal footing with the bf16/fp16 models. Coverage is 626/626 clips on the
free-text and tag fields for five of seven models (Qwen3-VL-2B-Instruct 625, -2B-Thinking 624,
where output could not be parsed as JSON) and 566–568/626 on people count, where the reference
count could not be parsed.

**Scale does not predict agreement.** The smallest model in the study, InternVL3-2B, leads three of
five fields — on-screen text (0.544, 19% above the best Qwen at 0.456), visual tags (0.890) and
people count (0.417, 29% above the best Qwen at 0.323) — and beats InternVL3-8B, its own larger
sibling, on all three. The 8B Qwen does not lead any field. Quantisation confounds the two 8B
results and they should not be used to argue that scale *hurts*; the defensible claim is narrower
and still useful: **at this task, on this corpus, a 2B model was sufficient, and paying for 8B
bought nothing measurable.**

**Thinking variants do not dominate their Instruct siblings.** At 2B, Thinking is level on
on-screen text (0.384 vs 0.383) and tags (0.874 vs 0.871) but markedly ahead on people count
(0.323 vs 0.233); at 4B it is behind on on-screen text (0.389 vs 0.456) and tags
(0.873 vs 0.880) and ahead on people count (0.315 vs 0.241). Deliberation helps the field
requiring enumeration and does not help the perceptual fields. A further asymmetry must be
disclosed: Thinking models alone receive a forced-conclusion retry when the first pass exhausts
its budget without emitting JSON. This recovers data rather than altering answers, but it is not
an identical protocol, and it is the two Thinking-family models that nonetheless lost clips to
parse failure.

**Transcript is at or near zero for every model (0.034 to 0.000), as predicted.** None of these
models accepts audio, so the field measures how much speech content is recoverable from vision
alone. The answer is: essentially none. Three models — InternVL3-2B, Qwen3-VL-4B-Instruct and
Qwen3-VL-8B-Instruct — score exactly 0.000, returning an empty string rather than inventing
dialogue; the qualitative spot-checks confirm this is abstention, not failure to respond. A recall
metric cannot distinguish an honest abstention from a wrong answer, so both score 0.0. This is a
disclosed design decision and a quantified finding: speech is the one field in this pipeline that
a vision-only model cannot replace.

**Keywords are near zero (0.027–0.040) for a different and less interesting reason.** The
comparison is not like-for-like: reference keywords are extracted from the *transcript*, while
each model's keywords come from *frames*. The spot-checks make the mismatch concrete — against a
reference of `medication`, `population`, `Northern Ireland` the models returned `interview`,
`talk show format`, `studio set`. Both describe the clip correctly; they describe different
modalities of it. This column measures the same modality gap as the transcript column, indirectly,
and should not be read as a keyword-extraction result.

**The benchmark also exposes a false-negative cost in the pipeline's OCR veto.** On a clip whose
reference on-screen text was empty, all seven models independently read the station ident
*NVTV / BELFAST LOCAL TELEVISION*, with only single-character disagreements (`NVTW`, `NVTY`).
The text was present; the strict dual-engine rule of III-D rejected it. On a second clip the
reference held the fragment `TIVAL` while the models returned the full theatre poster — title,
author, director, dates, box-office number. In both cases ROUGE-L recall scores the models
*against* a reference that is less complete than they are. The veto buys precision on this field,
Table V confirms it is never overridden, and these examples put a visible price on it. Absent a
human reference the trade cannot be quantified, only demonstrated — which is itself an argument
for collecting one.

### H. Anticipated versus Actual Results `[Heading2]`

TABLE VII. `[tablehead]` ANTICIPATED VERSUS ACTUAL

| # | Anticipated | Actual | Verdict |
|---|---|---|---|
| RQ1 | More frames raise coverage and stability together | Coverage up (23.0 vs 14.5 items), stability **down** (0.5318 vs 1.0) | Partly refuted |
| RQ1 | Fixed three-frame sits between centre and scene-aware | Fixed three-frame is **worst** on OCR coverage (3.0) | Refuted |
| RQ3 | Degradation reduces all fields comparably | 13-fold spread: tags 0.96, OCR 0.07 under blur | Refuted |
| RQ4 | A third annotator mostly corroborates | Agrees 0.42 on tags yet changes 49.0% of them | Refuted |
| RQ4 | OCR veto holds | Change rate exactly 0.0000 | Confirmed |
| RQ5 | Larger models agree more with the consensus | InternVL3-2B leads 3 of 5 fields | Refuted |
| RQ5 | Thinking variants beat Instruct | Split by field; ahead only on people count | Partly refuted |
| RQ5 | Vision-only transcript will be near zero | 0.034 to 0.000; three models exactly 0.000 | Confirmed |

Six of eight anticipated outcomes were refuted or partly refuted. The two confirmed are the two
that follow deductively from the design (the OCR veto) or from the modality (transcript). Every
empirical expectation about scale, deliberation and frame budget was wrong.

---

## V. DISCUSSION `[Heading1]`

### A. Interpretation `[Heading2]`

The organising finding is that **reliability is a per-field property, not a system property**, and
that the mechanisms differ enough that a single confidence number for a clip would be actively
misleading. Blur destroys OCR (0.07) and leaves tagging intact (0.96) because the two depend on
different spatial frequencies. A third annotator is redundant for people count (0.8445 agreement,
1.8% change) and decisive for visual tags (0.4194 agreement, 49.0% change) because integer
counting has a narrow answer space that independent families converge on, while a 34-label
multi-label assignment has a combinatorially large one that they do not. A 2B model beats an 8B
model on on-screen text because reading a lower-third is a perceptual task with a short answer,
not a task where extra capacity has anything to contribute.

The RQ4 visual-tag result deserves to be stated as a genuine problem rather than a curiosity. The
equal-family-weight rule was chosen as the neutral default in the absence of measured reliability
— and it *is* neutral only if the families are equally reliable and mutually independent, which
two CLIP variants sharing an architecture are not. On the one field where that assumption is
stressed, adding a third, differently-trained family rewrites half the output. The design's own
provenance machinery makes this visible; it does not resolve it, and resolving it requires
exactly the independent reference this project could not collect.

The benchmark's near-zero transcript column is the cleanest result in the paper because it is the
one where the ground truth is not in doubt. Whisper hears speech; a vision-language model looking
at four frames cannot, and three of the seven abstain outright rather than guess. That is why this
pipeline is multi-component rather than a single prompt to a large multimodal model — which is, in
2026, the obvious alternative design and the one a reviewer will ask about.

The benchmark's least comfortable result runs the other way. Where the models and the pipeline
disagree on on-screen text, the spot-checks show the models are sometimes right and the reference
wrong — a station ident every model read and the veto discarded. The agreement score cannot see
this, because it measures corroboration among the pipeline's own sources and the veto removes the
candidate before any scoring happens. A conservative rule is still the right default for a field
where hallucination is unrecoverable, but its cost is real and, on this evidence, not small.

### B. Implications `[Heading2]`

For an archive, the deliverable is not a catalogue but a *triaged* catalogue: a record that
tells an archivist which fields two or more independent systems corroborated and which rest on a
single source. The read-only browser delivered with this work exposes exactly those five fields
with their evidence status, so a cataloguer's attention goes to the `needs_caution` records first.
That is a different and more honest product than a confident automatic catalogue of unknown
quality, and it is achievable with pretrained models and no annotation budget.

For practitioners choosing models, the results argue against defaulting to the largest checkpoint
that fits: a 2B model led three of five fields, and the compute saved is better spent on a second
*architecturally different* family, which is what produces the corroboration signal in the first
place.

### C. Limitations `[Heading2]`

1. **No human reference for NVTV.** Every reported number is agreement between automatic systems.
   No claim about factual correctness is made or supportable, and the RQ4 tag result specifically
   cannot be adjudicated without one.
2. **Underpowered experiments.** RQ1 uses 8 clips and RQ3 uses 5. Both are directionally clear and
   neither supports a significance claim.
3. **RQ2 is not yet reported.** The agreement distribution table is outstanding **`[TO FILL]`**.
4. **Correlated sources.** CLIP ViT-B/32 and ViT-L/14 share architecture and training objective;
   Whisper-small and -turbo share both. Agreement between them overstates independence, inflating
   scores on transcript and visual tags relative to fields whose sources are genuinely unrelated.
5. **Quantisation confound.** Both 8B benchmark models ran int4 while smaller models ran at full
   precision. The 8B rows are not on equal footing.
6. **Protocol asymmetry.** Thinking models receive a forced-conclusion retry that Instruct models
   do not.
7. **Benchmark frame budget.** 4 frames, not the pipeline's scene-aware policy, forced by the
   20 GB MIG slice — a hardware constraint, not a methodological choice.
8. **Closed vocabulary.** 34 labels authored by one person; multi-label accuracy over that
   vocabulary rewards sparse predictions, so absolute values in that column are not interpretable.
9. **Corpus scope.** 47 programmes from one broadcaster in one city in one year. Nothing here
   establishes generalisation to other archives.
10. **Single run.** Greedy decoding, one run per model, no variance estimate over seeds or prompt
    phrasings.
11. **Corroboration is blind to upstream error.** Keywords are extracted from the transcript, so
    an ASR failure propagates into them with every keyword source agreeing, because all three read
    the same faulty text. Section IV-G documents a clip where Whisper mis-identified the language
    on accented English and the resulting spurious tokens entered the published keyword field at
    full agreement. Any field derived from another field inherits its errors and reports them as
    corroborated; the design has no mechanism to detect this.

---

## VI. CONCLUSION AND FUTURE WORK `[Heading1]`

This work delivers a reliability-aware metadata pipeline for an archival community-television
corpus: 47 programmes segmented into 626 clips with zero failures, five fields per clip generated
by heterogeneous pretrained families, and every published value carrying an evidence status, its
supporting models and a self-similarity-free agreement score. Four experiments characterise it,
and the useful findings are mostly the ones that contradicted expectation — coverage and stability
trade against each other under scene-aware sampling (23.0 vs 14.5 OCR items, stability 0.53);
robustness is field-specific to a 13-fold degree (0.96 tags vs 0.07 OCR under blur); a third
annotator rewrites 49.0% of visual-tag sets while agreeing with the local consensus only 42% of
the time, and is vetoed on 100% of OCR decisions by design; and across seven open-weight
vision-language models and 21,489 scores, a 2B model leads three of five fields while every model
scores at or near zero on transcript, three of them abstaining outright.

**Future work.** (i) Collect a small human-annotated reference — a few hundred clips is enough —
which converts every agreement number here into a validity measurement and settles the RQ4 tag
question. (ii) Replace equal family weights with measured per-source reliability, for which the
provenance machinery is already in place. (iii) Add an audio-capable multimodal model to the
benchmark, so the transcript column tests a model that was given the information the task
requires. (iv) Scale the ablations past 8 and 5 clips. (v) Gate the ASR stage on Whisper's own
language-identification output, so that a mis-identified clip is flagged rather than propagated
into the transcript-derived keyword field. (vi) Test shot-boundary clip segmentation against the
fixed 30-second grid. (vii) Surface the sub-clip timing the pipeline already records — Whisper
segment boundaries and per-string OCR frame indices — in the published record, which needs an
export change rather than new inference and would let a user land on the second rather than the
half-minute. (viii) Add diarisation, which would let the transcript field carry speaker turns and
would give people count a second, audio-side source to corroborate against its four visual ones.

---

## REFERENCES `[references]`

> **`[TO FILL: verify every entry against the published record — volume, pages, DOI — before
> submission. Entries below are correct as to authorship, venue and year.]`**

[1] A. F. Smeaton, P. Over, and W. Kraaij, "Evaluation campaigns and TRECVid," in *Proc. 8th ACM
Int. Workshop on Multimedia Information Retrieval (MIR)*, 2006, pp. 321–330.

[2] A. Radford *et al.*, "Learning transferable visual models from natural language supervision,"
in *Proc. 38th Int. Conf. Machine Learning (ICML)*, 2021, pp. 8748–8763.

[3] A. Radford *et al.*, "Robust speech recognition via large-scale weak supervision," in *Proc.
40th Int. Conf. Machine Learning (ICML)*, 2023, pp. 28492–28518.

[4] J. Li, D. Li, C. Xiong, and S. Hoi, "BLIP: Bootstrapping language-image pre-training for
unified vision-language understanding and generation," in *Proc. 39th Int. Conf. Machine Learning
(ICML)*, 2022, pp. 12888–12900.

[5] W. Kim, B. Son, and I. Kim, "ViLT: Vision-and-language transformer without convolution or
region supervision," in *Proc. 38th Int. Conf. Machine Learning (ICML)*, 2021, pp. 5583–5594.

[6] N. Carion *et al.*, "End-to-end object detection with transformers," in *Proc. European Conf.
Computer Vision (ECCV)*, 2020, pp. 213–229.

[7] A. Ratner *et al.*, "Snorkel: Rapid training data creation with weak supervision," *Proc. VLDB
Endowment*, vol. 11, no. 3, pp. 269–282, 2017.

[8] R. Artstein and M. Poesio, "Inter-coder agreement for computational linguistics,"
*Computational Linguistics*, vol. 34, no. 4, pp. 555–596, 2008.

[9] Qwen Team, "Qwen3-VL technical report," 2025. **`[TO FILL: arXiv identifier]`**

[10] Z. Chen *et al.*, "InternVL3: Exploring advanced training and test-time recipes for
open-source multimodal models," 2025. **`[TO FILL: arXiv identifier]`**

[11] A. Rohrbach *et al.*, "Object hallucination in image captioning," in *Proc. Conf. Empirical
Methods in Natural Language Processing (EMNLP)*, 2018, pp. 4035–4045.

[12] B. Castellano, "PySceneDetect: Video scene cut detection and analysis tool," 2014–2025.
[Online]. Available: https://www.scenedetect.com

[13] C.-Y. Lin, "ROUGE: A package for automatic evaluation of summaries," in *Text Summarization
Branches Out*, ACL Workshop, 2004, pp. 74–81.

[14] R. Smith, "An overview of the Tesseract OCR engine," in *Proc. 9th Int. Conf. Document
Analysis and Recognition (ICDAR)*, 2007, pp. 629–633.

[15] N. Reimers and I. Gurevych, "Sentence-BERT: Sentence embeddings using Siamese BERT-networks,"
in *Proc. EMNLP-IJCNLP*, 2019, pp. 3982–3992.

[16] R. Campos *et al.*, "YAKE! Keyword extraction from single documents using multiple local
features," *Information Sciences*, vol. 509, pp. 257–289, 2020.

[17] M. Grootendorst, "KeyBERT: Minimal keyword extraction with BERT," 2020. [Online]. Available:
https://github.com/MaartenGr/KeyBERT

> **`[TO FILL: add 5–10 archival/cultural-heritage AV description references to Section II-A.]`**
