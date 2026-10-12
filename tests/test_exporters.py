from arquiteto.engine import recommend
from arquiteto.exporters import to_docx_bytes, to_markdown
from arquiteto.models import ArchitectureCase, DecisionPlan


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
