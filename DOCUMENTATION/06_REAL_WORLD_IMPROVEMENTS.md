# 🌐 Real-World Alignment Plan — Hack My Career

> Prepared based on guide's feedback: Fetch live jobs from Naukri, Indeed, LinkedIn and match with candidate skills. Plus all further real-world improvements.

---

## ⚠️ Important Reality Check First — Web Scraping vs APIs

Before diving in, your guide is absolutely right about the goal — but the *method* matters:

| Method | Naukri.com | Indeed.com | LinkedIn |
|---|---|---|---|
| **Web Scraping** | ❌ Blocks bots (Cloudflare) | ❌ ToS prohibits it | ❌ ToS + legal action risk |
| **Official API** | ❌ No public API | ❌ Publisher API discontinued | ❌ Requires company partnership |
| **Third-party Aggregator APIs** | ✅ JSearch (RapidAPI) | ✅ JSearch (RapidAPI) | ✅ JSearch (RapidAPI) |
| **Free Open APIs** | ✅ Adzuna (India coverage) | ✅ Adzuna | ⚠️ Partial |

**For your project (academic, real-world aligned), the best approach is:**

### ✅ Recommended: JSearch API (via RapidAPI)
- Aggregates real jobs from **Indeed, LinkedIn, Glassdoor, ZipRecruiter**
- **500 free requests/month** (plenty for demo)
- Returns structured JSON with title, company, location, description, salary
- URL: https://rapidapi.com/letscrape-6bfp2aj1t8/api/jsearch

### ✅ Also Recommended: Adzuna API
- Official job aggregator with **India support** (`in.api.adzuna.com`)
- **Free tier: 1000 calls/month**
- Returns real jobs from Naukri, TimesJobs, Shine etc. (India partners)
- URL: https://developer.adzuna.com/

---

## Part 1 — Real-World Jobs Tab Implementation Plan

### What to Build
A new **"Live Jobs"** tab that:
1. Accepts a **search query** (e.g., "Data Scientist Pune")
2. Fetches **real-time jobs** from Adzuna/JSearch API
3. **Automatically matches** them against the candidate's uploaded resume
4. Shows match score, skill overlap, and apply link for each real job

### Backend Changes Required

#### New file: `backend/app/ml/job_fetcher.py`
```python
import httpx
import os

class RealWorldJobFetcher:
    """Fetches live jobs from Adzuna API (India coverage)"""
    
    def __init__(self):
        self.app_id  = os.getenv("ADZUNA_APP_ID")
        self.app_key = os.getenv("ADZUNA_APP_KEY")
        self.base_url = "https://api.adzuna.com/v1/api/jobs/in/search"
    
    async def search_jobs(self, query: str, location: str = "", max_results: int = 20):
        params = {
            "app_id": self.app_id,
            "app_key": self.app_key,
            "results_per_page": max_results,
            "what": query,
            "where": location,
            "content-type": "application/json"
        }
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.base_url}/1", params=params, timeout=10)
            data = resp.json()
        
        jobs = []
        for item in data.get("results", []):
            # Normalize to our internal job schema
            jobs.append({
                "id": f"live-{item['id']}",
                "title": item.get("title", ""),
                "company": item.get("company", {}).get("display_name", "Unknown"),
                "location": item.get("location", {}).get("display_name", ""),
                "salary_range": self._format_salary(item),
                "description": item.get("description", ""),
                "apply_url": item.get("redirect_url", ""),
                "posted_at": item.get("created", ""),
                "source": "Adzuna",
                # Skills extracted by taxonomy engine later
                "required_skills": [],
                "preferred_skills": []
            })
        return jobs
    
    def _format_salary(self, item):
        min_s = item.get("salary_min")
        max_s = item.get("salary_max")
        if min_s and max_s:
            return f"₹{int(min_s):,} - ₹{int(max_s):,}"
        return "Salary not disclosed"
```

#### New API endpoint in `main.py`
```python
@app.post("/api/jobs/live-search")
async def search_live_jobs(req: LiveJobSearchRequest):
    """
    Fetches real jobs from Adzuna, extracts skills via taxonomy,
    then matches against candidate profile.
    """
    raw_jobs = await job_fetcher.search_jobs(req.query, req.location)
    
    # Extract skills from description using our taxonomy
    for job in raw_jobs:
        job["required_skills"] = taxonomy_engine.extract_skills_from_text(job["description"])
    
    # Match candidate against each live job
    if req.candidate:
        candidate = req.candidate.model_dump()
        for job in raw_jobs:
            if job["required_skills"]:
                match = matcher_engine.calculate_explainable_match(candidate, job)
                job["match_score"] = match["overall_match_score"]
                job["matched_skills"] = match["matched_skills"]
                job["missing_skills"] = match["missing_skills"]
    
    raw_jobs.sort(key=lambda x: x.get("match_score", 0), reverse=True)
    return {"jobs": raw_jobs, "total": len(raw_jobs), "source": "Adzuna API"}
```

#### `.env` additions needed
```
ADZUNA_APP_ID=your_app_id_here
ADZUNA_APP_KEY=your_app_key_here
# OR for JSearch:
RAPIDAPI_KEY=your_key_here
```

### Frontend Changes Required

#### New tab in `index.html`
```html
<!-- Add to tab navigation buttons -->
<button class="tab-btn" onclick="switchTab('tab-live-jobs')">
  🌐 Live Jobs
</button>

<!-- Add new tab pane -->
<div id="tab-live-jobs" class="tab-pane">
  <div class="live-jobs-search-bar">
    <input id="live-job-query" type="text" placeholder="e.g. Data Scientist, ML Engineer..." />
    <input id="live-job-location" type="text" placeholder="City (e.g. Pune, Bangalore)" />
    <button onclick="fetchLiveJobs()">🔍 Search Real Jobs</button>
  </div>
  <div id="live-jobs-container">
    <!-- Job cards with apply buttons render here -->
  </div>
</div>
```

#### New function in `app.js`
```javascript
async function fetchLiveJobs() {
    const query = document.getElementById('live-job-query').value;
    const location = document.getElementById('live-job-location').value;
    
    const res = await fetch('/api/jobs/live-search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            query,
            location,
            candidate: currentProfile  // pass current resume profile
        })
    });
    
    const data = await res.json();
    renderLiveJobs(data.jobs);
}

function renderLiveJobs(jobs) {
    const container = document.getElementById('live-jobs-container');
    container.innerHTML = jobs.map(job => `
        <div class="live-job-card">
            <h3>${job.title} @ ${job.company}</h3>
            <p>${job.location} • ${job.salary_range}</p>
            <p>Match Score: <strong>${job.match_score || 'N/A'}%</strong></p>
            <p>Matched Skills: ${job.matched_skills?.join(', ') || 'Upload resume first'}</p>
            <a href="${job.apply_url}" target="_blank">Apply Now →</a>
        </div>
    `).join('');
}
```

---

## Part 2 — Further Real-World Improvements

### Priority 1 — HIGH IMPACT (Do These First)

#### 1.1 Replace Static Salary Data with Live Salary APIs
**Current:** Salary ranges are hardcoded in `jobs_dataset.json`  
**Improvement:** Fetch real salary data from **Glassdoor API** or **LinkedIn Salary Insights**  
**Fallback:** Use **Ambitionbox scraper** or **AmbitionBox public API** for India salaries

```python
# .env
GLASSDOOR_PARTNER_ID=your_id
GLASSDOOR_API_KEY=your_key
```

---

#### 1.2 Resume Score Benchmarking Against Peers
**Current:** ATS score is absolute (0-100 rubric)  
**Improvement:** Store anonymized ATS scores for all users in MongoDB → compute **percentile ranking**

```
"Your ATS score of 78 is better than 64% of candidates who applied for Data Scientist roles"
```

**Implementation:**
```python
# In mongodb.py
def get_ats_percentile(self, ats_score: int, target_role: str) -> float:
    all_scores = [r["ats_score"] for r in 
                  self.db["resumes"].find({"target_role": target_role})]
    percentile = sum(1 for s in all_scores if s < ats_score) / len(all_scores) * 100
    return round(percentile, 1)
```

---

#### 1.3 AI-Powered Resume Rewriting Suggestions
**Current:** Shows missing skills list only  
**Improvement:** Use an LLM (Google Gemini API — free tier) to generate specific resume improvement suggestions

```python
# backend/app/ml/rewriter.py
import google.generativeai as genai

def suggest_resume_improvements(resume_text: str, missing_skills: list, job_title: str) -> str:
    prompt = f"""
    Given this resume and job requirements for {job_title}, 
    suggest 3 specific bullet point improvements to add to the resume.
    Missing skills: {missing_skills}
    Resume: {resume_text[:2000]}
    """
    model = genai.GenerativeModel('gemini-1.5-flash')  # Free tier
    return model.generate_content(prompt).text
```

**API Cost:** Gemini 1.5 Flash = **free up to 1 million tokens/day**

---

#### 1.4 Email/LinkedIn Job Alert System
**Current:** User must manually check jobs every time  
**Improvement:** Schedule background job to check for new matching jobs daily and email alerts

```python
# Using APScheduler + smtplib
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

@scheduler.scheduled_job('cron', hour=9)  # 9 AM daily
async def daily_job_alerts():
    for user in db.users.find():
        new_jobs = await job_fetcher.search_jobs(user["target_role"])
        high_matches = [j for j in new_jobs if j["match_score"] > 70]
        if high_matches:
            send_alert_email(user["email"], high_matches)
```

---

#### 1.5 Resume Version Control & Comparison
**Current:** Multiple resumes stored but no comparison  
**Improvement:** Side-by-side comparison of two saved resumes showing:
- ATS score difference
- New/removed skills
- Improvement in job match percentage

---

### Priority 2 — MEDIUM IMPACT

#### 2.1 Multi-Language Resume Support
- Add `langdetect` to detect resume language
- Support Hindi, Marathi resumes via Google Translate API
- Target entry-level candidates who write in regional languages

#### 2.2 GitHub Portfolio Integration
**Current:** GitHub URL extracted but not analyzed  
**Improvement:** Use **GitHub REST API** (free, no key needed) to:
- Fetch public repositories
- Extract programming languages used
- Add these as detected skills automatically

```python
import httpx

async def fetch_github_skills(github_url: str) -> list:
    username = github_url.split("github.com/")[-1].strip("/")
    async with httpx.AsyncClient() as client:
        repos = await client.get(f"https://api.github.com/users/{username}/repos")
        lang_counts = {}
        for repo in repos.json():
            lang = repo.get("language")
            if lang:
                lang_counts[lang] = lang_counts.get(lang, 0) + 1
    return list(lang_counts.keys())  # ["Python", "JavaScript", "SQL"]
```

**Cost:** FREE — GitHub API allows 60 unauthenticated requests/hour

---

#### 2.3 Interview Question Generator
Based on skill gaps, generate likely interview questions the candidate will face:

```
Missing skill: TensorFlow
→ "Explain the difference between tf.keras and standalone Keras"
→ "How would you implement a custom training loop in TensorFlow?"
```

This adds direct value beyond just showing the gap.

---

#### 2.4 LinkedIn Profile Import
Instead of uploading a PDF, allow users to paste their **LinkedIn profile URL**  
Use LinkedIn's public profile data (no API key needed for public pages):

```python
# Using linkedin-api (unofficial)
from linkedin_api import Linkedin
# OR use playwright to scrape public profile pages
```

> Note: For academic projects, use a "Paste your LinkedIn 'About' section text" input as a safe alternative

---

#### 2.5 Mock Interview Simulator (using LLM)
Integrate Gemini/ChatGPT to conduct a mock interview:
- Ask questions based on the job description
- Evaluate candidate's text responses
- Give feedback on answer quality and keywords

---

#### 2.6 Company Culture Fit Analysis
Add a culture/values dimension to job matching:
- Parse company reviews from **Glassdoor API**
- Ask candidate about work preferences (remote/hybrid, startup/MNC)
- Add a "Culture Fit Score" as a 6th factor in the composite formula

---

### Priority 3 — ADVANCED (Future Scope)

#### 3.1 Real Applicant Tracking — Full ATS System
Transform from a tool for *candidates* to a tool for *companies*:
- HR uploads job description
- Candidates upload resumes
- System ranks all candidates for that JD
- HR sees ranked shortlist

---

#### 3.2 Fine-tuned NLP Model for Skill Extraction
**Current:** Rule-based taxonomy matching (keyword lookup)  
**Future:** Train a custom Named Entity Recognition (NER) model using spaCy:
- Training data: 1000+ annotated resumes
- Labels: SKILL, DEGREE, INSTITUTION, COMPANY, ROLE
- Result: Catches "exp. in Python" even without exact word match

---

#### 3.3 Semantic Skill Equivalence
**Current:** "ML" ≠ "Machine Learning" (exact match only)  
**Future:** Use **sentence transformers** (all-MiniLM-L6-v2, free) to compute embedding similarity:
```
"Machine Learning" ↔ "ML" → similarity: 0.91 ✅
"React.js" ↔ "ReactJS" → similarity: 0.97 ✅
"Tensorflow" ↔ "TF" → similarity: 0.82 ✅
```
This eliminates missed skill detections due to abbreviations/synonyms.

---

#### 3.4 Browser Extension
Build a Chrome extension that:
- Detects when user is on a Naukri/LinkedIn job page
- Automatically computes match score against their stored resume
- Shows match percentage and missing skills in a popup

---

#### 3.5 College/Batch-Level Analytics Dashboard
Admin dashboard for placement officers:
- View all students' profiles (anonymized)
- Filter by skill, ATS score, target role
- Bulk export to Excel
- Trend: "% of batch job-ready for Data Science roles"

---

## Part 3 — Implementation Priority Summary

| # | Feature | Effort | Impact | Cost | Do When |
|---|---|---|---|---|---|
| Live Jobs (Adzuna) | Medium | ⭐⭐⭐⭐⭐ | Free tier | **NOW** |
| GitHub Portfolio Scan | Low | ⭐⭐⭐⭐ | Free | **NOW** |
| Gemini Resume Suggestions | Low | ⭐⭐⭐⭐⭐ | Free (flash) | **NOW** |
| ATS Percentile Ranking | Low | ⭐⭐⭐ | Free (own DB) | **NOW** |
| Email Job Alerts | Medium | ⭐⭐⭐ | Free (Gmail SMTP) | Next Phase |
| Mock Interview (Gemini) | Medium | ⭐⭐⭐⭐ | Free (flash) | Next Phase |
| Resume Version Comparison | Low | ⭐⭐⭐ | Free | Next Phase |
| Sentence Transformer Skill Match | High | ⭐⭐⭐⭐⭐ | Free model | Future |
| Custom NER Model | Very High | ⭐⭐⭐⭐ | Free (training) | Future |
| Browser Extension | High | ⭐⭐⭐⭐⭐ | Free | Future |
| Batch Analytics Dashboard | Medium | ⭐⭐⭐⭐ | Free | Future |

---

## Part 4 — API Keys You Need to Get Now (All Free)

| API | Purpose | Free Tier | Sign Up URL |
|---|---|---|---|
| **Adzuna** | Live India jobs | 1000 calls/month | developer.adzuna.com |
| **JSearch (RapidAPI)** | Indeed + LinkedIn jobs | 500 calls/month | rapidapi.com/jsearch |
| **GitHub REST API** | Portfolio analysis | 60 req/hr (no key) | No signup needed |
| **Google Gemini** | AI suggestions + interview | 1M tokens/day free | aistudio.google.com |
| **MongoDB Atlas** | Already connected | 512MB free | Already done ✅ |

**Total monthly cost for all features: ₹0**

---

## Part 5 — Exact Steps to Implement Live Jobs Tab

```
Step 1: Sign up at developer.adzuna.com → get App ID + App Key
        
Step 2: Add to .env:
        ADZUNA_APP_ID=xxxx
        ADZUNA_APP_KEY=xxxx
        
Step 3: pip install httpx

Step 4: Create backend/app/ml/job_fetcher.py (code above)

Step 5: Add /api/jobs/live-search endpoint to main.py

Step 6: Add "Live Jobs" tab to index.html

Step 7: Add fetchLiveJobs() + renderLiveJobs() to app.js

Step 8: Test with query "Data Scientist" + location "Pune"
        → Should return 20 real Adzuna jobs with match scores
```

**Estimated time to implement: 4-6 hours**

---

## What to Tell Your Guide

> "We are implementing real-world job fetching using the **Adzuna API** (official job aggregator that sources from Naukri, TimesJobs, Shine, and other Indian portals) because direct scraping of Naukri.com violates their Terms of Service. Adzuna provides structured, real-time job data via a free REST API with 1000 calls/month at no cost. The live jobs will be matched against the candidate's resume using our existing TF-IDF + LSA + 5-factor composite scoring engine."

This is the professionally correct answer — it shows awareness of legal constraints while still achieving the real-world goal.
