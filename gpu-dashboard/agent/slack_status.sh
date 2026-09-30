#!/usr/bin/env bash
# slack_status.sh — daily GPU status to Slack (compact: free GPUs first, one line per
# machine, problems only if any, last-24h utilization digest).
#
# Usage:
#   bash slack_status.sh          # post to the webhook in ~/.config/gpu-dashboard/slack.json
#   bash slack_status.sh --dry    # print to the terminal only
#
# Cron (weekday 8am):
#   0 8 * * 1-5 bash /home/exx/vast/leo/vibing/gpu-dashboard/agent/slack_status.sh
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
if [[ "${1:-}" == "--dry" ]]; then
    python3 "$HERE/slack_report.py" --daily --dry
else
    python3 "$HERE/slack_report.py" --daily --post
fi
