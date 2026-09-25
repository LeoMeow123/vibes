-- GPU Dashboard schema — part 2 of 6. Run the parts in order (1 → 6); each is safe to re-run.
-- Canonical single-file version: gpu-dashboard/supabase/schema.sql

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
