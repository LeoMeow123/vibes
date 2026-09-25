#!/usr/bin/env python3
"""GPU Dashboard bridge — copies the GitHub Gist snapshots into Supabase.

Phase-1 ingest. The agents on every machine keep pushing to the Gist exactly as
before; ONE instance of this bridge (on any machine that has the lab Gist config)
polls the Gist and writes to Supabase:

    gpu_machines       upsert label / hostname / type / last_seen
    gpu_latest         upsert the full snapshot (drives the live cards)
    gpu_samples        one row per GPU, at most every --sample-gap seconds (history)
    gpu_host_samples   CPU / RAM per machine, same cadence

and periodically calls gpu_rollup_hourly() and gpu_prune(keep_days).

Config
    ~/.config/gpu-dashboard/config.json     gist_id, github_token   (the existing agent config)
    ~/.config/gpu-dashboard/supabase.json   {"url": "https://xxxx.supabase.co",
                                             "service_role_key": "...",
                                             "keep_days": 14}
    env overrides: GPU_DASH_SUPABASE_URL, GPU_DASH_SUPABASE_SERVICE_KEY, GPU_DASH_KEEP_DAYS

Usage
    gpu-bridge                  # loop forever (default every 30 s)
    gpu-bridge --once           # one pass, then exit
    gpu-bridge --dry-run        # read the Gist, print what would be written, write nothing
    gpu-bridge --status         # show what Supabase currently holds
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
import time
from pathlib import Path

try:
    import requests
except ImportError:
    print("ERROR: requests required. Install with: pip install requests")
    sys.exit(1)

CONFIG_DIR = Path.home() / ".config" / "gpu-dashboard"
GIST_CONFIG_PATH = CONFIG_DIR / "config.json"
SUPA_CONFIG_PATH = CONFIG_DIR / "supabase.json"

GIST_FILE_RE = re.compile(r"^gpu-status-(.+)\.json$")


# ── Config ────────────────────────────────────────────────────────────────────


def load_gist_config() -> dict:
    cfg = {}
    if GIST_CONFIG_PATH.exists():
        with open(GIST_CONFIG_PATH) as f:
            cfg = json.load(f)
    gist_id = os.environ.get("GPU_DASH_GIST_ID", cfg.get("gist_id", ""))
    token = os.environ.get("GPU_DASH_GITHUB_TOKEN", cfg.get("github_token", ""))
    if not gist_id or not token:
        print(f"ERROR: gist_id / github_token missing. Expected in {GIST_CONFIG_PATH}")
        sys.exit(1)
    return {"gist_id": gist_id, "github_token": token}


def load_supabase_config(required: bool = True) -> dict | None:
    cfg = {}
    if SUPA_CONFIG_PATH.exists():
        with open(SUPA_CONFIG_PATH) as f:
            cfg = json.load(f)
    url = os.environ.get("GPU_DASH_SUPABASE_URL", cfg.get("url", "")).rstrip("/")
    key = os.environ.get("GPU_DASH_SUPABASE_SERVICE_KEY", cfg.get("service_role_key", ""))
    keep_days = int(os.environ.get("GPU_DASH_KEEP_DAYS", cfg.get("keep_days", 14)))
    if not url or not key:
        if required:
            print(f"ERROR: Supabase url / service_role_key missing. Expected in {SUPA_CONFIG_PATH}")
            print('  {"url": "https://xxxx.supabase.co", "service_role_key": "...", "keep_days": 14}')
            sys.exit(1)
        return None
    problem = describe_key_problem(key)
    if problem:
        print(f"ERROR: {problem}")
        print("  The bridge needs a key that bypasses row-level security:")
        print("  Supabase -> Project Settings -> API Keys -> the 'secret' key (sb_secret_...),")
        print("  or, on the Legacy tab, the 'service_role' key. Never the publishable / anon key.")
        print(f"  Fix it in {SUPA_CONFIG_PATH} or re-run bridge/install.sh and answer 'n' to reuse.")
        sys.exit(1)
    return {"url": url, "key": key, "keep_days": keep_days}


def describe_key_problem(key: str) -> str | None:
    """Return a message if this is not a server-side key, else None."""
    if key.startswith("sb_publishable_"):
        return "the configured key is the PUBLISHABLE (public) key, which only gets the anonymous role."
    if key.startswith("sb_secret_"):
        return None
    if key.startswith("eyJ"):
        try:
            import base64
            payload = key.split(".")[1]
            payload += "=" * (-len(payload) % 4)
            role = json.loads(base64.urlsafe_b64decode(payload)).get("role")
        except Exception:  # noqa: BLE001
            return None  # unreadable JWT: let the server decide
        if role != "service_role":
            return f"the configured key is a legacy '{role}' key, not the service_role key."
        return None
    return None  # unknown format: let the server decide


# ── Gist ──────────────────────────────────────────────────────────────────────


class RateLimited(Exception):
    def __init__(self, retry_after: int):
        super().__init__(f"rate limited, retry after {retry_after}s")
        self.retry_after = retry_after


def fetch_gist(cfg: dict) -> dict:
    resp = requests.get(
        f"https://api.github.com/gists/{cfg['gist_id']}",
        headers={
            "Authorization": f"token {cfg['github_token']}",
            "Accept": "application/vnd.github.v3+json",
        },
        timeout=20,
    )
    if resp.status_code in (403, 429):
        raise RateLimited(int(resp.headers.get("Retry-After", 60) or 60))
    resp.raise_for_status()
    return resp.json()


def machine_key_from_filename(filename: str) -> str | None:
    m = GIST_FILE_RE.match(filename)
    if not m:
        return None
    key = re.sub(r"[^a-z0-9_-]+", "-", m.group(1).lower()).strip("-")
    return key or None


def parse_snapshots(gist: dict) -> dict[str, dict]:
    """Return {machine_key: snapshot} for every parseable gpu-status-*.json file."""
    out: dict[str, dict] = {}
    for filename, f in (gist.get("files") or {}).items():
        key = machine_key_from_filename(filename)
        if not key:
            continue
        try:
            snap = json.loads(f.get("content") or "")
        except json.JSONDecodeError:
            _log(f"  skip {filename}: not JSON")
            continue
        if not isinstance(snap, dict) or "timestamp" not in snap or "machine" not in snap:
            _log(f"  skip {filename}: not a snapshot")
            continue
        out[key] = snap
    return out


# ── Row builders ──────────────────────────────────────────────────────────────


def _num(v):
    return v if isinstance(v, (int, float)) and not isinstance(v, bool) else None


def machine_row(key: str, snap: dict) -> dict:
    m = snap.get("machine") or {}
    return {
        "key": key,
        "label": m.get("label") or m.get("hostname") or key,
        "hostname": m.get("hostname"),
        "type": (m.get("type") or "workstation").lower(),
        "last_seen": snap["timestamp"],
    }


def latest_row(key: str, snap: dict) -> dict:
    return {"machine_key": key, "ts": snap["timestamp"], "snapshot": snap}


def sample_rows(key: str, snap: dict) -> list[dict]:
    rows = []
    for g in snap.get("gpus") or []:
        rows.append(
            {
                "machine_key": key,
                "ts": snap["timestamp"],
                "gpu_index": int(g.get("index", 0)),
                "util": _num(g.get("utilization_percent")),
                "util_peak": _num(g.get("utilization_peak_percent")),
                "mem_used_mb": _num(g.get("memory_used_mb")),
                "mem_total_mb": _num(g.get("memory_total_mb")),
                "temp_c": _num(g.get("temperature_c")),
                "power_w": _num(g.get("power_draw_w")),
                "n_procs": len(g.get("processes") or []),
            }
        )
    return rows


def host_row(key: str, snap: dict) -> dict:
    cpu = snap.get("cpu") or {}
    ram = snap.get("ram") or {}
    return {
        "machine_key": key,
        "ts": snap["timestamp"],
        "cpu_percent": _num(cpu.get("percent")),
        "ram_used_gb": _num(ram.get("used_gb")),
        "ram_total_gb": _num(ram.get("total_gb")),
        "ram_percent": _num(ram.get("percent")),
    }


# ── Supabase (PostgREST over plain HTTPS; no SDK needed) ──────────────────────


class Supa:
    def __init__(self, cfg: dict):
        self.url = cfg["url"]
        self.key = cfg["key"]
        self.keep_days = cfg["keep_days"]

    def _headers(self, prefer: str | None = None) -> dict:
        # Legacy keys are JWTs and go in both headers. New-style sb_secret_ keys go in
        # `apikey` only; the API gateway derives the role from it when Authorization is absent.
        h = {"apikey": self.key, "Content-Type": "application/json"}
        if self.key.startswith("eyJ"):
            h["Authorization"] = f"Bearer {self.key}"
        if prefer:
            h["Prefer"] = prefer
        return h

    def _req(self, method: str, path: str, *, params=None, payload=None, prefer=None):
        resp = requests.request(
            method,
            f"{self.url}/rest/v1/{path}",
            headers=self._headers(prefer),
            params=params,
            data=json.dumps(payload, separators=(",", ":")) if payload is not None else None,
            timeout=30,
        )
        if resp.status_code >= 300:
            raise RuntimeError(f"{method} {path} -> {resp.status_code} {resp.text[:300]}")
        return resp

    def upsert(self, table: str, rows: list[dict], on_conflict: str, ignore_dupes: bool = False):
        if not rows:
            return
        res = "ignore-duplicates" if ignore_dupes else "merge-duplicates"
        self._req(
            "POST",
            table,
            params={"on_conflict": on_conflict},
            payload=rows,
            prefer=f"resolution={res},return=minimal",
        )

    def rpc(self, fn: str, args: dict | None = None):
        resp = self._req("POST", f"rpc/{fn}", payload=args or {})
        try:
            return resp.json()
        except ValueError:
            return None

    def select(self, table: str, params: dict):
        return self._req("GET", table, params=params).json()

    def count(self, table: str) -> int:
        resp = requests.get(
            f"{self.url}/rest/v1/{table}",
            headers={**self._headers("count=exact"), "Range-Unit": "items", "Range": "0-0"},
            params={"select": "machine_key"},
            timeout=30,
        )
        cr = resp.headers.get("Content-Range", "*/0")
        try:
            return int(cr.split("/")[-1])
        except ValueError:
            return -1


# ── Bridge loop ───────────────────────────────────────────────────────────────


class Bridge:
    def __init__(self, gist_cfg: dict, supa: Supa | None, sample_gap: int, dry_run: bool):
        self.gist_cfg = gist_cfg
        self.supa = supa
        self.sample_gap = sample_gap
        self.dry_run = dry_run
        self.last_ts: dict[str, str] = {}          # machine_key -> last snapshot ts written to gpu_latest
        self.last_sample_ts: dict[str, float] = {}  # machine_key -> epoch of last stored sample
        self.last_rollup = 0.0
        self.last_prune = 0.0

    def pass_once(self) -> None:
        gist = fetch_gist(self.gist_cfg)
        snaps = parse_snapshots(gist)
        if not snaps:
            _log("no snapshots in Gist")
            return

        machines, latest, samples, hosts = [], [], [], []
        summary = []
        for key, snap in sorted(snaps.items()):
            ts = snap["timestamp"]
            changed = self.last_ts.get(key) != ts
            ts_epoch = _iso_to_epoch(ts)
            due = changed and (ts_epoch - self.last_sample_ts.get(key, 0.0)) >= self.sample_gap

            machines.append(machine_row(key, snap))
            if changed:
                latest.append(latest_row(key, snap))
            if due:
                samples.extend(sample_rows(key, snap))
                hosts.append(host_row(key, snap))

            n_gpus = len(snap.get("gpus") or [])
            age_min = int((time.time() - ts_epoch) / 60) if ts_epoch else -1
            summary.append(f"{key}({n_gpus}gpu,{age_min}m{'*' if changed else ''}{'+' if due else ''})")

        if self.dry_run:
            _log("DRY RUN — would write:")
            _log(f"  gpu_machines     upsert {len(machines)} rows")
            _log(f"  gpu_latest       upsert {len(latest)} rows")
            _log(f"  gpu_samples      insert {len(samples)} rows")
            _log(f"  gpu_host_samples insert {len(hosts)} rows")
            if samples:
                _log("  first sample row: " + json.dumps(samples[0]))
            if hosts:
                _log("  first host row:   " + json.dumps(hosts[0]))
        else:
            assert self.supa is not None
            self.supa.upsert("gpu_machines", machines, on_conflict="key")
            self.supa.upsert("gpu_latest", latest, on_conflict="machine_key")
            self.supa.upsert("gpu_samples", samples, on_conflict="machine_key,gpu_index,ts", ignore_dupes=True)
            self.supa.upsert("gpu_host_samples", hosts, on_conflict="machine_key,ts", ignore_dupes=True)

        # Only remember what we actually wrote (or would have).
        for key, snap in snaps.items():
            self.last_ts[key] = snap["timestamp"]
        for row in hosts:
            self.last_sample_ts[row["machine_key"]] = _iso_to_epoch(row["ts"])

        _log(f"[OK] {len(snaps)} machines, {len(latest)} updated, {len(samples)} gpu samples  " + " ".join(summary))
        self.maintenance()

    def maintenance(self) -> None:
        now = time.monotonic()
        if self.dry_run or self.supa is None:
            return
        if now - self.last_rollup >= 3600:
            try:
                n = self.supa.rpc("gpu_rollup_hourly")
                _log(f"[rollup] hourly rows written: {n}")
            except Exception as e:  # noqa: BLE001
                _log(f"[rollup] failed: {e}")
            self.last_rollup = now
        if now - self.last_prune >= 6 * 3600:
            try:
                n = self.supa.rpc("gpu_prune", {"p_keep_days": self.supa.keep_days})
                _log(f"[prune] raw rows deleted (> {self.supa.keep_days}d): {n}")
            except Exception as e:  # noqa: BLE001
                _log(f"[prune] failed: {e}")
            self.last_prune = now


def _iso_to_epoch(ts: str) -> float:
    try:
        return dt.datetime.fromisoformat(ts.replace("Z", "+00:00")).timestamp()
    except (ValueError, AttributeError):
        return 0.0


def _log(msg: str) -> None:
    print(f"[{dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}", flush=True)


# ── Status ────────────────────────────────────────────────────────────────────


def print_status(supa: Supa) -> None:
    machines = supa.select(
        "gpu_machines",
        {"select": "key,label,display_name,type,hidden,last_seen,first_seen", "order": "last_seen.desc"},
    )
    now = dt.datetime.now(dt.timezone.utc)
    print(f"Supabase: {supa.url}")
    print(f"machines: {len(machines)}")
    for m in machines:
        age = "?"
        if m.get("last_seen"):
            age = f"{int((now - dt.datetime.fromisoformat(m['last_seen'].replace('Z', '+00:00'))).total_seconds() / 60)}m"
        name = m.get("display_name") or m["label"]
        print(f"  {m['key']:28s} {name:28s} {m['type']:11s} last {age:>6s}{'  (hidden)' if m.get('hidden') else ''}")
    print(f"gpu_samples rows:        {supa.count('gpu_samples')}")
    print(f"gpu_host_samples rows:   {supa.count('gpu_host_samples')}")
    print(f"gpu_samples_hourly rows: {supa.count('gpu_samples_hourly')}")


# ── Main ──────────────────────────────────────────────────────────────────────


def main() -> None:
    p = argparse.ArgumentParser(description="GPU Dashboard bridge: Gist -> Supabase")
    p.add_argument("--once", action="store_true", help="one pass, then exit")
    p.add_argument("--dry-run", action="store_true", help="read the Gist, write nothing")
    p.add_argument("--status", action="store_true", help="print what Supabase holds and exit")
    p.add_argument("--interval", type=int, default=30, help="seconds between Gist polls (default 30)")
    p.add_argument("--sample-gap", type=int, default=55, help="min seconds between stored history samples per machine (default 55)")
    args = p.parse_args()

    if args.status:
        supa = Supa(load_supabase_config(required=True))
        print_status(supa)
        return

    gist_cfg = load_gist_config()
    supa_cfg = load_supabase_config(required=not args.dry_run)
    supa = Supa(supa_cfg) if supa_cfg else None

    _log("GPU bridge starting")
    _log(f"  Gist: {gist_cfg['gist_id'][:8]}...  interval {args.interval}s  sample gap {args.sample_gap}s")
    if supa:
        _log(f"  Supabase: {supa.url}  keep raw {supa.keep_days}d")
    if args.dry_run:
        _log("  DRY RUN: nothing will be written")

    bridge = Bridge(gist_cfg, supa, args.sample_gap, args.dry_run)
    backoff = 0
    while True:
        try:
            bridge.pass_once()
            backoff = 0
        except RateLimited as e:
            backoff = min(max(e.retry_after, 60), 600)
            _log(f"GitHub rate limited; backing off {backoff}s")
        except Exception as e:  # noqa: BLE001
            backoff = min(backoff * 2 if backoff else 30, 300)
            _log(f"Error: {e} (backoff {backoff}s)")
        if args.once or args.dry_run:
            break
        time.sleep(args.interval + backoff)


if __name__ == "__main__":
    main()
