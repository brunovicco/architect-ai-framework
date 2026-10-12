from .models import ArchitectureCase, ArchitecturePattern, IntegrationPattern, Recommendation


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

    information: list[str] = []
    if case.needs_document_knowledge:
        information.append("Use RAG for enterprise/document knowledge; evaluate chunking, indexing, retrieval quality and citations.")
    if case.needs_dynamic_data:
        information.append("Use a live operational source/API as source of truth for dynamic data; do not rely on model memory or stale RAG snapshots.")
    if case.long_running_context:
        information.append("Use progressive context loading and preserve critical state separately from disposable conversation history.")
    if not information:
        information.append("Keep context minimal; add retrieval or state only when the use case requires it.")

    # Model / provider strategy — deliberately vendor-neutral
    model_strategy: list[str] = [
        "Evaluate model/runtime candidates only after hard requirements are clear.",
        "Compare task quality, latency/throughput and total cost per successful task on representative evals.",
        "Validate context, structured-output and tool-use capabilities required by the architecture.",
        "Treat privacy, data residency, retention and compliance requirements as hard constraints when applicable.",
        "Assess rate limits, availability, observability, operational support and portability/vendor lock-in before selection.",
    ]

    # T — Trust
    controls: list[str] = [
        "Apply least privilege to tools, data and capabilities.",
        "Propagate real user/service identity to authorization checks at execution time.",
    ]
    if case.sensitive_data:
        controls.append("Enforce data isolation and access policy outside the model prompt; log access evidence where appropriate.")
    if case.high_impact_actions or case.irreversible_actions:
        controls.append("Enforce high-impact action policy in the execution layer; do not depend on prompt compliance.")
        controls.append("Use fail-closed behavior when authorization or policy evidence is unavailable.")
    if case.human_approval_required or case.irreversible_actions:
        controls.append("Place human approval immediately before the governed side effect, with the final action details visible to the reviewer.")
    if case.many_external_capabilities:
        controls.append("Use progressive capability discovery/exposure so the model sees only relevant tools at each stage.")

    # E — Evaluation
    evaluations: list[str] = [
        "Create a representative evaluation dataset before production promotion.",
        "Track quality/task success, latency, cost and relevant safety/security metrics.",
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
        "Define timeout, retry and fallback policies per dependency; avoid unsafe retries for non-idempotent side effects.",
        "Use feedback and production failure modes to drive the next evaluation and architecture iteration.",
    ]
    if case.high_impact_actions or case.irreversible_actions:
        operations.append("Require idempotency/deduplication for retried side effects and provide a kill-switch/feature flag for risky capabilities.")

    if case.strict_auditability and architecture == "Agent":
        warnings.append(
            "Strict auditability is in tension with open-ended agentic execution. Bound autonomy, persist state/decisions and consider workflow for regulated steps."
        )

    return Recommendation(
        architecture_pattern=architecture,
        integration_pattern=integration,
        information_strategy=information,
        model_strategy=model_strategy,
        controls=controls,
        evaluations=evaluations,
        operations=operations,
        rationale=rationale,
        warnings=warnings,
    )
