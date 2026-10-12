from io import BytesIO

from docx import Document

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


def _docx_text(docx_bytes: bytes) -> str:
    return "\n".join(p.text for p in Document(BytesIO(docx_bytes)).paragraphs)


def test_exports_include_entry_point_reference_architecture_feasibility_and_review_placement():
    # One case, all 4 export formats, both languages: every new Recommendation
    # field (entry_point, reference_architecture, feasibility_verdict,
    # review_placement) must show up, correctly translated, everywhere.
    case = ArchitectureCase(name="Demo", is_engineering_tool=True, dynamic_tool_choice=True, high_impact_actions=True)
    plan = DecisionPlan(case=case, recommendation=recommend(case))

    expected = {
        "en": ("Agentic coding assistant (CLI/IDE)", "Coding agent", "Not assessed", "Pre-action approval"),
        "pt-BR": ("Assistente de código agêntico (CLI/IDE)", "Agente de código", "Não avaliado", "Aprovação prévia à ação"),
    }
    for lang, (entry_point, reference_architecture, feasibility_verdict, review_placement) in expected.items():
        md = to_markdown(plan, lang)
        adr = to_adr_markdown(plan, lang)
        docx_text = _docx_text(to_docx_bytes(plan, lang))
        pdf_bytes = to_pdf_bytes(plan, lang)
        for text in (md, adr, docx_text):
            assert entry_point in text, f"{lang}: {entry_point!r} missing from a text export"
            assert reference_architecture in text, f"{lang}: {reference_architecture!r} missing from a text export"
            assert feasibility_verdict in text, f"{lang}: {feasibility_verdict!r} missing from a text export"
            assert review_placement in text, f"{lang}: {review_placement!r} missing from a text export"
        # fpdf2's content stream is uncompressed (see exporters.to_pdf_bytes),
        # so the rendered text is a literal substring of the file's bytes —
        # except "(" / ")", which PDF string syntax requires fpdf2 to escape
        # with a backslash, so entry_point (which contains parens) is
        # checked via its escaped form instead of verbatim.
        escaped_entry_point = entry_point.replace("(", "\\(").replace(")", "\\)")
        assert escaped_entry_point.encode("latin-1") in pdf_bytes, f"{lang}: entry point missing from PDF"
        assert reference_architecture.encode("latin-1") in pdf_bytes, f"{lang}: reference architecture missing from PDF"
        assert feasibility_verdict.encode("latin-1") in pdf_bytes, f"{lang}: feasibility verdict missing from PDF"
        assert review_placement.encode("latin-1") in pdf_bytes, f"{lang}: review placement missing from PDF"


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
