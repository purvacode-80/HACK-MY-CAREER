import os
from typing import Dict, Any, List

class CareerCopilot:
    def __init__(self):
        pass

    def answer_query(self, query: str, context: Dict[str, Any]) -> str:
        q = query.lower()
        candidate = context.get("candidate", {})
        target_job = context.get("target_job", {})
        match_info = context.get("match_info", {})

        skills = candidate.get("skills", [])
        ats_score = candidate.get("ats_score", 75)
        missing = match_info.get("missing_skills", [])
        matched = match_info.get("matched_skills", [])
        overall_score = match_info.get("overall_match_score", 80)
        job_title = target_job.get("title", "Target Role")
        company = target_job.get("company", "Target Company")

        # 1. Why is my score X%?
        if any(k in q for k in ["why is my score", "score explanation", "explain score", "breakdown"]):
            breakdown = match_info.get("breakdown", {})
            return (
                f"Your match score for **{job_title}** at **{company}** is **{overall_score}%**.\n\n"
                f"Here is why:\n"
                f"• **Semantic Context Match ({breakdown.get('semantic_similarity', 85)}%)**: Your resume closely mirrors the vocabulary and domain responsibilities of {job_title}.\n"
                f"• **Skill Match ({breakdown.get('skill_match', 70)}%)**: You matched {len(matched)} skills ({', '.join(matched[:4])}). However, you are missing {len(missing)} key requirements ({', '.join(missing[:4])}).\n"
                f"• **Experience Fit ({breakdown.get('experience_fit', 80)}%)**: Evaluated against the role seniority requirement.\n"
                f"• **ATS Resume Health ({ats_score}/100)**: Evaluated for section completeness, project depth, and contact details."
            )

        # 2. What should I learn first?
        if any(k in q for k in ["what should i learn", "priority", "learn first", "next step", "what to study"]):
            if missing:
                top_priority = missing[0]
                second_priority = missing[1] if len(missing) > 1 else "Cloud tools"
                return (
                    f"Based on your target of **{job_title}**, your #1 learning priority should be **{top_priority}**.\n\n"
                    f"**Why {top_priority}?** It is explicitly required by {company} and represents the largest gap reducing your match score.\n\n"
                    f"**Recommended Action**: Complete the foundational milestones in our Personalized Roadmap tab and build a mini-project showcasing {top_priority}."
                )
            return f"You currently meet all required core skills for {job_title}! We recommend deepening your knowledge in advanced cloud architecture or MLOps deployment."

        # 3. How to improve my resume / ATS score?
        if any(k in q for k in ["improve resume", "ats score", "ats", "resume tips", "better score"]):
            tips = []
            if len(candidate.get("projects", [])) < 3:
                tips.append("• **Add 1-2 quantified projects**: Include metrics like 'Improved inference latency by 35%' or 'Processed 50k+ records using SQL'.")
            if len(skills) < 8:
                tips.append("• **Expand Technical Skills**: Group your skills into Languages, Frameworks, Databases, and Developer Tools.")
            if missing:
                tips.append(f"• **Target High-Impact Keywords**: If you have worked with {', '.join(missing[:2])}, make sure they appear explicitly in your project bullets.")
            if not candidate.get("phone") or not candidate.get("email"):
                tips.append("• **Contact Headers**: Ensure phone number, institutional email, and GitHub/LinkedIn URLs are clearly formatted at the top.")

            if not tips:
                tips.append("• Your resume has solid fundamentals! Tailor your project bullet points to use strong action verbs (Architected, Engineered, Implemented) and quantify business impact.")

            return f"**Actionable Tips to Boost Your ATS & Job Fit Score**:\n" + "\n".join(tips)

        # 4. Default helpful career advice
        return (
            f"You are evaluating fit for **{job_title}** ({overall_score}% match). "
            f"You have strong core competencies in **{', '.join(skills[:3])}**. "
            f"To maximize your interview callback rate, simulate acquiring **{missing[0] if missing else 'production tooling'}** in our **What-If Simulator** and check your customized milestones in the **Learning Roadmap** tab."
        )

career_copilot = CareerCopilot()
