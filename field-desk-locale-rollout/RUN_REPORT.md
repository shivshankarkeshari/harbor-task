# Field Desk run report

**Claude Opus 5.5 high passed the corrected verifier. GPT-6.1-sol high has a reproducible critical draft-state failure.**

| Saved implementation | Checks | Overall | Critical failures |
| --- | ---: | ---: | ---: |
| Oracle reference | 70/70 | 1.0 | 0 |
| GPT-6.1-sol high / native Codex 0.167.0 | 69/70 | 0.8125 | 1 |
| Claude Opus 5.5 high / native Claude Code 2.1.319 / OpenRouter | 70/70 | 1.0 | 0 |

One model inference trial was run per model. The Claude job was `claude-opus55-high-01/field-desk-locale-rollout__jsYfYEs`, on November 9, 2026, approximately 12:31–12:41 IST. Its native configuration records high effort, the exact Opus model and a $35 CLI budget limit. Response logs identify `anthropic/claude-opus-5.5`. The harness reports $1.1656832. Authentication was loaded through `OPENROUTER_KEY` from a private `.env`; no credential file is included.

## Environment and scoring

This original work-order application, schema, seed data, catalogs, instruction, verifier and oracle were authored from scratch with AI assistance. No application repository was copied or used as a reference. The environment pins Python/Node image digests, Playwright 1.56.0 and Codex 0.167.0. Harbor 0.25.0 supplied the native clients. The app uses Python/SQLite and browser ES modules, with no external application service. Docker networking permits model access; browser checks use loopback, and artifact re-evaluations used `--network none`.

The fixed plan has 70 cases and 38 critical cases. It checks actual UI copy, all eight views, dialogs, operational actions, locale persistence, RTL, plurals, draft state, integer cents and API/CSV preservation. Screenshots cover all 24 page/language combinations. English part/crew/customer/operator names, branding and order content remain data; leaving them unchanged is required. Arabic interface labels and activity sentence templates still must translate.

Category values are pass fractions. Artifact quality is additionally multiplied by 1.0 for a complete report supported by every check, 0.75 for partial completion with disclosed issues, or 0.5 for a missing/invalid/contradicted report. Overall is the equal-weight mean of the four resulting categories. Missing cases count as failures; infrastructure errors force zero. Reporting-only failures do not establish substantive model failure. No LLM judges a trajectory. The separate 100-point reviewer rubric remains unscored.

## Accepted failure: unsaved money draft

The Codex artifact fails `live_draft_numeric_meaning_and_view_state`. Start a German draft, change language with the keyboard, and continue editing its amount while the successful preferences response is pending. After Arabic appears, submission rejects the valid amount and the dialog stays open. The saved backend order remains unchanged.

The captured form has German text `1.234,51` but `amountLocale: "ar"`. The implementation waits for the preferences API, converts the draft and rerenders. Removing the dirty focused input emits a stale change event that writes the German text back after the syntax tag became Arabic. This is a state-consistency defect, not merely a missing report or untranslated name.

The normal keyboard switch without concurrent editing passes. The pending-save edit fails 3/3 independent fixtures on Codex and passes 3/3 on the oracle. The final full-suite re-evaluation confirms 69/70 on the same saved Codex code. No code was repaired during replay. The final response claimed drafts were preserved, and `completion.json` claimed complete/no known issues; the runtime contradicts that completion claim. UI coverage itself is 49/49, robustness is 3/4, and the reporting multiplier reduces artifact quality from 1.0 to 0.5, producing overall 0.8125. The supported failure labels are bad state tracking and an overbroad completion claim; intent and hidden reasoning are not inferred.

## Verifier validity corrections

The initial draft probe used programmatic selection without focusing the dropdown. It was audited rather than accepted uncritically: ordinary keyboard selection passed, and the genuine pending-save edit above reproduced the defect. Before Claude ran, the verifier was changed to focus ordinary selectors and use a real keyboard action plus a held successful preferences response for that state case. The public state-preservation requirement and application source did not change. Oracle still passed 70/70; the saved Codex artifact still failed the critical case.

Claude's native run then reported 69/70 and overall 0.8724489796 solely because its Arabic accessible label included valid Unicode FSI/PDI marks around an English order title. The public contract already allowed bidi formatting marks, but this one assertion compared raw attributes. That was a verifier false positive. The assertion now uses the existing normalization function. The untranslated English label would still fail.

The saved Claude, Codex and oracle artifacts were all re-evaluated read-only through the same final verifier, without additional model calls: 70/70, 69/70 and 70/70 respectively. Claude's completion report is supported by these checks; its original completion-claim penalty is invalidated. Raw native results remain unchanged in `evidence/*/native-result.json` and `native-reward.json`; `evidence/*/reward.json` holds the corrected evaluation. The untranslated starter's original negative control passed only 22/70 and failed 32 critical checks; its earlier verifier revision is explicitly identified.

## Evidence and reproduction

`evidence/claude/` and `evidence/codex/` contain corrected checks/rewards, original native results, trajectories, collected source patches, completion/final reports and page screenshots. `evidence/reproduction/` contains the keyboard/pending-save probe and its repeated target/oracle results. `evidence/snapshots/` preserves the exact source ZIPs and hashes frozen before each model trial. The final evaluated-input manifest records the corrected verifier. The short instruction contains product outcomes and the report format, without implementation steps.

From the task directory, reproduce the failing saved Codex artifact without a model call:

```sh
task_dir="$PWD"
replay_dir="$(mktemp -d)"
cp -R environment/seed/app "$replay_dir/app"
(cd "$replay_dir/app" && git apply "$task_dir/evidence/codex/model.patch")
mkdir -p "$replay_dir/app/output" "$replay_dir/logs"
cp evidence/codex/completion.json "$replay_dir/app/output/completion.json"
docker build -t field-desk-repro environment
docker run --rm --network none \
  --mount type=bind,src="$replay_dir/app",dst=/app,readonly \
  --mount type=bind,src="$task_dir/tests",dst=/tests,readonly \
  --mount type=bind,src="$replay_dir/logs",dst=/logs/verifier \
  field-desk-repro sh /tests/test.sh
```

Expected: 69/70, one critical draft-state failure and overall 0.8125. Substitute `evidence/claude/` for the patch/report to replay Claude, expected 70/70 and 1.0. For the oracle, run `harbor run -p . -a oracle` with Docker available. Exact native commands used from the parent repository are preserved in `evidence/claude/command.txt` and `evidence/codex/command.txt`; use `-p .` when launching from this task directory and choose unused job names. No model failure is claimed for Claude, and these observed runs do not establish a general failure rate.
