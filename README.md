# Original Field Desk Harbor task

One task: `field-desk-locale-rollout/`. The application, copy, catalogs, data, verifier and oracle were authored from scratch for this assignment with AI assistance. No existing application repository was used as a reference or seed.

The task is a repo-wide locale rollout across eight operational views and shared UI. It checks localized copy and actual workflow state, including monetary meaning, operator-scoped preferences, live dialogs, plurals and machine-facing contracts. The app uses Python's standard library, SQLite and native browser ES modules. The sole test dependency is pinned Playwright/Chromium; there is no external application service or account.

```sh
harbor run -p field-desk-locale-rollout -a oracle --job-name oracle-05
harbor run -p field-desk-locale-rollout -a nop --job-name starter-03
CODEX_FORCE_AUTH_JSON=1 harbor run -p field-desk-locale-rollout -a codex \
  -m openai/gpt-6.1-sol --effort high --ak version=0.167.0 \
  -k 1 -n 1 --job-name codex-02
```

The task image contains only the starting application. Harbor supplies `solution/` to oracle runs and `tests/` to verification. Native jobs, development files and ZIPs stay outside the task. Model authentication is supplied by the native harness and is never committed. The shared Docker environment permits networking for the model client; application checks use local loopback.

Actual result: GPT-6.1-sol high passed all 70 checks and all 38 critical cases in `codex-02`; each category and the overall mean are 1.0. Oracle also passed 70/70. This candidate does not demonstrate model failure. See the task's `RUN_REPORT.md` for evidence and limitations. The source ZIP was frozen before the target started.

`tests/grade.py` defines the 70-case plan and 38 critical cases. `overall` is the equal-weight mean of the four category scores. `critical-outcomes.json` is the separate all-critical-success gate. Failed browser cases retain screenshots, visible text, form values and persisted state for reproduction.

`python3 review_trial.py --oracle jobs/oracle-05 --target jobs/codex-02 --out validation/assignment-audit.json` checks native run evidence, recomputes category scores and their arithmetic mean, verifies the case/critical plan and frozen hashes, and emits the six weighted assignment dimensions and evidence needed for the seven failure-analysis categories. It does not invent a 100-point grade or assign behavioral causes from a trajectory. No LLM judge is used. A portable copy and saved results are included under the task's `evidence/` directory.
