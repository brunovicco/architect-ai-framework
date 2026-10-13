"""Streamlit UI for the ARCHITECT decision framework.

Walks the user through the 9-step method across seven tabs, builds an
`ArchitectureCase` from their answers, calls `architect.engine.recommend()`
and renders/exports the resulting `DecisionPlan`. This module owns all
Streamlit-specific concerns (widget state, session management, rendering);
the decision logic itself lives in `architect.engine` and must stay
untouched by anything here.

Run with `streamlit run app.py`.
"""

import datetime
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT/"src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import streamlit as st

from architect.engine import recommend
from architect.exporters import model_comparison_lines, to_adr_markdown, to_docx_bytes, to_markdown, to_pdf_bytes
from architect.i18n import (
    BRAND,
    DEFAULT_LANG,
    LANGS,
    MODEL_CRITERIA,
    e,
    t,
    translate_criterion,
    translate_items,
    translate_pattern,
)
from architect.models import ArchitectureCase, DecisionPlan, ModelComparisonRow, OptionScore
from architect.providers import AdapterError, OpenAICompatibleAdapter
from architect.review_quota import ReviewQuota
from architect.scoring import DEFAULT_WEIGHTS, normalized_score
from architect.sensitivity import TRACKED_FIELDS, analyze_sensitivity

EXAMPLES: dict[str, dict[str, Path]] = {
    "investment_assistant": {
        "en": ROOT/"examples"/"investment_assistant.json",
        "pt-BR": ROOT/"examples"/"investment_assistant.pt-br.json",
    },
    "deterministic_order_lookup": {
        "en": ROOT/"examples"/"deterministic_order_lookup.json",
        "pt-BR": ROOT/"examples"/"deterministic_order_lookup.pt-br.json",
    },
    "policy_qa_assistant": {
        "en": ROOT/"examples"/"policy_qa_assistant.json",
        "pt-BR": ROOT/"examples"/"policy_qa_assistant.pt-br.json",
    },
    "research_agent": {
        "en": ROOT/"examples"/"research_agent.json",
        "pt-BR": ROOT/"examples"/"research_agent.pt-br.json",
    },
    "support_orchestrator": {
        "en": ROOT/"examples"/"support_orchestrator.json",
        "pt-BR": ROOT/"examples"/"support_orchestrator.pt-br.json",
    },
}
CANDIDATE_KEYS = ("model_candidate_a",
                  "model_candidate_b", "model_candidate_c")
CANDIDATE_COLS = ("a", "b", "c")

AI_REVIEW_SHARED_DAILY_CAP = 20
AI_REVIEW_SHARED_PER_SESSION_CAP = 3
AI_REVIEW_SHARED_MAX_TOKENS = 5000

_SENSITIVITY_METRIC_LABEL_KEYS = {
    "architecture_pattern": "architecture_metric_label",
    "integration_pattern": "integration_metric_label",
    "entry_point": "entry_point_metric_label",
    "reference_architecture": "reference_architecture_metric_label",
    "feasibility_verdict": "feasibility_verdict_metric_label",
    "review_placement": "review_placement_metric_label",
}
assert set(_SENSITIVITY_METRIC_LABEL_KEYS) == set(TRACKED_FIELDS)


@st.cache_resource
def _ai_review_shared_quota_state() -> ReviewQuota:
    """One atomic request-attempt budget per server process."""
    return ReviewQuota(AI_REVIEW_SHARED_DAILY_CAP)


def _ai_review_shared_quota_exceeded(lang: str) -> str | None:
    """Reserve budget before a request; errors also consume the reservation."""
    if st.session_state.get("ai_review_shared_uses", 0) >= AI_REVIEW_SHARED_PER_SESSION_CAP:
        return t(lang, "ai_review_shared_session_limit")
    if not _ai_review_shared_quota_state().reserve(datetime.datetime.now(datetime.UTC).date()):
        return t(lang, "ai_review_shared_daily_limit")
    st.session_state["ai_review_shared_uses"] = st.session_state.get("ai_review_shared_uses", 0) + 1
    return None


def _load_example(example_key: str) -> None:
    """Load one of the bundled examples for the current language.

    Reads the JSON file matching `lang` from `EXAMPLES[example_key]` and
    seeds `session_state` from it via `_apply_plan_dict`.

    Args:
        example_key: A key of `EXAMPLES` (e.g. "investment_assistant").
    """
    data = json.loads(EXAMPLES[example_key][lang].read_text(encoding="utf-8"))
    _apply_plan_dict(data)


def _clear_form() -> None:
    """Reset every form field to its default value.

    Iterates `ArchitectureCase().model_dump()` generically rather than a
    hardcoded field list, so a new `ArchitectureCase` field needs no change
    here - only a widget for it in the relevant tab. Also drops any stored
    AI review, since it would otherwise keep describing a plan that no
    longer exists.
    """
    for field, value in ArchitectureCase().model_dump().items():
        st.session_state[field] = value
    st.session_state["option_a_name"] = t(DEFAULT_LANG, "option_a_default")
    st.session_state["option_b_name"] = t(DEFAULT_LANG, "option_b_default")
    st.session_state["option_c_name"] = t(DEFAULT_LANG, "option_c_default")
    st.session_state.pop("selected_option", None)
    st.session_state["tradeoff_notes"] = ""
    for idx in range(3):
        for criterion in DEFAULT_WEIGHTS:
            st.session_state[f"{idx}-{criterion}"] = 3
    for key in CANDIDATE_KEYS:
        st.session_state[key] = ""
    for crit_key in MODEL_CRITERIA:
        for col in CANDIDATE_COLS:
            st.session_state[f"model_note_{crit_key}_{col}"] = ""
    st.session_state.pop("ai_review_result", None)


def _apply_plan_dict(data: dict) -> None:
    """Seed session_state from a DecisionPlan-shaped dict (model_dump()).

    Shared by "load a saved case" and "import a JSON plan" - both just need
    to populate the same widget keys before the next rerun. Must only be
    called before the widgets it targets are instantiated in the current
    script run (e.g. via the pending-flag + `st.rerun()` pattern), since
    Streamlit silently ignores a `session_state` write for an
    already-instantiated widget. Also drops any stored AI review, since
    it would otherwise keep describing the plan being replaced.

    Args:
        data: A dict shaped like `DecisionPlan.model_dump()` (or a subset
            of it) - typically a saved case or an imported JSON plan.
    """
    case_data = {**ArchitectureCase().model_dump(), **(data.get("case") or {})}
    for field, value in case_data.items():
        st.session_state[field] = value

    option_scores = data.get("option_scores") or []
    option_name_keys = ("option_a_name", "option_b_name", "option_c_name")
    for idx, key in enumerate(option_name_keys):
        entry = option_scores[idx] if idx < len(option_scores) else {}
        st.session_state[key] = entry.get("name", "")
        for criterion in DEFAULT_WEIGHTS:
            st.session_state[f"{idx}-{criterion}"] = entry.get(
                "scores", {}).get(criterion, 3)

    st.session_state["selected_option"] = data.get("selected_option", "")
    st.session_state["tradeoff_notes"] = data.get("tradeoff_notes", "")

    comparison = data.get("model_comparison") or []
    candidate_names: list[str] = []
    for row in comparison:
        for name in row.get("notes", {}):
            if name and name not in candidate_names:
                candidate_names.append(name)
    for idx, key in enumerate(CANDIDATE_KEYS):
        st.session_state[key] = candidate_names[idx] if idx < len(
            candidate_names) else ""
    for idx, crit_key in enumerate(MODEL_CRITERIA):
        row_notes = comparison[idx].get(
            "notes", {}) if idx < len(comparison) else {}
        for col, cand in zip(CANDIDATE_COLS, candidate_names):
            st.session_state[f"model_note_{crit_key}_{col}"] = row_notes.get(
                cand, "")
    st.session_state.pop("ai_review_result", None)


def field_text(key: str, label_key: str, *, area: bool = False, placeholder_key: str | None = None, default_text: str | None = None) -> str:
    """Render a text input/area whose widget arguments never vary by language.

    Streamlit resets a keyed widget's stored value whenever any other
    argument (label, placeholder, ...) differs between reruns, which
    silently breaks state on a language switch. This helper works around
    that by rendering the translated label as a separate `st.markdown`
    next to a `label_visibility="collapsed"` widget whose own arguments
    stay constant across reruns; any translated text goes below as a
    `st.caption` instead of a widget argument.

    Args:
        key: The `session_state` key, used as the widget's own key.
        label_key: The `i18n.UI` key for the field's label.
        area: Whether to render a multi-line `st.text_area` instead of a
            single-line `st.text_input`.
        placeholder_key: The `i18n.UI` key for a caption shown below the
            field, if any.
        default_text: A default value to seed `session_state[key]` with
            the first time this field is rendered.

    Returns:
        The field's current value.
    """
    st.markdown(f"**{t(lang, label_key)}**")
    if default_text is not None and key not in st.session_state:
        st.session_state[key] = default_text
    widget = st.text_area if area else st.text_input
    value = widget(key, key=key, label_visibility="collapsed")
    if placeholder_key:
        st.caption(t(lang, placeholder_key))
    return value


def field_checkbox(key: str, label_key: str, *, default: bool = False) -> bool:
    """Render a checkbox with its translated label in a separate column.

    Same widget-state rationale as `field_text`: the checkbox itself takes
    no label argument, so switching languages can never reset it.

    Args:
        key: The `session_state` key, used as the widget's own key.
        label_key: The `i18n.UI` key for the checkbox's label.
        default: Whether to default the checkbox to checked the first time
            it is rendered.

    Returns:
        Whether the checkbox is currently checked.
    """
    if default and key not in st.session_state:
        st.session_state[key] = True
    box_col, label_col = st.columns([0.08, 0.92])
    with box_col:
        value = st.checkbox(key, key=key, label_visibility="collapsed")
    with label_col:
        st.markdown(t(lang, label_key))
    return value


def field_number(key: str, label_key: str, *, placeholder_key: str | None = None) -> float:
    """Render a numeric input whose widget arguments never vary by language.

    Same widget-state rationale as `field_text`/`field_checkbox`.

    Args:
        key: The `session_state` key, used as the widget's own key.
        label_key: The `i18n.UI` key for the field's label.
        placeholder_key: The `i18n.UI` key for a caption shown below the
            field, if any.

    Returns:
        The field's current value (0.0 or greater, in steps of 50.0).
    """
    st.markdown(f"**{t(lang, label_key)}**")
    value = st.number_input(
        key, key=key, label_visibility="collapsed", min_value=0.0, step=50.0)
    if placeholder_key:
        st.caption(t(lang, placeholder_key))
    return value


if "lang" not in st.session_state:
    st.session_state["lang"] = DEFAULT_LANG

st.set_page_config(
    page_title=BRAND[st.session_state["lang"]], layout="wide")

lang = st.sidebar.selectbox(
    t(st.session_state["lang"], "lang_label"),
    LANGS,
    index=LANGS.index(st.session_state["lang"]),
    key="lang",
)

example_choice = st.sidebar.selectbox(
    t(lang, "load_example_select_label"),
    list(EXAMPLES.keys()),
    format_func=lambda key: t(lang, f"example_{key}_label"),
    key="example_choice",
)
if st.sidebar.button(t(lang, "load_example_button")):
    _load_example(example_choice)
    st.rerun()
if st.sidebar.button(t(lang, "clear_form_button")):
    _clear_form()
    st.rerun()

pending_case_name = st.session_state.pop("_pending_saved_case_load", None)
if pending_case_name is not None:
    saved = st.session_state.get("saved_cases", {})
    if pending_case_name in saved:
        _apply_plan_dict(saved[pending_case_name])

uploaded_plan = st.sidebar.file_uploader(t(lang, "import_json_label"), type=[
                                         "json"], key="import_json_uploader")
import_digest = hashlib.sha256(uploaded_plan.getvalue()).hexdigest() if uploaded_plan is not None else None
if uploaded_plan is None:
    st.session_state.pop("_last_import_digest", None)
if uploaded_plan is not None and st.session_state.get("_last_import_digest") != import_digest:
    try:
        validated = DecisionPlan.model_validate_json(uploaded_plan.getvalue())
    except Exception as exc:  # noqa: BLE001 - surfaced to the user, not swallowed
        st.sidebar.error(t(lang, "import_json_error").format(error=exc))
    else:
        _apply_plan_dict(validated.model_dump())
        st.session_state["_last_import_digest"] = import_digest
        st.sidebar.success(t(lang, "import_json_success"))
        st.rerun()

st.title(t(lang, "app_title"))
st.caption(t(lang, "app_caption"))
st.info(t(lang, "onboarding_hint"))

with st.sidebar:
    st.header(t(lang, "sidebar_header"))
    st.markdown(t(lang, "sidebar_steps"))
    st.info(t(lang, "sidebar_rule"))

basic, execution, info, risk_eval, compare, models_tab, final = st.tabs([
    t(lang, "tab_1"), t(lang, "tab_2"), t(lang, "tab_3"), t(lang, "tab_4"),
    t(lang, "tab_5"), t(lang, "tab_7"), t(lang, "tab_6"),
])

with basic:
    st.subheader(t(lang, "t1_subheader"))
    left, right = st.columns(2)
    st.caption(t(lang, "discovery_framing_hint"))
    with left:
        name = field_text("name", "case_name_label", default_text=t(
            DEFAULT_LANG, "case_name_default"))
        business_problem = field_text("business_problem", "business_problem_label",
                                      area=True, placeholder_key="business_problem_placeholder")
        desired_outcome = field_text("desired_outcome", "desired_outcome_label",
                                     area=True, placeholder_key="desired_outcome_placeholder")
        users = field_text("users", "users_label",
                           placeholder_key="users_placeholder")
        roi_notes = field_text("roi_notes", "roi_notes_label",
                               area=True, placeholder_key="roi_notes_placeholder")
    with right:
        quality_target = field_text(
            "quality_target", "quality_target_label", placeholder_key="quality_target_placeholder")
        latency_target = field_text(
            "latency_target", "latency_target_label", placeholder_key="latency_target_placeholder")
        cost_constraint = field_text(
            "cost_constraint", "cost_constraint_label", placeholder_key="cost_constraint_placeholder")
        regulatory_constraints = field_text("regulatory_constraints", "regulatory_constraints_label",
                                            area=True, placeholder_key="regulatory_constraints_placeholder")
        estimated_monthly_cost = field_number(
            "estimated_monthly_cost", "estimated_monthly_cost_label", placeholder_key="estimated_monthly_cost_placeholder")
        monthly_cost_ceiling = field_number(
            "monthly_cost_ceiling", "monthly_cost_ceiling_label", placeholder_key="monthly_cost_ceiling_placeholder")

with execution:
    st.subheader(t(lang, "t2_subheader"))
    st.write(t(lang, "t2_intro"))
    deterministic_sufficient = field_checkbox("deterministic_sufficient", "deterministic_sufficient_label")
    c1, c2 = st.columns(2)
    with c1:
        path_known = field_checkbox(
            "path_known", "path_known_label", default=True)
        dynamic_next_steps = field_checkbox(
            "dynamic_next_steps", "dynamic_next_steps_label")
        dynamic_tool_choice = field_checkbox(
            "dynamic_tool_choice", "dynamic_tool_choice_label")
        bounded_known_tool_set = field_checkbox(
            "bounded_known_tool_set", "bounded_known_tool_set_label")
        is_engineering_tool = field_checkbox(
            "is_engineering_tool", "is_engineering_tool_label")
    with c2:
        independent_autonomous_domains = field_checkbox(
            "independent_autonomous_domains", "independent_autonomous_domains_label")
        strict_auditability = field_checkbox(
            "strict_auditability", "strict_auditability_label")
        structured_output = field_checkbox(
            "structured_output", "structured_output_label")
        needs_custom_user_experience = field_checkbox(
            "needs_custom_user_experience", "needs_custom_user_experience_label")
        reusable_across_multiple_clients = field_checkbox(
            "reusable_across_multiple_clients", "reusable_across_multiple_clients_label")

with info:
    st.subheader(t(lang, "t3_subheader"))
    c1, c2 = st.columns(2)
    with c1:
        needs_document_knowledge = field_checkbox(
            "needs_document_knowledge", "needs_document_knowledge_label")
        needs_dynamic_data = field_checkbox(
            "needs_dynamic_data", "needs_dynamic_data_label")
        long_running_context = field_checkbox(
            "long_running_context", "long_running_context_label")
    with c2:
        existing_api = field_checkbox("existing_api", "existing_api_label")
        many_external_capabilities = field_checkbox(
            "many_external_capabilities", "many_external_capabilities_label")
        remote_autonomous_service = field_checkbox(
            "remote_autonomous_service", "remote_autonomous_service_label")

with risk_eval:
    st.subheader(t(lang, "t4_subheader"))
    c1, c2 = st.columns(2)
    with c1:
        sensitive_data = field_checkbox(
            "sensitive_data", "sensitive_data_label")
        high_impact_actions = field_checkbox(
            "high_impact_actions", "high_impact_actions_label")
        irreversible_actions = field_checkbox(
            "irreversible_actions", "irreversible_actions_label")
        human_approval_required = field_checkbox(
            "human_approval_required", "human_approval_required_label")
    with c2:
        subjective_quality = field_checkbox(
            "subjective_quality", "subjective_quality_label", default=True)
        critical_cohorts = field_checkbox(
            "critical_cohorts", "critical_cohorts_label")
        differential_outcomes_risk = field_checkbox(
            "differential_outcomes_risk", "differential_outcomes_risk_label")
        has_calibrated_confidence_score = field_checkbox(
            "has_calibrated_confidence_score", "has_calibrated_confidence_score_label")
        st.markdown(t(lang, "ops_note"))

case = ArchitectureCase(
    name=name,
    business_problem=business_problem,
    desired_outcome=desired_outcome,
    users=users,
    quality_target=quality_target,
    latency_target=latency_target,
    cost_constraint=cost_constraint,
    regulatory_constraints=regulatory_constraints,
    deterministic_sufficient=deterministic_sufficient,
    path_known=path_known,
    dynamic_next_steps=dynamic_next_steps,
    dynamic_tool_choice=dynamic_tool_choice,
    bounded_known_tool_set=bounded_known_tool_set,
    independent_autonomous_domains=independent_autonomous_domains,
    needs_document_knowledge=needs_document_knowledge,
    needs_dynamic_data=needs_dynamic_data,
    existing_api=existing_api,
    many_external_capabilities=many_external_capabilities,
    remote_autonomous_service=remote_autonomous_service,
    long_running_context=long_running_context,
    sensitive_data=sensitive_data,
    high_impact_actions=high_impact_actions,
    irreversible_actions=irreversible_actions,
    human_approval_required=human_approval_required,
    strict_auditability=strict_auditability,
    structured_output=structured_output,
    subjective_quality=subjective_quality,
    critical_cohorts=critical_cohorts,
    is_engineering_tool=is_engineering_tool,
    needs_custom_user_experience=needs_custom_user_experience,
    reusable_across_multiple_clients=reusable_across_multiple_clients,
    differential_outcomes_risk=differential_outcomes_risk,
    has_calibrated_confidence_score=has_calibrated_confidence_score,
    estimated_monthly_cost=estimated_monthly_cost,
    monthly_cost_ceiling=monthly_cost_ceiling,
    roi_notes=roi_notes,
)
rec = recommend(case)

with compare:
    st.subheader(t(lang, "t5_subheader"))
    st.write(t(lang, "t5_intro"))
    option_names = [
        field_text("option_a_name", "option_a_label",
                   default_text=t(DEFAULT_LANG, "option_a_default")),
        field_text("option_b_name", "option_b_label",
                   default_text=t(DEFAULT_LANG, "option_b_default")),
        field_text("option_c_name", "option_c_label",
                   default_text=t(DEFAULT_LANG, "option_c_default")),
    ]
    all_option_scores: list[dict[str, int]] = [dict(), dict(), dict()]
    for criterion, weight in DEFAULT_WEIGHTS.items():
        st.markdown(
            f"**{translate_criterion(lang, criterion)}** · {t(lang, 'weight_word')} {weight}")
        cols = st.columns(3)
        for idx, col in enumerate(cols):
            with col:
                score_key = f"{idx}-{criterion}"
                st.session_state.setdefault(score_key, 3)
                all_option_scores[idx][criterion] = st.slider(
                    f"{option_names[idx]} · {criterion}", 1, 5,
                    key=score_key, label_visibility="collapsed"
                )
    option_scores = [OptionScore(name=n.strip(), scores=s)
                     for n, s in zip(option_names, all_option_scores) if n.strip()]
    selectable_names = [option.name for option in option_scores]
    scores = {o.name: normalized_score(o.scores) for o in option_scores}
    if scores:
        best_name = max(scores, key=scores.get)
        st.metric(t(lang, "highest_score_label"),
                  f"{best_name} · {scores[best_name]:.1%}")
    else:
        st.info(t(lang, "no_named_options"))
    st.caption(e(lang, "option_matrix_methodology_note"))
    st.caption(f"{e(lang, 'recommended_pattern_note')}: {translate_pattern(lang, rec.architecture_pattern)}")
    st.markdown(f"**{t(lang, 'selected_option_label')}**")
    if selectable_names:
        if st.session_state.get("selected_option") not in selectable_names:
            st.session_state["selected_option"] = best_name
        selected_option = st.selectbox(
            "selected_option", selectable_names, key="selected_option", label_visibility="collapsed"
        )
    else:
        st.session_state.pop("selected_option", None)
        selected_option = ""
    tradeoff_notes = field_text("tradeoff_notes", "tradeoff_notes_label",
                                area=True, placeholder_key="tradeoff_notes_placeholder")

with models_tab:
    st.subheader(t(lang, "tab_7"))
    st.write(t(lang, "models_intro"))
    candidate_names = [
        field_text("model_candidate_a", "model_candidate_a_label",
                   default_text=t(DEFAULT_LANG, "model_candidate_a_default")),
        field_text("model_candidate_b", "model_candidate_b_label",
                   default_text=t(DEFAULT_LANG, "model_candidate_b_default")),
        field_text("model_candidate_c", "model_candidate_c_label",
                   default_text=t(DEFAULT_LANG, "model_candidate_c_default")),
    ]
    model_comparison_rows: list[ModelComparisonRow] = []
    for crit_key in MODEL_CRITERIA:
        st.markdown(f"**{t(lang, crit_key)}**")
        cols = st.columns(3)
        notes: dict[str, str] = {}
        for col, col_letter, cand_name in zip(cols, CANDIDATE_COLS, candidate_names):
            with col:
                st.caption(cand_name or "—")
                notes_key = f"model_note_{crit_key}_{col_letter}"
                value = st.text_input(
                    notes_key, key=notes_key, label_visibility="collapsed")
                if cand_name:
                    notes[cand_name] = value
        model_comparison_rows.append(ModelComparisonRow(
            criterion=t(lang, crit_key), notes=notes))

plan = DecisionPlan(
    case=case,
    recommendation=rec,
    option_scores=option_scores,
    selected_option=selected_option,
    tradeoff_notes=tradeoff_notes,
    model_comparison=model_comparison_rows,
)

with final:
    st.subheader(t(lang, "t6_subheader"))
    a, b = st.columns(2)
    with a:
        st.metric(t(lang, "architecture_metric_label"),
                  translate_pattern(lang, rec.architecture_pattern))
    with b:
        st.metric(t(lang, "integration_metric_label"),
                  translate_pattern(lang, rec.integration_pattern))

    c_, d_ = st.columns(2)
    with c_:
        st.metric(t(lang, "entry_point_metric_label"),
                  translate_pattern(lang, rec.entry_point))
    with d_:
        st.metric(t(lang, "reference_architecture_metric_label"),
                  translate_pattern(lang, rec.reference_architecture))

    e_, f_ = st.columns(2)
    with e_:
        st.metric(t(lang, "feasibility_verdict_metric_label"),
                  translate_pattern(lang, rec.feasibility_verdict))
        if rec.warnings:
            st.caption(e(lang, "feasibility_warnings_hint"))
    with f_:
        st.metric(t(lang, "review_placement_metric_label"),
                  translate_pattern(lang, rec.review_placement))

    if plan.case.roi_notes:
        roi_notes_safe = plan.case.roi_notes.replace("$", "\\$")
        st.markdown(
            f"**{t(lang, 'roi_notes_metric_label')}:** {roi_notes_safe}")

    if rec.warnings:
        for warning in translate_items(lang, rec.warnings):
            st.warning(warning)

    sensitivity_findings = analyze_sensitivity(case, baseline=rec)
    with st.expander(t(lang, "sensitivity_heading")):
        st.caption(t(lang, "sensitivity_intro"))
        if not sensitivity_findings:
            st.write(t(lang, "sensitivity_empty"))
        for finding in sensitivity_findings:
            action = t(lang, "sensitivity_check_to" if finding.flipped_to else "sensitivity_uncheck_to")
            st.markdown(t(lang, "sensitivity_finding_header").format(
                action=action, field_label=t(lang, f"{finding.field}_label")))
            for metric_field, old_value, new_value in finding.changes:
                st.markdown("- " + t(lang, "sensitivity_change_line").format(
                    metric_label=t(lang, _SENSITIVITY_METRIC_LABEL_KEYS[metric_field]),
                    old_value=translate_pattern(lang, old_value),
                    new_value=translate_pattern(lang, new_value),
                ))

            for warning in translate_items(lang, list(finding.warnings)):
                st.warning(warning)
            for warning in translate_items(lang, list(finding.resolved_warnings)):
                st.info(t(lang, "sensitivity_resolved_warning").format(warning=warning))

    st.markdown(t(lang, "rationale_heading"))
    for item in translate_items(lang, rec.rationale):
        st.write(f"- {item}")

    st.markdown(t(lang, "information_heading"))
    for item in translate_items(lang, rec.information_strategy):
        st.write(f"- {item}")

    st.markdown(t(lang, "model_strategy_heading"))
    for item in translate_items(lang, rec.model_strategy):
        st.write(f"- {item}")

    comparison_lines = model_comparison_lines(plan, lang)
    if comparison_lines:
        st.markdown(t(lang, "model_comparison_screen_heading"))
        for line in comparison_lines:
            st.write(line)

    st.markdown(t(lang, "controls_heading"))
    for item in translate_items(lang, rec.controls):
        st.write(f"- {item}")

    st.markdown(t(lang, "evaluation_heading"))
    for item in translate_items(lang, rec.evaluations):
        st.write(f"- {item}")

    st.markdown(t(lang, "operations_heading"))
    for item in translate_items(lang, rec.operations):
        st.write(f"- {item}")

    md = to_markdown(plan, lang)

    sensitivity_lines = [
        "## Sensitivity findings (deterministic)",
        "Hypothetical single-boolean changes, not validated alternative designs. "
        "Check conflicting assumptions and scenario warnings before interpreting a change.",
    ]
    if sensitivity_findings:
        for finding in sensitivity_findings:
            action = "Checking" if finding.flipped_to else "Unchecking"
            sensitivity_lines.append(f"- {action} `{finding.field}` would change:")
            for metric_field, old_value, new_value in finding.changes:
                sensitivity_lines.append(f"  - {metric_field}: {old_value} -> {new_value}")
            for warning in finding.warnings:
                sensitivity_lines.append(f"  - Scenario warning: {warning}")
            for warning in finding.resolved_warnings:
                sensitivity_lines.append(f"  - Warning no longer present: {warning}")
    else:
        sensitivity_lines.append("No single boolean flip changes the tracked outputs or warnings.")
    review_user_content = md + "\n\n" + "\n".join(sensitivity_lines)

    review_plan_digest = hashlib.sha256(review_user_content.encode("utf-8")).hexdigest()
    if st.session_state.get("ai_review_plan_digest") != review_plan_digest:
        st.session_state.pop("ai_review_result", None)
    st.session_state["ai_review_plan_digest"] = review_plan_digest
    docx = to_docx_bytes(plan, lang)
    pdf = to_pdf_bytes(plan, lang)
    adr = to_adr_markdown(plan, lang)
    json_bytes = plan.model_dump_json(indent=2).encode("utf-8")

    st.markdown(t(lang, "export_heading"))
    d1, d2, d3, d4, d5 = st.columns(5)
    d1.download_button(t(lang, "download_markdown_label"), md,
                       file_name="architecture-decision-plan.md", mime="text/markdown")
    d2.download_button(t(lang, "download_docx_label"), docx, file_name="architecture-decision-plan.docx",
                       mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    d3.download_button(t(lang, "download_pdf_label"), pdf,
                       file_name="architecture-decision-plan.pdf", mime="application/pdf")
    d4.download_button(t(lang, "download_adr_label"), adr,
                       file_name="adr.md", mime="text/markdown")
    d5.download_button(t(lang, "download_json_label"), json_bytes,
                       file_name="architecture-decision-plan.json", mime="application/json")

    with st.expander(t(lang, "preview_expander_label")):
        st.code(md, language="markdown")

    st.divider()
    st.markdown(f"**{t(lang, 'saved_cases_header')}**")
    st.caption(t(lang, "saved_cases_note"))
    saved_cases: dict[str, dict] = st.session_state.setdefault(
        "saved_cases", {})
    sc1, sc2 = st.columns([0.6, 0.4])
    with sc1:
        st.caption(t(lang, "saved_case_name_placeholder"))
        save_name = st.text_input(
            "save_case_name", key="save_case_name_input", label_visibility="collapsed")
    with sc2:
        if st.button(t(lang, "save_case_button")) and save_name:
            saved_cases[save_name] = plan.model_dump()
            st.toast(t(lang, "case_saved_toast"))
    if saved_cases:
        lc1, lc2, lc3 = st.columns([0.5, 0.25, 0.25])
        with lc1:
            chosen = st.selectbox(
                t(lang, "load_saved_case_label"), list(saved_cases.keys()),
                key="saved_case_select", label_visibility="collapsed",
            )
        with lc2:
            if st.button(t(lang, "load_saved_case_button")) and chosen:
                st.session_state["_pending_saved_case_load"] = chosen
                st.rerun()
        with lc3:
            if st.button(t(lang, "delete_saved_case_button")) and chosen:
                del saved_cases[chosen]
                st.rerun()
    else:
        st.caption(t(lang, "no_saved_cases"))

    st.divider()
    with st.expander(t(lang, "ai_review_expander_label")):
        st.write(t(lang, "ai_review_intro"))

        try:
            shared_secrets = dict(st.secrets.get("ai_review", {}))
        except Exception:
            shared_secrets = {}
        shared_available = bool(
            shared_secrets.get("base_url") and shared_secrets.get("api_key") and shared_secrets.get("model"))

        if shared_available:
            st.caption(t(lang, "ai_review_mode_label"))
            ai_review_mode = st.radio(
                "ai_review_mode",
                options=["shared", "byo"],
                format_func=lambda v: t(lang, "ai_review_mode_shared") if v == "shared" else t(lang, "ai_review_mode_byo"),
                key="ai_review_mode",
                label_visibility="collapsed",
                horizontal=True,
            )
        else:
            ai_review_mode = "byo"

        if ai_review_mode == "shared":
            st.caption(
                t(lang, "ai_review_shared_caption").format(
                    model=shared_secrets["model"],
                    daily=AI_REVIEW_SHARED_DAILY_CAP,
                    session=AI_REVIEW_SHARED_PER_SESSION_CAP,
                )
            )
            ai_base_url = ai_api_key = ai_model = None
        else:
            ac1, ac2, ac3 = st.columns(3)
            with ac1:
                st.caption(t(lang, "ai_review_base_url_label"))
                ai_base_url = st.text_input(
                    "ai_base_url", key="ai_base_url", label_visibility="collapsed")
            with ac2:
                st.caption(t(lang, "ai_review_api_key_label"))
                ai_api_key = st.text_input(
                    "ai_api_key", key="ai_api_key", type="password", label_visibility="collapsed")
            with ac3:
                st.caption(t(lang, "ai_review_model_label"))
                ai_model = st.text_input(
                    "ai_model", key="ai_model", label_visibility="collapsed")

        if st.button(t(lang, "ai_review_button")):
            if ai_review_mode == "shared":
                quota_error = _ai_review_shared_quota_exceeded(lang)
                if quota_error:
                    st.warning(quota_error)
                else:
                    try:
                        with st.spinner(t(lang, "ai_review_loading")):
                            adapter = OpenAICompatibleAdapter(
                                base_url=shared_secrets["base_url"],
                                api_key=shared_secrets["api_key"],
                                model=shared_secrets["model"],
                                max_tokens=AI_REVIEW_SHARED_MAX_TOKENS,
                            )
                            review = adapter.generate(
                                system=t(lang, "ai_review_system_prompt"), user=review_user_content)
                    except (ValueError, AdapterError) as exc:
                        st.session_state.pop("ai_review_result", None)
                        st.error(t(lang, "ai_review_error").format(error=exc))
                    else:
                        st.session_state["ai_review_result"] = review
            elif not (ai_base_url and ai_api_key and ai_model):
                st.warning(t(lang, "ai_review_intro"))
            else:
                try:
                    with st.spinner(t(lang, "ai_review_loading")):
                        adapter = OpenAICompatibleAdapter(
                            base_url=ai_base_url, api_key=ai_api_key, model=ai_model)
                        review = adapter.generate(
                            system=t(lang, "ai_review_system_prompt"), user=review_user_content)
                except (ValueError, AdapterError) as exc:
                    st.session_state.pop("ai_review_result", None)
                    st.error(t(lang, "ai_review_error").format(error=exc))
                else:
                    st.session_state["ai_review_result"] = review

        if st.session_state.get("ai_review_result"):
            st.warning(t(lang, "ai_review_disclaimer"))
            st.markdown(st.session_state["ai_review_result"])
            st.download_button(
                t(lang, "download_ai_review_label"),
                st.session_state["ai_review_result"],
                file_name="ai-review.md", mime="text/markdown",
            )
