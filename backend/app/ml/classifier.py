import json
import numpy as np
from pathlib import Path
from typing import Dict, Any, List
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import MultiLabelBinarizer

from backend.app.ml.taxonomy import taxonomy_engine

JOBS_PATH = Path(__file__).parent.parent / "data" / "jobs_dataset.json"

class CareerClassifier:
    def __init__(self, jobs_path: Path = JOBS_PATH):
        with open(jobs_path, "r", encoding="utf-8") as f:
            self.jobs = json.load(f)

        # Train a career classifier that predicts probability distribution across roles
        # X: Multi-hot binary skill vector based on canonical taxonomy
        # y: Target Career Role
        self.all_skills = taxonomy_engine.get_all_canonical_skills()
        self.skill_to_idx = {s: i for i, s in enumerate(self.all_skills)}
        
        X = []
        y = []
        for job in self.jobs:
            role = job["role"]
            req = job["required_skills"]
            pref = job["preferred_skills"]
            
            # Combine skills to create training samples
            vec = self._skills_to_vector(req + pref)
            X.append(vec)
            y.append(role)

        X = np.array(X)
        y = np.array(y)

        # Train Logistic Regression with probability estimates
        self.model = LogisticRegression(max_iter=500, random_state=42)
        self.model.fit(X, y)
        self.classes_ = self.model.classes_

        # Also fit Random Forest to compute feature importances
        self.rf = RandomForestClassifier(n_estimators=100, random_state=42)
        self.rf.fit(X, y)

    def _skills_to_vector(self, skills: List[str]) -> np.ndarray:
        vec = np.zeros(len(self.all_skills), dtype=np.float32)
        for s in skills:
            if s in self.skill_to_idx:
                vec[self.skill_to_idx[s]] = 1.0
        return vec

    def predict_career_fit(self, candidate_skills: List[str]) -> List[Dict[str, Any]]:
        vec = self._skills_to_vector(candidate_skills).reshape(1, -1)
        probs = self.model.predict_proba(vec)[0]
        
        results = []
        for role, prob in zip(self.classes_, probs):
            percentage = round(float(prob) * 100, 1)
            results.append({
                "role": role,
                "fit_probability": percentage,
                "fit_level": "High" if percentage > 30 else ("Medium" if percentage > 15 else "Low")
            })

        results.sort(key=lambda x: x["fit_probability"], reverse=True)
        return results

    def get_top_features_for_role(self, role: str, top_n: int = 5) -> List[str]:
        if role not in self.classes_:
            return []
        idx = list(self.classes_).index(role)
        coefs = self.model.coef_[idx]
        top_indices = np.argsort(coefs)[::-1][:top_n]
        return [self.all_skills[i] for i in top_indices if coefs[i] > 0]

career_classifier = CareerClassifier()
