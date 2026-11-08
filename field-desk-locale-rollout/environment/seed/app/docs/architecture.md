# Field Desk

Original fixture application created for this assignment. It is not copied or adapted from an existing application repository.

- `serve.py`: local HTTP API, static files and SQLite data. The `--data` directory isolates each instance.
- `static/app.js`: event delegation, view/modal state, actions and operator selection.
- `static/core/`: requests, state, text formatting, locale prototype and shared shell.
- `static/views/`: eight workflow modules.
- `static/locales/`: approved English/German/Arabic copy, including plural branches and parameter names.

The locale selector is a prototype; it is not a statement that the product already supports a complete locale rollout. Work-order titles, customer and crew names, part names, and charge memos are user/domain data. Machine-facing status/error codes and CSV fields are deliberately independent of the UI language.

The local operators have no login or external identity provider. This is the documented container/demo deployment, not a production authentication exercise. Robin starts with English and notifications enabled; Amal starts with German and notifications disabled.
