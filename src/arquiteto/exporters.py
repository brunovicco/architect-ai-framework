from io import BytesIO
from docx import Document

from .models import DecisionPlan
from .scoring import normalized_score


def _bullets(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items) if items else "- Not defined"


def to_markdown(plan: DecisionPlan) -> str:
    c = plan.case
    r = plan.recommendation
    option_lines = []
    for option in plan.option_scores:
        option_lines.append(f"- **{option.name}:** {normalized_score(option.scores):.1%}")
    option_text = "\n".join(option_lines) or "- No option matrix supplied"

    return f"""# Architecture Decision Plan — {c.name}

## A — Alvo
**Business problem:** {c.business_problem or 'Not defined'}  
**Desired outcome:** {c.desired_outcome or 'Not defined'}  
**Users / audience:** {c.users or 'Not defined'}

## R — Requisitos
- Quality target: {c.quality_target or 'Not defined'}
- Latency target: {c.latency_target or 'Not defined'}
- Cost constraint: {c.cost_constraint or 'Not defined'}
- Regulatory constraints: {c.regulatory_constraints or 'Not defined'}

## Q/U — Responsibility and architecture
- Recommended pattern: **{r.architecture_pattern}**

### Rationale
{_bullets(r.rationale)}

## I — Integration & Information
- Recommended integration: **{r.integration_pattern}**
{_bullets(r.information_strategy)}

## Model / Provider Strategy
{_bullets(r.model_strategy)}

## T — Trust & Controls
{_bullets(r.controls)}

## E — Evaluation
{_bullets(r.evaluations)}

## T — Trade-offs
### Option matrix
{option_text}

**Selected option:** {plan.selected_option or 'Not selected'}  
**Trade-off notes:** {plan.tradeoff_notes or 'Not defined'}

## O — Operations
{_bullets(r.operations)}

## Warnings / decisions to validate
{_bullets(r.warnings)}

---
Generated with the ARQUITETO framework — a vendor-neutral AI architecture decision method.
"""


def to_docx_bytes(plan: DecisionPlan) -> bytes:
    doc = Document()
    c = plan.case
    r = plan.recommendation

    doc.add_heading(f"Architecture Decision Plan — {c.name}", 0)

    sections = [
        ("A — Alvo", [f"Business problem: {c.business_problem or 'Not defined'}", f"Desired outcome: {c.desired_outcome or 'Not defined'}", f"Users / audience: {c.users or 'Not defined'}"]),
        ("R — Requisitos", [f"Quality target: {c.quality_target or 'Not defined'}", f"Latency target: {c.latency_target or 'Not defined'}", f"Cost constraint: {c.cost_constraint or 'Not defined'}", f"Regulatory constraints: {c.regulatory_constraints or 'Not defined'}"]),
        ("Q/U — Responsibility and architecture", [f"Recommended pattern: {r.architecture_pattern}", *r.rationale]),
        ("I — Integration & Information", [f"Recommended integration: {r.integration_pattern}", *r.information_strategy]),
        ("Model / Provider Strategy", r.model_strategy),
        ("T — Trust & Controls", r.controls),
        ("E — Evaluation", r.evaluations),
        ("O — Operations", r.operations),
    ]
    for heading, items in sections:
        doc.add_heading(heading, level=1)
        for item in items:
            doc.add_paragraph(item, style="List Bullet")

    doc.add_heading("T — Trade-offs", level=1)
    if plan.option_scores:
        for option in plan.option_scores:
            doc.add_paragraph(f"{option.name}: {normalized_score(option.scores):.1%}", style="List Bullet")
    else:
        doc.add_paragraph("No option matrix supplied", style="List Bullet")
    doc.add_paragraph(f"Selected option: {plan.selected_option or 'Not selected'}")
    doc.add_paragraph(f"Trade-off notes: {plan.tradeoff_notes or 'Not defined'}")

    if r.warnings:
        doc.add_heading("Warnings / decisions to validate", level=1)
        for item in r.warnings:
            doc.add_paragraph(item, style="List Bullet")

    doc.add_paragraph("Generated with the ARQUITETO framework — a vendor-neutral AI architecture decision method.")

    stream = BytesIO()
    doc.save(stream)
    return stream.getvalue()
