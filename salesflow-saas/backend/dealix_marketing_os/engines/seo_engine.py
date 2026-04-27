"""SEO Engine — generates keyword clusters and content briefs."""
import yaml
from pathlib import Path

_seo_path = Path(__file__).parent.parent / "config" / "seo_targets.yaml"
_seo = {}
if _seo_path.exists():
    with open(_seo_path) as f:
        _seo = yaml.safe_load(f) or {}

def generate_seo_plan() -> dict:
    clusters = _seo.get("clusters", [])
    pages = _seo.get("pages", [])
    p0 = [c for c in clusters if c.get("priority") == "P0"]
    return {
        "total_keywords": len(clusters),
        "p0_keywords": len(p0),
        "planned_pages": len(pages),
        "clusters": clusters,
        "pages": pages,
        "next_actions": [
            "أنشئ صفحة لكل keyword cluster P0",
            "أضف FAQ schema لكل صفحة",
            "اربط الصفحات ببعضها (internal links)",
        ],
    }
