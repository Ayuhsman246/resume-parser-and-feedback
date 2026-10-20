"""AI analysis module — Gemini API integration.

Handles prompt construction, API communication with Google Gemini,
response parsing, and result validation.
"""

import json

import google.generativeai as genai

MODEL_NAME = "gemini-3.8-flash"


def _build_prompt(resume_text, job_description):
    """Build the comprehensive analysis prompt with structured JSON schema."""
    return f"""You are a strict, expert technical recruiter and career coach.
Perform a thorough evaluation of the candidate's resume against the job
description below.

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

Respond with ONLY a raw JSON object (no markdown, no code fences, no prose).
The JSON must contain exactly these keys:

1. "match_score": integer from 1 to 100 showing overall resume-JD alignment.

2. "skill_analysis": an object with exactly three keys:
   - "matched_skills": list of strings — technical skills, tools, and
     technologies present in BOTH the resume and job description.
   - "missing_skills": list of strings — skills explicitly required or
     strongly implied by the job description that are ABSENT from the resume.
   - "bonus_skills": list of strings — valuable skills found in the resume
     that are NOT mentioned in the job description but would be beneficial.
   Each list should contain 3-8 items. Be specific (e.g. "Docker" not
   "containerization tools").

3. "improvements": list of exactly 3 strings, each a specific, actionable
   suggestion for improving the resume for this specific job.

4. "bullet_rewrites": a list of exactly 3 objects, each containing:
   - "original": a weak or vague bullet point copied verbatim from the resume.
   - "rewritten": the same bullet rewritten using the Google XYZ impact
     formula: "Accomplished [X] as measured by [Y], by doing [Z]". Add
     realistic quantified metrics if the original lacks them.
   - "critique": one sentence explaining what was wrong with the original
     and what makes the rewrite stronger.
   Pick the 3 weakest bullet points from the resume. If the resume has
   fewer than 3 bullet points, rewrite whatever is available.

5. "interview_questions": a list of exactly 5 objects, each containing:
   - "question": a specific interview question tailored to this candidate's
     profile and the gaps identified.
   - "type": either "Technical" or "Behavioral".
   - "context": one sentence explaining what the interviewer is testing for
     and a brief tip on how to prepare.
   Generate 3 Technical and 2 Behavioral questions. Base them on the
   candidate's SPECIFIC skill gaps and resume weaknesses, not generic
   questions.
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

    # --- match_score ---
    if "match_score" not in result:
        raise ValueError("Missing 'match_score' in response.")
    score = int(result["match_score"])
    score = max(1, min(100, score))

    # --- improvements ---
    improvements = result.get("improvements", [])
    if not isinstance(improvements, list) or not improvements:
        raise ValueError("'improvements' must be a non-empty list.")

    # --- skill_analysis (with safe defaults) ---
    skill_analysis = result.get("skill_analysis", {})
    if not isinstance(skill_analysis, dict):
        skill_analysis = {}
    validated_skills = {
        "matched_skills": [str(s) for s in skill_analysis.get("matched_skills", [])],
        "missing_skills": [str(s) for s in skill_analysis.get("missing_skills", [])],
        "bonus_skills": [str(s) for s in skill_analysis.get("bonus_skills", [])],
    }

    # --- bullet_rewrites (with safe defaults) ---
    bullet_rewrites = result.get("bullet_rewrites", [])
    if not isinstance(bullet_rewrites, list):
        bullet_rewrites = []
    validated_rewrites = []
    for item in bullet_rewrites[:3]:
        if isinstance(item, dict):
            validated_rewrites.append({
                "original": str(item.get("original", "")),
                "rewritten": str(item.get("rewritten", "")),
                "critique": str(item.get("critique", "")),
            })

    # --- interview_questions (with safe defaults) ---
    interview_questions = result.get("interview_questions", [])
    if not isinstance(interview_questions, list):
        interview_questions = []
    validated_questions = []
    for item in interview_questions[:5]:
        if isinstance(item, dict):
            validated_questions.append({
                "question": str(item.get("question", "")),
                "type": str(item.get("type", "Technical")),
                "context": str(item.get("context", "")),
            })

    return {
        "match_score": score,
        "improvements": [str(item) for item in improvements[:3]],
        "skill_analysis": validated_skills,
        "bullet_rewrites": validated_rewrites,
        "interview_questions": validated_questions,
    }


def analyze_resume(resume_text, job_description, api_key):
    """Send the resume and job description to Gemini and parse the reply.

    Args:
        resume_text: Extracted text from the candidate's resume.
        job_description: The target job description text.
        api_key: Google Gemini API key.

    Returns:
        dict with keys: match_score, improvements, skill_analysis,
        bullet_rewrites, interview_questions.

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
            _build_prompt(resume_text, job_description)
        )
        raw_text = response.text
    except Exception as exc:  # network, quota, invalid key, blocked content
        raise RuntimeError(f"Gemini API call failed: {exc}") from exc

    try:
        parsed = json.loads(_strip_code_fences(raw_text))
        return _validate_result(parsed)
    except (json.JSONDecodeError, ValueError, TypeError) as exc:
        raise RuntimeError(f"Could not parse the model's response: {exc}") from exc

