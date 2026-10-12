"""Bilingual document generation for a `DecisionPlan`.

Four independent renderers - `to_markdown`, `to_docx_bytes`, `to_pdf_bytes`
and `to_adr_markdown` - all take the same `(plan, lang)` signature and must
stay structurally in sync: each surfaces the same fields, just in a
different format. None of them call a model or make a network request;
they only read `plan` and look up display strings through `i18n.py`.
"""

from io import BytesIO

from docx import Document
from fpdf import FPDF

from .i18n import e, translate_items, translate_pattern
from .models import DecisionPlan
from .scoring import normalized_score


def _bullets(items: list[str], lang: str) -> str:
    """Render a list of already-translated strings as a Markdown bullet list.

    Args:
        items: The (already translated) lines to render, one per bullet.
        lang: The display language, used only to translate the fallback
            "not defined" message when `items` is empty.

    Returns:
        A newline-joined Markdown bullet list, or a single "not defined"
        bullet if `items` is empty.
    """
    return "\n".join(f"- {item}" for item in items) if items else f"- {e(lang, 'not_defined')}"


def model_comparison_lines(plan: DecisionPlan, lang: str) -> list[str]:
    """Render the model/provider comparison matrix as Markdown bullet lines.

    Shared by all four exporters and by the Plan tab in `app.py`, so the
    on-screen comparison and every exported document stay identical.

    Args:
        plan: The plan whose `model_comparison` rows should be rendered.
        lang: The display language for the "not defined" fallback.

    Returns:
        One Markdown bullet line per comparison row, or an empty list if
        `plan.model_comparison` is empty.
    """
    lines = []
    for row in plan.model_comparison:
        notes = "; ".join(f"{name}: {note}" for name, note in row.notes.items(
        ) if note) or e(lang, "not_defined")
        lines.append(f"- **{row.criterion}:** {notes}")
    return lines


def to_markdown(plan: DecisionPlan, lang: str = "en") -> str:
    """Render the plan as a standalone Markdown document.

    Args:
        plan: The decision plan to render.
        lang: The display language ("en" or "pt-BR").

    Returns:
        The complete Markdown document as a string.
    """
    c = plan.case
    r = plan.recommendation
    not_defined = e(lang, "not_defined")
    option_lines = []
    for option in plan.option_scores:
        option_lines.append(
            f"- **{option.name}:** {normalized_score(option.scores):.1%}")
    option_text = "\n".join(option_lines) or f"- {e(lang, 'no_option_matrix')}"
    option_methodology_note = f"*{e(lang, 'option_matrix_methodology_note')}*\n" if plan.option_scores else ""
    comparison_lines = model_comparison_lines(plan, lang)
    comparison_block = (
        f"\n## {e(lang, 'model_comparison_heading')}\n" +
        "\n".join(comparison_lines) + "\n"
        if comparison_lines
        else ""
    )
    roi_block = f"\n**{e(lang, 'roi_notes')}:** {c.roi_notes}\n" if c.roi_notes else ""
    feasibility_hint = f" ({e(lang, 'feasibility_warnings_hint')})" if r.warnings else ""

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
- {e(lang, 'entry_point')}: **{translate_pattern(lang, r.entry_point)}**
- {e(lang, 'reference_architecture')}: **{translate_pattern(lang, r.reference_architecture)}**

### {e(lang, 'rationale')}
{_bullets(translate_items(lang, r.rationale), lang)}

## {e(lang, 'section_i')}
- {e(lang, 'recommended_integration')}: **{translate_pattern(lang, r.integration_pattern)}**
{_bullets(translate_items(lang, r.information_strategy), lang)}

## {e(lang, 'section_model')}
- {e(lang, 'feasibility_verdict')}: **{translate_pattern(lang, r.feasibility_verdict)}**{feasibility_hint}
{_bullets(translate_items(lang, r.model_strategy), lang)}
{comparison_block}{roi_block}
## {e(lang, 'section_t')}
- {e(lang, 'review_placement')}: **{translate_pattern(lang, r.review_placement)}**
{_bullets(translate_items(lang, r.controls), lang)}

## {e(lang, 'section_e')}
{_bullets(translate_items(lang, r.evaluations), lang)}

## {e(lang, 'section_tradeoffs')}
### {e(lang, 'option_matrix')}
{option_text}
{option_methodology_note}
**{e(lang, 'recommended_pattern_note')}:** {translate_pattern(lang, r.architecture_pattern)}
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
    """Render the plan as a DOCX document.

    Args:
        plan: The decision plan to render.
        lang: The display language ("en" or "pt-BR").

    Returns:
        The DOCX file's raw bytes.
    """
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
            [
                f"{e(lang, 'recommended_pattern')}: {translate_pattern(lang, r.architecture_pattern)}",
                f"{e(lang, 'entry_point')}: {translate_pattern(lang, r.entry_point)}",
                f"{e(lang, 'reference_architecture')}: {translate_pattern(lang, r.reference_architecture)}",
                *translate_items(lang, r.rationale),
            ],
        ),
        (
            e(lang, "section_i"),
            [f"{e(lang, 'recommended_integration')}: {translate_pattern(lang, r.integration_pattern)}",
             *translate_items(lang, r.information_strategy)],
        ),
        (
            e(lang, "section_model"),
            [
                f"{e(lang, 'feasibility_verdict')}: {translate_pattern(lang, r.feasibility_verdict)}"
                + (f" ({e(lang, 'feasibility_warnings_hint')})" if r.warnings else ""),
                *translate_items(lang, r.model_strategy),
                *([f"{e(lang, 'roi_notes')}: {c.roi_notes}"]
                  if c.roi_notes else []),
            ],
        ),
        (
            e(lang, "section_t"),
            [f"{e(lang, 'review_placement')}: {translate_pattern(lang, r.review_placement)}",
             *translate_items(lang, r.controls)],
        ),
        (e(lang, "section_e"), translate_items(lang, r.evaluations)),
        (e(lang, "section_operations"), translate_items(lang, r.operations)),
    ]
    for heading, items in sections:
        doc.add_heading(heading, level=1)
        for item in items:
            doc.add_paragraph(item, style="List Bullet")

    comparison_lines = model_comparison_lines(plan, lang)
    if comparison_lines:
        doc.add_heading(e(lang, "model_comparison_heading"), level=1)
        for line in comparison_lines:
            doc.add_paragraph(line.lstrip("- "), style="List Bullet")

    doc.add_heading(e(lang, "section_tradeoffs"), level=1)
    if plan.option_scores:
        for option in plan.option_scores:
            doc.add_paragraph(
                f"{option.name}: {normalized_score(option.scores):.1%}", style="List Bullet")
        doc.add_paragraph(e(lang, "option_matrix_methodology_note"))
    else:
        doc.add_paragraph(e(lang, "no_option_matrix"), style="List Bullet")
    doc.add_paragraph(
        f"{e(lang, 'recommended_pattern_note')}: {translate_pattern(lang, r.architecture_pattern)}")
    doc.add_paragraph(
        f"{e(lang, 'selected_option')}: {plan.selected_option or e(lang, 'not_selected')}")
    doc.add_paragraph(
        f"{e(lang, 'tradeoff_notes')}: {plan.tradeoff_notes or not_defined}")

    if r.warnings:
        doc.add_heading(e(lang, "warnings"), level=1)
        for item in translate_items(lang, r.warnings):
            doc.add_paragraph(item, style="List Bullet")

    doc.add_paragraph(e(lang, "footer"))

    stream = BytesIO()
    doc.save(stream)
    return stream.getvalue()


_PDF_TEXT_REPLACEMENTS = {
    "—": "-",
    "–": "-",
    "‘": "'",
    "’": "'",
    "“": '"',
    "”": '"',
    "…": "...",
    "•": "-",
}


def _pdf_safe(text: str) -> str:
    """Normalize free text so fpdf2's base Latin-1 font can render it.

    Common Unicode punctuation (em/en dashes, curly quotes, ellipsis,
    bullets) is first mapped to its closest Latin-1 equivalent; anything
    still outside Latin-1 after that (emoji, CJK, ...) is replaced rather
    than raising, so arbitrary user-supplied text can never crash PDF
    generation.

    Args:
        text: The text to normalize.

    Returns:
        A string safe to pass to fpdf2 with the default Helvetica font.
    """
    for src, dst in _PDF_TEXT_REPLACEMENTS.items():
        text = text.replace(src, dst)
    return text.encode("latin-1", errors="replace").decode("latin-1")


def _pdf_write(pdf: FPDF, text: str, *, size: int = 11, bold: bool = False, gap_before: int = 2) -> None:
    """Write one paragraph of text to a PDF at the given style.

    Args:
        pdf: The `FPDF` document being built; mutated in place.
        text: The text to write (run through `_pdf_safe` internally).
        size: The font size in points.
        bold: Whether to use the bold variant of the font.
        gap_before: Vertical space (in document units) to add before this
            paragraph.
    """
    pdf.set_font("Helvetica", "B" if bold else "", size)
    pdf.set_x(pdf.l_margin)  # multi_cell doesn't reset x on its own; w=0 would
    if gap_before:  # otherwise measure from the previous call's end-x and
        pdf.ln(gap_before)  # can raise "not enough horizontal space".
    pdf.multi_cell(0, 8 if size > 12 else 6, _pdf_safe(text))


def to_pdf_bytes(plan: DecisionPlan, lang: str = "en") -> bytes:
    """Render the plan as a PDF document.

    The PDF's content stream is left uncompressed (see `pdf.set_compression`
    below) so the rendered text stays a literal, greppable substring of the
    output bytes - this is what lets tests assert on PDF content without a
    PDF-parsing dependency.

    Args:
        plan: The decision plan to render.
        lang: The display language ("en" or "pt-BR").

    Returns:
        The PDF file's raw bytes.
    """
    c = plan.case
    r = plan.recommendation
    not_defined = e(lang, "not_defined")

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_compression(False)
    pdf.add_page()

    def heading(text: str) -> None:
        """Write a top-level section heading."""
        _pdf_write(pdf, text, size=14, bold=True, gap_before=6)

    def subheading(text: str) -> None:
        """Write a sub-section heading."""
        _pdf_write(pdf, text, size=12, bold=True, gap_before=3)

    def body(text: str) -> None:
        """Write one paragraph of regular body text."""
        _pdf_write(pdf, text, size=11, bold=False, gap_before=1)

    def bullets(items: list[str]) -> None:
        """Write each item as its own bullet, or a "not defined" placeholder if empty."""
        for item in items or [not_defined]:
            body(f"- {item}")

    _pdf_write(pdf, f"{e(lang, 'doc_title')} - {c.name}",
               size=18, bold=True, gap_before=0)

    heading(e(lang, "section_a"))
    body(f"{e(lang, 'business_problem')}: {c.business_problem or not_defined}")
    body(f"{e(lang, 'desired_outcome')}: {c.desired_outcome or not_defined}")
    body(f"{e(lang, 'users')}: {c.users or not_defined}")

    heading(e(lang, "section_r"))
    body(f"{e(lang, 'quality_target')}: {c.quality_target or not_defined}")
    body(f"{e(lang, 'latency_target')}: {c.latency_target or not_defined}")
    body(f"{e(lang, 'cost_constraint')}: {c.cost_constraint or not_defined}")
    body(f"{e(lang, 'regulatory_constraints')}: {c.regulatory_constraints or not_defined}")

    heading(e(lang, "section_responsibility"))
    body(f"{e(lang, 'recommended_pattern')}: {translate_pattern(lang, r.architecture_pattern)}")
    body(f"{e(lang, 'entry_point')}: {translate_pattern(lang, r.entry_point)}")
    body(f"{e(lang, 'reference_architecture')}: {translate_pattern(lang, r.reference_architecture)}")
    subheading(e(lang, "rationale"))
    bullets(translate_items(lang, r.rationale))

    heading(e(lang, "section_i"))
    body(f"{e(lang, 'recommended_integration')}: {translate_pattern(lang, r.integration_pattern)}")
    bullets(translate_items(lang, r.information_strategy))

    heading(e(lang, "section_model"))
    feasibility_hint = f" ({e(lang, 'feasibility_warnings_hint')})" if r.warnings else ""
    body(f"{e(lang, 'feasibility_verdict')}: {translate_pattern(lang, r.feasibility_verdict)}{feasibility_hint}")
    bullets(translate_items(lang, r.model_strategy))
    if c.roi_notes:
        body(f"{e(lang, 'roi_notes')}: {c.roi_notes}")

    comparison_lines = model_comparison_lines(plan, lang)
    if comparison_lines:
        heading(e(lang, "model_comparison_heading"))
        for line in comparison_lines:
            body(line.lstrip("- "))

    heading(e(lang, "section_t"))
    body(f"{e(lang, 'review_placement')}: {translate_pattern(lang, r.review_placement)}")
    bullets(translate_items(lang, r.controls))

    heading(e(lang, "section_e"))
    bullets(translate_items(lang, r.evaluations))

    heading(e(lang, "section_tradeoffs"))
    subheading(e(lang, "option_matrix"))
    if plan.option_scores:
        for option in plan.option_scores:
            body(f"- {option.name}: {normalized_score(option.scores):.1%}")
        body(e(lang, "option_matrix_methodology_note"))
    else:
        body(f"- {e(lang, 'no_option_matrix')}")
    body(f"{e(lang, 'recommended_pattern_note')}: {translate_pattern(lang, r.architecture_pattern)}")
    body(f"{e(lang, 'selected_option')}: {plan.selected_option or e(lang, 'not_selected')}")
    body(f"{e(lang, 'tradeoff_notes')}: {plan.tradeoff_notes or not_defined}")

    heading(e(lang, "section_operations"))
    bullets(translate_items(lang, r.operations))

    if r.warnings:
        heading(e(lang, "warnings"))
        bullets(translate_items(lang, r.warnings))

    body(e(lang, "footer"))

    return bytes(pdf.output())


def to_adr_markdown(plan: DecisionPlan, lang: str = "en") -> str:
    """Render the plan as a Nygard-style Architecture Decision Record.

    Args:
        plan: The decision plan to render.
        lang: The display language ("en" or "pt-BR").

    Returns:
        The complete ADR as a Markdown string.
    """
    c = plan.case
    r = plan.recommendation
    not_defined = e(lang, "not_defined")
    option_lines = []
    for option in plan.option_scores:
        option_lines.append(
            f"- **{option.name}:** {normalized_score(option.scores):.1%}")
    option_text = "\n".join(option_lines) or f"- {e(lang, 'no_option_matrix')}"
    option_methodology_note = f"*{e(lang, 'option_matrix_methodology_note')}*\n" if plan.option_scores else ""
    decision_intro = e(lang, "adr_decision_intro").format(
        architecture=translate_pattern(lang, r.architecture_pattern),
        integration=translate_pattern(lang, r.integration_pattern),
    )
    roi_line = f"\n**{e(lang, 'roi_notes')}:** {c.roi_notes}\n" if c.roi_notes else ""
    feasibility_hint = f" ({e(lang, 'feasibility_warnings_hint')})" if r.warnings else ""

    return f"""# {e(lang, 'adr_title_prefix')}: {c.name}

**{e(lang, 'adr_status_heading')}:** {e(lang, 'adr_status_value')}

## {e(lang, 'adr_context_heading')}
- {e(lang, 'business_problem')}: {c.business_problem or not_defined}
- {e(lang, 'desired_outcome')}: {c.desired_outcome or not_defined}
- {e(lang, 'users')}: {c.users or not_defined}
- {e(lang, 'quality_target')}: {c.quality_target or not_defined}
- {e(lang, 'latency_target')}: {c.latency_target or not_defined}
- {e(lang, 'cost_constraint')}: {c.cost_constraint or not_defined}
- {e(lang, 'regulatory_constraints')}: {c.regulatory_constraints or not_defined}

## {e(lang, 'adr_decision_heading')}
- {e(lang, 'entry_point')}: **{translate_pattern(lang, r.entry_point)}**
- {e(lang, 'reference_architecture')}: **{translate_pattern(lang, r.reference_architecture)}**
- {e(lang, 'feasibility_verdict')}: **{translate_pattern(lang, r.feasibility_verdict)}**{feasibility_hint}

{decision_intro}

{_bullets(translate_items(lang, r.rationale), lang)}
{roi_line}
## {e(lang, 'adr_consequences_heading')}

### {e(lang, 'section_t')}
- {e(lang, 'review_placement')}: {translate_pattern(lang, r.review_placement)}
{_bullets(translate_items(lang, r.controls), lang)}

### {e(lang, 'section_e')}
{_bullets(translate_items(lang, r.evaluations), lang)}

### {e(lang, 'section_operations')}
{_bullets(translate_items(lang, r.operations), lang)}

## {e(lang, 'adr_alternatives_heading')}
{option_text}
{option_methodology_note}
**{e(lang, 'recommended_pattern_note')}:** {translate_pattern(lang, r.architecture_pattern)}
**{e(lang, 'selected_option')}:** {plan.selected_option or e(lang, 'not_selected')}
**{e(lang, 'tradeoff_notes')}:** {plan.tradeoff_notes or not_defined}

---
{e(lang, 'footer')}
"""
