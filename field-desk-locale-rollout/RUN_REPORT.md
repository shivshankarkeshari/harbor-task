# Field Desk run report

**GPT-6.1-sol high passed 70/70 checks, including every critical case. Overall mean: 1.0. This candidate does not demonstrate frontier-model failure and does not meet that part of the assignment.**

| Run | Checks passed | Overall mean | Critical failures | Interpretation |
| --- | ---: | ---: | ---: | --- |
| Oracle `oracle-05` | 70/70 | 1.0 | 0 | Passing reference |
| Starter `starter-03` | 22/70 | 0.264966 | 32 | Negative control |
| Target `codex-02` | 70/70 | 1.0 | 0 | Accepted model trial; passed |
| Setup attempt `codex-01` | Verifier did not run | Unavailable | Unavailable | Excluded infrastructure error |

## Originality and realism

The complete application, schema, seed data, English/German/Arabic copy, task prompt, verifier and oracle were authored from scratch for this exercise with AI assistance. No existing application repository, issue, benchmark, private task code or solution was used as a reference. Standard Python, SQLite, browser APIs and pinned Playwright are general dependencies. The scenario models a work-order application's multilingual release while preserving dispatch, inventory and billing data contracts.

The starting source has an incomplete locale-selector prototype and approved translation catalogs, alongside working English workflows. Difficulty is intended to come from tracing UI across modules and preserving the meaning of active state, rather than guessing translations, installing packages or discovering hidden requirements.

## Environment and reproduction

Python and Node base images are pinned by digest; Playwright is 1.56.0 and installs its matching Chromium. Codex CLI 0.167.0 is preinstalled from its official platform package with a pinned SHA-512 integrity check. No login is installed in the image. The app has no third-party runtime package or external service. SQLite databases are created in isolated temporary directories. The shared Docker network is public for native model access; the application/verifier use loopback. Validation used Harbor 0.25.0 on local Docker with Linux ARM64 containers. The native harness uses the operator's existing authenticated Codex client.

From the task directory, with Harbor and Docker available, use fresh job names:

```sh
harbor run -p . -a oracle --job-name oracle-repro
harbor run -p . -a nop --job-name starter-repro
CODEX_FORCE_AUTH_JSON=1 harbor run -p . -a codex \
  -m openai/gpt-6.1-sol --effort high --ak version=0.167.0 \
  -k 1 -n 1 --job-name target-repro
python3 evidence/review_trial.py --oracle jobs/oracle-repro \
  --target jobs/target-repro --out assignment-audit.json
```

The bundled evidence can be audited without a model call:

```sh
python3 evidence/review_trial.py --oracle evidence/oracle \
  --target evidence/codex --out assignment-audit.json
```

## Verifier and rubric

`tests/test.sh` initializes a five-key zero reward. `tests/verify.py` starts fresh app instances and drives Chromium against every view and dialog in all three locales. It uses independent copies of the approved catalogs, normalizes whitespace/bidirectional marks, checks system-owned copy in context, and separately verifies raw user data, API responses and CSV fields. It checks live form/error/notification changes, locale-aware cents, plural forms, RTL navigation and persisted per-operator preferences. The oracle and broken starter are positive/negative controls. No LLM grades a trajectory.

`tests/grade.py` defines the case plan, category mapping, critical mapping and reward calculation. Functional correctness has 12 cases for actions/numeric/plural/error behavior; constraints have 5 for data/API/CSV/preferences preservation; robustness has 4 for live state transitions and numeric edge cases; artifact quality has 49 for complete view/dialog UI and RTL behavior. Each category is its own pass fraction. Missing planned cases count as failed.

```text
overall = (functional_correctness + constraint_satisfaction
           + robustness + artifact_quality) / 4
```

This is an equal-weight mean of categories, rather than the fraction of all 70 cases. The starter's values are 0.333333, 0.4, 0.0 and 0.326531, giving 0.264966 overall. The target's four category scores are all 1.0. Complete success requires every acceptance case; the 38 named critical cases and their outcomes are reported separately in `critical-outcomes.json`. Infrastructure errors force zero rewards and remain distinguishable in logs. `coverage.json` records required/executed/passed case counts.

The assignment's separate 100-point rubric remains an evidence-based reviewer assessment: compliance/reproducibility 20, fairness/solvability 20, verifier quality 20, meaningful long-horizon difficulty 15, frontier-model failure evidence 15, originality/realism 10. No script invents those points or infers mental states from tool logs.

## Evidence status

Native oracle `oracle-05` passed 70/70 with no exceptions; `starter-03` passed 22/70 with no infrastructure error and 32 critical failures. The final verifier normalizes equivalent Arabic digits/separators as well as whitespace/bidirectional marks. The first two development oracle runs caught an Arabic numeric-format discrepancy and a stale form-change event during rerender; both reference defects were fixed before target evaluation. Those authoring failures are not model evidence. Final control evidence is under `evidence/oracle/` and `evidence/starter/`.

Accepted target trial `codex-02/field-desk-locale-rollout__pQUApuW` used GPT-6.1-sol high in native Codex 0.167.0, one trial. Native session metadata confirms the model and high effort. The job ran on November 9, 2026, approximately 02:31–02:44 IST; agent execution took 11 minutes 42 seconds. There was no agent exception, timeout or verifier infrastructure error. All 70 cases and all 38 critical cases passed.

The source was committed as `3cbd6d7` and archived before that trial. The pre-run ZIP SHA-256 is `fe35b2dfbfb8326e14d7434908183940da3e65b6b871d95bf29252feec811dc7`. `evidence/pre-run-manifest.json` contains the 33 frozen task-input hashes. They still match after the run; subsequent additions are this report and evidence. Native whole-directory Harbor checksums differ between the controls and target because the report/control-evidence packaging changed between those jobs; they include documentation and evidence as well as task inputs. The separate per-input manifest is the frozen instruction/environment/oracle/verifier comparison.

`evidence/codex/` contains per-case results, five-key reward, coverage, critical outcomes, native result/trajectory/session, final response, the model's patch against the starter, its audit, its browser verification output and screenshots. Credential fields in native metadata are redacted; source hashes before redaction and stored-file hashes are recorded in `origin.json`. No credential file is included. Apply `evidence/codex/model.patch` with `git apply` from a copy of `environment/seed/app` to reconstruct the collected final application source.

`evidence/review_trial.py` independently recomputes category fractions and their mean, validates the exact case plan and critical-failure list, checks frozen source hashes and confirms native model/harness/high-effort evidence. Its saved outcome is `target_passed_no_failure`; `failure_requirement_met` is false. `evidence/auditor-selfcheck.json` records checks that an incorrect mean, erased critical failures and a missing case are rejected. The excluded setup attempt is correctly rejected as model-failure evidence.

## Failure analysis and limits

No critical target failure was observed, so wrong hypothesis, incomplete inspection, bad state tracking, brittle patch, skipped verification, report hallucination and other substantive failure remain unassigned. There is no failed artifact to reproduce against the oracle. The target's saved source and browser output show that it handled localization throughout the modules, preserved integer-cent/API contracts and tested state transitions; the frozen verifier confirms these behaviors. A bounded source review found no additional concrete critical counterexample. This is evidence for the tested cases, rather than proof of every possible interaction or browser.

The task is original and covers multiple workflows, but its uniform modules and complete approved catalogs let the target solve it in one short run. The observed result does not establish long-horizon difficulty or a model failure rate. This package should not be represented as satisfying the assignment's demonstrated-failure requirement. The separate 100-point reviewer rubric is left unscored. A future candidate needs a concrete reproducible failed artifact and passing control before claiming the failure requirement; an average below 1.0 alone would also be insufficient.

### Excluded harness attempt

`codex-01` stopped during native agent setup because npm omitted the optional Linux ARM64 Codex binary. Agent execution and verification did not start; this is not frontier-model failure evidence. The environment was revised to preinstall the official integrity-verified Codex 0.167.0 binary. Application, instructions, catalogs, acceptance cases, critical mapping and oracle source stayed unchanged. The revised image passed oracle-05 and starter-03. A second source ZIP is frozen before the valid target retry, codex-02.
