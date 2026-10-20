"""Streamlit UI rendering components.

All visual rendering logic — skill badges, bullet rewrites, interview
questions, download buttons, and result layouts.
"""

import json
from datetime import datetime

import streamlit as st

from pdf_report import generate_pdf_report


# --------------------------------------------------------------------------
# Skill analysis badges
# --------------------------------------------------------------------------
def _render_skill_pills(skills, color, bg_color):
    """Render a list of skills as colored HTML pill badges."""
    if not skills:
        return "<span style='color: #888; font-style: italic;'>None detected</span>"
    pills = []
    for skill in skills:
        pills.append(
            f'<span style="display:inline-block; background:{bg_color}; '
            f'color:{color}; padding:4px 12px; border-radius:16px; '
            f'margin:3px 4px; font-size:14px; font-weight:500;">{skill}</span>'
        )
    return " ".join(pills)


def render_skill_analysis(skill_analysis):
    """Render the skill gap analysis section with colored badge groups."""
    st.subheader("🎯 Skill Gap Analysis")

    col1, col2, col3 = st.columns(3)

    with col1:
        matched = skill_analysis.get("matched_skills", [])
        st.markdown(f"**✅ Matched Skills** ({len(matched)})")
        st.markdown(
            _render_skill_pills(matched, "#1a7a1a", "#d4edda"),
            unsafe_allow_html=True,
        )

    with col2:
        missing = skill_analysis.get("missing_skills", [])
        st.markdown(f"**❌ Missing Critical Skills** ({len(missing)})")
        st.markdown(
            _render_skill_pills(missing, "#a71d2a", "#f8d7da"),
            unsafe_allow_html=True,
        )

    with col3:
        bonus = skill_analysis.get("bonus_skills", [])
        st.markdown(f"**🌟 Bonus Skills** ({len(bonus)})")
        st.markdown(
            _render_skill_pills(bonus, "#856404", "#fff3cd"),
            unsafe_allow_html=True,
        )


# --------------------------------------------------------------------------
# Bullet point rewrites
# --------------------------------------------------------------------------
def render_bullet_rewrites(bullet_rewrites):
    """Render before/after bullet-point comparisons."""
    st.subheader("✍️ Bullet-Point Rewriter (Google XYZ Formula)")
    st.caption(
        "Weak bullet points rewritten using: "
        '"Accomplished **[X]** measured by **[Y]**, by doing **[Z]**"'
    )

    if not bullet_rewrites:
        st.info("No bullet rewrites were generated.")
        return

    for idx, item in enumerate(bullet_rewrites, start=1):
        with st.expander(f"Rewrite #{idx}", expanded=(idx == 1)):
            col_before, col_after = st.columns(2)
            with col_before:
                st.markdown("**🔴 Original**")
                st.markdown(
                    f'<div style="background:#fff0f0; padding:12px; '
                    f'border-radius:8px; border-left:4px solid #dc3545; '
                    f'font-style:italic; color:#000000;">{item["original"]}</div>',
                    unsafe_allow_html=True,
                )
            with col_after:
                st.markdown("**🟢 Rewritten**")
                st.markdown(
                    f'<div style="background:#f0fff0; padding:12px; '
                    f'border-radius:8px; border-left:4px solid #28a745; '
                    f'font-weight:500; color:#000000;">{item["rewritten"]}</div>',
                    unsafe_allow_html=True,
                )
            st.markdown(f"💡 **Critique:** {item['critique']}")


# --------------------------------------------------------------------------
# Interview questions
# --------------------------------------------------------------------------
def render_interview_questions(interview_questions):
    """Render tailored interview prep questions with tips."""
    st.subheader("🎤 Tailored Interview Prep")
    st.caption(
        "Questions generated based on YOUR specific skill gaps and resume weaknesses."
    )

    if not interview_questions:
        st.info("No interview questions were generated.")
        return

    for idx, item in enumerate(interview_questions, start=1):
        q_type = item.get("type", "Technical")
        type_emoji = "🔧" if q_type == "Technical" else "🧠"
        type_color = "#0d6efd" if q_type == "Technical" else "#6f42c1"

        st.markdown(
            f'**{idx}.** <span style="background:{type_color}; color:white; '
            f'padding:2px 8px; border-radius:10px; font-size:12px;">'
            f'{type_emoji} {q_type}</span> {item["question"]}',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div style="margin-left:24px; color:#666; font-size:13px; '
            f'margin-bottom:12px;">💡 <em>{item["context"]}</em></div>',
            unsafe_allow_html=True,
        )


# --------------------------------------------------------------------------
# Download section
# --------------------------------------------------------------------------
def render_download_section(result):
    """Render download buttons for PDF report and raw JSON export."""
    st.subheader("📥 Download Report")

    col1, col2 = st.columns(2)

    with col1:
        try:
            pdf_bytes = generate_pdf_report(result)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            st.download_button(
                label="📄 Download Full Report (PDF)",
                data=pdf_bytes,
                file_name=f"resume_analysis_{timestamp}.pdf",
                mime="application/pdf",
                type="primary",
            )
        except Exception as exc:
            st.warning(f"Could not generate PDF: {exc}")

    with col2:
        json_str = json.dumps(result, indent=2, ensure_ascii=False)
        st.download_button(
            label="📊 Export Analysis (JSON)",
            data=json_str,
            file_name=f"resume_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
        )


# --------------------------------------------------------------------------
# Main results renderer
# --------------------------------------------------------------------------
def render_results(result):
    """Render all analysis results in organized sections."""
    st.success("✅ Analysis Complete!")

    # ── Match Score ──
    score = result["match_score"]
    score_color = "#28a745" if score >= 70 else "#ffc107" if score >= 40 else "#dc3545"

    col_score, col_bar = st.columns([1, 2])
    with col_score:
        st.markdown(
            f'<div style="text-align:center; padding:20px;">'
            f'<div style="font-size:48px; font-weight:bold; color:{score_color};">'
            f'{score}/100</div>'
            f'<div style="font-size:14px; color:#666;">Match Score</div></div>',
            unsafe_allow_html=True,
        )
    with col_bar:
        st.progress(score / 100)
        if score >= 70:
            st.markdown("🟢 **Strong match!** Your resume aligns well with this role.")
        elif score >= 40:
            st.markdown("🟡 **Moderate match.** Some key areas need attention.")
        else:
            st.markdown("🔴 **Weak match.** Significant gaps detected — see below.")

    st.divider()

    # ── Skill Analysis ──
    render_skill_analysis(result.get("skill_analysis", {}))

    st.divider()

    # ── Top 3 Improvements ──
    st.subheader("📋 Top 3 Improvements")
    for index, tip in enumerate(result["improvements"], start=1):
        st.markdown(f"**{index}.** {tip}")

    st.divider()

    # ── Bullet Rewrites ──
    render_bullet_rewrites(result.get("bullet_rewrites", []))

    st.divider()

    # ── Interview Questions ──
    render_interview_questions(result.get("interview_questions", []))

    st.divider()

    # ── Downloads ──
    render_download_section(result)

