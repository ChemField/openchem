#!/usr/bin/env python3
"""Refresh volatile metrics for the ChemField KG source catalog, then rebuild.

This is the scheduled-update entrypoint. It probes public, no-auth endpoints for
the sources that expose live counts, writes them into `snapshotStats` (with a
per-probe `refreshStatus` and `lastChecked`), and then re-runs the builder so the
catalog root cid/ual reflect the new snapshot. Every probe is best-effort: a
network failure keeps the previous value and records `refreshStatus:"unreachable"`
rather than failing the run.

Stable source identities (cid/ual) are never touched here — only the observed
snapshot changes. Add a probe by appending to PROBES.

Usage:
    python3 tools/refresh_kg_sources.py [--date YYYY-MM-DD] [--timeout 20]
"""
from __future__ import annotations

import argparse
import datetime
import json
import ssl
import urllib.request
from pathlib import Path
from typing import Any, Callable

import build_kg_sources as builder  # sibling module

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "data" / "chemfield-kg-sources.json"

UA = {"User-Agent": "ChemField-kg-refresh/1.0 (+https://chemfield.github.io/openchem/)"}


def _get_json(url: str, timeout: float) -> Any:
    ctx = ssl.create_default_context()
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _optimade_count(base: str, timeout: float) -> dict[str, Any]:
    """Total structures a provider advertises via OPTIMADE meta.data_available."""
    data = _get_json(f"{base.rstrip('/')}/v1/structures?page_limit=1", timeout)
    meta = data.get("meta", {})
    return {"structures": meta.get("data_available"), "apiVersion": meta.get("api_version")}


def _optimade_providers(timeout: float) -> dict[str, Any]:
    data = _get_json("https://providers.optimade.org/providers.json", timeout)
    providers = data.get("data", [])
    return {"providers": len(providers)}


# id -> probe callable returning a dict of metrics (raises on failure)
PROBES: dict[str, Callable[[float], dict[str, Any]]] = {
    "kg:optimade": _optimade_providers,
    "kg:cod": lambda t: _optimade_count("https://www.crystallography.net/cod/optimade", t),
    "kg:materials-project": lambda t: {"note": "count needs MP API key; enrich in an authenticated job"},
}


def refresh(timeout: float) -> dict[str, dict[str, Any]]:
    prior = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {}
    snapshot: dict[str, dict[str, Any]] = dict(prior.get("snapshotStats", {}))
    checked_at = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat()

    for sid, probe in PROBES.items():
        entry = dict(snapshot.get(sid, {}))
        try:
            metrics = probe(timeout)
            entry.update({k: v for k, v in metrics.items() if v is not None})
            entry["refreshStatus"] = "ok"
        except Exception as exc:  # noqa: BLE001 — degrade gracefully, keep prior values
            entry["refreshStatus"] = "unreachable"
            entry["lastError"] = f"{type(exc).__name__}: {exc}"[:200]
        entry["lastChecked"] = checked_at
        snapshot[sid] = entry
        print(f"  {sid}: {entry.get('refreshStatus')}  {({k: v for k, v in entry.items() if k not in ('lastChecked', 'lastError')})}")

    return snapshot


def main() -> int:
    ap = argparse.ArgumentParser(description="Refresh KG source catalog metrics and rebuild")
    ap.add_argument("--date", help="updatedAt for the rebuild (YYYY-MM-DD); default today (UTC)")
    ap.add_argument("--timeout", type=float, default=20.0)
    args = ap.parse_args()

    print("refreshing snapshot metrics...")
    snapshot = refresh(args.timeout)

    # Rebuild with the new snapshot + today's date so root cid/ual advance.
    prior = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {}
    prior["snapshotStats"] = snapshot
    date = args.date or datetime.date.today().isoformat()
    doc = builder.build(date, prior)
    OUT.write_text(builder.dump(doc), encoding="utf-8")
    print(f"rebuilt {OUT.relative_to(REPO)}  date={date}  root={doc['cid']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
