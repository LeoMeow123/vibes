#!/usr/bin/env python3
"""GPU Dashboard Slack Bot — /gpu-status and /hcm-status slash commands.

Runs in Socket Mode (outbound websocket, no public URL). Tokens live in
~/.config/gpu-dashboard/slack.json, never in this file.

    /gpu-status                  compact lab GPU status (free GPUs first)
    /gpu-status mine             status from your own registered Gist
    /gpu-status register ID [T]  link a Gist (token only for private gists)
    /gpu-status unregister
    /hcm-status                  HCM recording health + inference

Service:  systemctl --user restart gpu-slack-bot
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

sys.path.insert(0, str(Path(__file__).resolve().parent))
import slack_report as rep  # noqa: E402

CONFIG_DIR = Path.home() / ".config" / "gpu-dashboard"
USER_GISTS_PATH = CONFIG_DIR / "user_gists.json"
HCM_JSON = Path(__file__).resolve().parent.parent.parent / "hcm-monitor" / "hcm_daily_status.json"
HCM_DASHBOARD = "https://leomeow123.github.io/hcm-dashboard/"

SLACK = rep.slack_config()
app = App(token=SLACK["bot_token"])


# ── Personal gists ────────────────────────────────────────────────────────────


def load_user_gists() -> dict:
    return rep.load_json(USER_GISTS_PATH)


def save_user_gists(data: dict) -> None:
    USER_GISTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    USER_GISTS_PATH.write_text(json.dumps(data, indent=2))


# ── /gpu-status ───────────────────────────────────────────────────────────────

HELP = (
    ":information_source: *GPU status commands*\n"
    "`/gpu-status` — lab GPUs: free GPUs first, one line per machine, problems if any\n"
    "`/gpu-status mine` — the same view from your own registered Gist\n"
    "`/gpu-status register GIST_ID [TOKEN]` — link your Gist (token only for private gists)\n"
    "`/gpu-status unregister` — remove the link\n"
    f"Full dashboard: <{rep.DASHBOARD_URL}|GPU Dashboard>  ·  inference progress: <{rep.HCM_URL}|HCM Monitor>"
)


@app.command("/gpu-status")
def handle_gpu_status(ack, respond, body):
    ack()
    text = (body.get("text") or "").strip()
    user_id = body.get("user_id", "")
    try:
        if text == "help":
            respond(HELP)
            return

        if text.startswith("register"):
            parts = text.split()
            if len(parts) < 2:
                respond(":x: Usage: `/gpu-status register GIST_ID [TOKEN]`")
                return
            gist_id, token = parts[1], (parts[2] if len(parts) > 2 else None)
            try:
                machines = rep.machines_from_gist(gist_id, token)
            except Exception:  # noqa: BLE001
                machines = []
            if not machines:
                respond(f":x: Could not read any machines from Gist `{gist_id}`. Check the ID and, for private gists, the token.")
                return
            gists = load_user_gists()
            gists[user_id] = {"gist_id": gist_id, "token": token}
            save_user_gists(gists)
            respond(f":white_check_mark: Registered, {len(machines)} machine(s). Use `/gpu-status mine`.")
            return

        if text == "unregister":
            gists = load_user_gists()
            if user_id in gists:
                del gists[user_id]
                save_user_gists(gists)
                respond(":white_check_mark: Your Gist has been unlinked.")
            else:
                respond("You don't have a registered Gist.")
            return

        if text == "mine":
            gists = load_user_gists()
            if user_id not in gists:
                respond(":x: No Gist registered. `/gpu-status register YOUR_GIST_ID [TOKEN]` first.")
                return
            cfg = gists[user_id]
            machines = rep.machines_from_gist(cfg["gist_id"], cfg.get("token"))
            blocks, fallback = rep.build_blocks(rep.analyse(machines), title="Your GPUs")
            respond(text=fallback, blocks=blocks)
            return

        machines, _source = rep.load_machines()
        blocks, fallback = rep.build_blocks(rep.analyse(machines))
        respond(text=fallback, blocks=blocks)

    except Exception as e:  # noqa: BLE001
        respond(f":x: Error: {e}")


# ── /hcm-status ───────────────────────────────────────────────────────────────

# Camera wiring mismatch — see hcm-monitor/CAMERA_SWAP.md
HCM_CAM_PHYSICAL = {"cam_01": "Cam 1", "cam_02": "Cam 4", "cam_03": "Cam 2", "cam_04": "Cam 3"}
HCM_CAM_ORDER = ["cam_01", "cam_03", "cam_04", "cam_02"]


def build_hcm_status() -> str:
    if not HCM_JSON.exists():
        return ":x: HCM data not found. Run scan_daily.py first."
    data = json.loads(HCM_JSON.read_text())
    dates = sorted(data.get("dates", {}).keys())
    if not dates:
        return ":x: No HCM recording dates found."

    # The newest date is always partial (robocopy runs at 3 AM); report the previous one.
    report_date = dates[-2] if len(dates) >= 2 else dates[-1]
    day = data["dates"][report_date]
    summary = day.get("summary", {})
    transfer = data.get("scan_info", {}).get("transfer", {})
    scan_time = data.get("scan_info", {}).get("scan_time") or data.get("scan_info", {}).get("last_scan") or ""

    max_behind = max([info.get("days_behind") or 999 for info in transfer.values()] or [0])
    if max_behind <= 1:
        transfer_line = ":white_check_mark: Transfer OK, all cameras current"
    elif max_behind <= 3:
        transfer_line = f":warning: *Transfer delayed, latest data is {max_behind} days old.* Check robocopy on the recording PC."
    else:
        transfer_line = f":x: *Transfer stale, no new data for {max_behind} days.* Recording or robocopy is down."

    status = summary.get("status", "unknown")
    status_emoji = {"healthy": ":large_green_circle:", "degraded": ":large_yellow_circle:", "missing": ":red_circle:"}.get(status, ":white_circle:")
    cam_lines = []
    for cam in HCM_CAM_ORDER:
        c = day.get("cameras", {}).get(cam)
        label = HCM_CAM_PHYSICAL[cam]
        if not c or "videos" not in c:
            cam_lines.append(f"   :x: {label}: no data")
            continue
        flags = c.get("flags", [])
        icon = ":white_check_mark:" if "healthy" in flags else (":warning:" if c["videos"] > 0 else ":x:")
        note = " — crash storm" if "crash_storm" in flags else " — crashes" if "crash_day" in flags else " — incomplete" if "incomplete" in flags else ""
        cam_lines.append(f"   {icon} {label}: {c.get('hours_count', '?')}/24 h, {c['videos']} videos, {c.get('sessions', '?')} sessions{note}")

    overall = data.get("scan_info", {}).get("overall", {})
    inf_done, inf_total = overall.get("inference_videos_done", 0), overall.get("inference_videos_total", 0)
    inf_line = ""
    if inf_total:
        remaining = inf_total - inf_done
        inf_line = (f":microscope: Inference: {inf_done:,}/{inf_total:,} ({inf_done / inf_total * 100:.1f}%), {remaining:,} remaining"
                    if remaining > 0 else ":microscope: Inference: complete")

    lines = [f":house: *HCM recording, {report_date}* — {status_emoji} {status}", "", transfer_line, ""] + cam_lines
    if inf_line:
        lines += ["", inf_line]
    lines += ["", f"<{HCM_DASHBOARD}|Open HCM Monitor>" + (f"  ·  last scan {scan_time}" if scan_time else "")]
    return "\n".join(lines)


@app.command("/hcm-status")
def handle_hcm_status(ack, respond):
    ack()
    try:
        respond(build_hcm_status())
    except Exception as e:  # noqa: BLE001
        respond(f":x: Error: {e}")


if __name__ == "__main__":
    print(f"GPU Slack Bot starting (Socket Mode) at {datetime.now(timezone.utc).isoformat()}")
    SocketModeHandler(app, SLACK["app_token"]).start()
