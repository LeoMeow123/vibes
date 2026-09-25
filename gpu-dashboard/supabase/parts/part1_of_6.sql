-- GPU Dashboard schema — part 1 of 6. Run the parts in order (1 → 6); each is safe to re-run.
-- Canonical single-file version: gpu-dashboard/supabase/schema.sql

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
