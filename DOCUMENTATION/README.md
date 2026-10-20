# 📚 Hack My Career — Documentation Index

**Project:** Hack My Career — AI-Powered Career Intelligence Platform  
**Student:** Purva Waykole | VIT Pune, B.Tech IT  
**Subject:** Data Science and Analytics (5th Semester)

---

## 📄 Document List

| # | Document | Description |
|---|---|---|
| 1 | [01_PROJECT_OVERVIEW.md](./01_PROJECT_OVERVIEW.md) | What the project does, who it's for, directory structure, how to run |
| 2 | [02_DATA_SCIENCE_CONCEPTS.md](./02_DATA_SCIENCE_CONCEPTS.md) | All 17 DS/ML concepts explained with code references |
| 3 | [03_PROJECT_FLOW.md](./03_PROJECT_FLOW.md) | Step-by-step data pipeline from resume upload to recommendations |
| 4 | [04_ARCHITECTURE_AND_TECHNOLOGIES.md](./04_ARCHITECTURE_AND_TECHNOLOGIES.md) | 3-tier architecture, component diagrams, tech stack, DB schema |
| 5 | [05_MODEL_EVALUATION.md](./05_MODEL_EVALUATION.md) | ML model metrics, performance evaluation, course topic mapping |

---

## 🧠 Quick Reference — Data Science Concepts Used

| Concept | Category | File |
|---|---|---|
| Document Parsing (PDF, DOCX) | NLP | `backend/app/ml/parser.py` |
| Regular Expressions (Email, Phone, URL) | NLP | `backend/app/ml/parser.py` |
| Named Entity Recognition (Skill extraction) | NLP | `backend/app/ml/taxonomy.py` |
| TF-IDF Vectorization | NLP / ML | `backend/app/ml/matcher.py` |
| Latent Semantic Analysis (TruncatedSVD) | Dimensionality Reduction | `backend/app/ml/matcher.py` |
| Cosine Similarity | Mathematical Metric | `backend/app/ml/matcher.py` |
| 5-Factor Composite Scoring (Explainable AI) | ML + Decision Logic | `backend/app/ml/matcher.py` |
| K-Means Clustering (k=5) | Unsupervised ML | `backend/app/ml/clusterer.py` |
| Silhouette Score (Cluster Validation) | Model Evaluation | `backend/app/ml/clusterer.py` |
| PCA — 2D Visualisation | Dimensionality Reduction | `backend/app/ml/clusterer.py` |
| Logistic Regression (Career Classifier) | Supervised ML | `backend/app/ml/classifier.py` |
| Random Forest (Feature Importances) | Supervised ML | `backend/app/ml/classifier.py` |
| ATS Resume Scoring Rubric | Rule-based Scoring | `backend/app/ml/parser.py` |
| Counterfactual / What-If Analysis | Explainable AI | `backend/app/ml/simulator.py` |
| Multi-hot Binary Feature Encoding | Feature Engineering | `classifier.py`, `clusterer.py` |
| NoSQL Document Database (MongoDB Atlas) | Database Engineering | `backend/app/db/mongodb.py` |
| REST API Architecture (FastAPI) | Software Engineering | `backend/app/main.py` |

---

## 🚀 Start Here for Presentation

1. **Start with** `01_PROJECT_OVERVIEW.md` — explains the big picture
2. **Walk through** `03_PROJECT_FLOW.md` — follow the data pipeline step-by-step
3. **Deep dive into** `02_DATA_SCIENCE_CONCEPTS.md` — explain each algorithm when asked
4. **Show the architecture** from `04_ARCHITECTURE_AND_TECHNOLOGIES.md`
5. **Back up with metrics** from `05_MODEL_EVALUATION.md`

---

## 🌐 Key URLs (when server is running)

| URL | Purpose |
|---|---|
| `http://127.0.0.1:8000` | Main application |
| `http://127.0.0.1:8000/docs` | Interactive API Explorer (Swagger UI) |
| `http://127.0.0.1:8000/api/health` | System health + model metrics |
| `http://127.0.0.1:8000/redoc` | API Reference Documentation |
