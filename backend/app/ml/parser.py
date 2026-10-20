import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Any, List, Optional
import io
try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False

from backend.app.ml.taxonomy import taxonomy_engine

class ResumeParser:
    def __init__(self):
        pass

    def extract_text_from_pdf(self, file_bytes: bytes) -> str:
        """Extracts text from PDF bytes using pdfplumber with column awareness, or fallback."""
        text_parts = []
        if HAS_PDFPLUMBER:
            try:
                with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text(layout=False)
                        if page_text and len(page_text.strip()) > 50:
                            text_parts.append(page_text)
                        else:
                            text_parts.append(page.extract_text() or "")
                if text_parts and any(t.strip() for t in text_parts):
                    return "\n".join(text_parts)
            except Exception as e:
                print(f"pdfplumber error: {e}")

        # Fallback raw stream parser
        try:
            # Extract parenthesized strings from PDF content streams
            matches = re.findall(rb"\(([\w\s.,@:+\-/]+)\)\s*Tj", file_bytes)
            if matches:
                decoded = [m.decode("utf-8", errors="ignore") for m in matches]
                return " ".join(decoded)
            return file_bytes.decode("latin-1", errors="ignore")
        except Exception:
            return ""

    def extract_text_from_docx(self, file_bytes: bytes) -> str:
        """Extracts text from DOCX bytes using standard zipfile XML parsing."""
        try:
            with zipfile.ZipFile(io.BytesIO(file_bytes)) as z:
                xml_content = z.read("word/document.xml")
                tree = ET.fromstring(xml_content)
                text_parts = []
                for node in tree.iter():
                    if node.tag.endswith("}t"):
                        text_parts.append(node.text or "")
                    elif node.tag.endswith("}p"):
                        text_parts.append("\n")
                return "".join(text_parts)
        except Exception as e:
            print(f"docx extraction error: {e}")
            return ""

    def extract_text_from_pptx(self, file_bytes: bytes) -> str:
        """Extracts text from PPT/PPTX presentation bytes."""
        try:
            with zipfile.ZipFile(io.BytesIO(file_bytes)) as z:
                text_parts = []
                for name in sorted(z.namelist()):
                    if name.startswith("ppt/slides/slide") and name.endswith(".xml"):
                        xml_content = z.read(name)
                        tree = ET.fromstring(xml_content)
                        for node in tree.iter():
                            if node.tag.endswith("}t"):
                                text_parts.append(node.text or "")
                            elif node.tag.endswith("}p"):
                                text_parts.append("\n")
                return "".join(text_parts)
        except Exception as e:
            print(f"pptx extraction error: {e}")
            return ""

    def extract_from_file_bytes(self, filename: str, file_bytes: bytes) -> str:
        """Extracts text from PDF, DOCX, PPT, PPTX or plain text files."""
        fn = filename.lower()
        if fn.endswith(".pdf"):
            return self.extract_text_from_pdf(file_bytes)
        elif fn.endswith(".docx"):
            return self.extract_text_from_docx(file_bytes)
        elif fn.endswith(".ppt") or fn.endswith(".pptx"):
            return self.extract_text_from_pptx(file_bytes)
        else:
            try:
                return file_bytes.decode("utf-8", errors="ignore")
            except Exception:
                return ""

    def clean_text(self, text: str) -> str:
        """Cleans and normalizes extracted text."""
        text = text.replace("\xa0", " ")
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n\s*\n+", "\n\n", text)
        return text.strip()

    def extract_email(self, text: str) -> Optional[str]:
        match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
        if match:
            em = match.group(0).strip(".,;:- ")
            return em
        return None

    def extract_phone(self, text: str) -> Optional[str]:
        # Indian 10-digit phone with optional country code (+91)
        match_in = re.search(r"(?:\+91[\s-]?)?[6-9]\d{4}[\s-]?\d{5}", text)
        if match_in:
            return match_in.group(0).strip()
        # General format
        match_gen = re.search(r"(\+?\d{1,3}[-.\s]?)?(\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}", text)
        if match_gen:
            return match_gen.group(0).strip()
        return None

    def extract_contact_info(self, text: str, name: str) -> Dict[str, Any]:
        email = self.extract_email(text)
        phone = self.extract_phone(text)
        
        # Location
        loc_match = re.search(r"([A-Za-z\s]+,\s*[A-Za-z\s]+,\s*India|[A-Za-z\s]+,\s*India)", text)
        location = ""
        if loc_match:
            cand_loc = loc_match.group(0).strip()
            # remove candidate name if prepended
            if name and cand_loc.startswith(name):
                cand_loc = cand_loc[len(name):].strip()
            location = re.sub(r"\s+", " ", cand_loc).strip(" ,.-")

        # Profiles
        profiles = []
        if "linkedin.com" in text.lower():
            lm = re.search(r"linkedin\.com/in/[\w-]+", text, re.IGNORECASE)
            if lm: profiles.append(lm.group(0))
        if "github.com" in text.lower():
            gm = re.search(r"github\.com/[\w-]+", text, re.IGNORECASE)
            if gm: profiles.append(gm.group(0))

        # Build dynamic display string
        display_items = []
        if email: display_items.append(email)
        if phone: display_items.append(phone)
        if location and location not in display_items: display_items.append(location)
        if profiles: display_items.extend(profiles[:2])

        contact_display = " • ".join(display_items) if display_items else "Contact details extracted from document"

        return {
            "email": email,
            "phone": phone,
            "location": location,
            "profiles": profiles,
            "contact_display": contact_display
        }

    def extract_education(self, text: str) -> str:
        edu_keywords = ["vishwakarma", "institute of technology", "vit", "b.tech", "bachelor", "diploma", "polytechnic", "m.tech", "m.s.", "master", "bca", "mca", "b.sc", "m.sc", "degree", "university", "college", "school"]
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        detected = []
        for line in lines:
            if any(k in line.lower() for k in edu_keywords):
                clean_line = re.sub(r"\s+", " ", line).strip()
                # filter out non-education summary lines
                if len(clean_line) > 8 and clean_line not in detected and not clean_line.lower().startswith("third-year"):
                    detected.append(clean_line)
        return " | ".join(detected[:2]) if detected else "Degree in Computer Science / Engineering"

    def extract_experience(self, text: str) -> Dict[str, Any]:
        # Experience display and numerical estimate
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        exp_summary = ""
        years = 1.0

        for l in lines:
            if any(k in l.lower() for k in ["third-year", "3rd year", "final-year", "undergraduate"]) and len(l) > 15:
                exp_summary = re.sub(r"\s+", " ", l).strip()
                years = 0.5
                break

        internships = []
        for l in lines:
            if "intern" in l.lower() and len(l) > 10 and not l.lower().startswith("work experience"):
                internships.append(re.sub(r"\s+", " ", l).strip())

        if internships and not exp_summary:
            exp_summary = " • ".join(internships[:2])
            years = round(min(len(internships) * 0.5, 2.0), 1)
        elif internships and exp_summary:
            exp_summary = f"{exp_summary} ({internships[0]})"
            years = max(years, 1.0)
        elif not exp_summary:
            exp_summary = "Fresher / Undergraduate Student"
            years = 0.5

        return {
            "experience_years": years,
            "experience_display": exp_summary
        }

    def extract_projects(self, text: str) -> List[str]:
        projects = []
        
        # 1. Look for numbered projects like "1. ProjectName: Description" or "2. ProjectName | Tech"
        proj_pattern = re.findall(r'(?:^|\n)\s*(\d+\.\s*[A-Za-z0-9\s:|-]+(?:\([^\)]+\))?)\n([\s\S]*?)(?=(?:\n\s*\d+\.|\n\s*[A-Z\s]{4,}|\Z))', text)
        if proj_pattern:
            for title, desc in proj_pattern:
                clean_t = re.sub(r"\s+", " ", title).strip()
                # Take first 2 sentences / 35 words
                words = desc.strip().split()
                clean_d = " ".join(words[:30])
                if len(clean_d) > 15:
                    projects.append(f"{clean_t}: {clean_d}...")
                else:
                    projects.append(clean_t)

        # 2. Look for explicit project bullet points under project headers
        if not projects:
            project_section = re.search(r"(?:technical projects|academic projects|key projects|projects)([\s\S]*?)(?:experience|work experience|education|skills|certifications|leadership|$)", text, re.IGNORECASE)
            target_text = project_section.group(1) if project_section else text
            lines = target_text.split("\n")
            current = []
            for line in lines:
                l_str = line.strip()
                if re.match(r"^(\d+\.|\*|-|•)\s*", l_str):
                    if current:
                        projects.append(" ".join(current))
                        current = []
                    current.append(re.sub(r"^(\d+\.|\*|-|•)\s*", "", l_str))
                elif current and len(l_str) > 0 and len(current) < 3:
                    current.append(l_str)
            if current:
                projects.append(" ".join(current))

        # 3. Fallback to lines with project keywords
        if not projects:
            for l in text.split("\n"):
                if any(w in l.lower() for w in ["developed a", "built a", "implemented", "designed a", "pipeline using", "system using"]) and len(l.strip()) > 25:
                    projects.append(l.strip())

        valid = [p for p in projects if len(p) > 15]
        return valid[:4] if valid else ["Academic Projects in Data Engineering & Software Development"]

    def calculate_ats_completeness_score(self, profile: Dict[str, Any]) -> int:
        score = 0
        # Contact info
        if profile.get("email"): score += 8
        if profile.get("phone") or profile.get("profiles"): score += 7
        
        # Skills richness
        skill_count = len(profile.get("skills", []))
        if skill_count >= 10: score += 35
        elif skill_count >= 6: score += 25
        elif skill_count >= 3: score += 15
        else: score += 5

        # Education
        if profile.get("education") and len(profile.get("education")) > 5:
            score += 15

        # Projects
        proj_count = len(profile.get("projects", []))
        if proj_count >= 2: score += 20
        elif proj_count >= 1: score += 12
        else: score += 5

        # Length & structure
        text_len = len(profile.get("raw_text", ""))
        if 500 <= text_len <= 8000: score += 15
        elif text_len > 200: score += 10
        else: score += 5

        return min(100, score)

    def parse_resume(self, text: str, filename: str = "Uploaded_Resume.pdf") -> Dict[str, Any]:
        cleaned = self.clean_text(text)
        lines = [l.strip() for l in cleaned.split("\n") if l.strip()]
        
        first_line = lines[0] if lines else "Candidate"
        name = first_line if len(first_line) < 40 and not any(k in first_line.lower() for k in ["resume", "curriculum", "email", "phone"]) else "Candidate"

        contact_data = self.extract_contact_info(cleaned, name)
        education = self.extract_education(cleaned)
        exp_data = self.extract_experience(cleaned)
        skills = taxonomy_engine.extract_skills_from_text(cleaned)
        projects = self.extract_projects(cleaned)

        profile = {
            "filename": filename,
            "name": name,
            "email": contact_data["email"],
            "phone": contact_data["phone"],
            "location": contact_data["location"],
            "profiles": contact_data["profiles"],
            "contact_display": contact_data["contact_display"],
            "education": education,
            "experience_years": exp_data["experience_years"],
            "experience_display": exp_data["experience_display"],
            "skills": skills,
            "projects": projects,
            "raw_text": cleaned,
            "skill_count": len(skills)
        }
        profile["ats_score"] = self.calculate_ats_completeness_score(profile)
        return profile

parser_engine = ResumeParser()
