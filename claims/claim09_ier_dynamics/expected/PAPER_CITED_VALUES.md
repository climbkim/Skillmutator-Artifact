# Figure 4 Cited Values (paper Figure 4)

Aggregation: at iteration k each scenario uses its latest refusal-free iteration ≤ k
(§6.1 Experimental Setup). A scenario with no refusal-free mutation yet counts as not
detected, so the denominators stay at the evaluable sets of Table 4.

LLM self-scanner per-iteration detection rate (%), evaluable-subset denominators
(GPT-4o-mini: n=48; GPT-5.4-mini: n=63; GPT-5.4: n=76 at every iteration):

| Oracle | iter_0 | iter_1 | iter_2 | iter_3 | iter_4 | Source |
|---|---|---|---|---|---|---|
| GPT-4o-mini | 39.6% | 27.1% | 33.3% | 27.1% | 35.4% | ier_dynamics.csv |
| GPT-5.4-mini | 84.1% | 73.0% | 68.3% | 74.6% | 71.4% | ier_dynamics.csv |
| GPT-5.4 | 92.1% | 85.5% | 86.8% | 84.2% | 86.8% | ier_dynamics.csv |

Matches the paper text: GPT-4o-mini 39.6%->27.1%, GPT-5.4-mini 84.1%->73.0%
(first refinement step). The trend is **not strictly monotonic**, but every
later iteration (iter_1-iter_4) stays below the iter_0 level for all three oracles
(0-indexed here; the paper and Figure 4 label iterations iter 1-5).
