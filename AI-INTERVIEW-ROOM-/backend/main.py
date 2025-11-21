from fastapi import FastAPI, UploadFile, File
from sqlalchemy import text
from database import engine  
import fitz  # PyMuPDF
import re


app = FastAPI()

@app.get("/")
def home():
    return {"status": "AI Interview Backend Running Successfully"}

@app.get("/db-check")
def check_db():
    # simple test query
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    return {"status": "✅ Connected to Supabase successfully"}


# ✅ Function to read text from PDF
def extract_text_from_pdf(file_bytes):
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    text_data = ""
    for i in range(min(len(doc), 5)):   # only first 5 pages
        text_data += doc[i].get_text()
    return text_data


# ✅ Get email from text
def extract_email(text):
    match = re.search(r"[a-zA-Z0-9\.\-_]+@[a-zA-Z\.\-]+", text)
    return match.group(0) if match else "Not found"


# ✅ Get phone number from text
def extract_phone(text):
    match = re.search(r"\+?\d[\d\s\-]{8,}", text)
    return match.group(0) if match else "Not found"

def extract_skills(text):
    match = re.search(r"(Skills|TECHNICAL SKILLS)([\s\S]+?)(Education|Experience)", text, re.I)
    return match.group(2).strip() if match else "Not found"

def extract_education(text):
    match = re.search(r"(Education)([\s\S]+?)(Experience|Projects)", text, re.I)
    return match.group(2).strip() if match else "Not found"

def extract_experience(text):
    match = re.search(r"(Experience)([\s\S]+)", text, re.I)
    return match.group(2).strip() if match else "Not found"


@app.post("/upload_resume")
async def upload_resume(file: UploadFile = File(...)):
    try:
        print("✅ File received:", file.filename)

        content = await file.read()
        print("✅ File size:", len(content))

        resume_text = extract_text_from_pdf(content)
        print("✅ Resume text extracted")

        name = resume_text.split("\n")[0] if resume_text else "Not found"
        email = extract_email(resume_text)
        phone = extract_phone(resume_text)
        skills = extract_skills(resume_text)
        education = extract_education(resume_text)
        experience = extract_experience(resume_text)

        print("✅ Extracted:", name, email, phone)

        with engine.connect() as conn:
            conn.execute(
    text("""
        INSERT INTO candidates 
        (name, email, phone, skills, education, experience, resume_text)
        VALUES 
        (:name, :email, :phone, :skills, :education, :experience, :resume_text)
    """),
    {
        "name": name,
        "email": email,
        "phone": phone,
        "skills": skills,
        "education": education,
        "experience": experience,
        "resume_text": resume_text
    }
)
            conn.commit()

        print("✅ Data inserted into database")

        return {
            "message": "✅ Resume uploaded and saved to database",
            "name": name,
            "email": email,
            "phone": phone
        }

    except Exception as e:
        print("❌ ERROR:", str(e))
        return {"error": str(e)}
