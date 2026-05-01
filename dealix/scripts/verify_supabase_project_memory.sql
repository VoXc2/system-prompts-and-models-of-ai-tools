-- Run in Supabase SQL editor or psql against staging DB after migration.
-- Expects migration 202605010001_v3_project_memory.sql applied.

-- 1) Extension
select extname, extversion
from pg_extension
where extname = 'vector';

-- 2) Tables
select table_schema, table_name
from information_schema.tables
where table_schema = 'public'
  and table_name in ('project_documents', 'project_chunks', 'strategic_memory')
order by table_name;

-- 3) Functions
select routine_name
from information_schema.routines
where specific_schema = 'public'
  and routine_name in ('match_project_chunks', 'match_strategic_memory')
order by routine_name;

-- 4) RLS enabled
select relname, relrowsecurity as rls_enabled
from pg_class c
join pg_namespace n on n.oid = c.relnamespace
where n.nspname = 'public'
  and relname in ('project_documents', 'project_chunks', 'strategic_memory')
order by relname;
