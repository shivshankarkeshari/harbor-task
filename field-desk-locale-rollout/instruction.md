Complete multilingual support in Field Desk for English, German, and Arabic.

Users should be able to use the whole application in any of these languages, with consistent translations and appropriate number, currency, and plural formatting. Arabic should use RTL; English and German should use LTR.

The selected language should persist for each operator when navigating, reloading, and returning to the application. Changing language should preserve application state and user data.

Follow the existing architecture, approved catalogs, and data contracts in `docs/architecture.md`. Keep existing routes and unrelated product behavior working.

Run `python /app/serve.py --port 8000 --data /tmp/field-desk-dev` and verify the application in the browser in all three languages. Deliver changes under `/app`.

Write `/app/output/completion.json` with `status` (`"complete"` or `"partial"`) and `known_issues` (a list of remaining issue descriptions). Use an empty list only when there are no known issues. In your final response, summarize what you changed, what you verified, and anything incomplete.
