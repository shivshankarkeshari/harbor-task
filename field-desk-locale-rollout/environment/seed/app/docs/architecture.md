# Field Desk

Original fixture application created for this assignment. It is not copied or adapted from an existing application repository.

- `serve.py`: local HTTP API, static files and SQLite data. The `--data` directory isolates each instance.
- `static/app.js`: event delegation, view/modal state, actions and operator selection.
- `static/core/`: requests, state, text formatting, locale prototype and shared shell.
- `static/views/`: eight workflow modules.
- `static/locales/`: approved English/German/Arabic copy, including plural branches and parameter names.

The locale selector is a prototype; it is not a statement that the product already supports a complete locale rollout. Work-order titles, customer and crew names, part names, and charge memos are user/domain data. Machine-facing status/error codes and CSV fields are deliberately independent of the UI language.

The local operators have no login or external identity provider. This is the documented container/demo deployment, not a production authentication exercise. Robin starts with English and notifications enabled; Amal starts with German and notifications disabled.

## Locale behavior and existing contracts

All eight views (orders, dispatch, parts, billing, activity, reports, settings and help) participate in the rollout, including shared navigation, headings, table headers, field labels/placeholders/accessibility names, empty states, errors, confirmations, notifications and help feedback. Use the supplied catalog key/value pairs unchanged; new keys may be added. Field Desk branding, operator/crew/part/customer names, and user-entered titles and memos remain data.

Changing language updates open dialogs, active errors, selection counts and visible notifications immediately. Preserve the route, search/status filter, selected orders, draft text and the meaning of entered amounts. Keep the existing `data-testid` controls available. Set document language/direction and place navigation appropriately for RTL/LTR.

Store locale through the existing preferences API for the selected operator. Navigation, reload and operator switches restore that operator's locale; changing it preserves the saved notification preference.

Format euro amounts and quantities for the selected locale, including the supplied Arabic zero/one/two/few/many/other plural forms. Seed stock counts cover all six Arabic branches. Equivalent Arabic digit/separator presentation, whitespace and bidirectional marks are accepted.

Money inputs accept normal locale grouping/decimal syntax: English `1,234.50`, German `1.234,50` and Arabic `١٬٢٣٤٫٥٠` all mean 123450 cents. Accept Arabic-Indic quantity digits. Amounts are nonnegative, at most 99999999 cents, with at most two fractional digits. Reject malformed input instead of truncating it. Preserve an open amount draft's numeric meaning across language changes; send/store integer cents.

Keep routes, operator IDs and status codes (`OPEN`, `ASSIGNED`, `DONE`) stable. API errors retain their codes, fields and English `message` values; translate their UI presentation. CSV exports retain filename `work-orders.csv`, columns `order_id,title,status,budget_minor,crew_id`, raw user text, original status codes and integer-cent values. Stored event payloads remain data and render in the current locale.
