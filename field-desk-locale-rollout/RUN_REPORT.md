# Field Desk fresh run report

Fresh validation and target evaluation pending. No model failure is claimed.

The application, translations, data, task, verifier and oracle were authored from scratch. The task is a locale rollout in an operational work-order app with eight views. It uses Python/SQLite and browser ES modules; the environment pins base-image digests, Playwright 1.56.0 and native Codex 0.167.0. The app needs no external service. Docker networking is public for native model access; the verifier exercises local loopback.

The instruction states product outcomes and the completion-report contract, without implementation steps or solution hints. Detailed existing numeric/data contracts are in the application documentation.

The fixed browser plan contains 70 cases and 38 critical cases. Actual UI text and persisted behavior determine the scores. Page screenshots and visible text provide review evidence. Artifact quality is additionally multiplied by 1.0 for a complete report supported by all checks, 0.75 for a partial report with known issues, or 0.5 for a missing/invalid/contradicted report. Overall is the equal-weight mean of four categories. Report-only failures are distinguished from critical functional failures. No LLM grades a trajectory.

Run from the repository root with Docker available:

```sh
harbor run -p field-desk-locale-rollout -a oracle --job-name oracle-fresh-01
harbor run -p field-desk-locale-rollout -a nop --job-name starter-fresh-01
CODEX_FORCE_AUTH_JSON=1 harbor run -p field-desk-locale-rollout -a codex \
  -m openai/gpt-6.1-sol --effort high --ak version=0.167.0 \
  -k 1 -n 1 --job-name codex-fresh-01
```

A source ZIP and per-file hashes will be frozen before the model starts. Final evidence will include the controls, model result, exact configuration, trajectory, collected patch, screenshots and a short analysis grounded in any reproducible critical failure. A passing target will be reported as passing. The assignment's 100-point qualitative reviewer rubric is not automatically self-scored.
