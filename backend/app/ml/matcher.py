import json
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity

from backend.app.ml.taxonomy import taxonomy_engine

JOBS_PATH = Path(__file__).parent.parent / "data" / "jobs_dataset.json"

class MatcherEngine:
    def __init__(self, jobs_path: Path = JOBS_PATH):
        self.jobs_path = jobs_path
        with open(jobs_path, "r", encoding="utf-8") as f:
            self.jobs: List[Dict[str, Any]] = json.load(f)
            
        # Build text corpus for fitting vectorizers
        self.job_texts = [f"{j['title']} {j['role']} {' '.join(j['required_skills'])} {' '.join(j['preferred_skills'])} {j['description']}" for j in self.jobs]
        
        # 1. Baseline TF-IDF Vectorizer
        self.tfidf_vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
            sublinear_tf=True,
            max_features=5000
        )
        self.tfidf_job_matrix = self.tfidf_vectorizer.fit_transform(self.job_texts)

        # 2. Advanced Dense Semantic Space (Latent Semantic Analysis via TruncatedSVD on TF-IDF)
        # In Data Science & Analytics, LSA maps high-dimensional sparse terms into dense semantic concept vectors
        n_components = min(64, self.tfidf_job_matrix.shape[1] - 1)
        self.svd = TruncatedSVD(n_components=n_components, random_state=42)
        self.dense_job_matrix = self.svd.fit_transform(self.tfidf_job_matrix)
        # Normalize dense vectors to unit norm for exact cosine similarity
        dense_norms = np.linalg.norm(self.dense_job_matrix, axis=1, keepdims=True)
        dense_norms[dense_norms == 0] = 1.0
        self.dense_job_matrix = self.dense_job_matrix / dense_norms

    def compute_similarity(self, resume_text: str, job_text: str) -> Dict[str, float]:
        """Computes both Baseline TF-IDF and Dense Semantic Cosine Similarity."""
        tfidf_pair = self.tfidf_vectorizer.transform([resume_text, job_text])
        baseline_sim = float(cosine_similarity(tfidf_pair[0:1], tfidf_pair[1:2])[0][0])
        
        dense_pair = self.svd.transform(tfidf_pair)
        norm_r = np.linalg.norm(dense_pair[0])
        norm_j = np.linalg.norm(dense_pair[1])
        if norm_r > 0 and norm_j > 0:
            semantic_sim = float(np.dot(dense_pair[0], dense_pair[1]) / (norm_r * norm_j))
        else:
            semantic_sim = baseline_sim

        return {
            "baseline_tfidf": round(max(0.0, min(1.0, baseline_sim)), 4),
            "dense_semantic": round(max(0.0, min(1.0, (semantic_sim + 1.0) / 2.0 if semantic_sim < 0 else semantic_sim)), 4)
        }

    def compute_skill_overlap(self, candidate_skills: List[str], required_skills: List[str], preferred_skills: List[str]) -> Dict[str, Any]:
        """Calculates exact matched, partial, and missing skills."""
        candidate_set = set(candidate_skills)
        req_set = set(required_skills)
        pref_set = set(preferred_skills)

        matched_req = sorted(list(candidate_set.intersection(req_set)))
        missing_req = sorted(list(req_set.difference(candidate_set)))
        
        matched_pref = sorted(list(candidate_set.intersection(pref_set)))
        missing_pref = sorted(list(pref_set.difference(candidate_set)))

        # Skill match score calculation
        total_req_count = max(1, len(req_set))
        req_score = (len(matched_req) / total_req_count) * 100
        
        pref_bonus = (len(matched_pref) / max(1, len(pref_set))) * 15 if pref_set else 0
        total_skill_score = min(100.0, round(req_score * 0.85 + pref_bonus, 1))

        return {
            "matched_skills": matched_req + matched_pref,
            "missing_skills": missing_req,
            "preferred_missing": missing_pref,
            "skill_match_percentage": total_skill_score
        }

    def calculate_experience_score(self, candidate_years: float, required_years: float) -> int:
        if candidate_years >= required_years:
            return 100
        diff = required_years - candidate_years
        if diff <= 1.0: return 85
        if diff <= 2.0: return 70
        return 50

    def calculate_explainable_match(self, candidate_profile: Dict[str, Any], job: Dict[str, Any]) -> Dict[str, Any]:
        """Calculates the 5-factor explainable match score."""
        resume_text = f"{candidate_profile.get('raw_text', '')} {' '.join(candidate_profile.get('skills', []))}"
        job_text = f"{job['title']} {job['role']} {' '.join(job['required_skills'])} {' '.join(job['preferred_skills'])} {job['description']}"

        # 1. Similarity
        sim_scores = self.compute_similarity(resume_text, job_text)
        semantic_score = sim_scores["dense_semantic"] * 100
        baseline_score = sim_scores["baseline_tfidf"] * 100

        # 2. Skill Gap
        skill_analysis = self.compute_skill_overlap(
            candidate_profile.get("skills", []),
            job.get("required_skills", []),
            job.get("preferred_skills", [])
        )
        skill_score = skill_analysis["skill_match_percentage"]

        # 3. Experience Fit
        candidate_exp = candidate_profile.get("experience_years", 1.0)
        job_exp = job.get("min_experience_years", 1)
        exp_score = self.calculate_experience_score(candidate_exp, job_exp)

        # 4. Education Fit
        edu_score = 95 if candidate_profile.get("education") else 80

        # 5. Project Relevance
        proj_count = len(candidate_profile.get("projects", []))
        proj_score = min(100, 70 + (proj_count * 10))

        # Composite Weighted Formula (Sum of weights = 1.00)
        # JobMatch = 0.40 * Semantic + 0.30 * Skill + 0.15 * Exp + 0.10 * Edu + 0.05 * Proj
        composite_score = round(
            0.40 * semantic_score +
            0.30 * skill_score +
            0.15 * exp_score +
            0.10 * edu_score +
            0.05 * proj_score,
            1
        )

        return {
            "job_id": job.get("id"),
            "job_title": job.get("title"),
            "company": job.get("company"),
            "location": job.get("location"),
            "role": job.get("role"),
            "salary_range": job.get("salary_range"),
            "overall_match_score": composite_score,
            "baseline_tfidf_score": round(baseline_score, 1),
            "dense_semantic_score": round(semantic_score, 1),
            "breakdown": {
                "semantic_similarity": round(semantic_score, 1),
                "skill_match": round(skill_score, 1),
                "experience_fit": exp_score,
                "education_fit": edu_score,
                "project_relevance": proj_score
            },
            "matched_skills": skill_analysis["matched_skills"],
            "missing_skills": skill_analysis["missing_skills"],
            "preferred_missing": skill_analysis["preferred_missing"]
        }

    def rank_jobs(self, candidate_profile: Dict[str, Any], top_k: int = 10, role_filter: str = None) -> List[Dict[str, Any]]:
        """Ranks all jobs for the candidate."""
        ranked = []
        for job in self.jobs:
            if role_filter and role_filter.lower() != "all" and role_filter.lower() not in job["role"].lower():
                continue
            scored = self.calculate_explainable_match(candidate_profile, job)
            ranked.append(scored)

        ranked.sort(key=lambda x: x["overall_match_score"], reverse=True)
        return ranked[:top_k]

matcher_engine = MatcherEngine()
