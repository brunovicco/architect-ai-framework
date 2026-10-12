from typing import Dict, List, Literal
from pydantic import BaseModel, Field


ArchitecturePattern = Literal["Augmented LLM", "Workflow", "Agent", "Multi-agent"]
IntegrationPattern = Literal["API / Tool", "Tool Protocol / MCP", "Agent-to-Agent", "None"]


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


class Recommendation(BaseModel):
    architecture_pattern: ArchitecturePattern
    integration_pattern: IntegrationPattern
    information_strategy: List[str] = Field(default_factory=list)
    model_strategy: List[str] = Field(default_factory=list)
    controls: List[str] = Field(default_factory=list)
    evaluations: List[str] = Field(default_factory=list)
    operations: List[str] = Field(default_factory=list)
    rationale: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


class OptionScore(BaseModel):
    name: str
    scores: Dict[str, int]


class DecisionPlan(BaseModel):
    case: ArchitectureCase
    recommendation: Recommendation
    option_scores: List[OptionScore] = Field(default_factory=list)
    selected_option: str = ""
    tradeoff_notes: str = ""
