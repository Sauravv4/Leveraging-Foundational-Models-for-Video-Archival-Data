// Build the slide deck that accompanies the recorded demo.
// Palette and figures are shared with the paper, so the deck and the paper read
// as one piece of work.
const pptxgen = require('pptxgenjs');

const NAVY = '12305B', BLUE = '2A78D6', ORANGE = 'EB6834', AQUA = '1BAF7A';
const INK = '10100F', MUTED = '5A5954', LINE = 'DEDDD8';
const PAPER = 'FFFFFF', TINT = 'F4F6FA';
const HEAD = 'Cambria', BODY = 'Calibri';
const FIG = (n) => `docs/figures/${n}`;

const pres = new pptxgen();
pres.layout = 'LAYOUT_WIDE';                 // 13.3 x 7.5 in — set before any slide
pres.author = 'Saurav Kumar Vellattuparambil Vijayakumar';
pres.title = 'Leveraging Foundational Models for Video Archival Data';

const W = 13.3, M = 0.75;                     // slide width, side margin

// ---- helpers ---------------------------------------------------------------
function darkSlide() {
  const s = pres.addSlide();
  s.background = { color: NAVY };
  return s;
}
function lightSlide(title, kicker) {
  const s = pres.addSlide();
  s.background = { color: PAPER };
  if (kicker) {
    s.addText(kicker, {
      x: M, y: 0.42, w: 8, h: 0.3, isTextBox: true, margin: 0,
      fontFace: BODY, fontSize: 12, bold: true, color: ORANGE, charSpacing: 1.4,
    });
  }
  s.addText(title, {
    x: M, y: kicker ? 0.74 : 0.55, w: W - 2 * M, h: 0.85, isTextBox: true, margin: 0,
    fontFace: HEAD, fontSize: 32, bold: true, color: NAVY,
  });
  return s;
}
// The deck's one repeated motif: a figure in a tinted rounded card.
function statCard(s, x, y, w, value, label, colour) {
  s.addShape(pres.ShapeType.roundRect, {
    x, y, w, h: 1.5, rectRadius: 0.1,
    fill: { color: TINT }, line: { color: TINT },
  });
  s.addText(value, {
    x, y: y + 0.16, w, h: 0.72, isTextBox: true, align: 'center',
    fontFace: HEAD, fontSize: 34, bold: true, color: colour || NAVY,
  });
  s.addText(label, {
    x: x + 0.12, y: y + 0.88, w: w - 0.24, h: 0.48, isTextBox: true, align: 'center',
    fontFace: BODY, fontSize: 11.5, color: MUTED,
  });
}
function bullets(s, items, opts) {
  s.addText(items.map((t, i) => ({
    text: t, options: { bullet: true, breakLine: i < items.length - 1 },
  })), Object.assign({
    isTextBox: true, fontFace: BODY, fontSize: 15, color: INK,
    paraSpaceAfter: 9, lineSpacing: 21,
  }, opts));
}

// ---- 1 · title -------------------------------------------------------------
{
  const s = darkSlide();
  s.addText('Leveraging Foundational Models\nfor Video Archival Data', {
    x: M, y: 1.75, w: 8.6, h: 2.0, isTextBox: true, margin: 0,
    fontFace: HEAD, fontSize: 40, bold: true, color: 'FFFFFF', lineSpacing: 46,
  });
  s.addText('Segment-level metadata for a community-television archive, published with an auditable estimate of how strongly independent models corroborate it.', {
    x: M, y: 3.95, w: 8.2, h: 0.9, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 15, color: 'CADCFC', lineSpacing: 22,
  });
  s.addText([
    { text: 'Saurav Kumar Vellattuparambil Vijayakumar', options: { bold: true, breakLine: true } },
    { text: 'Student number 40490925', options: { breakLine: true } },
    { text: 'Supervisor: Dr Awais Rauf', options: { breakLine: true } },
    { text: 'MSc Artificial Intelligence · ECS8056', options: { breakLine: true } },
    { text: "School of EEECS, Queen's University Belfast", options: {} },
  ], {
    x: M, y: 5.15, w: 7.5, h: 1.6, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 13, color: 'FFFFFF', lineSpacing: 19,
  });
  // Photograph goes here — required by the handbook.
  s.addShape(pres.ShapeType.roundRect, {
    x: 9.9, y: 2.0, w: 2.65, h: 2.65, rectRadius: 0.14,
    fill: { color: '1C4478' }, line: { color: BLUE, width: 1.25 },
  });
  s.addText('YOUR PHOTO\nreplace this shape', {
    x: 9.9, y: 3.0, w: 2.65, h: 0.8, isTextBox: true, align: 'center',
    fontFace: BODY, fontSize: 11, color: 'CADCFC',
  });
  s.addNotes('Say your name and student number aloud here — the handbook requires both on screen and it is the first thing an assessor checks.');
}

// ---- 2 · the problem -------------------------------------------------------
{
  const s = lightSlide('An archive you cannot search inside', 'THE PROBLEM');
  bullets(s, [
    'NVTV is a Belfast community broadcaster with a public archive of the city’s civic life.',
    'Every programme has a title. Nothing describes what happens inside it.',
    'To find one moment, an archivist watches the whole programme.',
    'Manual annotation was excluded for this corpus, closing the usual route to a gold standard.',
  ], { x: M, y: 2.0, w: 6.5, h: 3.2 });

  s.addShape(pres.ShapeType.roundRect, {
    x: 7.7, y: 1.95, w: 4.85, h: 3.4, rectRadius: 0.12,
    fill: { color: TINT }, line: { color: LINE },
  });
  s.addText('WHAT A SINGLE-MODEL PIPELINE PUBLISHES', {
    x: 8.0, y: 2.2, w: 4.3, h: 0.3, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 10.5, bold: true, color: MUTED, charSpacing: 1,
  });
  s.addText([
    { text: 'people_count: 3', options: { breakLine: true } },
    { text: 'visual_tags: interview, podium', options: { breakLine: true } },
    { text: 'transcript: "…medication study…"', options: {} },
  ], {
    x: 8.0, y: 2.6, w: 4.3, h: 1.1, isTextBox: true, margin: 0,
    fontFace: 'Courier New', fontSize: 12.5, color: INK, lineSpacing: 20,
  });
  s.addText('Three models agreed, or one model guessed — the record looks identical either way. A missing field can be worked around. A confidently wrong field silently corrupts the catalogue.', {
    x: 8.0, y: 3.85, w: 4.3, h: 1.3, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 13, color: INK, italic: true, lineSpacing: 20,
  });
  s.addNotes('The contrast card is the whole motivation: identical-looking output, completely different support underneath.');
}

// ---- 3 · aim and objectives ------------------------------------------------
{
  const s = lightSlide('Publish the corroboration, not just the metadata', 'AIM');
  s.addText('Produce segment-level metadata using only pretrained models, and attach to every published field an auditable estimate of how strongly independent sources support it.', {
    x: M, y: 1.95, w: 11.8, h: 0.95, isTextBox: true, margin: 0,
    fontFace: HEAD, fontSize: 19, color: NAVY, italic: true, lineSpacing: 27,
  });
  const objs = [
    ['01', 'Segment the corpus reproducibly and resumably'],
    ['02', 'Generate five fields from ≥ 2 independent families each'],
    ['03', 'Score agreement without self-similarity or empty promotion'],
    ['04', 'Quantify sampling, degradation and a hosted annotator'],
    ['05', 'Benchmark seven open-weight VLMs against the consensus'],
  ];
  objs.forEach(([n, text], i) => {
    const y = 3.2 + i * 0.72;
    s.addShape(pres.ShapeType.ellipse, {
      x: M, y, w: 0.46, h: 0.46, fill: { color: BLUE }, line: { color: BLUE },
    });
    s.addText(n, {
      x: M, y: y + 0.04, w: 0.46, h: 0.38, isTextBox: true, align: 'center',
      fontFace: BODY, fontSize: 12, bold: true, color: 'FFFFFF',
    });
    s.addText(text, {
      x: M + 0.68, y: y + 0.03, w: 10.5, h: 0.42, isTextBox: true, margin: 0,
      fontFace: BODY, fontSize: 15, color: INK,
    });
  });
  s.addNotes('Five objectives, five research questions — they map one to one.');
}

// ---- 4 · the corpus --------------------------------------------------------
{
  const s = lightSlide('47 programmes, segmented and verified', 'THE DATA');
  const cards = [
    ['47', 'archival programmes\nNVTV, 2016', NAVY],
    ['626', 'fixed 30-second clips\nzero failures', BLUE],
    ['5.09 h', 'total duration\nFFprobe-verified', NAVY],
    ['123 / 503', 'calibration / evaluation\nsplit at source level', ORANGE],
  ];
  cards.forEach(([v, l, c], i) => statCard(s, M + i * 3.03, 2.15, 2.8, v, l, c));
  bullets(s, [
    'FFmpeg stream copy — no re-encoding; every clip FFprobe-verified after writing.',
    'Atomic publication: each worker renames on success, so an interrupted run leaves no truncated file.',
    'The split is assigned per source, so no programme contributes clips to both halves.',
    'Boundary continuity verified across all 579 adjacent pairs — maximum drift 0.0000 s.',
  ], { x: M, y: 4.1, w: 11.8, h: 2.5 });
  s.addNotes('Zero failures out of 626 is worth saying aloud — it is the claim the V&V section backs.');
}

// ---- 5 · five fields -------------------------------------------------------
{
  const s = lightSlide('Every field, at least two unrelated families', 'METHOD');
  const rows = [
    ['Transcript', 'Whisper small + turbo', 'two decoder configs — the weakest pair, reported as such'],
    ['On-screen text', 'Tesseract + EasyOCR', 'classical line recogniser vs neural detector'],
    ['Keywords', 'KeyBERT, YAKE, TF-IDF', 'three rankers — but one transcript'],
    ['Visual tags', 'CLIP ViT-B/32 + ViT-L/14', 'capacity differs, mechanism does not'],
    ['People count', 'BLIP-VQA, ViLT-VQA, DETR', 'captioner, transformer, detector — three routes to one integer'],
  ];
  rows.forEach(([f, m, why], i) => {
    const y = 1.95 + i * 0.86;
    s.addShape(pres.ShapeType.roundRect, {
      x: M, y, w: 11.8, h: 0.74, rectRadius: 0.08,
      fill: { color: i % 2 ? PAPER : TINT }, line: { color: i % 2 ? PAPER : TINT },
    });
    s.addText(f, {
      x: M + 0.22, y, w: 2.2, h: 0.74, isTextBox: true, margin: 0, valign: 'middle',
      fontFace: BODY, fontSize: 14.5, bold: true, color: NAVY,
    });
    s.addText(m, {
      x: M + 2.5, y, w: 3.5, h: 0.74, isTextBox: true, margin: 0, valign: 'middle',
      fontFace: BODY, fontSize: 14, color: INK,
    });
    s.addText(why, {
      x: M + 6.2, y, w: 5.3, h: 0.74, isTextBox: true, margin: 0, valign: 'middle',
      fontFace: BODY, fontSize: 12.5, color: MUTED, italic: true,
    });
  });
  s.addText('The models fail in different ways — that is the point. Agreement between unrelated mechanisms carries information that agreement between two checkpoints of one architecture does not.', {
    x: M, y: 6.35, w: 11.8, h: 0.6, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 13.5, color: NAVY, italic: true,
  });
  s.addNotes('Do not read the table aloud. Say the closing line: diversity of failure modes is the mechanism.');
}

// ---- 6 · what gets published -----------------------------------------------
{
  const s = lightSlide('What the system actually publishes', 'THE RECORD');
  s.addShape(pres.ShapeType.roundRect, {
    x: M, y: 1.95, w: 5.9, h: 3.85, rectRadius: 0.12,
    fill: { color: NAVY }, line: { color: NAVY },
  });
  s.addText([
    { text: '"people_count": {', options: { breakLine: true } },
    { text: '   "value": 1,', options: { breakLine: true } },
    { text: '   "status": "observed",', options: { breakLine: true } },
    { text: '   "models": ["BLIP-VQA",', options: { breakLine: true } },
    { text: '              "ViLT-VQA", "DETR"],', options: { breakLine: true } },
    { text: '   "agreement_score": 0.812,', options: { breakLine: true, color: '8ED6B4' } },
    { text: '   "needs_caution": false', options: { breakLine: true } },
    { text: '}', options: {} },
  ], {
    x: M + 0.35, y: 2.3, w: 5.3, h: 3.2, isTextBox: true, margin: 0,
    fontFace: 'Courier New', fontSize: 14, color: 'FFFFFF', lineSpacing: 23,
  });
  const rules = [
    ['Self-similarity excluded', 'a source never corroborates itself'],
    ['Empty output never promoted', 'silence is not_detected, never high agreement'],
    ['Strict dual-engine OCR veto', 'both engines, two frames, 0.80 cross-engine'],
  ];
  rules.forEach(([h, d], i) => {
    const y = 2.05 + i * 1.32;
    s.addShape(pres.ShapeType.ellipse, {
      x: 7.2, y, w: 0.42, h: 0.42, fill: { color: ORANGE }, line: { color: ORANGE },
    });
    s.addText(String(i + 1), {
      x: 7.2, y: y + 0.04, w: 0.42, h: 0.34, isTextBox: true, align: 'center',
      fontFace: BODY, fontSize: 12, bold: true, color: 'FFFFFF',
    });
    s.addText(h, {
      x: 7.85, y: y - 0.02, w: 4.7, h: 0.36, isTextBox: true, margin: 0,
      fontFace: BODY, fontSize: 15.5, bold: true, color: NAVY,
    });
    s.addText(d, {
      x: 7.85, y: y + 0.36, w: 4.7, h: 0.55, isTextBox: true, margin: 0,
      fontFace: BODY, fontSize: 13.5, color: MUTED, lineSpacing: 19,
    });
  });
  s.addText('A hallucinated name in a catalogue is the most damaging error available here, so on-screen text is deliberately conservative.', {
    x: M, y: 6.15, w: 11.8, h: 0.6, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 14, color: NAVY, italic: true,
  });
  s.addNotes('Rule 2 matters most: without it, a corpus of quiet low-text clips would report near-perfect reliability.');
}

// ---- 7 · demo divider ------------------------------------------------------
{
  const s = darkSlide();
  s.addText('LIVE DEMO', {
    x: M, y: 2.5, w: 9, h: 0.4, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 14, bold: true, color: ORANGE, charSpacing: 2.2,
  });
  s.addText('The review dashboard', {
    x: M, y: 2.95, w: 10, h: 0.9, isTextBox: true, margin: 0,
    fontFace: HEAD, fontSize: 40, bold: true, color: 'FFFFFF',
  });
  s.addText('The clip plays beside its record. A field supported by four independent families is safe to publish; a field carrying needs_caution goes to a human first. The deliverable is not a list — it is a triaged list.', {
    x: M, y: 4.05, w: 9.4, h: 1.2, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 16, color: 'CADCFC', lineSpacing: 24,
  });
  s.addNotes('Switch to screen capture here. Have the dashboard and a clip already loaded — nothing should be seen booting.');
}

// ---- 8 · no training -------------------------------------------------------
{
  const s = lightSlide('Nothing is trained — and that is deliberate', 'CONFIGURATION');
  s.addText('An archive with no annotated reference cannot supervise training, and a system whose product is a reliability estimate must not be tuned against labels it does not have.', {
    x: M, y: 1.95, w: 11.8, h: 0.9, isTextBox: true, margin: 0,
    fontFace: HEAD, fontSize: 18, color: NAVY, italic: true, lineSpacing: 26,
  });
  statCard(s, M, 3.05, 3.5, 'Zero-shot', 'every checkpoint at its\npublished revision', NAVY);
  statCard(s, M + 4.15, 3.05, 3.5, '12', 'configuration parameters\nin place of hyperparameters', BLUE);
  statCard(s, M + 8.3, 3.05, 3.5, '123 clips', 'the calibration split every\nchoice was made on', ORANGE);
  bullets(s, [
    'Sampling policy chosen by the RQ1 ablation; OCR thresholds set to bias toward precision.',
    'Two parameters rest on library defaults and are disclosed as untuned.',
    'The 503-clip evaluation split was never used for any selection decision.',
  ], { x: M, y: 4.95, w: 11.8, h: 1.8 });
  s.addNotes('Assessors will be waiting for the training section. Answering it confidently beats leaving a gap.');
}

// ---- 9 · how it is evaluated ----------------------------------------------
{
  const s = lightSlide('Inference and scoring are separate notebooks', 'EVALUATION');
  const cards = [
    ['02_vlm_benchmark.ipynb', 'GPU \u00b7 Kelvin2 MIG slice', [
      'Seven models over all 626 clips under one protocol: 4 frames, one prompt, greedy decoding.',
      'Writes one prediction cache per model.',
      'Fully resumable \u2014 reloads the cache, retries only failures, skips completed work.',
      'Each cache carries a prompt version; a stale cache is ignored, never silently mixed in.',
    ], BLUE],
    ['03_vlm_benchmark.ipynb', 'CPU \u00b7 anywhere, no GPU', [
      'Loads no models at all.',
      'Reads the ground truth and the caches, and rebuilds every comparison table in seconds.',
      'Coverage denominators are reported beside every mean.',
      'Scoring can be corrected and re-run without paying for inference again.',
    ], ORANGE],
  ];
  cards.forEach(([name, sub, points, colour], i) => {
    const x = M + i * 6.05;
    s.addShape(pres.ShapeType.roundRect, {
      x, y: 1.95, w: 5.75, h: 4.15, rectRadius: 0.12,
      fill: { color: TINT }, line: { color: TINT },
    });
    s.addText(name, {
      x: x + 0.35, y: 2.2, w: 5.05, h: 0.4, isTextBox: true, margin: 0,
      fontFace: 'Courier New', fontSize: 15, bold: true, color: colour,
    });
    s.addText(sub, {
      x: x + 0.35, y: 2.62, w: 5.05, h: 0.3, isTextBox: true, margin: 0,
      fontFace: BODY, fontSize: 11.5, color: MUTED, charSpacing: 0.6,
    });
    bullets(s, points, { x: x + 0.35, y: 3.05, w: 5.05, h: 2.9, fontSize: 13 });
  });
  s.addText('The split is the highest-value structural decision in the project: an interrupted GPU job costs nothing, and a scoring fix never re-runs inference.', {
    x: M, y: 6.3, w: 11.8, h: 0.6, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 13.5, color: NAVY, italic: true,
  });
  s.addNotes('This is the answer to "how is it evaluated". Show 02 resuming from its caches, then 03 rebuilding the tables with no GPU.');
}

// ---- 10-13 \u00b7 results --------------------------------------------------------
function resultSlide(kicker, title, figure, points, note) {
  const s = lightSlide(title, kicker);
  s.addImage({ path: figure, x: M, y: 1.95, w: 6.6, h: 4.4, sizing: { type: 'contain', w: 6.6, h: 4.4 } });
  bullets(s, points, { x: 7.75, y: 2.15, w: 4.8, h: 4.0, fontSize: 14 });
  s.addNotes(note);
  return s;
}
resultSlide('RQ2 · 626 CLIPS', 'Agreement ranks independence, not difficulty',
  FIG('fig1_agreement_tiers.png'), [
    'People count 0.812 — four unrelated families.',
    'Keywords 0.173 — three extractors, one transcript.',
    'On-screen text conflicts on 53.4% of clips and reaches high agreement on none.',
    'The ordering is the ordering of source independence.',
  ], 'This is the headline finding. Keywords are not weak because the task is hard — they are weak because there is one input.');

resultSlide('RQ3 · 5 CLIPS', 'Robustness is field-specific, not system-wide',
  FIG('fig3_robustness.png'), [
    'Under blur, visual tagging holds 0.96 of its output.',
    'On-screen text retains 0.07 — a thirteen-fold spread under one perturbation.',
    'CLIP reads global scene semantics that survive low-pass filtering; character recognition does not.',
    'Deployment rule: on degraded material, treat the text field as absent, not as evidence of absence.',
  ], 'n = 5. Directionally clear, statistically weak — say so.');

resultSlide('RQ4 · 626 CLIPS', 'A third annotator refuted my own hypothesis',
  FIG('fig4_hosted_annotator.png'), [
    'The hosted annotator agrees with the local consensus only 0.419 of the time …',
    '… yet rewrites 49.0% of published visual-tag sets.',
    'On on-screen text the dual-engine veto holds it to exactly zero changes.',
    'Equal weighting is neutral only when families are independent — and two CLIP variants are not.',
  ], 'The uncomfortable result, and the most useful one. The provenance machinery makes it visible but cannot fix it.');

resultSlide('RQ5 · 21,489 SCORES', 'Scale did not predict agreement',
  FIG('fig2_vlm_benchmark.png'), [
    'Seven open-weight models, one protocol, 626 clips.',
    'InternVL3-2B — the smallest — leads three of five fields.',
    'It beats its own 8B sibling on all three.',
    'Every model scores at or near zero on transcript: none of them accepts audio.',
  ], 'Both 8B models ran int4 on the MIG slice, so this is not evidence that scale hurts — only that 2B sufficed here.');

// ---- 13 · anticipated vs actual -------------------------------------------
{
  const s = lightSlide('The useful findings contradicted expectation', 'RESULTS');
  statCard(s, M, 2.05, 3.5, '8 of 11', 'anticipated outcomes\nrefuted or partly refuted', ORANGE);
  statCard(s, M + 4.15, 2.05, 3.5, '3', 'confirmed — all following\ndeductively from the design', NAVY);
  statCard(s, M + 8.3, 2.05, 3.5, '0', 'empirical expectations about\nscale or deliberation upheld', BLUE);
  bullets(s, [
    'Agreement was expected to track task difficulty. It tracks source independence.',
    'Three keyword extractors were expected to give three-way corroboration. They give one view, three times.',
    'Degradation was expected to affect fields comparably. The spread is thirteen-fold.',
    'Larger models were expected to agree more. The smallest led.',
  ], { x: M, y: 3.95, w: 11.8, h: 2.6 });
  s.addNotes('Frame this as confidence, not failure: pre-registering expectations is what makes the refutations meaningful.');
}

// ---- 14 · limitations ------------------------------------------------------
{
  const s = lightSlide('What these numbers do not say', 'LIMITATIONS');
  const items = [
    ['No human reference', 'Every figure measures corroboration between automatic sources — never accuracy.'],
    ['Correlated sources', 'Two CLIP variants and two Whisper checkpoints share an architecture, inflating their fields.'],
    ['Blind to upstream error', 'If speech recognition fails, all three keyword extractors agree on the same wrong text.'],
    ['Underpowered ablations', 'RQ1 uses 8 clips and RQ3 uses 5. Directional, not significant.'],
    ['Single setting', 'One broadcaster, one city, one year, one run per model.'],
  ];
  items.forEach(([h, d], i) => {
    const y = 2.0 + i * 0.94;
    s.addShape(pres.ShapeType.roundRect, {
      x: M, y, w: 11.8, h: 0.82, rectRadius: 0.08,
      fill: { color: TINT }, line: { color: TINT },
    });
    s.addText(h, {
      x: M + 0.25, y, w: 3.1, h: 0.82, isTextBox: true, margin: 0, valign: 'middle',
      fontFace: BODY, fontSize: 14.5, bold: true, color: ORANGE,
    });
    s.addText(d, {
      x: M + 3.5, y, w: 8.0, h: 0.82, isTextBox: true, margin: 0, valign: 'middle',
      fontFace: BODY, fontSize: 13.5, color: INK,
    });
  });
  s.addNotes('Say these plainly. An examiner who finds a limitation you did not name trusts nothing else you said.');
}

// ---- 15 · future work ------------------------------------------------------
{
  const s = lightSlide('The next step is small and decisive', 'FUTURE WORK');
  s.addShape(pres.ShapeType.roundRect, {
    x: M, y: 1.95, w: 11.8, h: 1.5, rectRadius: 0.12,
    fill: { color: NAVY }, line: { color: NAVY },
  });
  s.addText('A few hundred human-annotated clips would convert every agreement figure in this project into a measure of validity.', {
    x: M + 0.4, y: 2.25, w: 11.0, h: 0.95, isTextBox: true, margin: 0,
    fontFace: HEAD, fontSize: 20, color: 'FFFFFF', italic: true, lineSpacing: 28,
  });
  bullets(s, [
    'Persist per-family candidate lists so the CLIP-pair inflation can be measured rather than declared.',
    'Replace equal weighting with measured per-source reliability weights.',
    'Add an audio-capable model to the benchmark, and a video-native one.',
    'Re-annotate the shot-boundary partition — 72.2% of published clips span at least one shot cut.',
    'Gate the ASR stage on Whisper’s own language identification, and add speaker diarisation.',
  ], { x: M, y: 3.75, w: 11.8, h: 3.0 });
  s.addNotes('Lead with the human-annotation item — it is the one that unlocks everything else.');
}

// ---- 16 · close ------------------------------------------------------------
{
  const s = darkSlide();
  s.addText('The contribution is not better metadata.\nIt is metadata that tells you how much to trust it.', {
    x: M, y: 2.4, w: 11.0, h: 1.8, isTextBox: true, margin: 0,
    fontFace: HEAD, fontSize: 30, bold: true, color: 'FFFFFF', lineSpacing: 44,
  });
  s.addText('626 clips · five fields · every published value carrying its evidence status, its supporting models and an auditable agreement score.', {
    x: M, y: 4.45, w: 10.4, h: 0.9, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 15, color: 'CADCFC', lineSpacing: 23,
  });
  s.addText('Saurav Kumar Vellattuparambil Vijayakumar · 40490925 · Supervisor: Dr Awais Rauf', {
    x: M, y: 5.9, w: 11.0, h: 0.4, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 13, color: 'FFFFFF',
  });
  s.addNotes('Close on this line, then thank the viewer. Do not add new information here.');
}

pres.writeFile({ fileName: 'docs/slides/demo_deck.pptx' })
  .then((f) => console.log('wrote', f));
