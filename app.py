"""AI-Powered Resume Analyzer & ATS Intelligence Platform.

Main entry point — wires together the document parser, AI analyzer,
UI components, and PDF report generator.

Run with:
    streamlit run app.py
"""

import os

import streamlit as st
from dotenv import load_dotenv

from ai_analyzer import analyze_resume
from document_parser import SUPPORTED_TYPES, extract_text
from ui_components import render_results

# Load environment variables (e.g. GEMINI_API_KEY) from a local .env file.
load_dotenv()


def _get_api_key():
    """Read the API key from the environment, or ask the user for it."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        st.info("No `GEMINI_API_KEY` found in `.env`. Enter one to continue.")
        api_key = st.text_input("Gemini API key", type="password")
        if not api_key:
            st.stop()
    return api_key


def main():
    """Configure the page and run the analysis workflow."""
    st.set_page_config(
        page_title="AI Resume Analyzer",
        page_icon="📄",
        layout="wide",
    )
    st.title("📄 AI-Powered Resume Analyzer & ATS Intelligence Platform")
    st.markdown(
        "Upload your resume and paste a job description. The AI acts as a "
        "**strict technical recruiter** — scoring your match, identifying "
        "skill gaps, rewriting weak bullet points, and generating tailored "
        "interview prep questions."
    )

    api_key = _get_api_key()

    # ── Input section (two columns) ──
    col_input1, col_input2 = st.columns(2)

    with col_input1:
        st.subheader("1. Upload your resume")
        uploaded_file = st.file_uploader(
            "Supported formats: PDF, DOCX, TXT", type=SUPPORTED_TYPES
        )

    with col_input2:
        st.subheader("2. Paste the job description")
        job_description = st.text_area(
            "Job description",
            height=200,
            placeholder="Paste the full posting here...",
        )

    # ── Analyze button ──
    if st.button("🚀 Analyze Match", type="primary", use_container_width=True):
        if not uploaded_file:
            st.error("Please upload a resume first.")
            return
        if not job_description.strip():
            st.error("Please paste a job description.")
            return

        with st.spinner(
            "🔍 Analyzing your resume — extracting skills, rewriting bullets, "
            "generating interview questions... This may take 15-30 seconds."
        ):
            try:
                resume_text = extract_text(uploaded_file)
                result = analyze_resume(resume_text, job_description, api_key)
            except ValueError as exc:
                st.error(f"**Document error:** {exc}")
                return
            except RuntimeError as exc:
                st.error(f"**Analysis error:** {exc}")
                return

        render_results(result)


if __name__ == "__main__":
    main()
