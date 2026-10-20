# Hack My Career
### *Intelligent Semantic Resume–Job Matching, Explainable Skill Gap Analysis, MongoDB Atlas Vault & Personalized Career Guidance*

[![Data Science & Analytics](https://img.shields.io/badge/Subject-Data%20Science%20%26%20Analytics-indigo.svg)](https://scikit-learn.org)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI%20%7C%20Python-009688.svg)](https://fastapi.tiangolo.com)
[![MongoDB Atlas](https://img.shields.io/badge/Database-MongoDB%20Atlas-47A248.svg)](https://www.mongodb.com/atlas)
[![Streamlit](https://img.shields.io/badge/Demo-Streamlit-FF4B4B.svg)](https://streamlit.io)
[![Licence](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## 🌟 Executive Summary

**Hack My Career** is an end-to-end Data Science and Natural Language Processing platform designed to empower students and job seekers with precision career intelligence.

Rather than relying on naive keyword matching, this platform:
1. **Parses and normalizes** unstructured PDF/DOCX resumes into dynamic candidate profiles using regular expressions, entity recognition, and a canonical taxonomy of 70+ technical skills.
2. **Evaluates fit** using a **5-Factor Explainable Composite Scoring Formula** combining dense semantic concept similarity (40%), direct skill matching (30%), experience seniority (15%), degree alignment (10%), and project depth (5%).
3. **Features an Interactive What-If Simulator** where candidates toggle prospective skills (e.g. *Docker + AWS*) and observe immediate, real-time score elevations.
4. **Generates a Personalized Learning Roadmap** with milestone sequencing, tutorial links, and recommended portfolio capstone projects.
5. **Discovers latent job families** via **Unsupervised K-Means Clustering** with 2D PCA projection and Silhouette Score validation.
6. **MongoDB Atlas Cloud Vault**: Securely manages user sign-up, authentication credentials, and stores individual user resumes with past ATS scores and skill breakdowns.

---

## 🍃 MongoDB Atlas Configuration

Hack My Career natively connects to **MongoDB Atlas** for secure cloud storage of accounts and resumes.

### How to Connect:
1. **Option A: Environment Variable / `.env`**
   Create a `.env` file in the project root:
   ```env
   MONGODB_URI=mongodb+srv://<username>:<password>@cluster0.xxxx.mongodb.net/?retryWrites=true&w=majority
   ```
2. **Option B: Web UI Settings**
   Click **⚙️ Atlas Settings** on the top navigation bar and paste your MongoDB Atlas connection string. The platform validates the connection live.
3. **Offline Fallback:** If no URI is provided, the platform automatically stores data in `backend/app/data/hack_my_career_mongodb.json`.

---

## 🚀 How to Run the Project

### Option A: Modern Fullstack Web App (FastAPI + Acadia Web UI)
Starts the FastAPI backend serving the rich UI with animated gauges, What-If simulator, and Career Copilot:
```bash
# In project root:
python -m uvicorn backend.app.main:app --reload --port 8000
```
Open your browser and navigate to:
👉 **`http://localhost:8000`**

### Option B: Interactive Streamlit Dashboard
Launch the Python Data Science dashboard:
```bash
# In project root:
streamlit run streamlit_app.py --server.port 8501
```
Open your browser and navigate to:
👉 **`http://localhost:8501`**

---

## 📁 Repository Structure

```
HACK MY CAREER/
├── backend/
│   ├── app/
│   │   ├── data/
│   │   │   ├── jobs_dataset.json            # 120 curated industry job descriptions
│   │   │   ├── skill_taxonomy.json          # 70+ canonical skills with aliases
│   │   │   ├── learning_resources.json      # Curated tutorials, courses, and projects
│   │   │   ├── market_trends.json           # In-demand skill stats and salary curves
│   │   │   ├── sample_resumes.json          # Ready-to-test student profiles
│   │   │   └── hack_my_career_mongodb.json  # Local persistent document store fallback
│   │   ├── db/
│   │   │   └── mongodb.py                   # MongoDB Atlas cluster connection & manager
│   │   ├── ml/
│   │   │   ├── parser.py                    # PDF/DOCX extractor & ATS score calculator
│   │   │   ├── taxonomy.py                  # Alias normalizer & regex extractor
│   │   │   ├── matcher.py                   # 5-factor explainable scoring engine
│   │   │   ├── classifier.py                # Supervised Career Role Predictor (LR/RF)
│   │   │   ├── clusterer.py                 # K-Means Unsupervised Job Clustering (PCA 2D)
│   │   │   ├── simulator.py                 # What-If Dynamic Delta Simulator
│   │   │   ├── roadmap.py                   # Topological Learning Curriculum Generator
│   │   │   └── copilot.py                   # Grounded Career AI Assistant
│   │   ├── static/
│   │   │   ├── index.html                   # Acadia-style portal & dashboard
│   │   │   ├── styles.css                   # Custom responsive design & design tokens
│   │   │   └── app.js                       # Dynamic client-side controller
│   │   └── main.py                          # FastAPI server with all endpoints
├── streamlit_app.py                         # Streamlit dashboard
├── requirements.txt                         # Project dependencies
└── README.md                                # Documentation
```
