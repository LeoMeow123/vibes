# GPU Dashboard

Monitor the lab's GPUs from one web page, with live status and utilization history. Anyone with a **@salk.edu** email can sign in; no GitHub account or token is needed.

![GPU Dashboard Screenshot](screenshot.png)

## How It Works

```
Workstation 1 ──push──►                      ┌─ bridge ─►  Supabase (Postgres + Auth + Realtime)  ◄──read──  Dashboard (GitHub Pages)
Workstation 2 ──push──►  GitHub Gist  ───────┤                 · gpu_latest    live cards
RunAI pod     ──push──►  (agents, as before) │                 · gpu_samples   history & charts
                                             └─ read ───►  Slack bot · daily report · 30-min alert (still on the Gist)
```

- **Agents are unchanged.** Each machine runs the same small Python agent, pushing a JSON snapshot to the shared GitHub Gist every 30 s.
- **A bridge copies the Gist into Supabase.** One instance (on the lab workstation) polls the Gist and writes the latest snapshot per machine, plus one history sample per GPU per minute. It also rolls history up to hourly rows and prunes raw rows after 14 days.
- **The dashboard reads Supabase, not GitHub.** Sign in with a one-time code sent to your Salk email. Live cards update over Realtime; history charts are bucketed server-side.
- **Access is enforced in the database.** Row-level security allows reads only for signed-in users whose email ends in `@salk.edu` (plus an optional allow-list). Writes are only possible with the service-role key, which lives on the bridge machine.
- **Preferences are shared.** Renaming, hiding and reordering machines is stored in Supabase, so everyone sees the same layout. "Hide" replaces the old "Remove" (nothing is deleted; the machine keeps reporting).

## What It Shows

The live page is built around one question: **which GPUs are free right now, and who is on the rest?**

| Top of page | Per machine | Per GPU | History tab |
|---|---|---|---|
| Free GPUs / total, machines online, average utilization, VRAM in use, running jobs, power draw | Free-count badge, CPU and RAM, 3-hour utilization sparkline | State (free / busy / offline), utilization with 30-min peak, VRAM, temperature, power | All machines: average utilization and VRAM per machine |
| "GPUs now" strip: one square per GPU, click to jump to the machine | Rename, hide and reorder, shared with everyone | Who is using it: user, command, memory, runtime | Per machine: utilization, VRAM, temperature, power, CPU/RAM per GPU |
| Filters: machine type, "Has free GPU", sort, search | | | Ranges 1h to 90d, table view for every chart |

SLEAP inference progress is not shown here anymore; the **Inference progress** tile and the header link jump to the [HCM Monitor](https://leomeow123.github.io/hcm-dashboard/#inference-panel), which tracks inference and recording health.

A GPU counts as **free** when it has no visible process and utilization is below 10%. A machine that has not reported for 10 minutes shows as **offline**.

Raw per-minute history is kept for 14 days (configurable); hourly roll-ups are kept indefinitely, so long ranges always work.

## Viewing the Dashboard

1. Open **https://leomeow123.github.io/vibes/gpu-dashboard/**
2. Enter your `@salk.edu` email and click **Send code**.
3. Open the email **in the same browser** and click the sign-in link. You land back on the dashboard, signed in, and stay signed in on that browser. (Once custom SMTP is configured the email carries a 6-digit code instead, which you type into the page.)

The built-in mailer can only send a couple of sign-in emails per hour across the whole lab. If you see "Email limit reached", wait a bit, or ask the maintainer to configure custom SMTP (see below).

Preview without signing in: append `?demo=1` to the URL for synthetic data.

## Quick Start (Add Your Machine)

Unchanged from before. Run this on any machine with `nvidia-smi` and Python:

```bash
pip install psutil requests
curl -sL https://raw.githubusercontent.com/LeoMeow123/vibes/main/gpu-dashboard/agent/install.sh -o /tmp/gpu-install.sh && \
curl -sL https://raw.githubusercontent.com/LeoMeow123/vibes/main/gpu-dashboard/agent/gpu_agent.py -o /tmp/gpu_agent.py && \
SCRIPT_DIR=/tmp bash /tmp/gpu-install.sh
```

The installer asks for the lab Gist ID and token (ask the maintainer), sets up a systemd user service on workstations, and prints tmux/cron instructions on RunAI. Files are also on VAST:

```bash
bash /home/exx/vast/leo/vibing/gpu-dashboard/agent/install.sh    # workstation
bash /root/vast/leo/vibing/gpu-dashboard/agent/install.sh        # RunAI
```

RunAI workspace restarts wipe the agent; re-run the installer and `tmux new -d -s gpu-agent "python3 ~/.local/bin/gpu-agent"` afterwards.

## Maintainer Setup (one-time)

### 1. Database

In the lab Supabase project: **SQL Editor → New query**, paste `supabase/schema.sql`, **Run**. It is idempotent. If the editor limits paste size, run `supabase/parts/part1_of_6.sql` … `part6_of_6.sql` in order instead.

This creates the `gpu_*` tables, the `gpu_is_salk_user()` check, the history functions, the maintenance functions, and adds `gpu_latest` / `gpu_machines` to the Realtime publication. Other tools sharing the project are untouched.

### 2. Authentication

In **Authentication**:

- **Sign In / Providers → Email**: enabled (default). "Confirm email" stays on.
- **URL Configuration** (required): set **Site URL** to `https://leomeow123.github.io/vibes/gpu-dashboard/` and add the same address under **Redirect URLs**. The sign-in link in the email redirects here; without this the link is refused.

Salk's mail security opens links before recipients do, which consumes one-time sign-in links, so the dashboard is set to code-based sign-in (`CODE_IN_EMAIL = true`). That requires the SMTP and template steps below.

**Optional, needs custom SMTP:** Supabase only lets you edit email templates once custom SMTP is configured (or on the Pro plan). After step 3 below, open **Emails → Templates → Magic Link**, put `{{ .Token }}` in the body so the email carries a 6-digit code, e.g.

```html
<h2>GPU Dashboard sign-in</h2>
<p>Your one-time code is</p>
<p style="font-size:28px;font-weight:bold;letter-spacing:4px">{{ .Token }}</p>
<p>Type it into the dashboard page you already have open. It is valid for 1 hour.</p>
```

The dashboard already leads with the code entry (`CODE_IN_EMAIL = true` in `index.html`). Do this for **both** the "Confirm signup" template (first-time users) and the "Magic Link" template (returning users). Leaving the link out means a mail scanner has nothing to consume.

Anyone can *request* a sign-in email, but the database only returns data to `@salk.edu` accounts, so a stray sign-up sees nothing. To admit a collaborator without a Salk address:

```sql
insert into public.gpu_allowed_emails (email, note) values ('someone@ucsd.edu', 'rotation student');
```

### 3. Optional: custom SMTP

Supabase's built-in mailer allows **2 auth emails per hour** per project and locks the email templates. That is workable once everyone is signed in (sessions persist per browser), but onboarding the lab in one afternoon needs more, and the code-in-email flow needs editable templates.

Most SMTP providers (Resend, Postmark, SendGrid) require a verified sending domain, which the lab does not have. The zero-domain option is a Gmail account with an app password:

1. On a Google account you control (a lab Gmail is ideal), turn on 2-step verification, then create an **App password** (Google Account → Security → App passwords).
2. In Supabase: **Authentication → Emails → SMTP Settings** (older layout: **Project Settings → Authentication → SMTP**). Enable custom SMTP with host `smtp.gmail.com`, port `587`, username = the Gmail address, password = the app password, sender email = the Gmail address, sender name `GPU Dashboard`.
3. Under **Authentication → Rate Limits**, raise "emails sent per hour" to something like 30.

Gmail allows about 500 messages per day, far more than the lab will use.

### 4. Bridge

On one machine that has the agent config (the lab workstation that runs the Slack bot is the natural choice):

```bash
bash /home/exx/vast/leo/vibing/gpu-dashboard/bridge/install.sh
```

It asks for the project URL and the **service_role** key (Project Settings → API Keys; never the anon/publishable key), writes `~/.config/gpu-dashboard/supabase.json` with mode 600, does a dry run, one real pass, and installs the `gpu-bridge` systemd user service.

```bash
systemctl --user status gpu-bridge        # running?
journalctl --user -u gpu-bridge -f        # logs: one line per pass
gpu-bridge --status                       # what Supabase holds
gpu-bridge --dry-run                      # read the Gist, write nothing
```

### 5. Dashboard

`index.html` has the project URL and publishable key near the top of the script (`SUPA_URL`, `SUPA_KEY`). The publishable key is meant to be public; row-level security does the gating. Push to `main` and GitHub Pages serves it. The previous Gist-based page is kept as `legacy.html`.

## Data Model

| Table | Contents | Retention |
|---|---|---|
| `gpu_machines` | one row per machine: label, hostname, type, `display_name`, `hidden`, `sort_order` | forever |
| `gpu_latest` | latest full agent snapshot per machine (JSON, same shape as the Gist file) | latest only |
| `gpu_samples` | per-GPU util / VRAM / temp / power, ~1 row per GPU per minute | 14 days |
| `gpu_host_samples` | CPU / RAM per machine, same cadence | 14 days |
| `gpu_samples_hourly`, `gpu_host_samples_hourly` | hourly averages and maxima | forever |
| `gpu_allowed_emails` | viewers without a Salk address | forever |

Functions viewers can call: `gpu_history`, `gpu_host_history`, `gpu_fleet_history` (bucketed server-side, raw where available and hourly beyond), `gpu_set_order`. Maintenance (service role only): `gpu_rollup_hourly`, `gpu_prune`.

At the current scale (about 13 GPUs) raw history is roughly 20k rows per day, well inside the free tier.

## Slack Integration

Unchanged: `/gpu-status` and the daily report still read the Gist, which the agents keep writing.

| Command | Description |
|---|---|
| `/gpu-status` | Shared lab dashboard (all machines) |
| `/gpu-status mine` | Your personal dashboard |
| `/gpu-status register GIST_ID [TOKEN]` | Link your own Gist |
| `/gpu-status unregister` | Remove the link |
| `/gpu-status help` | All commands |

## Agent Usage

```bash
python3 gpu_agent.py              # run continuously (default 30 s)
python3 gpu_agent.py --once       # single snapshot (for cron)
python3 gpu_agent.py --interval 60
python3 gpu_agent.py --dry-run    # print the snapshot without pushing
```

Config lives in `~/.config/gpu-dashboard/config.json` or environment variables:

| Config key | Env variable | Description |
|---|---|---|
| `gist_id` | `GPU_DASH_GIST_ID` | Shared Gist ID |
| `github_token` | `GPU_DASH_GITHUB_TOKEN` | GitHub token with `gist` scope |
| `machine_label` | `GPU_DASH_LABEL` | Display name (also the machine key in Supabase) |
| `machine_type` | `GPU_DASH_TYPE` | `workstation` or `runai` |
| `interval_seconds` | — | Push interval (default 120) |

The agent may still attach SLEAP inference / ROI progress summaries to its snapshot for other consumers; the dashboard ignores those fields.

## Security Notes

- Viewers authenticate with Supabase Auth; data access is enforced by row-level security on every `gpu_*` table. Anonymous requests get nothing.
- The service-role key exists only in `~/.config/gpu-dashboard/supabase.json` (mode 600) on the bridge machine.
- The Gist and its token still work exactly as before, but nobody needs them to *view* anything anymore.
- Snapshots include usernames and command lines of GPU processes, as they always did; they are now visible only to Salk accounts.

## Roadmap

- **Phase 2, ingest:** agents post straight to Supabase with a per-machine key (revocable), retiring the shared Gist token and the bridge.
- Slack bot and reports read Supabase instead of the Gist.
- "Sign in with Microsoft" via Salk's Entra tenant, if IT ever registers the app; Supabase Auth supports it with no other changes.
