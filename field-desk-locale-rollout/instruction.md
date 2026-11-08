# Finish the Field Desk locale rollout

Field Desk is an original local work-order application. Its English operational workflows work, and approved English/German/Arabic message catalogs are present, but the locale-selector prototype is incomplete. Complete the rollout across the entire application. Deliver repaired source under `/app`. You may also leave a concise `/app/output/LOCALE_AUDIT.md` describing what you changed, what you actually verified and any remaining gaps; the source and runtime outcomes determine the score.

Run it with `python /app/serve.py --port 8000 --data /tmp/field-desk-dev` and open `http://127.0.0.1:8000`. This is a self-contained demo with two local operators, Robin and Amal. There is no external service, account or API key. The Python standard library serves the app; there is no frontend build step. Playwright/Chromium are installed.

## Required result

English (`en`), German (`de`) and Arabic (`ar`) must work throughout all eight production views: work orders, dispatch, parts, billing, activity, reports, settings and help. Include the shared header/navigation; headings, table headers, metadata/options, labels, placeholders, accessibility labels, empty states, validation and server-error displays, confirmation dialogs, operational notifications and help-copy feedback. Use the approved catalogs in `static/locales/`; retain those files and their supplied key/value pairs. Add keys only if genuinely needed. Field Desk, operator/crew/part/customer names and user-entered text are data/branding and remain unchanged.

Locale changes must update already-open views, dialogs, active errors, selected-count messages and visible notifications. Do not require closing/reopening a dialog to change its language. Preserve the active view, search/status filter, selected work orders, unsaved form text and numeric meaning. Previously entered amounts must not be reinterpreted under the new locale. Existing `data-testid` automation IDs and the controls they identify remain available; styling and internal implementation choices are otherwise yours.

Arabic uses RTL; English/German use LTR. Set effective document language/direction and make the navigation/main layout follow it. The existing layout and text must remain usable. Format displayed quantities and euro amounts for the active locale. Use the supplied plural messages, including Arabic zero/one/two/few/many/other forms. All stock-count forms are represented by the seed inventory.

## Preferences and data contracts

Locale belongs to the selected operator. Persist it through the existing preferences API. Switching operators, navigating and reloading must restore that operator's locale without leaking the previous operator's choice. Changing language must preserve the saved notification preference.

Money inputs accept the selected locale's normal decimal/grouping syntax: `1,234.50` in English, `1.234,50` in German and `١٬٢٣٤٫٥٠` in Arabic all mean 123450 cents. Accept Arabic-Indic digits in quantity fields. Amounts are nonnegative, at most 99999999 cents, with at most two fractional digits; reject malformed values rather than silently truncating them. Preserve an amount's value when a dialog stays open during a locale change. Display localized money, but send/store **integer cents**, never localized numeric strings.

Do not change unrelated product behavior or the backend's machine-facing contracts. Order statuses remain `OPEN`, `ASSIGNED`, `DONE`; operator IDs and route hashes are stable. Error responses retain their existing codes, fields and English `message` values. Localize their presentation in the UI. CSV downloads retain filename `work-orders.csv`, column names `order_id,title,status,budget_minor,crew_id`, raw user text, original status codes and integer-cent values in every language. Stored event payloads remain data and render in the current locale.

## Acceptance coverage

Verification exercises every view in every locale, including:

- Work-order table/filter/search/empty state, create/edit form, invalid title/amount, selection and bulk completion.
- Available/unavailable crew assignments and their error dialogs.
- Parts inventory counts, invalid/insufficient reservations and successful stock updates.
- Charge form, localized numeric input, memo preservation, recorded totals and empty state.
- Stored activity messages, report tiles, CSV confirmation/download and settings/help feedback.
- Live locale switches while a draft, error, selection or notification is active; operator switching and reload; navigation placement under RTL/LTR.

The provided catalogs are the translation acceptance reference; whitespace, bidirectional formatting marks and equivalent Arabic digit/separator presentation are normalized. No arbitrary DOM layout, code structure or translation library is required. A static string search or a report claiming completion is not sufficient. The verifier runs the real browser and inspects persisted API/SQLite outcomes. Category scores are pass fractions; `overall` is their equal-weight arithmetic mean. Critical outcome failures are also reported explicitly, so partial credit does not imply complete success. No LLM judges your trajectory. You have two hours to inspect, implement and verify.
