-- GPU Dashboard migration 002, part 1 of 2: gpu_apply_snapshot (bridge / service role).
-- GPU Dashboard — migration 002: direct ingest (agents -> Supabase, no GitHub).
-- Run once in the SQL editor after schema.sql. Idempotent.
--   gpu_apply_snapshot(key, snapshot): machine row + gpu_latest (only if newer) + a history
--     sample at most every 55 s. Service role only (the bridge uses it).
--   gpu_ingest(ingest_key, snapshot): same, for agents; sha256(ingest_key) must match
--     gpu_machines.ingest_key_hash. Callable by anon, so machines only hold their own key.
-- Issue keys with bridge/issue_key.py.

create extension if not exists pgcrypto with schema extensions;

create or replace function public.gpu_apply_snapshot(p_key text, p_snapshot jsonb)
returns jsonb
language plpgsql security definer
set search_path = public, extensions
as $$
declare
  v_ts          timestamptz;
  v_prev        timestamptz;
  v_last_sample timestamptz;
  v_label       text;
  v_host        text;
  v_type        text;
  v_g           jsonb;
  v_rows        integer := 0;
  v_sampled     boolean := false;
begin
  if p_key is null or p_key !~ '^[a-z0-9_-]{1,64}$' then
    raise exception 'bad machine key' using errcode = '22023';
  end if;
  v_ts := (p_snapshot ->> 'timestamp')::timestamptz;
  if v_ts is null then
    raise exception 'snapshot has no timestamp' using errcode = '22023';
  end if;
  v_label := coalesce(p_snapshot -> 'machine' ->> 'label', p_snapshot -> 'machine' ->> 'hostname', p_key);
  v_host  := p_snapshot -> 'machine' ->> 'hostname';
  v_type  := lower(coalesce(p_snapshot -> 'machine' ->> 'type', 'workstation'));

  insert into public.gpu_machines (key, label, hostname, type, last_seen)
  values (p_key, v_label, v_host, v_type, v_ts)
  on conflict (key) do update
    set label = excluded.label, hostname = excluded.hostname, type = excluded.type,
        last_seen = greatest(coalesce(public.gpu_machines.last_seen, excluded.last_seen), excluded.last_seen);

  select ts into v_prev from public.gpu_latest where machine_key = p_key;
  if v_prev is not null and v_prev >= v_ts then
    return jsonb_build_object('ok', true, 'skipped', 'not newer than stored snapshot');
  end if;

  insert into public.gpu_latest (machine_key, ts, received_at, snapshot)
  values (p_key, v_ts, now(), p_snapshot)
  on conflict (machine_key) do update
    set ts = excluded.ts, received_at = now(), snapshot = excluded.snapshot;

  select max(ts) into v_last_sample from public.gpu_host_samples where machine_key = p_key;
  if v_last_sample is null or v_ts - v_last_sample >= interval '55 seconds' then
    v_sampled := true;
    for v_g in select * from jsonb_array_elements(coalesce(p_snapshot -> 'gpus', '[]'::jsonb)) loop
      insert into public.gpu_samples (machine_key, ts, gpu_index, util, util_peak, mem_used_mb, mem_total_mb, temp_c, power_w, n_procs)
      values (p_key, v_ts,
              coalesce((v_g ->> 'index')::smallint, 0),
              (v_g ->> 'utilization_percent')::smallint,
              (v_g ->> 'utilization_peak_percent')::smallint,
              (v_g ->> 'memory_used_mb')::integer,
              (v_g ->> 'memory_total_mb')::integer,
              (v_g ->> 'temperature_c')::smallint,
              (v_g ->> 'power_draw_w')::real,
              jsonb_array_length(coalesce(v_g -> 'processes', '[]'::jsonb)))
      on conflict do nothing;
      v_rows := v_rows + 1;
    end loop;
    insert into public.gpu_host_samples (machine_key, ts, cpu_percent, ram_used_gb, ram_total_gb, ram_percent)
    values (p_key, v_ts,
            (p_snapshot -> 'cpu' ->> 'percent')::real,
            (p_snapshot -> 'ram' ->> 'used_gb')::real,
            (p_snapshot -> 'ram' ->> 'total_gb')::real,
            (p_snapshot -> 'ram' ->> 'percent')::real)
    on conflict do nothing;
  end if;

  return jsonb_build_object('ok', true, 'sampled', v_sampled, 'gpu_rows', v_rows);
end;
$$;

revoke all on function public.gpu_apply_snapshot(text, jsonb) from public, anon, authenticated;
grant execute on function public.gpu_apply_snapshot(text, jsonb) to service_role;
