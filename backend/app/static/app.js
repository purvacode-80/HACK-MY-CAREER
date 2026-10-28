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
let liveJobsData = [];
let selectedLiveJobId = null;

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
    // 0. Initialize Light/Dark Theme
    initTheme();

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
      dashboard.style.display = "flex";
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
  const sidebarAvatar = document.getElementById("sidebar-user-avatar");

  if (currentUser) {
    const displayName = currentUser.name || "Candidate";
    const initial = (currentUser.name || "U")[0].toUpperCase();
    if (nameEl) nameEl.innerText = displayName;
    if (avatarEl) avatarEl.innerText = initial;
    if (sidebarAvatar) sidebarAvatar.innerText = initial;
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

  // Sync breadcrumb title in topbar
  const titles = {
    "tab-resume": "Resume Intelligence & ATS",
    "tab-matching": "Job Matching & Skill Gap",
    "tab-live-jobs": "Real-World Live Jobs",
    "tab-simulator": "What-If Simulator",
    "tab-roadmap": "Learning Roadmap",
    "tab-market": "Market Analytics & Clusters",
    "tab-history": "Saved Resumes (Atlas)"
  };
  const titleEl = document.getElementById("topbar-current-tab");
  if (titleEl && titles[tabId]) titleEl.innerText = titles[tabId];

  // Close mobile sidebar if open
  const sidebar = document.getElementById("sidebar-nav");
  if (sidebar) sidebar.classList.remove("mobile-open");

  if (tabId === "tab-market") {
    setTimeout(renderMarketCharts, 100);
  }
  if (tabId === "tab-history") {
    fetchUserResumes();
  }
  if (tabId === "tab-live-jobs") {
    if (!liveJobsData || liveJobsData.length === 0) {
      fetchLiveJobs();
    }
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

  // 2b. Update Live Jobs Active Candidate Status
  const liveCandEl = document.getElementById("live-matching-candidate-label");
  if (liveCandEl) {
    liveCandEl.innerHTML = `<strong>${profile.name || "Candidate"}</strong> (${(profile.skills || []).length} Skills Detected) • Dynamic 5-Factor Score Active`;
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

  // 8b. Update ATS Completeness Health badge & metric bars
  const atsBadge = document.getElementById("ats-badge");
  if (atsBadge) {
    atsBadge.textContent = `${ats}/100`;
    atsBadge.className = ats >= 75 ? "badge badge-matched" : ats >= 50 ? "badge badge-missing" : "badge badge-neutral";
  }

  // Contact & Links Integrity — score based on email + phone + linkedin presence
  const hasEmail = !!(profile.email || (profile.contact && profile.contact.email));
  const hasPhone = !!(profile.phone || (profile.contact && profile.contact.phone));
  const hasLinkedin = !!(profile.linkedin || (profile.contact && profile.contact.linkedin));
  const contactScore = Math.round(((hasEmail ? 40 : 0) + (hasPhone ? 30 : 0) + (hasLinkedin ? 30 : 0)));
  const contactValEl = document.getElementById("metric-contact-val");
  const contactBarEl = document.getElementById("metric-contact-bar");
  if (contactValEl) contactValEl.textContent = `${contactScore}%`;
  if (contactBarEl) contactBarEl.style.width = `${contactScore}%`;

  // Extracted Skills Density — based on number of skills detected
  const skillCount = (profile.skills || []).length;
  const skillScore = Math.min(100, Math.round(skillCount * 6));
  const skillValEl = document.getElementById("metric-skills-val");
  const skillBarEl = document.getElementById("metric-skills-bar");
  if (skillValEl) skillValEl.textContent = `${skillCount} skills (${skillScore}%)`;
  if (skillBarEl) skillBarEl.style.width = `${skillScore}%`;

  // Project Depth & Technical Validation — based on projects count
  const projCount = (profile.projects || []).length;
  const projScore = Math.min(100, Math.round(projCount * 20));
  const projValEl = document.getElementById("metric-proj-val");
  const projBarEl = document.getElementById("metric-proj-bar");
  if (projValEl) projValEl.textContent = `${projCount} projects (${projScore}%)`;
  if (projBarEl) projBarEl.style.width = `${projScore}%`;

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

    // Update Cohort Benchmark widget with new ATS score
    const atsScore = parsedProfile.ats_score || parsedProfile.match_score || 70;
    const targetRole = parsedProfile.target_role || parsedProfile.primary_role || "Data Scientist";
    updateCohortBenchmark(atsScore, targetRole);

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
      <div class="job-meta-scores">
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
function renderRoadmap(data) {
  if (!data) return;
  const hoursBadge = document.getElementById("roadmap-hours-badge");
  if (hoursBadge) {
    hoursBadge.innerText = `${data.total_estimated_hours || 40} Total Hours • ${data.estimated_completion_weeks || 4} Weeks`;
  }
  
  const container = document.getElementById("roadmap-timeline");
  if (!container) return;
  container.innerHTML = "";

  const steps = data.steps || [];
  if (steps.length === 0) {
    container.innerHTML = `<div style="text-align:center; padding:2rem; color:var(--text-muted);">No roadmap steps generated for this role.</div>`;
    return;
  }

  steps.forEach(step => {
    const stepDiv = document.createElement("div");
    stepDiv.className = "timeline-step";
    stepDiv.innerHTML = `
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.5rem;">
        <strong class="timeline-step-title">Step ${step.step_number}: Master ${escapeHtml(step.skill)}</strong>
        <span class="badge badge-neutral">${escapeHtml(step.difficulty || "Intermediate")} • ${step.estimated_hours || 10} Hours</span>
      </div>
      <p class="timeline-step-summary">${escapeHtml(step.summary || "")}</p>
      
      <div class="timeline-step-heading">KEY MILESTONES:</div>
      <ul class="timeline-milestones-list">
        ${(step.milestones || []).map(m => `<li>${escapeHtml(m)}</li>`).join("")}
      </ul>

      <div class="timeline-capstone-box">
        <strong style="color:var(--success);">💡 Capstone Project Idea:</strong> ${escapeHtml(step.project_idea || "")}
      </div>

      <div style="display:flex; gap:0.5rem; flex-wrap:wrap;">
        ${(step.tutorials || []).map(t => `<a href="${t.url}" target="_blank" class="sample-btn timeline-tutorial-link" style="text-decoration:none; display:inline-flex; align-items:center; gap:0.3rem;">🔗 ${escapeHtml(t.title)}</a>`).join("")}
      </div>
    `;
    container.appendChild(stepDiv);
  });
}

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
    renderRoadmap(data);
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
// 11. CAREER COPILOT AI CHAT (RIGHT SIDEBAR DRAWER)
// =========================================================================
function toggleChat() {
  const drawer = document.getElementById("chat-drawer");
  const backdrop = document.getElementById("chat-backdrop");
  if (!drawer) return;
  const isOpen = drawer.classList.contains("open");
  if (isOpen) {
    drawer.classList.remove("open");
    if (backdrop) backdrop.classList.remove("open");
  } else {
    drawer.classList.add("open");
    if (backdrop) backdrop.classList.add("open");
    const input = document.getElementById("chat-input");
    if (input) setTimeout(() => input.focus(), 250);
  }
}

function toggleMobileSidebar() {
  const sidebar = document.getElementById("sidebar-nav");
  if (sidebar) sidebar.classList.toggle("mobile-open");
}

function toggleGeminiKeyInput() {
  const box = document.getElementById("gemini-key-box");
  if (!box) return;
  const isHidden = box.style.display === "none";
  box.style.display = isHidden ? "block" : "none";
  if (isHidden) {
    const input = document.getElementById("gemini-key-input");
    if (input) {
      input.value = localStorage.getItem("hmc_gemini_key") || "";
      input.focus();
    }
  }
}

function saveGeminiKey() {
  const input = document.getElementById("gemini-key-input");
  if (!input) return;
  const key = input.value.trim();
  if (key) {
    localStorage.setItem("hmc_gemini_key", key);
    showToast("Gemini API key saved!", "success");
    const ind = document.getElementById("copilot-model-indicator");
    if (ind) ind.innerText = "⚡ Gemini 1.5 Flash Connected";
  } else {
    localStorage.removeItem("hmc_gemini_key");
    showToast("Cleared Gemini key. Using Smart Advisor.", "info");
    const ind = document.getElementById("copilot-model-indicator");
    if (ind) ind.innerText = "⚡ Smart Career Advisor Ready";
  }
  const box = document.getElementById("gemini-key-box");
  if (box) box.style.display = "none";
}

function askPreset(text) {
  const input = document.getElementById("chat-input");
  if (input) {
    input.value = text;
    sendChatMessage();
  }
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
  botDiv.innerHTML = "<em>Analyzing career context & market data...</em>";
  msgs.appendChild(botDiv);
  msgs.scrollTop = msgs.scrollHeight;

  const savedGeminiKey = localStorage.getItem("hmc_gemini_key") || "";

  try {
    const res = await fetch("/api/copilot/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        query: query,
        context: {
          candidate: currentProfile || {},
          target_job: selectedJobMatch || {},
          match_info: selectedJobMatch || {},
          gemini_api_key: savedGeminiKey
        }
      })
    });

    if (res.ok) {
      const data = await res.json();
      let replyHtml = (data.reply || "")
        .replace(/^### (.*$)/gim, '<h3>$1</h3>')
        .replace(/^## (.*$)/gim, '<h3>$1</h3>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/`([^`]+)`/g, '<code>$1</code>')
        .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer" style="color:var(--primary-light);font-weight:700;text-decoration:underline;">$1 ➔</a>')
        .replace(/\n/g, '<br>');

      botDiv.innerHTML = replyHtml;
    } else {
      botDiv.innerText = "Sorry, I had trouble answering that. Please try again.";
    }
  } catch (err) {
    botDiv.innerText = "Network error connecting to Copilot API.";
  }
  msgs.scrollTop = msgs.scrollHeight;
}

// =========================================================================
// THEME MANAGEMENT (LIGHT / DARK THEME)
// =========================================================================
function initTheme() {
  const saved = localStorage.getItem("hmc_theme") || "dark";
  if (saved === "light") {
    document.body.classList.add("light-theme");
  } else {
    document.body.classList.remove("light-theme");
  }
  updateThemeUI(saved);
}

function toggleTheme() {
  const isLight = document.body.classList.toggle("light-theme");
  const theme = isLight ? "light" : "dark";
  localStorage.setItem("hmc_theme", theme);
  updateThemeUI(theme);
}

function updateThemeUI(theme) {
  const isLight = theme === "light";
  const icon = isLight ? "☀️" : "🌙";
  const label = isLight ? "Light Mode" : "Dark Mode";

  const btnIcon = document.getElementById("theme-btn-icon");
  const btnText = document.getElementById("theme-btn-text");
  const topIcon = document.getElementById("topbar-theme-icon");

  if (btnIcon) btnIcon.innerText = icon;
  if (btnText) btnText.innerText = label;
  if (topIcon) topIcon.innerText = icon;
}

// =========================================================================
// 12. REAL-WORLD LIVE JOBS (NAUKRI.COM, LINKEDIN, INDEED, ADZUNA)
// =========================================================================
function applyLiveJobPreset(role, location) {
  const qEl = document.getElementById("live-job-query");
  const locEl = document.getElementById("live-job-location");
  if (qEl) qEl.value = role;
  if (locEl) locEl.value = location;
  fetchLiveJobs();
}

async function fetchLiveJobs() {
  const qEl = document.getElementById("live-job-query");
  const locEl = document.getElementById("live-job-location");
  const portalEl = document.getElementById("live-job-portal");
  const btn = document.getElementById("btn-live-search");
  const container = document.getElementById("live-jobs-container");
  const statBadge = document.getElementById("live-jobs-stat-badge");

  const query = (qEl ? qEl.value : "Data Scientist").trim();
  const location = (locEl ? locEl.value : "").trim();
  const portal = portalEl ? portalEl.value : "all";

  if (btn) {
    btn.disabled = true;
    btn.innerHTML = `<span>⏳ Searching Portals...</span>`;
  }
  if (container) {
    container.innerHTML = `
      <div style="grid-column: 1/-1; text-align: center; padding: 3rem 1rem; color: var(--text-muted);">
        <div style="font-size: 2.2rem; margin-bottom: 0.75rem;">🌐</div>
        <p style="font-size: 1.05rem; color: white; font-weight: 700;">Querying Live Market & Parsing Requirements...</p>
        <p style="font-size: 0.85rem; margin-top: 0.35rem; color: var(--text-muted);">
          Extracting skills via NLP Taxonomy Engine & scoring against active resume using 5-Factor composite formula
        </p>
      </div>
    `;
  }

  try {
    const res = await fetch("/api/jobs/live-search", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        query: query,
        location: location,
        portal_filter: portal,
        candidate: currentProfile,
        max_results: 25
      })
    });

    if (!res.ok) {
      throw new Error(`Server returned HTTP ${res.status}`);
    }

    const data = await res.json();
    liveJobsData = data.jobs || [];
    renderLiveJobs(liveJobsData);

    if (statBadge) {
      statBadge.innerText = `Showing ${liveJobsData.length} Real-World Jobs`;
    }
  } catch (err) {
    console.error("Live jobs search failed:", err);
    if (container) {
      container.innerHTML = `
        <div style="grid-column: 1/-1; text-align: center; padding: 2.5rem; background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: var(--radius-md);">
          <div style="font-size: 1.8rem; margin-bottom: 0.5rem;">⚠️</div>
          <p style="color: #fca5a5; font-weight: 700;">Could not connect to Live Job Aggregator</p>
          <p style="color: var(--text-muted); font-size: 0.85rem; margin-top: 0.3rem;">${err.message}</p>
          <button class="btn btn-primary" style="margin-top: 1rem;" onclick="fetchLiveJobs()">Try Again</button>
        </div>
      `;
    }
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.innerHTML = `<span>🔍 Search Real Jobs</span>`;
    }
  }
}

function renderLiveJobs(jobs) {
  const container = document.getElementById("live-jobs-container");
  if (!container) return;

  if (!jobs || jobs.length === 0) {
    container.innerHTML = `
      <div style="grid-column: 1/-1; text-align: center; padding: 3rem 1rem; color: var(--text-muted); background: rgba(19, 29, 49, 0.4); border-radius: var(--radius-lg); border: 1px dashed var(--border);">
        <div style="font-size: 2rem; margin-bottom: 0.5rem;">🔍</div>
        <p style="color: white; font-weight: 600;">No live jobs found matching your search criteria.</p>
        <p style="font-size: 0.85rem; margin-top: 0.25rem;">Try broadening your role title or selecting 'All Portals'.</p>
      </div>
    `;
    return;
  }

  container.innerHTML = jobs.map(job => {
    // Portal styling
    let portalClass = "portal-naukri";
    const src = (job.source || "").toLowerCase();
    if (src.includes("linkedin")) portalClass = "portal-linkedin";
    else if (src.includes("indeed")) portalClass = "portal-indeed";
    else if (src.includes("adzuna")) portalClass = "portal-adzuna";

    // Match score formatting
    let scoreHtml = "";
    if (job.match_score !== null && job.match_score !== undefined) {
      const s = Number(job.match_score);
      let scoreClass = "score-high";
      if (s < 60) scoreClass = "score-moderate";
      else if (s < 75) scoreClass = "score-medium";

      scoreHtml = `
        <div class="live-job-score-badge ${scoreClass}">
          <span>🎯</span>
          <span>${s.toFixed(1)}% Match</span>
        </div>
        <span class="live-score-formula-label">
          5-Factor Composite
        </span>
      `;
    } else {
      scoreHtml = `
        <div class="live-job-score-badge score-moderate">
          <span>📄</span>
          <span style="font-size: 0.82rem;">Awaiting Resume Upload</span>
        </div>
        <button class="sample-btn" style="padding: 0.2rem 0.5rem; font-size: 0.72rem;" onclick="switchTab('tab-resume')">
          Upload Now
        </button>
      `;
    }

    // Matched skills tags
    const matched = job.matched_skills || [];
    const missing = job.missing_skills || [];
    const reqSkills = job.required_skills || [];

    let skillsHtml = "";
    if (matched.length > 0) {
      skillsHtml += `
        <div class="live-skills-title live-skills-matched-title">✓ Matched Resume Skills (${matched.length})</div>
        <div class="live-skills-wrap">
          ${matched.map(sk => `<span class="live-skill-tag tag-matched">✓ ${sk}</span>`).join("")}
        </div>
      `;
    }
    if (missing.length > 0) {
      skillsHtml += `
        <div class="live-skills-title live-skills-missing-title">✗ Skill Gaps to Learn (${missing.length})</div>
        <div class="live-skills-wrap">
          ${missing.slice(0, 6).map(sk => `<span class="live-skill-tag tag-missing">✗ ${sk}</span>`).join("")}
        </div>
      `;
    } else if (matched.length === 0 && reqSkills.length > 0) {
      skillsHtml += `
        <div class="live-skills-title" style="color:#a5b4fc;">★ Employer Required Skills (${reqSkills.length})</div>
        <div class="live-skills-wrap">
          ${reqSkills.slice(0, 6).map(sk => `<span class="live-skill-tag tag-req">${sk}</span>`).join("")}
        </div>
      `;
    }

    return `
      <div class="live-job-card">
        <div>
          <!-- Header: Portal badge & Salary -->
          <div class="live-job-header">
            <span class="live-job-portal-badge ${portalClass}">
              ${job.source_badge || job.source || "Job Portal"}
            </span>
            <span class="live-job-salary">${job.salary_range || "Market Standard"}</span>
          </div>

          <!-- Title & Company -->
          <h3 class="live-job-title">${escapeHtml(job.title)}</h3>
          <div class="live-job-company">
            <span>🏢</span>
            <span>${escapeHtml(job.company)}</span>
          </div>

          <!-- Metadata row -->
          <div class="live-job-meta-row">
            <div class="live-job-meta-item">
              <span>📍</span>
              <span>${escapeHtml(job.location || "India")}</span>
            </div>
            <div class="live-job-meta-item">
              <span>🕒</span>
              <span>${escapeHtml(job.posted_at || "Recent")}</span>
            </div>
            <div class="live-job-meta-item">
              <span>🎓</span>
              <span>${job.min_experience_years || 1}+ yrs exp</span>
            </div>
          </div>

          <!-- Match Score Ribbon -->
          <div class="live-job-score-container">
            ${scoreHtml}
          </div>

          <!-- Description snippet -->
          <p class="live-job-desc">${escapeHtml(job.description || "")}</p>

          <!-- Skills breakdown -->
          <div class="live-job-skills-section">
            ${skillsHtml}
          </div>
        </div>

        <!-- Footer Actions -->
        <div class="live-job-footer">
          <a href="${job.apply_url || '#'}" target="_blank" rel="noopener noreferrer" class="btn-apply-portal" title="Direct live application link on ${job.source}">
            <span>Apply on ${job.source} ➔</span>
          </a>
          ${job.careers_url ? `
            <a href="${job.careers_url}" target="_blank" rel="noopener noreferrer" class="btn-job-action-sm" style="text-decoration:none; display:inline-flex; align-items:center; gap:0.3rem;" title="Visit official careers portal for ${escapeHtml(job.company)}">
              <span>🏢 Careers</span>
            </a>
          ` : ''}
          <button class="btn-job-action-sm" onclick="simulateLiveJob('${job.id}')" title="Test skill impact in simulator">
            ⚡ What-If
          </button>
          <button class="btn-job-action-sm" onclick="roadmapLiveJob('${job.id}')" title="Generate learning curriculum">
            🗺️ Roadmap
          </button>
          <button class="btn-job-action-sm" onclick="openResumeTailorForLiveJob('${job.id}')" title="Generate AI-tailored resume bullets for this role" style="background:rgba(236,72,153,0.14);border-color:rgba(236,72,153,0.35);color:#f9a8d4;">
            ✨ AI Tailor
          </button>
        </div>
      </div>
    `;
  }).join("");
}

function simulateLiveJob(jobId) {
  const job = liveJobsData.find(j => j.id === jobId);
  if (!job) return;

  switchTab("tab-simulator");

  const targetRoleEl = document.getElementById("sim-target-role");
  const targetCompanyEl = document.getElementById("sim-target-company");
  const origScoreEl = document.getElementById("sim-orig-score");
  const newScoreEl = document.getElementById("sim-new-score");
  const deltaBadge = document.getElementById("sim-delta-badge");
  const container = document.getElementById("sim-skill-checkboxes");

  if (targetRoleEl) targetRoleEl.innerText = job.title;
  if (targetCompanyEl) targetCompanyEl.innerText = `${job.company} (${job.source})`;
  
  const currentScore = job.match_score !== null && job.match_score !== undefined ? job.match_score : 50;
  if (origScoreEl) origScoreEl.innerText = `${currentScore}%`;
  if (newScoreEl) newScoreEl.innerText = `${currentScore}%`;
  if (deltaBadge) deltaBadge.innerText = "+0.0% Increase";

  selectedSimSkills.clear();

  if (container) {
    container.innerHTML = "";
    const candidateCurrent = new Set(currentProfile ? currentProfile.skills || [] : []);
    // Use a Set to deduplicate — missing_skills and required_skills often overlap
    const seenSkills = new Set();
    const targetSkills = [];
    [...(job.missing_skills || []), ...(job.required_skills || [])].forEach(sk => {
      if (!seenSkills.has(sk)) { seenSkills.add(sk); targetSkills.push(sk); }
    });

    const extraPool = ["Docker", "AWS", "Kubernetes", "PyTorch", "FastAPI", "PostgreSQL", "MLOps"];
    extraPool.forEach(sk => {
      if (!candidateCurrent.has(sk) && !seenSkills.has(sk)) {
        seenSkills.add(sk);
        targetSkills.push(sk);
      }
    });

    targetSkills.forEach(skill => {
      if (candidateCurrent.has(skill)) return;
      const label = document.createElement("label");
      label.className = "checkbox-item";
      label.innerHTML = `
        <input type="checkbox" value="${skill}" onchange="toggleSimSkill('${skill}')">
        <span>+ ${skill}</span>
      `;
      container.appendChild(label);
    });
  }
}

async function roadmapLiveJob(jobId) {
  const job = liveJobsData.find(j => j.id === jobId);
  if (!job) return;

  switchTab("tab-roadmap");

  const roleEl = document.getElementById("roadmap-role-title");
  if (roleEl) roleEl.innerText = `${job.title} @ ${job.company}`;

  const missing = job.missing_skills && job.missing_skills.length > 0 ? job.missing_skills : (job.required_skills || ["Docker", "AWS", "PyTorch"]);

  try {
    const res = await fetch("/api/learning/roadmap", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        missing_skills: missing,
        target_role: job.role || "Data Scientist"
      })
    });

    if (res.ok) {
      const data = await res.json();
      renderRoadmap(data);
    }
  } catch (e) {
    console.error("Roadmap generation failed for live job:", e);
  }
}

function escapeHtml(text) {
  if (!text) return "";
  const map = {
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#039;"
  };
  return String(text).replace(/[&<>"']/g, m => map[m]);
}

// =========================================================================
// REAL-WORLD FEATURE 1: GITHUB PORTFOLIO CODE EVIDENCE SCANNER
// =========================================================================
async function scanGitHubPortfolio() {
  const input = document.getElementById("github-username-input");
  const btn   = document.getElementById("btn-scan-github");
  const badge = document.getElementById("github-verify-badge");
  const container = document.getElementById("github-results-container");

  if (!input || !input.value.trim()) {
    showToast("⚠️ Please enter a GitHub username or URL", "warning");
    return;
  }

  const username = input.value.trim();
  btn.disabled = true;
  btn.innerHTML = `<span>⏳ Scanning Code Evidence…</span>`;
  badge.textContent = "Scanning…";
  badge.className = "badge badge-neutral";

  try {
    const res = await fetch("/api/portfolio/scan-github", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ profile_url_or_username: username })
    });

    if (!res.ok) throw new Error(await res.text());
    const data = await res.json();

    badge.textContent = `Score ${data.evidence_score}/100`;
    badge.className = data.evidence_score >= 70
      ? "badge badge-matched"
      : data.evidence_score >= 40
        ? "badge badge-missing"
        : "badge badge-neutral";

    container.style.display = "block";
    container.innerHTML = renderGitHubResults(data);

  } catch(e) {
    console.error("GitHub scan error:", e);
    badge.textContent = "Scan Failed";
    badge.className = "badge badge-missing";
    container.style.display = "block";
    container.innerHTML = `<div style="color:#fca5a5; font-size:0.85rem; padding:0.75rem;">
      ⚠️ Could not scan GitHub profile. Check username or network and try again.
    </div>`;
  } finally {
    btn.disabled = false;
    btn.innerHTML = `<span>⚡ Verify Code Evidence</span>`;
  }
}

function renderGitHubResults(data) {
  // Backend returns: top_languages (array), verified_skills (array of objects), repo_highlights (array)
  const topLangs = data.top_languages || [];       // [{language, repos}]
  const verified = data.verified_skills || [];      // [{skill, evidence_type, repo_count, confidence}]
  const repos = data.repo_highlights || [];         // top repos
  const totalStars = data.total_stars || 0;
  const repoCount = data.public_repos_count || data.public_repo_count || 0;
  const scoreColor = data.evidence_score >= 70 ? "#34d399" : data.evidence_score >= 40 ? "#f59e0b" : "#ef4444";

  // Language bars — from top_languages array
  const langMax = Math.max(...topLangs.map(l => l.repos || 0), 1);
  const langBars = topLangs.slice(0, 6).map(l => `
    <div class="github-lang-bar-wrap">
      <div class="github-lang-bar-label">
        <span>${escapeHtml(l.language)}</span><span>${l.repos} repo${l.repos !== 1 ? 's' : ''}</span>
      </div>
      <div class="github-lang-bar-bg">
        <div class="github-lang-bar-fill" style="width:${Math.round((l.repos/langMax)*100)}%"></div>
      </div>
    </div>
  `).join("");

  // Verified skill badges — extract .skill string from objects
  const skillBadges = verified.map(sk => {
    const skillName = typeof sk === "object" ? (sk.skill || String(sk)) : String(sk);
    const conf = typeof sk === "object" && sk.confidence ? ` (${sk.confidence}%)` : "";
    return `<span class="github-verified-tag" title="${escapeHtml(sk.evidence_type || 'Code Evidence')}${conf}">✅ ${escapeHtml(skillName)}</span>`;
  }).join(" ");

  // Top repo cards — from repo_highlights
  const repoCards = repos.slice(0, 6).map(r => `
    <div class="github-repo-card">
      <div class="github-repo-name" title="${escapeHtml(r.name)}">
        📁 ${escapeHtml(r.name)}
      </div>
      <div class="github-repo-meta">
        <span>⭐ ${r.stars || 0}</span>
        <span>${escapeHtml(r.language || "—")}</span>
        ${r.updated_at ? `<span>${r.updated_at}</span>` : ""}
      </div>
      ${r.description && r.description !== "No description provided" ? `<div style="font-size:0.74rem; color:var(--text-muted); margin-top:0.3rem;">${escapeHtml(r.description.slice(0,80))}${r.description.length>80?"…":""}</div>` : ""}
    </div>
  `).join("");

  return `
    <!-- Summary Stats -->
    <div style="display:flex; gap:0.6rem; flex-wrap:wrap; margin-bottom:1.25rem; align-items:center;">
      <div class="github-stat-pill">
        <span style="font-size:1.1rem; font-weight:900; color:${scoreColor};">${data.evidence_score}</span>
        <span>/ 100 Score</span>
      </div>
      <div class="github-stat-pill">📁 ${repoCount} Public Repos</div>
      <div class="github-stat-pill">⭐ ${totalStars} Stars</div>
      <div class="github-stat-pill">✅ ${verified.length} Skills Verified</div>
    </div>

    <!-- Verified Skills -->
    ${verified.length > 0 ? `
    <div style="margin-bottom:1.25rem;">
      <div style="font-size:0.78rem; font-weight:700; color:#a5b4fc; text-transform:uppercase; letter-spacing:0.5px; margin-bottom:0.5rem;">
        ✅ Code-Verified Skills
      </div>
      <div style="display:flex; flex-wrap:wrap; gap:0.4rem;">${skillBadges}</div>
    </div>` : ""}

    <!-- Language Breakdown -->
    ${langBars ? `
    <div style="margin-bottom:1.25rem;">
      <div style="font-size:0.78rem; font-weight:700; color:#a5b4fc; text-transform:uppercase; letter-spacing:0.5px; margin-bottom:0.65rem;">
        📊 Language Distribution
      </div>
      ${langBars}
    </div>` : ""}

    <!-- Top Repos -->
    ${repos.length > 0 ? `
    <div>
      <div style="font-size:0.78rem; font-weight:700; color:#a5b4fc; text-transform:uppercase; letter-spacing:0.5px; margin-bottom:0.65rem;">
        🏆 Top Repositories
      </div>
      <div class="github-results-grid">${repoCards}</div>
    </div>` : ""}
  `;
}

// =========================================================================
// REAL-WORLD FEATURE 2: AI RESUME TAILOR MODAL
// =========================================================================
let _tailorBulletsCache = [];

async function openResumeTailorForSelectedJob() {
  const selected = liveJobsData && liveJobsData.length > 0
    ? liveJobsData.find(j => j.id === selectedLiveJobId) || liveJobsData[0]
    : null;

  const jobTitle   = selected ? selected.title   : (document.getElementById("job-title-output")  ?.innerText || "Data Scientist");
  const company    = selected ? selected.company  : (document.getElementById("job-company-output")?.innerText || "Target Company");
  const reqSkills  = selected ? (selected.required_skills || []) : [];
  const missSkills = selected ? (selected.missing_skills  || []) : [];
  const candSkills = currentProfile ? (currentProfile.skills || []) : [];

  openResumeTailorModal(jobTitle, company, reqSkills, missSkills, candSkills);
}

async function openResumeTailorForLiveJob(jobId) {
  const job = liveJobsData && liveJobsData.find(j => j.id === jobId);
  if (!job) return;

  openResumeTailorModal(
    job.title, job.company,
    job.required_skills || [],
    job.missing_skills  || [],
    currentProfile ? (currentProfile.skills || []) : []
  );
}

async function openResumeTailorModal(jobTitle, company, reqSkills, missSkills, candSkills) {
  const modal = document.getElementById("resume-tailor-modal");
  if (!modal) return;

  // Reset & show
  document.getElementById("tailor-modal-title").textContent = `AI Optimizer: ${jobTitle}`;
  document.getElementById("tailor-modal-subtitle").textContent = `Tailored STAR bullets for ${company} — bridging your skill gaps`;
  document.getElementById("tailor-modal-meta").textContent    = `${jobTitle} @ ${company}`;
  document.getElementById("tailor-uplift-badge").textContent  = "+??%";
  document.getElementById("tailor-bullets-container").innerHTML = `
    <div style="color:var(--text-muted); font-size:0.85rem; padding:1rem; text-align:center;">
      ⏳ Generating AI bullets…
    </div>`;
  document.getElementById("tailor-keywords-list").innerHTML = "";
  document.getElementById("tailor-verbs-list").innerHTML    = "";
  modal.style.display = "flex";
  _tailorBulletsCache = [];

  try {
    const res = await fetch("/api/resume/tailor-bullets", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        job_title: jobTitle,
        company: company,
        target_role: jobTitle,
        required_skills: reqSkills,
        missing_skills:  missSkills,
        candidate_skills: candSkills
      })
    });

    if (!res.ok) throw new Error(await res.text());
    const data = await res.json();
    renderTailoredBullets(data);

  } catch(e) {
    console.error("Resume tailor error:", e);
    document.getElementById("tailor-bullets-container").innerHTML = `
      <div style="color:#fca5a5; font-size:0.85rem; padding:0.75rem;">
        ⚠️ Could not generate bullets. Check server and try again.
      </div>`;
  }
}

function renderTailoredBullets(data) {
  // Backend returns: generated_bullets[{skill, bullet, is_gap_skill}], projected_ats_uplift, top_resume_keywords
  _tailorBulletsCache = data.generated_bullets || data.bullets || [];
  const container = document.getElementById("tailor-bullets-container");
  const upliftEl  = document.getElementById("tailor-uplift-badge");

  // Show projected uplift from backend
  const uplift = data.projected_ats_uplift || "+?%";
  if (upliftEl) upliftEl.textContent = uplift;

  if (_tailorBulletsCache.length === 0) {
    container.innerHTML = `<div style="color:var(--text-muted); padding:0.75rem; font-size:0.85rem;">No tailored bullets generated. Please try selecting a specific job first.</div>`;
    return;
  }

  // Render bullet cards — field is 'bullet', not 'bullet_text'
  container.innerHTML = _tailorBulletsCache.map((b, i) => {
    const text = b.bullet || b.bullet_text || "";
    const isGap = b.is_gap_skill ? " 🎯 Gap Skill" : "";
    return `
      <div class="tailor-bullet-card">
        <div class="tailor-bullet-text">${escapeHtml(text)}</div>
        <span class="bullet-uplift-tag">${escapeHtml(b.skill || "")}${isGap}</span>
        <button class="btn-copy-bullet" onclick="copyBullet(${i})">📋 Copy</button>
      </div>
    `;
  }).join("");

  // Keywords — backend field is top_resume_keywords
  const kwList = document.getElementById("tailor-keywords-list");
  const keywords = data.top_resume_keywords || data.critical_keywords || [];
  if (kwList && keywords.length > 0) {
    kwList.innerHTML = keywords.map(k =>
      `<span class="badge badge-matched" style="font-size:0.72rem; margin:0.2rem;">${escapeHtml(k)}</span>`
    ).join("");
  } else if (kwList) {
    kwList.innerHTML = `<span style="color:var(--text-muted); font-size:0.8rem;">No keywords extracted</span>`;
  }

  // Verbs
  const vbList = document.getElementById("tailor-verbs-list");
  if (vbList && data.recommended_action_verbs && data.recommended_action_verbs.length > 0) {
    vbList.innerHTML = data.recommended_action_verbs.map(v =>
      `<span class="badge badge-neutral" style="font-size:0.72rem; margin:0.2rem; background:rgba(139,92,246,0.18); border-color:rgba(139,92,246,0.35); color:#c084fc;">${escapeHtml(v)}</span>`
    ).join("");
  }
}

function copyBullet(index) {
  const bullet = _tailorBulletsCache[index];
  if (!bullet) return;
  const text = bullet.bullet || bullet.bullet_text || "";
  navigator.clipboard.writeText(text).then(() => {
    showToast("\ud83d\udccb Bullet copied to clipboard!");
  });
}

function copyAllTailoredBullets() {
  if (!_tailorBulletsCache.length) { showToast("\u26a0\ufe0f No bullets to copy", "warning"); return; }
  const text = _tailorBulletsCache.map((b, i) => `${i+1}. ${b.bullet || b.bullet_text || ""}`).join("\n\n");
  navigator.clipboard.writeText(text).then(() => {
    showToast(`\ud83d\udccb All ${_tailorBulletsCache.length} bullets copied!`);
  });
}

function closeResumeTailorModal() {
  const modal = document.getElementById("resume-tailor-modal");
  if (modal) modal.style.display = "none";
}

// Close modal on backdrop click
document.addEventListener("click", (e) => {
  if (e.target && e.target.id === "resume-tailor-modal") closeResumeTailorModal();
});

// =========================================================================
// REAL-WORLD FEATURE 3: COHORT PERCENTILE BENCHMARK UPDATER
// =========================================================================
async function updateCohortBenchmark(atsScore, targetRole) {
  const badge   = document.getElementById("cohort-rank-badge");
  const numEl   = document.getElementById("cohort-percentile-num");
  if (!badge || !numEl) return;

  try {
    const res = await fetch("/api/analytics/benchmark-applicant", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ats_score: atsScore, target_role: targetRole || "Data Scientist" })
    });

    if (!res.ok) return;
    const data = await res.json();
    const pct  = data.percentile || 50;
    const label = data.rank_label || "Developing";

    numEl.textContent = `${pct.toFixed(1)}%`;

    if (pct >= 75) {
      badge.textContent = `Top ${(100 - pct).toFixed(0)}% Exceptional`;
      badge.className   = "badge cohort-rank-label cohort-rank-exceptional";
    } else if (pct >= 45) {
      badge.textContent = `Top ${(100 - pct).toFixed(0)}% Competitive`;
      badge.className   = "badge cohort-rank-label cohort-rank-competitive";
    } else {
      badge.textContent = `Developing`;
      badge.className   = "badge cohort-rank-label cohort-rank-developing";
    }
  } catch(e) {
    console.warn("Cohort benchmark update skipped:", e);
  }
}

// =========================================================================
// SHARED UTILITY: TOAST NOTIFICATION
// =========================================================================
function showToast(message, type = "success") {
  // Remove any existing toast
  const existing = document.querySelector(".toast-notification");
  if (existing) existing.remove();

  const toast = document.createElement("div");
  toast.className = "toast-notification";
  toast.style.cssText = type === "warning"
    ? "background:linear-gradient(135deg,#f59e0b,#d97706);"
    : "";
  toast.textContent = message;
  document.body.appendChild(toast);

  setTimeout(() => { if (toast.parentNode) toast.remove(); }, 2700);
}
