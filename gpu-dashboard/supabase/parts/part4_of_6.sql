-- GPU Dashboard schema — part 4 of 6. Run the parts in order (1 → 6); each is safe to re-run.
-- Canonical single-file version: gpu-dashboard/supabase/schema.sql

-- Fleet overview: average GPU utilization per machine per bucket.
create or replace function public.gpu_fleet_history(
  p_from timestamptz, p_to timestamptz, p_bucket_seconds integer default 900)
returns table (bucket timestamptz, machine_key text, util real, gpus integer, mem_used_mb real)
language sql stable security invoker
set search_path = public
as $$
  with raw_start as (
    select machine_key, min(ts) as t from public.gpu_samples group by machine_key
  ),
  src as (
    select s.machine_key, s.ts, s.gpu_index, s.util::real as util, s.mem_used_mb::real as mem_used_mb
      from public.gpu_samples s
     where s.ts >= p_from and s.ts < p_to
    union all
    select h.machine_key, h.hour, h.gpu_index, h.avg_util, h.avg_mem_used_mb
      from public.gpu_samples_hourly h
      left join raw_start r on r.machine_key = h.machine_key
     where h.hour >= p_from and h.hour < p_to
       and h.hour < coalesce(date_trunc('hour', r.t), 'infinity'::timestamptz)
  )
  select to_timestamp(floor(extract(epoch from ts) / greatest(p_bucket_seconds, 1)) * greatest(p_bucket_seconds, 1)) as bucket,
         machine_key,
         avg(util)::real,
         count(distinct gpu_index)::integer,
         (avg(mem_used_mb) * count(distinct gpu_index))::real
    from src
   group by 1, 2
   order by 1, 2;
$$;

-- Drag-to-reorder: one call instead of one update per card.
create or replace function public.gpu_set_order(p_keys text[])
returns void
language plpgsql security invoker
set search_path = public
as $$
begin
  update public.gpu_machines m
     set sort_order = k.ord
    from unnest(p_keys) with ordinality as k(key, ord)
   where m.key = k.key;
end;
$$;

revoke all on function public.gpu_history(text, timestamptz, timestamptz, integer)      from public, anon;

revoke all on function public.gpu_host_history(text, timestamptz, timestamptz, integer) from public, anon;

revoke all on function public.gpu_fleet_history(timestamptz, timestamptz, integer)      from public, anon;

revoke all on function public.gpu_set_order(text[])                                     from public, anon;

grant execute on function public.gpu_history(text, timestamptz, timestamptz, integer)      to authenticated, service_role;

grant execute on function public.gpu_host_history(text, timestamptz, timestamptz, integer) to authenticated, service_role;

grant execute on function public.gpu_fleet_history(timestamptz, timestamptz, integer)      to authenticated, service_role;

grant execute on function public.gpu_set_order(text[])                                     to authenticated, service_role;
