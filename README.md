# Original Field Desk Harbor task

One task: `field-desk-locale-rollout/`. The application, copy, catalogs, data, verifier and oracle were authored from scratch for this assignment with AI assistance. No existing application repository was used as a reference or seed.

The task is a repo-wide locale rollout across eight operational views and shared UI. It checks localized copy and actual workflow state, including monetary meaning, operator-scoped preferences, live dialogs, plurals and machine-facing contracts. The app uses Python's standard library, SQLite and native browser ES modules. The sole test dependency is pinned Playwright/Chromium; there is no external application service or account.

```sh
harbor run -p field-desk-locale-rollout -a oracle --job-name oracle-04
harbor run -p field-desk-locale-rollout -a nop --job-name starter-02
CODEX_FORCE_AUTH_JSON=1 harbor run -p field-desk-locale-rollout -a codex \
  -m openai/gpt-6.1-sol --effort high --ak version=0.167.0 \
  -k 1 -n 1 --job-name codex-01
```

The task image contains only the starting application. Harbor supplies `solution/` to oracle runs and `tests/` to verification. Native jobs, development files and ZIPs stay outside the task. Model authentication is supplied by the native harness and is never committed. The shared Docker environment permits networking for the model client; application checks use local loopback.

No model failure is claimed before an actual accepted target trial. See the task's `RUN_REPORT.md` for measured results and limitations. The source ZIP is frozen before the target starts. A passing target must be recorded as passing.

`tests/grade.py` defines the 70-case plan and 38 critical cases. `overall` is the equal-weight mean of the four category scores. `critical-outcomes.json` is the separate all-critical-success gate. Failed browser cases retain screenshots, visible text, form values and persisted state for reproduction.

`review_trial.py --oracle jobs/oracle-04 --target jobs/codex-01 --out validation/assignment-audit.json` checks actual native run evidence and emits the six weighted assignment dimensions and evidence needed for the seven failure-analysis categories. It does not invent a 100-point grade or assign behavioral causes from a trajectory. No LLM judge is used.
