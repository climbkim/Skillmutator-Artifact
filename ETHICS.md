# Ethics — SkillMutator

Ethical considerations for this artifact. It mirrors the Ethics / Responsible
Disclosure discussion in the paper; where they differ, the paper is
authoritative.

## Purpose (defensive)

The work is **defensive security research**: it measures a real, under-studied
language-and-code cross-modal attack surface on LLM Agent Skills and builds a
locally deployable **install-time detector** for it. The framework and benchmark
exist to evaluate and improve scanners, not to facilitate attacks.

## Dual-use of the SkillMutator code (important)

The submitted artifact is primarily **code**, and that code is **dual-use**: the
SkillMutator mutation pipeline (Stage 1–4 + Iterative Evasion Refinement) is
designed to **generate adversarial Agent Skills that evade scanners**. In the
wrong hands it could be used to *produce* stealthy malicious skills rather than
to defend against them. We release it because:

- the defensive value (reproducible benchmarking + a local detector) outweighs
  the marginal offensive uplift — the underlying techniques (prompt injection,
  cross-modal directives) are already publicly known; and
- generation requires an attacker-supplied LLM API key and produces skills that
  our own detector is trained to catch.

Mitigations and restrictions:

- **The generated malicious benchmark itself is NOT redistributed** (see below);
  only scanner verdicts/aggregates are shipped.
- Released under MIT **for research and defensive use only**. Users must not use
  the pipeline to attack systems they do not own or lack permission to test, and
  must not deploy generated skills operationally.
- The shipped end-to-end demo runs on a **self-authored sample skill** with a
  fake endpoint, in an isolated environment.

## Withheld malicious content

The paper's benchmark consists of **mutated Agent Skills with injected malicious
instructions** (e.g., data-exfiltration directives in `SKILL.md`). Per the
paper's disclosure policy this content — and scanner outputs that quote it
verbatim — is **not published**. The artifact ships only detection verdicts and
aggregates (no injected payloads). Any injected directives used internally are
inert templates with **no real credentials, secrets, or live exfiltration
endpoints**. The mutated skills are **author-produced derivatives** of host
skills, not collected from third parties.

## Third-party content

ClawHub skills and the original host skills are third-party and are **not
redistributed**; only metadata / attribution (`clawhub_skills.csv`,
`data/skills/SOURCES.csv`) is shared, so evaluation stays reproducible via public
URLs without republishing others' content. The ClawHub corpus was collected from
**public ClawHub listings only** (2026-04 snapshot; no authentication and no
scraping of private data).

## Human subjects

No human-subjects data and no personal data collection; the work operates only
on software artifacts (Agent Skills) and model outputs, so no IRB review was
required.
