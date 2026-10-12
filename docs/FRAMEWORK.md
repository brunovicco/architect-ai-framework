# ARCHITECT Framework

ARCHITECT is a repeatable, vendor-neutral decision flow for AI/LLM architecture.

| Step | Question | Output |
| --- | --- | --- |
| **A - Aim** | What business outcome must change? | Problem + measurable success |
| **R - Requirements** | What are the hard constraints and SLAs? | Decision criteria + feasibility verdict |
| **C - Composition** | Probabilistic model, deterministic software or human? | Responsibility boundaries |
| **H - Harness** | Augmented LLM, workflow, agent or multi-agent? | Architecture pattern + named reference architecture + entry point |
| **I - Integration & Information** | Prompt/context, RAG, API/tool, tool protocol or A2A? | Context + integration map |
| **T - Trust & Controls** | What happens when model/tool behavior is wrong? | Auth, least privilege, HITL, fail-closed + review placement |
| **E - Evaluation** | How do we prove the system works? | Dataset, metrics and evaluators |
| **C - Comparison** | What do we gain and what do we pay? | Decision rationale |
| **T - Telemetry** | How do we observe and evolve it? | Operational plan + feedback loop |

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
- Promoting a model/prompt/retrieval change → run a structured experiment first (hypothesis, metrics tied to the eval suite, sized sample), not a single anecdotal run.
- Agent or multi-agent operations → define circuit-breaker policy alongside retry/fallback; never retry non-idempotent side effects unsafely.

## The four model properties (the decomposition lens)

Before deciding what the model should own versus a deterministic system or a
human, name which of these four properties the task actually depends on —
each is a capability paired with a matching limitation:

| Property | Strong on | Weak on | Compensate with |
| --- | --- | --- | --- |
| Next-token prediction | Pattern-rich generation: summarizing, reformatting, drafting | Precision on specific values (names, dates, figures) | Citations, generator-verifier loops, tool calls for exact data |
| Knowledge | Common, recent, well-represented topics | Rare, niche, contested or fast-changing topics | RAG, web search, tool calls, MCP — make an external system the source of truth |
| Working memory | Anything that fits the context window | The context window is a hard edge, not a soft degradation | Chunking, progressive context loading, summarization across turns |
| Steerability | Short, concrete, verifiable instructions | Abstract/ambiguous instructions, long reasoning chains, precise computation | System prompts, structured outputs, code execution |

A task that depends on a property's weak side needs a compensating control,
not a bigger model.

## Delegation criteria

For each piece of work, justify the model/system/human assignment through:

- **Reversibility** — can a wrong call be undone?
- **Stakes** — what does a wrong call cost?
- **Accountability** — who must answer for it?

High stakes, low reversibility and unclear accountability all push toward a
human-in-the-loop or a deterministic system, regardless of how capable the
model is at the task in isolation.

## Reference architectures

`H — Harness` picks one of four abstract patterns (Augmented LLM /
Workflow/Agent/Multi-agent). Within that, a reference architecture names
the concrete, recognizable shape:

| Reference architecture | Typical `architecture_pattern` | Fits when |
| --- | --- | --- |
| Single augmented call | Augmented LLM | One bounded, verifiable task, no document knowledge needed |
| RAG pipeline | Augmented LLM | The task needs stable document/knowledge-base context |
| Chaining | Workflow | The task decomposes into stages with clean handoffs |
| Routing | Workflow | Inputs vary in kind and need different downstream handling |
| Document processing pipeline | Workflow | Structured extraction from semi-structured documents, with a schema check |
| Agent (autonomous tool use) | Agent | The path can't be enumerated in advance, bounded by tool scope and turn budget |
| Coding agent | Agent | The work is an engineering workflow with agentic exploration and deterministic edit/test/review steps |
| Orchestrator-workers | Multi-agent | Separate autonomous domains with clear ownership and contracts |

The most common reference-architecture mistake is using retrieval where a
tool call belongs: RAG answers questions about *stable* knowledge; live,
transactional state (order status, inventory, account balance) needs a
direct call to the system of record, never a cached index.

## Entry point

Independently of the architecture pattern, name which delivery surface the
solution needs — generic categories, not a vendor product:

- **Hosted chat/web UI** — lowest build cost; default when nothing else applies.
- **Agentic coding assistant (CLI/IDE)** — the work is an engineering workflow inside a developer's own code/terminal loop.
- **Direct API/SDK integration** — a fully custom, branded, product-embedded experience.
- **Protocol server for multi-client reuse** — the capability must be discoverable and reusable by more than one client (e.g. exposed via MCP or an equivalent tool protocol), not rebuilt per integration.

## Feasibility verdict

Once cost, scope and risk are known, state one of four verdicts rather than
leaving feasibility implicit:

- **Feasible as scoped** — no open warning, and (if supplied) estimated cost is within the budget ceiling.
- **Feasible with constraints** — workable, but at least one warning or boundary condition must be tracked (e.g. multi-agent complexity, an auditability/autonomy tension).
- **Not feasible as scoped** — a hard constraint is violated, most commonly estimated cost exceeding the stated ceiling.
- **Not assessed** — neither a cost estimate/ceiling nor any other warning was supplied; there isn't enough information for a verdict yet.

## Review placement

`human_approval_required`/`irreversible_actions`/`high_impact_actions` say
*whether* a human reviews a decision; review placement says *where* in the
flow, driven by reversibility, cost and whether a calibrated confidence
signal exists to route on:

- **Pre-action approval** — anything irreversible, or high-impact without a calibrated confidence score to route by.
- **Sampled review** — high-impact, but a calibrated confidence score lets you gate only the low-confidence fraction and sample the rest.
- **Post-action audit** — sensitive but reversible, lower-cost decisions; the action runs, a person checks afterward.
- **No review needed** — none of the above risk signals are present.

Routing everything to a person by volume (instead of by stakes) overwhelms
reviewers and degrades review quality; routing nothing lets a high-stakes,
irreversible action through ungated. Neither is a review *strategy*.

## Fairness and auditability

When a decision can affect people or groups unevenly — approval/denial,
prioritization, eligibility — add two obligations on top of the usual
Trust & Controls set:

- Audit the four common bias injection points: retrieval-corpus
  representativeness, prompt framing, few-shot example selection and
  downstream routing logic — each can skew outcomes independently of model
  behavior.
- Log enough of each decision to reconstruct it afterward for the affected
  person, a regulator and your own debugging team.

For high-impact or irreversible actions, Trust & Controls is three distinct
layers, not one combined check: **input screening** (sanitize what reaches
the model before it can trigger the action), **output screening** (check
what the model produced against policy before it is shown or executed) and
**authorization** (enforce policy in the execution layer, fail-closed when
authorization or policy evidence is unavailable).

## Model/provider decision

ARCHITECT does not prescribe a model vendor. Select the runtime after requirements are clear.

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

Before committing to one, compare delivery routes on compliance, cost and
latency — a provider's direct API, a cloud marketplace/gateway, or a
self-hosted/open-weight runtime — rather than defaulting to whichever route
was easiest to try first.

## Return on investment

A feasible design is not automatically a funded one. Map business value to
five ROI pillars before treating it as such: **efficiency** (time/cost saved on existing work), **transformation**
(work that was not possible before), **productivity** (output per person),
**solution cost** (build + run, compared against `estimated_monthly_cost`/
`monthly_cost_ceiling`) and **performance SLAs** (the latency/quality bar the
business actually needs, not the best the model can do). `feasibility_verdict`
is the scope/budget gate; ROI is the separate question of whether the gate is
worth clearing at all.

## Central rule

> Prefer the simplest architecture that satisfies hard requirements and keep critical enforcement outside probabilistic model behavior whenever possible.
