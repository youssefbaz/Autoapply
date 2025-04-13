import streamlit as st
import tempfile
import json
from parse_resume_llm import analyze_resume
from apec_scraper import scrape_apec_jobs
from motivation_letter_llm import generate_letters_for_jobs
from fpdf import FPDF
import io
import time
from streamlit_lottie import st_lottie
import requests


# --- PDF Generator ---
def generate_pdf_bytes(letter_text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)
    for line in letter_text.split("\n"):
        safe_line = line.encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(0, 10, safe_line)
    pdf_output = pdf.output(dest='S').encode('latin-1')
    return io.BytesIO(pdf_output)

# --- Resume Parsing ---
def handle_resume_upload(uploaded_file):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_path = tmp_file.name
    result = analyze_resume(tmp_path)
    st.session_state.resume_text = result["raw_profile"]
    st.session_state.keyword_text = result["job_keyword"]

# --- Resume Display ---
def display_resume():
    try:
        resume_data = json.loads(st.session_state.resume_text)
    except Exception:
        st.warning("⚠️ Couldn't parse resume data.")
        return

    st.markdown(f"**👤 Full Name:** {resume_data.get('full_name', 'N/A')}")
    st.markdown(f"**📩 Email:** {resume_data.get('email', 'N/A')}")
    st.markdown(f"**🎯 Job Title:** {resume_data.get('job_title')}")
    st.markdown("**💡 Top Skills:**")
    st.write(", ".join(resume_data.get("top_skills", [])))
    st.markdown("**📊 Experience:**")
    for exp in resume_data.get("experiences", []):
        st.markdown(f"- **{exp.get('job_title')}** at {exp.get('company')} ({exp.get('years', 'N/A')})")
    st.markdown("**🎓 Education:**")
    for edu in resume_data.get("education", []):
        st.markdown(f"- **{edu.get('degree')}**, {edu.get('university', '')}")

# --- Job Scraping ---
def scrape_jobs():
    with st.spinner("Scraping APEC..."):
        df = scrape_apec_jobs(keyword=st.session_state.final_keyword)
        st.session_state.df = df
        job_options = df.head(10).to_dict(orient="records")
        st.success("✅ Scraping done!")
        st.dataframe(df.head(10))
        st.session_state.job_loaded = job_options

# --- Job Selection ---
def select_jobs():
    job_options = st.session_state.job_loaded
    job_labels = [f"{job.get('Title', 'Untitled')} at {job.get('Company', 'Unknown Company')}" for job in job_options]
    selected_labels = st.multiselect("Jobs:", options=job_labels)
    selected_job_objects = [job for job, label in zip(job_options, job_labels) if label in selected_labels]
    st.session_state.selected_jobs = selected_job_objects

# --- Letter Generation ---
def generate_letters():
    loading_area = st.empty()
    lottie_animation = load_lottie_file("Animation - 1744378184737.json")  # adjust path if needed

    with loading_area.container():
        st.markdown("<h4 style='text-align: center;'>✨ Rédaction de lettres personnalisées rien que pour vous...</h4>", unsafe_allow_html=True)
        if lottie_animation:
            st_lottie(lottie_animation, speed=1, loop=True, quality="high", height=300)


    letters = generate_letters_for_jobs(
        st.session_state.selected_jobs,
        candidate_profile=st.session_state.resume_text,
        save_pdfs=False
    )

    st.session_state.generated_letters = {
        f"{title}_{company}": letter for title, company, letter in letters
    }

    loading_area.empty()


# --- Display & Edit Letters ---
def display_letters():
    for key, letter in st.session_state.generated_letters.items():
        title, company = key.split("_", 1)
        with st.container():
            with st.form(f"form_{key}"):
                st.subheader(f"📬 Letter for: {title} at {company}")
                edited_letter = st.text_area("Motivation Letter", value=letter, height=300, key=f"{key}_text_area")
                submitted = st.form_submit_button("📥 Generate PDF")
            if submitted:
                st.session_state.generated_letters[key] = edited_letter
                pdf_buffer = generate_pdf_bytes(edited_letter)
                filename = f"{title.replace(' ', '_')}_{company.replace(' ', '_')}.pdf"
                st.download_button("Download PDF", data=pdf_buffer, file_name=filename, mime="application/pdf")

def load_lottie_file(filepath: str):
    with open(filepath, "r") as f:
        return json.load(f)

# --- Main App ---
st.title("📄 Upload Resume")
uploaded_file = st.file_uploader("Choose your resume", type=["pdf", "txt", "docx"])
if uploaded_file:
    st.success("✅ File uploaded successfully.")

    animation_container = st.empty()
    with animation_container.container():
        st.markdown("<h4 style='text-align: center;'>🔍 Analyzing your resume...</h4>", unsafe_allow_html=True)
        lottie_animation2 = load_lottie_file("Animation - 1744379496284.json")
        if lottie_animation2:
            st_lottie(lottie_animation2, speed=1, height=300, loop=True)

    if "resume_text" not in st.session_state:
        handle_resume_upload(uploaded_file)

    animation_container.empty()  # Remove animation after resume is processed

    st.subheader("🧾 Resume Uploaded")
    display_resume()
    st.subheader("🔍 Job Search Setup")
    default_keyword = json.loads(st.session_state.resume_text).get("job_title") or st.session_state.get("keyword_text", "")
    st.text_input("Enter a the job title you want to search for :", value=default_keyword, key="final_keyword")
    option = st.selectbox("Select the job platform:", ("Apec", "Indeed"), index=0)
    if option == "Apec" and st.button("🚀 Scrape APEC Jobs"):
        scrape_jobs()
    if option =="Indeed":
        st.info("Indeed scraper is coming soon ")

if st.session_state.get("job_loaded"):
    st.subheader("📌 Select Jobs for Motivation Letters")
    select_jobs()

if st.session_state.get("selected_jobs") and "generated_letters" not in st.session_state:
    if st.button("✍️ Generate Motivation Letters"):
        generate_letters()

if "generated_letters" in st.session_state:
    display_letters()
elif "selected_jobs" in st.session_state and not st.session_state.selected_jobs:
    st.warning("⚠️ Please select at least one job before generating letters.")
