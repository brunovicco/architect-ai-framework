from arquiteto.engine import recommend
from arquiteto.exporters import to_adr_markdown, to_docx_bytes, to_markdown, to_pdf_bytes
from arquiteto.models import ArchitectureCase, DecisionPlan, ModelComparisonRow


def test_markdown_contains_core_sections():
    case = ArchitectureCase(name="Demo", business_problem="Reduce review time")
    plan = DecisionPlan(case=case, recommendation=recommend(case))
    md = to_markdown(plan)
    assert "# Architecture Decision Plan — Demo" in md
    assert "## T — Trust & Controls" in md
    assert "## E — Evaluation" in md


def test_markdown_is_translated_for_pt_br():
    case = ArchitectureCase(name="Demo", business_problem="Reduce review time")
    plan = DecisionPlan(case=case, recommendation=recommend(case))
    md = to_markdown(plan, lang="pt-BR")
    assert "# Plano de Decisão de Arquitetura — Demo" in md
    assert "## A — Alvo" in md
    assert "Gerado com o framework ARQUITETO" in md


def test_docx_bytes_are_generated_for_both_languages():
    case = ArchitectureCase(name="Demo")
    plan = DecisionPlan(case=case, recommendation=recommend(case))
    for lang in ("en", "pt-BR"):
        docx = to_docx_bytes(plan, lang=lang)
        assert docx.startswith(b"PK")  # docx is a zip archive
        assert len(docx) > 0


def test_pdf_bytes_are_generated_for_both_languages():
    case = ArchitectureCase(name="Demo", business_problem="Reduzir tempo de revisão — ção ãõ")
    plan = DecisionPlan(case=case, recommendation=recommend(case))
    for lang in ("en", "pt-BR"):
        pdf = to_pdf_bytes(plan, lang=lang)
        assert pdf.startswith(b"%PDF")
        assert len(pdf) > 0


def test_pdf_does_not_crash_on_unsupported_characters():
    case = ArchitectureCase(name="Demo", business_problem="Emoji test \U0001f3db CJK 中文")
    plan = DecisionPlan(case=case, recommendation=recommend(case))
    pdf = to_pdf_bytes(plan)
    assert pdf.startswith(b"%PDF")


def test_markdown_includes_model_comparison_when_present():
    case = ArchitectureCase(name="Demo")
    row = ModelComparisonRow(criterion="Latency class", notes={"Provider A": "Low", "Provider B": "Medium"})
    plan = DecisionPlan(case=case, recommendation=recommend(case), model_comparison=[row])
    md = to_markdown(plan)
    assert "Model / Provider Comparison" in md
    assert "Latency class" in md
    assert "Provider A: Low" in md


def test_adr_markdown_contains_core_sections():
    case = ArchitectureCase(name="Demo", business_problem="Reduce review time")
    plan = DecisionPlan(case=case, recommendation=recommend(case))
    adr = to_adr_markdown(plan)
    assert "# ADR: Demo" in adr
    assert "**Status:** Proposed" in adr
    assert "## Context" in adr
    assert "## Decision" in adr
    assert "We will adopt" in adr
    assert "## Consequences" in adr


def test_exports_include_entry_point_reference_architecture_feasibility_and_review_placement():
    case = ArchitectureCase(name="Demo", is_engineering_tool=True, dynamic_tool_choice=True, high_impact_actions=True)
    plan = DecisionPlan(case=case, recommendation=recommend(case))
    md = to_markdown(plan)
    adr = to_adr_markdown(plan)
    for text in (md, adr):
        assert "Agentic coding assistant (CLI/IDE)" in text
        assert "Coding agent" in text
        assert "Pre-action approval" in text


def test_roi_notes_appears_in_exports_when_present():
    case = ArchitectureCase(name="Demo", roi_notes="Saves 5h/week for the ops team")
    plan = DecisionPlan(case=case, recommendation=recommend(case))
    md = to_markdown(plan)
    adr = to_adr_markdown(plan)
    assert "Saves 5h/week for the ops team" in md
    assert "Saves 5h/week for the ops team" in adr


def test_roi_notes_omitted_from_markdown_when_blank():
    case = ArchitectureCase(name="Demo")
    plan = DecisionPlan(case=case, recommendation=recommend(case))
    md = to_markdown(plan)
    assert "Business value / ROI" not in md
