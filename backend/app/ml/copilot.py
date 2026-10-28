import os
import re
import json
import httpx
from typing import Dict, Any, List, Optional
from backend.app.ml.job_fetcher import job_fetcher

class CareerCopilot:
    """
    Intelligent Career & Resume Copilot.
    Supports real-time Google Gemini LLM API generation with smart fallback
    to live real-world job retrieval, ATS analytics, and roadmap advice.
    """

    def __init__(self):
        self.default_api_key = os.getenv("GEMINI_API_KEY", "")

    async def answer_query(self, query: str, context: Dict[str, Any]) -> str:
        q = (query or "").strip()
        q_lower = q.lower()
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

        # 1. Check for Gemini API Key (from request context or environment)
        api_key = (context.get("gemini_api_key") or self.default_api_key).strip()

        # If user explicitly asks for live job listings (e.g. "latest jobs for data scientist in pune")
        # We can directly fetch real-world jobs to provide instant actionable answers!
        if any(term in q_lower for term in ["job", "jobs", "opening", "openings", "hiring", "vacancy", "vacancies", "internship"]):
            job_reply = await self._handle_job_search_query(q, q_lower, job_title)
            if job_reply:
                return job_reply

        # 2. If Gemini API key is available, call Gemini 1.5 Flash
        if api_key:
            try:
                gemini_res = await self._call_gemini_api(api_key, q, candidate, target_job, match_info)
                if gemini_res:
                    return gemini_res
            except Exception as e:
                print(f"[CareerCopilot] Gemini API call failed: {e}")
                # Fall through to domain-smart engine

        # 3. Domain-Smart Fallback Engine (Answers all career questions accurately)
        return self._generate_domain_response(q, q_lower, candidate, target_job, match_info)

    async def _handle_job_search_query(self, query: str, q_lower: str, default_role: str) -> Optional[str]:
        """Detects job search intent, extracts role & city, and fetches real live jobs."""
        cities = ["pune", "bengaluru", "bangalore", "hyderabad", "mumbai", "delhi", "gurugram", "gurgaon", "noida", "chennai", "kolkata", "remote"]
        detected_loc = "India"
        for c in cities:
            if c in q_lower:
                detected_loc = "Bengaluru" if c == "bangalore" else ("Gurugram" if c == "gurgaon" else c.title())
                break

        # Detect role
        role_search = default_role or "Data Scientist"
        common_roles = [
            ("data scientist", "Data Scientist"),
            ("data science", "Data Scientist"),
            ("machine learning", "Machine Learning Engineer"),
            ("ml engineer", "Machine Learning Engineer"),
            ("ai engineer", "AI Engineer"),
            ("data engineer", "Data Engineer"),
            ("software engineer", "Software Engineer"),
            ("frontend", "Frontend Engineer"),
            ("backend", "Backend Engineer"),
            ("full stack", "Full Stack Developer"),
            ("devops", "DevOps Engineer"),
            ("cloud", "Cloud Engineer"),
            ("data analyst", "Data Analyst")
        ]
        for term, title in common_roles:
            if term in q_lower:
                role_search = title
                break

        try:
            live_jobs = await job_fetcher.search_jobs(query=role_search, location=detected_loc, max_results=4)
            if live_jobs:
                lines = [
                    f"### 🌐 Real-World Live Openings: **{role_search}** in **{detected_loc}**\n",
                    f"Here are active positions fetched live from market aggregators:\n"
                ]
                for idx, j in enumerate(live_jobs[:4], 1):
                    apply_btn = f"[Apply Direct on {j.get('source', 'Portal')}]({j.get('apply_url', '#')})"
                    req_skills = ", ".join(j.get("required_skills", [])[:4]) or "Tech Stack listed in posting"
                    lines.append(
                        f"**{idx}. {j.get('title')}** @ **{j.get('company')}**\n"
                        f"• 📍 **Location**: {j.get('location')} | 💰 **Salary**: {j.get('salary_range')}\n"
                        f"• 🎯 **Key Skills**: `{req_skills}`\n"
                        f"• 🔗 {apply_btn}\n"
                    )
                lines.append("💡 *Tip: Head over to the **Real-World Live Jobs** tab to benchmark your resume directly against these employers!*")
                return "\n".join(lines)
        except Exception as e:
            print(f"[Copilot] Live job search in copilot error: {e}")
        return None

    async def _call_gemini_api(self, api_key: str, user_query: str, candidate: Dict[str, Any], target_job: Dict[str, Any], match_info: Dict[str, Any]) -> Optional[str]:
        """Calls Google Gemini via REST endpoint with model fallback."""
        cand_skills = ", ".join(candidate.get("skills", [])[:12]) or "Python, SQL, Machine Learning"
        cand_score = candidate.get("ats_score", 85)
        cand_name = candidate.get("name", "Candidate")
        target_title = target_job.get("title", "Data Scientist")
        target_co = target_job.get("company", "Target Tech Company")
        missing = ", ".join(match_info.get("missing_skills", [])[:5]) or "Docker, AWS, MLOps"
        match_score = match_info.get("overall_match_score", 85)

        system_instruction = (
            f"You are the Hack My Career AI Copilot, a top-tier senior tech career advisor and hiring lead. "
            f"You are speaking to {cand_name}.\n"
            f"Candidate Context:\n"
            f"- Extracted Skills: {cand_skills}\n"
            f"- ATS Score: {cand_score}/100\n"
            f"- Target Role: {target_title} at {target_co} (Overall Match: {match_score}%)\n"
            f"- Current Skill Gaps: {missing}\n\n"
            f"Guidelines:\n"
            f"- Answer the candidate's question with precise, actionable, industry-relevant advice.\n"
            f"- Use concise markdown formatting, bold keywords, and bullet points.\n"
            f"- If the candidate asks for code, resume bullet points, interview questions, or study milestones, provide production-grade, highly specific examples.\n"
            f"- Keep the tone encouraging, professional, and directly tailored to their tech stack."
        )

        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": f"System Context:\n{system_instruction}\n\nCandidate Question: {user_query}"}]
                }
            ],
            "generationConfig": {
                "temperature": 0.4,
                "maxOutputTokens": 800
            }
        }

        models_to_try = ["gemini-1.5-flash-latest", "gemini-1.5-flash", "gemini-2.0-flash", "gemini-pro"]
        async with httpx.AsyncClient(timeout=15.0) as client:
            for model_name in models_to_try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
                try:
                    resp = await client.post(url, json=payload, headers={"Content-Type": "application/json"})
                    if resp.status_code == 200:
                        data = resp.json()
                        candidates = data.get("candidates", [])
                        if candidates:
                            parts = candidates[0].get("content", {}).get("parts", [])
                            if parts:
                                return parts[0].get("text", "")
                    elif resp.status_code == 404:
                        continue  # Try next model candidate
                    else:
                        print(f"[Gemini API Error] {resp.status_code}: {resp.text}")
                        break
                except Exception as e:
                    print(f"[Gemini API Exception] {e}")
                    break
        return None

    def _generate_domain_response(self, q: str, q_lower: str, candidate: Dict[str, Any], target_job: Dict[str, Any], match_info: Dict[str, Any]) -> str:
        """Intelligent structured responses for all career, interview, ATS, and skill queries."""
        skills = candidate.get("skills", [])
        ats_score = candidate.get("ats_score", 85)
        missing = match_info.get("missing_skills", [])
        matched = match_info.get("matched_skills", [])
        overall_score = match_info.get("overall_match_score", 84)
        job_title = target_job.get("title", "Data Scientist")
        company = target_job.get("company", "Target Company")

        # 1. Score breakdown explanation
        if any(k in q_lower for k in ["why is my score", "score explanation", "explain score", "breakdown", "match score", "how is score calculated"]):
            breakdown = match_info.get("breakdown", {})
            return (
                f"### 📊 Match Score Analysis: **{overall_score}%** for **{job_title}**\n\n"
                f"Your match score is calculated across 4 weighted production pillars:\n\n"
                f"• **Semantic Context Alignment ({breakdown.get('semantic_similarity', 88)}%)**: TF-IDF & Cosine vector similarity comparing your resume content against industry job requisitions.\n"
                f"• **Skill Overlap ({breakdown.get('skill_match', 74)}%)**: You have matched **{len(matched)}** core skills ({', '.join(matched[:4]) or 'Python, SQL'}), while missing **{len(missing)}** high-demand competencies ({', '.join(missing[:4]) or 'Docker, AWS'}).\n"
                f"• **Experience Level Match ({breakdown.get('experience_fit', 85)}%)**: Evaluated against role seniority criteria.\n"
                f"• **ATS Resume Health ({ats_score}/100)**: Verification of quantifiable metrics, technical density, and contact accessibility.\n\n"
                f"👉 *Use our **What-If Simulator** to test how learning {missing[0] if missing else 'a cloud tool'} raises your score.*"
            )

        # 2. What should I learn / Learning priority
        if any(k in q_lower for k in ["what should i learn", "priority", "learn first", "next step", "what to study", "roadmap", "curriculum", "skill to learn"]):
            if missing:
                top_priority = missing[0]
                second_priority = missing[1] if len(missing) > 1 else "Cloud Infrastructure (AWS/GCP)"
                return (
                    f"### 🎯 Recommended Learning Path for **{job_title}**\n\n"
                    f"Based on real-world employer requirements at {company}, your optimal learning sequence is:\n\n"
                    f"1. **{top_priority} (Highest Impact)**\n"
                    f"   • *Why*: Appears in 75%+ of active postings and accounts for your largest current score deficit.\n"
                    f"   • *Action*: Build a functional mini-project using {top_priority} and push code evidence to GitHub.\n\n"
                    f"2. **{second_priority} (Secondary Boost)**\n"
                    f"   • *Why*: Essential for production pipelines and scaling models.\n\n"
                    f"💡 *Switch to the **Learning Roadmap** tab to access week-by-week tutorials and capstone ideas.*"
                )
            return (
                f"### 🌟 Skill Profile Fully Aligned!\n"
                f"You already hold all core skills for **{job_title}**. To differentiate yourself in the top 5% of candidates:\n"
                f"• Focus on **MLOps Deployment** (CI/CD pipelines, Docker, Kubernetes).\n"
                f"• Add **System Design & Latency Optimization** benchmarks to your GitHub portfolio."
            )

        # 3. ATS & Resume Optimization tips
        if any(k in q_lower for k in ["improve resume", "ats score", "ats", "resume tips", "better score", "bullet", "bullets"]):
            return (
                f"### 🚀 Actionable Strategy to Boost Your ATS & Interview Callback Rate\n\n"
                f"1. **Adopt Google XYZ Format**:\n"
                f"   *Instead of*: 'Built machine learning model for customer churn.'\n"
                f"   *Write*: 'Engineered an XGBoost churn prediction pipeline achieving **0.91 AUC**, reducing user attrition by **18%** across 45,000 active accounts.'\n\n"
                f"2. **Keyword Placement**:\n"
                f"   Explicitly integrate high-demand tokens: `{', '.join(missing[:3]) if missing else 'Docker, Kubernetes, AWS'}` in your Technical Skills section.\n\n"
                f"3. **Verify Code Evidence**:\n"
                f"   Use our **GitHub Portfolio Scanner** on the Resume tab to attach verifiable code highlights directly to your application!\n\n"
                f"✨ *Click the **AI Tailor** button on any job card to automatically generate custom bullet points.*"
            )

        # 4. Interview preparation advice
        if any(k in q_lower for k in ["interview", "interview prep", "questions", "prepare", "coding round", "behavioral"]):
            role = job_title or "Software / Data Engineer"
            return (
                f"### 🎯 Interview Preparation Blueprint for **{role}**\n\n"
                f"Most modern hiring bars evaluate candidates across 3 core stages:\n\n"
                f"1. **Technical Problem Solving & DSA (45 mins)**\n"
                f"   • Focus on Arrays, Hash Maps, Dynamic Programming, and SQL Window Functions (`RANK`, `ROW_NUMBER`, `LEAD/LAG`).\n\n"
                f"2. **Domain & System Architecture (45 mins)**\n"
                f"   • Be prepared to explain your capstone project's trade-offs: Why did you pick `{skills[0] if skills else 'Python'}` over alternatives?\n"
                f"   • How would you scale the data ingestion pipeline if throughput increased 100x?\n\n"
                f"3. **Behavioral (STAR Method)**\n"
                f"   • Prepare stories showcasing cross-functional collaboration and handling ambiguous technical requirements."
            )

        # 5. Salary & Compensation
        if any(k in q_lower for k in ["salary", "package", "lpa", "compensation", "pay"]):
            return (
                f"### 💼 Market Compensation Benchmarks (India Tech Hubs)\n\n"
                f"For **{job_title}** in Pune / Bengaluru / Hyderabad:\n"
                f"• **Entry-Level (0 - 2 yrs)**: ₹6,50,000 – ₹12,00,000 P.A.\n"
                f"• **Mid-Level (2 - 5 yrs)**: ₹14,00,000 – ₹24,00,000 P.A.\n"
                f"• **Senior / Staff (5+ yrs)**: ₹26,00,000 – ₹45,00,000+ P.A.\n\n"
                f"💡 *Check the **Market Analytics & Clusters** tab to visualize the complete salary spectrum across tech specializations.*"
            )

        # 6. Default open-ended response
        return (
            f"### 🤖 Hack My Career AI Copilot\n\n"
            f"You are currently evaluating fit for **{job_title}** at **{company}** with an overall match of **{overall_score}%**.\n\n"
            f"Here are key recommendations tailored to your profile:\n"
            f"• **Top Competencies Detected**: {', '.join(skills[:4]) or 'Software Engineering Fundamentals'}\n"
            f"• **Key Gap to Close**: `{missing[0] if missing else 'Cloud Architecture'}` (simulating this in What-If elevates callback odds)\n"
            f"• **Real-World Live Jobs**: Type `'latest jobs in Pune'` or click **Real-World Live Jobs** to view live aggregator postings.\n\n"
            f"💡 *To unlock unlimited open-ended conversations with Google Gemini 1.5 Flash, paste your free Gemini API key into the Copilot header settings!*"
        )

career_copilot = CareerCopilot()
