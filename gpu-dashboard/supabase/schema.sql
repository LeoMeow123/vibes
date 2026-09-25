-- ============================================================================
-- GPU Dashboard v2 — Supabase schema
-- ============================================================================
-- Paste into the Supabase SQL editor (Dashboard → SQL Editor → New query) and
-- run it once. It is idempotent: re-running it is safe.
--
-- Every object is prefixed gpu_ so it coexists with the other lab tools that
-- share this Supabase project (tmaze-recorder, hcm-metadata, mouse-colony).
-- Those tools keep their own fully-open policies; nothing here touches them.
--
-- Tables
--   gpu_machines             one row per machine + shared display prefs (rename / hide / order)
--   gpu_latest               latest full agent snapshot per machine (what the live cards render)
--   gpu_samples              per-GPU time series (~1 row per GPU per minute), pruned after N days
--   gpu_host_samples         per-machine CPU / RAM time series, pruned after N days
--   gpu_samples_hourly       hourly roll-ups per GPU, kept indefinitely
--   gpu_host_samples_hourly  hourly roll-ups per machine, kept indefinitely
--   gpu_allowed_emails       optional allow-list for viewers WITHOUT an @salk.edu address
--
-- Access model
--   read   : any signed-in user whose email ends in @salk.edu (or is listed in gpu_allowed_emails)
--   prefs  : the same users may rename / hide / reorder machines (column-level grant)
--   write  : only the service role (the bridge today, a per-machine ingest function later).
--            Row-level security blocks every other role from writing.
--   anon   : nothing at all.
-- ============================================================================

begin;

-- ── Identity ────────────────────────────────────────────────────────────────

create table if not exists public.gpu_allowed_emails (
  email     text primary key,
  note      text,
  added_at  timestamptz not null default now()
);
alter table public.gpu_allowed_emails enable row level security;
revoke all on table public.gpu_allowed_emails from anon, authenticated;

-- True when the caller is a signed-in user with a Salk address (or allow-listed).
-- security definer so it can consult gpu_allowed_emails, which viewers cannot read.
create or replace function public.gpu_is_salk_user()
returns boolean
language sql stable security definer
set search_path = public
as $$
  select
    coalesce(auth.jwt() ->> 'role', '') = 'authenticated'
    and (
      lower(coalesce(auth.jwt() ->> 'email', '')) like '%@salk.edu'
      or exists (
        select 1 from public.gpu_allowed_emails e
        where lower(e.email) = lower(coalesce(auth.jwt() ->> 'email', ''))
      )
    );
$$;
revoke all on function public.gpu_is_salk_user() from public;
grant execute on function public.gpu_is_salk_user() to anon, authenticated, service_role;

-- ── Tables ──────────────────────────────────────────────────────────────────

create table if not exists public.gpu_machines (
  key              text primary key,                       -- stable slug, e.g. 'blackwell-workstation'
  label            text not null,                          -- label reported by the agent
  display_name     text,                                   -- viewer rename (null = use label)
  hostname         text,
  type             text not null default 'workstation',    -- 'workstation' | 'runai'
  hidden           boolean not null default false,         -- viewer "hide" (replaces the old delete)
  sort_order       integer,                                -- viewer drag order (null = by recency)
  notes            text,
  first_seen       timestamptz not null default now(),
  last_seen        timestamptz,
  ingest_key_hash  text                                    -- phase 2: sha256 of a per-machine ingest key
);

create table if not exists public.gpu_latest (
  machine_key  text primary key references public.gpu_machines(key) on delete cascade,
  ts           timestamptz not null,                       -- snapshot timestamp written by the agent
  received_at  timestamptz not null default now(),
  snapshot     jsonb not null                              -- full agent snapshot, same shape as the Gist file
);

create table if not exists public.gpu_samples (
  id            bigint generated always as identity primary key,
  machine_key   text not null references public.gpu_machines(key) on delete cascade,
  ts            timestamptz not null,
  gpu_index     smallint not null,
  util          smallint,
  util_peak     smallint,
  mem_used_mb   integer,
  mem_total_mb  integer,
  temp_c        smallint,
  power_w       real,
  n_procs       smallint,
  unique (machine_key, gpu_index, ts)
);
create index if not exists gpu_samples_machine_ts_idx on public.gpu_samples (machine_key, ts desc);
create index if not exists gpu_samples_ts_idx on public.gpu_samples (ts);

create table if not exists public.gpu_host_samples (
  id            bigint generated always as identity primary key,
  machine_key   text not null references public.gpu_machines(key) on delete cascade,
  ts            timestamptz not null,
  cpu_percent   real,
  ram_used_gb   real,
  ram_total_gb  real,
  ram_percent   real,
  unique (machine_key, ts)
);
create index if not exists gpu_host_samples_machine_ts_idx on public.gpu_host_samples (machine_key, ts desc);
create index if not exists gpu_host_samples_ts_idx on public.gpu_host_samples (ts);

create table if not exists public.gpu_samples_hourly (
  machine_key      text not null references public.gpu_machines(key) on delete cascade,
  hour             timestamptz not null,
  gpu_index        smallint not null,
  avg_util         real,
  max_util         smallint,
  avg_mem_used_mb  real,
  max_mem_used_mb  integer,
  mem_total_mb     integer,
  avg_temp_c       real,
  max_temp_c       smallint,
  avg_power_w      real,
  n_samples        integer,
  primary key (machine_key, gpu_index, hour)
);

create table if not exists public.gpu_host_samples_hourly (
  machine_key      text not null references public.gpu_machines(key) on delete cascade,
  hour             timestamptz not null,
  avg_cpu          real,
  max_cpu          real,
  avg_ram_percent  real,
  max_ram_percent  real,
  avg_ram_used_gb  real,
  ram_total_gb     real,
  n_samples        integer,
  primary key (machine_key, hour)
);

-- ── Row-level security ──────────────────────────────────────────────────────

alter table public.gpu_machines            enable row level security;
alter table public.gpu_latest              enable row level security;
alter table public.gpu_samples             enable row level security;
alter table public.gpu_host_samples        enable row level security;
alter table public.gpu_samples_hourly      enable row level security;
alter table public.gpu_host_samples_hourly enable row level security;

-- Supabase grants anon/authenticated everything on new public tables by default. Undo that.
revoke all on table
  public.gpu_machines, public.gpu_latest, public.gpu_samples, public.gpu_host_samples,
  public.gpu_samples_hourly, public.gpu_host_samples_hourly
from anon, authenticated;

grant select on table
  public.gpu_machines, public.gpu_latest, public.gpu_samples, public.gpu_host_samples,
  public.gpu_samples_hourly, public.gpu_host_samples_hourly
to authenticated;

-- Viewers may only touch the display-preference columns.
grant update (display_name, hidden, sort_order, notes) on table public.gpu_machines to authenticated;

drop policy if exists gpu_machines_read  on public.gpu_machines;
drop policy if exists gpu_machines_prefs on public.gpu_machines;
create policy gpu_machines_read  on public.gpu_machines for select to authenticated using (public.gpu_is_salk_user());
create policy gpu_machines_prefs on public.gpu_machines for update to authenticated
  using (public.gpu_is_salk_user()) with check (public.gpu_is_salk_user());

drop policy if exists gpu_latest_read on public.gpu_latest;
create policy gpu_latest_read on public.gpu_latest for select to authenticated using (public.gpu_is_salk_user());

drop policy if exists gpu_samples_read on public.gpu_samples;
create policy gpu_samples_read on public.gpu_samples for select to authenticated using (public.gpu_is_salk_user());

drop policy if exists gpu_host_samples_read on public.gpu_host_samples;
create policy gpu_host_samples_read on public.gpu_host_samples for select to authenticated using (public.gpu_is_salk_user());

drop policy if exists gpu_samples_hourly_read on public.gpu_samples_hourly;
create policy gpu_samples_hourly_read on public.gpu_samples_hourly for select to authenticated using (public.gpu_is_salk_user());

drop policy if exists gpu_host_samples_hourly_read on public.gpu_host_samples_hourly;
create policy gpu_host_samples_hourly_read on public.gpu_host_samples_hourly for select to authenticated using (public.gpu_is_salk_user());

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

commit;

-- ── Optional: allow a collaborator without a Salk address ───────────────────
-- insert into public.gpu_allowed_emails (email, note) values ('someone@ucsd.edu', 'rotation student');
