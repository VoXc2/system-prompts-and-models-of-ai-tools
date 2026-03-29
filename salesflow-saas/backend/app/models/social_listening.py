"""Social listening and human-approved comment workflow models."""
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.models.base import TenantModel


class SocialPost(TenantModel):
    """A social media post detected by the listening engine."""
    __tablename__ = "social_posts"

    platform = Column(String(50), nullable=False, index=True)  # linkedin, twitter, instagram, tiktok
    external_id = Column(String(255))
    author_name = Column(String(255))
    author_handle = Column(String(255))
    author_url = Column(Text)
    content = Column(Text)
    post_url = Column(Text)
    post_type = Column(String(50))  # text, image, video, carousel
    engagement_count = Column(Integer, default=0)
    posted_at = Column(DateTime(timezone=True))

    # Classification
    relevance_score = Column(Integer, default=50)  # 0-100
    topic = Column(String(100))  # industry, pain_point, competitor, event
    icp_match = Column(String(50))  # high, medium, low, none
    priority = Column(String(20), default="medium", index=True)  # low, medium, high, urgent
    status = Column(String(50), default="new", index=True)  # new, reviewed, actioned, skipped

    matched_keywords = Column(JSONB, default=list)
    extra_data = Column("metadata", JSONB, default=dict)


class CommentDraft(TenantModel):
    """AI-drafted comment awaiting human approval."""
    __tablename__ = "comment_drafts"

    post_id = Column(UUID(as_uuid=True), ForeignKey("social_posts.id"), nullable=False, index=True)
    draft_type = Column(String(50), default="value_add")  # value_add, contrarian, proof_point, question
    content = Column(Text, nullable=False)
    tone = Column(String(50), default="professional")  # professional, casual, authority
    account_type = Column(String(50), default="brand")  # brand, founder, sales_leader, employee
    status = Column(String(50), default="pending", index=True)  # pending, approved, rejected, published
    approved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime(timezone=True))
    published_at = Column(DateTime(timezone=True))
    rejection_reason = Column(Text)
    edited_content = Column(Text)  # Human-edited version (if modified before publishing)


class ListeningStream(TenantModel):
    """Configuration for a social listening stream."""
    __tablename__ = "listening_streams"

    name = Column(String(255), nullable=False)
    platform = Column(String(50), nullable=False)  # linkedin, twitter, instagram, all
    stream_type = Column(String(50), nullable=False)  # keyword, competitor, industry, hashtag
    keywords = Column(JSONB, default=list)
    competitors = Column(JSONB, default=list)
    hashtags = Column(JSONB, default=list)
    is_active = Column(Boolean, default=True)
    auto_draft = Column(Boolean, default=True)  # Auto-generate comment drafts
    check_interval_minutes = Column(Integer, default=60)
    last_checked_at = Column(DateTime(timezone=True))
    posts_found = Column(Integer, default=0)
    comments_drafted = Column(Integer, default=0)
    comments_published = Column(Integer, default=0)
