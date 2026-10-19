"""AI-Powered Resume Analyzer.

A Streamlit app that scores a resume against a job description using the
Google Gemini API and returns three actionable improvements.

Run with:
    streamlit run app.py
"""

import io
import json
import os

import docx  # provided by the python-docx package
import google.generativeai as genai
import PyPDF2
import streamlit as st
from dotenv import load_dotenv

# Load environment variables (e.g. GEMINI_API_KEY) from a local .env file.
load_dotenv()

MODEL_NAME = "gemini-3.8-flash"
SUPPORTED_TYPES = ["pdf", "docx", "txt"]


# --------------------------------------------------------------------------
# Document processing
# --------------------------------------------------------------------------
def _extract_pdf(file_bytes):
    """Extract text from PDF bytes using PyPDF2."""
    reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages)


def _extract_docx(file_bytes):
    """Extract text from DOCX bytes using python-docx (paragraphs + tables)."""
    document = docx.Document(io.BytesIO(file_bytes))
    lines = [para.text for para in document.paragraphs]

    # Resumes often use tables for layout, so include their cell text too.
    for table in document.tables:
        for row in table.rows:
            for cell in row.cells:
                if cell.text.strip():
                    lines.append(cell.text)
    return "\n".join(lines)


def _extract_txt(file_bytes):
    """Decode plain-text bytes, falling back to latin-1 if UTF-8 fails."""
    try:
        return file_bytes.decode("utf-8")
    except UnicodeDecodeError:
        return file_bytes.decode("latin-1")


def extract_text(uploaded_file):
    """Detect the file type from its extension and extract its text.

    Args:
        uploaded_file: Streamlit UploadedFile object (PDF, DOCX or TXT).

    Returns:
        str: The extracted text.

    Raises:
        ValueError: If the type is unsupported or no text could be extracted.
    """
    extension = os.path.splitext(uploaded_file.name)[1].lower()
    file_bytes = uploaded_file.getvalue()

    extractors = {
        ".pdf": _extract_pdf,
        ".docx": _extract_docx,
        ".txt": _extract_txt,
    }
    if extension not in extractors:
        raise ValueError(f"Unsupported file type: '{extension}'.")

    try:
        text = extractors[extension](file_bytes)
    except Exception as exc:  # corrupt or encrypted files, etc.
        raise ValueError(f"Could not read the {extension} file: {exc}") from exc

    if not text.strip():
        raise ValueError(
            "No text could be extracted. The file may be empty or a scanned image."
        )
    return text


# --------------------------------------------------------------------------
# AI integration
# --------------------------------------------------------------------------
def build_prompt(resume_text, job_description):
    """Build the prompt that injects the resume and job description."""
    return f"""You are a strict, expert technical recruiter. Evaluate the
candidate's resume against the job description below.

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

Respond with ONLY a raw JSON object. Do not use markdown formatting, code
fences, or any conversational text. The object must contain exactly these
two keys:
  "match_score": an integer from 1 to 100 showing how well the resume
                 matches the job description.
  "improvements": a list of exactly 3 strings, each a specific, actionable
                  suggestion for improving the resume for this specific job.
"""


def _strip_code_fences(text):
    """Remove stray markdown fences and surrounding prose around a JSON object."""
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:]
    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end != -1 and end > start:
        text = text[start : end + 1]
    return text.strip()


def _validate_result(result):
    """Check the parsed JSON matches the spec and normalise its values."""
    if not isinstance(result, dict):
        raise ValueError("The model response was not a JSON object.")
    if "match_score" not in result or "improvements" not in result:
        raise ValueError("The model response is missing required keys.")

    score = int(result["match_score"])
    score = max(1, min(100, score))

    improvements = result["improvements"]
    if not isinstance(improvements, list) or not improvements:
        raise ValueError("'improvements' must be a non-empty list.")

    return {
        "match_score": score,
        "improvements": [str(item) for item in improvements[:3]],
    }


def analyze_resume(resume_text, job_description, api_key):
    """Send the resume and job description to Gemini and parse the reply.

    Returns:
        dict: {"match_score": int, "improvements": list[str]}

    Raises:
        RuntimeError: On API failures or an unparseable response.
    """
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            MODEL_NAME,
            generation_config={
                "temperature": 0.2,
                "response_mime_type": "application/json",
            },
        )
        response = model.generate_content(
            build_prompt(resume_text, job_description)
        )
        raw_text = response.text
    except Exception as exc:  # network, quota, invalid key, blocked content
        raise RuntimeError(f"Gemini API call failed: {exc}") from exc

    try:
        parsed = json.loads(_strip_code_fences(raw_text))
        return _validate_result(parsed)
    except (json.JSONDecodeError, ValueError, TypeError) as exc:
        raise RuntimeError(f"Could not parse the model's response: {exc}") from exc


# --------------------------------------------------------------------------
# User interface
# --------------------------------------------------------------------------
def get_api_key():
    """Read the API key from the environment, or ask the user for it."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        st.info("No `GEMINI_API_KEY` found in `.env`. Enter one to continue.")
        api_key = st.text_input("Gemini API key", type="password")
        if not api_key:
            st.stop()
    return api_key


def render_results(result):
    """Render the score as a metric and the feedback as markdown."""
    st.success("Analysis complete!")
    st.metric(label="Match Score", value=f"{result['match_score']}/100")
    st.progress(result["match_score"] / 100)

    st.subheader("Top 3 Improvements")
    for index, tip in enumerate(result["improvements"], start=1):
        st.markdown(f"**{index}.** {tip}")


def main():
    """Configure the page and run the analysis workflow."""
    st.set_page_config(
        page_title="AI Resume Analyzer", page_icon="📄", layout="centered"
    )
    st.title("📄 AI-Powered Resume Analyzer")
    st.markdown(
        "Upload your resume and paste a job description. A strict AI "
        "recruiter will score the match and suggest three concrete "
        "improvements."
    )

    api_key = get_api_key()

    st.subheader("1. Upload your resume")
    uploaded_file = st.file_uploader(
        "Supported formats: PDF, DOCX, TXT", type=SUPPORTED_TYPES
    )

    st.subheader("2. Paste the job description")
    job_description = st.text_area(
        "Job description", height=300, placeholder="Paste the full posting here..."
    )

    if st.button("Analyze Match", type="primary"):
        if not uploaded_file:
            st.error("Please upload a resume first.")
            return
        if not job_description.strip():
            st.error("Please paste a job description.")
            return

        with st.spinner("Analyzing your resume..."):
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
