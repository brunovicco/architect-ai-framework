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

if "lang" not in st.session_state:
    st.session_state["lang"] = DEFAULT_LANG

st.set_page_config(page_title=BRAND[st.session_state["lang"]], page_icon="🏛️", layout="wide")

lang = st.sidebar.selectbox(
    t(st.session_state["lang"], "lang_label"),
    LANGS,
    index=LANGS.index(st.session_state["lang"]),
    key="lang",
)

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
        name = st.text_input(t(lang, "case_name_label"), t(lang, "case_name_default"))
        business_problem = st.text_area(t(lang, "business_problem_label"), placeholder=t(lang, "business_problem_placeholder"))
        desired_outcome = st.text_area(t(lang, "desired_outcome_label"), placeholder=t(lang, "desired_outcome_placeholder"))
        users = st.text_input(t(lang, "users_label"), placeholder=t(lang, "users_placeholder"))
    with right:
        quality_target = st.text_input(t(lang, "quality_target_label"), placeholder=t(lang, "quality_target_placeholder"))
        latency_target = st.text_input(t(lang, "latency_target_label"), placeholder=t(lang, "latency_target_placeholder"))
        cost_constraint = st.text_input(t(lang, "cost_constraint_label"), placeholder=t(lang, "cost_constraint_placeholder"))
        regulatory_constraints = st.text_area(t(lang, "regulatory_constraints_label"), placeholder=t(lang, "regulatory_constraints_placeholder"))

with execution:
    st.subheader(t(lang, "t2_subheader"))
    st.write(t(lang, "t2_intro"))
    c1, c2 = st.columns(2)
    with c1:
        path_known = st.checkbox(t(lang, "path_known_label"), value=True)
        dynamic_next_steps = st.checkbox(t(lang, "dynamic_next_steps_label"))
        dynamic_tool_choice = st.checkbox(t(lang, "dynamic_tool_choice_label"))
    with c2:
        independent_autonomous_domains = st.checkbox(t(lang, "independent_autonomous_domains_label"))
        strict_auditability = st.checkbox(t(lang, "strict_auditability_label"))
        structured_output = st.checkbox(t(lang, "structured_output_label"))

with info:
    st.subheader(t(lang, "t3_subheader"))
    c1, c2 = st.columns(2)
    with c1:
        needs_document_knowledge = st.checkbox(t(lang, "needs_document_knowledge_label"))
        needs_dynamic_data = st.checkbox(t(lang, "needs_dynamic_data_label"))
        long_running_context = st.checkbox(t(lang, "long_running_context_label"))
    with c2:
        existing_api = st.checkbox(t(lang, "existing_api_label"))
        many_external_capabilities = st.checkbox(t(lang, "many_external_capabilities_label"))
        remote_autonomous_service = st.checkbox(t(lang, "remote_autonomous_service_label"))

with risk_eval:
    st.subheader(t(lang, "t4_subheader"))
    c1, c2 = st.columns(2)
    with c1:
        sensitive_data = st.checkbox(t(lang, "sensitive_data_label"))
        high_impact_actions = st.checkbox(t(lang, "high_impact_actions_label"))
        irreversible_actions = st.checkbox(t(lang, "irreversible_actions_label"))
        human_approval_required = st.checkbox(t(lang, "human_approval_required_label"))
    with c2:
        subjective_quality = st.checkbox(t(lang, "subjective_quality_label"), value=True)
        critical_cohorts = st.checkbox(t(lang, "critical_cohorts_label"))
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
        st.text_input(t(lang, "option_a_label"), t(lang, "option_a_default")),
        st.text_input(t(lang, "option_b_label"), t(lang, "option_b_default")),
        st.text_input(t(lang, "option_c_label"), t(lang, "option_c_default")),
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
    selected_option = st.selectbox(t(lang, "selected_option_label"), option_names, index=option_names.index(best_name))
    tradeoff_notes = st.text_area(t(lang, "tradeoff_notes_label"), placeholder=t(lang, "tradeoff_notes_placeholder"))

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

    md = to_markdown(plan)
    docx = to_docx_bytes(plan)
    json_bytes = plan.model_dump_json(indent=2).encode("utf-8")

    st.markdown(t(lang, "export_heading"))
    d1, d2, d3 = st.columns(3)
    d1.download_button(t(lang, "download_markdown_label"), md, file_name="architecture-decision-plan.md", mime="text/markdown")
    d2.download_button(t(lang, "download_docx_label"), docx, file_name="architecture-decision-plan.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    d3.download_button(t(lang, "download_json_label"), json_bytes, file_name="architecture-decision-plan.json", mime="application/json")

    with st.expander(t(lang, "preview_expander_label")):
        st.code(md, language="markdown")
