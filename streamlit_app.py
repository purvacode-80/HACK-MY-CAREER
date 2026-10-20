import streamlit as st
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

from backend.app.ml.parser import parser_engine
from backend.app.ml.taxonomy import taxonomy_engine
from backend.app.ml.matcher import matcher_engine
from backend.app.ml.classifier import career_classifier
from backend.app.ml.clusterer import job_clusterer
from backend.app.ml.simulator import what_if_simulator
from backend.app.ml.roadmap import roadmap_engine
from backend.app.ml.copilot import career_copilot
from backend.app.db.mongodb import db_manager

st.set_page_config(
    page_title="Hack My Career | AI Resume & Career Intelligence",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-header { font-size: 2.2rem; font-weight: 800; color: #818cf8; margin-bottom: 0px; }
    .sub-header { font-size: 1.0rem; color: #94a3b8; margin-bottom: 20px; }
    .metric-card { background: #1e293b; border-radius: 10px; padding: 15px; border: 1px solid #334155; }
</style>
""", unsafe_allow_html=True)

# Load sample resumes
with open("backend/app/data/sample_resumes.json") as f:
    sample_resumes = json.load(f)

# Sidebar
st.sidebar.title("🎯 Control Panel")
profile_choice = st.sidebar.selectbox(
    "Select Student Profile (or Upload PDF below)",
    ["⭐ Vaishnavi Pawar (VIT Pune)", "Aarav Sharma (Data Science)", "Karan Verma (AI & Deep Learning)", "Riya Patel (Full Stack Web)"]
)

uploaded_file = st.sidebar.file_uploader("Upload Your Resume (PDF or DOCX)", type=["pdf", "docx", "txt"])

# Active Profile Selection
active_profile = None
if uploaded_file is not None:
    file_bytes = uploaded_file.read()
    if uploaded_file.name.endswith(".pdf"):
        text = parser_engine.extract_text_from_pdf(file_bytes)
    elif uploaded_file.name.endswith(".docx"):
        text = parser_engine.extract_text_from_docx(file_bytes)
    else:
        text = file_bytes.decode("utf-8", errors="ignore")
    active_profile = parser_engine.parse_resume(text, filename=uploaded_file.name)
    st.sidebar.success(f"Loaded: {uploaded_file.name}")
else:
    if "Vaishnavi" in profile_choice:
        active_profile = sample_resumes[0]   # Vaishnavi Pawar — index 0 (primary)
    elif "Data Science" in profile_choice:
        active_profile = sample_resumes[1]
    elif "AI & Deep Learning" in profile_choice:
        active_profile = sample_resumes[2]
    else:
        active_profile = sample_resumes[3] if len(sample_resumes) > 3 else sample_resumes[1]

# Header
st.markdown('<div class="main-header">⚡ Hack My Career</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">AI Resume & Career Intelligence • Data Science & Analytics Platform • Explainable Job Matching • What-If Simulation</div>', unsafe_allow_html=True)

# Navigation Tabs
tabs = st.tabs([
    "📄 Resume & ATS Health",
    "🎯 Explainable Job Matching",
    "⚡ What-If Simulator",
    "🗺️ Personalized Learning Roadmap",
    "📊 Job Market Analytics & Clusters",
    "📂 My Uploaded Resumes (MongoDB)"
])

# ----------------- TAB 1: RESUME & ATS HEALTH -----------------
with tabs[0]:
    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("ATS Resume Health")
        ats_score = active_profile.get("ats_score", 85)
        fig_ats = go.Figure(go.Indicator(
            mode="gauge+number",
            value=ats_score,
            title={'text': "ATS Score / 100"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "#6366f1"},
                'steps': [
                    {'range': [0, 50], 'color': "#334155"},
                    {'range': [50, 80], 'color': "#475569"},
                    {'range': [80, 100], 'color': "#1e293b"}
                ],
                'threshold': {'line': {'color': "#10b981", 'width': 4}, 'thickness': 0.75, 'value': 85}
            }
        ))
        fig_ats.update_layout(height=280, margin=dict(l=20, r=20, t=40, b=20), paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"})
        st.plotly_chart(fig_ats, use_container_width=True)

    with col2:
        st.subheader(f"Extracted Profile: {active_profile['name']}")
        st.write(f"**Education:** {active_profile.get('education', 'B.Tech')}")
        
        # Dynamic experience — use experience_display if available, else fallback to years
        exp_display = active_profile.get("experience_display", "")
        if not exp_display:
            exp_years = active_profile.get("experience_years", 1.0)
            exp_display = f"{exp_years} years"
        st.write(f"**Experience / Seniority:** {exp_display}")
        
        # Dynamic contact — use contact_display if available, else show individual fields
        contact_display = active_profile.get("contact_display", "")
        if not contact_display:
            email = active_profile.get("email", "N/A")
            phone = active_profile.get("phone", "N/A")
            contact_display = f"{email} | {phone}"
        st.write(f"**Contact Info:** {contact_display}")
        
        skill_count = active_profile.get("skill_count", len(active_profile.get("skills", [])))
        st.write(f"**Canonical Skills Detected:** {skill_count}")
        
        st.write("**Extracted Canonical Skills:**")
        skills_html = "".join([f'<span style="background:#334155; color:#a5b4fc; padding:4px 10px; margin:3px; border-radius:12px; display:inline-block; font-size:12px;">{s}</span>' for s in active_profile.get("skills", [])])
        st.markdown(skills_html, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("🎯 Target Job Role & Custom Job Description Matcher")
    c_role, c_jd = st.columns([1, 2])
    with c_role:
        custom_role = st.selectbox(
            "Select Job Role You Want to Apply For:",
            ["Data Scientist", "Machine Learning Engineer", "Data Analyst", "AI Research Engineer", "MLOps Engineer", "Full Stack Developer", "Backend Engineer (Python)", "Big Data Engineer"]
        )
        jd_file = st.file_uploader("Upload Job Description (PDF, DOCX, PPT, PPTX, TXT):", type=["pdf", "docx", "ppt", "pptx", "txt"], key="jd_file_upload")
        
    with c_jd:
        default_jd_text = ""
        if jd_file is not None:
            raw_jd = parser_engine.extract_from_file_bytes(jd_file.name, jd_file.read())
            default_jd_text = raw_jd
            st.success(f"Extracted JD from {jd_file.name}")
        
        custom_jd_input = st.text_area("Or Paste Job Description Text Here:", value=default_jd_text, height=140, placeholder="Paste job requirements, required technologies, responsibilities...")
        
    if st.button("⚡ Analyze & Match Resume Against This Role / Job"):
        if not custom_jd_input.strip():
            custom_jd_input = f"Looking for a {custom_role} with strong engineering and analytical competencies."
        
        extracted_jd_skills = taxonomy_engine.extract_skills_from_text(custom_jd_input)
        if not extracted_jd_skills:
            extracted_jd_skills = career_classifier.get_top_features_for_role(custom_role, top_n=5)
        
        custom_job = {
            "id": "custom-target-job",
            "title": f"Custom {custom_role}",
            "role": custom_role,
            "company": "Target Employer",
            "location": "Custom Application",
            "min_experience_years": 1,
            "salary_range": "Market Standard",
            "required_skills": extracted_jd_skills[:6] if len(extracted_jd_skills) >= 4 else extracted_jd_skills,
            "preferred_skills": extracted_jd_skills[6:10] if len(extracted_jd_skills) > 6 else [],
            "description": custom_jd_input
        }
        custom_res = matcher_engine.calculate_explainable_match(active_profile, custom_job)
        
        st.markdown(f"### Custom Fit Score: **{custom_res['overall_match_score']}%** for **{custom_role}**")
        m_c1, m_c2 = st.columns(2)
        with m_c1:
            st.success(f"✓ Matched Skills ({len(custom_res['matched_skills'])}): " + ", ".join(custom_res['matched_skills']))
        with m_c2:
            st.error(f"✗ Critical Missing Skills ({len(custom_res['missing_skills'])}): " + (", ".join(custom_res['missing_skills']) if custom_res['missing_skills'] else "None! Perfect fit."))

    st.markdown("---")
    st.subheader("Extracted Projects & Achievements")
    for proj in active_profile.get("projects", []):
        st.markdown(f"• {proj}")

# ----------------- TAB 2: EXPLAINABLE JOB MATCHING -----------------
with tabs[1]:
    st.subheader("Ranked Industry Matches")
    role_filter = st.selectbox("Filter by Role Family", ["All", "Data Scientist", "Machine Learning", "Data Analyst", "AI Research", "Full Stack", "Backend"])
    ranked_jobs = matcher_engine.rank_jobs(active_profile, top_k=10, role_filter=None if role_filter == "All" else role_filter)

    selected_idx = st.selectbox("Select a Job Posting to Inspect Explainability Breakdown", range(len(ranked_jobs)), format_func=lambda i: f"{ranked_jobs[i]['job_title']} at {ranked_jobs[i]['company']} ({ranked_jobs[i]['overall_match_score']}%)")
    target_job_match = ranked_jobs[selected_idx]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Overall Match", f"{target_job_match['overall_match_score']}%")
    c2.metric("Semantic Similarity", f"{target_job_match['dense_semantic_score']}%")
    c3.metric("Baseline TF-IDF", f"{target_job_match['baseline_tfidf_score']}%")
    c4.metric("Salary Range", target_job_match['salary_range'])

    st.write(f"**Company:** {target_job_match['company']} | **Location:** {target_job_match['location']}")

    st.markdown("#### 5-Factor Weighted Score Attribution")
    b = target_job_match["breakdown"]
    df_breakdown = pd.DataFrame({
        "Evaluation Dimension": ["Semantic Context (40%)", "Direct Skills (30%)", "Experience Fit (15%)", "Education Fit (10%)", "Project Relevance (5%)"],
        "Score (%)": [b["semantic_similarity"], b["skill_match"], b["experience_fit"], b["education_fit"], b["project_relevance"]]
    })
    fig_bar = px.bar(df_breakdown, x="Score (%)", y="Evaluation Dimension", orientation="h", color="Score (%)", color_continuous_scale="Viridis")
    fig_bar.update_layout(height=260, margin=dict(l=20, r=20, t=20, b=20), paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"})
    st.plotly_chart(fig_bar, use_container_width=True)

    col_m, col_g = st.columns(2)
    with col_m:
        st.success(f"✓ Matched Skills ({len(target_job_match['matched_skills'])})")
        st.write(", ".join(target_job_match["matched_skills"]))
    with col_g:
        st.error(f"✗ Critical Missing Skills ({len(target_job_match['missing_skills'])})")
        st.write(", ".join(target_job_match["missing_skills"]) if target_job_match["missing_skills"] else "None! Perfect skill fit.")

# ----------------- TAB 3: WHAT-IF SIMULATOR -----------------
with tabs[2]:
    st.subheader("Interactive 'What-If' Skill Acquisition Simulator")
    st.write(f"Simulating for target job: **{target_job_match['job_title']}** at **{target_job_match['company']}**")
    
    available_sim_skills = target_job_match["missing_skills"] + target_job_match.get("preferred_missing", []) + ["Docker", "AWS", "Kubernetes", "PyTorch", "FastAPI"]
    available_sim_skills = list(set(available_sim_skills))

    chosen_skills = st.multiselect("Select skills you plan to acquire:", available_sim_skills, default=target_job_match["missing_skills"][:2] if target_job_match["missing_skills"] else [])

    sim_res = what_if_simulator.simulate(active_profile, target_job_match["job_id"], chosen_skills)

    sc1, sc2, sc3 = st.columns(3)
    sc1.metric("Current Match", f"{sim_res['original_score']}%")
    sc2.metric("Simulated Match", f"{sim_res['simulated_score']}%", delta=f"+{sim_res['score_delta']}%")
    sc3.metric("Newly Satisfied", len(sim_res["newly_satisfied_skills"]))

    st.info(sim_res["summary"])

# ----------------- TAB 4: PERSONALIZED LEARNING ROADMAP -----------------
with tabs[3]:
    st.subheader(f"Personalized Learning Roadmap for {target_job_match['role']}")
    missing_for_roadmap = target_job_match["missing_skills"] if target_job_match["missing_skills"] else ["Docker", "AWS", "PyTorch"]
    roadmap_plan = roadmap_engine.generate_roadmap(missing_for_roadmap, target_job_match["role"])

    st.write(f"**Total Estimated Commitment:** {roadmap_plan['total_estimated_hours']} Hours • ~{roadmap_plan['estimated_completion_weeks']} Weeks (at 10 hours/week)")

    for s in roadmap_plan["steps"]:
        with st.expander(f"Step {s['step_number']}: Master {s['skill']} ({s['difficulty']} • {s['estimated_hours']} Hours)", expanded=True):
            st.write(s["summary"])
            st.write("**Key Milestones:**")
            for m in s["milestones"]:
                st.write(f"- {m}")
            st.info(f"💡 **Recommended Capstone Project:** {s['project_idea']}")
            st.write("**Free Curated Resources:**")
            for tut in s["tutorials"]:
                st.markdown(f"- [{tut['title']}]({tut['url']})")

# ----------------- TAB 5: MARKET ANALYTICS & CLUSTERS -----------------
with tabs[4]:
    st.subheader("Job Market Intelligence & Cluster Analysis")
    
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        # Top Demanded Skills
        with open("backend/app/data/market_trends.json") as f:
            market_trends_data = json.load(f)
        df_trends = pd.DataFrame(market_trends_data["top_demanded_skills"])
        fig_demand = px.bar(df_trends, x="skill", y="demand_percentage", title="Top Demanded Tech Skills (%)", color="demand_percentage", color_continuous_scale="Purples")
        fig_demand.update_layout(paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"})
        st.plotly_chart(fig_demand, use_container_width=True)

    with col_c2:
        df_sal = pd.DataFrame(market_trends_data["salary_by_role"])
        fig_sal = go.Figure()
        fig_sal.add_trace(go.Bar(x=df_sal["role"], y=df_sal["entry_level_lpa"], name="Entry Level (LPA)"))
        fig_sal.add_trace(go.Bar(x=df_sal["role"], y=df_sal["senior_level_lpa"], name="Senior Level (LPA)"))
        fig_sal.update_layout(title="Salary Spectrum Across Career Roles (₹ LPA)", barmode="group", paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"})
        st.plotly_chart(fig_sal, use_container_width=True)

    st.markdown("#### K-Means Unsupervised Job Clusters (2D PCA Space)")
    points = job_clusterer.get_cluster_points()
    df_pts = pd.DataFrame(points)
    fig_pca = px.scatter(df_pts, x="x", y="y", color="cluster_name", hover_data=["title", "company"], title=f"K=5 Job Clusters (Silhouette Score: {round(job_clusterer.silhouette, 3)})")
    fig_pca.update_layout(paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"})
    st.plotly_chart(fig_pca, use_container_width=True)

# ----------------- TAB 6: MY UPLOADED RESUMES (MONGODB ATLAS) -----------------
with tabs[5]:
    st.subheader("📂 My Uploaded Resumes (MongoDB Atlas Repository)")
    db_stat = db_manager.get_db_status()
    if db_stat.get("is_atlas_connected"):
        st.success("🍃 Connected to MongoDB Atlas Cloud Cluster (`hack_my_career`)")
    else:
        st.info("📂 Stored in MongoDB Document Repository (`backend/app/data/hack_my_career_mongodb.json`)")

    # Fetch stored resumes
    all_resumes = db_manager.get_user_resumes("usr_vaishnavi") or db_manager._read_local_db().get("resumes", [])
    
    if all_resumes:
        st.write(f"Total Resumes Available: **{len(all_resumes)}**")
        for r in all_resumes:
            with st.expander(f"📄 {r.get('filename', 'Resume')} — ATS Score: {r.get('ats_score', 85)}/100"):
                st.write(f"**Target Role:** {r.get('target_role', 'Data Scientist')}")
                st.write(f"**Uploaded At:** {r.get('uploaded_at', 'Recently')}")
                st.write(f"**Skills Detected ({r.get('skill_count', 0)}):** {', '.join(r.get('skills', []))}")
                cand = r.get("candidate_profile", {})
                if cand.get("projects"):
                    st.write("**Extracted Projects:**")
                    for p in cand["projects"]:
                        st.markdown(f"- {p}")
    else:
        st.info("No resumes uploaded yet. Upload a resume above to store it in MongoDB Atlas.")
