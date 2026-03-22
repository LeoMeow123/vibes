# GPU Dashboard

Monitor GPUs across multiple workstations from a single web page. No server required.

## How It Works

```
Ubuntu Box 1 ──push──►                              ◄──read── GitHub Pages
Ubuntu Box 2 ──push──►  GitHub Gist (JSON store)    ◄──  Dashboard
RunAI Pod    ──push──►
```

A lightweight Python agent runs on each machine, collects GPU/CPU/RAM stats every 30 seconds, and pushes them to a GitHub Gist. The dashboard (a static HTML page) reads the Gist and displays everything.

- **No server** — Gist is the data store, GitHub Pages hosts the dashboard
- **No inbound ports** — agents push outbound to GitHub API
- **Auto-pause** — stops polling when you switch tabs

## Quick Start

### 1. Create a GitHub Gist

Go to [gist.github.com](https://gist.github.com) and create a new **secret** gist with any content (e.g., `init`). Copy the Gist ID from the URL:
```
https://gist.github.com/YourUsername/████████████████████████████████
                                      ↑ this is the Gist ID
```

### 2. Create a Personal Access Token

Go to [github.com/settings/tokens](https://github.com/settings/tokens) → **Generate new token (classic)** → select only the **`gist`** scope → Generate.

### 3. Install the Agent

On each machine you want to monitor:

```bash
# Clone or download the agent
git clone https://github.com/LeoMeow123/vibes.git /tmp/vibes

# Run the installer
bash /tmp/vibes/gpu-dashboard/agent/install.sh
```

The installer will:
- Prompt for your Gist ID, token, and machine label
- Install the agent to `~/.local/bin/gpu-agent`
- Set up a systemd user service (or show manual instructions for RunAI)

**Or install manually:**

```bash
pip install psutil requests

# Configure
mkdir -p ~/.config/gpu-dashboard
cat > ~/.config/gpu-dashboard/config.json << 'EOF'
{
    "gist_id": "YOUR_GIST_ID",
    "github_token": "ghp_YOUR_TOKEN",
    "machine_label": "Workstation 1",
    "machine_type": "workstation",
    "interval_seconds": 30
}
EOF
chmod 600 ~/.config/gpu-dashboard/config.json

# Run
python gpu-dashboard/agent/gpu_agent.py
```

### 4. Open the Dashboard

Visit the hosted page or open `index.html` locally. Enter your Gist ID on first visit.

## Agent Options

```bash
# Run continuously (default)
python gpu_agent.py

# Single snapshot then exit (for cron)
python gpu_agent.py --once

# Custom interval
python gpu_agent.py --interval 60

# Dry run (print JSON, don't push)
python gpu_agent.py --dry-run
```

## What It Shows

**Per machine:**
- CPU usage and core count
- RAM usage
- Machine uptime
- Freshness indicator (how recently the agent reported)

**Per GPU:**
- Utilization %
- VRAM usage
- Temperature
- Power draw

**Per process:**
- Command line
- GPU memory
- User
- Runtime

## RunAI Workspaces

RunAI workspaces typically don't have systemd. Options:

```bash
# Option 1: Run in tmux
tmux new -s gpu-agent
python gpu_agent.py
# Ctrl-B, D to detach

# Option 2: Run via cron (single snapshots)
crontab -e
# Add: * * * * * python3 ~/.local/bin/gpu-agent --once

# Option 3: Add to workspace init script
```

## Environment Variables

Instead of a config file, you can use environment variables:

| Variable | Description |
|----------|-------------|
| `GPU_DASH_GIST_ID` | GitHub Gist ID |
| `GPU_DASH_GITHUB_TOKEN` | GitHub Personal Access Token |
| `GPU_DASH_LABEL` | Machine display name |
| `GPU_DASH_TYPE` | `workstation` or `runai` |

## Security

- The PAT only needs `gist` scope — it cannot access repos or org settings
- Config file is stored with `chmod 600` (owner-only read)
- The Gist is **secret** (not listed on your profile) but readable by anyone with the URL
- Process command lines are included in the data — if this is a concern, review what's running before deploying
- The dashboard stores the Gist ID in `localStorage` — clear browser data to remove it

## Rate Limits

| Action | Rate | Budget |
|--------|------|--------|
| Agent writes (authenticated) | 5,000/hr | 3 machines × 2/min = 360/hr |
| Dashboard reads (no token) | 60/hr | 1 tab × 1/min = 60/hr |
| Dashboard reads (with token) | 5,000/hr | comfortable margin |

Tip: Add your token in dashboard Settings for reliable polling.
