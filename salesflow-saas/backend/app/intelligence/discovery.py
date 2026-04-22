"""
Lead Discovery Engine — Multi-source, Arabic/English
Searches web, news, job boards, and directories to find lead targets.
Returns structured LeadCandidate objects ready for enrichment.
"""
import re
import uuid
import hashlib
import unicodedata
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import urllib.request
import urllib.parse
import json
import time


@dataclass
class LeadCandidate:
    """Raw discovered lead — before enrichment and scoring"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    company_name: str = ""
    company_name_ar: str = ""
    domain: str = ""
    industry: str = ""
    region: str = ""
    source: str = ""                    # web_search | news | job_board | directory
    source_url: str = ""
    raw_snippet: str = ""
    contact_name: str = ""
    contact_title: str = ""
    contact_email: str = ""
    contact_linkedin: str = ""
    phone: str = ""                                    # legacy field
    contact_phone: str = ""                            # canonical field (alias for phone)
    signals: List[str] = field(default_factory=list)   # ["hiring", "expansion", ...]
    trigger: str = ""                                   # what triggered discovery
    confidence: float = 0.5                             # 0-1 source confidence
    discovered_at: str = ""


def normalize_company_name(name: str) -> str:
    """Normalize company name for deduplication — Arabic + English"""
    name = name.strip().lower()
    # Remove Arabic definite article
    name = re.sub(r'^(ال|شركة\s+|مجموعة\s+)', '', name)
    # Remove common suffixes
    suffixes = [
        r'\s+(llc|ltd|co\.|inc\.|corp\.?|group|holding|sa|كو|ليميتد|للتقنية|للخدمات|السعودية)$'
    ]
    for s in suffixes:
        name = re.sub(s, '', name, flags=re.IGNORECASE)
    # Normalize unicode
    name = unicodedata.normalize('NFKC', name)
    return name.strip()


def extract_domain_from_url(url: str) -> str:
    try:
        parsed = urllib.parse.urlparse(url)
        domain = parsed.netloc.replace('www.', '')
        return domain
    except Exception:
        return ""


def extract_emails_from_text(text: str) -> List[str]:
    pattern = r'\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Z|a-z]{2,}\b'
    return list(set(re.findall(pattern, text)))


def extract_phones_from_text(text: str) -> List[str]:
    pattern = r'(\+966|00966|05\d)[\s\-]?(\d[\s\-]?){8,9}'
    return list(set(re.findall(pattern, text) or []))


def extract_linkedin_profiles(text: str) -> List[str]:
    pattern = r'linkedin\.com/in/[\w\-]+'
    return list(set(re.findall(pattern, text, re.IGNORECASE)))


def detect_signals(text: str) -> List[str]:
    """Detect intent/trigger signals in text"""
    signals = []
    text_lower = text.lower()
    signal_map = {
        "hiring": ["hiring", "we're hiring", "join our team", "نحن نوظف", "فرص عمل", "وظائف"],
        "expansion": ["expansion", "new office", "توسع", "افتتاح فرع", "نطاق جديد"],
        "funding": ["funding", "raised", "investment", "تمويل", "استثمار", "سلسلة", "series"],
        "partnership": ["partnership", "collaboration", "شراكة", "تعاون"],
        "digital_transformation": ["digital transformation", "تحول رقمي", "رقمنة"],
        "new_product": ["launch", "new product", "إطلاق", "منتج جديد"],
        "pain_point_crm": ["crm", "sales management", "إدارة المبيعات", "عملاء"],
        "pain_point_outreach": ["outreach", "leads", "عملاء محتملين", "مبيعات"],
        "regulation": ["zatca", "pdpl", "vat", "ضريبة", "ضريبة القيمة المضافة", "حوكمة"],
        "ipo": ["ipo", "طرح عام", "اكتتاب"],
    }
    for signal, keywords in signal_map.items():
        if any(kw in text_lower for kw in keywords):
            signals.append(signal)
    return signals


# ─── Curated Saudi B2B Lead Database (fallback when web search is rate-limited) ───
SAUDI_B2B_SEED_LEADS = [
    # Tech / SaaS
    {"company_name": "Elm", "domain": "elm.sa", "industry": "technology", "region": "Riyadh", "company_size": "1000+", "signals": ["digital_transformation", "hiring"]},
    {"company_name": "Unifonic", "domain": "unifonic.com", "industry": "tech", "region": "Riyadh", "company_size": "200-1000", "signals": ["expansion", "funding"]},
    {"company_name": "Foodics", "domain": "foodics.com", "industry": "saas", "region": "Riyadh", "company_size": "200-1000", "signals": ["funding", "expansion"]},
    {"company_name": "Salla", "domain": "salla.sa", "industry": "technology", "region": "Jeddah", "company_size": "200-1000", "signals": ["expansion", "hiring"]},
    {"company_name": "Zid", "domain": "zid.sa", "industry": "saas", "region": "Riyadh", "company_size": "50-200", "signals": ["digital_transformation"]},
    {"company_name": "Lean Technologies", "domain": "leantech.me", "industry": "fintech", "region": "Riyadh", "company_size": "50-200", "signals": ["funding"]},
    {"company_name": "Tamara", "domain": "tamara.co", "industry": "fintech", "region": "Riyadh", "company_size": "200-1000", "signals": ["funding", "expansion"]},
    {"company_name": "Mozn", "domain": "mozn.sa", "industry": "technology", "region": "Riyadh", "company_size": "50-200", "signals": ["digital_transformation", "hiring"]},
    {"company_name": "Rewaa", "domain": "rewaaapp.com", "industry": "saas", "region": "Riyadh", "company_size": "50-200", "signals": ["pain_point_crm"]},
    {"company_name": "Tamatem", "domain": "tamatem.co", "industry": "technology", "region": "Riyadh", "company_size": "50-200", "signals": ["expansion"]},
    # Healthcare
    {"company_name": "مجموعة دله للرعاية الصحية", "domain": "dallah-hospital.com", "industry": "healthcare", "region": "Riyadh", "company_size": "1000+", "signals": ["digital_transformation"]},
    {"company_name": "مستشفى الحمادي", "domain": "hammadi.com", "industry": "healthcare", "region": "Riyadh", "company_size": "200-1000", "signals": ["hiring"]},
    {"company_name": "Aster DM Healthcare Saudi", "domain": "asterhospitals.sa", "industry": "healthcare", "region": "Riyadh", "company_size": "200-1000", "signals": ["expansion"]},
    # Finance / Banking
    {"company_name": "Riyad Bank", "domain": "riyadbank.com", "industry": "banking", "region": "Riyadh", "company_size": "1000+", "signals": ["digital_transformation", "hiring"]},
    {"company_name": "SABB", "domain": "sabb.com", "industry": "banking", "region": "Jeddah", "company_size": "1000+", "signals": ["digital_transformation"]},
    {"company_name": "Alinma Bank", "domain": "alinma.com", "industry": "banking", "region": "Riyadh", "company_size": "1000+", "signals": ["digital_transformation", "expansion"]},
    {"company_name": "STC Pay", "domain": "stcpay.com.sa", "industry": "fintech", "region": "Riyadh", "company_size": "200-1000", "signals": ["expansion", "hiring"]},
    # Retail / E-commerce
    {"company_name": "نون", "domain": "noon.com", "industry": "retail", "region": "Riyadh", "company_size": "1000+", "signals": ["expansion", "hiring", "digital_transformation"]},
    {"company_name": "Jarir Bookstore", "domain": "jarir.com", "industry": "retail", "region": "Riyadh", "company_size": "1000+", "signals": ["digital_transformation"]},
    {"company_name": "Extra", "domain": "extra.com", "industry": "retail", "region": "Riyadh", "company_size": "200-1000", "signals": ["pain_point_crm"]},
    # Logistics
    {"company_name": "NAQEL Express", "domain": "naqel.com.sa", "industry": "logistics", "region": "Riyadh", "company_size": "1000+", "signals": ["digital_transformation", "expansion"]},
    {"company_name": "Aramex Saudi Arabia", "domain": "aramex.com", "industry": "logistics", "region": "Riyadh", "company_size": "1000+", "signals": ["expansion"]},
    {"company_name": "Fetchr", "domain": "fetchr.us", "industry": "logistics", "region": "Riyadh", "company_size": "50-200", "signals": ["digital_transformation"]},
    # Real Estate
    {"company_name": "Bayut Saudi Arabia", "domain": "bayut.sa", "industry": "real estate", "region": "Riyadh", "company_size": "50-200", "signals": ["digital_transformation"]},
    {"company_name": "مدار للعقارات", "domain": "madar.com.sa", "industry": "real estate", "region": "Riyadh", "company_size": "50-200", "signals": ["expansion"]},
    # Manufacturing / Industrial
    {"company_name": "SABIC", "domain": "sabic.com", "industry": "manufacturing", "region": "Riyadh", "company_size": "1000+", "signals": ["digital_transformation", "ipo"]},
    {"company_name": "Saudi Cement", "domain": "saudicement.com.sa", "industry": "manufacturing", "region": "Riyadh", "company_size": "1000+", "signals": ["hiring"]},
    # Consulting / Professional Services
    {"company_name": "Deloitte Saudi Arabia", "domain": "deloitte.com/sa", "industry": "consulting", "region": "Riyadh", "company_size": "200-1000", "signals": ["hiring", "expansion"]},
    {"company_name": "McKinsey Riyadh", "domain": "mckinsey.com", "industry": "consulting", "region": "Riyadh", "company_size": "50-200", "signals": ["pain_point_outreach"]},
    {"company_name": "PwC Saudi Arabia", "domain": "pwc.com/m1", "industry": "consulting", "region": "Riyadh", "company_size": "200-1000", "signals": ["regulation", "hiring"]},
    # Media / Education
    {"company_name": "MBC Group", "domain": "mbc.net", "industry": "media", "region": "Riyadh", "company_size": "1000+", "signals": ["digital_transformation"]},
    {"company_name": "Edraak", "domain": "edraak.org", "industry": "education", "region": "Amman", "company_size": "50-200", "signals": ["digital_transformation"]},
    # Energy / Government
    {"company_name": "Saudi Electricity Company", "domain": "se.com.sa", "industry": "energy", "region": "Riyadh", "company_size": "1000+", "signals": ["digital_transformation", "regulation"]},
    {"company_name": "Maaden", "domain": "maaden.com.sa", "industry": "manufacturing", "region": "Riyadh", "company_size": "1000+", "signals": ["expansion", "ipo"]},
]


class LeadDiscoveryEngine:
    """
    Multi-source lead discovery engine.
    Searches web sources and extracts structured lead candidates.
    """

    def __init__(self, icp=None):
        self.icp = icp

    def search_web_simple(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        Lightweight web search via DuckDuckGo HTML (no API key required).
        Returns list of {title, url, snippet} dicts.
        """
        results = []
        try:
            encoded = urllib.parse.quote(query)
            url = f"https://html.duckduckgo.com/html/?q={encoded}"
            req = urllib.request.Request(
                url,
                headers={
                    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0",
                    "Accept": "text/html,application/xhtml+xml",
                    "Accept-Language": "ar,en;q=0.9",
                }
            )
            with urllib.request.urlopen(req, timeout=8) as resp:
                html = resp.read().decode('utf-8', errors='ignore')

            # DDG HTML uses redirect URLs: //duckduckgo.com/l/?uddg=<encoded_real_url>
            # Extract all anchor text + href pairs
            link_pattern = re.compile(
                r'<a[^>]+href="(//duckduckgo\.com/l/\?uddg=[^"]+)"[^>]*>(.*?)</a>',
                re.DOTALL | re.IGNORECASE
            )
            # Extract snippets from result__snippet divs
            snippet_pattern = re.compile(
                r'class="result__snippet"[^>]*>(.*?)</a>',
                re.DOTALL | re.IGNORECASE
            )
            snippets_raw = snippet_pattern.findall(html)
            
            # Extract URL domain displays (result__url spans)
            domain_pattern = re.compile(
                r'<span class="result__url"[^>]*>\s*([^<]+)\s*</span>',
                re.IGNORECASE
            )
            domains_raw = domain_pattern.findall(html)

            # Extract title links
            title_pattern = re.compile(
                r'class="result__a"[^>]*>(.*?)</a>',
                re.DOTALL | re.IGNORECASE
            )
            titles_raw = title_pattern.findall(html)

            # Extract real URLs from DDG redirect
            uddg_pattern = re.compile(
                r'uddg=([A-Za-z0-9%+_.-]+)',
                re.IGNORECASE
            )

            all_hrefs = re.findall(
                r'class="result__a"[^>]*href="([^"]+)"',
                html, re.IGNORECASE
            )

            for i in range(min(max_results, len(titles_raw))):
                title = re.sub(r'<[^>]+>', '', titles_raw[i]).strip()
                if not title or len(title) < 4:
                    continue

                # Decode real URL
                real_url = ""
                if i < len(all_hrefs):
                    href = all_hrefs[i]
                    m = uddg_pattern.search(href)
                    if m:
                        try:
                            real_url = urllib.parse.unquote(m.group(1))
                        except Exception:
                            real_url = ""

                snippet = ""
                if i < len(snippets_raw):
                    snippet = re.sub(r'<[^>]+>', '', snippets_raw[i]).strip()

                results.append({
                    "title": title[:200],
                    "url": real_url[:500],
                    "snippet": snippet[:800],
                })

        except Exception as e:
            pass  # Silent fail — don't break the pipeline

        return results

    def candidate_from_search_result(
        self, result: Dict, query: str, source: str = "web_search"
    ) -> Optional[LeadCandidate]:
        """Convert a raw search result into a LeadCandidate"""
        title = result.get("title", "")
        snippet = result.get("snippet", "")
        url = result.get("url", "")

        if not title or len(title) < 3:
            return None

        text = f"{title} {snippet}"
        signals = detect_signals(text)
        emails = extract_emails_from_text(text)
        phones = extract_phones_from_text(text)
        linkedin_profiles = extract_linkedin_profiles(text)

        candidate = LeadCandidate(
            company_name=title[:100],
            domain=extract_domain_from_url(url),
            source=source,
            source_url=url[:500],
            raw_snippet=snippet[:1000],
            signals=signals,
            trigger=query[:200],
            contact_email=emails[0] if emails else "",
            phone=str(phones[0]) if phones else "",
            contact_linkedin=linkedin_profiles[0] if linkedin_profiles else "",
            confidence=0.6 if signals else 0.4,
            discovered_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        )
        return candidate

    def _seed_candidates_from_db(self, icp=None) -> List[LeadCandidate]:
        """Generate candidates from curated Saudi B2B seed database"""
        candidates = []
        now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        for entry in SAUDI_B2B_SEED_LEADS:
            # ICP filter by industry if ICP is provided
            if icp and icp.industries:
                industry = entry.get("industry", "").lower()
                if not any(ind.lower() in industry or industry in ind.lower() for ind in icp.industries):
                    continue
            c = LeadCandidate(
                company_name=entry["company_name"],
                domain=entry.get("domain", ""),
                industry=entry.get("industry", ""),
                region=entry.get("region", ""),
                source="seed_database",
                source_url=f"https://{entry.get('domain','')}",
                # Embed region in raw_snippet so scoring picks it up
                raw_snippet=f"{entry.get('company_name','')} | {entry.get('industry','')} | {entry.get('region','')} Saudi Arabia KSA",
                signals=entry.get("signals", []),
                trigger="ICP match — seed database",
                confidence=0.7,
                discovered_at=now,
            )
            candidates.append(c)
        return candidates

    def discover(self, queries: List[str], max_per_query: int = 8) -> List[LeadCandidate]:
        """
        Run discovery across all queries, return deduplicated LeadCandidates.
        Falls back to seed database if web search returns 0 results.
        """
        all_candidates = []
        seen_domains = set()
        seen_names = set()
        web_found = 0

        for query in queries:
            time.sleep(0.3)  # rate limiting
            results = self.search_web_simple(query, max_results=max_per_query)
            web_found += len(results)
            for result in results:
                candidate = self.candidate_from_search_result(result, query)
                if candidate is None:
                    continue
                # Dedup by domain
                if candidate.domain and candidate.domain in seen_domains:
                    continue
                # Dedup by normalized name
                norm_name = normalize_company_name(candidate.company_name)
                if norm_name and norm_name in seen_names:
                    continue
                if candidate.domain:
                    seen_domains.add(candidate.domain)
                if norm_name:
                    seen_names.add(norm_name)
                all_candidates.append(candidate)

        # Fallback: if web search returned nothing (rate-limited), use seed DB
        if web_found == 0:
            seed_candidates = self._seed_candidates_from_db(self.icp)
            for candidate in seed_candidates:
                if candidate.domain and candidate.domain in seen_domains:
                    continue
                norm_name = normalize_company_name(candidate.company_name)
                if norm_name and norm_name in seen_names:
                    continue
                if candidate.domain:
                    seen_domains.add(candidate.domain)
                if norm_name:
                    seen_names.add(norm_name)
                all_candidates.append(candidate)
        else:
            # Also enrich with seed DB entries not already found
            seed_candidates = self._seed_candidates_from_db(self.icp)
            for candidate in seed_candidates:
                if candidate.domain and candidate.domain in seen_domains:
                    continue
                norm_name = normalize_company_name(candidate.company_name)
                if norm_name and norm_name in seen_names:
                    continue
                if candidate.domain:
                    seen_domains.add(candidate.domain)
                if norm_name:
                    seen_names.add(norm_name)
                all_candidates.append(candidate)

        return all_candidates

    def discover_from_icp(self, icp=None, max_per_query: int = 6) -> List[LeadCandidate]:
        """Run discovery using ICP-generated queries"""
        icp = icp or self.icp
        if icp is None:
            return []
        queries = icp.build_search_queries()
        return self.discover(queries, max_per_query=max_per_query)
