# Original Field Desk Harbor task

One task: `field-desk-locale-rollout/`. The application, copy, catalogs, data, verifier and oracle were authored from scratch for this assignment with AI assistance. No existing application repository was used as a reference or seed.

The task is a repo-wide locale rollout across eight operational views and shared UI. It checks localized copy and actual workflow state, including monetary meaning, operator-scoped preferences, live dialogs, plurals and machine-facing contracts. The app uses Python's standard library, SQLite and native browser ES modules. The sole test dependency is pinned Playwright/Chromium; there is no external application service or account.

To preview the **saved model output**, run `python3 preview.py` and open http://127.0.0.1:8001/. The launcher verifies and applies the recorded model patch to a temporary copy; it never edits the task input. Select Arabic to inspect the translated UI and RTL layout.

To inspect the **intentionally incomplete starter**, run `python3 preview.py --starter` and open http://127.0.0.1:8000/. Its language selector does not complete the translations. `environment/seed/app` is this starter; its behavior does not represent the model's graded output. Each preview uses a separate SQLite database under ignored `validation/preview/`.

For a fresh evaluation, choose unused job names:

```sh
harbor run -p field-desk-locale-rollout -a oracle --job-name oracle-rerun-01
harbor run -p field-desk-locale-rollout -a nop --job-name starter-rerun-01
CODEX_FORCE_AUTH_JSON=1 harbor run -p field-desk-locale-rollout -a codex \
  -m openai/gpt-6.1-sol --effort high --ak version=0.167.0 \
  -k 1 -n 1 --job-name codex-rerun-01
```

The task image contains only the starting application. Harbor supplies `solution/` to oracle runs and `tests/` to verification. Native jobs, development files and ZIPs stay outside the task. Model authentication is supplied by the native harness and is never committed. The shared Docker environment permits networking for the model client; application checks use local loopback.

Actual result: GPT-6.1-sol high passed all 70 checks and all 38 critical cases in `codex-02`; each category and the overall mean are 1.0. Oracle also passed 70/70. This candidate does not demonstrate model failure. See the task's `RUN_REPORT.md` for evidence and limitations. The source ZIP was frozen before the target started.

The current instruction has since been shortened into five plain paragraphs. Exact numeric/data rules remain in the app's existing `docs/architecture.md`. This prompt revision has not been run against a model. The recorded trial's original source/prompt is preserved in `field-desk-locale-rollout/evidence/pre-run-task.zip`; the verifier and application code are unchanged.

`tests/grade.py` defines the 70-case plan and 38 critical cases. `overall` is the equal-weight mean of the four category scores. `critical-outcomes.json` is the separate all-critical-success gate. Failed browser cases retain screenshots, visible text, form values and persisted state for reproduction.

`python3 review_trial.py --oracle jobs/oracle-05 --target jobs/codex-02 --out validation/assignment-audit.json` checks native run evidence, recomputes category scores and their arithmetic mean, verifies the case/critical plan and frozen hashes, and emits the six weighted assignment dimensions and evidence needed for the seven failure-analysis categories. It does not invent a 100-point grade or assign behavioral causes from a trajectory. No LLM judge is used. A portable copy and saved results are included under the task's `evidence/` directory.

The additional claim-review policy preserves original Harbor rewards and writes a separate `reviewed_reward.json`. A verified critical defect that contradicts a completion claim, or was left undisclosed, halves `artifact_quality`; the reviewed overall is still the mean of four categories. Factual annotations must cite the exact report quotation, hash and trial. Missing annotations require review; they do not trigger an automatic accusation. The current model has no observed critical defect, so its reviewed mean remains 1.0. This is an additional post-run assessment, not a claim that the original verifier graded reporting.

```sh
python3 review_trial.py --oracle jobs/oracle-05 --target jobs/codex-02 \
  --claim-review field-desk-locale-rollout/evidence/codex/claim-review.json \
  --out validation/assignment-audit.json
```
