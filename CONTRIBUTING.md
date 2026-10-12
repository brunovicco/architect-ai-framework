# Contributing

🇧🇷 This project also has a [Portuguese README](README.pt-br.md); contributions and issues in either English or Portuguese are welcome.

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
```

All three run in CI (`.github/workflows/ci.yml`) on Python 3.11 and 3.12; a PR won't merge cleanly until they pass.

## Scope

- `src/arquiteto/engine.py` is the deterministic decision core — it must stay provider-neutral (no model SDK calls, no vendor-specific logic). `tests/test_vendor_neutral.py` enforces this.
- UI strings and translations (pt-BR/en) live in `src/arquiteto/i18n.py`. See the module docstring for how the sidebar/tab headings are derived from `STEPS` — don't hardcode a step's letter+word pair in more than one place.
- Keep `app.py` widget arguments (label, default value, placeholder) identical across reruns for any widget that has a `key`; Streamlit resets a keyed widget's stored value if any other argument changes between runs, which silently breaks state on a language switch. Use the `field_text`/`field_checkbox` helpers already in `app.py` rather than calling `st.text_input`/`st.checkbox` directly with a translated label.

## Pull requests

1. Fork the repo and create a branch from `main`.
2. Make your change, with tests for new behavior.
3. Run the checks above.
4. Open a PR describing the change and why it's needed.

## License

By contributing, you agree that your contributions will be licensed under the project's [MIT License](LICENSE).
