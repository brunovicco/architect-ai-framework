"""Domain models for the ARCHITECT decision engine.

`ArchitectureCase` is the questionnaire the user fills in; `recommend()` in
`engine.py` turns it into a `Recommendation`. `DecisionPlan` bundles a case,
its recommendation and the optional trade-off/model-comparison data the UI
collects, and is the single object every exporter in `exporters.py` takes.

All fields and `Literal` values here are in English and vendor-neutral by
design - `i18n.py` is solely responsible for translating them for display.
"""

from typing import Literal

from pydantic import BaseModel, Field

ArchitecturePattern = Literal["Deterministic software", "Augmented LLM",
                              "Workflow", "Agent", "Multi-agent"]
IntegrationPattern = Literal["API/Tool",
                             "Tool Protocol/MCP", "Agent-to-Agent", "None"]

EntryPoint = Literal[
    "Hosted chat/web UI",
    "Agentic coding assistant (CLI/IDE)",
    "Direct API/SDK integration",
    "Protocol server for multi-client reuse",
]

ReferenceArchitecture = Literal[
    "Deterministic service",
    "Single augmented call",
    "RAG pipeline",
    "Document processing pipeline",
    "Routing",
    "Chaining",
    "Orchestrator-workers",
    "Agent (autonomous tool use)",
    "Coding agent",
]

FeasibilityVerdict = Literal[
    "Feasible as scoped",
    "Feasible with constraints",
    "Not feasible as scoped",
    "Not assessed",
]

ReviewPlacement = Literal[
    "Pre-action approval",
    "Post-action audit",
    "Sampled review",
    "No review needed",
]


class ArchitectureCase(BaseModel):
    """The questionnaire answers describing one architecture decision.

    Every field defaults to a safe, conservative value so a case can be
    constructed incrementally (e.g. from a partially filled form) and still
    produce a valid `Recommendation`. Fields are grouped by the question
    they answer, matching the ARCHITECT method's steps:

    Attributes:
        name: A short label for the case, used in exported documents.
        business_problem: The outcome that must change.
        desired_outcome: The measurable definition of success.
        users: Who the solution is for.
        quality_target: The quality bar the solution must hit.
        latency_target: The latency/throughput requirement.
        cost_constraint: The cost requirement, in free text.
        regulatory_constraints: Any regulatory/compliance requirement.
        deterministic_sufficient: Explicit human assessment that rules/APIs
            satisfy the requirements without a language model. Defaults to
            False for compatibility with existing cases.
        path_known: Whether the execution path is known in advance.
        dynamic_next_steps: Whether the system must decide its own next
            step during execution.
        dynamic_tool_choice: Whether the system must choose which tool to
            call at runtime.
        independent_autonomous_domains: Whether separate autonomous domains
            with distinct ownership are involved.
        needs_document_knowledge: Whether the task needs stable
            document/knowledge-base context (a RAG candidate).
        needs_dynamic_data: Whether the task needs live, authoritative
            operational data rather than static knowledge.
        existing_api: Whether an existing API already exposes the needed
            operational data/actions.
        many_external_capabilities: Whether the task needs many
            model-facing tools/capabilities.
        remote_autonomous_service: Whether the task depends on a remote
            service that has its own autonomy/execution lifecycle.
        long_running_context: Whether the task spans a long-running
            session whose context keeps growing.
        sensitive_data: Whether the task touches sensitive data.
        high_impact_actions: Whether the task can trigger high-impact
            side effects.
        irreversible_actions: Whether the task can trigger irreversible
            side effects.
        human_approval_required: Whether a human must approve the action
            regardless of other signals.
        strict_auditability: Whether the task is subject to strict
            auditability requirements (e.g. regulated steps).
        structured_output: Whether the task's output must satisfy an
            objective schema/format.
        subjective_quality: Whether the task's quality is subjective and
            needs judgment-based evaluation.
        critical_cohorts: Whether specific user/use-case cohorts must be
            evaluated separately so aggregate metrics cannot hide failures.
        is_engineering_tool: Whether the solution is used by developers
            inside their own code/terminal workflow.
        needs_custom_user_experience: Whether the solution needs a fully
            custom, branded, product-embedded experience.
        reusable_across_multiple_clients: Whether the capability must be
            discoverable and reusable by more than one client.
        differential_outcomes_risk: Whether the decision can affect people
            or groups unevenly (approval/denial, prioritization,
            eligibility).
        has_calibrated_confidence_score: Whether the system produces a
            calibrated confidence score usable to route review.
        estimated_monthly_cost: The user's own estimate of monthly running
            cost. `0.0` means "not supplied".
        monthly_cost_ceiling: The budget ceiling to compare the estimate
            against. `0.0` means "not supplied".
        roi_notes: Free-text notes on the expected return on investment.
    """

    name: str = "Untitled case"
    business_problem: str = ""
    desired_outcome: str = ""
    users: str = ""
    quality_target: str = ""
    latency_target: str = ""
    cost_constraint: str = ""
    regulatory_constraints: str = ""

    deterministic_sufficient: bool = False
    path_known: bool = True
    dynamic_next_steps: bool = False
    dynamic_tool_choice: bool = False
    independent_autonomous_domains: bool = False

    needs_document_knowledge: bool = False
    needs_dynamic_data: bool = False
    existing_api: bool = False
    many_external_capabilities: bool = False
    remote_autonomous_service: bool = False
    long_running_context: bool = False

    sensitive_data: bool = False
    high_impact_actions: bool = False
    irreversible_actions: bool = False
    human_approval_required: bool = False
    strict_auditability: bool = False

    structured_output: bool = False
    subjective_quality: bool = True
    critical_cohorts: bool = False

    is_engineering_tool: bool = False
    needs_custom_user_experience: bool = False
    reusable_across_multiple_clients: bool = False

    differential_outcomes_risk: bool = False
    has_calibrated_confidence_score: bool = False

    estimated_monthly_cost: float = 0.0
    monthly_cost_ceiling: float = 0.0

    roi_notes: str = ""


class Recommendation(BaseModel):
    """The engine's output for one `ArchitectureCase`.

    Produced only by `engine.recommend()`; every string here is English and
    is translated for display by `i18n.py`'s `translate_items`/
    `translate_pattern` helpers, never mutated in place.

    Attributes:
        architecture_pattern: The recommended abstract pattern (Augmented
            LLM, Workflow, Agent, Multi-agent or Deterministic software).
        integration_pattern: The recommended integration approach.
        entry_point: The recommended delivery surface, as a vendor-neutral
            category.
        reference_architecture: The named, concrete shape within
            `architecture_pattern` (e.g. "RAG pipeline", "Coding agent").
        feasibility_verdict: Whether the case is feasible given its stated
            cost ceiling/estimate and any open warnings.
        review_placement: Where in the flow a human should review the
            action, driven by reversibility/impact/confidence.
        information_strategy: Guidance on how context/knowledge should be
            supplied to the model.
        model_strategy: Guidance on selecting and comparing model/runtime
            candidates.
        controls: Trust & Controls recommendations (authorization, least
            privilege, HITL, fail-closed behavior, fairness audits, ...).
        evaluations: Recommendations for the evaluation/testing plan.
        operations: Recommendations for the operational/observability plan.
        rationale: The reasoning behind the architecture/integration/entry
            point choices.
        warnings: Boundary conditions or risks the user should track even
            though the case is still workable.
    """

    architecture_pattern: ArchitecturePattern
    integration_pattern: IntegrationPattern
    entry_point: EntryPoint
    reference_architecture: ReferenceArchitecture
    feasibility_verdict: FeasibilityVerdict
    review_placement: ReviewPlacement
    information_strategy: list[str] = Field(default_factory=list)
    model_strategy: list[str] = Field(default_factory=list)
    controls: list[str] = Field(default_factory=list)
    evaluations: list[str] = Field(default_factory=list)
    operations: list[str] = Field(default_factory=list)
    rationale: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class OptionScore(BaseModel):
    """One architecture option's per-criterion scores for the trade-off matrix.

    Attributes:
        name: The option's label (e.g. "Workflow + RAG").
        scores: Per-criterion scores (typically 1-5), keyed by criterion
            name; fed into `scoring.normalized_score()`.
    """

    name: str
    scores: dict[str, int]


class ModelComparisonRow(BaseModel):
    """One row of the model/provider comparison matrix.

    Attributes:
        criterion: The comparison criterion (e.g. "Latency class").
        notes: Free-text notes per candidate, keyed by candidate name.
    """

    criterion: str
    notes: dict[str, str] = Field(default_factory=dict)


class DecisionPlan(BaseModel):
    """The complete, exportable Architecture Decision Plan.

    Attributes:
        case: The questionnaire answers the plan was built from.
        recommendation: The engine's recommendation for `case`.
        option_scores: Scored architecture options for the trade-off
            matrix, if the user compared any.
        selected_option: The name of the option the user selected, if any.
        tradeoff_notes: Free-text notes on what was gained/given up.
        model_comparison: Rows of the model/provider comparison matrix, if
            the user filled any in.
    """

    case: ArchitectureCase
    recommendation: Recommendation
    option_scores: list[OptionScore] = Field(default_factory=list)
    selected_option: str = ""
    tradeoff_notes: str = ""
    model_comparison: list[ModelComparisonRow] = Field(default_factory=list)
