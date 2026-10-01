-- GPU Dashboard migration 002, part 2 of 2 (run after part 1): gpu_ingest for agents.
-- Canonical single file: supabase/migration_002_direct_ingest.sql

create or replace function public.gpu_ingest(p_ingest_key text, p_snapshot jsonb)
returns jsonb
language plpgsql security definer
set search_path = public, extensions
as $$
declare
  v_key text;
begin
  if p_ingest_key is null or length(p_ingest_key) < 20 then
    raise exception 'invalid ingest key' using errcode = '28000';
  end if;
  select key into v_key
    from public.gpu_machines
   where ingest_key_hash = encode(digest(p_ingest_key, 'sha256'), 'hex');
  if v_key is null then
    raise exception 'unknown ingest key' using errcode = '28000';
  end if;
  return public.gpu_apply_snapshot(v_key, p_snapshot);
end;
$$;

revoke all on function public.gpu_ingest(text, jsonb) from public, authenticated;
grant execute on function public.gpu_ingest(text, jsonb) to anon, service_role;
