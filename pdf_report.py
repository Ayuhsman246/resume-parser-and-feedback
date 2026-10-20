"""PDF report generator for the AI Resume Analyzer.

This module provides functionality to generate a professional PDF scorecard
report from a resume analysis result dictionary. The report includes match
scores, skill analysis tables, improvement suggestions, bullet-point rewrites,
and interview preparation questions.

Dependencies:
    - reportlab
"""

import io
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


# ---------------------------------------------------------------------------
# Colour palette
# ---------------------------------------------------------------------------
_GREEN = colors.HexColor("#2e7d32")
_RED = colors.HexColor("#c62828")
_ORANGE = colors.HexColor("#ef6c00")
_LIGHT_GREEN = colors.HexColor("#e8f5e9")
_LIGHT_RED = colors.HexColor("#ffebee")
_LIGHT_ORANGE = colors.HexColor("#fff3e0")
_HEADER_BG = colors.HexColor("#1565c0")
_ALT_ROW = colors.HexColor("#f5f5f5")
_DARK_TEXT = colors.HexColor("#212121")
_GREY_TEXT = colors.HexColor("#757575")


# ---------------------------------------------------------------------------
# Style helpers
# ---------------------------------------------------------------------------

def _build_styles() -> dict:
    """Return a dictionary of custom ``ParagraphStyle`` objects."""
    base = getSampleStyleSheet()

    return {
        "title": ParagraphStyle(
            "ReportTitle",
            parent=base["Title"],
            fontName="Helvetica-Bold",
            fontSize=22,
            leading=28,
            textColor=_DARK_TEXT,
            alignment=TA_CENTER,
            spaceAfter=4,
        ),
        "subtitle": ParagraphStyle(
            "ReportSubtitle",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=10,
            leading=14,
            textColor=_GREY_TEXT,
            alignment=TA_CENTER,
            spaceAfter=12,
        ),
        "heading": ParagraphStyle(
            "SectionHeading",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=14,
            leading=18,
            textColor=_HEADER_BG,
            spaceBefore=18,
            spaceAfter=8,
        ),
        "body": ParagraphStyle(
            "BodyText",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=10,
            leading=14,
            textColor=_DARK_TEXT,
        ),
        "body_bold": ParagraphStyle(
            "BodyBold",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=14,
            textColor=_DARK_TEXT,
        ),
        "body_italic": ParagraphStyle(
            "BodyItalic",
            parent=base["Normal"],
            fontName="Helvetica-Oblique",
            fontSize=10,
            leading=14,
            textColor=_GREY_TEXT,
        ),
        "score": ParagraphStyle(
            "ScoreText",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=36,
            leading=44,
            textColor=_HEADER_BG,
            alignment=TA_CENTER,
        ),
        "score_label": ParagraphStyle(
            "ScoreLabel",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=12,
            leading=16,
            textColor=_GREY_TEXT,
            alignment=TA_CENTER,
            spaceAfter=6,
        ),
        "footer": ParagraphStyle(
            "FooterText",
            parent=base["Normal"],
            fontName="Helvetica-Oblique",
            fontSize=8,
            leading=10,
            textColor=_GREY_TEXT,
            alignment=TA_CENTER,
        ),
        "table_header": ParagraphStyle(
            "TableHeader",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=13,
            textColor=colors.white,
            alignment=TA_CENTER,
        ),
        "table_cell": ParagraphStyle(
            "TableCell",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            textColor=_DARK_TEXT,
            alignment=TA_LEFT,
        ),
    }


def _skill_bullets(skills: list) -> str:
    """Convert a list of skill strings into an HTML bullet list for Paragraph."""
    if not skills:
        return "<i>None</i>"
    return "<br/>".join(f"• {s}" for s in skills)


def _score_color(score: int) -> colors.HexColor:
    """Return a colour that reflects the quality of the match score."""
    if score >= 75:
        return _GREEN
    if score >= 50:
        return _ORANGE
    return _RED


# ---------------------------------------------------------------------------
# Section builders
# ---------------------------------------------------------------------------

def _build_title_section(styles: dict) -> list:
    """Return flowables for the report title and horizontal rule."""
    return [
        Paragraph("AI Resume Analysis Report", styles["title"]),
        HRFlowable(
            width="100%",
            thickness=2,
            color=_HEADER_BG,
            spaceAfter=12,
            spaceBefore=2,
        ),
    ]


def _build_score_section(result: dict, styles: dict) -> list:
    """Return flowables for the match-score display."""
    score = result.get("match_score", 0)
    colour = _score_color(score)

    score_style = ParagraphStyle(
        "DynamicScore",
        parent=styles["score"],
        textColor=colour,
    )

    return [
        Paragraph("Match Score", styles["heading"]),
        Paragraph(f"{score}%", score_style),
        Paragraph("Overall resume-to-job match percentage", styles["score_label"]),
    ]


def _build_skill_table(result: dict, styles: dict) -> list:
    """Return flowables for the three-column skill-analysis table."""
    skill_analysis = result.get("skill_analysis", {})
    matched = skill_analysis.get("matched_skills", [])
    missing = skill_analysis.get("missing_skills", [])
    bonus = skill_analysis.get("bonus_skills", [])

    # Header row
    header_green = ParagraphStyle("HdrGreen", parent=styles["table_header"])
    header_red = ParagraphStyle("HdrRed", parent=styles["table_header"])
    header_orange = ParagraphStyle("HdrOrange", parent=styles["table_header"])

    headers = [
        Paragraph("Matched Skills", header_green),
        Paragraph("Missing Skills", header_red),
        Paragraph("Bonus Skills", header_orange),
    ]

    body = [
        Paragraph(_skill_bullets(matched), styles["table_cell"]),
        Paragraph(_skill_bullets(missing), styles["table_cell"]),
        Paragraph(_skill_bullets(bonus), styles["table_cell"]),
    ]

    col_width = 2.1 * inch
    table = Table([headers, body], colWidths=[col_width] * 3)

    table.setStyle(
        TableStyle(
            [
                # Header row backgrounds
                ("BACKGROUND", (0, 0), (0, 0), _GREEN),
                ("BACKGROUND", (1, 0), (1, 0), _RED),
                ("BACKGROUND", (2, 0), (2, 0), _ORANGE),
                # Body row tints
                ("BACKGROUND", (0, 1), (0, 1), _LIGHT_GREEN),
                ("BACKGROUND", (1, 1), (1, 1), _LIGHT_RED),
                ("BACKGROUND", (2, 1), (2, 1), _LIGHT_ORANGE),
                # Grid & padding
                ("GRID", (0, 0), (-1, -1), 0.5, colors.white),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )

    return [
        Paragraph("Skill Analysis", styles["heading"]),
        table,
    ]


def _build_improvements_section(result: dict, styles: dict) -> list:
    """Return flowables for the numbered improvements list."""
    improvements = result.get("improvements", [])

    elements: list = [Paragraph("Top 3 Improvements", styles["heading"])]

    if not improvements:
        elements.append(Paragraph("<i>No improvements listed.</i>", styles["body"]))
        return elements

    for idx, item in enumerate(improvements, start=1):
        elements.append(
            Paragraph(f"<b>{idx}.</b>  {item}", styles["body"])
        )
        elements.append(Spacer(1, 4))

    return elements


def _build_rewrites_section(result: dict, styles: dict) -> list:
    """Return flowables for the bullet-point rewrites."""
    rewrites = result.get("bullet_rewrites", [])

    elements: list = [Paragraph("Bullet-Point Rewrites", styles["heading"])]

    if not rewrites:
        elements.append(Paragraph("<i>No rewrites available.</i>", styles["body"]))
        return elements

    for idx, entry in enumerate(rewrites, start=1):
        original = entry.get("original", "")
        rewritten = entry.get("rewritten", "")
        critique = entry.get("critique", "")

        elements.append(
            Paragraph(f"<b>Rewrite #{idx}</b>", styles["body_bold"])
        )
        elements.append(Spacer(1, 2))
        elements.append(
            Paragraph(f"<i>Original:</i>  <i>{original}</i>", styles["body_italic"])
        )
        elements.append(Spacer(1, 2))
        elements.append(
            Paragraph(f"<b>Rewritten:</b>  <b>{rewritten}</b>", styles["body_bold"])
        )
        elements.append(Spacer(1, 2))
        elements.append(
            Paragraph(f"Critique: {critique}", styles["body"])
        )
        elements.append(
            HRFlowable(
                width="80%",
                thickness=0.5,
                color=colors.lightgrey,
                spaceBefore=6,
                spaceAfter=6,
            )
        )

    return elements


def _build_interview_section(result: dict, styles: dict) -> list:
    """Return flowables for the interview prep questions."""
    questions = result.get("interview_questions", [])

    elements: list = [Paragraph("Interview Prep Questions", styles["heading"])]

    if not questions:
        elements.append(Paragraph("<i>No questions generated.</i>", styles["body"]))
        return elements

    for idx, entry in enumerate(questions, start=1):
        question = entry.get("question", "")
        context = entry.get("context", "")
        q_type = entry.get("type", "General")

        # Type badge colour
        badge_colour = "#1565c0"
        if q_type == "Technical":
            badge_colour = "#2e7d32"
        elif q_type == "Behavioral":
            badge_colour = "#ef6c00"

        elements.append(
            Paragraph(
                f'<b>{idx}.</b>  <b>{question}</b>'
                f'  <font color="{badge_colour}" size="8">[{q_type}]</font>',
                styles["body"],
            )
        )
        if context:
            elements.append(
                Paragraph(
                    f"<i>Tip: {context}</i>",
                    styles["body_italic"],
                )
            )
        elements.append(Spacer(1, 6))

    return elements


def _build_footer(styles: dict) -> list:
    """Return flowables for the report footer with a timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return [
        Spacer(1, 20),
        HRFlowable(
            width="100%",
            thickness=1,
            color=colors.lightgrey,
            spaceBefore=8,
            spaceAfter=6,
        ),
        Paragraph(
            f"Generated by AI Resume Analyzer  •  {timestamp}",
            styles["footer"],
        ),
    ]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_pdf_report(result: dict) -> bytes:
    """Generate a professional PDF report from the analysis result dict.

    Args:
        result: Dictionary with these keys:
            - match_score (int): 1-100 match percentage
            - improvements (list[str]): 3 actionable improvement suggestions
            - skill_analysis (dict): with keys:
                - matched_skills (list[str])
                - missing_skills (list[str])
                - bonus_skills (list[str])
            - bullet_rewrites (list[dict]): each has 'original', 'rewritten',
              'critique'
            - interview_questions (list[dict]): each has 'question', 'context',
              'type' (Technical/Behavioral)

    Returns:
        bytes: The PDF file content as bytes.
    """
    buf = io.BytesIO()

    doc = SimpleDocTemplate(
        buf,
        pagesize=letter,
        topMargin=0.6 * inch,
        bottomMargin=0.5 * inch,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
        title="AI Resume Analysis Report",
        author="AI Resume Analyzer",
    )

    styles = _build_styles()

    # Assemble all flowable elements in order
    elements: list = []
    elements.extend(_build_title_section(styles))
    elements.extend(_build_score_section(result, styles))
    elements.extend(_build_skill_table(result, styles))
    elements.extend(_build_improvements_section(result, styles))
    elements.extend(_build_rewrites_section(result, styles))
    elements.extend(_build_interview_section(result, styles))
    elements.extend(_build_footer(styles))

    doc.build(elements)
    return buf.getvalue()
