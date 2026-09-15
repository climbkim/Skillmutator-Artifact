"""Generate Option A (Grouped Bar) + Option B (Delta Plot) for Table 6 viz.

Output: prefill_delta_figures/
  - option_a_grouped_bar.png
  - option_b_delta_plot.png

Source data: paper.tex Table tab:prefill_delta_comparison
"""
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
from pathlib import Path

OUT_DIR = Path(__file__).resolve().parent

# ─────────────────────────────────────────────────────────────────────
# IEEE / USENIX / CCS / S&P paper figure style
# (serif font matching paper body text, minimal bold, restrained palette)
# ─────────────────────────────────────────────────────────────────────
mpl.rcParams.update({
    "font.family":      "serif",
    "font.serif":       ["Times New Roman", "Liberation Serif", "STIX", "DejaVu Serif"],
    "mathtext.fontset": "stix",
    "font.size":        13,
    "axes.titlesize":   15,
    "axes.labelsize":   14,
    "axes.titleweight": "normal",
    "axes.spines.top":  False,
    "axes.spines.right": False,
    "xtick.labelsize":  12,
    "ytick.labelsize":  13,
    "legend.fontsize":  12,
    "legend.frameon":   True,
    "legend.framealpha": 1.0,
    "legend.edgecolor": "0.4",
    "legend.fancybox":  False,
    "axes.linewidth":   0.8,
    "xtick.major.width": 0.8,
    "ytick.major.width": 0.8,
    "grid.linewidth":   0.5,
    "lines.linewidth":  1.5,
    "savefig.bbox":     "tight",
    "savefig.dpi":      300,
})

# ─────────────────────────────────────────────────────────────────────
# Data (from paper.tex Table tab:prefill_delta_comparison)
# ─────────────────────────────────────────────────────────────────────
MODELS = ["Qwen2.5-Coder-7B-Instruct", "Llama-3.1-8B-Instruct",
          "Mistral-7B-Instruct-v0.3", "Gemma-2-9b-it"]
# Two-line full names so labels can stay horizontal (no rotation).
MODELS_SHORT = [
    "Qwen2.5\nCoder-7B-Instruct",
    "Llama-3.1\n8B-Instruct",
    "Mistral\n7B-Instruct-v0.3",
    "Gemma-2\n9b-it",
]

# GPT-5.4 judge: Base, no-prefill, prefill
gpt_base    = [17.1,  7.9,  5.3, 10.5]
gpt_noprefx = [79.0, 82.9, 72.4, 59.2]
gpt_prefx   = [88.2, 75.0, 55.3, 56.6]

# Claude judge: Base, no-prefill, prefill
cla_base    = [ 7.9,  2.6,  5.3,  6.6]
cla_noprefx = [75.0, 88.2, 68.4, 68.4]
cla_prefx   = [85.5, 76.3, 55.3, 69.7]

# Frontier GPT-5.4 reference
GPT54_GPT_JUDGE    = 86.8
GPT54_CLAUDE_JUDGE = 81.6

# Restrained palette in line with USENIX/CCS/S&P paper conventions
# (lightly colored, color-blind safe, prints readable in grayscale).
COL_BASE   = "#bdbdbd"   # neutral light gray
COL_NOPFX  = "#4c72b0"   # muted blue (seaborn deep)
COL_PFX    = "#dd8452"   # muted terracotta (seaborn deep)
COL_REF    = "#222222"   # near-black for reference line


def option_a_grouped_bar(legend_loc="upper left", out_name="option_a_grouped_bar"):
    """Grouped bar chart: 4 models × 3 modes × 2 judges (2 subplots).

    legend_loc: 'upper left' (default) or 'upper right'.
        - upper left: legend in GPT panel; frontier label on right.
        - upper right: legend in Claude panel (avoids Qwen prefill bar);
                       frontier label moved to left side to avoid overlap.
    """
    fig, axes = plt.subplots(1, 2, figsize=(15, 5.5), sharey=True)  # larger for readability
    x = np.arange(len(MODELS))
    width = 0.26

    # frontier label position depends on legend location
    # Frontier label: always right side (Gemma above), same position as option_a
    label_x, label_ha = len(MODELS) - 0.5, "right"
    label_y_off = 1.5
    if legend_loc == "upper right":
        ymax = 120  # extra headroom for upper-right legend (above Llama 88.2 bar in Claude panel)
    else:
        ymax = 112

    for ax, (title, base, nopfx, pfx, ref) in zip(
        axes,
        [("GPT-5.4 judge", gpt_base, gpt_noprefx, gpt_prefx, GPT54_GPT_JUDGE),
         ("Claude-Opus-4.7 judge", cla_base, cla_noprefx, cla_prefx, GPT54_CLAUDE_JUDGE)]
    ):
        b1 = ax.bar(x - width, base,  width, label="Base (no fine-tune)",   color=COL_BASE,  edgecolor=COL_REF, linewidth=0.4)
        b2 = ax.bar(x,         nopfx, width, label="Fine-tuned, no-prefill", color=COL_NOPFX, edgecolor=COL_REF, linewidth=0.4)
        b3 = ax.bar(x + width, pfx,   width, label="Fine-tuned, prefill",    color=COL_PFX,   edgecolor=COL_REF, linewidth=0.4)

        # frontier GPT-5.4 reference line — bold black to emphasize baseline.
        # Low zorder so bar value labels render on top (not obscured by the dashed line).
        ax.axhline(ref, ls="--", lw=1.6, color="black", alpha=1.0, zorder=1.5)
        ax.text(label_x, ref + label_y_off, f"GPT-5.4 baseline: {ref}%",
                ha=label_ha, va="bottom", color="black",
                fontsize=13, fontweight="bold", zorder=6)

        # numeric labels on top of bars.
        # If a bar's top is within ±3pp of the baseline, push its label higher
        # (above the dashed line) to avoid the label sitting on the line.
        from matplotlib import patheffects as _pe
        for bars in (b1, b2, b3):
            for rect in bars:
                h = rect.get_height()
                if abs(h - ref) < 5:
                    label_y = max(h, ref) + 4.5  # nudge clear of the baseline line
                else:
                    label_y = h + 1.5
                t = ax.text(rect.get_x() + rect.get_width()/2, label_y, f"{h:.1f}",
                            ha="center", va="bottom", fontsize=11, color=COL_REF,
                            zorder=5)
                t.set_path_effects([_pe.withStroke(linewidth=2.5, foreground="white")])

        ax.set_xticks(x)
        ax.set_xticklabels(MODELS_SHORT, rotation=0, ha="center")
        ax.set_title(title)
        ax.set_ylim(0, ymax)  # extra headroom for legend + frontier label
        ax.set_yticks([0, 20, 40, 60, 80, 100])  # hide 120 tick (visual cleanliness)
        ax.grid(axis="y", ls=":", alpha=0.4)
        ax.set_axisbelow(True)

    axes[0].set_ylabel("Detection rate (%)", fontsize=14)
    # Legend placement
    if legend_loc == "upper right":
        # Each panel gets its own legend at upper-right (panel-local, self-contained)
        for ax in axes:
            ax.legend(loc="upper right", fontsize=9, framealpha=0.95,
                      ncol=1, borderaxespad=0.5)
    else:
        # Default: single legend in GPT panel upper-left (option_a)
        axes[0].legend(loc="upper left", fontsize=9, framealpha=0.95,
                       ncol=1, borderaxespad=0.5)
    fig.tight_layout()
    fig.savefig(OUT_DIR / f"{out_name}.png", dpi=200, bbox_inches="tight")
    fig.savefig(OUT_DIR / f"{out_name}.pdf", bbox_inches="tight")
    plt.close(fig)
    print(f"[saved] {out_name}.{{png,pdf}}")


def option_b_delta_plot():
    """Delta plot: prefill effect (Δ = prefill − no-prefill) per model × judge."""
    fig, ax = plt.subplots(figsize=(8, 4.5))
    x = np.arange(len(MODELS))
    width = 0.34

    delta_gpt = [p - n for p, n in zip(gpt_prefx, gpt_noprefx)]
    delta_cla = [p - n for p, n in zip(cla_prefx, cla_noprefx)]

    b1 = ax.bar(x - width/2, delta_gpt, width, label="GPT-5.4 judge",       color=COL_NOPFX, edgecolor=COL_REF, linewidth=0.4)
    b2 = ax.bar(x + width/2, delta_cla, width, label="Claude-Opus-4.7 judge", color=COL_PFX,   edgecolor=COL_REF, linewidth=0.4)

    # zero line
    ax.axhline(0, lw=0.8, color=COL_REF)

    # noise zone (±3pp) shaded
    ax.axhspan(-3, 3, alpha=0.10, color="gray", label="$\\pm 3$\\,pp noise zone")

    # numeric labels (no bold)
    for bars in (b1, b2):
        for rect in bars:
            h = rect.get_height()
            va = "bottom" if h >= 0 else "top"
            off = 0.4 if h >= 0 else -0.4
            ax.text(rect.get_x() + rect.get_width()/2, h + off,
                    f"{h:+.1f}", ha="center", va=va, fontsize=7.5, color=COL_REF)

    ax.set_xticks(x)
    ax.set_xticklabels(MODELS_SHORT)
    ax.set_ylabel("$\\Delta$ = prefill $-$ no-prefill (pp)")
    ax.set_title("Phase~4 prefill effect by base-model family")
    ax.set_ylim(-22, 16)
    ax.grid(axis="y", ls=":", alpha=0.4)
    ax.set_axisbelow(True)
    ax.legend(loc="lower right")

    fig.tight_layout()
    fig.savefig(OUT_DIR / "option_b_delta_plot.png", dpi=200, bbox_inches="tight")
    fig.savefig(OUT_DIR / "option_b_delta_plot.pdf", bbox_inches="tight")
    plt.close(fig)
    print(f"[saved] option_b_delta_plot.{{png,pdf}}")


if __name__ == "__main__":
    option_a_grouped_bar(legend_loc="upper left",
                         out_name="option_a_grouped_bar")
    option_a_grouped_bar(legend_loc="upper right",
                         out_name="option_a_grouped_bar_legend_right")
    option_b_delta_plot()
    print(f"\nOutput dir: {OUT_DIR}")
