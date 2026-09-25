-- GPU Dashboard schema — part 6 of 6. Run the parts in order (1 → 6); each is safe to re-run.
-- Canonical single-file version: gpu-dashboard/supabase/schema.sql

-- ── Realtime ────────────────────────────────────────────────────────────────
-- Live cards subscribe to gpu_latest and gpu_machines. RLS is enforced per subscriber.

do $$
begin
  if exists (select 1 from pg_publication where pubname = 'supabase_realtime') then
    if not exists (select 1 from pg_publication_tables
                    where pubname = 'supabase_realtime' and schemaname = 'public' and tablename = 'gpu_latest') then
      alter publication supabase_realtime add table public.gpu_latest;
    end if;
    if not exists (select 1 from pg_publication_tables
                    where pubname = 'supabase_realtime' and schemaname = 'public' and tablename = 'gpu_machines') then
      alter publication supabase_realtime add table public.gpu_machines;
    end if;
  end if;
end;
$$;
