# 📄 AI-Powered Resume Analyzer & ATS Intelligence Platform

An intelligent, ATS-style resume analysis and feedback platform powered by **Google Gemini 3.8 Flash** and **Streamlit**. It evaluates candidate resumes against specific job descriptions, providing a comprehensive analysis suite including match scoring, skill-gap identification, bullet-point rewriting, interview preparation, and downloadable PDF reports.

---

## 🚀 Key Features

### 🎯 Skill Gap Analysis Dashboard
Automatically extracts and categorizes technical skills into three visual groups:
- **✅ Matched Skills** — Present in both resume and job description
- **❌ Missing Critical Skills** — Required by JD but absent from resume
- **🌟 Bonus Skills** — Valuable extras found in resume

### ✍️ Bullet-Point Rewriter (Google XYZ Formula)
Identifies weak bullet points and rewrites them using the impact formula used at Google, Amazon, and Meta:
> *"Accomplished [X] as measured by [Y], by doing [Z]"*

Displays side-by-side **Before → After** comparisons with inline critiques.

### 🎤 Tailored Interview Question Generator
Generates 5 role-specific interview questions (3 Technical + 2 Behavioral) based on the candidate's **specific skill gaps**, not generic questions. Each includes a coaching tip explaining what the interviewer is testing for.

### 📥 Downloadable PDF Scorecard Report
One-click download of a professionally formatted PDF containing all analysis results — match score, skill breakdown, improvements, rewritten bullets, and interview prep.

### 📊 Core ATS Match Scoring
- **Match Score (1–100)** with color-coded visual feedback (green/yellow/red)
- **Top 3 Actionable Improvements** tailored to the specific job description
- **Multi-format support:** PDF, DOCX, and plain text resumes

---

## 🛠️ Tech Stack

| Component | Technology |
|:---|:---|
| **Language** | Python 3.10+ |
| **LLM / AI** | Google Gemini API (`gemini-3.8-flash` via `google-generativeai`) |
| **Web Framework** | [Streamlit](https://streamlit.io/) |
| **Document Parsing** | [PyPDF2](https://pypdf2.readthedocs.io/), [python-docx](https://python-docx.readthedocs.io/) |
| **PDF Generation** | [ReportLab](https://www.reportlab.com/) |
| **Configuration** | [python-dotenv](https://github.com/theskumar/python-dotenv) |

---

## 📁 Project Structure

```text
├── app.py              # Main Streamlit application & Gemini integration
├── pdf_report.py       # PDF scorecard report generator (ReportLab)
├── requirements.txt    # Project dependencies
├── .env.example        # Template for environment configuration
├── .gitignore          # Shields secrets and virtual environments
└── README.md           # Documentation
```

---

## ⚙️ Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/Ayuhsman246/resume-parser-and-feedback.git
cd resume-parser-and-feedback
```

### 2. Set Up Virtual Environment
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Your API Key
1. Get a free API key from [Google AI Studio](https://aistudio.google.com/apikey).
2. Create a `.env` file (or copy the template):
   ```bash
   cp .env.example .env
   ```
3. Add your key:
   ```env
   GEMINI_API_KEY="your_actual_api_key_here"
   ```

### 5. Launch the Application
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 💡 How It Works

1. **Upload Resume** — Provide your resume in PDF, DOCX, or TXT format.
2. **Paste Job Description** — Enter the target job posting.
3. **Analyze** — Click **"🚀 Analyze Match"** to run the full analysis pipeline.
4. **Review Results** — Explore your match score, skill gaps, rewritten bullets, and interview prep.
5. **Download** — Export the full analysis as a PDF report or raw JSON.

---

## 📸 Analysis Output Includes

| Section | Description |
|:---|:---|
| **Match Score** | Color-coded 1-100 score with progress bar |
| **Skill Gap Dashboard** | Matched / Missing / Bonus skills with colored pill badges |
| **Top 3 Improvements** | Specific, actionable resume optimization suggestions |
| **Bullet Rewrites** | Before/After comparison using Google XYZ impact formula |
| **Interview Prep** | 5 tailored questions with type badges and coaching tips |
| **PDF Download** | Professional scorecard report with all findings |
| **JSON Export** | Raw analysis data for programmatic use |

---

## 🛡️ License

Distributed under the MIT License. See `LICENSE` for more information.
