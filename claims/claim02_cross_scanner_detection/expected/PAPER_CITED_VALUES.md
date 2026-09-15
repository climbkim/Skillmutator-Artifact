# Paper-cited Values — Table IV (`tab:cross_matrix`)

From Table IV (`tab:cross_matrix`) in the paper.

## Cell-by-cell verification target

| Scanner | gpt-4o-mini | gpt-5.4-mini | gpt-5.4 | Verified? |
|---|---|---|---|---|
| skill-security-scan | 2.08% (1/48) | 6.35% (4/63) | 7.89% (6/76) | ✅ |
| Snyk Agent Scan | 16.67% (8/48) | 9.52% (6/63) | 9.21% (7/76) | ✅ |
| SkillScan API | 0.00% (0/48) | 0.00% (0/63) | 1.32% (1/76) | ✅ |
| LLM-Guard | 2.08% (1/48) | 0.00% (0/63) | 3.95% (3/76) | ✅ |
| PIGuard | 39.58% (19/48) | 4.76% (3/63) | 17.11% (13/76) | ✅ |
| DataSentinel | 4.17% (2/48) | 11.11% (7/63) | 10.53% (8/76) | ✅ |
| GPT-4o-mini | 35.42% (17/48) | 9.52% (6/63) | 23.68% (18/76) | ✅ |
| GPT-5.4-mini | 79.17% (38/48) | 71.43% (45/63) | 78.95% (60/76) | ✅ |
| **GPT-5.4** | **89.58%** (43/48) | **88.89%** (56/63) | **86.84%** (66/76) | ✅ |

**Status**: 27/27 cells verified. Paper Table IV (L654) reports LLM-Guard as 2.1%/0.0%/4.0%; the bundle's 2.08% (1/48) and 3.95% (3/76) match at 1-decimal rounding.
