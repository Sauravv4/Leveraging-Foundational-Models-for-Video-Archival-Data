# Write-up guide — research paper + supporting materials

Derived from the four exemplar submissions in `references/exemplars/` and the
IEEE conference template in `references/ieee-conference-template-letter.docx`.
This is the plan the project's two written deliverables should follow.

---

## 1. The two deliverables

Both exemplars submit the same pair, and the split between them is deliberate:

| | Research paper | Supporting materials |
|---|---|---|
| Format | IEEE two-column conference paper | Single-column technical report |
| Length (exemplar A) | ~6,400 words / 11 pp | ~7,800 words / 17 pp |
| Length (exemplar B) | ~5,000 words / 10 pp | ~12,600 words / 40 pp |
| Contains | The claim and the evidence for it | Everything that supports the claim but does not fit |
| Literature | ~1 page, only work the contribution stands on | Full review, 5–7 sub-areas, comparative matrix |
| Method | What was done and why, compressed | Full configs, prompts, hyperparameters, seeds |
| Results | Headline tables + the figures that carry the argument | Per-run detail, worked examples, failure cases |
| Process | Not present | Lifecycle, tool choices, verification, divergence from spec |

Rule of thumb from both exemplars: **the paper must stand alone**. The supporting
materials are read second, by someone who already believes the result and wants
to check it.

---

## 2. Research paper — section plan

IEEE numbering (`I.`, `II.`, …) with lettered subsections (`A.`, `B.`, …).
Word styles from the template are given in backticks.

**Title** (`papertitle`), **Authors** (`Author`), **Abstract** (`Abstract`),
**Keywords** (`Keywords`).

*Abstract (~200–250 words).* Both exemplars use the same five-move shape:
problem → why existing approaches fall short → what was built → **numeric**
headline results, including the negative ones → what the result licenses.
Exemplar A states both the win (0.0218–0.0704 mAP gain on four datasets) and the
loss (−0.0907 on the smallest); exemplar B leads with a null result. Report the
numbers that did not go your way — both exemplars do, and both are stronger for it.

### I. Introduction
- `A. Problem and Context` — archival video at NVTV: hours of long-form community
  broadcast with no per-segment index, so nothing inside a programme is findable.
- `B. Research Aim and Objectives` — numbered objectives, each one testable.
- `C. Scope and Boundaries` — say plainly what is *not* attempted (no scene
  detection, no fine-tuning of the foundation models, fixed 30 s segmentation,
  English-language speech).
- `D. Research Questions` — 3–4, each answerable by one experiment you actually ran.
- `E. Methodology Overview and Paper Organisation`.

Candidate RQs for this project (pick the ones the experiments can actually answer):
1. Does zero-shot CLIP labelling over a fixed taxonomy produce retrieval-usable
   clip metadata without any domain training data?
2. Does fusing transcript/NER evidence with visual evidence beat either alone
   for clip retrieval?
3. How does fixed-length 30 s segmentation compare with shot-boundary
   segmentation on retrieval quality — and what does it cost?
4. Which metadata field carries the retrieval signal (ablation over the 10
   categories + caption + transcript)?

### II. Related Work
One page, three or four themed subsections (exemplar A: *Blade Defect Detection*,
*Conventional Detectors*, *Foundation Models*). Here: `A. Video Retrieval and
Archival Indexing`, `B. Vision–Language Foundation Models (CLIP, BLIP-2)`,
`C. ASR and Entity Linking for Broadcast Audio`. Close the section by naming the
gap the project fills — exemplar A ends on exactly one unaddressed question and
then builds the whole paper on it.

### III. Methods
- `A. Dataset` — NVTV corpus: number of programmes, total duration, resulting
  clip count, what the `.txt` synopses provide, licence/access conditions.
- `B. Pipeline Architecture` — one figure (`figurecaption` style, "Fig. 1.").
  The four stages, what each model contributes, where the 30 s boundary is set.
- `C. Implementation Procedure` — the decisions with consequences: stream-copy
  segmentation, 6 keyframes averaged pre-softmax, BLIP-2 in 8-bit, models never
  co-resident, per-clip checkpointing.
- `D. Design Choices and Their Limits` — exemplar B's `D. Hyperparameter
  Rationale and its Limits` is the model: justify a choice, then state what it
  was not possible to tune and why.
- `E. Ethical Considerations` — broadcast footage of identifiable people, ASR
  transcription of private speech, redistribution limits, bias in a taxonomy
  written by one annotator. Both exemplars keep this in the paper, not only the
  appendix.

### IV. Experimentation and Results
- `A. Hardware and Software Environment` — exact GPU, driver, library versions.
- `B. Evaluation Metrics and Rationale` — define each metric *and* say what it
  cannot see. Exemplar A gives metric limitations its own subsection.
- `C.`–`F.` One subsection per RQ, in RQ order, each with a table
  (`tablehead`/`tablecolhead`/`tablecopy`) and a figure where it helps.
- A `Comparison Against Anticipated Results` subsection (exemplar B, Table 9):
  what you predicted before running vs. what happened. This is cheap to write
  and reads as genuine science.

### V. Discussion
`A. Interpretation` — why the numbers came out this way, mechanism not restatement.
`B. Implications` — what an archivist can now do that they could not before.
`C. Limitations` — specific and quantified ("evaluated on N clips from M
programmes, all English-language, single annotator"), never generic.

### VI. Conclusion and Future Work
Contributions as a short list, then concrete next steps (Component 2 retrieval
UI, temporal segmentation, speaker diarisation, domain-tuned taxonomy).

### References
`references` style, IEEE numeric `[1]`. Exemplar A carries 28, exemplar B 10 in
the paper with the full set in the supporting materials. Aim for 20–30, with the
foundation-model primary sources (CLIP, BLIP-2, Whisper) cited directly.

---

## 3. Supporting materials — section plan

Single column, numbered `1`, `1.1`, `1.2`. Open with a contents list — both
exemplars do, and it is what makes a 40-page report navigable.

1. **Extended Literature and Context** — open with `1.1 Scope and Method`: the
   databases searched, the search terms, the inclusion window. Then one
   sub-section per area, ending in `Synthesis and Gap`. Exemplar B adds a
   **comparative literature matrix** (paper × task × model × data × what it
   leaves open) — include one.
2. **Project Lifecycle** — planning and scoping, data acquisition, implementation,
   experimentation, evaluation and iteration. Written as decisions with reasons,
   not as a diary.
3. **Verification and Validation** — the section that most raises a grade and is
   most often missing. For this project: manual audit of a random sample of
   clip labels against human judgement; check that segment boundaries and
   timestamps line up with the source video; confirm resumed runs reproduce
   an uninterrupted run; confirm embeddings are unit-norm and aligned to clip ids;
   spot-check Whisper output against the supplied `.txt` transcripts.
   Exemplar A's annotation audit — which found real label errors in a published
   dataset — is the standard to aim at.
4. **Tooling and Environment** — model versions and revisions, CUDA/driver, ffmpeg
   build, quantisation library versions, and `4.x Summary of Tool-Driven
   Constraints`: where the tooling, not the science, set the ceiling.
5. **Reflection** — `5.1 Divergence from the Original Specification` (state scope
   changes plainly and say who approved them; exemplar B's supervisor-approved
   narrowing is handled in one honest paragraph), `5.2 Design Rationale`,
   `5.3 Lessons Learned`, `5.4 Evaluation of the Outcome`.
6. **Responsible AI** — bias, privacy, fairness, transparency, accountability and
   human oversight, one subsection each (exemplar B's layout), plus an explicit
   statement of AI-assistance and student responsibility.
7. **Appendices** — full config, the complete category taxonomy, prompt/label
   sets, per-clip failure analysis, extra tables.

---

## 4. Conventions to follow

- Every claim in the paper carries a number or a citation. Neither exemplar
  contains an unsupported comparative adjective.
- Tables: `TABLE I` / `TABLE 1`, small caps caption above the table. Figures:
  `Fig. 1.` caption below. Refer to them in-text ("Table II reports …").
- Report negative and null results in the abstract, not buried in discussion.
- State threats to validity *before* the results (exemplar B, §5.5), so they
  read as design awareness rather than excuses.
- British spelling throughout; define every acronym at first use in the body
  even if the abstract already defined it.
- Pre-register anticipated results, then table them against the actual ones.
- Keep raw numbers in the supporting materials; keep only the numbers that carry
  the argument in the paper.

---

## 5. Status

Drafts now exist for both deliverables, written against the executed notebooks:

- `paper/conference_paper.md`
- `report/supporting_materials.md`

The list below was written before those drafts and is superseded by the
`[TO FILL]` markers inside them, which are specific to what each section needs.

## 5b. Original gap list

- [ ] Corpus statistics: programmes, total hours, clip count, clips per programme.
- [ ] An evaluation set — a labelled sample of clips, or a set of retrieval
      queries with relevance judgements. Without this there are no results tables.
- [ ] A baseline to compare against (transcript-only keyword search is the
      obvious one, and is cheap to build).
- [ ] Runtime and cost measurements per stage, per hour of video.
- [ ] The Component 2 retrieval results, once that component exists.
