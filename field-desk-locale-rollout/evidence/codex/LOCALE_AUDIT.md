# Field Desk locale rollout

Completed English, German and Arabic across the shared shell, all eight views,
forms/dialogs, labels/placeholders/accessibility names, errors, plural messages,
activity, notifications and help clipboard feedback. The supplied catalogs and
backend contracts are unchanged; no catalog keys were added.

Locale is loaded from and saved to the selected operator's preferences API.
Preference writes are ordered per operator and preserve saved notifications.
Live switches retain filters, selections, draft text, selected options, active
errors and notifications. Valid amount drafts are reformatted from their original
locale without changing cents; invalid drafts retain their text and parsing locale.
A render guard prevents stale input change events from overwriting converted drafts.

Amounts use strict locale-specific grouping/decimal validation and integer cents,
with the existing maximum enforced. Arabic-Indic quantity digits are accepted.
Arabic uses RTL navigation/layout and Arabic digit formatting; English/German use
LTR. Notifications no longer intercept clicks on underlying controls.

Verified with `python tests/locale_browser.py` (passing; isolated SQLite fixture):
- Every view in every locale, shared navigation, headings/copy, controls, stock
  plurals (all six Arabic branches), selection plurals and RTL/LTR placement.
- Create/edit, title/amount validation, bulk completion, available/unavailable
  assignment, invalid/insufficient/successful reservations, and charge entry.
- Live draft/error/selection/notification/help feedback switches, including a
  focused amount input, and operator switching/reload with saved preferences.
- SQLite integer-cent values, raw text/memos, statuses, crew/stock changes,
  activity rendering, totals, downloaded CSV filename/columns/data, unchanged
  English API error payloads and a simulated server failure.
- No browser JavaScript errors; `git diff --check` passes; original automation
  IDs remain available. The requested port-8000 development instance was opened
  in Chromium. `locale-verification.txt` records the regression run.

No known gaps in the requested behavior. Verification used Chromium; other browser
engines and assistive technology were not separately exercised.
