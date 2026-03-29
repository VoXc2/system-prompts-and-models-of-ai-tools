"""Social listening & human-approved comment workflow API."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user, get_db
from app.models.social_listening import SocialPost, CommentDraft, ListeningStream

router = APIRouter()


# ─── Schemas ───

class StreamCreate(BaseModel):
    name: str
    platform: str = "all"
    stream_type: str = "keyword"
    keywords: List[str] = []
    competitors: List[str] = []
    hashtags: List[str] = []
    auto_draft: bool = True
    check_interval_minutes: int = 60


class CommentApproval(BaseModel):
    action: str  # approve, reject, edit_and_approve
    edited_content: Optional[str] = None
    rejection_reason: Optional[str] = None


# ─── Listening Streams ───

@router.get("/streams")
async def list_streams(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """List all listening streams."""
    result = await db.execute(
        select(ListeningStream)
        .where(ListeningStream.tenant_id == current_user["tenant_id"])
        .order_by(ListeningStream.created_at.desc())
    )
    streams = result.scalars().all()
    return {
        "streams": [
            {
                "id": str(s.id),
                "name": s.name,
                "platform": s.platform,
                "stream_type": s.stream_type,
                "keywords": s.keywords,
                "is_active": s.is_active,
                "posts_found": s.posts_found,
                "comments_published": s.comments_published,
                "last_checked_at": s.last_checked_at.isoformat() if s.last_checked_at else None,
            }
            for s in streams
        ]
    }


@router.post("/streams")
async def create_stream(
    req: StreamCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Create a new listening stream."""
    stream = ListeningStream(
        tenant_id=current_user["tenant_id"],
        name=req.name,
        platform=req.platform,
        stream_type=req.stream_type,
        keywords=req.keywords,
        competitors=req.competitors,
        hashtags=req.hashtags,
        auto_draft=req.auto_draft,
        check_interval_minutes=req.check_interval_minutes,
    )
    db.add(stream)
    return {"status": "created", "id": str(stream.id)}


# ─── Detected Posts ───

@router.get("/posts")
async def list_detected_posts(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    status: Optional[str] = None,
    priority: Optional[str] = None,
    limit: int = 50,
):
    """List posts detected by listening streams."""
    query = select(SocialPost).where(
        SocialPost.tenant_id == current_user["tenant_id"]
    )
    if status:
        query = query.where(SocialPost.status == status)
    if priority:
        query = query.where(SocialPost.priority == priority)

    query = query.order_by(SocialPost.relevance_score.desc()).limit(limit)
    result = await db.execute(query)
    posts = result.scalars().all()

    return {
        "posts": [
            {
                "id": str(p.id),
                "platform": p.platform,
                "author_name": p.author_name,
                "author_handle": p.author_handle,
                "content": p.content[:300] if p.content else None,
                "post_url": p.post_url,
                "relevance_score": p.relevance_score,
                "topic": p.topic,
                "icp_match": p.icp_match,
                "priority": p.priority,
                "status": p.status,
                "posted_at": p.posted_at.isoformat() if p.posted_at else None,
            }
            for p in posts
        ],
        "total": len(posts),
    }


# ─── Comment Drafts (Human Approval Workflow) ───

@router.get("/comments/pending")
async def list_pending_comments(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """List comment drafts awaiting human approval."""
    result = await db.execute(
        select(CommentDraft)
        .where(
            CommentDraft.tenant_id == current_user["tenant_id"],
            CommentDraft.status == "pending",
        )
        .order_by(CommentDraft.created_at.desc())
        .limit(50)
    )
    drafts = result.scalars().all()

    return {
        "pending_comments": [
            {
                "id": str(d.id),
                "post_id": str(d.post_id),
                "draft_type": d.draft_type,
                "content": d.content,
                "tone": d.tone,
                "account_type": d.account_type,
                "created_at": d.created_at.isoformat() if d.created_at else None,
            }
            for d in drafts
        ],
        "total": len(drafts),
    }


@router.post("/comments/{comment_id}/review")
async def review_comment(
    comment_id: str,
    req: CommentApproval,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Approve, reject, or edit a comment draft."""
    result = await db.execute(
        select(CommentDraft).where(
            CommentDraft.id == comment_id,
            CommentDraft.tenant_id == current_user["tenant_id"],
        )
    )
    draft = result.scalar_one_or_none()
    if not draft:
        raise HTTPException(status_code=404, detail="التعليق غير موجود")

    now = datetime.now(timezone.utc)

    if req.action == "approve":
        draft.status = "approved"
        draft.approved_by = current_user["user_id"]
        draft.approved_at = now
    elif req.action == "reject":
        draft.status = "rejected"
        draft.rejection_reason = req.rejection_reason
    elif req.action == "edit_and_approve":
        if not req.edited_content:
            raise HTTPException(status_code=400, detail="يجب تقديم المحتوى المعدل")
        draft.status = "approved"
        draft.edited_content = req.edited_content
        draft.approved_by = current_user["user_id"]
        draft.approved_at = now
    else:
        raise HTTPException(status_code=400, detail="الإجراء غير صالح")

    return {"status": draft.status, "comment_id": str(draft.id)}


# ─── Stats ───

@router.get("/stats")
async def listening_stats(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get social listening statistics."""
    tenant_id = current_user["tenant_id"]

    posts_count = await db.execute(
        select(func.count(SocialPost.id)).where(SocialPost.tenant_id == tenant_id)
    )
    pending_comments = await db.execute(
        select(func.count(CommentDraft.id)).where(
            CommentDraft.tenant_id == tenant_id,
            CommentDraft.status == "pending",
        )
    )
    published_comments = await db.execute(
        select(func.count(CommentDraft.id)).where(
            CommentDraft.tenant_id == tenant_id,
            CommentDraft.status == "published",
        )
    )
    active_streams = await db.execute(
        select(func.count(ListeningStream.id)).where(
            ListeningStream.tenant_id == tenant_id,
            ListeningStream.is_active == True,
        )
    )

    return {
        "total_posts_detected": posts_count.scalar() or 0,
        "pending_approvals": pending_comments.scalar() or 0,
        "published_comments": published_comments.scalar() or 0,
        "active_streams": active_streams.scalar() or 0,
    }
