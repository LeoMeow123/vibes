-- GPU Dashboard schema — part 5 of 6. Run the parts in order (1 → 6); each is safe to re-run.
-- Canonical single-file version: gpu-dashboard/supabase/schema.sql

-- ── Maintenance functions (service role only; the bridge calls these) ───────

-- Roll raw samples up into hourly rows. Re-rolls the most recent rolled hour so
-- late-arriving samples are included. Returns the number of GPU-hour rows written.
create or replace function public.gpu_rollup_hourly()
returns integer
language plpgsql security definer
set search_path = public
as $$
declare
  v_to   timestamptz := date_trunc('hour', now());   -- the current, incomplete hour is excluded
  v_from timestamptz;
  v_n    integer := 0;
begin
  -- GPUs
  select coalesce(max(hour), (select date_trunc('hour', min(ts)) from public.gpu_samples))
    into v_from from public.gpu_samples_hourly;
  if v_from is not null and v_from < v_to then
    insert into public.gpu_samples_hourly as h
      (machine_key, hour, gpu_index, avg_util, max_util, avg_mem_used_mb, max_mem_used_mb,
       mem_total_mb, avg_temp_c, max_temp_c, avg_power_w, n_samples)
    select machine_key, date_trunc('hour', ts), gpu_index,
           avg(util), max(util), avg(mem_used_mb), max(mem_used_mb),
           max(mem_total_mb), avg(temp_c), max(temp_c), avg(power_w), count(*)
      from public.gpu_samples
     where ts >= v_from and ts < v_to
     group by 1, 2, 3
    on conflict (machine_key, gpu_index, hour) do update set
      avg_util = excluded.avg_util,               max_util = excluded.max_util,
      avg_mem_used_mb = excluded.avg_mem_used_mb, max_mem_used_mb = excluded.max_mem_used_mb,
      mem_total_mb = excluded.mem_total_mb,       avg_temp_c = excluded.avg_temp_c,
      max_temp_c = excluded.max_temp_c,           avg_power_w = excluded.avg_power_w,
      n_samples = excluded.n_samples;
    get diagnostics v_n = row_count;
  end if;

  -- Hosts
  select coalesce(max(hour), (select date_trunc('hour', min(ts)) from public.gpu_host_samples))
    into v_from from public.gpu_host_samples_hourly;
  if v_from is not null and v_from < v_to then
    insert into public.gpu_host_samples_hourly as h
      (machine_key, hour, avg_cpu, max_cpu, avg_ram_percent, max_ram_percent, avg_ram_used_gb, ram_total_gb, n_samples)
    select machine_key, date_trunc('hour', ts),
           avg(cpu_percent), max(cpu_percent), avg(ram_percent), max(ram_percent), avg(ram_used_gb), max(ram_total_gb), count(*)
      from public.gpu_host_samples
     where ts >= v_from and ts < v_to
     group by 1, 2
    on conflict (machine_key, hour) do update set
      avg_cpu = excluded.avg_cpu,                 max_cpu = excluded.max_cpu,
      avg_ram_percent = excluded.avg_ram_percent, max_ram_percent = excluded.max_ram_percent,
      avg_ram_used_gb = excluded.avg_ram_used_gb, ram_total_gb = excluded.ram_total_gb,
      n_samples = excluded.n_samples;
  end if;

  return v_n;
end;
$$;

-- Delete raw samples older than p_keep_days (after rolling up, so nothing is lost).
-- Returns the number of rows deleted.
create or replace function public.gpu_prune(p_keep_days integer default 14)
returns integer
language plpgsql security definer
set search_path = public
as $$
declare
  v_cutoff timestamptz := now() - make_interval(days => greatest(coalesce(p_keep_days, 14), 1));
  v_n integer := 0;
  v_m integer := 0;
begin
  perform public.gpu_rollup_hourly();
  delete from public.gpu_samples where ts < v_cutoff;
  get diagnostics v_n = row_count;
  delete from public.gpu_host_samples where ts < v_cutoff;
  get diagnostics v_m = row_count;
  return v_n + v_m;
end;
$$;

revoke all on function public.gpu_rollup_hourly()      from public, anon, authenticated;

revoke all on function public.gpu_prune(integer)       from public, anon, authenticated;

grant execute on function public.gpu_rollup_hourly()   to service_role;

grant execute on function public.gpu_prune(integer)    to service_role;
