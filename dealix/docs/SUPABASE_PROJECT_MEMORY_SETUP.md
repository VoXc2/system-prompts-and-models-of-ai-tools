# Supabase / pgvector — Project Memory Setup

## Enable pgvector

In the Supabase dashboard: **Database → Extensions →** enable `vector` (pgvector).

Alternatively, the migration `supabase/migrations/202605010001_v3_project_memory.sql` runs `create extension if not exists vector;` (requires sufficient DB privileges).

## Run migration

1. Install [Supabase CLI](https://supabase.com/docs/guides/cli).
2. Link the project: `supabase link --project-ref <ref>`.
3. Push SQL: `supabase db push` **or** paste the migration file into the SQL editor and execute.

## Environment variables

| Variable | Purpose |
|----------|---------|
| `SUPABASE_URL` | Project API URL (server-side only). |
| `SUPABASE_SERVICE_ROLE_KEY` | **Server only** — bypasses RLS; never expose to browsers or mobile clients. |
| `SUPABASE_ANON_KEY` | Optional for public features — **not** for project memory tables. |

Local indexing (no keys required):

```bash
python scripts/index_project_memory.py --root . --out .dealix/project_index.json
python scripts/index_project_memory.py --root . --query "personal operator"
```

## Embedding model choices

- **gte-small** (384 dims) via Edge Function or local worker — low cost, aligns with migration vector(384).
- **OpenAI `text-embedding-3-small`** — set dimension to match your DB column if you change size.
- **BGE-small** — similar footprint; validate dimension before altering the column type.

## Security notes

- **RLS** is enabled on `project_documents`, `project_chunks`, and `strategic_memory` with **no default policies** — intended for **service role from backend only**.
- **Never store API keys, tokens, or private keys** in `content` or `metadata` destined for embeddings.
- Strip or redact secrets **before** chunking; use `should_block_embedding()` in `project_intelligence.py` as a guardrail.

## RLS policy examples (commented in migration)

Uncomment and adapt only after security review. Typical pattern: allow `service_role` full access; deny `anon`/`authenticated` direct reads on strategic embeddings.

## Launch checklist

- [ ] Extension `vector` active  
- [ ] Migration applied without errors  
- [ ] Indexes created (`project_chunks_embedding_hnsw`, etc.)  
- [ ] Backend uses service role only in trusted runtime  
- [ ] Chunk pipeline redacts secrets  
- [ ] Staging load test on `match_project_chunks`  
- [ ] Retention / deletion policy documented  
