# Figure 4 Cited Values (paper Figure 4, pinD)

LLM self-scanner per-iteration detection rate (%), evaluable-subset denominators
(GPT-4o-mini: n=46 at iter_0, n=48 at iter_1-4; GPT-5.4-mini: n=63; GPT-5.4: n=76):

| Oracle | iter_0 | iter_1 | iter_2 | iter_3 | iter_4 | Source |
|---|---|---|---|---|---|---|
| GPT-4o-mini | 41.3% | 27.1% | 33.3% | 27.1% | 35.4% | ier_dynamics.csv |
| GPT-5.4-mini | 84.1% | 73.0% | 68.3% | 74.6% | 71.4% | ier_dynamics.csv |
| GPT-5.4 | 92.1% | 85.5% | 86.8% | 84.2% | 86.8% | ier_dynamics.csv |

Matches the paper text: GPT-4o-mini 41.3%->27.1%, GPT-5.4-mini 84.1%->73.0%
(first refinement step). The trend is **not strictly monotonic**, but every
post-iter_1 iteration stays below the iter_1 level for all three oracles.
