Complete multilingual support in Field Desk for English, German, and Arabic.

Apply the selected language consistently across all eight views, navigation, forms, dialogs, errors, notifications, and help. Arabic should use RTL; English and German should use LTR. Numbers, euro amounts, input parsing, and plural messages should follow the selected language.

Save the language for each operator and restore it when navigating, reloading, or switching operators. Changing language should update open screens and dialogs without losing filters, selections, unsaved text, numeric values, or notification preferences.

Use the approved translations in `static/locales/` and follow the existing data contracts documented in `docs/architecture.md`. Preserve user-entered data, routes, automation IDs, and API/CSV formats. Do not change unrelated product behavior.

Run `python /app/serve.py --port 8000 --data /tmp/field-desk-dev` and verify the application in the browser in all three languages. Deliver your changes under `/app`. In your final response, state what you changed, what you actually verified, and any remaining issues. Do not claim complete support when known issues remain.
