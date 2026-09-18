"""
Render the four result figures for the conference paper.

Every value is transcribed from the paper's own result tables (III to VII) and
nothing is recomputed here, so a figure can never disagree with its table.
Output is 600 dpi PNG for the .docx build plus PDF for a LaTeX build.

    python docs/figures/make_figures.py
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch

OUT = Path(__file__).parent

# IEEE two-column geometry.
COL, FULL = 3.5, 7.16

# Validated palette (dataviz reference instance, light mode).
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
TIER = ["#1c5cab", "#3987e5", "#86b6ef", "#c9c8c3"]   # ordinal ramp + neutral
INK, INK2, GRID = "#0b0b0b", "#52514e", "#d8d7d2"
SURFACE = "#ffffff"

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["DejaVu Serif"],
    "font.size": 7.2,
    "axes.labelsize": 7.2,
    "axes.titlesize": 7.6,
    "xtick.labelsize": 6.8,
    "ytick.labelsize": 6.8,
    "legend.fontsize": 6.6,
    "axes.edgecolor": GRID,
    "axes.linewidth": 0.6,
    "text.color": INK,
    "axes.labelcolor": INK2,
    "xtick.color": INK2,
    "ytick.color": INK2,
    "figure.facecolor": SURFACE,
    "axes.facecolor": SURFACE,
    "savefig.facecolor": SURFACE,
})


def tidy(ax, axis="y"):
    """Recessive grid on one axis only, no top/right spines."""
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.grid(axis=axis, color=GRID, linewidth=0.5, alpha=0.9)
    ax.set_axisbelow(True)
    ax.tick_params(length=2, width=0.6)


def save(fig, name):
    for ext, dpi in (("png", 600), ("pdf", None)):
        fig.savefig(OUT / f"{name}.{ext}", dpi=dpi, bbox_inches="tight",
                    pad_inches=0.02)
    plt.close(fig)
    print("wrote", name)


# --- Fig. 1 -- Table IV: agreement-tier distribution by field ---------------
def fig1():
    fields = ["On-screen text", "Keywords", "Visual tags",
              "Transcript", "People count"]          # worst to best, bottom-up
    tiers = ["High ≥ 0.75", "Moderate ≥ 0.50", "Low < 0.50",
             "Not scored"]
    data = np.array([                                 # rows: field, cols: tier
        [0.000, 0.005, 0.462, 0.534],
        [0.002, 0.005, 0.990, 0.003],
        [0.026, 0.511, 0.463, 0.000],
        [0.722, 0.045, 0.230, 0.003],
        [0.625, 0.174, 0.109, 0.093],
    ])
    means = [0.156, 0.173, 0.509, 0.680, 0.812]
    hatches = ["", "", "", "///"]                     # print/CVD relief

    fig, ax = plt.subplots(figsize=(COL, 2.35))
    left = np.zeros(len(fields))
    for j, tier in enumerate(tiers):
        ax.barh(fields, data[:, j], left=left, height=0.62, color=TIER[j],
                edgecolor=SURFACE, linewidth=1.1, hatch=hatches[j],
                label=tier, zorder=3)
        for i, v in enumerate(data[:, j]):            # selective direct labels
            if v >= 0.16:
                ax.text(left[i] + v / 2, i, f"{v:.2f}".lstrip("0"),
                        ha="center", va="center", fontsize=6.2,
                        color=SURFACE if j < 2 else INK, zorder=4)
        left += data[:, j]

    for i, m in enumerate(means):                     # mean agreement, at right
        ax.text(1.015, i, f"{m:.3f}", ha="left", va="center", fontsize=6.6,
                color=INK, fontweight="bold")
    ax.text(1.015, len(fields) - 0.42, "mean", ha="left", va="center",
            fontsize=6.0, color=INK2)

    ax.set_xlim(0, 1)
    ax.set_xlabel("Proportion of 626 clips")
    tidy(ax, axis="x")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.26), ncol=4,
              frameon=False, handlelength=1.1, columnspacing=1.0,
              handletextpad=0.4)
    save(fig, "fig1_agreement_tiers")


# --- Fig. 2 -- Table VII: VLM agreement, one panel per field ----------------
def fig2():
    # Abbreviated in-figure; the caption expands them.
    models = ["Qwen 2B-I", "Qwen 2B-T", "Qwen 4B-I", "Qwen 4B-T",
              "Qwen 8B-I\u2020", "IVL3-2B", "IVL3-8B\u2020"][::-1]
    panels = [
        ("On-screen text", [0.383, 0.384, 0.456, 0.389, 0.431, 0.544, 0.416]),
        ("Visual tags",    [0.871, 0.874, 0.880, 0.873, 0.876, 0.890, 0.883]),
        ("People count",   [0.233, 0.323, 0.241, 0.315, 0.232, 0.417, 0.366]),
        ("Keywords",       [0.039, 0.028, 0.030, 0.040, 0.036, 0.031, 0.027]),
        ("Transcript",     [0.034, 0.018, 0.000, 0.019, 0.000, 0.000, 0.013]),
    ]
    lead = models.index("IVL3-2B")

    fig, axes = plt.subplots(2, 3, figsize=(COL, 2.95), sharex=True)
    y = np.arange(len(models))
    for k, (title, vals) in enumerate(panels):
        ax = axes[k // 3][k % 3]
        vals = vals[::-1]
        for yi, v in zip(y, vals):
            top = yi == lead
            ax.barh(yi, v, height=0.70,
                    color=ORANGE if top else BLUE, edgecolor=SURFACE,
                    linewidth=0.7, hatch="xx" if top else "", zorder=3)
        best = int(np.argmax(vals))
        ax.text(vals[best] + 0.06, best, f"{vals[best]:.3f}".lstrip("0"),
                va="center", ha="left", fontsize=6.0, color=INK,
                fontweight="bold")
        ax.set_title(title, color=INK, pad=3, fontsize=6.8)
        ax.set_xlim(0, 1.16)
        ax.set_xticks([0, 0.5, 1.0])
        ax.set_xticklabels(["0", ".5", "1"])
        ax.set_ylim(-0.7, len(models) - 0.3)
        tidy(ax, axis="x")
        ax.tick_params(axis="y", length=0)
        if k % 3 == 0:
            ax.set_yticks(y)
            ax.set_yticklabels(models, fontsize=6.2)
        else:
            ax.set_yticks([])

    legend_ax = axes[1][2]                             # sixth cell -> legend
    legend_ax.axis("off")
    legend_ax.legend(handles=[
        Patch(facecolor=ORANGE, hatch="xx", edgecolor=SURFACE,
              label="InternVL3-2B\n(smallest; leads\n3 of 5 fields)"),
        Patch(facecolor=BLUE, edgecolor=SURFACE, label="all others")],
        loc="center", frameon=False, handlelength=1.0, fontsize=6.0,
        labelspacing=0.9, handletextpad=0.5, borderpad=0)
    fig.supxlabel("Agreement with pipeline consensus", fontsize=6.8,
                  color=INK2, y=0.005)
    fig.subplots_adjust(hspace=0.30, wspace=0.16)
    save(fig, "fig2_vlm_benchmark")


# --- Fig. 3 -- Table V: field-dependent robustness --------------------------
def fig3():
    perts = ["Gaussian\nblur", "JPEG\nquality 25", "Low\nbrightness"]
    series = [("On-screen text", [0.0714, 0.1111, 0.3000], BLUE, ""),
              ("Visual tags",    [0.96, 0.80, 0.84],       ORANGE, "//"),
              ("People count",   [0.5742, 0.6207, 0.5742], AQUA, "xx")]

    fig, ax = plt.subplots(figsize=(COL, 2.1))
    x, w = np.arange(len(perts)), 0.26
    for k, (label, vals, colour, hatch) in enumerate(series):
        pos = x + (k - 1) * w
        ax.bar(pos, vals, width=w * 0.92, color=colour, edgecolor=SURFACE,
               linewidth=0.9, hatch=hatch, label=label, zorder=3)
        for xi, v in zip(pos, vals):
            ax.text(xi, v + 0.03, f"{v:.2f}".lstrip("0"), ha="center",
                    fontsize=6.0, color=INK)

    ax.annotate("", xy=(-0.56, 0.96), xytext=(-0.56, 0.0714),
                arrowprops=dict(arrowstyle="<->", color=INK2, lw=0.7))
    ax.text(-0.51, 0.52, "13×", fontsize=6.6, color=INK,
            fontweight="bold", va="center", ha="left")

    ax.set_xlim(-0.72, len(perts) - 0.52)
    ax.set_xticks(x)
    ax.set_xticklabels(perts)
    ax.set_ylim(0, 1.12)
    ax.set_ylabel("Stability vs unperturbed evidence")
    tidy(ax)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.19), ncol=3,
              frameon=False, handlelength=1.1, columnspacing=1.0,
              handletextpad=0.4)
    save(fig, "fig3_robustness")


# --- Fig. 4 -- Table VI: hosted-annotator ablation --------------------------
def fig4():
    fields = ["On-screen text", "People count", "Visual tags"]
    agree = [0.5468, 0.8445, 0.4194]
    change = [0.0000, 0.0176, 0.4904]

    fig, ax = plt.subplots(figsize=(COL, 2.2))
    x, w = np.arange(len(fields)), 0.34
    ax.bar(x - w / 2, agree, width=w * 0.92, color=BLUE, edgecolor=SURFACE,
           linewidth=0.9, label="Agrees with local consensus", zorder=3)
    ax.bar(x + w / 2, change, width=w * 0.92, color=ORANGE, hatch="///",
           edgecolor=SURFACE, linewidth=0.9, label="Changes published output",
           zorder=3)
    for xi, v in zip(x - w / 2, agree):
        ax.text(xi, v + 0.03, f"{v:.3f}".lstrip("0"), ha="center",
                fontsize=6.2, color=INK)
    for xi, v in zip(x + w / 2, change):
        ax.text(xi, v + 0.03, f"{v:.3f}".lstrip("0"), ha="center",
                fontsize=6.2, color=INK)

    ax.axhline(0.5, color=INK2, linewidth=0.7, linestyle=(0, (4, 3)), zorder=2)
    ax.text(-0.46, 0.485, "half", fontsize=6.0, color=INK2, ha="left",
            va="top")
    ax.annotate("agrees less than half the time,\nyet rewrites half the tag sets",
                xy=(2 + w / 2 + 0.16, 0.42), xytext=(1.02, 1.04),
                fontsize=6.2, color=INK, ha="center",
                arrowprops=dict(arrowstyle="->", color=INK2, lw=0.7,
                                connectionstyle="arc3,rad=-0.15"))

    ax.set_xticks(x)
    ax.set_xticklabels(fields)
    ax.set_ylim(0, 1.22)
    ax.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_ylabel("Proportion of 626 clips")
    tidy(ax)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.13), ncol=2,
              frameon=False, handlelength=1.1, columnspacing=1.0,
              handletextpad=0.4)
    save(fig, "fig4_hosted_annotator")


if __name__ == "__main__":
    fig1(); fig2(); fig3(); fig4()
