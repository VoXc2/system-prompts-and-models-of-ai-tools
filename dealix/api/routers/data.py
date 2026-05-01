"""
Data Lake + Lead Graph ingestion router.

Endpoints:
    POST /api/v1/data/import                    — register a dataset (JSON rows)
    POST /api/v1/data/import/{id}/normalize     — normalize raw rows
    POST /api/v1/data/import/{id}/dedupe        — match + merge into accounts
    POST /api/v1/data/import/{id}/enrich        — run enrichment for new accounts
    GET  /api/v1/data/import/{id}/report        — totals + per-row counts
    POST /api/v1/data/suppression               — add opt-out email/phone/domain
    GET  /api/v1/data/suppression               — list suppression rows
    GET  /api/v1/data/imports                   — list all imports
    GET  /api/v1/data/accounts                  — list accounts (paginated)
    GET  /api/v1/data/accounts/{id}             — single account + signals
    POST /api/v1/data/accounts/{id}/score       — recompute score from current data

Ingestion is *append-only*. Raw rows are kept; normalization writes
new account/contact/signal records but never deletes raw_lead_rows.

PDPL compliance:
- Every import declares allowed_use, source_type, consent_status, risk_level.
- Suppression list is checked at outreach time, not at ingest time.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Body, HTTPException
from sqlalchemy import select

from auto_client_acquisition.pipelines.dedupe import build_index, find_match
from auto_client_acquisition.pipelines.enrichment import enrich_account
from auto_client_acquisition.pipelines.normalize import (
    fuzzy_company_key,
    is_acceptable,
    normalize_row,
)
from auto_client_acquisition.pipelines.scoring import (
    compute_data_quality,
    compute_lead_score,
)
from db.models import (
    AccountRecord,
    ContactRecord,
    LeadScoreRecord,
    RawLeadImport,
    RawLeadRow,
    SignalRecord,
    SuppressionRecord,
)
from db.session import async_session_factory

router = APIRouter(prefix="/api/v1/data", tags=["data"])
log = logging.getLogger(__name__)


# ── Data Source Catalog (compliance-graded) ──────────────────────
SAUDI_DATA_SOURCE_CATALOG: list[dict[str, Any]] = [
    {
        "key": "riyadh_chamber",
        "name_ar": "غرفة الرياض — دليل الأعضاء",
        "name_en": "Riyadh Chamber of Commerce Member Directory",
        "url": "https://chamber.org.sa",
        "rating": "green",
        "access_method": "public_web",
        "coverage_city": ["riyadh"],
        "coverage_sector": "all",
        "ingest_strategy": "crawl_with_requests_bs4_provider",
    },
    {
        "key": "jeddah_chamber",
        "name_ar": "غرفة جدة — دليل الأعضاء",
        "name_en": "Jeddah Chamber of Commerce Member Directory",
        "url": "https://jcci.org.sa",
        "rating": "green",
        "access_method": "public_web",
        "coverage_city": ["jeddah"],
        "coverage_sector": "all",
    },
    {
        "key": "eastern_chamber",
        "name_ar": "غرفة الشرقية",
        "name_en": "Asharqia Chamber",
        "url": "https://chamber.org.sa/eastern",
        "rating": "green",
        "access_method": "public_web",
        "coverage_city": ["dammam", "khobar", "jubail"],
        "coverage_sector": "all",
    },
    {
        "key": "data_gov_sa",
        "name_ar": "بوابة البيانات المفتوحة (سدايا)",
        "name_en": "SDAIA Open Data Portal",
        "url": "https://data.gov.sa",
        "rating": "green",
        "access_method": "public_dataset_download",
        "coverage_city": "all",
        "coverage_sector": "all",
    },
    {
        "key": "google_places",
        "name_ar": "Google Places (Maps API)",
        "name_en": "Google Places via MapsProvider chain",
        "url": "internal:auto_client_acquisition.providers.maps",
        "rating": "green",
        "access_method": "api_with_key",
        "coverage_city": "all",
        "coverage_sector": "all",
        "ingest_strategy": "store_place_id_only_per_terms",
    },
    {
        "key": "saudi_contractors_authority",
        "name_ar": "هيئة المقاولين السعودية",
        "name_en": "Saudi Contractors Authority Registry",
        "url": "https://sca.org.sa",
        "rating": "green",
        "access_method": "public_web",
        "coverage_sector": ["construction"],
    },
    {
        "key": "saudi_tourism_authority",
        "name_ar": "هيئة السياحة السعودية",
        "name_en": "Saudi Tourism Authority Registry",
        "url": "https://scth.gov.sa",
        "rating": "green",
        "access_method": "public_web",
        "coverage_sector": ["hospitality_events"],
    },
    {
        "key": "linkedin",
        "name_ar": "LinkedIn",
        "name_en": "LinkedIn",
        "url": "https://www.linkedin.com",
        "rating": "red",
        "access_method": "scraping_prohibited",
        "ingest_strategy": "manual_research_only_no_bulk_ingest",
        "note": "Dealix uses LinkedIn for human research + human send only — never for data ingestion.",
    },
    {
        "key": "linkedin_chamber_other_yellow",
        "name_ar": "أدلة تجارية مدفوعة",
        "name_en": "Paid B2B Data Vendors (general)",
        "url": "various",
        "rating": "yellow",
        "access_method": "purchase_with_documentation",
        "ingest_strategy": "audit_lead_file_first_then_import",
        "note": "Demand source documentation, allowed_use, last_updated, sample of 100 rows before paying.",
    },
]


def _new_id(prefix: str = "") -> str:
    suffix = uuid.uuid4().hex[:24]
    return f"{prefix}{suffix}" if prefix else suffix


def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


async def _safe_commit(session, *objs: Any) -> bool:
    try:
        for o in objs:
            session.add(o)
        await session.commit()
        return True
    except Exception as exc:  # noqa: BLE001
        log.warning("data_router_commit_failed err=%s", exc)
        try:
            await session.rollback()
        except Exception:
            pass
        return False


# ── Source catalog ────────────────────────────────────────────────
@router.get("/sources/catalog")
async def list_data_sources() -> dict[str, Any]:
    """Compliance-graded Saudi business data source catalog."""
    return {
        "count": len(SAUDI_DATA_SOURCE_CATALOG),
        "rating_legend": {
            "green": "public + clearly permissive — direct ingest",
            "yellow": "public but ToS-sensitive — lookup-only, manual approval",
            "red": "scraping forbidden / paywalled-without-allowed-use — DO NOT INGEST",
        },
        "sources": SAUDI_DATA_SOURCE_CATALOG,
        "doc": "See docs/ops/SAUDI_DATA_SOURCE_CATALOG.md for ingestion strategy per source.",
    }


# ── Import: register a dataset ────────────────────────────────────
@router.post("/import")
async def create_import(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """
    Register a dataset. Body:
        source_name (required, str)
        source_type (required, one of: owned/public/paid/partner/google_maps/google_search/manual)
        allowed_use (optional, str — defaults to "business_contact_research_only")
        consent_status (optional)
        risk_level (optional, low/medium/high)
        rows (required, list[dict] — raw records, can be loose schema)
        file_name (optional)
        imported_by (optional)
        notes (optional)
    """
    source_name = str(body.get("source_name") or "").strip()
    source_type = str(body.get("source_type") or "").strip()
    rows = body.get("rows")
    if not source_name:
        raise HTTPException(400, "source_name_required")
    if source_type not in {
        "owned", "public", "paid", "partner",
        "google_maps", "google_search", "manual",
    }:
        raise HTTPException(400, "source_type_invalid")
    if not isinstance(rows, list) or not rows:
        raise HTTPException(400, "rows_required: provide a non-empty list of dicts")
    if len(rows) > 10000:
        raise HTTPException(400, "too_many_rows: max 10000 per import; split into batches")

    import_id = _new_id("imp_")

    rec = RawLeadImport(
        id=import_id,
        source_name=source_name,
        source_type=source_type,
        file_name=body.get("file_name"),
        imported_by=body.get("imported_by"),
        allowed_use=str(body.get("allowed_use") or "business_contact_research_only"),
        consent_status=str(body.get("consent_status") or "unknown"),
        risk_level=str(body.get("risk_level") or "medium"),
        rows_total=len(rows),
        notes=body.get("notes"),
        status="raw",
    )
    raw_rows = [
        RawLeadRow(
            id=_new_id("rr_"),
            import_id=import_id,
            raw_json=r if isinstance(r, dict) else {"value": r},
            normalized_status="pending",
        )
        for r in rows
    ]

    async with async_session_factory() as session:
        ok = await _safe_commit(session, rec, *raw_rows)
        if not ok:
            return {
                "import_id": import_id,
                "status": "skipped_db_unreachable",
                "rows_total": len(rows),
            }

    return {
        "import_id": import_id,
        "status": "raw",
        "rows_total": len(rows),
        "next_action": f"POST /api/v1/data/import/{import_id}/normalize",
    }


# ── Normalize ─────────────────────────────────────────────────────
@router.post("/import/{import_id}/normalize")
async def normalize_import(import_id: str) -> dict[str, Any]:
    async with async_session_factory() as session:
        try:
            imp_rec = (await session.execute(
                select(RawLeadImport).where(RawLeadImport.id == import_id)
            )).scalar_one_or_none()
        except Exception as exc:  # noqa: BLE001
            return {"status": "skipped_db_unreachable", "error": str(exc)}
        if not imp_rec:
            raise HTTPException(404, "import_not_found")

        rows = (await session.execute(
            select(RawLeadRow).where(RawLeadRow.import_id == import_id)
        )).scalars().all()

        normalized_count = 0
        rejected_count = 0
        accounts_created: list[str] = []

        for row in rows:
            if row.normalized_status != "pending":
                continue
            try:
                normalized = normalize_row(row.raw_json or {})
            except Exception as exc:  # noqa: BLE001
                row.normalized_status = "rejected"
                row.error = f"normalize_error: {exc}"
                rejected_count += 1
                continue

            ok, reason = is_acceptable(normalized)
            if not ok:
                row.normalized_status = "rejected"
                row.error = reason or "unacceptable"
                rejected_count += 1
                continue

            # Create AccountRecord stub (dedupe runs in next step)
            acc_id = _new_id("acc_")
            acc = AccountRecord(
                id=acc_id,
                company_name=normalized["company_name"][:255],
                normalized_name=normalized["normalized_name"][:255],
                domain=normalized["domain"],
                website=normalized["website"][:500] if normalized["website"] else None,
                city=normalized["city"][:128] if normalized["city"] else None,
                country=normalized["country"][:64] if normalized["country"] else "SA",
                sector=normalized["sector"][:64] if normalized["sector"] else None,
                google_place_id=normalized["google_place_id"][:128]
                if normalized["google_place_id"] else None,
                source_count=1,
                best_source=imp_rec.source_type,
                risk_level=imp_rec.risk_level,
                status="new",
                extra={
                    "import_id": import_id,
                    "source_url": normalized["source_url"],
                    "raw_keys": normalized["raw_keys"],
                    "allowed_use": imp_rec.allowed_use,
                    "consent_status": imp_rec.consent_status,
                },
            )
            session.add(acc)
            accounts_created.append(acc_id)

            # Optional contact
            if normalized["email"] or normalized["phone"] or normalized["contact_name"]:
                session.add(ContactRecord(
                    id=_new_id("ct_"),
                    account_id=acc_id,
                    name=normalized["contact_name"][:255] if normalized["contact_name"] else None,
                    role=normalized["role"][:128] if normalized["role"] else None,
                    email=normalized["email"][:255] if normalized["email"] else None,
                    phone=normalized["phone"][:32] if normalized["phone"] else None,
                    source=imp_rec.source_type,
                    consent_status=imp_rec.consent_status,
                    opt_out=False,
                    risk_level=imp_rec.risk_level,
                ))

            row.normalized_status = "ok"
            row.account_id = acc_id
            normalized_count += 1

        imp_rec.rows_normalized = normalized_count
        imp_rec.rows_rejected = rejected_count
        imp_rec.status = "normalized"
        imp_rec.updated_at = _utcnow()

        try:
            await session.commit()
        except Exception as exc:  # noqa: BLE001
            await session.rollback()
            return {"status": "commit_failed", "error": str(exc)}

    return {
        "import_id": import_id,
        "status": "normalized",
        "rows_normalized": normalized_count,
        "rows_rejected": rejected_count,
        "accounts_created": len(accounts_created),
        "next_action": f"POST /api/v1/data/import/{import_id}/dedupe",
    }


# ── Dedupe ────────────────────────────────────────────────────────
@router.post("/import/{import_id}/dedupe")
async def dedupe_import(import_id: str) -> dict[str, Any]:
    """Match accounts created by this import against the existing graph."""
    async with async_session_factory() as session:
        try:
            imp_rec = (await session.execute(
                select(RawLeadImport).where(RawLeadImport.id == import_id)
            )).scalar_one_or_none()
            if not imp_rec:
                raise HTTPException(404, "import_not_found")
            all_accounts = (await session.execute(select(AccountRecord))).scalars().all()
        except HTTPException:
            raise
        except Exception as exc:  # noqa: BLE001
            return {"status": "skipped_db_unreachable", "error": str(exc)}

        # Split into already-existing (from prior imports) vs this-import's new ones
        new_for_import = [a for a in all_accounts if (a.extra or {}).get("import_id") == import_id]
        existing = [a for a in all_accounts if a.id not in {n.id for n in new_for_import}]
        existing_dicts = [
            {
                "id": a.id, "company_name": a.company_name,
                "normalized_name": a.normalized_name, "domain": a.domain,
                "website": a.website, "city": a.city,
                "phone": None, "email": None,  # not on AccountRecord directly
                "google_place_id": a.google_place_id,
            }
            for a in existing
        ]
        idx = build_index(existing_dicts)

        merged_count = 0
        kept_count = 0
        for acc in new_for_import:
            normalized = {
                "company_name": acc.company_name,
                "normalized_name": acc.normalized_name,
                "domain": acc.domain,
                "phone": None,
                "email": None,
                "google_place_id": acc.google_place_id,
                "city": acc.city,
            }
            match_id, match_kind = find_match(normalized, idx)
            if match_id:
                # Merge: increment source_count on the canonical, mark this one as duplicate
                target = next((a for a in existing if a.id == match_id), None)
                if target is not None:
                    target.source_count = (target.source_count or 1) + 1
                    extra = dict(target.extra or {})
                    sources = list(extra.get("sources", []))
                    if imp_rec.source_type not in sources:
                        sources.append(imp_rec.source_type)
                        extra["sources"] = sources
                    target.extra = extra
                    acc.status = "merged_into"
                    acc.extra = {**(acc.extra or {}), "merged_into": match_id, "match_kind": match_kind}
                    merged_count += 1
            else:
                kept_count += 1

        imp_rec.rows_duplicate = merged_count
        imp_rec.status = "deduped"
        imp_rec.updated_at = _utcnow()

        try:
            await session.commit()
        except Exception as exc:  # noqa: BLE001
            await session.rollback()
            return {"status": "commit_failed", "error": str(exc)}

    return {
        "import_id": import_id,
        "status": "deduped",
        "merged": merged_count,
        "new_accounts": kept_count,
        "next_action": f"POST /api/v1/data/import/{import_id}/enrich",
    }


# ── Enrich ────────────────────────────────────────────────────────
@router.post("/import/{import_id}/enrich")
async def enrich_import(import_id: str, body: dict[str, Any] = Body(default={})) -> dict[str, Any]:
    """
    Run the enrichment pipeline against new accounts created by this import.

    Body:
        enrichment_level: basic / standard / deep (default: standard)
        max_accounts: int (default 25 — cap to avoid runaway API calls)
    """
    level = str(body.get("enrichment_level") or "standard")
    max_accounts = int(body.get("max_accounts") or 25)
    if max_accounts < 1 or max_accounts > 200:
        raise HTTPException(400, "max_accounts_out_of_range: 1..200")

    async with async_session_factory() as session:
        try:
            new_accounts = (await session.execute(
                select(AccountRecord).where(
                    AccountRecord.status == "new"
                ).limit(max_accounts)
            )).scalars().all()
        except Exception as exc:  # noqa: BLE001
            return {"status": "skipped_db_unreachable", "error": str(exc)}

        # Filter to accounts from this import
        from_this_import = [
            a for a in new_accounts
            if (a.extra or {}).get("import_id") == import_id
        ]

        enriched = 0
        for acc in from_this_import:
            account_dict = {
                "id": acc.id,
                "company_name": acc.company_name,
                "domain": acc.domain,
                "website": acc.website,
                "city": acc.city,
                "country": acc.country,
                "sector": acc.sector,
                "google_place_id": acc.google_place_id,
                "best_source": acc.best_source,
                "source_type": acc.best_source,
                "allowed_use": (acc.extra or {}).get("allowed_use"),
                "risk_level": acc.risk_level,
            }
            try:
                result = await enrich_account(account_dict, enrichment_level=level)
            except Exception as exc:  # noqa: BLE001
                log.warning("enrich_failed acc=%s err=%s", acc.id, exc)
                continue

            # Persist signals
            for s in result.get("signals", []):
                session.add(SignalRecord(
                    id=_new_id("sig_"),
                    account_id=acc.id,
                    signal_type=str(s.get("signal_type") or "tech")[:64],
                    signal_value=str(s.get("signal_value") or "")[:500],
                    source_url=s.get("source_url"),
                    confidence=float(s.get("confidence") or 0.5),
                ))

            # Persist score
            sc = result.get("score") or {}
            session.add(LeadScoreRecord(
                id=_new_id("ls_"),
                account_id=acc.id,
                fit_score=float(sc.get("fit") or 0),
                intent_score=float(sc.get("intent") or 0),
                urgency_score=float(sc.get("urgency") or 0),
                risk_score=float(sc.get("risk") or 0),
                total_score=float(sc.get("total") or 0),
                priority=str(sc.get("priority") or "P3")[:8],
                recommended_channel=sc.get("recommended_channel"),
                reason=sc.get("reason"),
            ))

            # Update account with crawled domain + DQ score
            if result.get("domain") and not acc.domain:
                acc.domain = result["domain"]
                acc.website = f"https://{result['domain']}"
            acc.data_quality_score = float(result.get("data_quality", {}).get("score", 0))
            acc.status = "enriched"
            acc.updated_at = _utcnow()

            # Persist new contacts (avoid dup by email/phone)
            for c in result.get("contacts", []):
                if c.get("type") == "email":
                    session.add(ContactRecord(
                        id=_new_id("ct_"),
                        account_id=acc.id,
                        name=c.get("name"),
                        role=c.get("role"),
                        email=c.get("value"),
                        source=c.get("source") or "enrichment",
                        consent_status="legitimate_interest",
                        opt_out=False,
                        risk_level=acc.risk_level,
                    ))
                elif c.get("type") in ("phone", "whatsapp"):
                    session.add(ContactRecord(
                        id=_new_id("ct_"),
                        account_id=acc.id,
                        name=None,
                        role=None,
                        phone=c.get("value"),
                        source=c.get("source") or "enrichment",
                        consent_status="legitimate_interest",
                        opt_out=False,
                        risk_level=acc.risk_level,
                    ))

            enriched += 1

        try:
            await session.commit()
        except Exception as exc:  # noqa: BLE001
            await session.rollback()
            return {"status": "commit_failed", "error": str(exc)}

    return {
        "import_id": import_id,
        "status": "enriched",
        "accounts_enriched": enriched,
        "level": level,
        "next_action": f"GET /api/v1/data/import/{import_id}/report",
    }


# ── Report ────────────────────────────────────────────────────────
@router.get("/import/{import_id}/report")
async def import_report(import_id: str) -> dict[str, Any]:
    async with async_session_factory() as session:
        try:
            imp = (await session.execute(
                select(RawLeadImport).where(RawLeadImport.id == import_id)
            )).scalar_one_or_none()
            if not imp:
                raise HTTPException(404, "import_not_found")
            accounts = (await session.execute(select(AccountRecord))).scalars().all()
        except HTTPException:
            raise
        except Exception as exc:  # noqa: BLE001
            return {"status": "skipped_db_unreachable", "error": str(exc)}

        related = [a for a in accounts if (a.extra or {}).get("import_id") == import_id]
        priority_counts: dict[str, int] = {}
        # Collect latest scores per account
        try:
            scores = (await session.execute(
                select(LeadScoreRecord).where(
                    LeadScoreRecord.account_id.in_([a.id for a in related])
                )
            )).scalars().all()
            for s in scores:
                priority_counts[s.priority] = priority_counts.get(s.priority, 0) + 1
        except Exception:
            scores = []

    return {
        "import_id": import_id,
        "source_name": imp.source_name,
        "source_type": imp.source_type,
        "status": imp.status,
        "rows_total": imp.rows_total,
        "rows_normalized": imp.rows_normalized,
        "rows_rejected": imp.rows_rejected,
        "rows_duplicate": imp.rows_duplicate,
        "accounts_in_graph_from_this_import": len(related),
        "scored_accounts": len(scores),
        "priority_distribution": priority_counts,
        "allowed_use": imp.allowed_use,
        "consent_status": imp.consent_status,
        "risk_level": imp.risk_level,
    }


# ── Suppression list ──────────────────────────────────────────────
@router.post("/suppression")
async def add_suppression(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """
    Add a suppression entry. At least one of email/phone/domain required.
    Body: {email?, phone?, domain?, reason?}
    """
    email = body.get("email")
    phone = body.get("phone")
    domain = body.get("domain")
    if not (email or phone or domain):
        raise HTTPException(400, "at_least_one_of_email_phone_domain_required")
    rec = SuppressionRecord(
        id=_new_id("sup_"),
        email=str(email).strip().lower() if email else None,
        phone=str(phone).strip() if phone else None,
        domain=str(domain).strip().lower() if domain else None,
        reason=str(body.get("reason") or "opt_out")[:128],
    )
    async with async_session_factory() as session:
        ok = await _safe_commit(session, rec)
    return {
        "id": rec.id,
        "email": rec.email, "phone": rec.phone, "domain": rec.domain,
        "reason": rec.reason,
        "status": "ok" if ok else "skipped_db_unreachable",
    }


@router.get("/suppression")
async def list_suppression(limit: int = 200) -> dict[str, Any]:
    async with async_session_factory() as session:
        try:
            rows = (await session.execute(
                select(SuppressionRecord).limit(min(1000, limit))
            )).scalars().all()
        except Exception as exc:  # noqa: BLE001
            return {"status": "skipped_db_unreachable", "error": str(exc), "items": []}
        return {
            "status": "ok",
            "count": len(rows),
            "items": [
                {
                    "id": r.id, "email": r.email, "phone": r.phone, "domain": r.domain,
                    "reason": r.reason, "created_at": r.created_at.isoformat(),
                }
                for r in rows
            ],
        }


# ── Listings ──────────────────────────────────────────────────────
@router.get("/imports")
async def list_imports(limit: int = 50) -> dict[str, Any]:
    async with async_session_factory() as session:
        try:
            rows = (await session.execute(
                select(RawLeadImport).order_by(RawLeadImport.created_at.desc()).limit(min(500, limit))
            )).scalars().all()
        except Exception as exc:  # noqa: BLE001
            return {"status": "skipped_db_unreachable", "error": str(exc), "items": []}
        return {
            "count": len(rows),
            "items": [
                {
                    "id": r.id, "source_name": r.source_name, "source_type": r.source_type,
                    "status": r.status, "rows_total": r.rows_total,
                    "rows_normalized": r.rows_normalized, "rows_rejected": r.rows_rejected,
                    "rows_duplicate": r.rows_duplicate,
                    "risk_level": r.risk_level, "created_at": r.created_at.isoformat(),
                }
                for r in rows
            ],
        }


@router.get("/accounts")
async def list_accounts(
    limit: int = 50,
    sector: str | None = None,
    city: str | None = None,
    status: str | None = None,
    priority: str | None = None,
) -> dict[str, Any]:
    async with async_session_factory() as session:
        try:
            q = select(AccountRecord)
            if sector:
                q = q.where(AccountRecord.sector == sector)
            if city:
                q = q.where(AccountRecord.city == city)
            if status:
                q = q.where(AccountRecord.status == status)
            q = q.order_by(AccountRecord.data_quality_score.desc()).limit(min(500, limit))
            rows = (await session.execute(q)).scalars().all()

            score_map: dict[str, LeadScoreRecord] = {}
            if rows:
                ids = [r.id for r in rows]
                scores = (await session.execute(
                    select(LeadScoreRecord).where(LeadScoreRecord.account_id.in_(ids))
                )).scalars().all()
                for s in scores:
                    if s.account_id not in score_map or s.created_at > score_map[s.account_id].created_at:
                        score_map[s.account_id] = s
        except Exception as exc:  # noqa: BLE001
            return {"status": "skipped_db_unreachable", "error": str(exc), "items": []}

        items = []
        for a in rows:
            s = score_map.get(a.id)
            if priority and (not s or s.priority != priority):
                continue
            items.append({
                "id": a.id, "company_name": a.company_name, "domain": a.domain,
                "website": a.website, "city": a.city, "sector": a.sector,
                "google_place_id": a.google_place_id, "source_count": a.source_count,
                "best_source": a.best_source, "status": a.status,
                "data_quality_score": a.data_quality_score, "risk_level": a.risk_level,
                "score": {
                    "fit": s.fit_score, "intent": s.intent_score,
                    "total": s.total_score, "priority": s.priority,
                    "recommended_channel": s.recommended_channel,
                } if s else None,
            })
        return {"count": len(items), "items": items}


@router.get("/accounts/{account_id}")
async def get_account(account_id: str) -> dict[str, Any]:
    async with async_session_factory() as session:
        try:
            acc = (await session.execute(
                select(AccountRecord).where(AccountRecord.id == account_id)
            )).scalar_one_or_none()
            if not acc:
                raise HTTPException(404, "account_not_found")
            contacts = (await session.execute(
                select(ContactRecord).where(ContactRecord.account_id == account_id)
            )).scalars().all()
            signals = (await session.execute(
                select(SignalRecord).where(SignalRecord.account_id == account_id)
            )).scalars().all()
            scores = (await session.execute(
                select(LeadScoreRecord).where(
                    LeadScoreRecord.account_id == account_id
                ).order_by(LeadScoreRecord.created_at.desc()).limit(1)
            )).scalars().all()
        except HTTPException:
            raise
        except Exception as exc:  # noqa: BLE001
            return {"status": "skipped_db_unreachable", "error": str(exc)}

        latest = scores[0] if scores else None
        return {
            "account": {
                "id": acc.id, "company_name": acc.company_name,
                "domain": acc.domain, "website": acc.website,
                "city": acc.city, "country": acc.country, "sector": acc.sector,
                "google_place_id": acc.google_place_id,
                "source_count": acc.source_count, "best_source": acc.best_source,
                "status": acc.status, "data_quality_score": acc.data_quality_score,
                "risk_level": acc.risk_level, "extra": acc.extra,
                "created_at": acc.created_at.isoformat(),
                "updated_at": acc.updated_at.isoformat(),
            },
            "contacts": [
                {"id": c.id, "name": c.name, "role": c.role, "email": c.email,
                 "phone": c.phone, "source": c.source, "consent_status": c.consent_status,
                 "opt_out": c.opt_out, "risk_level": c.risk_level}
                for c in contacts
            ],
            "signals": [
                {"id": s.id, "type": s.signal_type, "value": s.signal_value,
                 "source_url": s.source_url, "confidence": s.confidence,
                 "detected_at": s.detected_at.isoformat()}
                for s in signals
            ],
            "score": {
                "fit": latest.fit_score, "intent": latest.intent_score,
                "urgency": latest.urgency_score, "risk": latest.risk_score,
                "total": latest.total_score, "priority": latest.priority,
                "recommended_channel": latest.recommended_channel, "reason": latest.reason,
            } if latest else None,
        }


@router.post("/accounts/{account_id}/score")
async def score_account(account_id: str) -> dict[str, Any]:
    """Recompute score from current data in the graph."""
    async with async_session_factory() as session:
        try:
            acc = (await session.execute(
                select(AccountRecord).where(AccountRecord.id == account_id)
            )).scalar_one_or_none()
            if not acc:
                raise HTTPException(404, "account_not_found")
            contacts = (await session.execute(
                select(ContactRecord).where(ContactRecord.account_id == account_id)
            )).scalars().all()
            signals = (await session.execute(
                select(SignalRecord).where(SignalRecord.account_id == account_id)
            )).scalars().all()
        except HTTPException:
            raise
        except Exception as exc:  # noqa: BLE001
            return {"status": "skipped_db_unreachable", "error": str(exc)}

        first_email = next((c.email for c in contacts if c.email), None)
        first_phone = next((c.phone for c in contacts if c.phone), None)

        account_dict = {
            "id": acc.id, "company_name": acc.company_name, "domain": acc.domain,
            "website": acc.website, "city": acc.city, "country": acc.country,
            "sector": acc.sector, "google_place_id": acc.google_place_id,
            "best_source": acc.best_source, "source_count": acc.source_count,
            "risk_level": acc.risk_level, "email": first_email, "phone": first_phone,
            "allowed_use": (acc.extra or {}).get("allowed_use"),
            "opt_out": any(c.opt_out for c in contacts),
            "signals": signals,
        }
        sig_dicts = [
            {"signal_type": s.signal_type, "signal_value": s.signal_value,
             "confidence": s.confidence}
            for s in signals
        ]
        sb = compute_lead_score(account_dict, signals=sig_dicts, technologies=[])
        dq, _reasons = compute_data_quality(account_dict)

        rec = LeadScoreRecord(
            id=_new_id("ls_"),
            account_id=account_id,
            fit_score=sb.fit, intent_score=sb.intent, urgency_score=sb.urgency,
            risk_score=sb.risk, total_score=sb.total, priority=sb.priority,
            recommended_channel=sb.recommended_channel, reason=sb.reason,
        )
        acc.data_quality_score = dq
        acc.updated_at = _utcnow()
        ok = await _safe_commit(session, rec)
        if not ok:
            return {"status": "commit_failed"}

    return {
        "account_id": account_id,
        "score": {
            "fit": sb.fit, "intent": sb.intent, "urgency": sb.urgency,
            "risk": sb.risk, "total": sb.total, "priority": sb.priority,
            "recommended_channel": sb.recommended_channel, "reason": sb.reason,
        },
        "data_quality_score": dq,
    }
