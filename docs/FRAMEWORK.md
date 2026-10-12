# ARQUITETO Framework

ARQUITETO is a repeatable, vendor-neutral decision flow for AI/LLM architecture.

| Step | Question | Output |
|---|---|---|
| **A — Alvo** | What business outcome must change? | Problem + measurable success |
| **R — Requisitos** | What are the hard constraints and SLAs? | Decision criteria |
| **Q — Quem faz o quê?** | Probabilistic model, deterministic software or human? | Responsibility boundaries |
| **U — Uso arquitetural** | Augmented LLM, workflow, agent or multi-agent? | Architecture pattern |
| **I — Integração & Informação** | Prompt/context, RAG, API/tool, tool protocol or A2A? | Context + integration map |
| **T — Trust & Controls** | What happens when model/tool behavior is wrong? | Auth, least privilege, HITL, fail-closed |
| **E — Evaluation** | How do we prove the system works? | Dataset, metrics and evaluators |
| **T — Trade-offs** | What do we gain and what do we pay? | Decision rationale |
| **O — Operação** | How do we observe and evolve it? | Operational plan + feedback loop |

## Decision heuristics

- Known path → prefer a workflow.
- Path discovered during execution → bounded agentic behavior may be justified.
- Multi-agent is not a default; require separate autonomy/ownership and clear contracts.
- Documents/knowledge base → RAG candidate.
- Dynamic operational truth → API/tool/source of truth.
- Large capability catalogs → progressive capability discovery; standardized tool protocols may help.
- Remote autonomous capability → consider agent-to-agent integration.
- High-impact actions → execution-layer enforcement; consider HITL and fail-closed.
- Objective constraints → deterministic evaluators first.
- Subjective quality → calibrated model-based judge and/or human evaluation.
- Aggregate scores can hide critical failures → segment important cohorts.

## Model/provider decision

ARQUITETO does not prescribe a model vendor. Select the runtime after requirements are clear.

Evaluate model/runtime candidates against:

- task quality and capability fit;
- latency and throughput;
- total cost per successful task;
- context-window requirements;
- structured-output/tool-use support;
- privacy and data handling;
- residency/compliance constraints;
- availability and rate limits;
- observability and operational support;
- portability and vendor lock-in risk.

A model or provider that violates a hard constraint is eliminated regardless of benchmark score.

## Central rule

> Prefer the simplest architecture that satisfies hard requirements and keep critical enforcement outside probabilistic model behavior whenever possible.
