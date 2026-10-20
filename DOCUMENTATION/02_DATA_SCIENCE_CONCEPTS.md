# 🔬 Data Science Concepts — Explained in Detail

> This document explains every Data Science and Machine Learning concept used in **Hack My Career**, with clear definitions, the exact implementation in our code, and why it was chosen.

---

## 1. Natural Language Processing (NLP) — Resume Text Extraction

### What is NLP?
Natural Language Processing is a branch of AI that enables computers to understand, interpret, and manipulate human language. In our project, NLP is used to extract structured information from raw resume documents.

### What we do in the code (`parser.py`)

**Step 1 — Document Parsing:**
```
PDF  → pdfplumber library → raw text string
DOCX → zipfile + XML parsing (word/document.xml) → raw text string
PPTX → zipfile + XML parsing (ppt/slides/*.xml) → raw text string
TXT  → direct UTF-8 decode
```

**Step 2 — Regex-based Information Extraction:**
We use **Regular Expressions (RegEx)**, a pattern-matching NLP technique, to extract:

| Field | RegEx Pattern |
|---|---|
| Email | `[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+` |
| Phone | `(?:\+91[\s-]?)?[6-9]\d{4}[\s-]?\d{5}` (Indian format) |
| Location | `[City], [State], India` geographic pattern |
| LinkedIn URL | `linkedin\.com/in/[\w-]+` |
| GitHub URL | `github\.com/[\w-]+` |
| Projects | Numbered bullet patterns `1. Title: Description` |

**Why RegEx?**
Regular expressions are computationally lightweight, deterministic (same input = same output), and perfect for extracting structured patterns like emails, phone numbers, and URLs from unstructured text.

---

## 2. Skill Taxonomy & Entity Recognition (`taxonomy.py`)

### What is a Taxonomy?
A **taxonomy** is a hierarchical classification system. In our project, we built a canonical taxonomy of 80+ technical skills organized by domain:

| Domain | Example Skills |
|---|---|
| Programming Languages | Python, Java, C++, JavaScript, SQL, R |
| Machine Learning | Scikit-Learn, TensorFlow, PyTorch, Deep Learning, NLP |
| Databases | MySQL, PostgreSQL, MongoDB, Redis |
| DevOps / Cloud | Docker, Linux, Git, GitHub Actions |
| Data Science | Pandas, NumPy, Matplotlib, Power BI |

### How Skill Extraction Works
We use **exact keyword matching** with canonical normalization:
```python
# "python", "Python 3", "Python Programming" → all normalize to "Python"
```
This is called **Named Entity Recognition (NER)** — identifying specific real-world entities (skill names) from free text.

**Why a custom taxonomy instead of a pre-trained NER model?**
- No internet dependency; works fully offline
- 100% precision for domain-specific technical skills
- No false positives (e.g., "Java" the island mistaken for "Java" the language)

---

## 3. TF-IDF Vectorization (`matcher.py`)

### What is TF-IDF?
**Term Frequency–Inverse Document Frequency** is a numerical statistic that reflects how important a word is to a document in a collection.

```
TF(t, d)  = (number of times term t appears in document d) / (total terms in d)
IDF(t)    = log(total documents / documents containing t)
TF-IDF(t, d) = TF(t, d) × IDF(t)
```

### How we use it
Both the candidate's resume and each job description are converted into TF-IDF vectors with:
- **Stop words removed** (`"the"`, `"is"`, `"and"` are removed — they carry no meaning)
- **N-grams (1,2)** — captures both single words (`"machine learning"` → `"machine"`, `"learning"`, `"machine_learning"`)
- **Sublinear TF scaling** — `log(1 + TF)` to reduce dominance of highly repeated terms
- **Max 5,000 features** — controls dimensionality

**Result:** Each resume and job description becomes a sparse vector of 5,000 dimensions.

---

## 4. Latent Semantic Analysis (LSA) — Dense Semantic Matching (`matcher.py`)

### The Problem with TF-IDF Alone
TF-IDF only matches **exact words**. "Machine Learning" and "Deep Learning" are treated as completely different — but semantically they are very close career concepts.

### What is LSA?
**Latent Semantic Analysis** uses **Singular Value Decomposition (SVD)** to discover hidden (latent) semantic concepts in text. It maps the high-dimensional sparse TF-IDF space into a dense, lower-dimensional **semantic concept space**.

```
TF-IDF Matrix (n_documents × 5000 terms)
          ↓ TruncatedSVD (n_components = 64)
Dense Semantic Matrix (n_documents × 64 concepts)
```

Each of the 64 dimensions captures a "concept" (e.g., Concept 3 might correlate strongly with "data engineering" — Python, SQL, ETL, Spark — even if those words don't all appear in the same document).

### Implementation in our code
```python
self.svd = TruncatedSVD(n_components=64, random_state=42)
self.dense_job_matrix = self.svd.fit_transform(self.tfidf_job_matrix)
```

**Why TruncatedSVD and not full SVD?**  
Full SVD is O(n³). For sparse matrices (TF-IDF is very sparse), TruncatedSVD computes only the top k singular values — much faster and sufficient.

---

## 5. Cosine Similarity — Computing Match Score (`matcher.py`)

### What is Cosine Similarity?
Cosine similarity measures the **angle** between two vectors, not their magnitude. This is crucial for text — a 2-page resume and a 1-page resume should be comparable even though one has more words.

```
cosine_similarity(A, B) = (A · B) / (||A|| × ||B||)

Range: -1 to 1
1.0 = identical direction (perfect match)
0.0 = orthogonal (no relationship)
-1.0 = opposite directions
```

### Two-layer Similarity in our project

| Layer | Technique | Weight in Final Score |
|---|---|---|
| **Baseline** | TF-IDF cosine similarity | Shown for transparency |
| **Semantic** | LSA dense cosine similarity | **40% of composite score** |

The semantic similarity captures **conceptual closeness** while the TF-IDF baseline captures **literal keyword overlap**.

---

## 6. The 5-Factor Explainable Composite Scoring Formula (`matcher.py`)

### Formula
```
JobMatch Score = (0.40 × Semantic_Similarity)
              + (0.30 × Skill_Match_Percentage)
              + (0.15 × Experience_Fit)
              + (0.10 × Education_Fit)
              + (0.05 × Project_Relevance)
```

### Why "Explainable"?
Traditional "black-box" ML models give a score with no explanation. Our formula is **transparent** — the user sees exactly which of the 5 factors contributed to their score and by how much.

| Factor | Weight | How It's Computed |
|---|---|---|
| Semantic Similarity | 40% | LSA cosine similarity × 100 |
| Skill Match | 30% | `(matched_required / total_required) × 85 + preferred_bonus × 15` |
| Experience Fit | 15% | Piecewise linear: 100 if years ≥ required, penalised otherwise |
| Education Fit | 10% | 95 if education detected, 80 if not |
| Project Relevance | 5% | `70 + (project_count × 10)`, capped at 100 |

---

## 7. K-Means Clustering — Job Family Discovery (`clusterer.py`)

### What is K-Means Clustering?
K-Means is an **unsupervised machine learning** algorithm that partitions n observations into k clusters, where each observation belongs to the cluster with the nearest centroid (mean).

### Algorithm Steps
```
1. Initialize k=5 cluster centroids randomly
2. Assign each job to nearest centroid (by Euclidean distance)
3. Recompute centroids as mean of assigned jobs
4. Repeat steps 2-3 until convergence
```

### What we cluster
Each job is represented as a **binary skill vector**:
```
[Python=1, SQL=1, Docker=0, React=1, TensorFlow=0, ...]
(One dimension per canonical skill — 80+ dimensions)
```

### Result
5 natural job clusters are discovered, e.g.:
- Cluster 1: "Python & Machine Learning" (Data Science roles)
- Cluster 2: "React & JavaScript" (Frontend roles)
- Cluster 3: "Docker & Linux" (DevOps roles)
- Cluster 4: "SQL & Power BI" (Data Analyst roles)
- Cluster 5: "PyTorch & Deep Learning" (AI/Research roles)

### Silhouette Score — Validating Cluster Quality
```python
silhouette_score(X, cluster_labels)
# Range: -1 to 1. Higher = better-separated clusters.
```
This is reported in the API health endpoint — our teacher can verify cluster quality.

---

## 8. PCA — 2D Visualisation of the Cluster Map (`clusterer.py`)

### What is PCA?
**Principal Component Analysis** is a dimensionality reduction technique that projects high-dimensional data into lower dimensions while preserving maximum variance.

```
Binary Skill Vectors (80+ dimensions)
          ↓ PCA(n_components=2)
2D scatter plot coordinates (x, y)
```

### Why do we need it?
You cannot plot 80-dimensional data on a screen. PCA finds the **two directions of maximum variance** in the data and projects everything onto them, giving us a 2D map where nearby jobs are semantically similar.

```python
self.pca = PCA(n_components=2, random_state=42)
self.pca_coords = self.pca.fit_transform(self.X)
self.variance_explained = self.pca.explained_variance_ratio_
# → [35.2%, 18.7%] means the 2D plot captures 53.9% of original variance
```

---

## 9. Logistic Regression — Career Role Classifier (`classifier.py`)

### What is Logistic Regression?
Logistic Regression is a **supervised classification algorithm** that predicts the probability that an input belongs to each class. Unlike its name suggests, it's a classifier, not a regressor.

```
P(role = "Data Scientist" | skills) = sigmoid(w · skills + b)
```

### How we train it
- **Input (X):** Binary skill vector for each job (multi-hot encoding)
- **Target (y):** The job's role label (e.g., "Data Scientist", "Full Stack Developer")
- **Training data:** All 50+ jobs in our dataset

### Multi-class Output
The model predicts a **probability distribution** across all career roles:
```
{
  "Data Scientist": 67.3%,
  "Data Engineer": 18.2%,
  "Full Stack Developer": 8.4%,
  "AI Engineer": 4.8%,
  ...
}
```

This tells the candidate: *"Based on your current skills, you're most likely fit for Data Science roles."*

### Random Forest — Feature Importance
We also train a **Random Forest Classifier** alongside Logistic Regression to compute feature importances — identifying which skills are most predictive of each career role. These importances power the "Top Skills Required" display.

---

## 10. ATS Score — Resume Completeness Scoring (`parser.py`)

### What is an ATS?
**Applicant Tracking System** — software used by companies to filter resumes. Our ATS score measures how "ATS-friendly" a resume is.

### Our Scoring Rubric (Max: 100)

| Section | Points Awarded |
|---|---|
| Has email | +8 |
| Has phone or LinkedIn/GitHub | +7 |
| Has 10+ skills | +35 |
| Has 6-9 skills | +25 |
| Has 3-5 skills | +15 |
| Education detected | +15 |
| 2+ projects detected | +20 |
| 1 project detected | +12 |
| Resume length 500–8000 chars | +15 |

This is a **deterministic, weighted scoring rubric** — a rule-based approach grounded in industry ATS best practices.

---

## 11. What-If Simulator — Counterfactual Analysis (`simulator.py`)

### What is Counterfactual Analysis?
Counterfactual Analysis asks: *"What would have happened if conditions were different?"*

In our platform: *"What would my job match score be if I also knew Docker and AWS?"*

### How it works
```python
# 1. Compute original match score
original_score = matcher.calculate_explainable_match(candidate, job)

# 2. Create hypothetical candidate profile
simulated_profile = candidate.copy()
simulated_profile["skills"] += added_skills  # Add the new skills

# 3. Compute new score
simulated_score = matcher.calculate_explainable_match(simulated_profile, job)

# 4. Report the delta
score_delta = simulated_score - original_score
```

**Output Example:**
> "Acquiring Docker and AWS increases your match from 62% to 78% (+16%). These skills satisfy 2 of the 3 missing required skills."

---

## 12. MongoDB Atlas — Cloud Database (`db/mongodb.py`)

### What is MongoDB?
MongoDB is a **NoSQL document database** that stores data as flexible JSON-like documents (called BSON — Binary JSON). Unlike SQL databases with rigid table schemas, MongoDB handles nested structures naturally (perfect for variable-length resume data).

### Why MongoDB Atlas for this project?
| Requirement | MongoDB Atlas Solution |
|---|---|
| Store user accounts | `users` collection |
| Store uploaded resumes | `resumes` collection with nested JSON profile |
| Variable resume structure | Schema-less documents — no columns to predefine |
| Cloud access from anywhere | Hosted on MongoDB Atlas (cloud) |
| Secure authentication | Password hashing with SHA-256 |

### Key Operations in our code
```python
db["users"].insert_one(user_doc)       # Store new user
db["users"].find_one({"email": ...})   # Find user by email
db["resumes"].insert_one(resume_doc)   # Save uploaded resume
db["resumes"].find({"user_id": ...})   # Get user's resume history
db["resumes"].delete_one({"resume_id": ...})  # Delete resume
```

---

## 13. REST API Architecture — FastAPI (`main.py`)

### What is a REST API?
**Representational State Transfer (REST)** is an architectural style for building web services. Our FastAPI backend exposes endpoints:

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/auth/signup` | POST | Register new user |
| `/api/auth/login` | POST | Authenticate user |
| `/api/resume/upload` | POST | Upload & parse resume |
| `/api/jobs/match` | POST | Run job matching |
| `/api/jobs/match-custom` | POST | Match against custom JD |
| `/api/simulate/what-if` | POST | Run What-If simulation |
| `/api/career/recommendations` | POST | Career role classification |
| `/api/analytics/market` | GET | Market trends & cluster data |
| `/api/learning/roadmap` | POST | Generate learning roadmap |

### Data Validation — Pydantic Models
FastAPI uses **Pydantic** for automatic JSON schema validation. If the frontend sends wrong data types, the API returns a clear 422 error rather than crashing silently.

---

## Summary Table — All Concepts at a Glance

| # | Concept | Category | Module |
|---|---|---|---|
| 1 | Document Parsing (pdfplumber, XML) | NLP | `parser.py` |
| 2 | Regular Expressions (RegEx) | NLP | `parser.py` |
| 3 | Named Entity Recognition (Skill Extraction) | NLP | `taxonomy.py` |
| 4 | TF-IDF Vectorization | NLP / ML | `matcher.py` |
| 5 | Latent Semantic Analysis (LSA / SVD) | Dimensionality Reduction | `matcher.py` |
| 6 | Cosine Similarity | Mathematical Metric | `matcher.py` |
| 7 | 5-Factor Composite Scoring | Explainable AI | `matcher.py` |
| 8 | K-Means Clustering | Unsupervised ML | `clusterer.py` |
| 9 | Silhouette Score | Cluster Validation | `clusterer.py` |
| 10 | PCA (2D Projection) | Dimensionality Reduction | `clusterer.py` |
| 11 | Logistic Regression | Supervised ML | `classifier.py` |
| 12 | Random Forest (Feature Importances) | Supervised ML | `classifier.py` |
| 13 | ATS Scoring Rubric | Rule-Based Scoring | `parser.py` |
| 14 | Counterfactual / What-If Analysis | Explainable AI | `simulator.py` |
| 15 | NoSQL Document Database | Database Engineering | `mongodb.py` |
| 16 | REST API Design | Software Engineering | `main.py` |
| 17 | Multi-hot Binary Encoding | Feature Engineering | `classifier.py`, `clusterer.py` |
