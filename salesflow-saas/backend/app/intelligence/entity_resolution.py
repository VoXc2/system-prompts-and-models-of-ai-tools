"""
Entity Resolution & Deduplication Engine
Arabic/English normalization + fuzzy company matching.
Prevents same company appearing twice under different names.
"""
import re
import unicodedata
from typing import List, Dict, Tuple, Optional
from difflib import SequenceMatcher


# Common Arabic/English company suffixes to strip
STRIP_SUFFIXES_AR = [
    r'\s*(شركة|مجموعة|مؤسسة|ش\.م\.م|ش\.م\.س|ذ\.م\.م|للخدمات|للتقنية|للمعلوماتية'
    r'|السعودية|العربية|الخليجية|الدولية|التجارية|الحديثة|المتحدة|المتقدمة)\s*$'
]
STRIP_SUFFIXES_EN = [
    r'\s*(llc|ltd|co\.|co|inc\.|inc|corp\.|corp|group|holding|holdings|sa|plc'
    r'|technologies|solutions|services|systems|international|global|company)\s*$'
]
ARABIC_ARTICLE = r'^(ال)'

# Arabic → English character transliteration for matching
ARABIC_ROMAN_MAP = {
    'ا': 'a', 'أ': 'a', 'إ': 'a', 'آ': 'a',
    'ب': 'b', 'ت': 't', 'ث': 'th', 'ج': 'j', 'ح': 'h', 'خ': 'kh',
    'د': 'd', 'ذ': 'dh', 'ر': 'r', 'ز': 'z', 'س': 's', 'ش': 'sh',
    'ص': 's', 'ض': 'd', 'ط': 't', 'ظ': 'z', 'ع': 'a', 'غ': 'gh',
    'ف': 'f', 'ق': 'q', 'ك': 'k', 'ل': 'l', 'م': 'm', 'ن': 'n',
    'ه': 'h', 'و': 'w', 'ي': 'y', 'ى': 'a', 'ة': 'h',
    'ئ': 'y', 'ء': '', 'ؤ': 'w',
}


def transliterate_arabic(text: str) -> str:
    """Convert Arabic script to approximate Latin for cross-script matching"""
    return ''.join(ARABIC_ROMAN_MAP.get(c, c) for c in text)


def normalize_name(name: str) -> str:
    """Canonical form for deduplication matching"""
    if not name:
        return ""
    name = name.strip().lower()
    # Strip Arabic article
    name = re.sub(ARABIC_ARTICLE, '', name)
    # Strip Arabic suffixes
    for pattern in STRIP_SUFFIXES_AR:
        name = re.sub(pattern, '', name, flags=re.IGNORECASE)
    # Strip English suffixes
    for pattern in STRIP_SUFFIXES_EN:
        name = re.sub(pattern, '', name, flags=re.IGNORECASE)
    # Normalize unicode
    name = unicodedata.normalize('NFKC', name)
    # Remove punctuation
    name = re.sub(r'[^\w\s\u0600-\u06FF]', '', name)
    name = re.sub(r'\s+', ' ', name).strip()
    return name


def normalize_domain(domain: str) -> str:
    """Strip www, https, subdomains for domain matching"""
    domain = domain.lower().strip()
    domain = re.sub(r'^https?://', '', domain)
    domain = re.sub(r'^www\.', '', domain)
    domain = re.sub(r'/.*$', '', domain)
    return domain


def fuzzy_match_score(a: str, b: str) -> float:
    """Similarity ratio between two strings 0-1"""
    return SequenceMatcher(None, a, b).ratio()


def are_same_company(
    name_a: str, domain_a: str,
    name_b: str, domain_b: str,
    threshold: float = 0.82
) -> Tuple[bool, float, str]:
    """
    Determine if two company records refer to the same entity.
    Returns: (is_same, confidence, reason)
    """
    # Domain match is definitive
    if domain_a and domain_b:
        d_a = normalize_domain(domain_a)
        d_b = normalize_domain(domain_b)
        if d_a == d_b and d_a:
            return True, 1.0, "exact_domain_match"

    # Normalize names
    norm_a = normalize_name(name_a)
    norm_b = normalize_name(name_b)

    if not norm_a or not norm_b:
        return False, 0.0, "insufficient_data"

    # Exact normalized match
    if norm_a == norm_b:
        return True, 0.98, "exact_name_match"

    # Fuzzy match on original names
    ratio = fuzzy_match_score(norm_a, norm_b)
    if ratio >= threshold:
        return True, ratio, f"fuzzy_match_{ratio:.2f}"

    # Cross-script: transliterate Arabic and compare with English
    translit_a = transliterate_arabic(norm_a)
    translit_b = transliterate_arabic(norm_b)
    cross_ratio = fuzzy_match_score(translit_a, norm_b)
    if cross_ratio >= threshold:
        return True, cross_ratio, f"cross_script_match_{cross_ratio:.2f}"
    cross_ratio2 = fuzzy_match_score(norm_a, translit_b)
    if cross_ratio2 >= threshold:
        return True, cross_ratio2, f"cross_script_match_{cross_ratio2:.2f}"

    return False, max(ratio, cross_ratio), "no_match"


class EntityRegistry:
    """
    Maintains a registry of known companies with deduplication.
    Use resolve() to find or create a canonical entity.
    """

    def __init__(self):
        self._entities: List[Dict] = []   # List of canonical entity records
        self._domain_index: Dict[str, int] = {}  # domain → entity index
        self._name_index: Dict[str, int] = {}    # normalized name → entity index

    def resolve(self, name: str, domain: str = "") -> Tuple[int, bool]:
        """
        Find existing entity or create new one.
        Returns: (entity_id, is_new)
        """
        norm_name = normalize_name(name)
        norm_domain = normalize_domain(domain) if domain else ""

        # Fast lookup by domain
        if norm_domain and norm_domain in self._domain_index:
            return self._domain_index[norm_domain], False

        # Fast lookup by exact name
        if norm_name and norm_name in self._name_index:
            return self._name_index[norm_name], False

        # Fuzzy scan
        for idx, entity in enumerate(self._entities):
            is_same, confidence, reason = are_same_company(
                name, domain,
                entity.get("canonical_name", ""),
                entity.get("domain", ""),
            )
            if is_same:
                # Update entity with better data
                if not entity.get("domain") and norm_domain:
                    entity["domain"] = norm_domain
                    self._domain_index[norm_domain] = idx
                return idx, False

        # Create new entity
        new_id = len(self._entities)
        entity = {
            "id": new_id,
            "canonical_name": name,
            "normalized_name": norm_name,
            "domain": norm_domain,
            "aliases": [],
        }
        self._entities.append(entity)
        if norm_domain:
            self._domain_index[norm_domain] = new_id
        if norm_name:
            self._name_index[norm_name] = new_id

        return new_id, True

    def deduplicate_lead_list(self, leads: List[Dict]) -> List[Dict]:
        """
        Deduplicate a list of lead dicts.
        Each lead must have 'company_name' and optionally 'domain'.
        Returns deduplicated list with canonical names.
        """
        seen = {}  # entity_id → first lead index
        deduped = []

        for lead in leads:
            name = lead.get("company_name", "")
            domain = lead.get("domain", "")
            entity_id, is_new = self.resolve(name, domain)
            if is_new or entity_id not in seen:
                seen[entity_id] = len(deduped)
                lead["entity_id"] = entity_id
                deduped.append(lead)
            else:
                # Merge: keep richer record
                existing = deduped[seen[entity_id]]
                for field in ["contact_email", "contact_phone", "contact_linkedin",
                               "description", "tech_stack", "signals"]:
                    if not existing.get(field) and lead.get(field):
                        existing[field] = lead[field]
                # Merge signals list
                if isinstance(existing.get("signals"), list) and isinstance(lead.get("signals"), list):
                    existing["signals"] = list(set(existing["signals"] + lead["signals"]))

        return deduped

    @property
    def entity_count(self) -> int:
        return len(self._entities)
