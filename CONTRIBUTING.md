# Contributing

This project also has a [Portuguese README](README.pt-br.md); contributions and issues in either English or Portuguese are welcome.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
```

## Before opening a PR

```bash
pytest
ruff check .
mypy src
pip-audit
```

All four run in CI (`.github/workflows/ci.yml`) on Python 3.11 and 3.12; a PR won't merge cleanly until they pass.

## Scope

- `src/architect/engine.py` is the deterministic decision core - it must stay provider-neutral (no model SDK calls, no vendor-specific logic). `tests/test_vendor_neutral.py` enforces this.
- UI strings and translations (pt-BR/en) live in `src/architect/i18n.py`. See the module docstring for how the sidebar/tab headings are derived from `STEPS` - don't hardcode a step's letter+word pair in more than one place.
- Keep `app.py` widget arguments (label, default value, placeholder) identical across reruns for any widget that has a `key`; Streamlit resets a keyed widget's stored value if any other argument changes between runs, which silently breaks state on a language switch. Use the `field_text`/`field_checkbox` helpers already in `app.py` rather than calling `st.text_input`/`st.checkbox` directly with a translated label.

## Pull requests

1. Fork the repo and create a branch from `main`.
2. Make your change, with tests for new behavior.
3. Run the checks above.
4. Open a PR describing the change and why it's needed.

## License

By contributing, you agree that your contributions will be licensed under the project's [MIT License](LICENSE).

## Disagree with a recommendation

Use the recommendation-feedback issue form with a sanitized case, the actual and expected patterns, and the missing criterion. Include the version/commit. A useful contribution is a minimal counterexample plus a regression test; changing a heuristic should document which existing cases change and why. Do not attach customer data, credentials or private plans.

Once a disagreement is confirmed as a genuine rule gap (not a missing input), add it as a new `LabeledCase` to `tests/cases.py` with the corrected expectation and a one-line `reason`, rather than only a one-off assert in `test_engine.py`. `tests/test_labeled_cases.py` checks every labeled case on each CI run, so this keeps the suite a living, append-only record of resolved disagreements instead of losing that history in a closed issue.
