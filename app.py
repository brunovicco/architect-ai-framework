import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import streamlit as st

from arquiteto.engine import recommend
from arquiteto.exporters import to_docx_bytes, to_markdown
from arquiteto.i18n import BRAND, DEFAULT_LANG, LANGS, t, translate_criterion, translate_items, translate_pattern
from arquiteto.models import ArchitectureCase, DecisionPlan, OptionScore
from arquiteto.scoring import DEFAULT_WEIGHTS, normalized_score

EXAMPLE_PATH = ROOT / "examples" / "investment_assistant.json"


def _load_example() -> None:
    defaults = ArchitectureCase().model_dump()
    data = json.loads(EXAMPLE_PATH.read_text(encoding="utf-8"))
    for field, value in {**defaults, **data}.items():
        st.session_state[field] = value


def field_text(key: str, label_key: str, *, area: bool = False, placeholder_key: str | None = None, default_text: str | None = None) -> str:
    # Every widget argument below must stay identical across reruns (only
    # `key` may vary): Streamlit resets a widget's stored value whenever any
    # of its other parameters change between runs, which breaks state when
    # the label/placeholder text is translated on a language switch. So the
    # translated label/placeholder are rendered as plain text next to a
    # label_visibility="collapsed" widget instead of being passed into it.
    st.markdown(f"**{t(lang, label_key)}**")
    if default_text is not None and key not in st.session_state:
        st.session_state[key] = default_text
    widget = st.text_area if area else st.text_input
    value = widget(key, key=key, label_visibility="collapsed")
    if placeholder_key:
        st.caption(t(lang, placeholder_key))
    return value


def field_checkbox(key: str, label_key: str, *, default: bool = False) -> bool:
    if default and key not in st.session_state:
        st.session_state[key] = True
    box_col, label_col = st.columns([0.08, 0.92])
    with box_col:
        value = st.checkbox(key, key=key, label_visibility="collapsed")
    with label_col:
        st.markdown(t(lang, label_key))
    return value


if "lang" not in st.session_state:
    st.session_state["lang"] = DEFAULT_LANG

st.set_page_config(page_title=BRAND[st.session_state["lang"]], page_icon="🏛️", layout="wide")

lang = st.sidebar.selectbox(
    t(st.session_state["lang"], "lang_label"),
    LANGS,
    index=LANGS.index(st.session_state["lang"]),
    key="lang",
)

if st.sidebar.button(t(lang, "load_example_button")):
    _load_example()
    st.rerun()

st.title(t(lang, "app_title"))
st.caption(t(lang, "app_caption"))

with st.sidebar:
    st.header(t(lang, "sidebar_header"))
    st.markdown(t(lang, "sidebar_steps"))
    st.info(t(lang, "sidebar_rule"))

basic, execution, info, risk_eval, compare, final = st.tabs([
    t(lang, "tab_1"), t(lang, "tab_2"), t(lang, "tab_3"), t(lang, "tab_4"), t(lang, "tab_5"), t(lang, "tab_6")
])

with basic:
    st.subheader(t(lang, "t1_subheader"))
    left, right = st.columns(2)
    with left:
        name = field_text("name", "case_name_label", default_text=t(DEFAULT_LANG, "case_name_default"))
        business_problem = field_text("business_problem", "business_problem_label", area=True, placeholder_key="business_problem_placeholder")
        desired_outcome = field_text("desired_outcome", "desired_outcome_label", area=True, placeholder_key="desired_outcome_placeholder")
        users = field_text("users", "users_label", placeholder_key="users_placeholder")
    with right:
        quality_target = field_text("quality_target", "quality_target_label", placeholder_key="quality_target_placeholder")
        latency_target = field_text("latency_target", "latency_target_label", placeholder_key="latency_target_placeholder")
        cost_constraint = field_text("cost_constraint", "cost_constraint_label", placeholder_key="cost_constraint_placeholder")
        regulatory_constraints = field_text("regulatory_constraints", "regulatory_constraints_label", area=True, placeholder_key="regulatory_constraints_placeholder")

with execution:
    st.subheader(t(lang, "t2_subheader"))
    st.write(t(lang, "t2_intro"))
    c1, c2 = st.columns(2)
    with c1:
        path_known = field_checkbox("path_known", "path_known_label", default=True)
        dynamic_next_steps = field_checkbox("dynamic_next_steps", "dynamic_next_steps_label")
        dynamic_tool_choice = field_checkbox("dynamic_tool_choice", "dynamic_tool_choice_label")
    with c2:
        independent_autonomous_domains = field_checkbox("independent_autonomous_domains", "independent_autonomous_domains_label")
        strict_auditability = field_checkbox("strict_auditability", "strict_auditability_label")
        structured_output = field_checkbox("structured_output", "structured_output_label")

with info:
    st.subheader(t(lang, "t3_subheader"))
    c1, c2 = st.columns(2)
    with c1:
        needs_document_knowledge = field_checkbox("needs_document_knowledge", "needs_document_knowledge_label")
        needs_dynamic_data = field_checkbox("needs_dynamic_data", "needs_dynamic_data_label")
        long_running_context = field_checkbox("long_running_context", "long_running_context_label")
    with c2:
        existing_api = field_checkbox("existing_api", "existing_api_label")
        many_external_capabilities = field_checkbox("many_external_capabilities", "many_external_capabilities_label")
        remote_autonomous_service = field_checkbox("remote_autonomous_service", "remote_autonomous_service_label")

with risk_eval:
    st.subheader(t(lang, "t4_subheader"))
    c1, c2 = st.columns(2)
    with c1:
        sensitive_data = field_checkbox("sensitive_data", "sensitive_data_label")
        high_impact_actions = field_checkbox("high_impact_actions", "high_impact_actions_label")
        irreversible_actions = field_checkbox("irreversible_actions", "irreversible_actions_label")
        human_approval_required = field_checkbox("human_approval_required", "human_approval_required_label")
    with c2:
        subjective_quality = field_checkbox("subjective_quality", "subjective_quality_label", default=True)
        critical_cohorts = field_checkbox("critical_cohorts", "critical_cohorts_label")
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
    path_known=path_known,
    dynamic_next_steps=dynamic_next_steps,
    dynamic_tool_choice=dynamic_tool_choice,
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
)
rec = recommend(case)

with compare:
    st.subheader(t(lang, "t5_subheader"))
    st.write(t(lang, "t5_intro"))
    option_names = [
        field_text("option_a_name", "option_a_label", default_text=t(DEFAULT_LANG, "option_a_default")),
        field_text("option_b_name", "option_b_label", default_text=t(DEFAULT_LANG, "option_b_default")),
        field_text("option_c_name", "option_c_label", default_text=t(DEFAULT_LANG, "option_c_default")),
    ]
    all_option_scores: list[dict[str, int]] = [dict(), dict(), dict()]
    for criterion, weight in DEFAULT_WEIGHTS.items():
        st.markdown(f"**{translate_criterion(lang, criterion)}** · {t(lang, 'weight_word')} {weight}")
        cols = st.columns(3)
        for idx, col in enumerate(cols):
            with col:
                all_option_scores[idx][criterion] = st.slider(
                    f"{option_names[idx]} · {criterion}", 1, 5, 3,
                    key=f"{idx}-{criterion}", label_visibility="collapsed"
                )
    option_scores = [OptionScore(name=n, scores=s) for n, s in zip(option_names, all_option_scores)]
    scores = {o.name: normalized_score(o.scores) for o in option_scores}
    best_name = max(scores, key=scores.get)
    st.metric(t(lang, "highest_score_label"), f"{best_name} · {scores[best_name]:.1%}")
    st.markdown(f"**{t(lang, 'selected_option_label')}**")
    selected_option = st.selectbox(
        "selected_option", option_names, index=option_names.index(best_name), label_visibility="collapsed"
    )
    tradeoff_notes = field_text("tradeoff_notes", "tradeoff_notes_label", area=True, placeholder_key="tradeoff_notes_placeholder")

plan = DecisionPlan(
    case=case,
    recommendation=rec,
    option_scores=option_scores,
    selected_option=selected_option,
    tradeoff_notes=tradeoff_notes,
)

with final:
    st.subheader(t(lang, "t6_subheader"))
    a, b = st.columns(2)
    with a:
        st.metric(t(lang, "architecture_metric_label"), translate_pattern(lang, rec.architecture_pattern))
    with b:
        st.metric(t(lang, "integration_metric_label"), translate_pattern(lang, rec.integration_pattern))

    if rec.warnings:
        for warning in translate_items(lang, rec.warnings):
            st.warning(warning)

    st.markdown(t(lang, "rationale_heading"))
    for item in translate_items(lang, rec.rationale):
        st.write(f"- {item}")

    st.markdown(t(lang, "information_heading"))
    for item in translate_items(lang, rec.information_strategy):
        st.write(f"- {item}")

    st.markdown(t(lang, "model_strategy_heading"))
    for item in translate_items(lang, rec.model_strategy):
        st.write(f"- {item}")

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
    docx = to_docx_bytes(plan, lang)
    json_bytes = plan.model_dump_json(indent=2).encode("utf-8")

    st.markdown(t(lang, "export_heading"))
    d1, d2, d3 = st.columns(3)
    d1.download_button(t(lang, "download_markdown_label"), md, file_name="architecture-decision-plan.md", mime="text/markdown")
    d2.download_button(t(lang, "download_docx_label"), docx, file_name="architecture-decision-plan.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    d3.download_button(t(lang, "download_json_label"), json_bytes, file_name="architecture-decision-plan.json", mime="application/json")

    with st.expander(t(lang, "preview_expander_label")):
        st.code(md, language="markdown")
