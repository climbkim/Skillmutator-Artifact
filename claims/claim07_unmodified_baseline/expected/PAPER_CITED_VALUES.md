# Paper-cited Values — Table X (`tab:baseline_aggregate`)

## Current paper.tex (L1234–L1254)

```latex
\begin{table}[t]
\centering
\caption{Per-scanner finding counts on the 17 unmodified Anthropic skills. The Skills column reports the count and fraction of skills with at least one finding.}
\label{tab:baseline_aggregate}
\footnotesize
\setlength{\tabcolsep}{4pt}
\begin{tabular}{lrrrr}
\toprule
Scanner & Skills & Mean & Max & Total \\
\midrule
\multicolumn{5}{l}{\textit{Rule-based / Commercial}} \\
\texttt{skill-security-scan}            & 9/17  & 18.2 & 190 & 309 \\
Snyk Agent Scan                         & 4/17  &  0.4 &   2 &   6 \\
\midrule
\multicolumn{5}{l}{\textit{Proprietary LLM}} \\
GPT-4o-mini                             & 17/17 &  7.1 &   9 & 121 \\
GPT-5.4-mini                            & 17/17 &  6.4 &  10 & 109 \\
GPT-5.4                                 & 17/17 &  9.6 &  14 & 163 \\
\bottomrule
\end{tabular}
\end{table}
```

Narrative context (paper L1231):
> As shown in Table~\ref{tab:baseline_aggregate}, skill-security-scan flags 9 of
> 17 skills, with one skill (\texttt{claude-api}) accounting for 190 of its 309
> total findings. Snyk Agent Scan reports 6 HIGH-severity findings on 4 of 17
> skills, concentrated in three rule IDs covering external URL exposure (W012),
> third-party content (W011), and credential handling (W007). The three LLM
> scanners each report findings on every one of the 17 skills, with mean counts
> between 6.4 and 9.6 distinct issues per skill.

## Post-patch (proposed)

```latex
\begin{table}[t]
\centering
\caption{Per-scanner finding counts on the 17 unmodified Anthropic skills. The Skills column reports the count and fraction of skills with at least one finding. Bold marks scanners added post-review.}
\label{tab:baseline_aggregate}
\footnotesize
\setlength{\tabcolsep}{4pt}
\begin{tabular}{lrrrr}
\toprule
Scanner & Skills & Mean & Max & Total \\
\midrule
\multicolumn{5}{l}{\textit{Rule-based / Commercial}} \\
\texttt{skill-security-scan}            & 9/17  & 18.2 & 190 & 309 \\
Snyk Agent Scan                         & 4/17  &  0.4 &   2 &   6 \\
\textbf{SkillScan (upload API)}         & 5/17  &  0.4 &   2 &   6 \\
\midrule
\multicolumn{5}{l}{\textit{Proprietary LLM}} \\
GPT-4o-mini                             & 17/17 &  7.1 &   9 & 121 \\
GPT-5.4-mini                            & 17/17 &  6.4 &  10 & 109 \\
GPT-5.4                                 & 17/17 &  9.6 &  14 & 163 \\
\midrule
\multicolumn{5}{l}{\textit{Fine-tuned student model (ours)}} \\
\textbf{Qwen2.5-Coder-7B + fine-tuned (prefill)} & 17/17 &  7.4 &  22 & 126 \\
\bottomrule
\end{tabular}
\end{table}
```

## Cell-by-cell verification target

| Scanner | Skills | Mean | Max | Total |
|---|---|---|---|---|
| skill-security-scan | 9/17 | 18.2 | 190 | 309 |
| Snyk Agent Scan | 4/17 | 0.4 | 2 | 6 |
| SkillScan | 5/17 | 0.4 | 2 | 6 |
| GPT-4o-mini | 17/17 | 7.1 | 9 | 121 |
| GPT-5.4-mini | 17/17 | 6.4 | 10 | 109 |
| GPT-5.4 | 17/17 | 9.6 | 14 | 163 |
| fine-tuned Qwen2.5-Coder-7B (prefill, Excl. Uncat) | 17/17 | 7.4 | 22 | 126 |

Verified by `scripts/verify_paper_match.py`.