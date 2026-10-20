# 🚀 Hack My Career — Project Overview

## Project Title
**Hack My Career: An AI-Powered Career Intelligence & Resume Analytics Platform**

---

## 🎯 Project Objective

Hack My Career is an end-to-end, intelligent platform designed to help students and fresh graduates:

1. **Parse** their resumes automatically (PDF, DOCX, TXT) and extract structured data
2. **Analyse** their skills against a curated canonical taxonomy of 80+ technical skills
3. **Match** their profiles against real-world job listings using explainable ML scoring
4. **Simulate** how adding new skills would improve their job-match score (What-If Analysis)
5. **Cluster** jobs into career families using unsupervised learning
6. **Recommend** personalised learning roadmaps with milestone sequencing
7. **Store** user accounts and uploaded resumes securely in MongoDB Atlas cloud

---

## 👥 Target Users

| User Type | How They Use the Platform |
|---|---|
| **Students / Freshers** | Upload resume, discover best-fit jobs, identify skill gaps |
| **Career Advisors / Teachers** | View candidate profiles, compare ATS scores, suggest skill roadmaps |
| **Placement Officers** | Monitor student-job fit across a batch |

---

## 🔑 Key Value Propositions

- **Zero manual input** — everything is extracted automatically from the uploaded resume
- **Explainable AI** — every match score is broken down into 5 transparent sub-factors
- **What-If Simulator** — "If I learn Docker + AWS, my score goes from 62% → 78%"
- **Personal Cloud Vault** — each user's resumes and analytics are saved in their own MongoDB account
- **Market Intelligence** — live salary trends, in-demand skills, job cluster map

---

## 📁 Project Directory Structure

```
HACK MY CAREER/
│
├── backend/
│   ├── app/
│   │   ├── main.py               ← FastAPI REST API (all endpoints)
│   │   ├── db/
│   │   │   └── mongodb.py        ← MongoDB Atlas connection & operations
│   │   ├── ml/
│   │   │   ├── parser.py         ← Resume text extraction & NLP parsing
│   │   │   ├── taxonomy.py       ← Canonical skill taxonomy & NLP extractor
│   │   │   ├── matcher.py        ← TF-IDF + LSA + Cosine similarity job matcher
│   │   │   ├── classifier.py     ← Logistic Regression career role classifier
│   │   │   ├── clusterer.py      ← K-Means clustering + PCA visualisation
│   │   │   ├── simulator.py      ← What-If skill addition simulator
│   │   │   ├── roadmap.py        ← Personalised learning roadmap generator
│   │   │   └── copilot.py        ← AI Career Copilot chatbot
│   │   ├── static/
│   │   │   ├── index.html        ← Single-Page Application (frontend)
│   │   │   ├── app.js            ← Frontend controller (all UI logic)
│   │   │   └── styles.css        ← Premium dark-mode UI styling
│   │   └── data/
│   │       ├── jobs_dataset.json       ← 50+ real-world job listings
│   │       ├── sample_resumes.json     ← Generic demo candidate profiles
│   │       └── market_trends.json      ← Salary & skill trend data
│
├── .env                          ← MongoDB Atlas URI (secret config)
├── requirements.txt              ← Python dependencies
└── DOCUMENTATION/                ← This folder (teacher documentation)
```

---

## 🛠️ How to Run the Project

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start the backend server
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000

# 3. Open browser at:
http://127.0.0.1:8000
```

---

## 🌐 Live API Documentation
After starting the server, visit:
- **Interactive API Docs (Swagger UI):** `http://127.0.0.1:8000/docs`
- **Redoc API Reference:** `http://127.0.0.1:8000/redoc`
