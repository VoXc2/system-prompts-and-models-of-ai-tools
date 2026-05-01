"""Project Intelligence layer for Dealix v3.

Inspired by tools like SocraticCode, but implemented as a Dealix-owned core:
- index project files
- chunk code/docs
- prepare deterministic local embeddings hooks
- answer architectural questions with source-aware context

Production storage target: Supabase/Postgres + pgvector via the migration in
supabase/migrations/202605010001_v3_project_memory.sql.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any, Iterable

TEXT_EXTENSIONS = {
    ".py", ".ts", ".tsx", ".js", ".jsx", ".md", ".txt", ".sql", ".json", ".yaml", ".yml", ".html", ".css", ".toml", ".ini", ".env.example",
}

IGNORE_DIRS = {
    ".git", ".venv", "venv", "node_modules", ".next", "dist", "build", "__pycache__", ".pytest_cache", ".mypy_cache",
}


@dataclass(frozen=True)
class ProjectDocument:
    path: str
    source_type: str
    content: str
    content_hash: str
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "source_type": self.source_type,
            "content_hash": self.content_hash,
            "metadata": self.metadata,
            "chars": len(self.content),
        }


@dataclass(frozen=True)
class ProjectChunk:
    path: str
    chunk_index: int
    content: str
    token_estimate: int
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "chunk_index": self.chunk_index,
            "content": self.content,
            "token_estimate": self.token_estimate,
            "metadata": self.metadata,
        }


def classify_path(path: str) -> str:
    p = path.lower()
    if p.startswith("api/"):
        return "api"
    if p.startswith("auto_client_acquisition/"):
        return "revenue_engine"
    if p.startswith("db/") or "migration" in p:
        return "database"
    if p.startswith("landing/") or p.endswith(".html"):
        return "frontend_landing"
    if p.startswith("docs/") or p.endswith(".md"):
        return "documentation"
    if p.startswith("tests/"):
        return "tests"
    return "code"


def should_index(path: Path) -> bool:
    if any(part in IGNORE_DIRS for part in path.parts):
        return False
    if path.is_dir():
        return False
    if path.name == ".env":
        return False
    suffix = path.suffix.lower()
    if suffix in TEXT_EXTENSIONS:
        return True
    return path.name.endswith(".env.example")


def scan_project(root: str | Path) -> list[ProjectDocument]:
    root_path = Path(root)
    docs: list[ProjectDocument] = []
    for path in root_path.rglob("*"):
        if not should_index(path):
            continue
        rel = str(path.relative_to(root_path)).replace("\\", "/")
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if not content.strip():
            continue
        docs.append(
            ProjectDocument(
                path=rel,
                source_type=classify_path(rel),
                content=content,
                content_hash=sha256(content.encode("utf-8")).hexdigest(),
                metadata={"extension": path.suffix.lower(), "chars": len(content)},
            )
        )
    return docs


def chunk_text(document: ProjectDocument, *, max_chars: int = 1800, overlap: int = 180) -> list[ProjectChunk]:
    content = document.content
    chunks: list[ProjectChunk] = []
    start = 0
    index = 0
    while start < len(content):
        end = min(len(content), start + max_chars)
        window = content[start:end]
        # Prefer to cut on line boundary when possible.
        if end < len(content):
            newline = window.rfind("\n")
            if newline > max_chars * 0.55:
                end = start + newline
                window = content[start:end]
        chunks.append(
            ProjectChunk(
                path=document.path,
                chunk_index=index,
                content=window.strip(),
                token_estimate=max(1, len(window) // 4),
                metadata={"source_type": document.source_type, "content_hash": document.content_hash},
            )
        )
        index += 1
        start = max(end - overlap, end)
    return chunks


def build_index_summary(documents: Iterable[ProjectDocument]) -> dict[str, Any]:
    docs = list(documents)
    by_type: dict[str, int] = {}
    total_chars = 0
    for doc in docs:
        by_type[doc.source_type] = by_type.get(doc.source_type, 0) + 1
        total_chars += len(doc.content)
    return {
        "documents": len(docs),
        "total_chars": total_chars,
        "by_type": by_type,
        "recommended_next_step": "Generate embeddings and upsert into Supabase project_chunks.",
    }


def naive_search(documents: Iterable[ProjectDocument], query: str, limit: int = 10) -> list[dict[str, Any]]:
    terms = [term.lower() for term in query.split() if len(term) > 2]
    scored: list[tuple[int, ProjectDocument]] = []
    for doc in documents:
        text = f"{doc.path}\n{doc.content}".lower()
        score = sum(text.count(term) for term in terms)
        if score:
            scored.append((score, doc))
    scored.sort(key=lambda item: item[0], reverse=True)
    return [
        {"score": score, **doc.to_dict()}
        for score, doc in scored[:limit]
    ]


def explain_project_intelligence_stack() -> dict[str, Any]:
    return {
        "purpose": "Make Dealix understand its own codebase, docs, strategy, and relationships.",
        "storage": "Supabase Postgres + pgvector",
        "embedding_dimensions": 384,
        "embedding_model_options": ["gte-small local/edge", "OpenAI text-embedding-3-small", "bge-small"],
        "search_modes": ["keyword", "semantic", "hybrid", "relationship-aware"],
        "best_use": [
            "Ask what is missing before launch",
            "Find files related to a feature",
            "Generate implementation plans grounded in code",
            "Power Sami Personal Operator memory",
            "Let agents understand project relationships before editing",
        ],
    }


def should_block_embedding(text: str) -> tuple[bool, str]:
    """Block embedding if content looks like secrets (never embed keys/tokens)."""
    from auto_client_acquisition.personal_operator.memory import looks_like_secret

    if looks_like_secret(text):
        return True, "secret_pattern_detected"
    return False, ""


def answer_operator_question(
    question: str,
    *,
    root: str | Path = ".",
    deep_scan: bool = False,
) -> dict[str, Any]:
    """Grounded answers for Personal Operator; keyword search optional."""
    q = question.strip().lower()
    note_ar = (
        "البحث الدلالي غير متصل بعد؛ نستخدم مخطط المشروع المعروف والوحدات الأساسية. "
        "semantic search not connected yet; using project blueprint and known modules."
    )
    answer_ar = (
        "ركّز على: Personal Operator API، ذاكرة المشروع (Supabase/pgvector)، اختبارات، "
        "واتساب موافقات، Gmail/Calendar كمسودات فقط، ثم pilot لـ 10 عملاء."
    )
    related_files: list[str] = [
        "api/main.py",
        "api/routers/personal_operator.py",
        "api/routers/v3.py",
        "auto_client_acquisition/personal_operator/operator.py",
        "auto_client_acquisition/v3/project_intelligence.py",
    ]
    if "ناقص" in question or "missing" in q:
        answer_ar = (
            "قبل التدشين: ربط embeddings بـ Supabase، سياسات RLS، تدفق واتساب بأزرار، "
            "Gmail draft + Calendar draft بموافقة، تثبيت الاختبارات، ومراقبة (Sentry/OTel)."
        )
    elif "خطوة" in question or "next" in q:
        answer_ar = "الخطوة التالية العملية: شغّل فهرسة المشروع، راجع تقرير الجاهزية، ثم ربط pilot مع قائمة 10 مؤسسين."
    elif "ملف" in question or "files" in q or "pr" in q:
        answer_ar = "أهم الملفات: `api/routers/personal_operator.py`, `auto_client_acquisition/personal_operator/`, `supabase/migrations/`."
    elif "supabase" in q:
        answer_ar = "أفضل مسار: Postgres + pgvector + Edge Function للـ embeddings، ومفتاح الخدمة فقط في السيرفر وليس في الواجهة."
    elif "whatsapp" in q or "واتساب" in question or "buttons" in q:
        answer_ar = "استخدم رسالتين كحد أقصى 3 أزرار لكل رسالة: قبول/تخطي/رسالة ثم اعتماد/تعديل/إلغاء. لا إرسال بارد."
    elif "personal operator" in q or "مشغل" in question or "operator" in q:
        answer_ar = "Personal Operator: daily brief + فرص + قرارات + مسودات برسالة عربية وموافقة صريحة قبل أي إرسال خارجي."

    search_hits: list[dict[str, Any]] = []
    if deep_scan:
        docs = scan_project(root)
        search_hits = naive_search(docs, question, limit=5)

    return {
        "question": question,
        "answer_ar": answer_ar,
        "semantic_status_ar": note_ar,
        "related_files": related_files,
        "search_hits": search_hits,
    }
