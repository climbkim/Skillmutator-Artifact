"""Plot Figure 4 (IER dynamics) with a broken y-axis, as in the camera-ready paper.

Reads:
  derived/ier_dynamics.csv   (or any rate table from compute_ier_dynamics.py: --csv)

Outputs (default ../results/):
  fig4_ier_dynamics.pdf / .png

Paper settings: break (45, 68), HEIGHT_SCALE=0.72, ANN_FS=7.5, COMPACT=True.
Layout: 1 row x 3 cols (oracle), each col split top/bottom (broken y-axis).
Colors: per scanner identity (ss, snyk, llm).
Line styles: rule-based (ss, snyk) = dashed; LLM-based (llm) = solid.
Iter labels: iter 1 ~ iter 5 (1-indexed display).
"""
import argparse
import csv
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import gridspec

DATA = Path(__file__).resolve().parents[1]                 # claims/claim09_ier_dynamics/data
HEIGHT_SCALE = 0.72
OFF = 1.0      # scale for annotation point offsets
ANN_FS = 7.5   # annotation font size
CSV_IN = DATA / "derived" / "ier_dynamics.csv"
OUT_DIR = DATA.parent / "results"

ORACLES = ["gpt-4o-mini", "gpt-5.4-mini", "gpt-5.4"]
ORACLE_TITLES = {
    "gpt-4o-mini": "GPT-4o-mini oracle",
    "gpt-5.4-mini": "GPT-5.4-mini oracle",
    "gpt-5.4": "GPT-5.4 oracle",
}
SCANNERS = ["ss", "snyk", "llm"]
SCANNER_LABELS = {
    "ss": "skill-security-scan",
    "snyk": "Snyk Agent Scan",
    "llm": "LLM scanner (self)",
}
SCANNER_COLORS = {
    "ss":   "#d62728",   # red
    "snyk": "#1f77b4",   # blue
    "llm":  "#2ca02c",   # green
}
SCANNER_STYLES = {
    "ss":   "--",
    "snyk": "--",
    "llm":  "-",
}
SCANNER_MARKERS = {
    "ss":   "s",
    "snyk": "^",
    "llm":  "o",
}

# Annotation placement (in axis coords + points offset).
ANN_Y_BASE = 7
ANN_Y_BUMP = 14
ANN_CLOSE_PP = 5.0
ANN_X_OFFSET = 3
ANN_Y_TIGHT = 2

# Iter indices used internally (data column "iter" is 0..4).
ITER_VALS = [0, 1, 2, 3, 4]
# Display labels (1-indexed per user decision: iter 0..4 -> iter 1..5).
ITER_LABELS = ["iter\\,1", "iter\\,2", "iter\\,3", "iter\\,4", "iter\\,5"]


COMPACT = True
BOT_BOOST = 2.0
CLOSE_PP = 10.0


def compact_place(oracle, sc, it, yv, data):
    """Label placement for the height-reduced figure (offsets in points, before OFF scaling)."""
    by = {s: dict(data[oracle][s]) for s in SCANNERS}
    ss, sn = by["ss"].get(it), by["snyk"].get(it)
    close = ss is not None and sn is not None and abs(sn - ss) < CLOSE_PP
    side = it in (0, 4)
    sx, sha = ((-9, "right") if it == 0 else (9, "left")) if side else (0, "center")
    if sc == "llm":
        if side:
            return sx, 0, sha, "center"
        if yv >= 80:
            return 0, -6, "center", "top"
        return 0, 6, "center", "bottom"
    if sc == "snyk":
        if side:
            return (sx, 3, sha, "bottom") if close else (sx, 0, sha, "center")
        return 0, 6, "center", "bottom"
    # skill-security-scan
    if side:
        return (sx, -3, sha, "top") if close else (sx, 0, sha, "center")
    if close and ss >= 6:
        return 0, -5, "center", "top"
    if close:
        return 8, 0, "left", "center"
    return 0, 6, "center", "bottom"


def load(csv_path=None):
    """Returns dict[oracle][scanner] -> list of (iter, rate%)."""
    if csv_path is None:
        csv_path = CSV_IN
    data = {o: {s: [] for s in SCANNERS} for o in ORACLES}
    with Path(csv_path).open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            o = r["oracle"]
            s = r["scanner"]
            if o in data and s in data[o]:
                n, d = int(r["n"]), int(r["detected"])
                data[o][s].append((int(r["iter"]), 100.0 * d / n if n else 0.0))
    for o in data:
        for s in data[o]:
            data[o][s].sort()
    return data


def plot_oracle_panel(ax_top, ax_bot, oracle, data, break_low, break_high, ann_iters):
    """Plot one oracle panel with broken y-axis (top + bottom subplot pair)."""
    # Plot identical data on both axes; matplotlib auto-clips to ylim.
    for sc in SCANNERS:
        pts = data[oracle][sc]
        if not pts:
            continue
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        for ax in (ax_top, ax_bot):
            ax.plot(
                xs, ys,
                color=SCANNER_COLORS[sc],
                linestyle=SCANNER_STYLES[sc],
                marker=SCANNER_MARKERS[sc],
                markersize=6,
                linewidth=1.6,
                label=SCANNER_LABELS[sc] if ax is ax_top else None,
            )

    # Annotate i0, i3, i4 on whichever pane the point falls into.
    ss_y_by_iter = dict(data[oracle].get("ss", []))

    ann_placement = {
        0: (-ANN_X_OFFSET - 4, "right"),
        1: (0, "center"),
        2: (0, "center"),
        3: (0, "center"),
        4: (ANN_X_OFFSET + 4, "left"),
    }

    custom_overrides = {
        ("gpt-5.4", "llm", 0): (0, -ANN_Y_BASE - 2, "center", "top"),

        ("gpt-5.4-mini", "snyk", 1): (0, ANN_Y_BUMP, "center", "bottom"),
        ("gpt-5.4-mini", "ss", 1):   (0, ANN_Y_BASE+10, "center", "bottom"),
        ("gpt-5.4-mini", "snyk", 2): (0, ANN_Y_BUMP+3, "center", "bottom"),
        ("gpt-5.4-mini", "ss", 2):   (0, ANN_Y_BASE+5, "center", "bottom"),
        ("gpt-5.4-mini", "snyk", 3): (0, ANN_Y_BUMP+1, "center", "bottom"),
        ("gpt-5.4-mini", "ss", 3):   (0, ANN_Y_BASE+6, "center", "bottom"),
        ("gpt-5.4-mini", "snyk", 4): (0, ANN_Y_BUMP, "center", "bottom"),
        ("gpt-5.4-mini", "ss", 4):   (0, ANN_Y_BASE+10, "center", "bottom"),

        ("gpt-5.4", "snyk", 1): (0, ANN_Y_BUMP+1.5,  "center", "bottom"),
        ("gpt-5.4", "ss", 1):   (0, ANN_Y_BASE+8.5, "center", "bottom"),
        ("gpt-5.4", "snyk", 2): (0, ANN_Y_BUMP+2, "center", "bottom"),
        ("gpt-5.4", "ss", 2):   (0, ANN_Y_BASE+2.8, "center", "bottom"),
        ("gpt-5.4", "snyk", 3): (0, ANN_Y_BUMP, "center", "bottom"),
        ("gpt-5.4", "ss", 3):   (0, ANN_Y_BASE-1.5, "center", "bottom"),
        ("gpt-5.4", "snyk", 4): (0, ANN_Y_BUMP, "center", "bottom"),
        ("gpt-5.4", "ss", 4):   (0, ANN_Y_BASE+8, "center", "bottom"),
    }

    ss_y_by_iter = dict(data[oracle].get("ss", []))



    for sc in SCANNERS:
        pts = data[oracle][sc]
        if not pts:
            continue
        pts_by_iter = dict(pts)
        color = SCANNER_COLORS[sc]
        for it in ann_iters:
            if it not in pts_by_iter:
                continue
            yv = pts_by_iter[it]
            
            if yv >= break_high:
                ax = ax_top
            elif yv <= break_low:
                ax = ax_bot
            else:
                continue
                
            x_off, ha = ann_placement[it]
            y_off = ANN_Y_BASE
            va = "bottom"

            if sc == "llm":
                y_off = ANN_Y_BASE + 2
                va = "bottom"
            else:
                if yv >= 90:
                    y_off = -ANN_Y_BASE
                    va = "top"
                elif sc == "snyk":
                    other = ss_y_by_iter.get(it)
                    if other is not None and abs(yv - other) < ANN_CLOSE_PP:
                        y_off = ANN_Y_BUMP

            if COMPACT:
                x_off, y_off, ha, va = compact_place(oracle, sc, it, yv, data)
            elif (oracle, sc, it) in custom_overrides:
                cx, cy, cha, cva = custom_overrides[(oracle, sc, it)]
                if it in (0, 4):
                    cx, cha = ann_placement[it]
                x_off, y_off, ha, va = cx, cy, cha, cva

            ax.annotate(
                f"{yv:.1f}",
                xy=(it, yv),
                xytext=(x_off * OFF, y_off * OFF),
                textcoords="offset points",
                fontsize=ANN_FS,
                color=color,
                ha=ha,
                va=va,
                fontweight="bold",
            )

            
    # Y-axis ranges
    ax_top.set_ylim(break_high, 100)
    ax_bot.set_ylim(0, break_low)

    # Hide adjacent spines for break effect
    ax_top.spines["bottom"].set_visible(False)
    ax_bot.spines["top"].set_visible(False)
    ax_top.tick_params(axis="x", which="both", bottom=False, labelbottom=False)
    ax_bot.tick_params(axis="x", which="both", top=False)

    # Break markers (diagonal lines)
    d = 0.018
    kwargs = dict(transform=ax_top.transAxes, color="k", clip_on=False, linewidth=1)
    ax_top.plot((-d, +d), (-d, +d), **kwargs)
    ax_top.plot((1 - d, 1 + d), (-d, +d), **kwargs)
    kwargs["transform"] = ax_bot.transAxes
    ax_bot.plot((-d, +d), (1 - d, 1 + d), **kwargs)
    ax_bot.plot((1 - d, 1 + d), (1 - d, 1 + d), **kwargs)

    # x ticks and labels (only on bottom)
    ax_bot.set_xticks(ITER_VALS)
    ax_bot.set_xticklabels([lbl.replace("\\,", " ") for lbl in ITER_LABELS], fontsize=9)
    xl = (-0.85, 4.85) if COMPACT else (-0.6, 4.6)
    ax_bot.set_xlim(*xl)
    ax_top.set_xlim(*xl)

    # Grid
    for ax in (ax_top, ax_bot):
        ax.grid(True, axis="y", alpha=0.3, linestyle=":")
        ax.set_axisbelow(True)

    ax_top.set_title(ORACLE_TITLES[oracle], fontsize=11)


def make_figure(break_low, break_high, out_pdf, out_png, suffix="", csv_path=None):
    data = load(csv_path)
    fig = plt.figure(figsize=(11.5, 3.0 * HEIGHT_SCALE))
    # height_ratios reflect zone heights for visual proportion.
    top_h = max(1.0, 100 - break_high)
    bot_h = max(1.0, break_low) * (BOT_BOOST if COMPACT else 1.0)
    gs = gridspec.GridSpec(
        2, 3,
        height_ratios=[top_h, bot_h],
        hspace=0.10,
        wspace=0.10,
        left=0.07, right=0.99, top=0.92, bottom=0.20,
    )

    axes_top = []
    axes_bot = []
    for col, oracle in enumerate(ORACLES):
        ax_top = fig.add_subplot(gs[0, col])
        ax_bot = fig.add_subplot(gs[1, col])
        axes_top.append(ax_top)
        axes_bot.append(ax_bot)
        ann_iters = [0, 1, 2, 3, 4]
        plot_oracle_panel(ax_top, ax_bot, oracle, data, break_low, break_high, ann_iters)
        # Hide y-tick labels on middle/right panels (sharey-like effect).
        if col > 0:
            ax_top.tick_params(axis="y", labelleft=False)
            ax_bot.tick_params(axis="y", labelleft=False)

    # Shared y-label on leftmost panel
    fig.text(
        0.015, 0.52,
        "Detection rate (%)",
        rotation=90, ha="center", va="center", fontsize=10,
    )

    # Single legend at bottom
    handles, labels = axes_top[0].get_legend_handles_labels()
    fig.legend(
        handles, labels,
        loc="lower center",
        ncol=3,
        bbox_to_anchor=(0.5, -0.05),
        frameon=False,
        fontsize=9.5,
    )

    fig.savefig(out_pdf, bbox_inches="tight")
    fig.savefig(out_png, bbox_inches="tight", dpi=150)
    plt.close(fig)
    print(f"wrote {out_pdf}")
    print(f"wrote {out_png}")


BREAK = (45, 68)   # rule-based + gpt-4o-mini LLM below the break, gpt-5.4(-mini) LLM above


def main():
    ap = argparse.ArgumentParser(description="Plot Figure 4 (IER dynamics).")
    ap.add_argument("--csv", type=Path, default=CSV_IN, help="rate table (oracle,iter,scanner,n,detected,rate_pct)")
    ap.add_argument("--out-dir", type=Path, default=OUT_DIR)
    a = ap.parse_args()
    a.out_dir.mkdir(parents=True, exist_ok=True)
    stem = a.out_dir / "fig4_ier_dynamics"
    make_figure(
        break_low=BREAK[0],
        break_high=BREAK[1],
        out_pdf=stem.with_suffix(".pdf"),
        out_png=stem.with_suffix(".png"),
        csv_path=a.csv,
    )


if __name__ == "__main__":
    main()
