# GPU Dashboard

Monitor GPUs across multiple workstations from a single web page. No server required.

![GPU Dashboard Screenshot](screenshot.png)

## How It Works

```
Workstation 1  ──push──►                              ◄──read── GitHub Pages
Workstation 2  ──push──►  GitHub Gist (JSON store)    ◄──       Dashboard
RunAI Pod      ──push──►
```

A lightweight Python agent runs on each machine, collects GPU/CPU/RAM stats every 30 seconds, and pushes them to a GitHub Gist. The dashboard (a static HTML page on GitHub Pages) reads the Gist and displays everything.

- **No server needed** — GitHub Gist is the data store, GitHub Pages hosts the dashboard
- **No inbound ports** — agents push outbound to GitHub API
- **Auto-pause** — stops polling when you switch browser tabs
- **Works anywhere** — Ubuntu workstations, RunAI, any machine with `nvidia-smi` and Python

## What It Shows

| Per Machine | Per GPU | Per Process |
|-------------|---------|-------------|
| CPU usage & core count | Utilization % | Command line |
| RAM usage | VRAM usage | GPU memory |
| Uptime | Temperature | User |
| Freshness (last report) | Power draw | Runtime |

## Quick Start

### 1. Create a GitHub Gist

Go to [gist.github.com](https://gist.github.com), create a new **secret** gist with any content. Copy the Gist ID from the URL:
```
https://gist.github.com/YourUsername/████████████████████████████████
                                      ↑ this is the Gist ID
```

### 2. Create a Personal Access Token

Go to [github.com/settings/tokens](https://github.com/settings/tokens) → **Generate new token (classic)** → check only **`gist`** → Generate.

### 3. Set Up the Template Config

Edit `gpu-dashboard/agent/config.json` with your Gist ID and token:
```json
{
    "gist_id": "YOUR_GIST_ID",
    "github_token": "ghp_YOUR_TOKEN",
    "machine_label": "CHANGE_THIS",
    "machine_type": "workstation",
    "interval_seconds": 30
}
```

This template is used by the install script so you only enter the Gist ID and token once.

### 4. Install the Agent on Each Machine

```bash
# Install dependencies (pick whichever works)
pip install psutil requests
# or: sudo apt install python3-psutil python3-requests

# Run the installer
bash gpu-dashboard/agent/install.sh
```

The installer loads the Gist ID and token from the template, then asks for a machine label and type. It sets up a systemd service that starts automatically on boot.

### 5. Open the Dashboard

Visit the [GPU Dashboard](https://leomeow123.github.io/vibes/gpu-dashboard/) and enter your Gist ID. It saves to your browser so you only need to enter it once.

## Agent Usage

```bash
# Run continuously (default 30s interval)
python3 gpu_agent.py

# Single snapshot then exit (for cron)
python3 gpu_agent.py --once

# Custom interval
python3 gpu_agent.py --interval 60

# Print snapshot without pushing (test)
python3 gpu_agent.py --dry-run
```

## RunAI Workspaces

RunAI workspaces don't have systemd. Run the agent in tmux instead:

```bash
tmux new -s gpu-agent
python3 ~/.local/bin/gpu-agent
# Ctrl-B, D to detach
```

Or use cron for single snapshots every minute:
```bash
crontab -e
# Add: * * * * * python3 ~/.local/bin/gpu-agent --once
```

Note: RunAI workspace restarts wipe the agent — re-run `install.sh` after a restart.

## Configuration

The agent reads config from `~/.config/gpu-dashboard/config.json` or environment variables:

| Config Key | Env Variable | Description |
|------------|-------------|-------------|
| `gist_id` | `GPU_DASH_GIST_ID` | GitHub Gist ID |
| `github_token` | `GPU_DASH_GITHUB_TOKEN` | GitHub PAT with `gist` scope |
| `machine_label` | `GPU_DASH_LABEL` | Display name on dashboard |
| `machine_type` | `GPU_DASH_TYPE` | `workstation` or `runai` |
| `interval_seconds` | — | Polling interval (default 30) |

## Security

- PAT only needs `gist` scope — cannot access repos or org settings
- Config file stored with `chmod 600` (owner-only read)
- Gist is **secret** (not listed on your profile, but readable by anyone with the URL)
- Dashboard stores Gist ID in browser `localStorage`

## Rate Limits

| Action | Rate Limit | Typical Usage |
|--------|-----------|---------------|
| Agent writes (with PAT) | 5,000/hr | 3 machines × 2/min = 360/hr |
| Dashboard reads (no token) | 60/hr | 1/min = 60/hr |
| Dashboard reads (with token) | 5,000/hr | comfortable margin |

Add your token in dashboard Settings for reliable polling at 30s intervals.
