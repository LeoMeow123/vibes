#!/usr/bin/env python3
"""Issue (or revoke) a per-machine ingest key for direct agent -> Supabase reporting.

Needs the service role key (~/.config/gpu-dashboard/supabase.json), i.e. run this on
the bridge host. The key is printed ONCE; only its sha256 is stored in
gpu_machines.ingest_key_hash. Paste the key into the machine's agent config
(~/.config/gpu-dashboard/config.json -> "ingest_key"), or run agent/install.sh there.

    issue_key.py blackwell-2                 # issue a key for an existing or new machine
    issue_key.py blackwell-2 --revoke        # clear the hash (agent writes start failing)
    issue_key.py --list                      # which machines have a key
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import secrets
import sys
import urllib.error
import urllib.request
from pathlib import Path

CONFIG = Path.home() / ".config" / "gpu-dashboard" / "supabase.json"


def cfg() -> dict:
    try:
        d = json.load(open(CONFIG))
    except (OSError, json.JSONDecodeError):
        sys.exit(f"ERROR: {CONFIG} missing; this must run on the bridge host")
    if not d.get("url") or not d.get("service_role_key"):
        sys.exit(f"ERROR: {CONFIG} needs url and service_role_key")
    return d


def req(c: dict, method: str, path: str, payload=None, prefer: str | None = None):
    key = c["service_role_key"]
    h = {"apikey": key, "Content-Type": "application/json"}
    if key.startswith("eyJ"):
        h["Authorization"] = f"Bearer {key}"
    if prefer:
        h["Prefer"] = prefer
    body = json.dumps(payload).encode() if payload is not None else None
    r = urllib.request.Request(f"{c['url'].rstrip('/')}/rest/v1/{path}", data=body, method=method, headers=h)
    try:
        with urllib.request.urlopen(r, timeout=30) as resp:
            raw = resp.read()
            return json.loads(raw) if raw else None
    except urllib.error.HTTPError as e:
        sys.exit(f"ERROR: {method} {path} -> {e.code} {e.read().decode()[:300]}")


def main() -> None:
    p = argparse.ArgumentParser(description="Issue per-machine ingest keys")
    p.add_argument("machine", nargs="?", help="machine key, e.g. blackwell-2 (lowercase, [a-z0-9_-])")
    p.add_argument("--revoke", action="store_true")
    p.add_argument("--list", action="store_true")
    a = p.parse_args()
    c = cfg()

    if a.list or not a.machine:
        rows = req(c, "GET", "gpu_machines?select=key,label,type,last_seen,ingest_key_hash&order=key")
        for r in rows:
            print(f"  {r['key']:26s} {r.get('label') or '':26s} {'KEY ISSUED' if r.get('ingest_key_hash') else 'no key (gist/bridge)'}")
        if not a.machine:
            return

    key_name = a.machine.strip().lower()
    if not re.fullmatch(r"[a-z0-9_-]{1,64}", key_name):
        sys.exit("ERROR: machine key must match [a-z0-9_-]")

    if a.revoke:
        req(c, "PATCH", f"gpu_machines?key=eq.{key_name}", {"ingest_key_hash": None}, prefer="return=minimal")
        print(f"revoked ingest key for {key_name}")
        return

    secret = "gdk_" + secrets.token_urlsafe(32)
    digest = hashlib.sha256(secret.encode()).hexdigest()
    # upsert: creates the machine row if the agent has never reported
    req(c, "POST", "gpu_machines?on_conflict=key",
        [{"key": key_name, "label": key_name, "ingest_key_hash": digest}],
        prefer="resolution=merge-duplicates,return=minimal")
    print(f"Ingest key for {key_name} (shown once, store it in that machine's config):\n")
    print(f"    {secret}\n")
    print("On the machine, in ~/.config/gpu-dashboard/config.json add:")
    print(json.dumps({"supabase_url": c["url"], "supabase_anon_key": "<publishable key>", "ingest_key": secret, "push_gist": False}, indent=4))
    print("then: systemctl --user restart gpu-agent")


if __name__ == "__main__":
    main()
