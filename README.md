# Field Desk Harbor assignment

This repository contains exactly one original Harbor task: `field-desk-locale-rollout/`. The application, catalogs, data, verifier and oracle were authored from scratch with AI assistance. No application repository was copied.

## Setup

Requirements: Python 3.12 or newer, Git, and Docker Desktop (or a compatible running Docker daemon). The first container build needs network access. Run these commands from this repository directory:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp -n .env-example .env
```

Edit the private `.env` and fill `OPENROUTER_KEY` only if you want to run Claude through OpenRouter. Keep `.env` private. The oracle, starter and recorded-output preview do not need an API key. The host runner is pinned to Harbor 0.25.0; application/browser dependencies are installed by the task's Dockerfile.

## Preview without a new model call

The submission includes recorded model patches, so raw `jobs/` directories are not needed:

```sh
python preview.py --recorded claude
```

Open http://127.0.0.1:8001/#orders. Use `#parts`, `#dispatch` and `#activity` without a trailing slash. Stop the server with Ctrl+C. To inspect the recorded failing Codex output, use `--recorded codex`. To inspect the intentionally incomplete input, use `python preview.py --starter` on port 8000. The launcher verifies the recorded source hashes and never substitutes the starter for missing model output.

English names and record content are intentional: Adapter A, North crew, Robin, customer names and order titles remain unchanged. Headings, navigation, buttons, statuses and activity sentence templates must translate. This boundary is documented in the app's `docs/architecture.md`.

## Run Harbor

Start Docker Desktop and activate `.venv`. Choose unused job names:

```sh
harbor run -p field-desk-locale-rollout -a oracle --job-name oracle-new
harbor run -p field-desk-locale-rollout -a nop --job-name starter-new
CODEX_FORCE_AUTH_JSON=1 harbor run -p field-desk-locale-rollout -a codex \
  -m openai/gpt-6.1-sol --effort high --ak version=0.167.0 \
  -k 1 -n 1 --job-name codex-new
harbor run -p field-desk-locale-rollout -a claude-code \
  -m openrouter/anthropic/claude-opus-5.5 --effort high \
  --ak version=2.1.319 --ak 'max_budget_usd="35"' \
  --base-url https://openrouter.ai/api --api-key-name OPENROUTER_KEY \
  --env-file .env -k 1 -n 1 --job-name claude-new
```

The Claude command loads the key from the local `.env`; the key itself is not a command argument. Routing follows the [OpenRouter Claude Code guide](https://openrouter.ai/docs/cookbook/coding-agents/claude-code-integration). The Codex command uses an existing native Codex login. Paid model commands consume the account's credits; the configured Claude CLI budget limit is $35.

After a new model run, `python preview.py --job <job-name>` opens that job's collected output. Results are under `jobs/<job>/<trial>/verifier/`.

## Recorded results

Final saved-artifact evaluations with the corrected verifier:

| Implementation | Passed | Overall | Critical failures |
| --- | ---: | ---: | ---: |
| Oracle | 70/70 | 1.0 | 0 |
| GPT-6.1-sol high / Codex 0.167.0 | 69/70 | 0.8125 | 1 |
| Claude Opus 5.5 high / Claude Code 2.1.319 / OpenRouter | 70/70 | 1.0 | 0 |

Claude's original native result was a verifier false positive caused by a raw comparison of valid Arabic bidi isolation marks. Original results remain preserved; `field-desk-locale-rollout/evidence/claude/reward.json` is the corrected evaluation. No additional model call was made for the correction. The Codex pending-preferences/draft-state failure was independently reproduced 3/3 against an oracle passing 3/3.

Read [RUN_REPORT.md](field-desk-locale-rollout/RUN_REPORT.md) for the failure analysis, verifier corrections, source snapshots, exact recorded commands and reproduction instructions. Per-case evidence and all 24 page/language screenshots for each evaluated implementation are under the task's `evidence/` directory.

## Grading

The verifier runs 70 browser/state checks and writes five-key `reward.json`, per-case checks, critical outcomes, coverage and screenshots. It checks the real UI and persisted state, not just the completion claim. Artifact quality is UI coverage multiplied by 1.0 for supported completion, 0.75 for disclosed partial completion, or 0.5 for a missing/invalid/contradicted completion report. Overall is the mean of four categories. Reporting errors alone do not establish substantive critical-model failure. No LLM judges a trajectory; the assignment's qualitative 100-point rubric is left to the reviewer.

## Submission

Submit `dist/harbor-field-desk-submission.zip`. It contains this README, `requirements.txt`, `.env-example`, the preview launcher, and exactly one task directory with its environment, executable oracle, verifier and evidence.

The archive excludes `.env`, `.venv/`, Git history, raw `jobs/`, temporary `validation/`, caches and superseded distribution files. Docker and the private key must be supplied by the reviewer. The recorded preview remains usable without credentials or a model call.
