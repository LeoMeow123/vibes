-- GPU Dashboard schema — part 3 of 6. Run the parts in order (1 → 6); each is safe to re-run.
-- Canonical single-file version: gpu-dashboard/supabase/schema.sql

-- No insert/delete policies for authenticated: writes come from the service role, which bypasses RLS.

-- ── Viewer-callable functions (run as the caller, so RLS applies) ───────────

-- Per-GPU history for one machine. Raw samples where they exist, hourly roll-ups
-- for older ranges, bucketed server-side so the browser never pulls raw rows.
create or replace function public.gpu_history(
  p_machine text, p_from timestamptz, p_to timestamptz, p_bucket_seconds integer default 300)
returns table (
  bucket timestamptz, gpu_index smallint, util real, util_max smallint,
  mem_used_mb real, mem_total_mb integer, temp_c real, power_w real)
language sql stable security invoker
set search_path = public
as $$
  with raw_start as (
    select min(ts) as t from public.gpu_samples where machine_key = p_machine
  ),
  src as (
    select s.ts, s.gpu_index, s.util::real as util, s.util as util_max,
           s.mem_used_mb::real as mem_used_mb, s.mem_total_mb, s.temp_c::real as temp_c, s.power_w
      from public.gpu_samples s
     where s.machine_key = p_machine and s.ts >= p_from and s.ts < p_to
    union all
    select h.hour, h.gpu_index, h.avg_util, h.max_util, h.avg_mem_used_mb, h.mem_total_mb, h.avg_temp_c, h.avg_power_w
      from public.gpu_samples_hourly h, raw_start r
     where h.machine_key = p_machine and h.hour >= p_from and h.hour < p_to
       and h.hour < coalesce(date_trunc('hour', r.t), 'infinity'::timestamptz)
  )
  select to_timestamp(floor(extract(epoch from ts) / greatest(p_bucket_seconds, 1)) * greatest(p_bucket_seconds, 1)) as bucket,
         gpu_index,
         avg(util)::real, max(util_max)::smallint, avg(mem_used_mb)::real, max(mem_total_mb)::integer,
         avg(temp_c)::real, avg(power_w)::real
    from src
   group by 1, 2
   order by 1, 2;
$$;

-- CPU / RAM history for one machine.
create or replace function public.gpu_host_history(
  p_machine text, p_from timestamptz, p_to timestamptz, p_bucket_seconds integer default 300)
returns table (
  bucket timestamptz, cpu_percent real, cpu_max real, ram_percent real, ram_max real,
  ram_used_gb real, ram_total_gb real)
language sql stable security invoker
set search_path = public
as $$
  with raw_start as (
    select min(ts) as t from public.gpu_host_samples where machine_key = p_machine
  ),
  src as (
    select s.ts, s.cpu_percent, s.cpu_percent as cpu_max, s.ram_percent, s.ram_percent as ram_max,
           s.ram_used_gb, s.ram_total_gb
      from public.gpu_host_samples s
     where s.machine_key = p_machine and s.ts >= p_from and s.ts < p_to
    union all
    select h.hour, h.avg_cpu, h.max_cpu, h.avg_ram_percent, h.max_ram_percent, h.avg_ram_used_gb, h.ram_total_gb
      from public.gpu_host_samples_hourly h, raw_start r
     where h.machine_key = p_machine and h.hour >= p_from and h.hour < p_to
       and h.hour < coalesce(date_trunc('hour', r.t), 'infinity'::timestamptz)
  )
  select to_timestamp(floor(extract(epoch from ts) / greatest(p_bucket_seconds, 1)) * greatest(p_bucket_seconds, 1)) as bucket,
         avg(cpu_percent)::real, max(cpu_max)::real, avg(ram_percent)::real, max(ram_max)::real,
         avg(ram_used_gb)::real, max(ram_total_gb)::real
    from src
   group by 1
   order by 1;
$$;
