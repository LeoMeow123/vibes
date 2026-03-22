#!/usr/bin/env python3
"""GPU Dashboard Agent — collects GPU/CPU/RAM stats and pushes to a GitHub Gist.

Run on each machine you want to monitor. Requires: psutil, requests.

Usage:
    # Run continuously (default 30s interval)
    python gpu_agent.py

    # Single snapshot (for cron)
    python gpu_agent.py --once

    # Custom interval
    python gpu_agent.py --interval 60

Configuration (pick one):
    1. Config file: ~/.config/gpu-dashboard/config.json
    2. Environment variables: GPU_DASH_GIST_ID, GPU_DASH_GITHUB_TOKEN, GPU_DASH_LABEL
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import platform
import shutil
import subprocess
import sys
import time
from pathlib import Path

try:
    import psutil
except ImportError:
    print("ERROR: psutil required. Install with: pip install psutil")
    sys.exit(1)

try:
    import requests
except ImportError:
    print("ERROR: requests required. Install with: pip install requests")
    sys.exit(1)

# ── Config ────────────────────────────────────────────────────────────────────

CONFIG_PATH = Path.home() / ".config" / "gpu-dashboard" / "config.json"


def load_config() -> dict:
    """Load config from file or environment variables."""
    cfg = {}
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            cfg = json.load(f)

    # Environment overrides
    cfg["gist_id"] = os.environ.get("GPU_DASH_GIST_ID", cfg.get("gist_id", ""))
    cfg["github_token"] = os.environ.get(
        "GPU_DASH_GITHUB_TOKEN", cfg.get("github_token", "")
    )
    cfg["machine_label"] = os.environ.get(
        "GPU_DASH_LABEL", cfg.get("machine_label", platform.node())
    )
    cfg["machine_type"] = os.environ.get(
        "GPU_DASH_TYPE", cfg.get("machine_type", "workstation")
    )
    cfg.setdefault("interval_seconds", 30)

    if not cfg["gist_id"]:
        print("ERROR: No gist_id configured.")
        print(f"  Set GPU_DASH_GIST_ID env var or add to {CONFIG_PATH}")
        sys.exit(1)
    if not cfg["github_token"]:
        print("ERROR: No github_token configured.")
        print(f"  Set GPU_DASH_GITHUB_TOKEN env var or add to {CONFIG_PATH}")
        sys.exit(1)

    return cfg


# ── GPU data collection ───────────────────────────────────────────────────────

NVIDIA_SMI = shutil.which("nvidia-smi")


def _run_smi(query: str) -> list[str]:
    """Run nvidia-smi with a query and return lines."""
    if not NVIDIA_SMI:
        return []
    try:
        result = subprocess.run(
            [
                NVIDIA_SMI,
                f"--query-gpu={query}",
                "--format=csv,noheader,nounits",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            return []
        return [line.strip() for line in result.stdout.strip().split("\n") if line.strip()]
    except Exception:
        return []


def collect_gpus() -> list[dict]:
    """Collect GPU info via nvidia-smi."""
    lines = _run_smi(
        "index,name,utilization.gpu,memory.used,memory.total,temperature.gpu,power.draw,power.limit"
    )
    gpus = []
    for line in lines:
        parts = [p.strip() for p in line.split(",")]
        if len(parts) < 6:
            continue
        try:
            gpu = {
                "index": int(parts[0]),
                "name": parts[1],
                "utilization_percent": int(parts[2]) if parts[2] not in ("[N/A]", "") else 0,
                "memory_used_mb": int(parts[3]) if parts[3] not in ("[N/A]", "") else 0,
                "memory_total_mb": int(parts[4]) if parts[4] not in ("[N/A]", "") else 0,
                "temperature_c": int(parts[5]) if parts[5] not in ("[N/A]", "") else None,
                "power_draw_w": _safe_float(parts[6]) if len(parts) > 6 else None,
                "power_limit_w": _safe_float(parts[7]) if len(parts) > 7 else None,
                "processes": [],
            }
            gpus.append(gpu)
        except (ValueError, IndexError):
            continue
    return gpus


def _safe_float(val: str) -> float | None:
    try:
        v = float(val)
        return round(v, 1)
    except (ValueError, TypeError):
        return None


def collect_gpu_processes() -> list[dict]:
    """Collect per-GPU process info."""
    if not NVIDIA_SMI:
        return []
    try:
        result = subprocess.run(
            [
                NVIDIA_SMI,
                "--query-compute-apps=gpu_uuid,pid,used_gpu_memory",
                "--format=csv,noheader,nounits",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            return []
    except Exception:
        return []

    # Map GPU UUID to index
    uuid_lines = _run_smi("index,uuid")
    uuid_to_idx = {}
    for line in uuid_lines:
        parts = [p.strip() for p in line.split(",")]
        if len(parts) >= 2:
            uuid_to_idx[parts[1]] = int(parts[0])

    processes = []
    for line in result.stdout.strip().split("\n"):
        if not line.strip():
            continue
        parts = [p.strip() for p in line.split(",")]
        if len(parts) < 3:
            continue
        try:
            pid = int(parts[1])
            proc_info = {
                "gpu_index": uuid_to_idx.get(parts[0], -1),
                "pid": pid,
                "gpu_memory_mb": int(parts[2]) if parts[2] not in ("[N/A]", "") else 0,
            }
            # Enrich with psutil
            try:
                p = psutil.Process(pid)
                cmdline = p.cmdline()
                proc_info["user"] = p.username()
                proc_info["command"] = _format_command(cmdline)
                proc_info["cpu_percent"] = round(p.cpu_percent(interval=0), 1)
                proc_info["ram_mb"] = round(p.memory_info().rss / 1024 / 1024, 0)
                create_time = dt.datetime.fromtimestamp(
                    p.create_time(), tz=dt.timezone.utc
                )
                proc_info["started"] = create_time.isoformat()
                elapsed = time.time() - p.create_time()
                proc_info["runtime_human"] = _format_duration(elapsed)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                proc_info["user"] = "?"
                proc_info["command"] = "?"
                proc_info["runtime_human"] = "?"
            processes.append(proc_info)
        except (ValueError, IndexError):
            continue
    return processes


def _format_command(cmdline: list[str]) -> str:
    """Format command line to a readable short string."""
    if not cmdline:
        return "?"
    # If it's a python script, show "python script.py args..."
    cmd = " ".join(cmdline)
    # Truncate to reasonable length
    if len(cmd) > 120:
        cmd = cmd[:117] + "..."
    return cmd


def _format_duration(seconds: float) -> str:
    """Format seconds to human-readable duration."""
    s = int(seconds)
    if s < 60:
        return f"{s}s"
    if s < 3600:
        return f"{s // 60}m {s % 60}s"
    h = s // 3600
    m = (s % 3600) // 60
    if h < 24:
        return f"{h}h {m}m"
    d = h // 24
    h = h % 24
    return f"{d}d {h}h"


# ── System data collection ────────────────────────────────────────────────────


def collect_system() -> dict:
    """Collect CPU, RAM, and uptime."""
    mem = psutil.virtual_memory()
    return {
        "hostname": platform.node(),
        "uptime_seconds": int(time.time() - psutil.boot_time()),
        "cpu": {
            "percent": psutil.cpu_percent(interval=0),
            "cores_physical": psutil.cpu_count(logical=False) or 0,
            "cores_logical": psutil.cpu_count(logical=True) or 0,
        },
        "ram": {
            "used_gb": round(mem.used / 1024**3, 1),
            "total_gb": round(mem.total / 1024**3, 1),
            "percent": mem.percent,
        },
    }


# ── Assemble snapshot ─────────────────────────────────────────────────────────


def collect_snapshot(cfg: dict) -> dict:
    """Collect full machine snapshot."""
    gpus = collect_gpus()
    processes = collect_gpu_processes()

    # Attach processes to their GPUs
    for proc in processes:
        idx = proc.get("gpu_index", -1)
        for gpu in gpus:
            if gpu["index"] == idx:
                gpu["processes"].append(proc)
                break

    system = collect_system()

    return {
        "machine": {
            "hostname": system["hostname"],
            "label": cfg["machine_label"],
            "type": cfg["machine_type"],
        },
        "timestamp": dt.datetime.now(dt.timezone.utc).isoformat(),
        "uptime_seconds": system["uptime_seconds"],
        "cpu": system["cpu"],
        "ram": system["ram"],
        "gpus": gpus,
    }


# ── Push to Gist ──────────────────────────────────────────────────────────────


def push_to_gist(cfg: dict, snapshot: dict) -> bool:
    """Update the machine's file in the shared Gist."""
    hostname = snapshot["machine"]["hostname"]
    # Sanitize hostname for filename
    safe_name = "".join(c if c.isalnum() or c in "-_" else "-" for c in hostname)
    filename = f"gpu-status-{safe_name}.json"

    content = json.dumps(snapshot, indent=2)

    try:
        resp = requests.patch(
            f"https://api.github.com/gists/{cfg['gist_id']}",
            headers={
                "Authorization": f"token {cfg['github_token']}",
                "Accept": "application/vnd.github.v3+json",
            },
            json={"files": {filename: {"content": content}}},
            timeout=15,
        )
        if resp.status_code == 200:
            return True
        else:
            _log(f"Gist update failed: {resp.status_code} {resp.text[:200]}")
            return False
    except requests.RequestException as e:
        _log(f"Gist update error: {e}")
        return False


# ── Logging ───────────────────────────────────────────────────────────────────


def _log(msg: str) -> None:
    ts = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)


# ── Main loop ─────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(description="GPU Dashboard Agent")
    parser.add_argument(
        "--once", action="store_true", help="Collect and push once, then exit"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=None,
        help="Override polling interval in seconds",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Collect and print snapshot without pushing",
    )
    args = parser.parse_args()

    if args.dry_run:
        # Minimal config for dry run
        cfg = {
            "machine_label": os.environ.get("GPU_DASH_LABEL", platform.node()),
            "machine_type": os.environ.get("GPU_DASH_TYPE", "workstation"),
        }
        snapshot = collect_snapshot(cfg)
        print(json.dumps(snapshot, indent=2))
        return

    cfg = load_config()
    interval = args.interval or cfg.get("interval_seconds", 30)

    _log(f"GPU Agent starting — {cfg['machine_label']} ({platform.node()})")
    _log(f"  Gist: {cfg['gist_id'][:8]}...")
    _log(f"  Interval: {interval}s")
    _log(f"  GPUs detected: {len(collect_gpus())}")
    if not NVIDIA_SMI:
        _log("  WARNING: nvidia-smi not found — GPU data will be empty")

    # Initial CPU percent measurement (first call always returns 0)
    psutil.cpu_percent(interval=0)

    while True:
        try:
            snapshot = collect_snapshot(cfg)
            ok = push_to_gist(cfg, snapshot)
            gpu_summary = ", ".join(
                f"GPU{g['index']}:{g['utilization_percent']}%"
                for g in snapshot["gpus"]
            )
            status = "OK" if ok else "FAILED"
            _log(f"[{status}] CPU:{snapshot['cpu']['percent']}% RAM:{snapshot['ram']['percent']}% {gpu_summary}")
        except Exception as e:
            _log(f"Error: {e}")

        if args.once:
            break

        time.sleep(interval)


if __name__ == "__main__":
    main()
