#!/usr/bin/env python3
"""Validate MOLGANG: Speciation Quest levels against the real species graph.

Every level's start/target must be a species in data/chemfield-species-graph.json,
and the target must be reachable from the start using the same four moves the
game engine allows (oxidise / reduce / precipitate / dissolve). This is the CI
guard that keeps quest-levels.json honest: a level can never reference a species
that does not exist or set a target that cannot actually be reached.

The move engine here is the reference implementation; speciation-quest.html
mirrors it in JavaScript.

Usage:
    python3 tools/build_quest.py [--check]   # --check == same run, non-zero exit on any failure
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import deque
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
GRAPH = REPO / "data" / "chemfield-species-graph.json"
LEVELS = REPO / "data" / "quest-levels.json"


def load_species() -> dict[str, dict[str, Any]]:
    doc = json.loads(GRAPH.read_text(encoding="utf-8"))
    out = {}
    for n in doc["forceGraph"]["nodes"]:
        if n.get("kind") == "species":
            out[n["id"]] = {"id": n["id"], "element": n["element"],
                            "ox": int(n["oxidationState"]), "phase": n["phase"]}
    return out


def neighbours(sid: str, species: dict[str, dict[str, Any]]) -> list[tuple[str, str]]:
    """Return (move, targetId) pairs reachable from species `sid`."""
    s = species[sid]
    same_el = [o for o in species.values() if o["element"] == s["element"]]
    out: list[tuple[str, str]] = []

    # redox: next existing oxidation state in the SAME phase
    higher = [o for o in same_el if o["phase"] == s["phase"] and o["ox"] > s["ox"]]
    if higher:
        nxt = min(o["ox"] for o in higher)
        out += [("oxidise", o["id"]) for o in higher if o["ox"] == nxt]
    lower = [o for o in same_el if o["phase"] == s["phase"] and o["ox"] < s["ox"]]
    if lower:
        prv = max(o["ox"] for o in lower)
        out += [("reduce", o["id"]) for o in lower if o["ox"] == prv]

    # phase change at the same oxidation state
    if s["phase"] == "aqueous":
        out += [("precipitate", o["id"]) for o in same_el if o["phase"] == "solid" and o["ox"] == s["ox"]]
    else:
        out += [("dissolve", o["id"]) for o in same_el if o["phase"] == "aqueous" and o["ox"] == s["ox"]]

    return out


def shortest(start: str, target: str, species: dict[str, dict[str, Any]]) -> list[str] | None:
    if start not in species or target not in species:
        return None
    q: deque[tuple[str, list[str]]] = deque([(start, [start])])
    seen = {start}
    while q:
        cur, path = q.popleft()
        if cur == target:
            return path
        for _move, nxt in neighbours(cur, species):
            if nxt not in seen:
                seen.add(nxt)
                q.append((nxt, path + [nxt]))
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate speciation quest levels")
    ap.add_argument("--check", action="store_true")
    ap.parse_args()

    species = load_species()
    data = json.loads(LEVELS.read_text(encoding="utf-8"))
    failures = 0

    for lvl in data["levels"]:
        lid = lvl["id"]
        for key in ("start", "target"):
            if lvl[key] not in species:
                print(f"FAIL {lid}: {key} '{lvl[key]}' is not a species in the graph", file=sys.stderr)
                failures += 1
        if lvl["start"] in species and lvl["target"] in species:
            path = shortest(lvl["start"], lvl["target"], species)
            if path is None:
                print(f"FAIL {lid}: target '{lvl['target']}' unreachable from '{lvl['start']}'", file=sys.stderr)
                failures += 1
            else:
                optimal = len(path) - 1
                flag = "" if optimal == lvl["par"] else f"  (par={lvl['par']})"
                print(f"OK   {lid}: {optimal} optimal move(s){flag}  {' -> '.join(p.split(':')[-1] for p in path)}")

    if failures:
        print(f"{failures} level check(s) failed", file=sys.stderr)
        return 1
    print(f"all {len(data['levels'])} levels solvable")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
