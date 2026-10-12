from io import BytesIO

from docx import Document

from .i18n import e, translate_items, translate_pattern
from .models import DecisionPlan
from .scoring import normalized_score


def _bullets(items: list[str], lang: str) -> str:
    return "\n".join(f"- {item}" for item in items) if items else f"- {e(lang, 'not_defined')}"


def to_markdown(plan: DecisionPlan, lang: str = "en") -> str:
    c = plan.case
    r = plan.recommendation
    not_defined = e(lang, "not_defined")
    option_lines = []
    for option in plan.option_scores:
        option_lines.append(f"- **{option.name}:** {normalized_score(option.scores):.1%}")
    option_text = "\n".join(option_lines) or f"- {e(lang, 'no_option_matrix')}"

    return f"""# {e(lang, 'doc_title')} — {c.name}

## {e(lang, 'section_a')}
**{e(lang, 'business_problem')}:** {c.business_problem or not_defined}
**{e(lang, 'desired_outcome')}:** {c.desired_outcome or not_defined}
**{e(lang, 'users')}:** {c.users or not_defined}

## {e(lang, 'section_r')}
- {e(lang, 'quality_target')}: {c.quality_target or not_defined}
- {e(lang, 'latency_target')}: {c.latency_target or not_defined}
- {e(lang, 'cost_constraint')}: {c.cost_constraint or not_defined}
- {e(lang, 'regulatory_constraints')}: {c.regulatory_constraints or not_defined}

## {e(lang, 'section_responsibility')}
- {e(lang, 'recommended_pattern')}: **{translate_pattern(lang, r.architecture_pattern)}**

### {e(lang, 'rationale')}
{_bullets(translate_items(lang, r.rationale), lang)}

## {e(lang, 'section_i')}
- {e(lang, 'recommended_integration')}: **{translate_pattern(lang, r.integration_pattern)}**
{_bullets(translate_items(lang, r.information_strategy), lang)}

## {e(lang, 'section_model')}
{_bullets(translate_items(lang, r.model_strategy), lang)}

## {e(lang, 'section_t')}
{_bullets(translate_items(lang, r.controls), lang)}

## {e(lang, 'section_e')}
{_bullets(translate_items(lang, r.evaluations), lang)}

## {e(lang, 'section_tradeoffs')}
### {e(lang, 'option_matrix')}
{option_text}

**{e(lang, 'selected_option')}:** {plan.selected_option or e(lang, 'not_selected')}
**{e(lang, 'tradeoff_notes')}:** {plan.tradeoff_notes or not_defined}

## {e(lang, 'section_operations')}
{_bullets(translate_items(lang, r.operations), lang)}

## {e(lang, 'warnings')}
{_bullets(translate_items(lang, r.warnings), lang)}

---
{e(lang, 'footer')}
"""


def to_docx_bytes(plan: DecisionPlan, lang: str = "en") -> bytes:
    doc = Document()
    c = plan.case
    r = plan.recommendation
    not_defined = e(lang, "not_defined")

    doc.add_heading(f"{e(lang, 'doc_title')} — {c.name}", 0)

    sections = [
        (
            e(lang, "section_a"),
            [
                f"{e(lang, 'business_problem')}: {c.business_problem or not_defined}",
                f"{e(lang, 'desired_outcome')}: {c.desired_outcome or not_defined}",
                f"{e(lang, 'users')}: {c.users or not_defined}",
            ],
        ),
        (
            e(lang, "section_r"),
            [
                f"{e(lang, 'quality_target')}: {c.quality_target or not_defined}",
                f"{e(lang, 'latency_target')}: {c.latency_target or not_defined}",
                f"{e(lang, 'cost_constraint')}: {c.cost_constraint or not_defined}",
                f"{e(lang, 'regulatory_constraints')}: {c.regulatory_constraints or not_defined}",
            ],
        ),
        (
            e(lang, "section_responsibility"),
            [f"{e(lang, 'recommended_pattern')}: {translate_pattern(lang, r.architecture_pattern)}", *translate_items(lang, r.rationale)],
        ),
        (
            e(lang, "section_i"),
            [f"{e(lang, 'recommended_integration')}: {translate_pattern(lang, r.integration_pattern)}", *translate_items(lang, r.information_strategy)],
        ),
        (e(lang, "section_model"), translate_items(lang, r.model_strategy)),
        (e(lang, "section_t"), translate_items(lang, r.controls)),
        (e(lang, "section_e"), translate_items(lang, r.evaluations)),
        (e(lang, "section_operations"), translate_items(lang, r.operations)),
    ]
    for heading, items in sections:
        doc.add_heading(heading, level=1)
        for item in items:
            doc.add_paragraph(item, style="List Bullet")

    doc.add_heading(e(lang, "section_tradeoffs"), level=1)
    if plan.option_scores:
        for option in plan.option_scores:
            doc.add_paragraph(f"{option.name}: {normalized_score(option.scores):.1%}", style="List Bullet")
    else:
        doc.add_paragraph(e(lang, "no_option_matrix"), style="List Bullet")
    doc.add_paragraph(f"{e(lang, 'selected_option')}: {plan.selected_option or e(lang, 'not_selected')}")
    doc.add_paragraph(f"{e(lang, 'tradeoff_notes')}: {plan.tradeoff_notes or not_defined}")

    if r.warnings:
        doc.add_heading(e(lang, "warnings"), level=1)
        for item in translate_items(lang, r.warnings):
            doc.add_paragraph(item, style="List Bullet")

    doc.add_paragraph(e(lang, "footer"))

    stream = BytesIO()
    doc.save(stream)
    return stream.getvalue()
