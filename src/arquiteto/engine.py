from .models import (
    ArchitectureCase,
    ArchitecturePattern,
    EntryPoint,
    FeasibilityVerdict,
    IntegrationPattern,
    Recommendation,
    ReferenceArchitecture,
    ReviewPlacement,
)


def _entry_point(case: ArchitectureCase, rationale: list[str]) -> EntryPoint:
    if case.reusable_across_multiple_clients:
        rationale.append(
            "The capability needs to be discoverable and reusable by more than one client; expose it "
            "once through a standardized protocol server instead of rebuilding the integration per client."
        )
        return "Protocol server for multi-client reuse"
    if case.is_engineering_tool:
        rationale.append(
            "This is an engineering workflow where the path through unfamiliar work can't be scripted "
            "in advance; route it through an agentic coding assistant rather than a bespoke end-user UI."
        )
        return "Agentic coding assistant (CLI/IDE)"
    if case.needs_custom_user_experience:
        rationale.append(
            "A fully custom, branded, product-embedded experience needs direct API/SDK integration; a "
            "generic hosted chat interface won't carry your brand or business logic."
        )
        return "Direct API / SDK integration"
    rationale.append(
        "No custom experience, engineering workflow or multi-client reuse was identified; a hosted "
        "chat/web interface has the lowest build cost for this case."
    )
    return "Hosted chat / web UI"


def _reference_architecture(case: ArchitectureCase, architecture: ArchitecturePattern) -> ReferenceArchitecture:
    if architecture == "Multi-agent":
        return "Orchestrator-workers"
    if architecture == "Agent":
        return "Coding agent" if case.is_engineering_tool else "Agent (autonomous tool use)"
    if architecture == "Workflow":
        if case.many_external_capabilities:
            return "Routing"
        if case.needs_document_knowledge and case.structured_output:
            return "Document processing pipeline"
        return "Chaining"
    return "RAG pipeline" if case.needs_document_knowledge else "Single augmented call"


def _review_placement(case: ArchitectureCase) -> ReviewPlacement:
    if case.irreversible_actions:
        return "Pre-action approval"
    if case.high_impact_actions:
        return "Sampled review" if case.has_calibrated_confidence_score else "Pre-action approval"
    if case.sensitive_data:
        return "Post-action audit"
    return "No review needed"


def _feasibility_verdict(case: ArchitectureCase, warnings: list[str]) -> FeasibilityVerdict:
    cost_provided = case.monthly_cost_ceiling > 0 and case.estimated_monthly_cost > 0
    if cost_provided and case.estimated_monthly_cost > case.monthly_cost_ceiling:
        warnings.append(
            "Estimated monthly cost exceeds the stated budget ceiling; narrow scope, add caching, or "
            "raise the budget before committing."
        )
        return "Not feasible as scoped"
    if not cost_provided and not warnings:
        return "Not assessed"
    if warnings:
        return "Feasible with constraints"
    return "Feasible as scoped"


def recommend(case: ArchitectureCase) -> Recommendation:
    rationale: list[str] = []
    warnings: list[str] = []

    # U — Usage pattern
    architecture: ArchitecturePattern
    if case.independent_autonomous_domains and case.dynamic_next_steps:
        architecture = "Multi-agent"
        rationale.append(
            "Separate autonomous domains plus dynamic execution can justify multiple agents, "
            "but each boundary should have a clear ownership and contract."
        )
    elif case.dynamic_next_steps or case.dynamic_tool_choice:
        architecture = "Agent"
        rationale.append(
            "The system must discover or choose next steps during execution, which favors bounded agentic behavior."
        )
    elif case.path_known:
        architecture = "Workflow"
        rationale.append(
            "The execution path is known in advance, so a workflow offers greater predictability and auditability."
        )
    else:
        architecture = "Augmented LLM"
        rationale.append(
            "No orchestration requirement was identified; start with the smallest useful augmented-model pattern."
        )

    if architecture == "Multi-agent":
        warnings.append(
            "Validate that multi-agent autonomy is necessary. Prefer workflow + tools when it provides the same outcome with less complexity."
        )

    # I — Integration
    integration: IntegrationPattern
    if case.remote_autonomous_service:
        integration = "Agent-to-Agent"
        rationale.append("A remote capability has its own autonomy and execution lifecycle, favoring agent-to-agent coordination.")
    elif case.many_external_capabilities:
        integration = "Tool Protocol / MCP"
        rationale.append("Multiple model-facing capabilities benefit from standardized discovery and contracts; a tool protocol such as MCP can be a candidate interface.")
    elif case.existing_api or case.needs_dynamic_data:
        integration = "API / Tool"
        rationale.append("Existing operational sources should remain the source of truth and be exposed as tools/APIs.")
    else:
        integration = "None"

    entry_point = _entry_point(case, rationale)
    reference_architecture = _reference_architecture(case, architecture)

    information: list[str] = []
    if case.needs_document_knowledge:
        information.append("Use RAG for enterprise/document knowledge; evaluate chunking, indexing, retrieval quality and citations.")
    if case.needs_dynamic_data:
        information.append("Use a live operational source/API as source of truth for dynamic data; do not rely on model memory or stale RAG snapshots.")
    if case.long_running_context:
        information.append("Use progressive context loading and preserve critical state separately from disposable conversation history.")
    if not information:
        information.append("Keep context minimal; add retrieval or state only when the use case requires it.")
    information.append(
        "Decide what each piece of context is for using the four model properties as the lens: "
        "next-token prediction (pattern-rich generation, weak on precise specifics), knowledge "
        "(reliable on common/stable topics, weak on rare or fast-changing ones), working memory "
        "(a hard context-window edge, not graceful degradation) and steerability (reliable with "
        "concrete/verifiable instructions, weak on abstract or long reasoning chains)."
    )

    # Model / provider strategy — deliberately vendor-neutral
    model_strategy: list[str] = [
        "Evaluate model/runtime candidates only after hard requirements are clear.",
        "Compare task quality, latency/throughput and total cost per successful task on representative evals.",
        "Validate context, structured-output and tool-use capabilities required by the architecture.",
        "Treat privacy, data residency, retention and compliance requirements as hard constraints when applicable.",
        "Assess rate limits, availability, observability, operational support and portability/vendor lock-in before selection.",
        "Compare delivery routes — a provider's direct API, a cloud marketplace/gateway, or a "
        "self-hosted/open-weight runtime — on compliance, cost and latency before committing to one.",
        "Map business value to the five ROI pillars — efficiency, transformation, productivity, "
        "solution cost and performance SLAs — before treating a feasible design as a funded one.",
    ]

    # T — Trust
    controls: list[str] = [
        "Apply least privilege to tools, data and capabilities.",
        "Propagate real user/service identity to authorization checks at execution time.",
        "Justify each Claude/system/human assignment through reversibility (can a wrong call be "
        "undone?), stakes (what does a wrong call cost?) and accountability (who must answer for it?).",
    ]
    if case.sensitive_data:
        controls.append("Enforce data isolation and access policy outside the model prompt; log access evidence where appropriate.")
    if case.high_impact_actions or case.irreversible_actions:
        controls.append("Input screening: validate and sanitize what reaches the model before it can trigger the action, deterministically where the check is unambiguous.")
        controls.append("Output screening: check the model's output against policy before it is shown or executed, not only what goes in.")
        controls.append("Authorization: enforce high-impact action policy in the execution layer; do not depend on prompt compliance.")
        controls.append("Use fail-closed behavior when authorization or policy evidence is unavailable.")
    if case.human_approval_required or case.irreversible_actions:
        controls.append("Place human approval immediately before the governed side effect, with the final action details visible to the reviewer.")
    if case.many_external_capabilities:
        controls.append("Use progressive capability discovery/exposure so the model sees only relevant tools at each stage.")
    if case.differential_outcomes_risk:
        controls.append(
            "Audit the four common bias injection points: retrieval-corpus representativeness, "
            "prompt framing, few-shot example selection and downstream routing logic; each can skew "
            "outcomes independently of model behavior."
        )
        controls.append(
            "Log enough of each decision to reconstruct it afterward for the affected person, a "
            "regulator and your own debugging team."
        )

    review_placement = _review_placement(case)

    # E — Evaluation
    evaluations: list[str] = [
        "Create a representative evaluation dataset before production promotion.",
        "Track quality/task success, latency, cost and relevant safety/security metrics.",
        "Before promoting a model, prompt or retrieval change, run a structured experiment: state the "
        "hypothesis, pick metrics tied to the eval suite, size the sample, and avoid overclaiming from a single run.",
    ]
    if case.structured_output:
        evaluations.append("Use deterministic/code-based checks for schema, required fields and other objective constraints.")
    if case.subjective_quality:
        evaluations.append("Use calibrated LLM-as-a-judge and/or human evaluation for subjective quality dimensions.")
    if case.critical_cohorts:
        evaluations.append("Segment evaluation by critical cohorts/use cases so aggregate metrics do not hide failure modes.")
    if case.high_impact_actions:
        evaluations.append("Add adversarial and policy-bypass cases focused on unauthorized or unsafe actions.")

    # O — Operations
    operations = [
        "Trace model calls, retrieval, tool calls, latency, errors and final outcomes with a shared correlation/trace ID.",
        "Define timeout, retry, fallback and circuit-breaker policies per dependency; avoid unsafe retries for non-idempotent side effects.",
        "Use feedback and production failure modes to drive the next evaluation and architecture iteration.",
    ]
    if case.high_impact_actions or case.irreversible_actions:
        operations.append("Require idempotency/deduplication for retried side effects and provide a kill-switch/feature flag for risky capabilities.")

    if case.strict_auditability and architecture == "Agent":
        warnings.append(
            "Strict auditability is in tension with open-ended agentic execution. Bound autonomy, persist state/decisions and consider workflow for regulated steps."
        )

    feasibility_verdict = _feasibility_verdict(case, warnings)

    return Recommendation(
        architecture_pattern=architecture,
        integration_pattern=integration,
        entry_point=entry_point,
        reference_architecture=reference_architecture,
        feasibility_verdict=feasibility_verdict,
        review_placement=review_placement,
        information_strategy=information,
        model_strategy=model_strategy,
        controls=controls,
        evaluations=evaluations,
        operations=operations,
        rationale=rationale,
        warnings=warnings,
    )
