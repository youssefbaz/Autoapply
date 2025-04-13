# 🧠 AutoApply - AI-Powered Job Application Assistant

AutoApply is an intelligent job application assistant that helps users streamline their job hunt by automating the key steps:
- Extracts relevant information from a resume (PDF)
- Scrapes job listings from platforms like APEC and Indeed
- Generates tailored motivation letters using LLMs
- Presents results through a simple Streamlit web app

---

## 🚀 Features

- 🔍 **Resume Parsing:** Uses an LLM to extract name, skills, experience, etc.
- 🧠 **Job Recommendation:** Scrapes jobs related to your profile.
- 📝 **Motivation Letter Generator:** Creates personalized cover letters using LLMs.
- 🖥️ **Web Interface:** Intuitive app built with Streamlit.
- 🌐 **Multi-source Scraping:** APEC and Indeed support via Selenium.

---

## 📂 Project Structure

```
Autoapply/
│
├── app.py                        # Streamlit app UI
├── apec_scraper.py              # APEC job scraper
├── indeed_scraper.py            # Indeed job scraper
├── parse_resume_llm.py          # Resume parsing logic using LLM
├── motivation_letter_llm.py     # Motivation letter generator using LLM
├── chromedriver.exe             # Selenium driver (Windows)
├── .gitignore
└── Animation-*.json             # Lottie animations for UI
```

---

## 🛠️ Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/Autoapply.git
cd Autoapply
```

2. Create a virtual environment and activate it:

```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

3. Install the dependencies:

```bash
pip install -r requirements.txt
```

4. Run the app:

```bash
streamlit run app.py
```

---

## 🔐 Configuration

You may need API keys or access tokens for:
- OpenAI (for LLM calls)
- Any custom LangChain/LLM setup (adjust in `parse_resume_llm.py` or `motivation_letter_llm.py`)

Store them in environment variables or use `.env` files (not included here).

---

## 📸 Demo

![demo video or animation here "https://youssef.bazzaoui.com/genai_project.html"]

---


## 🙌 Acknowledgments

- [Streamlit](https://streamlit.io/)
- [LangChain](https://www.langchain.com/)
- [OpenAI](https://openai.com/)
- [Undetected Chromedriver](https://github.com/ultrafunkamsterdam/undetected-chromedriver)
