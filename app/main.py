import re
from pathlib import Path

import fitz  # PyMuPDF
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .data import OPPORTUNITIES, RESOURCES, ROLES

LABELS = {"ci/cd": "CI/CD", "api testing": "API Testing", "rest api": "REST API", "aws": "AWS", "sql": "SQL", "nlp": "NLP", "html": "HTML", "css": "CSS", "node.js": "Node.js", "power bi": "Power BI"}
app = FastAPI(title="PathPilot", version="1.0")
STATIC = Path(__file__).parent / "static"


def has_skill(text: str, skill: str) -> bool:
    return re.search(r"(?<![a-z0-9])" + re.escape(skill.lower()) + r"(?![a-z0-9])", text.lower()) is not None


def check_role(role: str):
    if role not in ROLES:
        raise HTTPException(400, "Unknown role")


@app.get("/api/roles")
def roles():
    return list(ROLES.keys())


@app.get("/api/opportunities")
def opportunities(type: str = ""):
    return [o for o in OPPORTUNITIES if not type or o["type"] == type]


@app.post("/api/analyze")
async def analyze(role: str = Form(...), resume_text: str = Form(""), file: UploadFile = File(None)):
    check_role(role)
    text = resume_text
    if file and file.filename:
        data = await file.read()
        try:
            with fitz.open(stream=data, filetype="pdf") as doc:
                text = "\n".join(p.get_text() for p in doc)
        except Exception:
            raise HTTPException(400, "PDF read cheyyalekapoyam. Text paste cheyyandi.")
    if len(text.strip()) < 30:
        raise HTTPException(400, "Resume text ivvandi (PDF upload leda paste).")

    required = ROLES[role]
    found = [s for s in required if has_skill(text, s)]
    missing = [s for s in required if s not in found]
    score = round(100 * len(found) / len(required))

    tips = []
    if not re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", text):
        tips.append("Email address add cheyyandi.")
    if "linkedin" not in text.lower():
        tips.append("LinkedIn link add cheyyandi.")
    if "github" not in text.lower():
        tips.append("GitHub link add cheyyandi.")
    if not re.search(r"\d+\s?%|\d{2,}\+?", text):
        tips.append("Numbers/metrics add cheyyandi (e.g. 'reduced time by 40%').")
    if len(text.split()) > 900:
        tips.append("Resume 1 page lo undali. Chala longga undi.")
    if not tips:
        tips.append("Good structure. Projects lo impact numbers inka strong cheyyandi.")

    return {"role": role, "score": score, "found": found, "missing": missing,
            "tips": tips, "text": text[:4000]}


@app.post("/api/roadmap")
def roadmap(role: str = Form(...), missing: str = Form(""), weeks: int = Form(8)):
    check_role(role)
    weeks = max(2, min(weeks, 24))
    skills = [s.strip() for s in missing.split(",") if s.strip()] or ROLES[role][:4]
    per = max(1, weeks // len(skills))
    lines, w = [], 1
    for s in skills:
        end = min(weeks, w + per - 1)
        lines.append(f"Week {w}-{end}: {LABELS.get(s, s.title())}\n  - {RESOURCES.get(s, 'Official docs + one small project')}")
        w = end + 1
        if w > weeks:
            break
    lines.append(f"\nFinal week: Combine skills into one portfolio project for {role}, push to GitHub, update resume.")
    return {"roadmap": "\n".join(lines)}


@app.post("/api/interview")
def interview(role: str = Form(...), skills: str = Form("")):
    check_role(role)
    sk = [s.strip() for s in skills.split(",") if s.strip()] or ROLES[role][:5]
    qs = [f"Q{i+1}. Explain {s} and where you used it in a project." for i, s in enumerate(sk[:6])]
    qs += ["Tell me about yourself.", "Explain your best project and your exact contribution."]
    return {"questions": "\n".join(qs)}


@app.post("/api/savings")
def savings(missing_count: int = Form(0), resume_review: int = Form(500),
            counseling: int = Form(1000), paid_course: int = Form(2000)):
    """Estimated money saved. Rates are user-editable assumptions (INR)."""
    free_courses = max(0, missing_count)
    total = resume_review + counseling + free_courses * paid_course
    return {"resume_review": resume_review, "counseling": counseling,
            "courses": free_courses * paid_course, "free_courses": free_courses,
            "total": total, "currency": "INR",
            "note": "Estimate based on your own assumptions, not a guarantee."}


app.mount("/static", StaticFiles(directory=STATIC), name="static")


@app.get("/")
def index():
    return FileResponse(STATIC / "index.html")
