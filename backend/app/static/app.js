// =========================================================================
// HACK MY CAREER — FRONTEND CONTROLLER (MONGODB ATLAS & NLP INTELLIGENCE)
// =========================================================================

// State Management
let sampleProfiles = [];
let currentProfile = null;
let allJobs = [];
let rankedMatches = [];
let selectedJobMatch = null;
let marketData = null;
let selectedSimSkills = new Set();
let customJobMatch = null;
let customJobObj = null;

// User Session State (MongoDB Atlas Authentication)
let currentUser = null;
let userResumes = [];
let authMode = "login"; // "login" | "signup"

// Chart Instances
let skillsChartInstance = null;
let salaryChartInstance = null;
let clusterChartInstance = null;

// =========================================================================
// APPLICATION INITIALIZATION
// =========================================================================
document.addEventListener("DOMContentLoaded", async () => {
  try {
    // 1. Check & Initialize User Session
    initUserSession();

    // 2. Check Database Status (MongoDB Atlas)
    await checkDbStatus();

    // 3. Load Sample Verified Profiles (kept for reference, not auto-loaded)
    await fetchSampleProfiles();

    // 4. Load Market Analytics Data
    await fetchMarketAnalytics();

    // 5. Show placeholder profile — real data only loads after login + resume upload
    if (!currentProfile) {
      renderPlaceholderProfile();
    }

    // 6. If user is logged in, fetch their resume history from MongoDB Atlas
    if (currentUser) {
      await fetchUserResumes();
    }
  } catch (err) {
    console.error("Initialization error:", err);
  }
});

// =========================================================================
// 1. ACADIA AUTHENTICATION GATEWAY & SESSION MANAGEMENT
// =========================================================================
function initUserSession() {
  const saved = localStorage.getItem("hack_my_career_user");
  const gateway = document.getElementById("auth-gateway");
  const dashboard = document.getElementById("dashboard-wrapper");

  if (saved) {
    try {
      currentUser = JSON.parse(saved);
      // User is logged in: enter main dashboard
      gateway.style.display = "none";
      dashboard.style.display = "block";
      updateUserHeaderUI();
      return;
    } catch (e) {
      currentUser = null;
    }
  }

  // Not logged in: show Gateway portal screen and hide main dashboard
  currentUser = null;
  gateway.style.display = "flex";
  dashboard.style.display = "none";
}

function updateUserHeaderUI() {
  const nameEl = document.getElementById("user-display-name");
  const avatarEl = document.getElementById("user-avatar-text");

  if (currentUser) {
    if (nameEl) nameEl.innerText = currentUser.name || "Candidate";
    if (avatarEl) avatarEl.innerText = (currentUser.name || "U")[0].toUpperCase();
  }
}

function setAuthMode(mode) {
  authMode = mode;
  const nameGroup = document.getElementById("name-input-group");
  const submitBtn = document.getElementById("auth-submit-button");
  const tabLogin = document.getElementById("tab-btn-login");
  const tabSignup = document.getElementById("tab-btn-signup");
  const authTitle = document.getElementById("auth-title");
  const authDesc = document.getElementById("auth-desc");

  if (mode === "signup") {
    nameGroup.style.display = "block";
    submitBtn.innerHTML = "<span>Create Account & Enter</span> ➔";
    tabSignup.classList.add("active");
    tabLogin.classList.remove("active");
    authTitle.innerText = "Create New Account";
    authDesc.innerText = "Store your resumes and analytics in your MongoDB Atlas vault";
  } else {
    nameGroup.style.display = "none";
    submitBtn.innerHTML = "<span>Sign In to Dashboard</span> ➔";
    tabLogin.classList.add("active");
    tabSignup.classList.remove("active");
    authTitle.innerText = "Welcome to Hack My Career";
    authDesc.innerText = "Sign in to access your personal resume analytics dashboard";
  }
}

async function handleAuthSubmit(event) {
  event.preventDefault();
  const email = document.getElementById("auth-email-input").value.trim();
  const password = document.getElementById("auth-password-input").value.trim();
  const name = document.getElementById("auth-name-input").value.trim();

  const endpoint = authMode === "signup" ? "/api/auth/signup" : "/api/auth/login";
  const payload = authMode === "signup" ? { name, email, password } : { email, password };

  try {
    const res = await fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const data = await res.json();
    if (!res.ok) {
      alert(data.detail || "Authentication failed. Please verify credentials.");
      return;
    }

    currentUser = data.user;
    localStorage.setItem("hack_my_career_user", JSON.stringify(currentUser));
    
    // Transition to Dashboard
    document.getElementById("auth-gateway").style.display = "none";
    document.getElementById("dashboard-wrapper").style.display = "block";
    updateUserHeaderUI();
    await fetchUserResumes();

    // Show placeholder — user must upload their own resume to populate real data
    if (!currentProfile) {
      renderPlaceholderProfile();
    }
  } catch (err) {
    alert("Connection error during authentication. Check server status.");
  }
}

async function quickDemoLogin() {
  document.getElementById("auth-email-input").value = "demo@hackcareer.ai";
  document.getElementById("auth-password-input").value = "demo1234";
  setAuthMode("login");

  try {
    const res = await fetch("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: "demo@hackcareer.ai", password: "demo1234" })
    });

    if (res.ok) {
      const data = await res.json();
      currentUser = data.user;
    } else {
      // Auto-signup demo account if it doesn't exist yet
      const signupRes = await fetch("/api/auth/signup", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: "Demo Student", email: "demo@hackcareer.ai", password: "demo1234" })
      });
      const data = await signupRes.json();
      currentUser = data.user;
    }

    localStorage.setItem("hack_my_career_user", JSON.stringify(currentUser));

    // Enter Dashboard
    document.getElementById("auth-gateway").style.display = "none";
    document.getElementById("dashboard-wrapper").style.display = "block";
    updateUserHeaderUI();
    await fetchUserResumes();

    // Show placeholder — upload a resume to see real analytics
    if (!currentProfile) {
      renderPlaceholderProfile();
    }
  } catch (err) {
    console.error("Demo login error:", err);
    // Fallback local session if server is offline
    currentUser = {
      user_id: "usr_demo",
      name: "Demo Student",
      email: "demo@hackcareer.ai"
    };
    localStorage.setItem("hack_my_career_user", JSON.stringify(currentUser));
    document.getElementById("auth-gateway").style.display = "none";
    document.getElementById("dashboard-wrapper").style.display = "block";
    updateUserHeaderUI();
    renderPlaceholderProfile();
  }
}

function logoutUser() {
  currentUser = null;
  localStorage.removeItem("hack_my_career_user");
  userResumes = [];
  
  // Return to Gateway Screen
  document.getElementById("dashboard-wrapper").style.display = "none";
  document.getElementById("auth-gateway").style.display = "flex";
  setAuthMode("login");
}

// =========================================================================
// 2. MONGODB ATLAS STATUS & CONFIGURATION
// =========================================================================
async function checkDbStatus() {
  try {
    const res = await fetch("/api/db/status");
    if (res.ok) {
      const st = await res.json();
      const badge = document.getElementById("db-status-badge");
      const gBadge = document.getElementById("gateway-db-status");

      const label = st.is_atlas_connected
        ? "🍃 Database: MongoDB Atlas (Connected)"
        : "📂 Database: MongoDB Local Store";

      if (badge) {
        badge.innerHTML = label;
        badge.style.color = st.is_atlas_connected ? "#34d399" : "#a5b4fc";
      }
      if (gBadge) {
        gBadge.innerHTML = label;
        gBadge.style.color = st.is_atlas_connected ? "#34d399" : "#a5b4fc";
      }
    }
  } catch (e) {
    console.warn("Could not check db status", e);
  }
}

// =========================================================================
// PLACEHOLDER PROFILE — shown before user uploads their resume
// =========================================================================
function renderPlaceholderProfile() {
  // Candidate name
  const nameEl = document.getElementById("cand-name");
  if (nameEl) nameEl.innerText = "Your Name Here";

  // Contact row
  const contactEl = document.getElementById("cand-contact");
  if (contactEl) contactEl.innerText = "Upload your resume to extract contact details automatically";

  // Experience badge
  const expEl = document.getElementById("cand-exp");
  if (expEl) expEl.innerText = "Experience extracted from resume";

  // Skills
  const skillsCountEl = document.getElementById("cand-skills-count");
  const skillsContainer = document.getElementById("cand-skills-badges");
  if (skillsCountEl) skillsCountEl.innerText = "—";
  if (skillsContainer) {
    skillsContainer.innerHTML = `
      <span class="badge badge-neutral" style="opacity:0.5;">Python</span>
      <span class="badge badge-neutral" style="opacity:0.5;">SQL</span>
      <span class="badge badge-neutral" style="opacity:0.5;">Machine Learning</span>
      <span class="badge badge-neutral" style="opacity:0.5;">React</span>
      <span class="badge badge-neutral" style="opacity:0.5;">Docker</span>
      <span style="color:var(--text-muted); font-size:0.82rem; display:block; margin-top:0.5rem;">↑ Sample skills shown for preview — upload your resume to see your actual skills</span>
    `;
  }

  // Projects
  const projContainer = document.getElementById("cand-projects-list");
  if (projContainer) {
    projContainer.innerHTML = `
      <div style="color:var(--text-muted); font-style:italic; line-height:1.7;">
        📄 Your capstone projects and portfolio items will appear here after you upload your resume.<br>
        <span style="font-size:0.82rem;">Supports PDF, DOCX, TXT formats.</span>
      </div>
    `;
  }

  // ATS score gauge — reset to 0
  const scoreText = document.getElementById("ats-score-text");
  if (scoreText) scoreText.innerText = "—";
  const circle = document.getElementById("ats-gauge-circle");
  if (circle) {
    const circumference = 2 * Math.PI * 54;
    circle.style.strokeDashoffset = circumference;
  }

  // Source badge
  const badge = document.getElementById("profile-source-badge");
  if (badge) {
    badge.innerText = "No resume uploaded";
    badge.title = "Upload a resume to begin";
  }

  // Active profile pill
  const pill = document.getElementById("active-profile-pill");
  if (pill) pill.innerText = "No resume uploaded";
}


// =========================================================================
// 3. TAB NAVIGATION
// =========================================================================
function switchTab(tabId) {
  document.querySelectorAll(".tab-pane").forEach(p => p.classList.remove("active"));
  document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));

  const targetPane = document.getElementById(tabId);
  if (targetPane) targetPane.classList.add("active");

  const matchingBtn = Array.from(document.querySelectorAll(".tab-btn")).find(b => 
    b.getAttribute("onclick") && b.getAttribute("onclick").includes(tabId)
  );
  if (matchingBtn) matchingBtn.classList.add("active");

  if (tabId === "tab-market") {
    setTimeout(renderMarketCharts, 100);
  }
  if (tabId === "tab-history") {
    fetchUserResumes();
  }
}

// =========================================================================
// 4. REQUIREMENT 1: 100% DYNAMIC CANDIDATE PROFILE EXTRACTION
// =========================================================================
async function fetchSampleProfiles() {
  try {
    const res = await fetch("/api/resume/samples");
    if (res.ok) {
      sampleProfiles = await res.json();
    }
  } catch (e) {
    console.warn("Could not fetch samples:", e);
  }
}

function loadSampleProfile(id) {
  const found = sampleProfiles.find(s => s.id === id);
  if (found) {
    setCandidateProfile(found);
  }
}

function setCandidateProfile(profile) {
  if (!profile) return;
  currentProfile = profile;

  // 1. Update Active Profile Pill in Header
  const pill = document.getElementById("active-profile-pill");
  if (pill) pill.innerText = `Active: ${profile.name || "Candidate"}`;

  // 2. Update Filename Badge on Profile Card (Matches User Screenshot)
  const badge = document.getElementById("profile-source-badge");
  if (badge) {
    const fn = profile.filename || profile.title || "Uploaded_Resume.pdf";
    badge.innerText = fn;
    badge.title = fn;
  }

  // 3. Candidate Name
  const nameEl = document.getElementById("cand-name");
  if (nameEl) nameEl.innerText = profile.name || "Candidate Name";

  // 4. Contact & Institution (Dynamic, NO dummy placeholders)
  const contactEl = document.getElementById("cand-contact");
  if (contactEl) {
    let contactStr = "";
    if (profile.contact_display) {
      contactStr = profile.contact_display;
    } else {
      const parts = [];
      if (profile.email) parts.push(profile.email);
      if (profile.phone) parts.push(profile.phone);
      if (profile.location) parts.push(profile.location);
      if (profile.profiles && profile.profiles.length > 0) parts.push(...profile.profiles.slice(0, 2));
      contactStr = parts.join(" • ") || "Contact details extracted from document";
    }
    // Include education / college if available and not redundant
    if (profile.education && !contactStr.toLowerCase().includes(profile.education.toLowerCase())) {
      contactStr += ` • ${profile.education}`;
    }
    contactEl.innerText = contactStr;
  }

  // 5. Seniority / Experience
  const expEl = document.getElementById("cand-exp");
  if (expEl) {
    const expStr = profile.experience_display || `${profile.experience_years || 0.5} Years Experience`;
    expEl.innerText = expStr;
  }

  // 6. Extracted Canonical Technical Skills
  const skillsCountEl = document.getElementById("cand-skills-count");
  const skillsContainer = document.getElementById("cand-skills-badges");
  const skillsList = profile.skills || [];

  if (skillsCountEl) skillsCountEl.innerText = skillsList.length;
  if (skillsContainer) {
    skillsContainer.innerHTML = "";
    if (skillsList.length === 0) {
      skillsContainer.innerHTML = `<span style="color:var(--text-muted); font-size:0.85rem;">No technical skills detected.</span>`;
    } else {
      skillsList.forEach(skill => {
        const span = document.createElement("span");
        span.className = "badge badge-neutral";
        span.innerText = skill;
        skillsContainer.appendChild(span);
      });
    }
  }

  // 7. Extracted Portfolio & Capstone Projects
  const projContainer = document.getElementById("cand-projects-list");
  if (projContainer) {
    projContainer.innerHTML = "";
    const projs = profile.projects || [];
    if (projs.length === 0) {
      projContainer.innerHTML = `<div style="color:var(--text-muted);">Academic portfolio & capstone projects extracted dynamically from document.</div>`;
    } else {
      projs.forEach(p => {
        const div = document.createElement("div");
        div.className = "cand-proj-item";
        div.innerHTML = `• ${p}`;
        projContainer.appendChild(div);
      });
    }
  }

  // 8. ATS Resume Score & Progress Gauge
  const ats = profile.ats_score || 85;
  const scoreText = document.getElementById("ats-score-text");
  if (scoreText) scoreText.innerText = ats;

  const circle = document.getElementById("ats-gauge-circle");
  if (circle) {
    const circumference = 2 * Math.PI * 54; // ~339.29
    const offset = circumference - (ats / 100) * circumference;
    circle.style.strokeDashoffset = offset;
  }

  // 9. Re-run Match Engine with new Profile
  runJobMatching();
}

// File Upload Handler (Auto-saves to MongoDB Atlas)
async function handleFileUpload(event) {
  const file = event.target.files[0];
  if (!file) return;

  const formData = new FormData();
  formData.append("file", file);
  if (currentUser) {
    formData.append("user_id", currentUser.user_id);
  }

  const pill = document.getElementById("active-profile-pill");
  if (pill) pill.innerText = `Parsing ${file.name}...`;

  try {
    const res = await fetch("/api/resume/upload", {
      method: "POST",
      body: formData
    });

    if (!res.ok) {
      alert("Error parsing document. Supported formats: PDF, DOCX, PPT, PPTX, TXT.");
      if (pill && currentProfile) pill.innerText = `Active: ${currentProfile.name}`;
      return;
    }

    const parsedProfile = await res.json();
    setCandidateProfile(parsedProfile);

    // Refresh user's saved resumes from MongoDB Atlas
    if (currentUser) {
      await fetchUserResumes();
    }

    switchTab("tab-resume");
    alert(`Successfully parsed ${file.name}! Detected ${parsedProfile.skill_count} skills and saved to MongoDB.`);
  } catch (err) {
    console.error("Upload error:", err);
    alert("Upload failed. Make sure the server backend is running.");
  }
}

// =========================================================================
// 5. REQUIREMENT 4: USER'S PERSONAL DASHBOARD & RESUME REPOSITORY (MONGODB)
// =========================================================================
async function fetchUserResumes() {
  if (!currentUser) return;
  try {
    const res = await fetch(`/api/user/resumes?user_id=${currentUser.user_id}`);
    if (res.ok) {
      const data = await res.json();
      userResumes = data.resumes || [];
      renderUserResumes();
    }
  } catch (err) {
    console.error("Error fetching user resumes:", err);
  }
}

function renderUserResumes() {
  const container = document.getElementById("user-resumes-container");
  const subtext = document.getElementById("user-repo-subtext");
  if (!container) return;
  container.innerHTML = "";

  if (subtext) {
    subtext.innerText = `Personal Vault: ${userResumes.length} Resume${userResumes.length === 1 ? "" : "s"} Saved in MongoDB`;
  }

  if (userResumes.length === 0) {
    container.innerHTML = `
      <div style="grid-column: 1/-1; text-align:center; padding:3rem; background:rgba(255,255,255,0.02); border-radius:var(--radius-md); border:1px dashed var(--border);">
        <p style="font-size:1.1rem; font-weight:600; color:white;">No resumes uploaded yet for this account.</p>
        <p style="font-size:0.85rem; color:var(--text-muted); margin:0.5rem 0 1.25rem;">
          Upload your resume using the button below or drag-and-drop on the Resume Intelligence tab. It will be securely stored in your personal MongoDB Atlas database!
        </p>
        <button class="btn btn-primary" onclick="document.getElementById('file-upload-input').click()">
          📥 Upload Resume Now
        </button>
      </div>
    `;
    return;
  }

  userResumes.forEach(r => {
    const card = document.createElement("div");
    card.className = "user-resume-card";
    const uploadDate = new Date(r.uploaded_at).toLocaleString();
    const skillsList = r.skills || [];
    const skillsSnippet = skillsList.slice(0, 5).join(", ") + (skillsList.length > 5 ? ` +${skillsList.length - 5} more` : "");

    card.innerHTML = `
      <div>
        <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:0.75rem;">
          <div style="max-width:70%;">
            <strong style="color:white; font-size:1.05rem; display:block; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;" title="${r.filename}">
              📄 ${r.filename}
            </strong>
            <span style="font-size:0.75rem; color:var(--text-muted);">${uploadDate}</span>
          </div>
          <div class="badge badge-matched" style="font-size:0.85rem;">ATS ${r.ats_score}/100</div>
        </div>
        <div style="font-size:0.8rem; color:#cbd5e1; margin-bottom:0.5rem;">
          <strong>Target Role:</strong> ${r.target_role || "Data Scientist"}
        </div>
        <div style="font-size:0.8rem; color:var(--text-muted); margin-bottom:1rem; line-height:1.4;">
          <strong>Detected Skills (${r.skill_count}):</strong> ${skillsSnippet || "None"}
        </div>
      </div>
      <div style="display:flex; gap:0.5rem;">
        <button class="btn btn-primary" style="flex:1; padding:0.45rem 0.8rem; font-size:0.82rem; justify-content:center;" onclick="loadSavedResume('${r.resume_id}')">
          🔍 Analyze Resume
        </button>
        <button class="btn btn-secondary" style="padding:0.45rem 0.65rem; color:#f87171;" onclick="deleteSavedResume('${r.resume_id}')" title="Delete from MongoDB">
          🗑️
        </button>
      </div>
    `;
    container.appendChild(card);
  });
}

async function loadSavedResume(resumeId) {
  try {
    const res = await fetch(`/api/user/resumes/${resumeId}?user_id=${currentUser?.user_id || ""}`);
    if (res.ok) {
      const data = await res.json();
      setCandidateProfile(data.candidate_profile);
      switchTab("tab-resume");
      alert(`Loaded "${data.filename}" from MongoDB Atlas repository!`);
    } else {
      alert("Could not load saved resume.");
    }
  } catch (err) {
    alert("Network error loading saved resume.");
  }
}

async function deleteSavedResume(resumeId) {
  if (!confirm("Are you sure you want to delete this resume from your MongoDB database?")) return;
  try {
    const res = await fetch(`/api/user/resumes/${resumeId}?user_id=${currentUser?.user_id || ""}`, {
      method: "DELETE"
    });
    if (res.ok) {
      await fetchUserResumes();
      alert("Resume removed from MongoDB Atlas.");
    }
  } catch (err) {
    alert("Failed to delete resume.");
  }
}

// =========================================================================
// 6. JOB MATCHING & SKILL GAP BREAKDOWN
// =========================================================================
async function runJobMatching() {
  if (!currentProfile) return;

  try {
    const roleFilterEl = document.getElementById("role-filter-select");
    const roleFilter = roleFilterEl ? roleFilterEl.value : "all";

    const res = await fetch("/api/jobs/match", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        candidate: currentProfile,
        top_k: 25,
        role_filter: roleFilter
      })
    });

    if (res.ok) {
      const data = await res.json();
      rankedMatches = data.matches || [];
      renderRankedJobs();
      if (rankedMatches.length > 0) {
        selectJob(rankedMatches[0]);
      }
    }
  } catch (e) {
    console.error("Job matching error:", e);
  }
}

function filterJobs() {
  runJobMatching();
}

function renderRankedJobs() {
  const container = document.getElementById("jobs-list-container");
  if (!container) return;
  container.innerHTML = "";

  const searchVal = (document.getElementById("job-search-input")?.value || "").toLowerCase();

  const filtered = rankedMatches.filter(m => {
    if (!searchVal) return true;
    return m.job_title.toLowerCase().includes(searchVal) || 
           m.company.toLowerCase().includes(searchVal) ||
           m.matched_skills.some(s => s.toLowerCase().includes(searchVal));
  });

  filtered.forEach(item => {
    const div = document.createElement("div");
    div.className = `job-item ${selectedJobMatch && selectedJobMatch.job_id === item.job_id ? "selected" : ""}`;
    div.onclick = () => selectJob(item);
    div.innerHTML = `
      <div class="job-header">
        <div>
          <div class="job-title">${item.job_title}</div>
          <div class="job-company">${item.company} • ${item.location} • ${item.salary_range}</div>
        </div>
        <div class="job-match-pill">${item.overall_match_score}%</div>
      </div>
      <div style="font-size:0.75rem; color:#818cf8; margin-top:0.25rem;">
        Semantic: ${item.dense_semantic_score}% | Direct Skills: ${item.breakdown.skill_match}%
      </div>
    `;
    container.appendChild(div);
  });
}

function selectJob(jobMatch) {
  selectedJobMatch = jobMatch;
  renderRankedJobs();

  document.getElementById("detail-job-title").innerText = jobMatch.job_title;
  document.getElementById("detail-job-company").innerText = `${jobMatch.company} • ${jobMatch.location} • ${jobMatch.salary_range}`;
  document.getElementById("detail-match-score").innerText = `${jobMatch.overall_match_score}%`;

  // 5-Factor Breakdown
  const b = jobMatch.breakdown;
  document.getElementById("factor-semantic").innerText = `${b.semantic_similarity}%`;
  document.getElementById("bar-semantic").style.width = `${b.semantic_similarity}%`;

  document.getElementById("factor-skill").innerText = `${b.skill_match}%`;
  document.getElementById("bar-skill").style.width = `${b.skill_match}%`;

  document.getElementById("factor-exp").innerText = `${b.experience_fit}%`;
  document.getElementById("bar-exp").style.width = `${b.experience_fit}%`;

  document.getElementById("factor-edu").innerText = `${b.education_fit}%`;
  document.getElementById("bar-edu").style.width = `${b.education_fit}%`;

  document.getElementById("factor-proj").innerText = `${b.project_relevance}%`;
  document.getElementById("bar-proj").style.width = `${b.project_relevance}%`;

  // Matched Skills Badges
  const matchedBox = document.getElementById("detail-matched-skills");
  matchedBox.innerHTML = "";
  jobMatch.matched_skills.forEach(s => {
    const badge = document.createElement("span");
    badge.className = "badge badge-matched";
    badge.innerText = `✓ ${s}`;
    matchedBox.appendChild(badge);
  });

  // Missing Skills Badges
  const missingBox = document.getElementById("detail-missing-skills");
  missingBox.innerHTML = "";
  jobMatch.missing_skills.forEach(s => {
    const badge = document.createElement("span");
    badge.className = "badge badge-missing";
    badge.innerText = `✗ ${s}`;
    missingBox.appendChild(badge);
  });

  // Preferred Missing Badges
  const prefBox = document.getElementById("detail-pref-missing");
  prefBox.innerHTML = "";
  jobMatch.preferred_missing.forEach(s => {
    const badge = document.createElement("span");
    badge.className = "badge badge-pref";
    badge.innerText = `★ ${s}`;
    prefBox.appendChild(badge);
  });
}

// =========================================================================
// 7. INTERACTIVE "WHAT-IF" SIMULATOR
// =========================================================================
function openSimulatorForJob() {
  if (!selectedJobMatch) return;
  switchTab("tab-simulator");

  document.getElementById("sim-target-role").innerText = selectedJobMatch.job_title;
  document.getElementById("sim-target-company").innerText = selectedJobMatch.company;
  document.getElementById("sim-orig-score").innerText = `${selectedJobMatch.overall_match_score}%`;
  document.getElementById("sim-new-score").innerText = `${selectedJobMatch.overall_match_score}%`;
  document.getElementById("sim-delta-badge").innerText = "+0.0% Increase";

  selectedSimSkills.clear();

  const container = document.getElementById("sim-skill-checkboxes");
  container.innerHTML = "";

  const candidateCurrent = new Set(currentProfile.skills || []);
  const allTargetSkills = [...selectedJobMatch.missing_skills, ...selectedJobMatch.preferred_missing];
  
  const extraPool = ["Docker", "AWS", "Kubernetes", "PyTorch", "FastAPI", "PostgreSQL", "MLOps"];
  extraPool.forEach(sk => {
    if (!candidateCurrent.has(sk) && !allTargetSkills.includes(sk)) {
      allTargetSkills.push(sk);
    }
  });

  allTargetSkills.forEach(skill => {
    const label = document.createElement("label");
    label.style.display = "flex";
    label.style.alignItems = "center";
    label.style.gap = "0.6rem";
    label.style.fontSize = "0.9rem";
    label.style.cursor = "pointer";

    const chk = document.createElement("input");
    chk.type = "checkbox";
    chk.value = skill;
    chk.onchange = () => toggleSimSkill(skill, chk.checked);

    label.appendChild(chk);
    label.appendChild(document.createTextNode(skill));
    container.appendChild(label);
  });
}

async function toggleSimSkill(skill, isChecked) {
  if (isChecked) selectedSimSkills.add(skill);
  else selectedSimSkills.delete(skill);

  const res = await fetch("/api/simulate/what-if", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      candidate: currentProfile,
      target_job_id: selectedJobMatch.job_id,
      added_skills: Array.from(selectedSimSkills)
    })
  });

  if (res.ok) {
    const data = await res.json();
    document.getElementById("sim-orig-score").innerText = `${data.original_score}%`;
    document.getElementById("sim-new-score").innerText = `${data.simulated_score}%`;
    document.getElementById("sim-delta-badge").innerText = `+${data.score_delta}% Score Increase`;
    document.getElementById("sim-summary-text").innerText = data.summary;
  }
}

// =========================================================================
// 8. PERSONALIZED LEARNING ROADMAP
// =========================================================================
async function openRoadmapForJob() {
  if (!selectedJobMatch) return;
  switchTab("tab-roadmap");

  const targetRole = selectedJobMatch.role || "Data Scientist";
  document.getElementById("roadmap-role-title").innerText = targetRole;

  const missing = [...selectedJobMatch.missing_skills, ...selectedJobMatch.preferred_missing];
  const missingList = missing.length > 0 ? missing : ["Docker", "AWS", "PyTorch"];

  const res = await fetch("/api/learning/roadmap", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      missing_skills: missingList,
      target_role: targetRole
    })
  });

  if (res.ok) {
    const data = await res.json();
    document.getElementById("roadmap-hours-badge").innerText = `${data.total_estimated_hours} Total Hours • ${data.estimated_completion_weeks} Weeks`;
    
    const container = document.getElementById("roadmap-timeline");
    container.innerHTML = "";

    data.steps.forEach(step => {
      const stepDiv = document.createElement("div");
      stepDiv.className = "timeline-step";
      stepDiv.innerHTML = `
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.5rem;">
          <strong style="color:#818cf8; font-size:1.05rem;">Step ${step.step_number}: Master ${step.skill}</strong>
          <span class="badge badge-neutral">${step.difficulty} • ${step.estimated_hours} Hours</span>
        </div>
        <p style="color:var(--text-muted); font-size:0.85rem; margin-bottom:0.75rem;">${step.summary}</p>
        
        <div style="font-size:0.8rem; font-weight:700; color:#cbd5e1; margin-bottom:0.3rem;">KEY MILESTONES:</div>
        <ul style="padding-left:1.25rem; font-size:0.8rem; color:var(--text-muted); margin-bottom:0.75rem;">
          ${step.milestones.map(m => `<li>${m}</li>`).join("")}
        </ul>

        <div style="background:rgba(255,255,255,0.03); padding:0.6rem; border-radius:var(--radius-sm); font-size:0.8rem; margin-bottom:0.6rem;">
          <strong style="color:#34d399;">💡 Capstone Project Idea:</strong> ${step.project_idea}
        </div>

        <div style="display:flex; gap:0.5rem; flex-wrap:wrap;">
          ${step.tutorials.map(t => `<a href="${t.url}" target="_blank" class="sample-btn" style="text-decoration:none; display:inline-flex; align-items:center; gap:0.3rem;">🔗 ${t.title}</a>`).join("")}
        </div>
      `;
      container.appendChild(stepDiv);
    });
  }
}

// =========================================================================
// 9. CUSTOM JOB DESCRIPTION MATCHER
// =========================================================================
async function handleJdFileUpload(event) {
  const file = event.target.files[0];
  if (!file) return;

  const formData = new FormData();
  formData.append("file", file);

  const badge = document.getElementById("custom-jd-status-badge");
  badge.innerText = `Extracting ${file.name}...`;

  try {
    const res = await fetch("/api/jobs/upload-jd", {
      method: "POST",
      body: formData
    });

    if (!res.ok) {
      alert("Error extracting document. Supported formats: PDF, DOCX, PPT, PPTX, TXT.");
      badge.innerText = "Upload failed";
      return;
    }

    const data = await res.json();
    document.getElementById("custom-jd-text").value = data.extracted_text;
    badge.innerText = `${file.name} (${data.extracted_skills.length} skills found)`;
    await matchCustomJobDescription();
  } catch (err) {
    console.error("JD upload error:", err);
    badge.innerText = "Upload failed";
    alert("Could not process job description document.");
  }
}

function handleTargetRoleChange() {
  const currentText = document.getElementById("custom-jd-text").value.trim();
  if (currentText) {
    matchCustomJobDescription();
  }
}

async function matchCustomJobDescription() {
  if (!currentProfile) {
    alert("Please load or upload a resume first!");
    return;
  }

  const role = document.getElementById("custom-target-role").value;
  let text = document.getElementById("custom-jd-text").value.trim();

  if (!text) {
    text = `Looking for a skilled ${role} to join our engineering team. Must have strong foundational competencies in modern software and analytical toolkits.`;
    document.getElementById("custom-jd-text").value = text;
  }

  try {
    const res = await fetch("/api/jobs/match-custom", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        candidate: currentProfile,
        target_role: role,
        job_title: `Custom: ${role}`,
        company: "Target Employer",
        job_description: text
      })
    });

    if (!res.ok) {
      alert("Failed to evaluate job description.");
      return;
    }

    const data = await res.json();
    customJobMatch = data.match;
    customJobObj = data.job;

    const box = document.getElementById("custom-match-result-box");
    box.style.display = "block";
    document.getElementById("custom-result-title").innerText = customJobMatch.job_title;
    document.getElementById("custom-result-role").innerText = `Target Role: ${role}`;
    document.getElementById("custom-result-score").innerText = `${customJobMatch.overall_match_score}%`;
    document.getElementById("custom-matched-count").innerText = `${customJobMatch.matched_skills.length} skills (${customJobMatch.matched_skills.slice(0, 4).join(", ") || "None"})`;
    document.getElementById("custom-missing-count").innerText = `${customJobMatch.missing_skills.length} skills (${customJobMatch.missing_skills.slice(0, 3).join(", ") || "None"})`;

    document.getElementById("custom-jd-status-badge").innerText = "Match Calculated";
  } catch (err) {
    console.error("Custom match error:", err);
  }
}

function clearCustomJd() {
  document.getElementById("custom-jd-text").value = "";
  document.getElementById("custom-match-result-box").style.display = "none";
  document.getElementById("custom-jd-status-badge").innerText = "Paste Text or Upload";
  customJobMatch = null;
  customJobObj = null;
}

function viewCustomJobInMatchingTab() {
  if (!customJobMatch) return;
  selectJob(customJobMatch);
  switchTab("tab-matching");
}

function openSimulatorForCustomJob() {
  if (!customJobMatch) return;
  selectedJobMatch = customJobMatch;
  openSimulatorForJob();
}

function openRoadmapForCustomJob() {
  if (!customJobMatch) return;
  selectedJobMatch = customJobMatch;
  openRoadmapForJob();
}

// =========================================================================
// 10. MARKET ANALYTICS CHARTS (CHART.JS)
// =========================================================================
async function fetchMarketAnalytics() {
  try {
    const res = await fetch("/api/analytics/market");
    if (res.ok) {
      marketData = await res.json();
    }
  } catch (e) {
    console.warn("Market analytics load failed:", e);
  }
}

function renderMarketCharts() {
  if (!marketData) return;

  const skillsCtx = document.getElementById("market-skills-chart");
  if (skillsCtx) {
    if (skillsChartInstance) skillsChartInstance.destroy();
    const topSkills = marketData.top_demanded_skills || [];
    skillsChartInstance = new Chart(skillsCtx, {
      type: "bar",
      data: {
        labels: topSkills.map(s => s.skill),
        datasets: [{
          label: "Job Demand Frequency (%)",
          data: topSkills.map(s => s.demand_percentage),
          backgroundColor: "rgba(79, 70, 229, 0.75)",
          borderColor: "#6366f1",
          borderWidth: 1,
          borderRadius: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          y: { beginAtZero: true, grid: { color: "rgba(255,255,255,0.05)" }, ticks: { color: "#94a3b8" } },
          x: { grid: { display: false }, ticks: { color: "#94a3b8" } }
        }
      }
    });
  }

  const salCtx = document.getElementById("salary-chart");
  if (salCtx) {
    if (salaryChartInstance) salaryChartInstance.destroy();
    const salaries = marketData.salary_by_role || [];
    salaryChartInstance = new Chart(salCtx, {
      type: "bar",
      data: {
        labels: salaries.map(s => s.role.replace(" Engineer", "")),
        datasets: [
          {
            label: "Entry Level (₹ LPA)",
            data: salaries.map(s => s.entry_level_lpa),
            backgroundColor: "rgba(16, 185, 129, 0.7)",
            borderRadius: 4
          },
          {
            label: "Senior Level (₹ LPA)",
            data: salaries.map(s => s.senior_level_lpa),
            backgroundColor: "rgba(139, 92, 246, 0.7)",
            borderRadius: 4
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { labels: { color: "#cbd5e1" } } },
        scales: {
          y: { beginAtZero: true, grid: { color: "rgba(255,255,255,0.05)" }, ticks: { color: "#94a3b8" } },
          x: { grid: { display: false }, ticks: { color: "#94a3b8" } }
        }
      }
    });
  }

  const clusterCtx = document.getElementById("pca-cluster-chart");
  if (clusterCtx) {
    if (clusterChartInstance) clusterChartInstance.destroy();
    const points = marketData.cluster_points || [];
    const clusterColors = ["#6366f1", "#10b981", "#f59e0b", "#ec4899", "#06b6d4"];
    const datasets = [];

    for (let c = 0; c < 5; c++) {
      const cPoints = points.filter(p => p.cluster_id === c);
      const cName = cPoints[0]?.cluster_name || `Cluster ${c}`;
      datasets.push({
        label: cName,
        data: cPoints.map(p => ({ x: p.x, y: p.y, title: p.title, company: p.company })),
        backgroundColor: clusterColors[c],
        pointRadius: 5
      });
    }

    clusterChartInstance = new Chart(clusterCtx, {
      type: "scatter",
      data: { datasets },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { labels: { color: "#cbd5e1" } },
          tooltip: {
            callbacks: {
              label: (ctx) => `${ctx.raw.title} (${ctx.raw.company})`
            }
          }
        },
        scales: {
          x: { title: { display: true, text: "Principal Component 1", color: "#94a3b8" }, ticks: { color: "#94a3b8" }, grid: { color: "rgba(255,255,255,0.05)" } },
          y: { title: { display: true, text: "Principal Component 2", color: "#94a3b8" }, ticks: { color: "#94a3b8" }, grid: { color: "rgba(255,255,255,0.05)" } }
        }
      }
    });
  }
}

// =========================================================================
// 11. CAREER COPILOT AI CHAT
// =========================================================================
function toggleChat() {
  const drawer = document.getElementById("chat-drawer");
  drawer.style.display = drawer.style.display === "flex" ? "none" : "flex";
}

async function sendChatMessage() {
  const input = document.getElementById("chat-input");
  const query = input.value.trim();
  if (!query) return;

  const msgs = document.getElementById("chat-messages");

  const userDiv = document.createElement("div");
  userDiv.className = "chat-msg user";
  userDiv.innerText = query;
  msgs.appendChild(userDiv);
  input.value = "";
  msgs.scrollTop = msgs.scrollHeight;

  const botDiv = document.createElement("div");
  botDiv.className = "chat-msg bot";
  botDiv.innerText = "Analyzing career context...";
  msgs.appendChild(botDiv);
  msgs.scrollTop = msgs.scrollHeight;

  try {
    const res = await fetch("/api/copilot/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        query: query,
        context: {
          candidate: currentProfile,
          target_job: selectedJobMatch || {},
          match_info: selectedJobMatch || {}
        }
      })
    });

    if (res.ok) {
      const data = await res.json();
      botDiv.innerHTML = data.reply.replace(/\n/g, "<br>").replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
    } else {
      botDiv.innerText = "Sorry, I had trouble answering that. Please try again.";
    }
  } catch (err) {
    botDiv.innerText = "Network error connecting to Copilot API.";
  }
  msgs.scrollTop = msgs.scrollHeight;
}
