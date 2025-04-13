import os
import re
import json
from datetime import date
from fpdf import FPDF
from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate

# Prompt templates
motivation_prompt = PromptTemplate(
    input_variables=[
        "job_title",
        "company",
        "job_description",
        "candidate_profile",
        "candidate_name",
        "recipient_name"
    ],
    template="""
You are a highly skilled career writer and application coach.

Write a personalized and professional motivation letter for a job application, using:
- The candidate's profile (résumé-based)
- The job title and company
- The tone and **language used in the job description** (French, English, etc.)

🎯 Goal: Convince the company the candidate is a strong fit by clearly highlighting their relevant experience, skills, and motivation — with fluency, structure, and a natural tone.

---
📌 Job Title: {job_title}  
🏢 Company: {company}  
📃 Job Description:  
{job_description}

🧑‍💼 Candidate Profile:  
{candidate_profile}
---

✍️ Write a complete motivation letter that:
- Matches the **same language and tone** as the job description
- Begins with **Dear {recipient_name}** (or “Dear Hiring Manager” if name is unknown)
- Presents a strong, polite introduction
- Highlights the candidate's most relevant strengths for the job
- Demonstrates alignment with the company’s values or goals
- Ends with a confident, respectful closing and the candidate’s full name: **{candidate_name}**

❌ Do NOT include any instructions, explanations, or extra formatting.
✅ Return only the clean, final letter content.
"""
)

refine_prompt = PromptTemplate(
    input_variables=["letter", "candidate_name"],
    template="""
You are an expert career writer and editor.

Your task is to enhance the following motivation letter:
- Improve the clarity, tone, flow, and vocabulary
- Make it more persuasive and professional
- Keep the original structure, intent, and meaning
- Maintain a natural and realistic tone — not robotic
- Do NOT remove or alter the opening line (e.g., "Dear [Name]")
- Always end the letter with the exact name: {candidate_name}

Return ONLY the improved letter — no extra commentary or formatting.

---
{letter}
"""
)

# Clean filename utility
def clean_filename(text):
    return re.sub(r'[\\/*?:"<>|]', "", text).replace(" ", "_")

# Save as PDF
def save_letter_as_pdf(letter_text, file_name):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)
    for line in letter_text.split("\n"):
        safe_line = line.encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(0, 10, safe_line)
    pdf.output(file_name)

# Main letter generation function
def generate_letters_for_jobs(top_jobs, candidate_profile, save_pdfs=True):
    os.makedirs("motivation letter", exist_ok=True)

    # Load LLMs
    llm = OllamaLLM(model="phi4-mini")
    mistral = OllamaLLM(model="mistral")
    phi = OllamaLLM(model="deepseek-r1")
    llama3 = OllamaLLM(model="llama3.2")

    # Refinement pipeline
    step1 = refine_prompt | mistral
    step2 = refine_prompt | phi
    step3 = refine_prompt | llama3

    # Extract candidate name from profile
    try:
        parsed_profile = json.loads(candidate_profile)
        candidate_name = parsed_profile.get("full_name", "Your Name")
    except Exception:
        candidate_name = "Your Name"

    letters = []

    for job in top_jobs:
        # Fallback for recipient name
        recipient_name = job.get("Contact", "Hiring Manager")

        # Chain to generate base letter
        chain = motivation_prompt | llm
        response = chain.invoke({
            "job_title": job["Title"],
            "company": job["Company"],
            "job_description": job["Description"],
            "candidate_profile": candidate_profile,
            "candidate_name": candidate_name,
            "recipient_name": recipient_name
        })

        # Refinement steps
        letter_step1 = step1.invoke({"letter": response, "candidate_name": candidate_name})
        letter_step2 = step2.invoke({"letter": letter_step1, "candidate_name": candidate_name})
        final_letter = step3.invoke({"letter": letter_step2, "candidate_name": candidate_name})

        # Save to PDF if needed
        if save_pdfs:
            title_clean = clean_filename(job["Title"])
            company_clean = clean_filename(job["Company"])
            file_name = f"./motivation letter/letter_{title_clean}_{company_clean}_{date.today()}.pdf"
            save_letter_as_pdf(final_letter, file_name)

        letters.append((job["Title"], job["Company"], final_letter))

    return letters
