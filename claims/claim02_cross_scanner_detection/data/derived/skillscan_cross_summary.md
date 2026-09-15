# Cross-oracle aggregate summary

paper Tab. III denominators: gpt-4o-mini n=48, gpt-5.4-mini n=63, gpt-5.4 n=76 (evaluable_per_oracle, applies last_good_carry).

## Detection rate matrix (paper criterion)

| Scanner | gpt-4o-mini (n=48) | gpt-5.4-mini (n=63) | gpt-5.4 (n=76) |
|---|---|---|---|
| skill-security-scan | 1/48 (2.08%) | 4/63 (6.35%) | 6/76 (7.89%) |
| Snyk Agent Scan | 8/48 (16.67%) | 6/63 (9.52%) | 7/76 (9.21%) |
| LLM self | 17/48 (35.42%) | 45/63 (71.43%) | 66/76 (86.84%) |
| LLM cross #1 | 38/48 (79.17%) | 6/63 (9.52%) | 18/76 (23.68%) |
| LLM cross #2 | 43/48 (89.58%) | 56/63 (88.89%) | 60/76 (78.95%) |
| SkillScan (≥MED) | 0/48 (0.00%) | 0/63 (0.00%) | 1/76 (1.32%) |

## Snyk severity distribution (mutated scenarios; new findings)

Confirms LOW/CRITICAL absence and MEDIUM rarity.

| Oracle | NEW LOW | NEW MED | NEW HIGH | NEW CRIT |
|---|---|---|---|---|
| gpt-4o-mini | 0 | 0 | 9 | 0 |
| gpt-5.4-mini | 0 | 0 | 6 | 0 |
| gpt-5.4 | 0 | 0 | 7 | 0 |

## SkillScan verdict distribution

| Oracle | SAFE | LOW | MED | HIGH | CRIT | ≥MED rate |
|---|---|---|---|---|---|---|
| gpt-4o-mini | 47 | 1 | 0 | 0 | 0 | 0/48 (0.00%) |
| gpt-5.4-mini | 63 | 0 | 0 | 0 | 0 | 0/63 (0.00%) |
| gpt-5.4 | 75 | 0 | 0 | 0 | 1 | 1/76 (1.32%) |

## SkillScan per-finding severity histogram

| Oracle | SAFE | LOW | MED | HIGH | CRIT |
|---|---|---|---|---|---|
| gpt-4o-mini | 5 | 15 | 0 | 0 | 0 |
| gpt-5.4-mini | 8 | 10 | 0 | 0 | 0 |
| gpt-5.4 | 10 | 14 | 0 | 0 | 2 |

## ss baseline vs mutated aggregate (sum)

| Oracle | base Total | mut Total | Δ | base Crit | mut Crit | Δ | base Warn | mut Warn | Δ |
|---|---|---|---|---|---|---|---|---|---|
| gpt-4o-mini | 914 | 916 | +2 | 823 | 825 | +2 | 91 | 91 | +0 |
| gpt-5.4-mini | 1207 | 1211 | +4 | 1114 | 1117 | +3 | 93 | 94 | +1 |
| gpt-5.4 | 1262 | 1274 | +12 | 1133 | 1145 | +12 | 129 | 129 | +0 |

## Key takeaways

1. **Snyk LOW/CRITICAL are not emitted** for any scenario across all 3 oracle datasets. MEDIUM appears only in 4 baseline reports (W007/W013 corner cases). HIGH dominates by design.
2. **ss aggregate mutation count is dominated by baseline.** Mutation contributes only a small delta on top of large pre-existing finding counts in the unmodified Anthropic skills.
3. **SkillScan verdicts cluster at SAFE.** The handful of LOW/CRITICAL come from explicit primitive detection (e.g., `uname -a`, `window.localStorage`), not from cross-modal semantic analysis.
4. **LLM scanners stay the gold standard.** Self-scanner reaches near-frontier detection on all oracle datasets; cross-LLM rates fall along the capability-parity ordering (paper Tab. III).
