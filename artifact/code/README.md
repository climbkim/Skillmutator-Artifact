# SkillMutator — code

**Benchmarking and Defending Language-and-Code Cross-modal Attacks on LLM Agent Skills**

SkillMutator generates adversarially mutated LLM Agent Skills and evaluates
whether security scanners detect them; a four-phase reasoning-trajectory
distillation framework then fine-tunes a small open-weight scanner that matches
frontier detection without third-party data exposure.

---

## Structure

```
artifact/code/
├── skillmutator/              # mutation + scan pipeline (released code; self-contained)
│   ├── src/skill_mutator/     #   pipeline (process/), scanners/llm_scanner (ours; skill-security & Snyk via pip), llm/, utils/
│   ├── scripts/               #   run_mutation.py, run_scanner.py, run_test_scanner.py,
│   │                          #   consolidate_to_datatree.py, evaluate_all.py, run_all_skills.py
│   ├── analysis/              #   paper table/figure builders (rq1/rq2) + skillmutator_utils
│   ├── examples/skills/weather-cache/  #   self-authored benign sample skill for the demo (MIT)
│   ├── docs/                  #   REPRODUCE.md, USAGE.md, ARCHITECTURE.md, attack_categories.md
│   └── run.sh                 #   one-command demo: mutate a sample skill -> scan -> build floats
├── finetuning-framework/      # §5-6 fine-tuning (released code; 4-phase schema) — see its docs/
├── external_scanners/         # held-out third-party scanner harness (RQ5)
├── docs/                      # code-level notes (attack_categories.json)
└── requirements.txt, pyproject.toml
```

`skillmutator/` and `finetuning-framework/` are the two released repositories
(`github.com/climbkim/SkillMutator`), each self-contained with its own
`scripts/`, `docs/`, and `pyproject.toml`.

---

## 13 Attack Categories

| # | Category | # | Category |
|---|----------|---|----------|
| 1 | Advertising Injection | 8 | False Attribution |
| 2 | Brand Hijacking | 9 | Information Gathering |
| 3 | Code Quality Degradation | 10 | Over-engineering |
| 4 | Configuration Weakening | 11 | Persistence Control |
| 5 | Data Exfiltration | 12 | Privilege Escalation |
| 6 | Data Integrity Risks | 13 | Supply Chain Attack |
| 7 | Disruption & Interference | | |

Full descriptions: `skillmutator/docs/attack_categories.md`.

---

## Mutation pipeline (LangGraph)

```
Stage 1 Skill Analysis -> Stage 2 Stealth-Aware Selection -> Stage 3 Scenario
Generation -> Stage 4 Skill Mutation  (+ Iterative Evasion Refinement, up to N iters)
-> Multi-scanner evaluation (skill-security / Snyk / LLM scanner)
```

The paper's stages map to the LangGraph nodes in
`skillmutator/src/skill_mutator/process/skill_mutation.py` and their output folders:

| Paper stage | Node | Output folder |
|---|---|---|
| Stage 1 Skill Analysis | `node_analyze_skill` | `analyze_skill/` |
| Stage 2 Stealth-Aware Selection | `node_select_attacks` | `select_attacks/` (no-select: `select_attacks_bypass/`) |
| Stage 3 Scenario Generation | `node_generate_scenarios` | `generate_scenarios/` |
| Stage 4 Skill Mutation | `node_generate_skill` | `generate_skill/<category>/iter_0/` |
| Iterative Evasion Refinement | `process/refine_mutation.py` | `generate_skill/<category>/iter_N/` (N ≥ 1) |

The pipeline is driven by `skillmutator/src/skill_mutator/main.py`. The 13 categories (§4.1) and 9 security principles (§5) are
code constants; the stealth score (§4.2) is computed in Stage 2. Fine-tuned student
inference: `finetuning-framework/scripts/run_scanner.py`.

---

## Scanners

Scanners are pluggable: subclass `BaseScanner` and `@register("name")` in
`skillmutator/src/skill_mutator/scan.py` (add `optional=True` to exclude from `--all`), implementing
`build_command()` over the skill directory. Bundled adapters:

| Adapter | Tool | Notes |
|---|---|---|
| `llm` | our semantic LLM harness (GPT / Claude / Gemini / fine-tuned Qwen-7B) | our code; `optional=True` (needs API key/GPU) |
| `skill-security` | skill-security-scan (MIT) | PyPI (in `requirements.txt`) |
| `snyk` | Snyk Agent Scan (Apache-2.0) | PyPI `snyk-agent-scan==0.4.9`; needs a Snyk token |

Held-out third-party scanners (paper eval; not bundled, installed from source;
drivers in `external_scanners/`). Each ran static and, where supported, +LLM.
Paper Table 12 (Appendix B.5 Held-out Third-party LLM-based Scanners) uses the +LLM
runs and counts a mutation as detected when the scanner raises any finding at
medium severity or above (`suspicious` for Under the Hood): Sentry 68/76 = 89.5%,
Under the Hood 58/76 = 76.3%, Cisco 53/76 = 69.7%.

| Scanner | Source | Run → verdict |
|---|---|---|
| Sentry Skill Scanner | github.com/getsentry/skills | static (max severity) / +LLM 8-step Risk; detected = Medium or above |
| Cisco AI Defense | github.com/cisco-ai-defense/skill-scanner | static YARA + dataflow / +LLM; detected = any Medium or above |
| SkillScan (NMitchem) (out-of-paper) | github.com/NMitchem/SkillScan | static audit, `risk_score` → `passed` at 6.0 (Python 3.12) |
| Under the Hood | github.com/ShoumikSaha/agent-skill-security | governance clean/suspicious/malicious; detected = suspicious or above |

Held-out result tables are available from the authors on request.

---

## Quick start

```bash
pip install -r requirements.txt     # add `pip install .[finetune]` for the GPU scanner stack
export OPENAI_API_KEY=...            # or put it in a local .env

# live mutate -> scan -> build the mutation-side floats (Tables 3/4/5 + Figure 4)
cd skillmutator && ./run.sh          # sample skill, gpt-4o-mini oracle+scanner+judge
```

`skillmutator/run.sh` mutates a bundled sample skill, scans it, and regenerates
Tables 3/4/5 + Figure 4 in the paper's format (SkillScan and
prompt-injection-detector rows: Tier 1 only). Demo scale (one skill) by
default; the full paper numbers come from the full benchmark (17 skills x 13
categories x 3 oracles) — see `skillmutator/docs/REPRODUCE.md`. **Requires an
OpenAI API key** (default `gpt-4o-mini`, overridable via `--model`).

The fine-tuning side is `finetuning-framework/` (LoRA training + local 7B scanner;
see its `docs/REPRODUCE.md`), with released adapters on Hugging Face.

Raw scanner/scan trees and the injected mutations are **not redistributed**; the
repo's `data/` ships only scanner verdicts and aggregates.

---

## Results (see the paper for the authoritative numbers)

The benchmark comprises **187 mutated skill scenarios** across the 13 attack
categories, generated by three adversarial oracles (GPT-4o-mini, GPT-5.4-mini,
GPT-5.4). On the strongest subset (**n = 76**, GPT-5.4 oracle, `select` mode),
the fine-tuned local scanner improves detection from **17.1 %** (base
Qwen2.5-Coder-7B) to **88.2 %**, surpassing GPT-4o-mini (23.7 %) and
GPT-5.4-mini (79.0 %) and reaching frontier GPT-5.4 (86.8 %). Rule-based
scanners detect far less (skill-security 2.1–7.9 %, Snyk 9.2–16.7 %).

Full per-table/figure numbers are in the paper (Tables 3–11, Findings 1–8).

---

## Citation

```bibtex
@misc{skillmutator2026,
  title={SkillMutator: Benchmarking and Defending Language-and-Code Cross-modal Attacks on LLM Agent Skills},
  year={2026}
}
```

## License

MIT (this repository). Only our own `llm_scanner` is bundled. The other two
scanners are third-party and **not** vendored — installed from PyPI (in
`requirements.txt`): `skill-security-scan` (MIT,
github.com/huifer/skill-security-scan) and `snyk-agent-scan` (Apache-2.0,
github.com/snyk/agent-scan).
