# Field Desk Harbor task

One original task: `field-desk-locale-rollout/`. The app, catalogs, data, verifier and oracle were authored from scratch. The short instruction asks for English, German and Arabic support throughout a local work-order app.

Final artifact evaluations with the corrected verifier:

| Implementation | Passed | Overall | Critical failures |
| --- | ---: | ---: | ---: |
| Oracle | 70/70 | 1.0 | 0 |
| GPT-6.1-sol high, Codex 0.167.0 | 69/70 | 0.8125 | 1 |
| Claude Opus 5.5 high, Claude Code 2.1.319 via OpenRouter | 70/70 | 1.0 | 0 |

Claude's original native verifier result was a false failure caused by a byte-for-byte comparison of valid Arabic bidi isolation marks. Raw native files are preserved; `field-desk-locale-rollout/evidence/claude/reward.json` is the corrected artifact evaluation. No second Claude model call was made. The Codex draft-state failure was reproduced with real keyboard input and a pending successful preferences response; see `RUN_REPORT.md`.

Start Docker Desktop and run from this directory. Choose unused job names:

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
  --env-file ../.env -k 1 -n 1 --job-name claude-new
```

The Claude command reads `OPENROUTER_KEY` from the private parent `.env`; the key is not a command argument or committed file. Routing uses Harbor's native Anthropic Messages support, matching the [OpenRouter Claude Code guide](https://openrouter.ai/docs/cookbook/coding-agents/claude-code-integration).

Preview the saved Claude output with `python3 preview.py --job claude-opus55-high-01`, then open http://127.0.0.1:8001/#orders. Use `#parts`, `#dispatch` and `#activity` without a trailing slash. `python3 preview.py --starter` opens the intentionally incomplete input on port 8000. The launcher never substitutes the starter for missing model output.

English names and record content are expected: Adapter A, North crew, Robin, customer names and order titles remain unchanged. Headings, navigation, buttons, statuses and activity sentence templates must translate. This boundary is documented in the app's `docs/architecture.md`.

The verifier runs 70 browser/state checks, including all eight views in three languages. It writes five-key `reward.json`, per-case `checks.json`, `critical-outcomes.json`, coverage, screenshots and visible text. Artifact quality is UI coverage multiplied by 1.0 for supported completion, 0.75 for disclosed partial completion, or 0.5 for a missing/invalid/contradicted completion report. Overall is the mean of four categories. Reporting errors alone are not counted as substantive critical-model failures. No LLM judges a trajectory.

Current native jobs are under `jobs/`. Final corrected evaluations and selected evidence are bundled under the task's `evidence/`. Old job directories, prototype code and review scaffolding were removed. The assignment's qualitative 100-point reviewer rubric is not automatically self-scored.
