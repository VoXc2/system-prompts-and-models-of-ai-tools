"""Enable PostgreSQL Row-Level Security on tenant-scoped tables.

Revision ID: 20260417_0002
Revises: 20260403_0001
Create Date: 2026-04-17

This migration enables RLS on all tenant-scoped tables. RLS policies
filter by current_setting('app.tenant_id') which the app sets via
SET LOCAL on each request (see app/database_rls.py).

OWASP A01:2025 — moves access control from app convention to DB-enforced
default-deny posture.

Skipped on SQLite (CI). Production PostgreSQL only.
"""

from typing import Sequence, Union

from alembic import op


revision: str = "20260417_0002"
down_revision: Union[str, None] = "20260403_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Tables with tenant_id column that need RLS
TENANT_SCOPED_TABLES = [
    "deals",
    "leads",
    "approval_requests",
    "evidence_packs",
    "contradictions",
    "compliance_controls",
    "ai_conversations",
    "audit_logs",
    "integration_sync_states",
    "strategic_deals",
    "domain_events",
    "consents",
    "complaints",
    "messages",
    "activities",
    "proposals",
    "sequences",
    "company_profiles",
    "deal_matches",
    "calls",
    "auto_bookings",
    "trust_scores",
    "scorecards",
]


def upgrade() -> None:
    """Enable RLS on tenant-scoped tables (PostgreSQL only)."""
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return  # SQLite/CI: skip

    for table in TENANT_SCOPED_TABLES:
        # Check if table exists before applying RLS
        op.execute(f"""
            DO $$
            BEGIN
                IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = '{table}') THEN
                    ALTER TABLE {table} ENABLE ROW LEVEL SECURITY;
                    ALTER TABLE {table} FORCE ROW LEVEL SECURITY;

                    DROP POLICY IF EXISTS tenant_isolation_select ON {table};
                    CREATE POLICY tenant_isolation_select ON {table}
                        FOR SELECT
                        USING (tenant_id::text = current_setting('app.tenant_id', true));

                    DROP POLICY IF EXISTS tenant_isolation_insert ON {table};
                    CREATE POLICY tenant_isolation_insert ON {table}
                        FOR INSERT
                        WITH CHECK (tenant_id::text = current_setting('app.tenant_id', true));

                    DROP POLICY IF EXISTS tenant_isolation_update ON {table};
                    CREATE POLICY tenant_isolation_update ON {table}
                        FOR UPDATE
                        USING (tenant_id::text = current_setting('app.tenant_id', true))
                        WITH CHECK (tenant_id::text = current_setting('app.tenant_id', true));

                    DROP POLICY IF EXISTS tenant_isolation_delete ON {table};
                    CREATE POLICY tenant_isolation_delete ON {table}
                        FOR DELETE
                        USING (tenant_id::text = current_setting('app.tenant_id', true));
                END IF;
            END $$;
        """)


def downgrade() -> None:
    """Disable RLS on all tenant-scoped tables."""
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return

    for table in TENANT_SCOPED_TABLES:
        op.execute(f"""
            DO $$
            BEGIN
                IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = '{table}') THEN
                    DROP POLICY IF EXISTS tenant_isolation_select ON {table};
                    DROP POLICY IF EXISTS tenant_isolation_insert ON {table};
                    DROP POLICY IF EXISTS tenant_isolation_update ON {table};
                    DROP POLICY IF EXISTS tenant_isolation_delete ON {table};
                    ALTER TABLE {table} NO FORCE ROW LEVEL SECURITY;
                    ALTER TABLE {table} DISABLE ROW LEVEL SECURITY;
                END IF;
            END $$;
        """)
