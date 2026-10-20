from typing import Dict, Any, List
from backend.app.ml.matcher import matcher_engine

class WhatIfSimulator:
    def __init__(self):
        pass

    def simulate(self, candidate_profile: Dict[str, Any], target_job_id: str, added_skills: List[str]) -> Dict[str, Any]:
        # Find target job
        target_job = next((j for j in matcher_engine.jobs if j["id"] == target_job_id), matcher_engine.jobs[0])

        # Original match
        orig_match = matcher_engine.calculate_explainable_match(candidate_profile, target_job)

        # Create simulated profile with added skills
        current_skills = set(candidate_profile.get("skills", []))
        simulated_skills = list(current_skills.union(set(added_skills)))

        simulated_profile = dict(candidate_profile)
        simulated_profile["skills"] = simulated_skills
        simulated_profile["raw_text"] = candidate_profile.get("raw_text", "") + " " + " ".join(added_skills)

        # Recalculate match
        sim_match = matcher_engine.calculate_explainable_match(simulated_profile, target_job)

        score_delta = round(sim_match["overall_match_score"] - orig_match["overall_match_score"], 1)

        # Impact explanation
        satisfied = [s for s in added_skills if s in target_job.get("required_skills", []) or s in target_job.get("preferred_skills", [])]
        
        return {
            "target_job_id": target_job["id"],
            "target_job_title": target_job["title"],
            "target_company": target_job["company"],
            "original_score": orig_match["overall_match_score"],
            "simulated_score": sim_match["overall_match_score"],
            "score_delta": score_delta,
            "added_skills": added_skills,
            "newly_satisfied_skills": satisfied,
            "original_missing": orig_match["missing_skills"],
            "simulated_missing": sim_match["missing_skills"],
            "original_breakdown": orig_match["breakdown"],
            "simulated_breakdown": sim_match["breakdown"],
            "summary": f"Acquiring {', '.join(satisfied) if satisfied else 'these skills'} increases your match from {orig_match['overall_match_score']}% to {sim_match['overall_match_score']}% (+{score_delta}%)."
        }

what_if_simulator = WhatIfSimulator()
