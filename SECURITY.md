# Security Policy

## Scope and threat model

This repo ships a Streamlit app with a deterministic decision core
(`src/architect/engine.py`, `models.py`, `scoring.py`): no database, no user
accounts, and the engine itself never makes a network call. The attack
surface is therefore small and concentrated in three places:

1. **Dependency supply chain** — covered by Dependabot + a `pip-audit` gate in
   CI (`.github/workflows/ci.yml`), on every push.
2. **CI/CD integrity** — GitHub Actions are pinned to a resolved commit SHA
   (not a mutable tag), the workflow's `GITHUB_TOKEN` is scoped to
   `contents: read`, and `main` requires its status checks to pass.
3. **The optional AI reviewer** (`src/architect/providers.py`,
   `OpenAICompatibleAdapter`) — the only code path that makes an outbound
   network request, and the only one that handles a credential. It offers
   two modes from the same generic, vendor-neutral adapter:
   - **Bring-your-own key** — a visitor-supplied API key, kept in memory
     for the duration of one request only — never logged, never persisted,
     never included in any exported plan.
   - **Shared demo credential** — a server-held key (currently NVIDIA's
     OpenAI-compatible endpoint), stored only in the deployment's secret
     store (Streamlit Community Cloud's own "Secrets" setting, mirrored
     locally in the gitignored `.streamlit/secrets.toml`) — never in git,
     never in GitHub Actions secrets (a separate store the running app
     cannot read anyway). Because this key is shared across every
     anonymous visitor, its blast radius is bounded by a global daily
     request cap, a per-browser-session request cap, and a response-length
     cap (`app.py`'s `AI_REVIEW_SHARED_*` constants) — all best-effort,
     in-process limits that reset on redeploy and are not safe if this app
     is ever horizontally scaled to multiple instances.

   Any change to either mode must pass
   [`docs/PROVIDERS_SECURITY_CHECKLIST.md`](docs/PROVIDERS_SECURITY_CHECKLIST.md),
   which maps each control to an OWASP LLM Top 10/MITRE ATLAS risk,
   including the SSRF guard on the endpoint URL and the rate/size caps on
   the shared-credential path.

Data handling note: the public demo deployment is multi-tenant with no
authentication. "Saved cases" are kept in `st.session_state` only (per
browser session, never written server-side), specifically so one visitor's
data can never leak to another.

## Supported versions

Only the latest commit on `main` is supported. This is a reference/portfolio
project, not a maintained library with a release/backport policy.

## Reporting a vulnerability

Please use GitHub's
[private vulnerability reporting](https://github.com/brunovicco/architect-ai-framework/security/advisories/new)
for this repository rather than opening a public issue. If that's not
available to you, open a regular issue describing the *category* of the
problem without exploit details, and ask for a private channel.

## Dependency policy

- Runtime dependencies are kept to the minimum needed (`streamlit`,
  `pydantic`, `python-docx`, `fpdf2`); no network-calling dependency is
  added without updating this policy and the checklist above.
- `pip-audit` failing CI blocks a merge; a flagged dependency is upgraded,
  not silenced, unless the finding is a false positive in a build tool
  (e.g. `pip`/`setuptools` bundled by the CI runner), which is documented in
  the commit that addresses it.
