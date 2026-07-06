#!/usr/bin/env python3
"""Validate + balance-check the Slag Run production chain (data/production-chain.json).

Confirms the JSON is well-formed and that the economy is actually playable: for a
representative feed, at least one comminution strategy must be affordable within
the research grant and yield > 0 g V2O5. Also prints a strategy table (days /
cost / recovery / V2O5) so the balance can be reviewed at a glance. Mirrors the
game's leach model: recovery interpolated by particle size; leach time = coarsest
size / 0.1mm days at 20 C.

Usage:
    python3 tools/build_production.py [--check]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CFG = REPO / "data" / "production-chain.json"


def recovery(size_mm: float, pts: list[dict]) -> float:
    p = sorted(pts, key=lambda x: x["sizeMm"])
    if size_mm <= p[0]["sizeMm"]:
        return p[0]["recovery"]
    if size_mm >= p[-1]["sizeMm"]:
        return p[-1]["recovery"]
    for a, b in zip(p, p[1:]):
        if a["sizeMm"] <= size_mm <= b["sizeMm"]:
            f = (size_mm - a["sizeMm"]) / (b["sizeMm"] - a["sizeMm"])
            return a["recovery"] + f * (b["recovery"] - a["recovery"])
    return p[0]["recovery"]


def simulate(cfg: dict, feed: dict, buckets: int, mill: dict) -> dict:
    """One strategy: order/collect `buckets` of `feed`, grind with `mill`, leach."""
    grant = cfg["research"]["grantEur"]
    days = cfg["research"]["leadTimeDays"] if feed.get("requiresBudget") else 0
    spend = mill["costEur"] + mill["mediaCostEur"]
    if feed.get("requiresBudget"):
        spend += buckets * feed["pricePerBucketEur"]
        days += feed["deliveryDays"]
    else:
        days += feed["travelDays"]

    size = min(feed["startSizeMm"], mill["outputSizeMm"]) if mill["outputSizeMm"] < feed["startSizeMm"] else feed["startSizeMm"]
    days += buckets * mill["daysPerBucket"]
    days += round(size / 0.1 * cfg["leach"]["timeModel"]["daysPer0_1mmAt20C"])

    v = buckets * feed["bucketKg"] * feed["vanadiumMassFraction"] * recovery(size, cfg["leach"]["yieldBySizeMm"])
    v2o5_g = v * cfg["product"]["v_to_v2o5_factor"] * 1000
    return {"days": round(days, 2), "spendEur": round(spend, 2),
            "affordable": mill["costEur"] == 0 or spend <= grant,
            "outSizeMm": size, "v2o5_g": round(v2o5_g, 1)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.parse_args()

    cfg = json.loads(CFG.read_text(encoding="utf-8"))
    ekoliet = next(f for f in cfg["feedstocks"] if f["id"] == "feed:ekoliet")

    print(f"Grant €{cfg['research']['grantEur']} after {cfg['research']['leadTimeDays']} days\n")
    print(f"{'strategy':24} {'days':>6} {'spend€':>8} {'out mm':>7} {'V2O5 g':>8}  ok")
    viable = 0
    for mill in cfg["comminution"]:
        r = simulate(cfg, ekoliet, 2, mill)
        ok = r["affordable"] and r["v2o5_g"] > 0
        viable += ok
        print(f"{mill['name'][:24]:24} {r['days']:>6} {r['spendEur']:>8} {r['outSizeMm']:>7} {r['v2o5_g']:>8}  {'✓' if ok else '✗'}")

    if viable == 0:
        print("FAIL: no affordable strategy yields V2O5 within the grant", file=sys.stderr)
        return 1
    print(f"\nOK: {viable}/{len(cfg['comminution'])} strategies viable within the grant")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
