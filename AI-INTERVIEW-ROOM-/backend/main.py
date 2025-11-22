from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from database import candidates
import fitz
import re

app = FastAPI()

# ✅ CORS FIX
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"status": "✅ AI Interview Backend Running"}


# ====================== UPLOAD RESUME ======================
@app.post("/upload_resume")
async def upload_resume(
    name: str = Form(...),
    domain: str = Form(...),
    position: str = Form(...),
    file: UploadFile = File(...)
):
    content = await file.read()
    text = extract_text_from_pdf(content)

    email = extract_email(text)
    phone = extract_phone(text)
    skills = extract_skills(text)
    education = extract_education(text)
    experience = extract_experience(text)

    data = {
        "name": name,
        "domain": domain,
        "position": position,
        "email": email,
        "phone": phone,
        "skills": skills,
        "education": education,
        "experience": experience,
        "resume_text": text
    }

    candidates.insert_one(data)

    return {
        "success": True,
        "message": "✅ Resume + Details saved"
    }


# ====================== GET QUESTIONS ======================
@app.get("/get_questions")
def get_questions():
    user = candidates.find_one(sort=[('_id', -1)])

    if not user:
        return {"error": "No candidate found"}

    questions = [
        f"Tell me about yourself {user['name']}",
        f"What is your experience in {user['domain']}?",
        f"Explain your key skills: {user['skills']}",
        f"Why should we hire you for {user['position']}?",
        f"Describe one project you've worked on"
    ]

    return {"questions": questions}


# ====================== HELPERS ======================

def extract_text_from_pdf(file_bytes):
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text


def extract_email(text):
    match = re.search(r"[a-zA-Z0-9\.\-_]+@[a-zA-Z\.\-]+", text)
    return match.group(0) if match else "Not found"


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
