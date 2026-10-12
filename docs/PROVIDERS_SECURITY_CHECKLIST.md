# Acceptance checklist for `providers.py` adapters

Any `ModelAdapter` implementation (including changes to `OpenAICompatibleAdapter`)
must satisfy this checklist before being merged or wired into `app.py`. It maps
each control to the risk it mitigates in the [OWASP Top 10 for LLM
Applications](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
and, where relevant, [MITRE ATLAS](https://atlas.mitre.org/).

The deterministic core (`engine.py`, `models.py`, `scoring.py`) never calls a
model and is out of scope for this checklist — it stays that way regardless of
what adapters exist. This checklist only governs the optional reviewer path.

| # | Control | Risk mitigated |
| --- | --- | --- |
| 1 | The adapter's `base_url` (or equivalent network target) is validated against a public-address allowlist (`assert_safe_base_url`) before any request is made. Reject non-`https`, `localhost`, loopback, private, link-local (incl. `169.254.169.254` cloud metadata) and reserved/multicast ranges. | SSRF (OWASP API/Web A10; relevant to LLM05 Supply Chain when the "model endpoint" is attacker-influenced) |
| 2 | Every outbound request has an explicit timeout and the failure path raises a typed `AdapterError` rather than letting the UI hang or crash. | LLM04 Model Denial of Service |
| 3 | API keys/credentials are never logged, never written to disk, never included in `DecisionPlan`, and never echoed back in an error message. They live only in the caller's local variables/`st.session_state` for the duration of the request. | LLM06 Sensitive Information Disclosure |
| 4 | The adapter's output is rendered as inert text/markdown in the UI — never `eval`'d, never used to construct a shell command or file path, never auto-executed as an action against the rest of the app. | LLM02 Insecure Output Handling |
| 5 | The UI clearly labels adapter output as AI-generated and unverified, and the feature never auto-applies the response to the `ArchitectureCase`/`DecisionPlan` without an explicit user action. | LLM08 Excessive Agency, LLM09 Overreliance |
| 6 | The prompt sent to the adapter is built only from this plan's own data (the case + recommendation the user is already looking at) — never from another user's session, never from an uploaded file's raw bytes without having gone through the same `ArchitectureCase`/`DecisionPlan` validation as the rest of the app. | LLM01 Prompt Injection (reduces blast radius; does not eliminate it — the plan's own free-text fields are still user-controlled input to the prompt) |
| 7 | The dependency used for the HTTP call (today: Python's stdlib `urllib`, so N/A) is covered by the project's existing `pip-audit` CI gate if a third-party HTTP client is ever introduced. | LLM05 Supply Chain Vulnerabilities |
| 8 | A model/provider is never hardcoded into the adapter class itself — `base_url`/`model` stay caller-supplied parameters, keeping `providers.py` vendor-neutral per the project's core design principle. | N/A (project design constraint, not an OWASP item) |
| 9 | When a call uses a server-held credential shared across anonymous visitors (`app.py`'s "shared demo key" mode) rather than a visitor-supplied one, the call path enforces a global daily request cap, a per-browser-session request cap, and a `max_tokens` response-size cap, so one shared credential's cost/abuse blast radius stays bounded. The credential itself lives only in the deployment's secret store (never in git, never in a GitHub Actions secret, which the running app can't read anyway). | OWASP API4:2023 Unrestricted Resource Consumption; LLM04 Model Denial of Service (cost exhaustion variant) |

## Known residual risk

The SSRF guard (#1) resolves DNS once at adapter construction time and checks
every returned address; it does not pin the connection to the checked IP, so a
DNS response that changes between the check and the actual request (DNS
rebinding) is not fully covered by application code alone. A production
deployment with a real threat model should additionally run this egress
through a network-level allowlist (e.g. an egress proxy or firewall rule), not
rely on this check in isolation.

Control #9's caps are deliberately simple, in-process counters (an
`st.cache_resource` singleton for the global cap, `st.session_state` for the
per-session cap): they reset on every app restart/redeploy, don't persist
across horizontally-scaled instances, and the per-session cap is trivially
reset by a visitor opening a fresh browser session. The global daily cap is
the real backstop against a runaway bill; the per-session cap is a soft
deterrent, not a security boundary. A deployment that outgrows a single
Streamlit Cloud instance should move this to an external store (e.g. Redis)
before relying on it.
