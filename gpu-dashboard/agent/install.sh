#!/usr/bin/env bash
# GPU Dashboard Agent — install script
# Usage: bash install.sh
set -euo pipefail

echo "=== GPU Dashboard Agent Setup ==="
echo ""

# ── Prompt for config ─────────────────────────────────────────────────────────

read -rp "GitHub Gist ID: " GIST_ID
read -rp "GitHub Personal Access Token (gist scope): " -s GITHUB_TOKEN
echo ""
read -rp "Machine label (e.g. 'Workstation 1'): " LABEL
read -rp "Machine type (workstation/runai) [workstation]: " TYPE
TYPE=${TYPE:-workstation}
read -rp "Poll interval in seconds [30]: " INTERVAL
INTERVAL=${INTERVAL:-30}

# ── Write config ──────────────────────────────────────────────────────────────

CONFIG_DIR="$HOME/.config/gpu-dashboard"
mkdir -p "$CONFIG_DIR"
cat > "$CONFIG_DIR/config.json" <<EOF
{
    "gist_id": "$GIST_ID",
    "github_token": "$GITHUB_TOKEN",
    "machine_label": "$LABEL",
    "machine_type": "$TYPE",
    "interval_seconds": $INTERVAL
}
EOF
chmod 600 "$CONFIG_DIR/config.json"
echo "Config written to $CONFIG_DIR/config.json"

# ── Install agent script ─────────────────────────────────────────────────────

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
AGENT_SRC="$SCRIPT_DIR/gpu_agent.py"

mkdir -p "$HOME/.local/bin"
cp "$AGENT_SRC" "$HOME/.local/bin/gpu-agent"
chmod +x "$HOME/.local/bin/gpu-agent"
echo "Agent installed to $HOME/.local/bin/gpu-agent"

# ── Install deps ──────────────────────────────────────────────────────────────

echo "Installing Python dependencies..."
pip install --quiet psutil requests 2>/dev/null || pip3 install --quiet psutil requests

# ── Dry run test ──────────────────────────────────────────────────────────────

echo ""
echo "Testing data collection (dry run)..."
python3 "$HOME/.local/bin/gpu-agent" --dry-run | head -20
echo "..."
echo ""

# ── Install as service or show manual instructions ────────────────────────────

if command -v systemctl &>/dev/null && systemctl --user status >/dev/null 2>&1; then
    echo "Installing systemd user service..."
    mkdir -p "$HOME/.config/systemd/user"

    # Write service file with correct python path
    PYTHON_PATH="$(command -v python3)"
    cat > "$HOME/.config/systemd/user/gpu-agent.service" <<SVCEOF
[Unit]
Description=GPU Dashboard Agent
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
ExecStart=$PYTHON_PATH $HOME/.local/bin/gpu-agent
Restart=always
RestartSec=10

[Install]
WantedBy=default.target
SVCEOF

    systemctl --user daemon-reload
    systemctl --user enable gpu-agent
    systemctl --user start gpu-agent
    echo ""
    echo "Service installed and started!"
    echo "  Check status:  systemctl --user status gpu-agent"
    echo "  View logs:     journalctl --user -u gpu-agent -f"
    echo "  Stop:          systemctl --user stop gpu-agent"
else
    echo "systemd user services not available."
    echo ""
    echo "To run manually (in tmux/screen):"
    echo "  python3 $HOME/.local/bin/gpu-agent"
    echo ""
    echo "To run via cron (every minute, single snapshot):"
    echo "  crontab -e"
    echo "  * * * * * python3 $HOME/.local/bin/gpu-agent --once"
fi

echo ""
echo "=== Setup complete! ==="
