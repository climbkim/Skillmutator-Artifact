# `external_scanners/` — held-out third-party scanner harness

Drivers that run the held-out (not-in-our-refinement-loop) third-party scanners
over the SkillMutator benchmark, used for the held-out re-evaluation
(paper Table 12, Appendix B.5 Held-out Third-party LLM-based Scanners; outside the
artifact's claims).

**Author-side harness, kept for transparency.** The scripts expect the author's
`Review_4/` layout and the unreleased mutation tree, so they are not runnable as
shipped. `REVIEW4` in the code is that `Review_4/` working folder: the scripts sat in
`Review_4/harness/`, with `Review_4/scanners/` (third-party scanner checkouts) and
`Review_4/results/` beside them, and the mutation tree in the sibling folder
`skillmutator-github/dataset/<oracle>/result/`.

- `run_external_scanners.py` — Sentry / Cisco / SkillScan drivers.
- `run_underhood_llm.py` — the "Under the Hood" static+LLM scanner.
- `run_llm_scanners.py` — LLM-mode scanning harness.
- `make_levels.py`, `make_summary.py` — aggregate detections into the held-out result tables.

Third-party scanner **sources are not bundled** (install them yourself); these
drivers invoke them via env-configured interpreters. The held-out evaluation
results and documentation are not bundled in this version; available from the
authors on request.
