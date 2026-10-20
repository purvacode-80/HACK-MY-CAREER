import json
from pathlib import Path
from typing import Dict, Any, List

RESOURCES_PATH = Path(__file__).parent.parent / "data" / "learning_resources.json"

class RoadmapEngine:
    def __init__(self, resources_path: Path = RESOURCES_PATH):
        with open(resources_path, "r", encoding="utf-8") as f:
            self.resources: Dict[str, Any] = json.load(f)

        # Standard default sequence order based on difficulty
        self.difficulty_order = {"Beginner": 1, "Intermediate": 2, "Advanced": 3}

    def generate_roadmap(self, missing_skills: List[str], target_role: str = "Target Role") -> Dict[str, Any]:
        """Generates a structured, milestone-based curriculum for missing skills."""
        steps = []
        total_hours = 0

        # Sort missing skills: if resource exists, sort by difficulty and prerequisites
        def get_sort_key(skill_name: str):
            res = self.resources.get(skill_name)
            if res:
                return (self.difficulty_order.get(res.get("difficulty", "Intermediate"), 2), res.get("estimated_hours", 20))
            return (2, 20)

        ordered_skills = sorted(missing_skills, key=get_sort_key)

        for idx, skill in enumerate(ordered_skills, start=1):
            res = self.resources.get(skill)
            if res:
                est_hrs = res.get("estimated_hours", 20)
                diff = res.get("difficulty", "Intermediate")
                milestones = res.get("milestones", [f"Master fundamentals of {skill}", f"Build a practical component using {skill}"])
                tutorials = res.get("free_tutorials", [])
                project_idea = res.get("project_idea", f"Build a mini-project integrating {skill}.")
                prereqs = res.get("prerequisites", [])
                summary = res.get("summary", f"Learn and master {skill} for {target_role}.")
            else:
                est_hrs = 15
                diff = "Intermediate"
                milestones = [
                    f"Core syntax and architecture of {skill}",
                    f"Hands-on integration with your existing stack",
                    f"Unit testing and deployment best practices"
                ]
                tutorials = [
                    {"title": f"Official {skill} Documentation & Guides", "url": "https://devdocs.io/"},
                    {"title": f"{skill} Crash Course (freeCodeCamp)", "url": "https://www.youtube.com/results?search_query=" + skill.replace(" ", "+")}
                ]
                project_idea = f"Develop a capstone project utilizing {skill} for your technical portfolio."
                prereqs = ["General Programming"]
                summary = f"Essential technology required for modern {target_role} roles."

            total_hours += est_hrs
            steps.append({
                "step_number": idx,
                "skill": skill,
                "difficulty": diff,
                "estimated_hours": est_hrs,
                "summary": summary,
                "prerequisites": prereqs,
                "milestones": milestones,
                "tutorials": tutorials,
                "project_idea": project_idea
            })

        weeks_at_10hrs_per_week = round(total_hours / 10.0, 1)

        return {
            "target_role": target_role,
            "total_skills_to_learn": len(ordered_skills),
            "total_estimated_hours": total_hours,
            "estimated_completion_weeks": weeks_at_10hrs_per_week,
            "steps": steps
        }

roadmap_engine = RoadmapEngine()
