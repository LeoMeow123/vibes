#!/usr/bin/env python3
"""Compact GPU status for Slack — one builder shared by the bot, the daily report, and cron.

Design: lead with the one number people want (free GPUs), one line per machine, a
"Problems" block only when something is wrong, and who is using what in one line.
No per-process dumps, no CPU/RAM unless abnormal, no inference (that lives in the
HCM Monitor, linked in the footer).

Data source: Supabase (gpu_machines + gpu_latest, the same data the dashboard shows,
including renames and hidden machines) when ~/.config/gpu-dashboard/supabase.json
exists; otherwise the GitHub Gist. Standard library only, so it runs in any Python.

Config
    ~/.config/gpu-dashboard/slack.json     {"webhook": "...", "bot_token": "...", "app_token": "..."}
    ~/.config/gpu-dashboard/supabase.json  {"url": "...", "service_role_key": "..."}   (optional)
    ~/.config/gpu-dashboard/config.json    {"gist_id": "...", "github_token": "..."}   (fallback)

Usage
    slack_report.py --dry            # print the text rendering
    slack_report.py --post           # post the status to the webhook
    slack_report.py --daily --post   # status + yesterday's utilization digest (needs Supabase)
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

CONFIG_DIR = Path.home() / ".config" / "gpu-dashboard"
DASHBOARD_URL = "https://leomeow123.github.io/vibes/gpu-dashboard/"
HCM_URL = "https://leomeow123.github.io/hcm-dashboard/#inference-panel"

# Same thresholds as index.html
BUSY_UTIL = 10          # util at/above this counts as in use
BUSY_MEM_MB = 2048      # processes holding this much VRAM count as in use even at 0% (idle kernel with a model loaded)
                        # below it with 0% util is desktop use (remote desktop, file manager) and the GPU is free
RECENT_PEAK = 30        # idle now, but peaked above this in the agent's 30-min window: not free
GLITCH_UTIL = 90        # util this high with ~no memory and no process = driver reporting glitch
GLITCH_MEM_MB = 64
STALE_SECONDS = 600     # no report for 10 min = offline
HOT_C = 88              # RTX PRO 6000 Blackwell runs 80-86 °C under load; flag only above that
VRAM_FULL_PCT = 95

SQUARE = {"free": ":large_green_square:", "busy": ":large_blue_square:", "recent": ":large_yellow_square:", "offline": ":black_large_square:"}
PLAIN = {"free": "F", "busy": "B", "recent": "r", "offline": "x"}


# ── Config ────────────────────────────────────────────────────────────────────


def load_json(path: Path) -> dict:
    try:
        with open(path) as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return {}


def slack_config() -> dict:
    cfg = load_json(CONFIG_DIR / "slack.json")
    if not cfg.get("webhook") and not cfg.get("bot_token"):
        sys.exit(f"ERROR: {CONFIG_DIR / 'slack.json'} missing or empty "
                 '(expected {"webhook": "...", "bot_token": "...", "app_token": "..."})')
    return cfg


# ── HTTP (stdlib) ─────────────────────────────────────────────────────────────


def http_json(url: str, headers: dict | None = None, data: dict | list | None = None, method: str | None = None, timeout: int = 20):
    body = json.dumps(data).encode() if data is not None else None
    req = urllib.request.Request(url, data=body, method=method or ("POST" if body is not None else "GET"))
    for k, v in (headers or {}).items():
        req.add_header(k, v)
    if body is not None:
        req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read()
    return json.loads(raw) if raw else None


# ── Data sources ──────────────────────────────────────────────────────────────


def _supa_headers(cfg: dict) -> dict:
    key = cfg["service_role_key"]
    h = {"apikey": key}
    if key.startswith("eyJ"):
        h["Authorization"] = f"Bearer {key}"
    return h


def machines_from_supabase(cfg: dict, include_hidden: bool = False) -> list[dict]:
    url = cfg["url"].rstrip("/")
    h = _supa_headers(cfg)
    meta = http_json(f"{url}/rest/v1/gpu_machines?select=key,label,display_name,type,hidden", headers=h)
    latest = http_json(f"{url}/rest/v1/gpu_latest?select=machine_key,ts,snapshot", headers=h)
    by_key = {m["key"]: m for m in meta}
    out = []
    for row in latest:
        m = by_key.get(row["machine_key"])
        if not m or (m.get("hidden") and not include_hidden):
            continue
        snap = row["snapshot"]
        out.append({
            "key": m["key"],
            "label": m.get("display_name") or m.get("label") or snap.get("machine", {}).get("label") or m["key"],
            "type": (m.get("type") or "workstation").lower(),
            "hidden": bool(m.get("hidden")),
            "ts": row["ts"],
            "snapshot": snap,
        })
    return out


def machines_from_gist(gist_id: str, token: str | None) -> list[dict]:
    h = {"Accept": "application/vnd.github.v3+json"}
    if token:
        h["Authorization"] = f"token {token}"
    gist = http_json(f"https://api.github.com/gists/{gist_id}", headers=h)
    out = []
    for fname, f in (gist.get("files") or {}).items():
        if not fname.startswith("gpu-status-"):
            continue
        try:
            snap = json.loads(f.get("content") or "")
        except json.JSONDecodeError:
            continue
        if not isinstance(snap, dict) or "timestamp" not in snap:
            continue
        label = snap.get("machine", {}).get("label") or snap.get("machine", {}).get("hostname") or fname
        out.append({"key": fname, "label": label, "type": (snap.get("machine", {}).get("type") or "workstation").lower(),
                    "hidden": False, "ts": snap["timestamp"], "snapshot": snap})
    return out


def load_machines() -> tuple[list[dict], str]:
    """Return (machines, source). Supabase if configured, else the lab Gist."""
    supa = load_json(CONFIG_DIR / "supabase.json")
    if supa.get("url") and supa.get("service_role_key"):
        try:
            return machines_from_supabase(supa), "supabase"
        except (urllib.error.URLError, KeyError, TypeError) as e:
            print(f"supabase read failed ({e}); falling back to gist", file=sys.stderr)
    gist = load_json(CONFIG_DIR / "config.json")
    if not gist.get("gist_id"):
        sys.exit("ERROR: neither supabase.json nor config.json (gist) is configured")
    return machines_from_gist(gist["gist_id"], gist.get("github_token")), "gist"


# ── State logic (mirrors index.html) ──────────────────────────────────────────


def age_seconds(ts: str) -> float:
    try:
        t = dt.datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return float("inf")
    return (dt.datetime.now(dt.timezone.utc) - t).total_seconds()


def proc_mem_mb(g: dict) -> int:
    return sum(int(p.get("gpu_memory_mb") or 0) for p in (g.get("processes") or []))


def gpu_state(g: dict, stale: bool) -> str:
    if stale:
        return "offline"
    util = g.get("utilization_percent") or 0
    peak = g.get("utilization_peak_percent")
    if util >= BUSY_UTIL or proc_mem_mb(g) >= BUSY_MEM_MB:
        return "busy"
    if (peak if peak is not None else util) >= RECENT_PEAK:
        return "recent"
    return "free"


def is_glitch(g: dict) -> bool:
    return not (g.get("processes") or []) and (g.get("utilization_percent") or 0) >= GLITCH_UTIL and (g.get("memory_used_mb") or 0) < GLITCH_MEM_MB


def human_age(seconds: float) -> str:
    if seconds == float("inf"):
        return "never"
    m = int(seconds // 60)
    if m < 1:
        return "just now"
    if m < 60:
        return f"{m} min ago"
    h = m // 60
    if h < 48:
        return f"{h} h ago"
    return f"{h // 24} d ago"


def analyse(machines: list[dict]) -> dict:
    """Per-machine rows + fleet totals + problems + users."""
    rows, problems = [], []
    users: dict[str, int] = {}
    tot = {"free": 0, "busy": 0, "recent": 0, "offline": 0, "gpus": 0, "online": 0, "machines": 0}
    newest = float("inf")

    for m in sorted(machines, key=lambda x: x["label"].lower()):
        snap = m["snapshot"]
        age = age_seconds(m["ts"])
        newest = min(newest, age)
        stale = age > STALE_SECONDS
        gpus = sorted(snap.get("gpus") or [], key=lambda g: g.get("index", 0))
        states = [gpu_state(g, stale) for g in gpus]
        counts = {s: states.count(s) for s in ("free", "busy", "recent", "offline")}
        live_utils = [g.get("utilization_percent") or 0 for g in gpus] if not stale else []
        avg_util = round(sum(live_utils) / len(live_utils)) if live_utils else None
        m_users: dict[str, int] = {}
        for g, st in zip(gpus, states):
            if st != "busy":          # desktop-only or offline processes are not "using" the GPU
                continue
            seen = set()
            for p in g.get("processes") or []:
                u = p.get("user") or "?"
                u = "unknown" if u == "?" else u
                if u in seen:
                    continue
                seen.add(u)
                m_users[u] = m_users.get(u, 0) + 1
                users[u] = users.get(u, 0) + 1
        for g in gpus:
            if stale:
                continue
            if is_glitch(g):
                problems.append(f"*{m['label']}* GPU {g.get('index')}: {g.get('utilization_percent')}% util with {g.get('memory_used_mb') or 0} MB in use and no process, likely a driver reporting glitch")
            t = g.get("temperature_c")
            if t is not None and t >= HOT_C:
                problems.append(f"*{m['label']}* GPU {g.get('index')}: {t} °C")
            mt = g.get("memory_total_mb") or 0
            if mt and (g.get("memory_used_mb") or 0) / mt * 100 >= VRAM_FULL_PCT:
                problems.append(f"*{m['label']}* GPU {g.get('index')}: VRAM {round((g.get('memory_used_mb') or 0) / 1024)} / {round(mt / 1024)} GB, nearly full")
        if stale:
            problems.append(f"*{m['label']}*: offline, last report {human_age(age)}")

        rows.append({"label": m["label"], "type": m["type"], "stale": stale, "age": age, "gpus": len(gpus), "states": states,
                     "counts": counts, "avg_util": avg_util, "users": m_users})
        tot["machines"] += 1
        tot["online"] += 0 if stale else 1
        tot["gpus"] += len(gpus)
        for s in ("free", "busy", "recent", "offline"):
            tot[s] += counts[s]

    # machines with free GPUs first, then by name
    rows.sort(key=lambda r: (r["stale"], -r["counts"]["free"], r["label"].lower()))
    return {"rows": rows, "totals": tot, "problems": problems, "users": users, "newest_age": newest}


# ── Rendering ─────────────────────────────────────────────────────────────────


def headline(a: dict) -> tuple[str, str]:
    t = a["totals"]
    if t["machines"] == 0:
        return ":white_circle:", "No machines are reporting"
    if t["free"] > 0:
        head = f"{t['free']} free GPU{'s' if t['free'] != 1 else ''} of {t['gpus']}"
        emoji = ":large_green_circle:"
    else:
        head = f"No free GPUs right now ({t['gpus']} total)"
        emoji = ":red_circle:"
    extras = []
    if t["recent"]:
        extras.append(f"{t['recent']} recently active")
    if t["offline"]:
        extras.append(f"{t['offline']} offline")
    if extras:
        head += " · " + ", ".join(extras)
    return emoji, head


def machine_line(r: dict, plain: bool = False) -> str:
    sq = "".join((PLAIN if plain else SQUARE)[s] for s in r["states"]) or ("—" if plain else "_no GPUs_")
    if r["stale"]:
        tail = f"offline · last report {human_age(r['age'])}"
    else:
        parts = [f"{r['counts']['free']} free" if r["counts"]["free"] else "all in use" if r["gpus"] else "no GPUs"]
        if r["avg_util"] is not None and r["gpus"]:
            parts.append(f"{r['avg_util']}% avg")
        if r["users"]:
            parts.append(", ".join(f"{u} ({n})" if n > 1 else u for u, n in sorted(r["users"].items(), key=lambda kv: -kv[1])))
        tail = " · ".join(parts)
    name = r["label"] if plain else f"*{r['label']}*"
    return f"{name}  {sq}  {tail}"


def users_line(a: dict) -> str:
    if not a["users"]:
        return "Nobody is running GPU jobs"
    return "Using GPUs: " + " · ".join(f"{u} ×{n}" if n > 1 else u for u, n in sorted(a["users"].items(), key=lambda kv: -kv[1]))


def build_blocks(a: dict, digest: str | None = None, title: str | None = None) -> tuple[list, str]:
    emoji, head = headline(a)
    updated = human_age(a["newest_age"])
    blocks = [
        {"type": "header", "text": {"type": "plain_text", "text": (f"{title} · " if title else "") + head, "emoji": True}},
        {"type": "section", "text": {"type": "mrkdwn", "text": emoji + " " + "\n".join(machine_line(r) for r in a["rows"]) if a["rows"] else "_no machines_"}},
    ]
    if a["problems"]:
        blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": ":warning: *Needs attention*\n" + "\n".join("• " + p for p in a["problems"][:8])}})
    if digest:
        blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": digest}})
    blocks.append({"type": "context", "elements": [{"type": "mrkdwn", "text":
        f"{users_line(a)}  ·  updated {updated}  ·  <{DASHBOARD_URL}|Dashboard>  ·  <{HCM_URL}|Inference progress>"}]})
    text = f"{head}\n" + "\n".join(machine_line(r, plain=True) for r in a["rows"])
    return blocks, text


def render_text(a: dict, digest: str | None = None) -> str:
    _, head = headline(a)
    lines = [head, ""]
    lines += [machine_line(r, plain=True) for r in a["rows"]]
    if a["problems"]:
        lines += ["", "Needs attention:"] + ["  - " + p.replace("*", "") for p in a["problems"]]
    if digest:
        lines += ["", digest.replace("*", "")]
    lines += ["", users_line(a) + f"  ·  updated {human_age(a['newest_age'])}", DASHBOARD_URL]
    return "\n".join(lines)


# ── Daily digest (Supabase history) ───────────────────────────────────────────


def yesterday_digest() -> str | None:
    supa = load_json(CONFIG_DIR / "supabase.json")
    if not supa.get("url"):
        return None
    now = dt.datetime.now(dt.timezone.utc)
    try:
        rows = http_json(f"{supa['url'].rstrip('/')}/rest/v1/rpc/gpu_fleet_history", headers=_supa_headers(supa),
                         data={"p_from": (now - dt.timedelta(hours=24)).isoformat(), "p_to": now.isoformat(), "p_bucket_seconds": 3600})
        meta = http_json(f"{supa['url'].rstrip('/')}/rest/v1/gpu_machines?select=key,label,display_name,hidden", headers=_supa_headers(supa))
    except (urllib.error.URLError, KeyError) as e:
        print(f"digest failed: {e}", file=sys.stderr)
        return None
    names = {m["key"]: (m.get("display_name") or m.get("label") or m["key"]) for m in meta if not m.get("hidden")}
    per: dict[str, list] = {}
    for r in rows or []:
        if r["machine_key"] in names and r.get("util") is not None:
            per.setdefault(r["machine_key"], []).append(float(r["util"]))
    if not per:
        return None
    avg = {k: sum(v) / len(v) for k, v in per.items()}
    fleet = sum(avg.values()) / len(avg)
    busiest = max(avg, key=avg.get)
    idlest = min(avg, key=avg.get)
    parts = [f"*Last 24 h:* fleet averaged {fleet:.0f}% GPU utilization",
             f"busiest {names[busiest]} ({avg[busiest]:.0f}%)"]
    if idlest != busiest:
        parts.append(f"quietest {names[idlest]} ({avg[idlest]:.0f}%)")
    return " · ".join(parts)


# ── Posting ───────────────────────────────────────────────────────────────────


def post_webhook(webhook: str, blocks: list, text: str) -> None:
    http_json(webhook, data={"text": text, "blocks": blocks})


def main() -> None:
    p = argparse.ArgumentParser(description="Compact GPU status for Slack")
    p.add_argument("--dry", action="store_true", help="print the text rendering, post nothing")
    p.add_argument("--post", action="store_true", help="post to the webhook in slack.json")
    p.add_argument("--daily", action="store_true", help="include the last-24h utilization digest (Supabase)")
    p.add_argument("--json", action="store_true", help="print the Block Kit JSON")
    args = p.parse_args()

    machines, source = load_machines()
    a = analyse(machines)
    digest = yesterday_digest() if args.daily else None
    title = dt.datetime.now().strftime("%a %b %d") if args.daily else None
    blocks, text = build_blocks(a, digest, title)

    if args.json:
        print(json.dumps(blocks, indent=2))
    if args.dry or not (args.post or args.json):
        print(f"[source: {source}]")
        print(render_text(a, digest))
    if args.post:
        post_webhook(slack_config()["webhook"], blocks, text)
        print("posted to Slack")


if __name__ == "__main__":
    main()
