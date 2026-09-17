"""Compute every outstanding [TO FILL] figure in one pass.

Run as a Colab cell after mounting Drive. Prints labelled blocks; paste the
output back and each block maps to one placeholder in the paper or report.
Each section is independent -- a failure in one prints and the rest continue.
"""
import json, re, sys, itertools
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path("/content/drive/MyDrive/NVTV_PublicData1/automatic_ground_truth_v4")
FIELDS = ("transcript", "on_screen_text", "keywords", "visual_tags", "people_count")


def block(title):
    print("\n" + "=" * 72); print(title); print("=" * 72)


def section(fn):
    try:
        fn()
    except Exception as exc:                      # keep going; report the failure
        print(f"  !! {type(exc).__name__}: {exc}")


def load_full_ground_truth():
    """Return the artefact that still carries the per-field consensus dicts."""
    for name in ("ground_truth_metadata.json",
                 "ground_truth_metadata_626.json",
                 "ground_truth_metadata_615.json",
                 "ground_truth_metadata_focused.json"):
        path = ROOT / name
        if not path.exists():
            continue
        payload = json.loads(path.read_text())
        clips = payload.get("clips", [])
        if not clips:
            continue
        sample = clips[0].get("ground_truth_metadata", {})
        keeps_dicts = any(isinstance(v, dict) and "agreement_score" in v
                          for v in sample.values())
        print(f"  {name}: {len(clips)} clips, consensus dicts = {keeps_dicts}")
        if keeps_dicts:
            return payload
    return None


# ---------------------------------------------------------------- RQ2
def rq2():
    block("RQ2 -- per-field evidence status and agreement  [paper IV-D, report D.5]")
    payload = load_full_ground_truth()
    if payload is None:
        print("  No artefact retains agreement data. Every candidate file is")
        print("  flattened by build_focused_ground_truth(). Re-run Section 14/15")
        print("  of the pipeline notebook and save the UNflattened payload.")
        return

    rows = []
    for clip in payload["clips"]:
        if clip.get("status") != "ok":
            continue
        for field, item in (clip.get("ground_truth_metadata") or {}).items():
            if field not in FIELDS or not isinstance(item, dict):
                continue
            rows.append({
                "field": field,
                "status": item.get("status", "?"),
                "tier": item.get("agreement_tier", "not_scored"),
                "score": item.get("agreement_score"),
                "caution": bool(item.get("needs_caution")),
                "n_support": len(item.get("support_models") or []),
            })
    df = pd.DataFrame(rows)
    if df.empty:
        print("  No scored fields found."); return
    print(f"\n  clips scored: {df.groupby('field').size().to_dict()}\n")

    print("-- status distribution (proportion) --")
    print(pd.crosstab(df["field"], df["status"], normalize="index").round(4))
    print("\n-- agreement tier distribution (proportion) --")
    print(pd.crosstab(df["field"], df["tier"], normalize="index").round(4))
    print("\n-- mean agreement score (scored fields only) --")
    print(df.dropna(subset=["score"]).groupby("field")["score"]
            .agg(["count", "mean", "std", "median"]).round(4))
    print("\n-- needs_caution rate, and mean supporting-source count --")
    print(df.groupby("field").agg(caution_rate=("caution", "mean"),
                                  mean_sources=("n_support", "mean")).round(4))


# -------------------------------------------- correlated-source audit
def independence():
    block("Source-independence audit  [report 3.6]")
    payload = load_full_ground_truth()
    if payload is None:
        print("  Needs the unflattened artefact (see RQ2 block)."); return

    pair_scores = defaultdict(list)
    for clip in payload["clips"]:
        if clip.get("status") != "ok":
            continue
        for field, item in (clip.get("ground_truth_metadata") or {}).items():
            if not isinstance(item, dict):
                continue
            cands = item.get("candidates")
            if not isinstance(cands, dict) or len(cands) < 2:
                continue
            for a, b in itertools.combinations(sorted(cands), 2):
                va, vb = cands[a], cands[b]
                if isinstance(va, list) and isinstance(vb, list):
                    sa = {str(x).lower().strip() for x in va}
                    sb = {str(x).lower().strip() for x in vb}
                    if not sa or not sb:
                        continue
                    f1 = 2 * len(sa & sb) / (len(sa) + len(sb))
                elif va is None or vb is None:
                    continue
                else:
                    f1 = float(str(va).strip().lower() == str(vb).strip().lower())
                pair_scores[(field, a, b)].append(f1)

    if not pair_scores:
        print("  No per-source candidate lists stored in the artefact.")
        print("  Fall back to: report mean agreement for visual_tags and")
        print("  transcript (correlated sources) against on_screen_text and")
        print("  people_count (unrelated sources), from the RQ2 table.")
        return
    out = pd.DataFrame(
        [{"field": f, "pair": f"{a} / {b}", "n": len(v), "mean_agreement": np.mean(v)}
         for (f, a, b), v in pair_scores.items()]
    ).sort_values(["field", "mean_agreement"], ascending=[True, False])
    print(out.round(4).to_string(index=False))
    print("\n  Compare CLIP ViT-B/32 vs ViT-L/14 and Whisper-small vs -turbo")
    print("  against any cross-architecture pair. The gap is the inflation factor.")


# ------------------------------------------------- language / fairness
def language():
    block("Non-English ASR detections  [report 6.3]")
    records = sorted(ROOT.glob("predictions_*.json"))
    records = [p for p in records if "qwen" not in p.name.lower()
               and "InternVL" not in p.name and "gemini" not in p.name.lower()]
    if not records:
        print("  predictions_<hash>.json not found under", ROOT); return
    payload = json.loads(records[0].read_text())
    print(f"  reading {records[0].name}")
    recs = payload.get("records", payload) if isinstance(payload, dict) else payload
    if isinstance(recs, dict):
        recs = list(recs.values())

    langs = Counter()
    non_english = []
    for r in recs:
        if not isinstance(r, dict):
            continue
        lang = ((r.get("asr") or {}).get("language")
                or (r.get("predictions", {}).get("common", {}) or {}).get("language") or "")
        lang = str(lang).strip().lower()
        if lang:
            langs[lang] += 1
            if lang not in {"en", "english"}:
                non_english.append((r.get("clip_id", "?"), lang))
    total = sum(langs.values())
    print(f"\n  clips with a language label: {total}")
    for lang, n in langs.most_common():
        print(f"    {lang:12s} {n:4d}  ({100*n/total:.1f}%)" if total else "")
    print(f"\n  non-English: {len(non_english)} clips"
          f"  ({100*len(non_english)/total:.1f}%)" if total else "")
    for clip_id, lang in non_english[:15]:
        print(f"    {lang:6s} {clip_id}")


# ------------------------------------------------------ tag frequency
def tags():
    block("Visual-tag frequency across the corpus  [report 6.1]")
    path = ROOT / "ground_truth_metadata_focused.csv"
    if not path.exists():
        print("  ground_truth_metadata_focused.csv not found"); return
    df = pd.read_csv(path)
    col = next((c for c in df.columns if "visual_tag" in c), None)
    if col is None:
        print("  no visual_tags column; columns are:", list(df.columns)); return
    counts = Counter()
    for cell in df[col].dropna():
        for tag in re.split(r"[;|]|,\s*(?=[a-z])", str(cell)):
            tag = tag.strip().strip("[]'\" ")
            if tag:
                counts[tag] += 1
    n = len(df)
    print(f"  clips: {n}\n")
    for tag, c in counts.most_common():
        print(f"    {tag:28s} {c:4d}  ({100*c/n:5.1f}% of clips)")
    fired = set(counts)
    print(f"\n  labels that never fire: {34 - len(fired)}")


# ----------------------------------------------------- split / bounds
def manifest_checks():
    block("Split integrity, clip boundaries, per-programme table  [report 3.1, 3.2, App. C]")
    m = pd.read_csv(ROOT / "clip_manifest.csv")

    cal = set(m.loc[m["split"] == "calibration", "source_id"])
    ev = set(m.loc[m["split"] == "evaluation", "source_id"])
    print(f"  calibration sources {len(cal)}, evaluation {len(ev)},"
          f" overlap {len(cal & ev)}  -> {'PASS' if not (cal & ev) else 'FAIL'}")

    drift = []
    for sid, g in m.sort_values(["source_id", "clip_index"]).groupby("source_id"):
        prev_end = None
        for row in g.itertuples(index=False):
            if prev_end is not None:
                drift.append(abs(row.start_sec - prev_end))
            prev_end = row.end_sec
    print(f"  boundary drift across {len(drift)} adjacent pairs:"
          f" max {max(drift):.4f}s, mean {np.mean(drift):.4f}s"
          f"  -> {'PASS' if max(drift) < 0.05 else 'CHECK'}")

    per = (m.groupby(["source_video", "split"])
             .agg(clips=("clip_id", "count"),
                  duration_s=("actual_duration_sec", "sum"))
             .reset_index().sort_values("source_video"))
    per["duration"] = per["duration_s"].map(lambda s: f"{int(s//60)}:{int(s%60):02d}")
    print(f"\n  Appendix C table ({len(per)} programmes):\n")
    print(per[["source_video", "duration", "clips", "split"]].to_string(index=False))


# ------------------------------------------- benchmark tier vacuity
def tier_charts():
    block("Benchmark agreement-tier charts  [report D.8 / item 20]")
    reports = sorted(ROOT.glob("qwen_vl_comparison/qwen_vl_accuracy_report__*.csv"))
    if not reports:
        print("  accuracy report not found"); return
    df = pd.read_csv(max(reports, key=lambda p: p.stat().st_size))
    counts = df["ground_truth_agreement_tier"].value_counts(normalize=True)
    print(f"  rows: {len(df)}")
    print(counts.round(4).to_string())
    if counts.get("not_scored", 0) > 0.95:
        print("\n  >95% not_scored -- the charts carry no signal. Report that the")
        print("  benchmark was scored against the FLATTENED ground truth, which")
        print("  build_focused_ground_truth() strips of agreement metadata, and")
        print("  drop the charts.")


for fn in (rq2, independence, language, tags, manifest_checks, tier_charts):
    section(fn)
print("\nDone.")
