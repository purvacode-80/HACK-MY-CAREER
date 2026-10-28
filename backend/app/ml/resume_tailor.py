import os
import random
from typing import Dict, Any, List

class AIResumeTailor:
    """
    Intelligent Resume Bullet Rewriter & Tailoring Engine.
    Generates role-tailored STAR/Google XYZ-format bullet points
    (Accomplished [X] as measured by [Y], by doing [Z]) targeting critical missing skills
    and employer keywords for higher ATS pass rates.
    """

    ROLE_ACTION_VERBS = {
        "Data Scientist": ["Formulated", "Engineered", "Optimized", "Benchmarked", "Trained", "Forecasted", "Extracted"],
        "Machine Learning Engineer": ["Architected", "Deployed", "Containerized", "Fine-tuned", "Scaled", "Integrated", "Inferred"],
        "Data Analyst": ["Analyzed", "Visualized", "Synthesized", "Automated", "Modeled", "Audited", "Consolidated"],
        "Full Stack Developer": ["Developed", "Engineered", "Refactored", "Spearheaded", "Implemented", "Secured", "Shipped"],
        "DevOps Engineer": ["Automated", "Orchestrated", "Containerized", "Streamlined", "Monitored", "Provisioned", "Hardened"],
        "Backend Engineer": ["Engineered", "Architected", "Accelerated", "Optimized", "Integrated", "Scaled", "Designed"]
    }

    SKILL_TEMPLATES = {
        "Python": "Developed modular Python microservices utilizing asynchronous concurrency, speeding up data ingestion throughput by {pct}%.",
        "SQL": "Engineered complex SQL analytical queries with window functions and indexing, cutting database query response times by {pct}%.",
        "Machine Learning": "Formulated supervised machine learning models with automated cross-validation, improving prediction accuracy to {metric}%.",
        "Scikit-Learn": "Built and evaluated Scikit-Learn classification pipelines with hyperparameter tuning, reducing false discovery rates by {pct}%.",
        "PyTorch": "Trained and evaluated deep neural networks using PyTorch with GPU acceleration, achieving a top-1 test accuracy of {metric}%.",
        "TensorFlow": "Deployed production TensorFlow deep learning pipelines with optimized TensorRT inference, lowering inference latency to <{ms}ms.",
        "Pandas": "Architected automated data cleaning and feature engineering pipelines using Pandas, processing over {records} records daily.",
        "NumPy": "Vectorized scientific computation workflows with NumPy array operations, achieving a {x_factor}x speedup over legacy loops.",
        "FastAPI": "Built resilient RESTful APIs using FastAPI and Pydantic validation, maintaining sub-{ms}ms p99 latency across {users} concurrent requests.",
        "Docker": "Containerized multi-tier applications using Docker and Docker Compose, reducing environment configuration and onboarding time by {pct}%.",
        "Kubernetes": "Orchestrated container clusters with Kubernetes and automated horizontal pod autoscaling, sustaining 99.9% application uptime.",
        "AWS": "Architected cloud infrastructure on AWS (EC2, S3, RDS), optimizing resource provisioning to cut infrastructure overhead by {pct}%.",
        "Git": "Maintained collaborative version control workflows with Git and GitHub PR reviews, improving development sprint velocity by {pct}%.",
        "Tableau": "Designed interactive executive Tableau dashboards tracking operational KPIs, driving data-informed business decisions.",
        "Power BI": "Consolidated disparate data sources into enterprise Power BI reports, automating weekly executive reporting and saving {hours} hours weekly.",
        "NLP": "Built end-to-end NLP pipelines using transformer embeddings and sentiment classification, achieving an F1-score of {metric}.",
        "Deep Learning": "Designed convolutional and recurrent deep learning architectures, improving anomaly detection precision by {pct}%.",
        "MongoDB": "Modeled flexible NoSQL document schemas in MongoDB Atlas with sharded collections, handling high-volume unstructured data streams."
    }

    def tailor_resume_bullets(
        self,
        job_title: str,
        company: str,
        target_role: str,
        required_skills: List[str],
        missing_skills: List[str],
        candidate_skills: List[str]
    ) -> Dict[str, Any]:
        """
        Generates role-tailored STAR bullet points, action verbs, and ATS keyword tips.
        """
        verbs = self.ROLE_ACTION_VERBS.get(target_role, self.ROLE_ACTION_VERBS["Data Scientist"])
        
        # Pick 3-4 focus skills (prioritizing missing skills to bridge the gap, then required skills)
        focus_skills = []
        for s in missing_skills:
            if s not in focus_skills:
                focus_skills.append(s)
            if len(focus_skills) >= 3:
                break
                
        for s in required_skills:
            if s not in focus_skills:
                focus_skills.append(s)
            if len(focus_skills) >= 4:
                break

        if not focus_skills:
            focus_skills = ["Python", "Machine Learning", "SQL", "Docker"]

        bullets = []
        for sk in focus_skills:
            bullet = self._generate_bullet(sk, target_role, company)
            bullets.append({
                "skill": sk,
                "bullet": bullet,
                "is_gap_skill": sk in missing_skills,
                "format": "Google XYZ / STAR Standard"
            })

        # Calculate estimated ATS uplift
        uplift_percent = min(22.0, max(6.0, len(missing_skills) * 3.5))

        return {
            "status": "success",
            "job_title": job_title,
            "company": company,
            "target_role": target_role,
            "generated_bullets": bullets,
            "recommended_action_verbs": verbs,
            "top_resume_keywords": required_skills[:8],
            "projected_ats_uplift": f"+{round(uplift_percent, 1)}%",
            "optimization_advice": f"Incorporate these tailored bullets under your projects section for {company} to directly address the ATS screening filters."
        }

    def _generate_bullet(self, skill: str, role: str, company: str) -> str:
        # Check template
        template = self.SKILL_TEMPLATES.get(skill)
        if not template:
            # Generic template
            template = "Leveraged {skill} and engineering best practices to design high-throughput modules, improving operational efficiency by {pct}%."

        pct = random.randint(22, 45)
        metric = round(random.uniform(88.0, 96.5), 1)
        ms = random.choice([45, 80, 110, 140])
        records = random.choice(["50,000+", "100,000+", "500,000+"])
        x_factor = random.choice(["3.5", "4.2", "5.0"])
        users = random.choice(["1,000+", "5,000+"])
        hours = random.choice([6, 8, 12])

        text = template.format(
            skill=skill,
            pct=pct,
            metric=metric,
            ms=ms,
            records=records,
            x_factor=x_factor,
            users=users,
            hours=hours
        )
        return text

resume_tailor = AIResumeTailor()
