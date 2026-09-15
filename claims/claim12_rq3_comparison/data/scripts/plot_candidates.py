"""Render 4 candidate visualizations for paper.tex Table VI (rq3_finding1).

Outputs: candidate_{1..4}.{pdf,png}

Data: GPT-5.4 oracle benchmark, n=76, select mode, GPT-5.4 judge.
"""
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
import numpy as np

ROOT = Path(__file__).resolve().parents[1] / "derived"  # self-relative: writes into <claim|rq>/derived/

# Detection rate data (% on n=76)
SCANNERS = [
    # (label, detected, rate, group)
    ("skill-security-scan",            6,  7.89, "rule"),
    ("Snyk Agent Scan",                7,  9.21, "rule"),
    ("GPT-4o-mini",                   18, 23.68, "proprietary"),
    ("GPT-5.4-mini",                  60, 78.95, "proprietary"),
    ("GPT-5.4",                       66, 86.84, "proprietary"),
    ("Qwen2.5-Coder-7B (base)",       13, 17.11, "ours_base"),
    ("Qwen2.5-Coder-7B (fine-tuned)", 61, 80.26, "ours_ft"),
]

# Color scheme — matches existing ier_dynamics (red/blue/green) where possible
GROUP_COLORS = {
    "rule":         "#999999",   # neutral grey for rule-based
    "proprietary":  "#1f77b4",   # blue for proprietary LLMs
    "ours_base":    "#d62728",   # muted red for our base
    "ours_ft":      "#d62728",   # same red for our fine-tuned (highlighted via hatch/edge)
}
GROUP_LABEL = {
    "rule":         "Rule-based / Commercial",
    "proprietary":  "Proprietary LLM",
    "ours_base":    "Open-source 7B (base)",
    "ours_ft":      "Open-source 7B (fine-tuned, ours)",
}


# ---------------------------------------------------------------------------
# Candidate 1: Horizontal bar chart, sorted, with Δ annotation between
#              Qwen-base and Fine-tuned bars.
# ---------------------------------------------------------------------------
def candidate_1():
    rows = sorted(SCANNERS, key=lambda r: r[2])
    fig, ax = plt.subplots(figsize=(5.5, 3.0))

    labels = [r[0] for r in rows]
    rates  = [r[2] for r in rows]
    groups = [r[3] for r in rows]
    colors = [GROUP_COLORS[g] for g in groups]

    y = np.arange(len(rows))
    bars = ax.barh(y, rates, color=colors, edgecolor="black", linewidth=0.4)

    # Hatch the "ours" fine-tuned bar so it pops in B&W as well
    for bar, g in zip(bars, groups):
        if g == "ours_ft":
            bar.set_hatch("///")
            bar.set_edgecolor("black")
            bar.set_linewidth(1.0)

    # Numeric labels at bar end
    for yi, (lab, det, rate, _) in zip(y, rows):
        ax.text(rate + 1.0, yi, f"{rate:.1f}%", va="center",
                fontsize=8.5, color="black")

    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=9)
    ax.set_xlabel("Detection rate (%)", fontsize=10)
    ax.set_xlim(0, 100)
    ax.grid(axis="x", linestyle=":", alpha=0.4)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # Δ annotation between Qwen-base (yi_base) and fine-tuned (yi_ft)
    yi_base = [i for i, (_, _, _, g) in enumerate(rows) if g == "ours_base"][0]
    yi_ft   = [i for i, (_, _, _, g) in enumerate(rows) if g == "ours_ft"][0]
    base_rate = rows[yi_base][2]
    ft_rate   = rows[yi_ft][2]
    delta = ft_rate - base_rate

    # Extend x-range to make room for the arrow + delta label outside the bars
    ax.set_xlim(0, 118)

    # Draw arrow on the right side of the bars connecting the two
    arrow_x = 105
    arrow = FancyArrowPatch((arrow_x, yi_base), (arrow_x, yi_ft),
                             arrowstyle="->", mutation_scale=14,
                             color="#d62728", linewidth=1.8)
    ax.add_patch(arrow)
    ax.annotate(f"+{delta:.1f} pp",
                xy=(arrow_x, (yi_base + yi_ft) / 2),
                xytext=(7, 0), textcoords="offset points",
                ha="left", va="center", fontsize=9,
                color="#d62728", fontweight="bold")

    # Legend — place at bottom of figure under the axes to avoid overlap
    handles = [plt.Rectangle((0, 0), 1, 1, color=GROUP_COLORS[g], ec="black",
                             lw=0.4, hatch=("///" if g == "ours_ft" else None))
               for g in ("rule", "proprietary", "ours_base", "ours_ft")]
    ax.legend(handles, [GROUP_LABEL[g] for g in
                        ("rule", "proprietary", "ours_base", "ours_ft")],
              loc="upper center", bbox_to_anchor=(0.5, -0.18),
              ncol=2, fontsize=7.5, frameon=False,
              handlelength=1.4, handletextpad=0.5, borderpad=0.3)

    fig.tight_layout()
    fig.savefig(ROOT / "candidate_1.pdf", bbox_inches="tight")
    fig.savefig(ROOT / "candidate_1.png", bbox_inches="tight", dpi=150)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Candidate 2: Dumbbell row for ours base→ft, single dots for the rest.
# ---------------------------------------------------------------------------
def candidate_2():
    fig, ax = plt.subplots(figsize=(5.5, 3.0))

    # Build ordered list: single-point scanners + a "ours" merged row
    singles = [r for r in SCANNERS
               if r[3] in ("rule", "proprietary")]
    base_row = [r for r in SCANNERS if r[3] == "ours_base"][0]
    ft_row   = [r for r in SCANNERS if r[3] == "ours_ft"][0]

    # Sort singles by rate ascending; insert "ours" between base and ft positions
    singles_sorted = sorted(singles, key=lambda r: r[2])

    # Choose vertical order: ascending overall by *fine-tuned* rate for "ours"
    # Place ours dumbbell at a position based on its midpoint
    ours_mid = (base_row[2] + ft_row[2]) / 2
    rows = singles_sorted + [("Qwen-7B (base → fine-tuned)",
                              None, ours_mid, "ours_dumbbell")]
    rows = sorted(rows, key=lambda r: r[2])

    y = np.arange(len(rows))
    for yi, (lab, det, rate, g) in zip(y, rows):
        if g == "ours_dumbbell":
            # Draw the dumbbell
            ax.plot([base_row[2], ft_row[2]], [yi, yi],
                    color="#d62728", linewidth=2.2, zorder=2)
            ax.scatter([base_row[2]], [yi], s=70,
                       facecolor="white", edgecolor="#d62728", linewidth=1.8,
                       zorder=3)
            ax.scatter([ft_row[2]],   [yi], s=85,
                       facecolor="#d62728", edgecolor="black", linewidth=0.6,
                       zorder=3)
            # Numeric labels
            ax.text(base_row[2] - 1.2, yi, f"{base_row[2]:.1f}",
                    ha="right", va="center", fontsize=8, color="#d62728")
            ax.text(ft_row[2] + 1.2,  yi, f"{ft_row[2]:.1f}",
                    ha="left",  va="center", fontsize=8.5,
                    color="#d62728", fontweight="bold")
        else:
            ax.scatter([rate], [yi], s=60, color=GROUP_COLORS[g],
                       edgecolor="black", linewidth=0.4, zorder=3)
            ax.text(rate + 1.2, yi, f"{rate:.1f}%",
                    ha="left", va="center", fontsize=8.5)

    ax.set_yticks(y)
    ax.set_yticklabels([r[0] for r in rows], fontsize=9)
    ax.set_xlabel("Detection rate (%)", fontsize=10)
    ax.set_xlim(0, 100)
    ax.grid(axis="x", linestyle=":", alpha=0.4)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # Mark the "ours" row
    ours_idx = [i for i, r in enumerate(rows) if r[3] == "ours_dumbbell"][0]
    ax.text(101, ours_idx, "ours", ha="left", va="center",
            fontsize=8.5, color="#d62728", fontweight="bold")

    fig.tight_layout()
    fig.savefig(ROOT / "candidate_2.pdf", bbox_inches="tight")
    fig.savefig(ROOT / "candidate_2.png", bbox_inches="tight", dpi=150)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Candidate 3: 2-panel — (left) bar of all scanners, (right) slope of ours.
# ---------------------------------------------------------------------------
def candidate_3():
    fig, (ax_l, ax_r) = plt.subplots(1, 2, figsize=(8.5, 3.0),
                                     gridspec_kw={"width_ratios": [3, 1]})

    # Left panel — horizontal bar of all 7 scanners
    rows = sorted(SCANNERS, key=lambda r: r[2])
    labels = [r[0] for r in rows]
    rates  = [r[2] for r in rows]
    groups = [r[3] for r in rows]
    colors = [GROUP_COLORS[g] for g in groups]

    y = np.arange(len(rows))
    bars = ax_l.barh(y, rates, color=colors, edgecolor="black", linewidth=0.4)
    for bar, g in zip(bars, groups):
        if g == "ours_ft":
            bar.set_hatch("///")
            bar.set_edgecolor("black")
            bar.set_linewidth(1.0)
    for yi, (lab, det, rate, _) in zip(y, rows):
        ax_l.text(rate + 1.0, yi, f"{rate:.1f}%", va="center", fontsize=8.5)

    ax_l.set_yticks(y)
    ax_l.set_yticklabels(labels, fontsize=9)
    ax_l.set_xlabel("Detection rate (%)", fontsize=10)
    ax_l.set_xlim(0, 100)
    ax_l.set_title("All scanners on n=76 benchmark", fontsize=10)
    ax_l.grid(axis="x", linestyle=":", alpha=0.4)
    ax_l.set_axisbelow(True)
    ax_l.spines["top"].set_visible(False)
    ax_l.spines["right"].set_visible(False)

    # Right panel — slope chart for ours
    base_row = [r for r in SCANNERS if r[3] == "ours_base"][0]
    ft_row   = [r for r in SCANNERS if r[3] == "ours_ft"][0]
    ax_r.plot([0, 1], [base_row[2], ft_row[2]],
              color="#d62728", linewidth=2.0, marker="o", markersize=8,
              markeredgecolor="black", markeredgewidth=0.6)
    ax_r.text(-0.05, base_row[2], f"{base_row[2]:.1f}%",
              ha="right", va="center", fontsize=9)
    ax_r.text(1.05,  ft_row[2],   f"{ft_row[2]:.1f}%",
              ha="left",  va="center", fontsize=9, fontweight="bold",
              color="#d62728")
    ax_r.text(0.5, (base_row[2] + ft_row[2]) / 2 + 4,
              f"+{ft_row[2]-base_row[2]:.1f} pp",
              ha="center", va="center", fontsize=10,
              color="#d62728", fontweight="bold")

    ax_r.set_xticks([0, 1])
    ax_r.set_xticklabels(["base", "fine-tuned"], fontsize=9)
    ax_r.set_xlim(-0.4, 1.4)
    ax_r.set_ylim(0, 100)
    ax_r.set_ylabel("Detection rate (%)", fontsize=10)
    ax_r.set_title("Qwen2.5-Coder-7B (ours)", fontsize=10)
    ax_r.grid(axis="y", linestyle=":", alpha=0.4)
    ax_r.set_axisbelow(True)
    ax_r.spines["top"].set_visible(False)
    ax_r.spines["right"].set_visible(False)

    fig.tight_layout()
    fig.savefig(ROOT / "candidate_3.pdf", bbox_inches="tight")
    fig.savefig(ROOT / "candidate_3.png", bbox_inches="tight", dpi=150)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Candidate 4: Lollipop chart with grouped sections.
# ---------------------------------------------------------------------------
def candidate_4():
    # Group rows in a fixed order (rule, proprietary, ours)
    order = []
    for g in ("rule", "proprietary", "ours_base", "ours_ft"):
        for r in SCANNERS:
            if r[3] == g:
                order.append(r)

    # Compute y positions with group separators (extra space between groups)
    y_positions = []
    y = 0
    last_group = None
    for r in order:
        if last_group and r[3] != last_group and not (
                last_group.startswith("ours") and r[3].startswith("ours")):
            y -= 0.7   # bigger gap between groups
        y_positions.append(y)
        y -= 1
        last_group = r[3]

    fig, ax = plt.subplots(figsize=(5.5, 3.4))
    for r, yi in zip(order, y_positions):
        lab, det, rate, g = r
        ax.hlines(yi, 0, rate, color=GROUP_COLORS[g], linewidth=1.6, alpha=0.8)
        ax.scatter([rate], [yi], s=80, color=GROUP_COLORS[g],
                   edgecolor="black", linewidth=0.5,
                   marker=("D" if g == "ours_ft" else "o"), zorder=3)
        ax.text(rate + 1.2, yi, f"{rate:.1f}%",
                ha="left", va="center", fontsize=8.5,
                fontweight=("bold" if g == "ours_ft" else "normal"))

    ax.set_yticks(y_positions)
    ax.set_yticklabels([r[0] for r in order], fontsize=9)
    ax.set_xlabel("Detection rate (%)", fontsize=10)
    ax.set_xlim(0, 100)
    ax.grid(axis="x", linestyle=":", alpha=0.4)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # Group section labels along the right margin (centered on each group)
    group_spans = {}
    for r, yi in zip(order, y_positions):
        group_spans.setdefault(r[3], []).append(yi)
    bands = [
        ("Rule-based",  "#666666", ["rule"]),
        ("Proprietary", "#1f77b4", ["proprietary"]),
        ("Ours",        "#d62728", ["ours_base", "ours_ft"]),
    ]
    for label, color, gs in bands:
        all_ys = []
        for g in gs:
            all_ys.extend(group_spans.get(g, []))
        if not all_ys:
            continue
        ax.text(105, sum(all_ys) / len(all_ys), label,
                ha="left", va="center", fontsize=8.5, color=color,
                fontweight="bold")
    ax.set_xlim(0, 118)

    fig.tight_layout()
    fig.savefig(ROOT / "candidate_4.pdf", bbox_inches="tight")
    fig.savefig(ROOT / "candidate_4.png", bbox_inches="tight", dpi=150)
    plt.close(fig)


def main():
    plt.rcParams["text.usetex"] = False  # native rendering for previews
    plt.rcParams["font.family"] = "DejaVu Sans"
    candidate_1()
    candidate_2()
    candidate_3()
    candidate_4()
    print("wrote 4 candidates to", ROOT)


if __name__ == "__main__":
    main()
