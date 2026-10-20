# 🔄 Project Flow — Step-by-Step Data Pipeline

> This document traces the complete journey of data through the system — from a user uploading their resume to seeing personalised job matches, clusters, and a learning roadmap.

---

## High-Level Flow

```
User uploads Resume
        ↓
[1] Text Extraction (PDF/DOCX/TXT)
        ↓
[2] NLP Parsing (Name, Contact, Education, Skills, Projects)
        ↓
[3] Skill Taxonomy Matching (80+ canonical skills extracted)
        ↓
[4] ATS Score Calculation (0–100 completeness rubric)
        ↓
[5] MongoDB Atlas Save (resume stored to user's cloud vault)
        ↓
[6] TF-IDF + LSA Vectorization of resume text
        ↓
[7] Cosine Similarity vs 50+ job vectors
        ↓
[8] 5-Factor Composite Scoring for each job
        ↓
[9] Ranked Job Matches displayed to user
        ↓
[10] User selects a job → Skill Gap Analysis shown
        ↓
[11] User clicks "What If?" → Simulated score with added skills
        ↓
[12] Learning Roadmap generated for missing skills
        ↓
[13] K-Means Cluster Map shows where candidate fits in job market
        ↓
[14] Logistic Regression predicts career role probability
```

---

## Stage 1 — User Authentication

```
Browser (Login Form)
    → POST /api/auth/login { email, password }
    → mongodb.py: authenticate_user()
        → SHA-256 hash(password) compared to stored hash
    ← Returns { user_id, name, email }
    → Stored in localStorage (browser session)
```

**On signup:**
```
POST /api/auth/signup { name, email, password }
    → SHA-256 hash(password)
    → MongoDB Atlas: db["users"].insert_one({ user_id, name, email, hash })
    ← Returns { user_id, name, email }
```

---

## Stage 2 — Resume Upload & Parsing

```
User selects file → handleFileUpload() in app.js
    → POST /api/resume/upload (multipart form-data)
    → main.py: upload_resume()
    
    File Routing:
    ┌─────────┬──────────────────────────────────────────────┐
    │ .pdf    │ pdfplumber.open() → page.extract_text()     │
    │ .docx   │ zipfile.ZipFile() → XML parse word/doc.xml  │
    │ .pptx   │ zipfile.ZipFile() → XML parse slides/*.xml  │
    │ .txt    │ bytes.decode("utf-8")                        │
    └─────────┴──────────────────────────────────────────────┘
    
    → parser.parse_resume(raw_text)
    → Returns structured profile JSON
    
    → If user_id provided: db_manager.save_user_resume() → MongoDB
    ← Profile JSON returned to frontend
    → setCandidateProfile(profile) updates the UI
```

---

## Stage 3 — NLP Parsing Pipeline

```
raw_text (string)
    ↓
clean_text()
    → Replace \xa0 (non-breaking space) → " "
    → Collapse multiple spaces → single space
    → Collapse 3+ newlines → double newline
    ↓
extract_email(text)       → RegEx: email pattern
extract_phone(text)       → RegEx: Indian +91 / international formats
extract_contact_info()    → Combines above + location + LinkedIn + GitHub
extract_education(text)   → Keyword match: B.Tech, VIT, University, Diploma
extract_experience(text)  → Detect "third-year", "intern" keywords → estimate years
extract_projects(text)    → Numbered pattern + section header parsing
extract_skills_from_text() → Taxonomy canonical matching (taxonomy_engine)
calculate_ats_score()     → Weighted rubric → integer 0-100
    ↓
{
  name, email, phone, location, profiles,
  contact_display, education,
  experience_years, experience_display,
  skills: [...],
  projects: [...],
  raw_text, skill_count, ats_score
}
```

---

## Stage 4 — Skill Extraction (Taxonomy Engine)

```
raw_text (cleaned string)
    ↓
taxonomy_engine.extract_skills_from_text(text)
    → Lowercase the text
    → For each canonical skill in taxonomy:
        → Check if skill name (or alias) appears in text
        → Case-insensitive exact / substring match
        → Add to detected_skills set (deduplication)
    ↓
Returns: ["Python", "SQL", "FastAPI", "Docker", "React", ...]
(Canonical names only — no duplicates, no aliases)
```

---

## Stage 5 — Job Matching Pipeline

```
setCandidateProfile() → runJobMatching()
    → POST /api/jobs/match { candidate: profile, top_k: 25 }
    → main.py → matcher_engine.rank_jobs()
    
    For each of 50+ jobs:
        ┌─────────────────────────────────────────────────────────┐
        │ 1. Build resume_text = raw_text + " " + skills.join(" ")│
        │ 2. Build job_text = title + role + skills + description │
        │                                                         │
        │ LAYER 1: TF-IDF Vectorization                          │
        │    tfidf_vectorizer.transform([resume_text, job_text]) │
        │    → cosine_similarity() → baseline_score (0-100)      │
        │                                                         │
        │ LAYER 2: LSA Dense Vectorization                       │
        │    svd.transform(tfidf_pair)                           │
        │    → dot product / (||a|| × ||b||) → semantic_score    │
        │                                                         │
        │ LAYER 3: Skill Overlap                                 │
        │    set(candidate_skills) ∩ set(required_skills)       │
        │    → matched, missing, preferred_missing               │
        │                                                         │
        │ LAYER 4: Experience Comparison                         │
        │    candidate_years vs job.min_experience_years         │
        │                                                         │
        │ LAYER 5: Education & Projects Count                    │
        │                                                         │
        │ COMPOSITE = 0.40×semantic + 0.30×skill +              │
        │             0.15×exp + 0.10×edu + 0.05×proj           │
        └─────────────────────────────────────────────────────────┘
    
    → ranked.sort(key=composite_score, descending=True)
    → Return top_k matches
    ← Frontend renders ranked job list cards
```

---

## Stage 6 — What-If Simulation

```
User toggles skills in What-If panel → simulate()
    → POST /api/simulate/what-if {
          candidate: profile,
          target_job_id: "job-xyz",
          added_skills: ["Docker", "AWS"]
      }
    
    simulator.simulate():
        original_match = matcher.calculate_explainable_match(profile, job)
        
        simulated_profile = copy(profile)
        simulated_profile.skills += added_skills
        
        simulated_match = matcher.calculate_explainable_match(simulated_profile, job)
        
        delta = simulated_score - original_score
    
    ← Returns { original_score, simulated_score, delta, newly_satisfied_skills }
    → UI updates the score gauge and breakdown bars in real-time
```

---

## Stage 7 — K-Means Clustering (Startup / Pre-computed)

```
At server startup (clusterer.py __init__):

1. Load all 50+ jobs
2. Build binary skill vectors:
   job_vec[i] = [1 if skill_i in job.required+preferred else 0]
   → Shape: (n_jobs × n_canonical_skills)

3. KMeans(n_clusters=5, n_init=10).fit(X)
   → cluster_labels = [0, 2, 1, 4, 0, 3, ...]
   → cluster_centers_ = 5 centroid vectors

4. silhouette_score(X, cluster_labels) → quality metric

5. PCA(n_components=2).fit_transform(X)
   → pca_coords: (n_jobs × 2) 2D coordinates

6. Name each cluster by top-3 skills in its centroid

→ GET /api/analytics/market → returns cluster_points for frontend scatter plot
→ POST /api/career/recommendations → project_candidate(skills) → 
     predict which cluster the candidate falls into
```

---

## Stage 8 — Career Classification

```
After job matching:
    → POST /api/career/recommendations { skills: [...] }
    
    career_classifier.predict_career_fit(skills):
        vec = skills_to_binary_vector(skills)
        probs = logistic_regression.predict_proba(vec)
        
        Returns:
        [
          { role: "Data Scientist",    fit_probability: 67.3%, fit_level: "High"   },
          { role: "Data Engineer",     fit_probability: 18.2%, fit_level: "Medium" },
          { role: "Full Stack Dev",    fit_probability: 8.4%,  fit_level: "Low"    },
          ...
        ]
    
    → Frontend renders probability bars for each career path
```

---

## Stage 9 — Learning Roadmap Generation

```
After seeing missing skills:
    → POST /api/learning/roadmap {
          missing_skills: ["Docker", "AWS", "TensorFlow"],
          target_role: "Data Scientist"
      }
    
    roadmap_engine.generate_roadmap():
        → For each missing skill:
            → Look up curated resource database
            → Find tutorials, courses, estimated duration
            → Assign milestone order (dependencies considered)
        → Generate milestone sequence with timelines
        → Add portfolio capstone project suggestion
    
    ← Returns structured weekly/monthly learning plan
    → Frontend renders milestone cards with resource links
```

---

## End-to-End Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          HACK MY CAREER — DATA FLOW                         │
└─────────────────────────────────────────────────────────────────────────────┘

  [USER]
    │
    ├─→ Sign Up/Login ─────────────────────→ [MongoDB Atlas]
    │         ↑ User session saved             users collection
    │
    ├─→ Upload Resume ─→ [FastAPI Backend]
    │         │             │
    │         │             ├─→ pdfplumber/DOCX parser → raw_text
    │         │             ├─→ RegEx NLP extraction   → name, email, phone
    │         │             ├─→ Taxonomy matcher        → skills[]
    │         │             ├─→ ATS rubric scorer       → ats_score (0-100)
    │         │             └─→ MongoDB save            → [MongoDB Atlas]
    │         │                                           resumes collection
    │         ↓
    │   structured profile JSON
    │         │
    ├─→ Job Matching ─→ [MatcherEngine]
    │         │             │
    │         │             ├─→ TF-IDF vectorize  → sparse matrix
    │         │             ├─→ TruncatedSVD      → dense semantic matrix
    │         │             ├─→ Cosine Similarity → scores per job
    │         │             ├─→ Skill overlap     → matched/missing lists
    │         │             └─→ Composite Score   → ranked job list
    │         ↓
    │   ranked matches + skill gaps
    │         │
    ├─→ What-If ──────→ [WhatIfSimulator]
    │         │             ├─→ Original score
    │         │             ├─→ Simulated score (with added skills)
    │         │             └─→ Score delta + explanation
    │         ↓
    │   score delta displayed
    │
    ├─→ Cluster Map ──→ [JobClusterer]
    │         │             ├─→ K-Means clusters (pre-computed at startup)
    │         │             ├─→ PCA 2D coords
    │         │             └─→ Candidate position projected
    │         ↓
    │   interactive scatter plot
    │
    └─→ Learning Roadmap → [RoadmapEngine]
              │             ├─→ missing skill lookup
              │             └─→ curated resource database
              ↓
        Personalised week-by-week plan
```
