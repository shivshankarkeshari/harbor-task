Verified using Chromium 141 and Playwright against the running application started with:

`python /app/serve.py --port 8000 --data /tmp/field-desk-dev`

`python tests/browser_locales.py --base-url http://127.0.0.1:8000` — PASS

- All eight routes in English, German and Arabic, including dialogs, accessible names, placeholders, empty states and errors.
- Arabic RTL navigation and readable text; English/German LTR. Screenshots: en-help.png, de-help.png, ar-help.png.
- All six Arabic stock plural branches; selection counts and confirmation plural forms.
- Localized currency, quantities, strict amount validation and integer-cent limits.
- Open order/charge drafts, user text, selections, filters, errors and notifications survive language changes.
- Operator preferences persist through navigation, reload, switches and a new browser context; saved and unsaved notification choices survive language changes.
- Order, billing, assignment, reservation and completion actions; translated stored activity and clipboard content/feedback.
- Identical CSV bytes and filename across languages; raw user text, status codes, cents, columns and API error contracts preserved.
- No browser JavaScript errors. JavaScript syntax checks and git diff --check passed.
