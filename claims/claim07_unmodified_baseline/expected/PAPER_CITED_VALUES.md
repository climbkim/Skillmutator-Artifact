# Paper-cited Values — Table 10 (Appendix B.3 Baseline Findings on Unmodified Skills)

## Paper Table 10 (camera-ready; Appendix B.3 Baseline Findings on Unmodified Skills)

The paper's `\cite{}` commands are omitted; rows, values and layout are as in the paper.

```latex
\begin{table}[t]
\centering
\caption{Per-scanner finding counts on the 17 unmodified Anthropic skills (Skills column: skills with at least one finding).}
\footnotesize
\setlength{\tabcolsep}{4pt}
\begin{tabular}{lrrrr}
\toprule
Scanner & Skills & Mean & Max & Total \\
\midrule
\multicolumn{5}{l}{\textit{Rule-based / Commercial}} \\
skill-security-scan                & 9/17  & 18.2 & 190 & 309 \\
Snyk Agent Scan                    & 4/17  &  0.4 &   2 &   6 \\
SkillScan                          & 5/17  &  0.4 &   2 &   6 \\
\midrule
\multicolumn{5}{l}{\textit{Proprietary LLM}} \\
GPT-4o-mini                        & 17/17 &  7.1 &   9 & 121 \\
GPT-5.4-mini                       & 17/17 &  6.4 &  10 & 109 \\
GPT-5.4                            & 17/17 &  9.6 &  14 & 163 \\
Qwen2.5-Coder-7B (FT + prefill)    & 17/17 &  7.4 &  22 & 126 \\
\bottomrule
\end{tabular}
\end{table}
```

Narrative context (paper Appendix B.3 Baseline Findings on Unmodified Skills):
> Table 10 shows two patterns. First, skill-security-scan
> is dominated by a single outlier, since \texttt{claude-api} alone accounts for 190
> of its 309 findings. Second, the four LLM scanners cluster in a mean range of
> 6.4--9.6. The Qwen student (7.4) sits between GPT-5.4-mini and GPT-5.4 and well
> below skill-security-scan (18.2).

## Cell-by-cell verification target

| Scanner | Skills | Mean | Max | Total |
|---|---|---|---|---|
| skill-security-scan | 9/17 | 18.2 | 190 | 309 |
| Snyk Agent Scan | 4/17 | 0.4 | 2 | 6 |
| SkillScan | 5/17 | 0.4 | 2 | 6 |
| GPT-4o-mini | 17/17 | 7.1 | 9 | 121 |
| GPT-5.4-mini | 17/17 | 6.4 | 10 | 109 |
| GPT-5.4 | 17/17 | 9.6 | 14 | 163 |
| fine-tuned Qwen2.5-Coder-7B (prefill, Excl. Uncat)† | 17/17 | 7.4 | 22 | 126 |

Verified by `scripts/verify_paper_match.py` (24 cells). † The Qwen row is not checked:
it is counted from the raw scanner reports, which are not redistributed (see `data/README.md`, note 2).