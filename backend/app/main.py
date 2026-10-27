import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.app.ml.parser import parser_engine
from backend.app.ml.taxonomy import taxonomy_engine
from backend.app.ml.matcher import matcher_engine
from backend.app.ml.classifier import career_classifier
from backend.app.ml.clusterer import job_clusterer
from backend.app.ml.simulator import what_if_simulator
from backend.app.ml.roadmap import roadmap_engine
from backend.app.ml.copilot import career_copilot
from backend.app.ml.job_fetcher import job_fetcher
from backend.app.db.mongodb import db_manager

app = FastAPI(
    title="Hack My Career API",
    description="Intelligent Semantic Resume-Job Matching, Career Recommendation, and Learning Analytics Engine",
    version="2.0.0"
)

# Enable CORS for local Vite development and deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = Path(__file__).parent / "data"

# Pydantic Request Models
class SignupRequest(BaseModel):
    name: str
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class ConnectDbRequest(BaseModel):
    mongodb_uri: str

class ParseTextRequest(BaseModel):
    text: str
    filename: Optional[str] = "Pasted_Resume.txt"

class CandidateProfileModel(BaseModel):
    name: str = "Candidate"
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    profiles: List[str] = []
    contact_display: Optional[str] = None
    education: Optional[str] = None
    experience_years: float = 1.0
    experience_display: Optional[str] = None
    skills: List[str] = []
    projects: List[str] = []
    raw_text: str = ""
    ats_score: Optional[int] = 80
    skill_count: Optional[int] = 0

class MatchRequest(BaseModel):
    candidate: CandidateProfileModel
    target_job_id: Optional[str] = None
    role_filter: Optional[str] = None
    top_k: int = 10

class WhatIfRequest(BaseModel):
    candidate: CandidateProfileModel
    target_job_id: str
    added_skills: List[str]

class RoadmapRequest(BaseModel):
    missing_skills: List[str]
    target_role: str = "Data Scientist"

class CopilotRequest(BaseModel):
    query: str
    context: Dict[str, Any]

class CustomJobMatchRequest(BaseModel):
    candidate: CandidateProfileModel
    target_role: str = "Data Scientist"
    job_title: Optional[str] = None
    company: Optional[str] = "Target Company"
    job_description: str

class SaveResumeRequest(BaseModel):
    user_id: str
    filename: str
    candidate: CandidateProfileModel
    target_role: Optional[str] = "Data Scientist"

class LiveJobSearchRequest(BaseModel):
    query: str = "Data Scientist"
    location: str = ""
    portal_filter: str = "all"
    candidate: Optional[CandidateProfileModel] = None
    max_results: int = 25

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Hack My Career",
        "canonical_skills_count": len(taxonomy_engine.get_all_canonical_skills()),
        "jobs_count": len(matcher_engine.jobs),
        "cluster_silhouette_score": job_clusterer.silhouette,
        "database": db_manager.get_db_status()
    }

# ----------------- AUTHENTICATION & MONGODB -----------------
@app.post("/api/auth/signup")
def signup(req: SignupRequest):
    try:
        user = db_manager.create_user(req.name, req.email, req.password)
        return {"status": "success", "user": user}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.post("/api/auth/login")
def login(req: LoginRequest):
    try:
        user = db_manager.authenticate_user(req.email, req.password)
        return {"status": "success", "user": user}
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Authentication error: {str(e)}")

@app.get("/api/db/status")
def get_db_status():
    return db_manager.get_db_status()

@app.post("/api/db/configure")
def configure_db(req: ConnectDbRequest):
    res = db_manager.connect_atlas(req.mongodb_uri)
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("error", "Failed to connect to MongoDB Atlas."))
    return res

# ----------------- USER RESUME HISTORY -----------------
@app.get("/api/user/resumes")
def get_user_resumes(user_id: str = Query(...)):
    resumes = db_manager.get_user_resumes(user_id)
    return {"resumes": resumes, "count": len(resumes)}

@app.post("/api/user/resumes")
def save_user_resume_endpoint(req: SaveResumeRequest):
    cand_dict = req.candidate.model_dump()
    saved = db_manager.save_user_resume(
        user_id=req.user_id,
        filename=req.filename,
        candidate_profile=cand_dict,
        target_role=req.target_role or "Data Scientist"
    )
    return {"status": "success", "resume": saved}

@app.get("/api/user/resumes/{resume_id}")
def get_single_resume(resume_id: str, user_id: Optional[str] = None):
    doc = db_manager.get_resume_by_id(resume_id, user_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Resume not found.")
    return doc

@app.delete("/api/user/resumes/{resume_id}")
def delete_user_resume_endpoint(resume_id: str, user_id: str = Query(...)):
    deleted = db_manager.delete_resume(resume_id, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Resume not found or unauthorized.")
    return {"status": "success", "message": "Resume deleted successfully."}

# ----------------- SAMPLES & RESUME EXTRACTION -----------------
@app.get("/api/resume/samples")
def get_sample_resumes():
    samples_path = DATA_DIR / "sample_resumes.json"
    if samples_path.exists():
        with open(samples_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

@app.post("/api/resume/upload")
async def upload_resume(file: UploadFile = File(...), user_id: Optional[str] = Form(None)):
    filename = file.filename or "uploaded_file"
    file_bytes = await file.read()
    
    if filename.lower().endswith(".pdf"):
        raw_text = parser_engine.extract_text_from_pdf(file_bytes)
    elif filename.lower().endswith(".docx"):
        raw_text = parser_engine.extract_text_from_docx(file_bytes)
    elif filename.lower().endswith(".ppt") or filename.lower().endswith(".pptx"):
        raw_text = parser_engine.extract_text_from_pptx(file_bytes)
    else:
        try:
            raw_text = file_bytes.decode("utf-8", errors="ignore")
        except Exception:
            raise HTTPException(status_code=400, detail="Unsupported file format. Please upload PDF, DOCX, PPT, or TXT.")

    if not raw_text.strip():
        raise HTTPException(status_code=400, detail="Could not extract text from document. Please ensure it is not scanned/empty.")

    profile = parser_engine.parse_resume(raw_text, filename=filename)

    # Save to user's MongoDB history if user_id is provided
    if user_id:
        try:
            saved_doc = db_manager.save_user_resume(
                user_id=user_id,
                filename=filename,
                candidate_profile=profile,
                target_role="Data Scientist"
            )
            profile["saved_resume_id"] = saved_doc.get("resume_id")
        except Exception as e:
            print(f"Failed to auto-save to MongoDB: {e}")

    return profile

@app.post("/api/resume/parse-text")
def parse_text(req: ParseTextRequest):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")
    return parser_engine.parse_resume(req.text, filename=req.filename or "Pasted_Resume.txt")

@app.get("/api/jobs")
def get_jobs(role: Optional[str] = None, search: Optional[str] = None):
    results = matcher_engine.jobs
    if role and role.lower() != "all":
        results = [j for j in results if role.lower() in j["role"].lower()]
    if search:
        s = search.lower()
        results = [j for j in results if s in j["title"].lower() or s in j["company"].lower() or any(s in sk.lower() for sk in j["required_skills"])]
    return results

@app.post("/api/jobs/match")
def match_jobs(req: MatchRequest):
    candidate_dict = req.candidate.model_dump()
    
    if req.target_job_id:
        target_job = next((j for j in matcher_engine.jobs if j["id"] == req.target_job_id), None)
        if not target_job:
            raise HTTPException(status_code=404, detail="Job not found.")
        single_match = matcher_engine.calculate_explainable_match(candidate_dict, target_job)
        return {"target_match": single_match}

    ranked = matcher_engine.rank_jobs(candidate_dict, top_k=req.top_k, role_filter=req.role_filter)
    return {"matches": ranked}

@app.post("/api/jobs/upload-jd")
async def upload_job_description(file: UploadFile = File(...)):
    filename = file.filename or "job_description"
    file_bytes = await file.read()
    raw_text = parser_engine.extract_from_file_bytes(filename, file_bytes)
    if not raw_text.strip():
        raise HTTPException(status_code=400, detail="Could not extract text from document. Please ensure file contains readable text.")
    extracted_skills = taxonomy_engine.extract_skills_from_text(raw_text)
    return {
        "filename": filename,
        "extracted_text": raw_text.strip(),
        "extracted_skills": extracted_skills
    }

@app.post("/api/jobs/match-custom")
def match_custom_job(req: CustomJobMatchRequest):
    candidate_dict = req.candidate.model_dump()
    desc = req.job_description.strip()
    if not desc:
        raise HTTPException(status_code=400, detail="Job description text cannot be empty.")
    
    extracted_skills = taxonomy_engine.extract_skills_from_text(desc)
    if not extracted_skills:
        extracted_skills = career_classifier.get_top_features_for_role(req.target_role, top_n=5)
    
    req_skills = extracted_skills[:6] if len(extracted_skills) >= 4 else (extracted_skills or ["Python", "Problem Solving"])
    pref_skills = extracted_skills[6:10] if len(extracted_skills) > 6 else []

    custom_job = {
        "id": "custom-target-job",
        "title": req.job_title or f"{req.target_role}",
        "role": req.target_role,
        "category": req.target_role,
        "company": req.company or "Target Company",
        "location": "Custom Application",
        "min_experience_years": 1,
        "education": "Degree in Engineering / Technology / Science",
        "salary_range": "Market Standard",
        "required_skills": req_skills,
        "preferred_skills": pref_skills,
        "description": desc
    }

    match_result = matcher_engine.calculate_explainable_match(candidate_dict, custom_job)
    return {
        "match": match_result,
        "job": custom_job
    }

@app.post("/api/jobs/live-search")
async def search_live_jobs(req: LiveJobSearchRequest):
    """
    Fetches real-world job listings from portals (Naukri, LinkedIn, Indeed, Adzuna),
    extracts canonical skills using taxonomy engine, and matches candidate profile
    using the 5-factor explainable scoring engine.
    """
    raw_jobs = await job_fetcher.search_jobs(
        query=req.query,
        location=req.location,
        portal_filter=req.portal_filter,
        max_results=req.max_results
    )

    matched_count = 0
    if req.candidate:
        candidate_dict = req.candidate.model_dump()
        for job in raw_jobs:
            try:
                match_result = matcher_engine.calculate_explainable_match(candidate_dict, job)
                job["match_score"] = match_result.get("overall_match_score", 0)
                job["matched_skills"] = match_result.get("matched_skills", [])
                job["missing_skills"] = match_result.get("missing_skills", [])
                job["score_breakdown"] = match_result.get("score_breakdown", {})
                job["strengths"] = match_result.get("strengths", [])
                job["gap_analysis"] = match_result.get("gap_analysis", [])
                matched_count += 1
            except Exception as e:
                print(f"[LiveMatch] Error matching job {job.get('id')}: {e}")
                job["match_score"] = None
                job["matched_skills"] = []
                job["missing_skills"] = job.get("required_skills", [])
        
        # Sort descending by match score
        raw_jobs.sort(key=lambda x: (x.get("match_score") is not None, x.get("match_score") or 0), reverse=True)

    return {
        "status": "success",
        "jobs": raw_jobs,
        "count": len(raw_jobs),
        "matched_with_candidate": bool(req.candidate),
        "query": req.query,
        "location": req.location,
        "portal_filter": req.portal_filter
    }

@app.post("/api/career/recommendations")
def career_recommendations(candidate: CandidateProfileModel):
    skills = candidate.skills
    fits = career_classifier.predict_career_fit(skills)
    cluster_projection = job_clusterer.project_candidate(skills)
    return {
        "candidate_skills": skills,
        "recommended_careers": fits,
        "cluster_projection": cluster_projection
    }

@app.post("/api/simulate/what-if")
def simulate_what_if(req: WhatIfRequest):
    candidate_dict = req.candidate.model_dump()
    return what_if_simulator.simulate(candidate_dict, req.target_job_id, req.added_skills)

@app.post("/api/learning/roadmap")
def get_roadmap(req: RoadmapRequest):
    return roadmap_engine.generate_roadmap(req.missing_skills, req.target_role)

@app.get("/api/analytics/market")
def get_market_analytics():
    trends_path = DATA_DIR / "market_trends.json"
    with open(trends_path, "r", encoding="utf-8") as f:
        trends = json.load(f)
    
    trends["cluster_points"] = job_clusterer.get_cluster_points()
    trends["cluster_variance_explained"] = job_clusterer.variance_explained
    return trends

@app.post("/api/copilot/chat")
def copilot_chat(req: CopilotRequest):
    response = career_copilot.answer_query(req.query, req.context)
    return {"reply": response}

STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/")
def serve_index():
    return FileResponse(STATIC_DIR / "index.html")
