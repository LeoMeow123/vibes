#!/usr/bin/env bash
# GPU Dashboard bridge — install script (run on ONE machine, e.g. the lab workstation
# that already runs the Slack bot). Needs the existing agent config with the Gist token.
set -euo pipefail

echo "=== GPU Dashboard Bridge Setup (Gist -> Supabase) ==="
echo ""

SCRIPT_DIR="${SCRIPT_DIR:-$(cd "$(dirname "$0")" && pwd)}"
CONFIG_DIR="$HOME/.config/gpu-dashboard"
GIST_CONFIG="$CONFIG_DIR/config.json"
SUPA_CONFIG="$CONFIG_DIR/supabase.json"

if [ ! -f "$GIST_CONFIG" ]; then
    echo "ERROR: $GIST_CONFIG not found. Run the agent installer first (it writes the Gist config)."
    exit 1
fi

# ── Supabase config ──────────────────────────────────────────────────────────

if [ -f "$SUPA_CONFIG" ]; then
    echo "Found existing $SUPA_CONFIG"
    python3 -c "import json;d=json.load(open('$SUPA_CONFIG'));print('  url:', d.get('url'));print('  keep_days:', d.get('keep_days', 14));print('  service_role_key: ****')"
    read -rp "Use this config? [Y/n]: " USE_EXISTING
    USE_EXISTING=${USE_EXISTING:-Y}
else
    USE_EXISTING="n"
fi

if [[ "$USE_EXISTING" =~ ^[Nn] ]]; then
    read -rp "Supabase project URL (https://xxxx.supabase.co): " SUPA_URL
    while true; do
        echo "Supabase secret key: Project Settings -> API Keys -> 'secret' (sb_secret_...),"
        echo "  or the 'service_role' key on the Legacy tab. NOT the publishable/anon key."
        read -rp "Paste the key (input hidden): " -s SUPA_KEY
        echo ""
        SUPA_KEY="${SUPA_KEY//[[:space:]]/}"
        if [ -z "$SUPA_KEY" ]; then
            echo "  Nothing was pasted. Try again."
        elif [[ "$SUPA_KEY" == sb_publishable_* ]]; then
            echo "  That is the PUBLISHABLE (public) key. The bridge needs the secret / service_role key."
        elif [[ "$SUPA_KEY" == eyJ* ]] && ! python3 -c "
import sys, json, base64
p = sys.argv[1].split('.')[1]; p += '=' * (-len(p) % 4)
sys.exit(0 if json.loads(base64.urlsafe_b64decode(p)).get('role') == 'service_role' else 1)" "$SUPA_KEY" 2>/dev/null; then
            echo "  That legacy key is not the service_role key (it is probably anon). Try again."
        else
            echo "  Key accepted (${SUPA_KEY:0:10}..., ${#SUPA_KEY} chars)."
            break
        fi
    done
    read -rp "Keep raw per-minute history for how many days? [14]: " KEEP_DAYS
    KEEP_DAYS=${KEEP_DAYS:-14}
    mkdir -p "$CONFIG_DIR"
    python3 - "$SUPA_CONFIG" "$SUPA_URL" "$SUPA_KEY" "$KEEP_DAYS" <<'EOF'
import json, sys
path, url, key, keep = sys.argv[1:5]
json.dump({"url": url.rstrip("/"), "service_role_key": key, "keep_days": int(keep)}, open(path, "w"), indent=2)
EOF
    chmod 600 "$SUPA_CONFIG"
    echo "Config written to $SUPA_CONFIG (mode 600)"
fi

# ── Install script ───────────────────────────────────────────────────────────

mkdir -p "$HOME/.local/bin"
cp "$SCRIPT_DIR/gist_bridge.py" "$HOME/.local/bin/gpu-bridge"
chmod +x "$HOME/.local/bin/gpu-bridge"
echo "Bridge installed to $HOME/.local/bin/gpu-bridge"

python3 -c "import requests" 2>/dev/null || { echo "Installing requests..."; pip3 install --user --quiet requests || pip install --quiet requests; }

# ── Test ─────────────────────────────────────────────────────────────────────

echo ""
echo "Dry run (reads the Gist, writes nothing):"
python3 "$HOME/.local/bin/gpu-bridge" --dry-run
echo ""
echo "One real pass:"
python3 "$HOME/.local/bin/gpu-bridge" --once
echo ""

# ── systemd user service ─────────────────────────────────────────────────────

if command -v systemctl &>/dev/null && systemctl --user status >/dev/null 2>&1; then
    mkdir -p "$HOME/.config/systemd/user"
    PYTHON_PATH="$(command -v python3)"
    cat > "$HOME/.config/systemd/user/gpu-bridge.service" <<SVCEOF
[Unit]
Description=GPU Dashboard Bridge (Gist -> Supabase)
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
ExecStart=$PYTHON_PATH $HOME/.local/bin/gpu-bridge
Restart=always
RestartSec=15

[Install]
WantedBy=default.target
SVCEOF
    systemctl --user daemon-reload
    systemctl --user enable gpu-bridge
    systemctl --user restart gpu-bridge
    echo "Service installed and started."
    echo "  Status:  systemctl --user status gpu-bridge"
    echo "  Logs:    journalctl --user -u gpu-bridge -f"
    echo "  Data:    gpu-bridge --status"
else
    echo "systemd user services not available. Run in tmux instead:"
    echo "  tmux new -d -s gpu-bridge \"python3 $HOME/.local/bin/gpu-bridge\""
fi

echo ""
echo "=== Bridge setup complete ==="
