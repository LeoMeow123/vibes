#!/usr/bin/env bash
# slack_alert.sh — Alert on Slack when GPU dashboard machines go offline
#
# Checks the Gist every run. Alerts once when a machine goes stale (>1hr).
# Alerts again when it recovers. No spam in between.
#
# Cron: */30 * * * * bash /home/exx/vast/leo/vibing/gpu-dashboard/agent/slack_alert.sh

set -euo pipefail

SLACK_WEBHOOK=$(python3 -c "import json,os;print(json.load(open(os.path.expanduser('~/.config/gpu-dashboard/slack.json')))['webhook'])")
STALE_MINUTES=60
CONFIG="$HOME/.config/gpu-dashboard/config.json"
ALERT_DIR="/tmp/gpu-dash-alerts"
GIST_CACHE="/tmp/gpu-dash-gist.json"

mkdir -p "$ALERT_DIR"

# Read config
GIST_ID=$(python3 -c "import json;print(json.load(open('$CONFIG'))['gist_id'])")
TOKEN=$(python3 -c "import json;print(json.load(open('$CONFIG'))['github_token'])")

# Fetch Gist → temp file
curl -s -H "Authorization: token $TOKEN" -H "Accept: application/vnd.github.v3+json" \
  "https://api.github.com/gists/$GIST_ID" > "$GIST_CACHE"

# Parse and check each machine
STALE_MIN_PY="$STALE_MINUTES"
python3 - "$GIST_CACHE" "$STALE_MIN_PY" "$ALERT_DIR" "$SLACK_WEBHOOK" << 'PYEOF'
import json, sys, os, subprocess
from datetime import datetime, timezone

gist_file, stale_min, alert_dir, webhook = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4]

with open(gist_file) as f:
    gist = json.load(f)

now = datetime.now(timezone.utc)
alerts = []
recoveries = []

for fname, fdata in gist.get("files", {}).items():
    if not fname.startswith("gpu-status-"):
        continue
    try:
        machine = json.loads(fdata["content"])
        label = machine.get("machine", {}).get("label", fname)
        ts_str = machine.get("timestamp", "")
        ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
        age_min = (now - ts).total_seconds() / 60

        alert_file = os.path.join(alert_dir, label.replace(" ", "_") + ".stale")

        gpus = machine.get("gpus", [])
        gpu_summary = ", ".join(f"GPU{g.get('index',0)}:{g.get('utilization_percent',0)}%" for g in gpus)

        if age_min > stale_min:
            if not os.path.exists(alert_file):
                alerts.append(f":red_circle: *{label}* — no update for {int(age_min)} min\n   Last seen: {ts_str}\n   GPUs: {gpu_summary}")
                open(alert_file, "w").write(ts_str)
        else:
            if os.path.exists(alert_file):
                recoveries.append(f":large_green_circle: *{label}* — back online ({int(age_min)} min ago)\n   GPUs: {gpu_summary}")
                os.remove(alert_file)
    except Exception as e:
        print(f"  Error parsing {fname}: {e}", file=sys.stderr)

def send_slack(text):
    subprocess.run(
        ["curl", "-s", "-X", "POST", webhook, "-H", "Content-type: application/json",
         "-d", json.dumps({"text": text})],
        capture_output=True
    )

if alerts:
    msg = ":warning: *GPU Dashboard Alert*\n\n" + "\n\n".join(alerts)
    msg += "\n\nDashboard: https://leomeow123.github.io/vibes/gpu-dashboard/"
    send_slack(msg)
    print(f"Sent {len(alerts)} alert(s)")

if recoveries:
    msg = ":white_check_mark: *GPU Recovery*\n\n" + "\n\n".join(recoveries)
    send_slack(msg)
    print(f"Sent {len(recoveries)} recovery notice(s)")

if not alerts and not recoveries:
    print("All machines OK")
PYEOF

rm -f "$GIST_CACHE"
