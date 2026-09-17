# Reliability-Aware Multi-Model Metadata Generation for Archival Community Television

**Title** `[papertitle]`
Reliability-Aware Multi-Model Metadata Generation for Archival Community Television

**Authors** `[Author]`
Saurav Vijay · School of Electronics, Electrical Engineering and Computer Science · Queen's University Belfast

---

## Abstract `[Abstract]`

Community-television archives hold thousands of hours of programming with no segment-level index,
and single-model pipelines publish output with no indication of which fields can be trusted. This
work builds a metadata pipeline for the NVTV public archive that publishes corroboration between
independent model families alongside the metadata. Forty-seven programmes were segmented into 626
fixed 30-second clips totalling 5.09 h and annotated across five fields by heterogeneous
pretrained families: Whisper-small/-turbo, Tesseract/EasyOCR, KeyBERT/YAKE/TF-IDF, CLIP ViT-B/32
and ViT-L/14 over a 34-label vocabulary, and BLIP-VQA/ViLT-VQA/DETR, plus an optional hosted
Gemini annotator. Every field carries an evidence status, its supporting models and an agreement
score excluding self-similarity. Agreement ranks fields by source independence rather than task
difficulty: 0.812 for the four-family people count against 0.173 for keywords, whose extractors
share one transcript, while on-screen text ends in conflict on 53.4% of clips and reaches high
agreement on none. Under blur, visual-tag stability holds at 0.96 while text stability falls to
0.07. The hosted annotator rewrites 49.0% of visual-tag sets while agreeing with the local
consensus 0.42 of the time, and changes 0.0% of on-screen text. Across seven open-weight
vision-language models — Qwen3-VL 2B/4B/8B Instruct and Thinking, InternVL3-2B and -8B — and
21,489 scores, InternVL3-2B leads three of five fields and every model scores at or near zero on
transcript. Reliability is a per-field property, and corroboration is reported as such.

**Keywords** `[Keywords]` — video archives; multimodal metadata; model consensus; vision-language
models; silver standard; reliability estimation.

---

## I. INTRODUCTION `[Heading1]`

### A. Problem and Context `[Heading2]`

Northern Visions Television (NVTV) is a Belfast community broadcaster whose public archive holds
long-form programming — launches, protests, panel discussions, blue-plaque unveilings — from
across the city's civic life. Each programme carries a title and sometimes a synopsis; nothing
describes what happens inside it, so an archivist seeking a moment must watch it.

Foundation models make automatic description feasible but not trustworthy: a pipeline emits its
output with uniform confidence whether three independent models concurred or one guessed. A field
marked uncertain can be worked with; a confidently wrong one silently corrupts the catalogue. The
project requirement additionally excluded manual annotation of this material, removing the
conventional route to a gold standard.

### B. Research Aim and Objectives `[Heading2]`

**Aim.** To produce segment-level metadata for an archival community-television corpus using only
pretrained models, attaching to every field an auditable estimate of how strongly independent
sources corroborate it. **Objectives.** Segment the corpus resumably; generate five fields per clip
from at least two independent families each; define an agreement scheme excluding self-similarity
that never promotes empty output; quantify the effect of frame sampling, degradation and a hosted
annotator; and benchmark seven vision-language models against the consensus.

### C. Scope and Boundaries `[Heading2]`

No human gold standard exists, so every number measures corroboration between automatic sources,
never correctness. No model is trained or fine-tuned. Clip boundaries are fixed and
content-independent — shot boundaries choose frames *within* a clip, never the clip itself. Only
English speech is evaluated, and visual tags are confined to 34 labels, so a concept outside that
list cannot be expressed. Fields are published at clip granularity, the underlying timing being
computed and retained but not exposed, and Whisper produces one undifferentiated transcript per
clip, so the record cannot say who said what.

### D. Research Questions `[Heading2]`

**RQ1.** How does scene-aware sampling affect coverage and stability relative to centre-frame and
fixed three-frame sampling? **RQ2.** How strongly do independent sources agree, field by field,
once self-similarity and empty-output inflation are removed? **RQ3.** Is robustness to visual
degradation uniform across fields? **RQ4.** How often does a hosted annotator corroborate the local
families, and how often does it change the output? **RQ5.** How do open-weight vision-language
models compare against the consensus, and does scale predict agreement?

---

## II. RELATED WORK `[Heading1]`

### A. Access to Archival and Broadcast Video `[Heading2]`

TRECVid [1] established both the task shapes and the expectation that systems be compared against
human-annotated references, which a working archive usually cannot satisfy. The German
Broadcasting Archive is the closest published analogue: Mühling *et al.* [2] applied shot-boundary
detection, concept classification, person and text recognition to roughly 34,000 hours of GDR
television, and VIVA [3] extended this to 91 archive-specific concepts; Pessanha and Akdag Salah
[4] survey the same shift in oral-history archives. These report **system-level** accuracy over an
evaluated concept set, and VIVA addresses unreliability by adding human review rather than by
attaching a reliability estimate to each record. The present work adds no reviewer, and publishes per
field how strongly independent sources corroborated the value. Three gaps meet here: archival
description rarely publishes per-field reliability, consensus methods are rarely applied to the
heterogeneous field types a catalogue record contains, and where no human reference exists little
guidance covers what may legitimately be reported.

### B. Foundation Models, Consensus and Vision-Language Models `[Heading2]`

Contrastive image–text pretraining [5] made open-vocabulary labelling possible without
task-specific training; weakly supervised recognition [6] did the same for speech, BLIP [7] and
ViLT [8] for visual question answering, and set-prediction detection [9] gives a third route to
counting people. What is exploited is not any model's accuracy but the heterogeneity of
their failure modes: CLIP's ranking errors, a VQA model's answer-prior bias and a detector's
missed small objects differ, so concurrence between them is informative in a way concurrence
between two checkpoints of one architecture is not. Combining such sources as votes is
the core of programmatic weak supervision [10]; inter-annotator agreement statistics [11] quantify
how far annotations can be relied upon independently of whether any annotator is correct — applied
here to machine annotators, with agreement reported as corroboration, never as a calibrated
probability. Open-weight multimodal models — Qwen3-VL [12] and InternVL3 [13] — emit
schema-constrained text from image sequences, making them plausible single-model replacements for
a pipeline; their known failure mode is object hallucination [14], untested on archival community
television.

---

## III. METHOD `[Heading1]`

### A. Corpus and Clip Construction `[Heading2]`

The corpus is 47 NVTV programmes from 2016, segmented into fixed 30-second clips with FFmpeg,
discarding any final fragment under 2.0 s, producing **626 clips totalling 5.09 h with zero
failures**. Each worker writes a unique partial file, validates duration and publishes atomically,
so ordering cannot perturb the dataset. Sources — not clips — are split, 9 programmes (123
clips) to calibration and 38 (503 clips) to evaluation, by a seeded permutation of the sorted
identifiers; only calibration material was inspected when choosing thresholds.

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
| Total clip duration | 5.09 h (18,312 s; mean clip 29.25 s) |

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

Two structural rules apply: each *family* receives equal total weight after within-family
aggregation, so extra frames cannot manufacture voters; and no value is corroborated by the source
that produced it.

### C. Scene-Aware Temporal Sampling `[Heading2]`

The production policy detects shot boundaries with an adaptive rolling-content detector [15],
samples scene midpoints, always includes the temporal centre and caps at 5 frames. On-screen text
uses a denser probe — every 2.5 s to at most 12 frames — because captions appear and disappear
faster than the visual sampling interval.

### D. Strict Dual-Engine OCR `[Heading2]`

On-screen text is the only field with a hard veto, because a hallucinated name in a catalogue
record is the most damaging error available here. A string is published only if it exceeds
per-engine confidence (Tesseract ≥ 60, EasyOCR ≥ 0.50), persists across ≥ 2 frames at similarity
≥ 0.82 and matches across engines at ≥ 0.80; otherwise the field is `conflict`, and no other
source can override this.

### E. Evidence Status and Agreement Scoring `[Heading2]`

Every field carries a status from `observed`, `not_detected`, `not_applicable`, `conflict` or
`error`, with its supporting models and weights. An agreement score is computed only when at least
two non-empty sources exist; otherwise it is `null` and `needs_caution` is set. Scores bin as
**high** (≥ 0.75), **moderate** (≥ 0.50) and **low** (< 0.50), using mean pairwise set-F1,
1 − min(WER, 1) for transcripts and per-family voting for integers. Empty output is never
promoted, preventing the degenerate optimum of a system that detects nothing and reports perfect
corroboration.

### F. Hosted Annotator, Reproducibility and Ethics `[Heading2]`

A hosted multimodal model (`gemini-3.6-flash`, ≤ 5 frames, schema-constrained JSON) contributes
**one family vote** to visual tags and people count; its on-screen text is diagnostic only. Seeds
are fixed, model revisions recorded, every stage resumable, artefacts written atomically.

The footage shows identifiable members of the public in public settings, recorded for broadcast.
The pipeline performs no identity inference and the annotator is prompted against it; people count
is an integer only; and sending frames to a hosted API is a third-party disclosure, gated on
licence and data-governance approval, with local-only operation supported. The 34-label
vocabulary encodes one person's view of what is worth recording about a community.

---

## IV. EXPERIMENTATION AND RESULTS `[Heading1]`

### A. Environment and Metrics `[Heading2]`

The pipeline ran on Google Colab with an **NVIDIA A100-SXM4-40GB**; the benchmark on a Kelvin2
A100 MIG `2g.20gb` slice, which is the binding constraint on that experiment — it sets the 4-frame
budget and forces int4 quantisation for the 8B models. Package versions are pinned.

Each metric has a limit. *Agreement* is corroboration, not correctness; *coverage* rewards recall
with no precision counterpart; *stability* cannot distinguish a consistently wrong system from a
correct one; *ROUGE-L recall* scores an honest abstention at 0.0 like a wrong answer; and
*multi-label accuracy* over 34 labels and 5 selected gives ≈ 0.85 for predicting nothing,
so only differences between models are meaningful. The benchmark's reference is the pipeline's own
consensus, so every benchmark number is agreement between automatic systems.

### B. RQ1: Frame-Sampling Ablation `[Heading2]`

TABLE III. `[tablehead]` FRAME-SAMPLING ABLATION (CALIBRATION SUBSET, *n* = 8)

| Policy | Mean frames | OCR items / clip | OCR set-F1 vs centre | Tag set-F1 vs centre | People-count stability | Mean stability |
|---|---|---|---|---|---|---|
| Centre frame | 1.000 | 14.5 | 1.0000 | 1.000 | 1.0000 | 1.0000 |
| Fixed 20/50/80% | 3.000 | 3.0 | 0.3027 | 0.650 | 0.6879 | 0.5469 |
| **Scene-aware** | 4.375 | **23.0** | 0.3115 | 0.675 | 0.6089 | 0.5318 |

Set-F1 columns are symmetric set overlap against the centre-frame baseline; people-count stability
is exp(−|Δ|), so 1.0 is an identical count. The centre row is 1.0 by construction.

The OCR counts are **not like-for-like, and the reason is the finding.** The persistence threshold
derives from the frame count: one frame requires one occurrence, so the centre-frame policy
publishes every raw OCR line unfiltered (14.5); fixed three-frame requires two of three widely
spaced frames, which almost nothing survives (3.0); scene-aware draws from the dense probe of up
to 12 frames, giving the same rule twelve chances (23.0). **On the only like-for-like
comparison — both filtered at two occurrences — scene-aware publishes roughly eight times the text
of fixed three-frame sampling.**

Mean stability is still *lowest* for scene-aware (0.5318 vs 0.5469), driven by people count:
looking at more of the clip finds more people than the centre frame shows. Coverage and agreement
trade directly. *n* = 8; no significance is claimed.

### C. RQ2: Agreement Structure Across Fields `[Heading2]`

Every field of all 626 clips was scored, ordered by mean agreement.

TABLE IV. `[tablehead]` EVIDENCE STATUS AND AGREEMENT BY FIELD (*n* = 626)

| Field | Families | Observed | Conflict | Not detected | High ≥ 0.75 | Moderate ≥ 0.50 | Low < 0.50 | Not scored | Mean agreement | Needs caution |
|---|---|---|---|---|---|---|---|---|---|---|
| People count | 4 | 0.907 | — | 0.093 | **0.625** | 0.174 | 0.109 | 0.093 | **0.812** | **0.109** |
| Transcript | 2 | 1.000 | — | — | 0.722 | 0.045 | 0.230 | 0.003 | 0.680 | 0.233 |
| Visual tags | 3 | 1.000 | — | — | 0.026 | 0.511 | 0.463 | 0.000 | 0.509 | 0.463 |
| Keywords | 3 | 1.000 | — | — | 0.002 | 0.005 | **0.990** | 0.003 | **0.173** | **0.994** |
| On-screen text | 2 | 0.467 | **0.534** | — | **0.000** | 0.005 | 0.462 | 0.534 | 0.156 | **0.995** |

**Agreement tracks how independent a field's sources are, not how hard its task is.** People count
is best corroborated (0.812, 62.5% high, 10.9% flagged) and has the most diverse evidence: two VQA
models of different architecture, a detector and a hosted model, converging on an integer. Visual
tags sit at 0.509; keywords, whose extractors read the *same* transcript, collapse to 0.173. The
ordering is the ordering of source independence.

**Keywords do not meet the design's own premise.** The scheme requires two independent families per
field; keywords have three extractors but one input, agreeing pairwise 0.327 (TF-IDF/YAKE), 0.108
(KeyBERT/YAKE) and 0.078 (KeyBERT/TF-IDF) — three ranking functions over one text, not three
sources of evidence.

**On-screen text is either vetoed or weakly corroborated, never confidently published:** 53.4% of
clips end in `conflict`, and of the rest none reaches high agreement — the intended trade, now
quantified. **Transcript's 0.680 is the number to trust least**, its two sources being the most
correlated pair in the system. 

### D. RQ3: Perturbation Robustness `[Heading2]`

TABLE V. `[tablehead]` STABILITY UNDER VISUAL DEGRADATION (*n* = 5)

| Perturbation | OCR stability | Tag stability | People-count stability | Mean |
|---|---|---|---|---|
| Gaussian blur | **0.0714** | **0.96** | 0.5742 | 0.5760 |
| JPEG quality 25 | 0.1111 | 0.80 | 0.6207 | 0.5421 |
| Low brightness | 0.3000 | 0.84 | 0.5742 | 0.6303 |

Robustness is a property of each field, not of the pipeline. Under blur, visual tagging is almost
unaffected (0.96) while OCR retains 7% of its output — a 13-fold difference. CLIP scores global
scene semantics that survive low-pass filtering, whereas character recognition depends on
high-frequency detail that blur removes and the dual-engine rule then vetoes. Hence a deployment
rule: **on degraded material the scene-level fields remain usable and the text field should be
treated as absent rather than as evidence of absence.** *n* = 5.

### E. RQ4: Hosted-Annotator Contribution Ablation `[Heading2]`

TABLE VI. `[tablehead]` HOSTED-ANNOTATOR ABLATION (*n* = 626)

| Field | Candidate coverage | Exact output-change rate | Mean candidate vs local agreement | Local vs augmented stability |
|---|---|---|---|---|
| On-screen text | 0.3850 | **0.0000** | 0.5468 | 1.0000 |
| People count | 0.6054 | 0.0176 | 0.8445 | 0.9883 |
| Visual tags | 1.0000 | **0.4904** | 0.4194 | 0.9029 |

**On-screen text: coverage 0.385, change rate exactly 0.0** — the annotator proposed text on 38.5%
of clips and changed the published field on none, verifying the veto empirically. **People count:
high agreement (0.8445), negligible change (1.8%).** **Visual tags: the annotator disagrees with
the local consensus more often than it agrees (0.4194) yet changes 49.0% of published tag sets.**

That last row is uncomfortable: under equal family weights a third voter differing systematically
from two correlated ones breaks ties in its own favour at scale. Whether that is correction or
corruption **cannot be determined from these numbers**, since no independent reference exists; a
deployment that cannot tolerate this should run local-only, which the design permits.

### F. RQ5: Open-Weight VLM Benchmark `[Heading2]`

Seven models ran zero-shot over all 626 clips under a constant protocol — 4 uniformly sampled
frames, identical prompt, greedy decoding, the same vocabulary — producing **21,489 (model, clip,
field) scores**. Thinking variants got a larger token budget (1400 vs 700); both 8B models ran
int4-quantised.

TABLE VII. `[tablehead]` VLM AGREEMENT WITH THE PIPELINE CONSENSUS (*n* = 626)

| Model | On-screen text (R-L) | Keywords (R-L) | Visual tags (acc.) | People count (acc.) | Transcript (R-L) |
|---|---|---|---|---|---|
| Qwen3-VL-2B-Instruct | 0.383 | 0.039 | 0.871 | 0.233 | **0.034** |
| Qwen3-VL-2B-Thinking | 0.384 | 0.028 | 0.874 | 0.323 | 0.018 |
| Qwen3-VL-4B-Instruct | 0.456 | 0.030 | 0.880 | 0.241 | 0.000 |
| Qwen3-VL-4B-Thinking | 0.389 | **0.040** | 0.873 | 0.315 | 0.019 |
| Qwen3-VL-8B-Instruct † | 0.431 | 0.036 | 0.876 | 0.232 | 0.000 |
| **InternVL3-2B** | **0.544** | 0.031 | **0.890** | **0.417** | 0.000 |
| InternVL3-8B † | 0.416 | 0.027 | 0.883 | 0.366 | 0.013 |

**Scale does not predict agreement.** InternVL3-2B, the smallest model here, leads three of five
fields — on-screen text (0.544, 19% above the best Qwen), visual tags (0.890) and people
count (0.417, 29% above) — and beats InternVL3-8B on all three, while the 8B Qwen leads nothing.
Quantisation confounds the 8B results, so the defensible claim is narrower: a 2B model sufficed
and paying for 8B bought nothing measurable.

**Thinking variants do not dominate their Instruct siblings.** At 2B, Thinking is level on
on-screen text and tags but ahead on people count (0.323 vs 0.233); at 4B it is behind on
on-screen text (0.389 vs 0.456) and ahead on people count (0.315 vs 0.241) — deliberation helping
enumeration, not perception. Thinking models alone receive a forced-conclusion retry.

**Transcript is at or near zero for every model (0.034 to 0.000), as predicted.** None accepts
audio, so the field measures how much speech is recoverable from vision alone: essentially none.
Three score exactly 0.000 by abstaining rather than inventing dialogue, which a recall metric
cannot distinguish from a wrong answer. **Keywords are near zero (0.027–0.040)** for the same
reason: reference keywords come from the transcript, model keywords from frames.

**The benchmark also prices the OCR veto.** On a clip whose reference on-screen text was empty, all
seven models read the station ident *NVTV / BELFAST LOCAL TELEVISION*; on another the reference
held only `TIVAL` while the models returned the full theatre poster — ROUGE-L recall scoring them
against a reference less complete than they are.

### G. Anticipated versus Actual `[Heading2]`

TABLE VIII. `[tablehead]` ANTICIPATED VERSUS ACTUAL

| # | Anticipated | Actual | Verdict |
|---|---|---|---|
| RQ1 | More frames raise coverage and stability together | Coverage up (23.0 vs 14.5 items), stability **down** (0.5318 vs 1.0) | Partly refuted |
| RQ1 | Fixed three-frame sits between centre and scene-aware | Fixed three-frame is **worst** on OCR coverage (3.0) | Refuted |
| RQ2 | Agreement will be highest where the task is easiest | Highest where the sources are most independent | Refuted |
| RQ2 | Three keyword extractors give three-way corroboration | 0.173 mean, 99.0% low — one input, three views | Refuted |
| RQ2 | The OCR veto is conservative | 53.4% conflict; no clip reaches high agreement | Confirmed |
| RQ3 | Degradation reduces all fields comparably | 13-fold spread: tags 0.96, OCR 0.07 under blur | Refuted |
| RQ4 | A third annotator mostly corroborates | Agrees 0.42 on tags yet changes 49.0% of them | Refuted |
| RQ4 | OCR veto holds | Change rate exactly 0.0000 | Confirmed |
| RQ5 | Larger models agree more with the consensus | InternVL3-2B leads 3 of 5 fields | Refuted |
| RQ5 | Thinking variants beat Instruct | Split by field; ahead only on people count | Partly refuted |
| RQ5 | Vision-only transcript will be near zero | 0.034 to 0.000; three models exactly 0.000 | Confirmed |

---

## V. DISCUSSION `[Heading1]`

### A. Interpretation `[Heading2]`

**Reliability is a per-field property, not a system property**, and the mechanisms differ enough
that a single confidence number per clip would mislead. Agreement ranks fields by how
architecturally independent their evidence is — 0.812 for four unrelated families, 0.173 for three
views of one transcript — so the score measures a property of the *ensemble* at least as much as
of the footage. The same logic explains the rest: blur destroys OCR and spares tagging
because they depend on different spatial frequencies, and a third annotator is redundant for
people count yet decisive for visual tags because integer counting has a narrow answer space that
independent families converge on. That last result is a genuine problem — equal weighting is
neutral only if families are independent, which two CLIP variants are not — and the provenance
machinery makes it visible without resolving it.

### B. Implications `[Heading2]`

The deliverable is not a catalogue but a *triaged* one, telling an archivist which fields two or
more independent systems corroborated and which rest on a single source — more honest than a
confident catalogue of unknown quality, and achievable with no annotation budget.

### C. Limitations `[Heading2]`

**No human reference** exists, so every number is agreement between automatic systems and the RQ4
tag result cannot be adjudicated. The **ablations are underpowered** (8 and 5 clips).
**Vocabulary is concentrated**: three of 34 labels fire on 63–95% of clips, two never fire.
**Sources are correlated** — the CLIP and Whisper pairs inflate their fields, and keywords are
worse, three extractors over one transcript, so 0.173 reflects the design rather than the corpus;
the CLIP-pair inflation could not be measured, because the artefact stores method-level rather
than model-level candidates. **Corroboration is blind to upstream error**: an ASR failure enters
the keyword field with every source agreeing, all three having read the same faulty text. In the
benchmark both 8B models ran int4, Thinking models alone receive a retry, and the 4-frame budget
was forced by the MIG slice. The corpus is one broadcaster, one city, one year, one run per model.

---

## VI. CONCLUSION AND FUTURE WORK `[Heading1]`

This work delivers a reliability-aware metadata pipeline for an archival community-television
corpus: 47 programmes segmented into 626 clips totalling 5.09 h with zero failures, five fields per
clip from heterogeneous pretrained families, every value carrying an evidence status, its
supporting models and a self-similarity-free agreement score. The useful findings mostly
contradicted expectation: agreement ranks fields by source independence rather than task difficulty
(0.812 against 0.173), on-screen text is in conflict on 53.4% of clips and reaches high agreement
on none, robustness is field-specific to a 13-fold degree, a third annotator rewrites 49.0% of tag
sets while agreeing 42% of the time, and a 2B model leads three of five benchmark fields while
every model scores at or near zero on transcript.

**Future work.** A small human reference — a few hundred clips — would convert every agreement
number here into a validity measurement and settle RQ4. Beyond that: measured per-source
weights, model-level candidate lists so the correlated-source inflation can be quantified, an
audio-capable benchmark model, larger ablations, a language-identification gate on the ASR stage,
the sub-clip timing the pipeline already records, and diarisation.

---

## REFERENCES `[references]`

[1] A. F. Smeaton, P. Over, and W. Kraaij, "Evaluation campaigns and TRECVid," in *Proc. 8th ACM
Int. Workshop on Multimedia Information Retrieval (MIR)*, 2006, pp. 321–330.

[2] M. Mühling, M. Meister, N. Korfhage, J. Wehling, A. Hörth, R. Ewerth, and B. Freisleben,
"Content-based video retrieval in historical collections of the German Broadcasting Archive,"
*Int. J. on Digital Libraries*, vol. 20, no. 2, pp. 167–183, 2019,
doi: 10.1007/s00799-018-0236-z.

[3] M. Mühling, N. Korfhage, K. Pustu-Iren, J. Bars, M. Knapp, H. Bellafkir, M. Vogelbacher,
D. Schneider, A. Hörth, R. Ewerth, and B. Freisleben, "VIVA: Visual information retrieval in video
archives," *Int. J. on Digital Libraries*, vol. 23, no. 4, pp. 319–333, 2022,
doi: 10.1007/s00799-022-00337-y.

[4] F. Pessanha and A. Akdag Salah, "A computational look at oral history archives," *ACM J. on
Computing and Cultural Heritage*, vol. 15, no. 1, art. 6, pp. 1–16, 2022, doi: 10.1145/3477605.

[5] A. Radford *et al.*, "Learning transferable visual models from natural language supervision,"
in *Proc. 38th Int. Conf. Machine Learning (ICML)*, 2021, pp. 8748–8763.

[6] A. Radford *et al.*, "Robust speech recognition via large-scale weak supervision," in *Proc.
40th Int. Conf. Machine Learning (ICML)*, 2023, pp. 28492–28518.

[7] J. Li, D. Li, C. Xiong, and S. Hoi, "BLIP: Bootstrapping language-image pre-training for
unified vision-language understanding and generation," in *Proc. 39th Int. Conf. Machine Learning
(ICML)*, 2022, pp. 12888–12900.

[8] W. Kim, B. Son, and I. Kim, "ViLT: Vision-and-language transformer without convolution or
region supervision," in *Proc. 38th Int. Conf. Machine Learning (ICML)*, 2021, pp. 5583–5594.

[9] N. Carion *et al.*, "End-to-end object detection with transformers," in *Proc. European Conf.
Computer Vision (ECCV)*, 2020, pp. 213–229.

[10] A. Ratner *et al.*, "Snorkel: Rapid training data creation with weak supervision," *Proc. VLDB
Endowment*, vol. 11, no. 3, pp. 269–282, 2017.

[11] R. Artstein and M. Poesio, "Inter-coder agreement for computational linguistics,"
*Computational Linguistics*, vol. 34, no. 4, pp. 555–596, 2008.

[12] Qwen Team, "Qwen3-VL technical report," 2025. **`[TO FILL: arXiv identifier]`**

[13] Z. Chen *et al.*, "InternVL3: Exploring advanced training and test-time recipes for
open-source multimodal models," 2025. **`[TO FILL: arXiv identifier]`**

[14] A. Rohrbach *et al.*, "Object hallucination in image captioning," in *Proc. Conf. Empirical
Methods in Natural Language Processing (EMNLP)*, 2018, pp. 4035–4045.

[15] B. Castellano, "PySceneDetect: Video scene cut detection and analysis tool," 2014–2025.
[Online]. Available: https://www.scenedetect.com

[16] C.-Y. Lin, "ROUGE: A package for automatic evaluation of summaries," in *Text Summarization
Branches Out*, ACL Workshop, 2004, pp. 74–81.

[17] R. Smith, "An overview of the Tesseract OCR engine," in *Proc. 9th Int. Conf. Document
Analysis and Recognition (ICDAR)*, 2007, pp. 629–633.

[18] N. Reimers and I. Gurevych, "Sentence-BERT: Sentence embeddings using Siamese BERT-networks,"
in *Proc. EMNLP-IJCNLP*, 2019, pp. 3982–3992.

[19] R. Campos *et al.*, "YAKE! Keyword extraction from single documents using multiple local
features," *Information Sciences*, vol. 509, pp. 257–289, 2020.

[20] M. Grootendorst, "KeyBERT: Minimal keyword extraction with BERT," 2020. [Online]. Available:
https://github.com/MaartenGr/KeyBERT

