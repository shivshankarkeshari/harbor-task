# Field Desk Harbor task

One original task: `field-desk-locale-rollout/`. Complete English, German and Arabic support in a local work-order app. The application, catalogs, seed data, oracle and verifier were authored from scratch; no application repository was used as a reference.

Start Docker Desktop, then run from this directory with unused job names:

```sh
harbor run -p field-desk-locale-rollout -a oracle --job-name oracle-fresh-01
harbor run -p field-desk-locale-rollout -a nop --job-name starter-fresh-01
CODEX_FORCE_AUTH_JSON=1 harbor run -p field-desk-locale-rollout -a codex \
  -m openai/gpt-6.1-sol --effort high --ak version=0.167.0 \
  -k 1 -n 1 --job-name codex-fresh-01
```

The browser verifier checks all eight views, seven dialog types and operational workflows in three languages. It checks actual localized text, state, API/CSV contracts, money and preferences. Screenshots and visible text are saved for the page matrix. A completion claim cannot make an untranslated UI pass.

`tests/grade.py` defines the 70 checks and 38 critical cases. Category scores are pass fractions. Artifact quality also incorporates the required `/app/output/completion.json`: its multiplier is 1.0 for verified completion, 0.75 for a partial result with disclosed issues, and 0.5 for a missing, invalid or contradicted completion report. `overall` is the arithmetic mean of the four resulting category scores. These rules affect Harbor's actual `reward.json`; no separate adjusted score is used. Reporting failures alone do not prove a substantive model failure. No LLM judges a trajectory.

After a model job finishes, preview its collected output:

```sh
python3 preview.py --job codex-fresh-01
```

Open http://127.0.0.1:8001/. To inspect the intentionally incomplete starter instead, use `python3 preview.py --starter` on port 8000. The launcher never substitutes the starter for missing model output. Preview databases are separate.

Results live under `jobs/<job>/<trial>/verifier/`: `reward.json`, `checks.json`, `critical-outcomes.json`, `coverage.json` and page screenshots. See the task's `RUN_REPORT.md` for the fresh measured results. Old run directories, historical evidence, prototype code and superseded ZIPs were removed before this evaluation. Authentication stays with the native harness and is never committed.
