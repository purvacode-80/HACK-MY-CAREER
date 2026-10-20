import json
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple

TAXONOMY_PATH = Path(__file__).parent.parent / "data" / "skill_taxonomy.json"

class SkillTaxonomy:
    def __init__(self, taxonomy_path: Path = TAXONOMY_PATH):
        with open(taxonomy_path, "r", encoding="utf-8") as f:
            self.taxonomy_data = json.load(f)
            
        # Build canonical lookup and alias map
        self.alias_to_canonical: Dict[str, str] = {}
        self.canonical_to_category: Dict[str, str] = {}
        self.canonical_skills: Set[str] = set()

        for category, skills in self.taxonomy_data.items():
            for canonical, aliases in skills.items():
                self.canonical_skills.add(canonical)
                self.canonical_to_category[canonical] = category
                # Map exact lowercase canonical
                self.alias_to_canonical[canonical.lower()] = canonical
                for alias in aliases:
                    self.alias_to_canonical[alias.lower()] = canonical

        # Pre-compile regex patterns for multi-word and special symbol aliases
        # Sort by length descending to match longest phrases first (e.g., 'machine learning' before 'learning')
        sorted_aliases = sorted(self.alias_to_canonical.keys(), key=lambda x: -len(x))
        self.patterns: List[Tuple[re.Pattern, str]] = []
        for alias in sorted_aliases:
            escaped = re.escape(alias)
            # Match with boundary check (letters/digits/plus/hash)
            pattern = re.compile(rf"(?<![a-zA-Z0-9_#+]){escaped}(?![a-zA-Z0-9_#+])", re.IGNORECASE)
            self.patterns.append((pattern, self.alias_to_canonical[alias]))

    def extract_skills_from_text(self, text: str) -> List[str]:
        """Extracts unique canonical skills found within raw text."""
        if not text:
            return []
        found_skills: Set[str] = set()
        for pattern, canonical in self.patterns:
            if pattern.search(text):
                found_skills.add(canonical)
        return sorted(list(found_skills))

    def get_category(self, skill: str) -> str:
        return self.canonical_to_category.get(skill, "General Tech")

    def get_all_canonical_skills(self) -> List[str]:
        return sorted(list(self.canonical_skills))

# Singleton instance
taxonomy_engine = SkillTaxonomy()
