# 📄 AI-Powered Resume Analyzer & ATS Feedback System

An intelligent, ATS-style resume analysis and feedback application powered by **Google Gemini 3.8 Flash** and **Streamlit**. It evaluates candidate resumes against specific job descriptions, computes an objective match score (1–100), and provides actionable, recruiter-grade recommendations to optimize job applications.

---

## 🚀 Key Features

- **Multi-Format Document Parsing:** Automatically extracts and sanitizes text from `.pdf`, `.docx`, and `.txt` files.
- **AI-Powered Evaluation:** Leverages Google's **Gemini 3.8 Flash** model with strict JSON schema constraints for consistent, deterministic outputs.
- **Recruiter Match Score:** Generates an ATS match percentage (1–100) indicating alignment with target qualifications.
- **Actionable Optimization Feedback:** Pinpoints the top 3 high-impact resume improvements tailored to the target job description.
- **Interactive UI:** Clean, responsive web dashboard built with Streamlit featuring real-time visual progress bars and metrics.
- **Zero-Data Leakage Security:** Environment-variable-based secret management with `.env` shielding.

---

## 🛠️ Tech Stack

- **Language:** Python 3.10+
- **LLM / AI:** Google Gemini API (`gemini-3.8-flash` via `google-generativeai`)
- **Web Framework:** [Streamlit](https://streamlit.io/)
- **Document Processing:** [PyPDF2](https://pypdf2.readthedocs.io/), [python-docx](https://python-docx.readthedocs.io/)
- **Configuration & Secrets:** [python-dotenv](https://github.com/theskumar/python-dotenv)

---

## 📁 Project Structure

```text
├── app.py              # Main Streamlit application & Gemini integration pipeline
├── requirements.txt    # Project dependencies
├── .env.example        # Template for environment configuration
├── .gitignore          # Shields secrets (.env) and virtual environments (.venv)
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
2. Create a `.env` file in the root directory (or copy `.env.example`):
   ```bash
   cp .env.example .env
   ```
3. Add your Gemini API key:
   ```env
   GEMINI_API_KEY="your_actual_api_key_here"
   ```

### 5. Launch the Application
```bash
streamlit run app.py
```
Open your browser and navigate to `http://localhost:8501`.

---

## 💡 How It Works

1. **Upload Resume:** Provide your resume in PDF, DOCX, or plain text format.
2. **Input Target Role:** Paste the job description you are targeting.
3. **Analyze:** Click **"Analyze Match"** — the pipeline parses your text, injects it into a structured prompt, and queries Gemini.
4. **Actionable Insights:** Review your ATS match score and implement the recommended revisions.

---

## 🛡️ License

Distributed under the MIT License. See `LICENSE` for more information.

