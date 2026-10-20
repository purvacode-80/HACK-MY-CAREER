# 🏗️ System Architecture — Hack My Career

> This document describes the technical architecture, component relationships, and design decisions.

---

## Architecture Pattern: 3-Tier Web Application

```
┌──────────────────────────────────────────────────────────────────┐
│  TIER 1: PRESENTATION LAYER (Frontend)                           │
│  ─────────────────────────────────────────────────────────────── │
│  Technology: Vanilla HTML5 + CSS3 + JavaScript (ES2022)         │
│  Files: index.html, styles.css, app.js                          │
│  Pattern: Single-Page Application (SPA)                          │
│  Runs in: User's browser (client-side)                           │
└──────────────────────────────────────────────────────────────────┘
                              ↕ REST API (HTTP/JSON)
┌──────────────────────────────────────────────────────────────────┐
│  TIER 2: APPLICATION LAYER (Backend)                             │
│  ─────────────────────────────────────────────────────────────── │
│  Technology: Python 3.10+ / FastAPI / Uvicorn ASGI              │
│  Files: main.py + ml/*.py                                        │
│  Pattern: RESTful microservice with ML engines                   │
│  Runs on: Local server (127.0.0.1:8000) or cloud deployment     │
└──────────────────────────────────────────────────────────────────┘
                              ↕ PyMongo driver (TCP/TLS)
┌──────────────────────────────────────────────────────────────────┐
│  TIER 3: DATA LAYER (Database + Storage)                         │
│  ─────────────────────────────────────────────────────────────── │
│  Technology: MongoDB Atlas (NoSQL Cloud Database)                │
│  Collections: users, resumes                                     │
│  Hosted on: MongoDB Atlas Cluster (cloud.mongodb.com)            │
│  Fallback: Local JSON file (hack_my_career_mongodb.json)         │
└──────────────────────────────────────────────────────────────────┘
```

---

## Component Architecture

```
backend/app/
│
├── main.py                 ← API Gateway (FastAPI)
│   ├── Routing             → maps URLs to handler functions
│   ├── Pydantic Validation → type-safe request/response models
│   ├── CORS Middleware     → allows cross-origin browser requests
│   └── Static File Mount  → serves HTML/JS/CSS at /static
│
├── db/
│   └── mongodb.py          ← Data Access Layer
│       ├── MongoDBManager  → manages connection lifecycle
│       ├── connect_atlas() → establishes TLS connection to Atlas
│       ├── create_user()   → hashes password + inserts user doc
│       ├── authenticate_user() → finds user + verifies hash
│       ├── save_user_resume()  → upserts resume to Atlas
│       ├── get_user_resumes()  → fetches all resumes for a user
│       └── Fallback         → local JSON if Atlas unreachable
│
└── ml/                     ← Machine Learning Engine Layer
    ├── taxonomy.py          → Skill knowledge base (80+ skills)
    ├── parser.py            → NLP text extraction pipeline
    ├── matcher.py           → TF-IDF + LSA + Cosine similarity
    ├── classifier.py        → Logistic Regression + Random Forest
    ├── clusterer.py         → K-Means + PCA + Silhouette
    ├── simulator.py         → What-If counterfactual analysis
    ├── roadmap.py           → Learning pathway generator
    └── copilot.py           → AI Career Copilot (rule-based NLG)
```

---

## API Layer — Request/Response Contracts

```
All API requests/responses are in JSON format.
Pydantic models enforce type safety automatically.

Example: POST /api/jobs/match

Request Body:
{
  "candidate": {
    "name": "Alex Morgan",
    "skills": ["Python", "SQL", "Machine Learning"],
    "experience_years": 1.0,
    "raw_text": "...",
    "projects": ["..."]
  },
  "top_k": 25,
  "role_filter": "Data Scientist"
}

Response:
{
  "matches": [
    {
      "job_title": "Junior Data Scientist",
      "company": "TechCorp",
      "overall_match_score": 78.4,
      "breakdown": {
        "semantic_similarity": 82.1,
        "skill_match": 75.0,
        "experience_fit": 85,
        "education_fit": 95,
        "project_relevance": 90
      },
      "matched_skills": ["Python", "SQL"],
      "missing_skills": ["Scikit-Learn", "TensorFlow"]
    },
    ...
  ]
}
```

---

## ML Engine Initialization (Startup Sequence)

When the server starts (`uvicorn backend.app.main:app`), all ML engines initialize:

```
Server Startup (one-time, ~3-5 seconds)
│
├── taxonomy_engine = TaxonomyEngine()
│     → Load 80+ canonical skills into memory
│     → Build skill-to-alias lookup dictionary
│
├── matcher_engine = MatcherEngine()
│     → Load jobs_dataset.json (50+ jobs)
│     → TfidfVectorizer.fit(all job texts)       ← TRAINS
│     → TruncatedSVD.fit(tfidf_job_matrix)       ← TRAINS
│     → Dense job matrix stored in RAM
│
├── career_classifier = CareerClassifier()
│     → Load jobs_dataset.json
│     → Build binary skill vectors (X) + role labels (y)
│     → LogisticRegression.fit(X, y)              ← TRAINS
│     → RandomForestClassifier.fit(X, y)          ← TRAINS
│
├── job_clusterer = JobClusterer()
│     → Load jobs_dataset.json
│     → Build binary skill vectors
│     → KMeans(k=5).fit(X)                        ← TRAINS
│     → silhouette_score computed
│     → PCA(n=2).fit_transform(X)                 ← FITS
│
└── db_manager = MongoDBManager()
      → Read MONGODB_URI from .env
      → Connect to MongoDB Atlas (ping test)
      → Fallback to local JSON if connection fails
```

**All training happens at startup using scikit-learn, takes ~3-5 seconds. After that, each request is sub-second.**

---

## Frontend Architecture (Single-Page Application)

```
index.html
│
├── Auth Gateway (shown before login)
│   ├── Login / Signup tabs
│   ├── Email + Password form
│   └── Demo login button
│
└── Dashboard Wrapper (shown after login)
    ├── Header Bar
    │   ├── User display name / avatar
    │   ├── Active profile pill
    │   ├── File upload button
    │   └── MongoDB status badge
    │
    └── Tab Navigation
        ├── tab-resume    → Candidate Profile Card + ATS gauge
        ├── tab-jobs      → Ranked Job Matches + Skill Gap
        ├── tab-whatif    → What-If Skill Simulator
        ├── tab-market    → Salary Trends + Cluster Map charts
        ├── tab-roadmap   → Learning Roadmap
        ├── tab-history   → User's Saved Resume Vault
        └── tab-copilot   → AI Career Copilot chatbot

app.js manages:
    ├── State variables: currentProfile, currentUser, userResumes, rankedMatches
    ├── Auth: handleAuthSubmit(), quickDemoLogin(), logoutUser()
    ├── Resume: handleFileUpload(), setCandidateProfile(), renderPlaceholderProfile()
    ├── Jobs: runJobMatching(), renderRankedJobs(), selectJob()
    ├── What-If: toggleSimSkill(), runWhatIfSimulation()
    ├── History: fetchUserResumes(), renderUserResumes(), loadSavedResume()
    └── Charts: renderMarketCharts() using Chart.js
```

---

## Data Flow — Authentication Security

```
Signup:
password (plaintext)
    → hashlib.sha256(password.encode()).hexdigest()
    → stored_hash (in MongoDB)
    → plaintext password NEVER stored

Login:
entered_password (plaintext)
    → hashlib.sha256(entered_password.encode()).hexdigest()
    → compare with stored_hash
    → match? → return user object
    → no match? → raise 401 Unauthorized
```

> **Note:** In production, this would use `bcrypt` with salt for stronger security. SHA-256 without salt is suitable for academic projects.

---

## Technologies Used — Complete Stack

| Layer | Technology | Version | Purpose |
|---|---|---|---|
| **Backend Framework** | FastAPI | 0.115+ | REST API server |
| **ASGI Server** | Uvicorn | 0.30+ | Async HTTP server |
| **ML / Data Science** | scikit-learn | 1.5+ | TF-IDF, SVD, KMeans, LR, RF, PCA |
| **NLP / Text** | NumPy | 2.0+ | Matrix operations, dot products |
| **PDF Parsing** | pdfplumber | 0.11+ | PDF text extraction |
| **Data Validation** | Pydantic | 2.0+ | API request/response models |
| **Database** | MongoDB Atlas | Cloud | NoSQL document storage |
| **DB Driver** | PyMongo | 4.8+ | Python ↔ MongoDB connection |
| **Config** | python-dotenv | 1.0+ | Load .env secrets |
| **Frontend** | HTML5 / CSS3 | Modern | UI structure & styling |
| **Frontend Logic** | Vanilla JavaScript | ES2022 | SPA controller |
| **Charts** | Chart.js | 4.x (CDN) | Bar, radar, scatter plots |
| **Fonts** | Google Fonts - Inter | CDN | Typography |

---

## Database Schema (MongoDB Collections)

### `users` Collection
```json
{
  "user_id": "usr_18f0bcaf3ad6",
  "name": "Purva Wagh",
  "email": "purva@example.com",
  "password_hash": "sha256_hex_string",
  "created_at": "2026-10-20T10:15:17.120Z"
}
```

### `resumes` Collection
```json
{
  "resume_id": "res_efb6071a99ed",
  "user_id": "usr_18f0bcaf3ad6",
  "filename": "Purva_Resume.pdf",
  "target_role": "Data Scientist",
  "ats_score": 88,
  "skill_count": 16,
  "skills": ["Python", "SQL", "Machine Learning", ...],
  "uploaded_at": "2026-10-20T11:30:00.000Z",
  "candidate_profile": {
    "name": "Purva Wagh",
    "email": "purva@vit.edu",
    "phone": "+91-9876543210",
    "location": "Pune, Maharashtra, India",
    "profiles": ["linkedin.com/in/purva", "github.com/purva"],
    "education": "VIT Pune — B.Tech IT (CGPA: 9.0)",
    "experience_years": 0.8,
    "skills": ["Python", "SQL", "FastAPI", "Docker", ...],
    "projects": ["Project 1...", "Project 2..."],
    "raw_text": "full resume text...",
    "ats_score": 88
  }
}
```

---

## Why These Technologies Were Chosen

| Choice | Reason |
|---|---|
| **FastAPI** over Flask | Automatic API docs, async support, Pydantic validation built-in |
| **scikit-learn** | Industry standard, well-documented, all required algorithms in one library |
| **TruncatedSVD** over full SVD | Efficient for sparse TF-IDF matrices — O(n×k) not O(n³) |
| **MongoDB Atlas** over SQL | Resumes are variable-length nested documents — SQL tables are inflexible |
| **Vanilla JS** over React/Vue | No build step needed; serves directly from FastAPI static files |
| **pdfplumber** over PyPDF2 | Better text extraction, layout-aware, handles columns in resumes |
| **Cosine similarity** over Euclidean | Length-invariant — short and long resumes compared fairly |
| **K-Means k=5** | 5 major tech career domains: DS, DE, Web, DevOps, AI |
