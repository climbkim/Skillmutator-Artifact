# `skills/` — default skill pool

This directory is the default location the pipeline looks up skills by name
(`python -m skill_mutator.main <name>` resolves `<name>` here). `run.sh --crawl`
writes into a sub-folder per registry (`./skills/anthropic`, `./skills/clawhub`) so
skills from different registries never mix.

It ships **empty on purpose**: no third-party skill bodies are redistributed
(licenses vary per skill). Populate it yourself:

- one bundled self-authored sample skill (MIT) lives at `examples/skills/weather-cache/` and is what
  `run.sh` mutates by default (no setup needed);
- to assemble the paper's evaluation/training pools, see `docs/SKILLS_SETUP.md`.

Drop each skill as its own sub-folder containing at least a `SKILL.md`.
