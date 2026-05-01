-- Dealix v3 — Project + strategic memory on Postgres/pgvector
-- Apply via Supabase SQL editor or `supabase db push` after linking the project.
-- RLS: enabled with no broad policies by default — use service role from backend only.

create extension if not exists vector;

-- ── Core tables ─────────────────────────────────────────────

create table if not exists public.project_documents (
    id uuid primary key default gen_random_uuid(),
    path text not null,
    source_type text,
    content_hash text not null,
    metadata jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now(),
    unique (path, content_hash)
);

create table if not exists public.project_chunks (
    id uuid primary key default gen_random_uuid(),
    document_id uuid not null references public.project_documents (id) on delete cascade,
    chunk_index int not null,
    content text not null,
    embedding vector(384),
    metadata jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now()
);

create table if not exists public.strategic_memory (
    id uuid primary key default gen_random_uuid(),
    category text,
    content text not null,
    embedding vector(384),
    metadata jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now()
);

-- ── Similarity search helpers (cosine distance) ─────────────

create or replace function public.match_project_chunks(
    query_embedding vector(384),
    match_count int default 12,
    min_similarity float default 0.05
)
returns table (
    id uuid,
    document_id uuid,
    chunk_index int,
    content text,
    similarity float
)
language sql
stable
parallel safe
as $$
    select
        pc.id,
        pc.document_id,
        pc.chunk_index,
        pc.content,
        (1 - (pc.embedding <=> query_embedding))::float as similarity
    from public.project_chunks pc
    where pc.embedding is not null
      and (1 - (pc.embedding <=> query_embedding)) >= min_similarity
    order by pc.embedding <=> query_embedding
    limit greatest(match_count, 1);
$$;

create or replace function public.match_strategic_memory(
    query_embedding vector(384),
    match_count int default 12,
    min_similarity float default 0.05
)
returns table (
    id uuid,
    category text,
    content text,
    similarity float
)
language sql
stable
parallel safe
as $$
    select
        sm.id,
        sm.category,
        sm.content,
        (1 - (sm.embedding <=> query_embedding))::float as similarity
    from public.strategic_memory sm
    where sm.embedding is not null
      and (1 - (sm.embedding <=> query_embedding)) >= min_similarity
    order by sm.embedding <=> query_embedding
    limit greatest(match_count, 1);
$$;

-- ── Indexes ─────────────────────────────────────────────────

create index if not exists project_documents_path_idx on public.project_documents (path);
create index if not exists project_chunks_document_idx on public.project_chunks (document_id);

-- HNSW (Supabase 15+); falls back to creating via dashboard if version lacks operator class.
create index if not exists project_chunks_embedding_hnsw
    on public.project_chunks
    using hnsw (embedding vector_cosine_ops);

create index if not exists strategic_memory_embedding_hnsw
    on public.strategic_memory
    using hnsw (embedding vector_cosine_ops);

-- ── Row Level Security ──────────────────────────────────────
-- No client-side anon access to embeddings. Backend uses service role.

alter table public.project_documents enable row level security;
alter table public.project_chunks enable row level security;
alter table public.strategic_memory enable row level security;

-- Example policies (KEEP COMMENTED — enable only with explicit security review):
--
-- create policy "service_role_all_documents"
--   on public.project_documents
--   for all
--   using (auth.role() = 'service_role')
--   with check (auth.role() = 'service_role');
--
-- create policy "service_role_all_chunks"
--   on public.project_chunks
--   for all
--   using (auth.role() = 'service_role')
--   with check (auth.role() = 'service_role');
--
-- create policy "service_role_all_strategic"
--   on public.strategic_memory
--   for all
--   using (auth.role() = 'service_role')
--   with check (auth.role() = 'service_role');

comment on table public.project_documents is 'Source files / docs indexed for Dealix Project Intelligence.';
comment on table public.project_chunks is 'Chunked text + optional pgvector embedding; never store raw secrets.';
comment on table public.strategic_memory is 'Strategic notes and decisions for operator + agents.';
