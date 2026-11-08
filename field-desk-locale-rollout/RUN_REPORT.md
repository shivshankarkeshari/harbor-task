# Field Desk run report

**Final controls validated: oracle 70/70 (mean 1.0), starter 22/70 (mean 0.264966; 32 critical failures). No accepted target run or failure claim yet.**

## Originality and realism

The complete application, schema, seed data, English/German/Arabic copy, task prompt, verifier and oracle were authored from scratch for this exercise with AI assistance. No existing application repository, issue, benchmark, private task code or solution was used as a reference. Standard Python, SQLite, browser APIs and pinned Playwright are general dependencies. The scenario models a work-order application's multilingual release while preserving dispatch, inventory and billing data contracts.

The starting source has an incomplete locale-selector prototype and approved translation catalogs, alongside working English workflows. Difficulty is intended to come from tracing UI across modules and preserving the meaning of active state, rather than guessing translations, installing packages or discovering hidden requirements.

## Environment and reproduction

The Python base image is pinned by digest; Playwright is 1.56.0 and installs its matching Chromium. The app has no third-party runtime package or external service. SQLite databases are created in isolated temporary directories. The shared Docker network is public for native model access; the application/verifier use loopback. Reproduction commands are in the parent README, and should use fresh job names.

## Verifier and rubric

`tests/test.sh` initializes a five-key zero reward. `tests/verify.py` starts fresh app instances and drives Chromium against every view and dialog in all three locales. It uses independent copies of the approved catalogs, normalizes whitespace/bidirectional marks, checks system-owned copy in context, and separately verifies raw user data, API responses and CSV fields. It checks live form/error/notification changes, locale-aware cents, plural forms, RTL navigation and persisted per-operator preferences. The oracle and broken starter are positive/negative controls. No LLM grades a trajectory.

Category scores are pass fractions: functional correctness covers working actions/numeric/plural/error behavior; constraints cover data/API/CSV/preferences preservation; robustness covers live state transitions and numeric edge cases; artifact quality covers complete view/dialog UI and RTL behavior. Overall is the equal-weight arithmetic mean of the four category pass fractions. Complete success still requires every acceptance case; critical outcomes are listed separately in `critical-outcomes.json`. Infrastructure errors force zero rewards and remain distinguishable in logs. `coverage.json` records the required/executed/passed case counts.

The assignment's separate 100-point rubric remains an evidence-based reviewer assessment: compliance/reproducibility 20, fairness/solvability 20, verifier quality 20, meaningful long-horizon difficulty 15, frontier-model failure evidence 15, originality/realism 10. No script invents those points or infers mental states from tool logs.

## Evidence status

Native oracle `oracle-04` passed 70/70 with no exceptions; `starter-02` passed 22/70 with no infrastructure error and 32 critical failures. The final verifier normalizes equivalent Arabic digits/separators as well as whitespace/bidirectional marks. The first two development oracle runs caught an Arabic numeric-format discrepancy and a stale form-change event during rerender; both reference defects were fixed before target evaluation. Those authoring failures are not model evidence. Final control evidence is under `evidence/oracle/` and `evidence/starter/`. Accepted target trial pending: GPT-6.1-sol high using Codex 0.167.0, native ChatGPT authentication, one trial. Freeze the task and ZIP after controls pass and before the target starts. Preserve all actual results, final source, native trajectory and exact configuration. For any critical target failure, reproduce its final artifact on the same case, compare with the passing oracle, audit verifier/environment assumptions and explain the cause using concrete evidence. If the target passes, this candidate does not demonstrate model failure.

The fixed acceptance plan contains 70 cases and 38 critical cases. Missing cases remain failures. The post-run detector uses the named critical outcomes independently of the average, confirms native model/harness metadata and high effort where available, and records evidence required for wrong hypothesis, incomplete inspection, bad state tracking, brittle patch, skipped verification, report hallucination or another substantive failure. Those cause labels and the 100-point reviewer rubric are not LLM-generated rewards.
