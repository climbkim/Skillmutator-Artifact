# -*- coding: utf-8 -*-
"""Figure 5 (fig:prefill_delta_comparison) — extract the plotted detection-rate
arrays from plot_prefill_delta.py (four base-model families x {base, no-prefill,
Phase-4-prefill} x two judge panels), recompute the prefill delta
(delta = prefill - no-prefill) per family/judge, then hand both to the shared
verifier, which writes results/derived/fig5_prefill_delta.csv and compares them
cell-by-cell against the paper golden in expected/metrics.json (values +
tolerances live there).

Residual relational rule (Finding 6): under the GPT-5.4 judge, Phase-4 prefill
helps Qwen (delta > 0) but hurts the other three families (delta < 0). The
expected direction is read from the golden's own delta signs, so no fixed
numbers live in this script.
"""
import io, json, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))   # claims/
import _verify_common as V

SRC = Path(__file__).resolve().parent / "plot_prefill_delta.py"
txt = SRC.read_text(encoding="utf-8")


def arr(name):
    m = re.search(rf"{name}\s*=\s*\[([^\]]+)\]", txt)
    return [float(x) for x in m.group(1).split(",")] if m else None


MODELS = ["Qwen", "Llama", "Mistral", "Gemma"]
PANELS = {"gpt": ("gpt_base", "gpt_noprefx", "gpt_prefx"),
          "cla": ("cla_base", "cla_noprefx", "cla_prefx")}

computed = {}
deltas = {}   # (judge, model) -> recomputed delta, for the residual relational rule
for judge, (b, n, p) in PANELS.items():
    base, nopf, pf = arr(b), arr(n), arr(p)
    for i, m in enumerate(MODELS):
        computed[f"{judge}/{m}/base"] = base[i]
        computed[f"{judge}/{m}/noprefill"] = nopf[i]
        computed[f"{judge}/{m}/prefill"] = pf[i]
        d = round(pf[i] - nopf[i], 1)
        computed[f"{judge}/{m}/delta"] = d
        deltas[(judge, m)] = d

rc = V.verify(__file__, "metrics.json", computed,
              results_name="fig5_prefill_delta.csv",
              title="Figure 5 — prefill delta recomputed vs expected/metrics.json (paper golden)\n")

# Residual relational rule (Finding 6, GPT-5.4 judge): prefill helps Qwen,
# hurts Llama/Mistral/Gemma. Expected direction taken from the golden's signs.
GOLD = json.load(io.open(Path(__file__).resolve().parents[2] / "expected" / "metrics.json",
                         encoding="utf-8"))["metrics"]
print("\nRelational rule — Phase-4 prefill direction under the GPT-5.4 judge:")
rel_ok = True
for m in MODELS:
    d = deltas[("gpt", m)]
    exp_d = GOLD[f"gpt/{m}/delta"]
    good = (d > 0) == (exp_d > 0)          # same sign as the paper delta
    rel_ok = rel_ok and good
    print(f"  [{'OK ' if good else 'XX '}] {m:8s} delta={d:+.1f}pp "
          f"(expect {'gain' if exp_d > 0 else 'loss'})")
print("\n" + ("RELATIONAL OK" if rel_ok else "RELATIONAL FAIL"))

sys.exit(rc or (0 if rel_ok else 1))
