# 🏛️ ARQUITETO — Vendor-Neutral AI Architecture Decision Framework

ARQUITETO is a **provider-agnostic** decision framework and web app for designing AI/LLM systems from business problem to production operating plan.

It can be used with **any model family, hosting model or provider**. The core decision engine has no dependency on any specific model provider, cloud platform or runtime.

The project turns architecture reasoning into a repeatable workflow:

**A**lvo → **R**equisitos → **Q**uem faz o quê → **U**so arquitetural → **I**ntegração & Informação → **T**rust & Controls → **E**valuation → **T**rade-offs → **O**peração.

## What the app does

- Guides discovery of business outcomes, SLAs and hard constraints.
- Recommends a starting architecture: Augmented LLM, Workflow, Agent or Multi-agent.
- Separates responsibilities between probabilistic models, deterministic software and humans.
- Helps decide between RAG, APIs/tools, protocol-based tool discovery and agent-to-agent integration.
- Generates security/governance recommendations such as least privilege, execution-layer authorization, HITL and fail-closed behavior.
- Produces an evaluation and observability plan.
- Compares up to three architecture options with weighted trade-offs.
- Exports the final **Architecture Decision Plan** as Markdown, DOCX or JSON.

## Vendor-neutral by design

ARQUITETO treats the model as an interchangeable architecture component.

```text
Business requirements
        ↓
ARQUITETO decision engine
        ↓
Architecture + controls + evals + operations
        ↓
Model adapter / runtime (optional)
        ↓
Any compatible LLM or model provider
```

The deterministic core does **not** call an LLM. A future AI reviewer can be connected through a provider adapter without changing the decision engine.

The framework therefore works equally well with:

- managed model APIs;
- cloud-hosted foundation models;
- self-hosted/open-weight models;
- model gateways/routers;
- hybrid or multi-model architectures.

Provider selection is a **trade-off decision**, not a framework dependency.

## Why this exists

AI architecture discussions often jump too early to model brands, agents, RAG or tool protocols. ARQUITETO starts with the business problem and hard constraints, then separates responsibilities between probabilistic model behavior, deterministic software and humans.

> Prefer the simplest architecture that satisfies hard requirements and keep critical enforcement outside probabilistic model behavior whenever possible.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -e .
streamlit run app.py
```

Open the local Streamlit URL and walk through the six tabs. The final tab provides downloadable Markdown, DOCX and JSON artifacts.

## Run tests

```bash
pip install -e '.[dev]'
pytest
```

## Repository structure

```text
arquiteto-ai-framework/
├── app.py
├── src/arquiteto/
│   ├── engine.py       # deterministic recommendation engine
│   ├── exporters.py    # Markdown and DOCX generation
│   ├── models.py       # domain models
│   └── scoring.py      # weighted trade-off matrix
├── docs/
│   ├── FRAMEWORK.md
│   └── PROVIDER_NEUTRALITY.md
├── examples/
│   └── investment_assistant.json
├── assets/
│   └── Framework_ARQUITETO_AI.xlsx
└── tests/
```

## Design principles

1. **Provider-neutral core.** No provider SDK or vendor-specific API is required by the decision engine.
2. **Deterministic core first.** The app does not require an LLM to make its primary recommendations.
3. **Hard constraints beat weighted scores.** A high aggregate score cannot rescue an option that violates a non-negotiable requirement.
4. **Controls belong at the right layer.** Prompts guide behavior; authorization and critical side-effect policy belong at execution boundaries.
5. **Agentic complexity must earn its place.** Workflow is preferred when the path is known; agents are used when the system genuinely must discover the path.
6. **Evaluation is part of architecture.** Quality, latency, cost, safety/security and cohort behavior are planned before production promotion.
7. **Model choice follows requirements.** Capability, latency, cost, context, privacy, residency and operational constraints determine the model/runtime choice.

## Roadmap

- [ ] Interactive architecture diagram (Mermaid export)
- [ ] Import/export existing JSON plans
- [ ] PDF export
- [ ] Optional vendor-neutral LLM reviewer via adapter interface
- [ ] Model/provider comparison matrix
- [ ] Saved case library
- [ ] Architecture Decision Record (ADR) export
- [ ] i18n: Portuguese / English UI

## License

MIT
