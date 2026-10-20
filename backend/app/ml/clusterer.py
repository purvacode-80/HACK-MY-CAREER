import json
import numpy as np
from pathlib import Path
from typing import Dict, Any, List
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score

from backend.app.ml.taxonomy import taxonomy_engine

JOBS_PATH = Path(__file__).parent.parent / "data" / "jobs_dataset.json"

class JobClusterer:
    def __init__(self, jobs_path: Path = JOBS_PATH, n_clusters: int = 5):
        self.n_clusters = n_clusters
        with open(jobs_path, "r", encoding="utf-8") as f:
            self.jobs = json.load(f)

        self.all_skills = taxonomy_engine.get_all_canonical_skills()
        self.skill_to_idx = {s: i for i, s in enumerate(self.all_skills)}

        # Build binary feature vectors
        X = []
        for job in self.jobs:
            vec = np.zeros(len(self.all_skills), dtype=np.float32)
            for s in job["required_skills"] + job["preferred_skills"]:
                if s in self.skill_to_idx:
                    vec[self.skill_to_idx[s]] = 1.0
            X.append(vec)
        self.X = np.array(X)

        # Fit K-Means
        self.kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        self.cluster_labels = self.kmeans.fit_predict(self.X)
        self.silhouette = float(silhouette_score(self.X, self.cluster_labels))

        # 2D PCA projection for interactive frontend visualization
        self.pca = PCA(n_components=2, random_state=42)
        self.pca_coords = self.pca.fit_transform(self.X)
        self.variance_explained = [round(float(v) * 100, 1) for v in self.pca.explained_variance_ratio_]

        # Name clusters by most representative skills
        self.cluster_names = {}
        for c_idx in range(n_clusters):
            centroid = self.kmeans.cluster_centers_[c_idx]
            top_skill_indices = np.argsort(centroid)[::-1][:3]
            top_skills = [self.all_skills[i] for i in top_skill_indices]
            self.cluster_names[c_idx] = " & ".join(top_skills)

    def get_cluster_points(self) -> List[Dict[str, Any]]:
        points = []
        for i, job in enumerate(self.jobs):
            c_id = int(self.cluster_labels[i])
            points.append({
                "job_id": job["id"],
                "title": job["title"],
                "role": job["role"],
                "company": job["company"],
                "cluster_id": c_id,
                "cluster_name": self.cluster_names[c_id],
                "x": round(float(self.pca_coords[i, 0]), 3),
                "y": round(float(self.pca_coords[i, 1]), 3)
            })
        return points

    def project_candidate(self, candidate_skills: List[str]) -> Dict[str, Any]:
        vec = np.zeros((1, len(self.all_skills)), dtype=np.float32)
        for s in candidate_skills:
            if s in self.skill_to_idx:
                vec[0, self.skill_to_idx[s]] = 1.0
        c_label = int(self.kmeans.predict(vec)[0])
        coord = self.pca.transform(vec)[0]
        return {
            "cluster_id": c_label,
            "cluster_name": self.cluster_names[c_label],
            "x": round(float(coord[0]), 3),
            "y": round(float(coord[1]), 3)
        }

job_clusterer = JobClusterer()
