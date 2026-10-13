"""Hand-labeled reference cases for `architect.engine.recommend`.

Each entry pairs an `ArchitectureCase` with the architecture/reference
architecture (and, where relevant, entry point) a human would expect, plus
a one-line reason. `test_labeled_cases.py` checks the engine's actual
output against this suite on every CI run, so a future rule change that
silently flips one of these is caught as a named regression rather than a
single buried assert.

See CONTRIBUTING.md's "Disagree with a recommendation" section: once a
reported disagreement is confirmed as a genuine rule gap, add it here with
the corrected expectation and a `reason`, instead of (or in addition to) a
one-off assert in `test_engine.py`. This file is meant to grow.
"""

from dataclasses import dataclass

from architect.models import ArchitectureCase, ArchitecturePattern, EntryPoint, ReferenceArchitecture


@dataclass(frozen=True)
class LabeledCase:
    name: str
    case: ArchitectureCase
    expected_architecture_pattern: ArchitecturePattern
    expected_reference_architecture: ReferenceArchitecture
    reason: str
    expected_entry_point: EntryPoint | None = None


LABELED_CASES: list[LabeledCase] = [
    LabeledCase(
        name="Rules and an existing API already satisfy the requirement",
        case=ArchitectureCase(deterministic_sufficient=True, existing_api=True),
        expected_architecture_pattern="Deterministic software",
        expected_reference_architecture="Deterministic service",
        reason="Explicit human assessment that rules/APIs suffice short-circuits to the deterministic baseline.",
    ),
    LabeledCase(
        name="Deterministic baseline despite a conflicting autonomy signal",
        case=ArchitectureCase(deterministic_sufficient=True, dynamic_tool_choice=True),
        expected_architecture_pattern="Deterministic software",
        expected_reference_architecture="Deterministic service",
        reason="deterministic_sufficient still wins the baseline; the conflict becomes a warning, not a different architecture.",
    ),
    LabeledCase(
        name="Single bounded question, no document knowledge",
        case=ArchitectureCase(path_known=False),
        expected_architecture_pattern="Augmented LLM",
        expected_reference_architecture="Single augmented call",
        reason="No orchestration signal and no document knowledge: the smallest useful pattern.",
    ),
    LabeledCase(
        name="Document Q&A over a stable knowledge base",
        case=ArchitectureCase(path_known=False, needs_document_knowledge=True),
        expected_architecture_pattern="Augmented LLM",
        expected_reference_architecture="RAG pipeline",
        reason="Stable document/knowledge-base context is a RAG candidate, with no orchestration need.",
    ),
    LabeledCase(
        name="Multi-stage staged workflow with a known path",
        case=ArchitectureCase(path_known=True),
        expected_architecture_pattern="Workflow",
        expected_reference_architecture="Chaining",
        expected_entry_point="Hosted chat/web UI",
        reason="Known execution path, no routing/document signal: a plain staged workflow, default entry point.",
    ),
    LabeledCase(
        name="Banking assistant routing among balance/portfolio/order tools",
        case=ArchitectureCase(
            path_known=True, dynamic_tool_choice=True, bounded_known_tool_set=True,
            sensitive_data=True, strict_auditability=True,
        ),
        expected_architecture_pattern="Workflow",
        expected_reference_architecture="Routing",
        reason=(
            "Choosing among a small, known, enumerable set of tools is routing, not open-ended "
            "autonomy - the motivating disagreement for this suite (a regulated case shouldn't "
            "be pushed into Agent just because it picks a tool at runtime)."
        ),
    ),
    LabeledCase(
        name="bounded_known_tool_set is a no-op without dynamic_tool_choice",
        case=ArchitectureCase(path_known=True, bounded_known_tool_set=True),
        expected_architecture_pattern="Workflow",
        expected_reference_architecture="Chaining",
        reason="The flag only matters alongside dynamic_tool_choice; alone it falls through to the plain known-path rule.",
    ),
    LabeledCase(
        name="Bounded tool choice still routes even for an engineering tool",
        case=ArchitectureCase(
            path_known=True, dynamic_tool_choice=True, bounded_known_tool_set=True, is_engineering_tool=True,
        ),
        expected_architecture_pattern="Workflow",
        expected_reference_architecture="Routing",
        expected_entry_point="Agentic coding assistant (CLI/IDE)",
        reason="bounded_known_tool_set dominates the architecture/reference-architecture choice; is_engineering_tool only drives entry point.",
    ),
    LabeledCase(
        name="Support triage routing among many known ticket categories",
        case=ArchitectureCase(path_known=True, many_external_capabilities=True),
        expected_architecture_pattern="Workflow",
        expected_reference_architecture="Routing",
        reason="Many known downstream handlers for varying input kinds is also routing, independent of dynamic_tool_choice.",
    ),
    LabeledCase(
        name="Structured extraction from semi-structured documents",
        case=ArchitectureCase(path_known=True, needs_document_knowledge=True, structured_output=True),
        expected_architecture_pattern="Workflow",
        expected_reference_architecture="Document processing pipeline",
        reason="Document extraction into a schema is a document-processing pipeline, not chaining.",
    ),
    LabeledCase(
        name="Research assistant exploring evidence with a known tool catalog",
        case=ArchitectureCase(path_known=False, dynamic_next_steps=True, dynamic_tool_choice=True, bounded_known_tool_set=True),
        expected_architecture_pattern="Agent",
        expected_reference_architecture="Agent (autonomous tool use)",
        reason="Intermediate evidence determines follow-up queries and termination even with a small, known tool catalog.",
    ),
    LabeledCase(
        name="Coding assistant that explores an unfamiliar codebase",
        case=ArchitectureCase(path_known=False, dynamic_tool_choice=True, is_engineering_tool=True),
        expected_architecture_pattern="Agent",
        expected_reference_architecture="Coding agent",
        expected_entry_point="Agentic coding assistant (CLI/IDE)",
        reason="Engineering workflow + undiscoverable path maps to the coding-agent reference architecture.",
    ),
    LabeledCase(
        name="Engineering workflow with a known, scriptable path",
        case=ArchitectureCase(path_known=True, is_engineering_tool=True),
        expected_architecture_pattern="Workflow",
        expected_reference_architecture="Chaining",
        expected_entry_point="Agentic coding assistant (CLI/IDE)",
        reason="is_engineering_tool only picks the entry point; a known path still recommends Workflow, not Agent.",
    ),
    LabeledCase(
        name="System that must decide its own next step at runtime",
        case=ArchitectureCase(path_known=False, dynamic_next_steps=True),
        expected_architecture_pattern="Agent",
        expected_reference_architecture="Agent (autonomous tool use)",
        reason="dynamic_next_steps alone is sufficient for Agent regardless of tool-set knowledge.",
    ),
    LabeledCase(
        name="Separate autonomous domains with dynamic execution",
        case=ArchitectureCase(path_known=False, dynamic_next_steps=True, independent_autonomous_domains=True),
        expected_architecture_pattern="Multi-agent",
        expected_reference_architecture="Orchestrator-workers",
        reason="Only independent ownership plus dynamic execution together justify multi-agent.",
    ),
    LabeledCase(
        name="Independent domains but a known, scriptable path",
        case=ArchitectureCase(path_known=True, independent_autonomous_domains=True),
        expected_architecture_pattern="Workflow",
        expected_reference_architecture="Chaining",
        reason="independent_autonomous_domains alone, without dynamic execution, doesn't earn Multi-agent.",
    ),
    LabeledCase(
        name="White-labeled, product-embedded assistant",
        case=ArchitectureCase(path_known=True, needs_custom_user_experience=True),
        expected_architecture_pattern="Workflow",
        expected_reference_architecture="Chaining",
        expected_entry_point="Direct API/SDK integration",
        reason="A fully custom, branded experience needs direct API/SDK integration, not hosted chat.",
    ),
    LabeledCase(
        name="Capability exposed to more than one client/agent",
        case=ArchitectureCase(path_known=True, reusable_across_multiple_clients=True),
        expected_architecture_pattern="Workflow",
        expected_reference_architecture="Chaining",
        expected_entry_point="Protocol server for multi-client reuse",
        reason="Multi-client reuse outranks a custom-UX or engineering-tool signal for entry point.",
    ),
    LabeledCase(
        name="Multi-client reuse outranks an engineering-tool signal too",
        case=ArchitectureCase(path_known=True, reusable_across_multiple_clients=True, is_engineering_tool=True),
        expected_architecture_pattern="Workflow",
        expected_reference_architecture="Chaining",
        expected_entry_point="Protocol server for multi-client reuse",
        reason="reusable_across_multiple_clients is checked first in _entry_point, ahead of is_engineering_tool.",
    ),
    LabeledCase(
        name="Agent architecture outside engineering maps to autonomous tool use, not coding agent",
        case=ArchitectureCase(path_known=False, dynamic_tool_choice=True, is_engineering_tool=False),
        expected_architecture_pattern="Agent",
        expected_reference_architecture="Agent (autonomous tool use)",
        reason="The coding-agent reference architecture is reserved for is_engineering_tool cases specifically.",
    ),
]
