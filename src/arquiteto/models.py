from typing import Literal

from pydantic import BaseModel, Field

ArchitecturePattern = Literal["Augmented LLM", "Workflow", "Agent", "Multi-agent"]
IntegrationPattern = Literal["API / Tool", "Tool Protocol / MCP", "Agent-to-Agent", "None"]

# Generic, provider-neutral entry-point categories — never a vendor product
# name. Any provider/runtime has an equivalent of each of these.
EntryPoint = Literal[
    "Hosted chat / web UI",
    "Agentic coding assistant (CLI/IDE)",
    "Direct API / SDK integration",
    "Protocol server for multi-client reuse",
]

# Named reference architectures (a level more concrete than ArchitecturePattern).
# "Parallelization" is part of the vocabulary but has no dedicated trigger in
# engine.py yet — no case signal cleanly distinguishes it from "Chaining".
ReferenceArchitecture = Literal[
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
    name: str = "Untitled case"
    business_problem: str = ""
    desired_outcome: str = ""
    users: str = ""
    quality_target: str = ""
    latency_target: str = ""
    cost_constraint: str = ""
    regulatory_constraints: str = ""

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

    # Entry-point signals (which delivery surface the solution needs)
    is_engineering_tool: bool = False
    needs_custom_user_experience: bool = False
    reusable_across_multiple_clients: bool = False

    # Fairness / review-routing signals
    differential_outcomes_risk: bool = False
    has_calibrated_confidence_score: bool = False

    # Lightweight sizing (0.0 = not provided; no built-in $/token calculator,
    # since per-token pricing changes and would go stale — the user supplies
    # their own estimate, the engine only compares it to the ceiling)
    estimated_monthly_cost: float = 0.0
    monthly_cost_ceiling: float = 0.0

    # Business value notes (free text; the 5 ROI pillars are prompted via the
    # UI placeholder, not computed)
    roi_notes: str = ""


class Recommendation(BaseModel):
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
    name: str
    scores: dict[str, int]


class ModelComparisonRow(BaseModel):
    criterion: str
    notes: dict[str, str] = Field(default_factory=dict)  # candidate name -> free-text note


class DecisionPlan(BaseModel):
    case: ArchitectureCase
    recommendation: Recommendation
    option_scores: list[OptionScore] = Field(default_factory=list)
    selected_option: str = ""
    tradeoff_notes: str = ""
    model_comparison: list[ModelComparisonRow] = Field(default_factory=list)
