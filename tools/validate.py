#!/usr/bin/env python3
"""Validate the ChemField composition dataset and its alias pointers.

Replaces the ad-hoc manual checks (jq empty, jq -e invariants, inline JS parsing)
with one repeatable command. Exit code 0 = all checks pass, 1 = at least one failure.

Checks (issue ChemField/openchem#7):
  1. data/chemfield-compositions.json parses as JSON.
  2. Content-identity: every object carrying a `cid` reproduces it as
     sha256 over canonical JSON (sorted keys, compact separators, `cid`/`ual`
     excluded) — the same rule used to mint the static release. The root `cid`
     is checked the same way.
  3. Alias pointer files (<alias>.json) target the current root CID and UAL.
  4. Fact boundary: every clay record that is not measured stays locked — its
     mass balance is pending and the enrichment comparison is not unlocked.
  5. The OriginTrail assertion graph contains mass-balance links.

No third-party dependencies (stdlib only).
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATASET = ROOT / "data" / "chemfield-compositions.json"

failures: list[str] = []
checks = 0


def check(ok: bool, msg: str) -> None:
    global checks
    checks += 1
    if not ok:
        failures.append(msg)


def _strip(o):
    """Recursively drop identity fields so content hashes to a stable value."""
    if isinstance(o, dict):
        return {k: _strip(v) for k, v in o.items() if k not in ("cid", "ual")}
    if isinstance(o, list):
        return [_strip(v) for v in o]
    return o


def content_cid(o) -> str:
    canon = json.dumps(_strip(o), sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(canon.encode("utf-8")).hexdigest()


def main() -> int:
    # 1. parse
    try:
        raw = DATASET.read_text(encoding="utf-8")
        data = json.loads(raw)
    except (OSError, json.JSONDecodeError) as e:
        print(f"FAIL: cannot parse {DATASET}: {e}")
        return 1

    # 2. content-identity of root + every object with a cid
    root_cid = content_cid(data)
    check(
        data.get("cid") == root_cid,
        f"root cid mismatch: field={data.get('cid')} computed={root_cid}",
    )

    def walk(o, path="$"):
        if isinstance(o, dict):
            if "cid" in o and isinstance(o["cid"], str) and o["cid"].startswith("sha256:"):
                exp = content_cid(o)
                check(o["cid"] == exp, f"cid mismatch at {path}: {o['cid']} != {exp}")
            for k, v in o.items():
                walk(v, f"{path}.{k}")
        elif isinstance(o, list):
            for i, v in enumerate(o):
                walk(v, f"{path}[{i}]")

    walk(data)

    # 3. alias pointer files target the current root CID/UAL
    root_ual = data.get("ual")
    aliases = [a["alias"] for a in data.get("aliases", []) if "alias" in a]
    check(bool(aliases), "no aliases declared in dataset")
    for alias in aliases:
        pf = ROOT / f"{alias}.json"
        if not pf.exists():
            check(False, f"alias pointer file missing: {pf.name}")
            continue
        try:
            p = json.loads(pf.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            check(False, f"alias pointer {pf.name} invalid JSON: {e}")
            continue
        check(
            p.get("targetCid") == root_cid,
            f"{pf.name}: targetCid {p.get('targetCid')} != root {root_cid}",
        )
        check(
            root_ual is None or p.get("targetUal") == root_ual,
            f"{pf.name}: targetUal {p.get('targetUal')} != root {root_ual}",
        )
        check(
            p.get("canonicalField") == data.get("canonicalField"),
            f"{pf.name}: canonicalField mismatch",
        )

    # 4. fact boundary: unmeasured clay records stay locked
    for rec in data.get("records", []):
        meas = str(rec.get("measurementStatus", ""))
        mb = (rec.get("massBalance") or {}).get("status", "")
        if "clay" in rec.get("id", "") and meas.startswith("not_measured"):
            check(
                "pending" in mb or "locked" in mb,
                f"unmeasured clay record {rec['id']} not locked (massBalance status={mb!r})",
            )
    for comp in data.get("comparisons", []):
        # any comparison against not-yet-measured clay must keep enrichment locked
        if "clay" in comp.get("id", ""):
            check(
                "locked" in comp.get("status", ""),
                f"comparison {comp['id']} must keep numeric enrichment locked "
                f"(status={comp.get('status')!r})",
            )

    # 5. assertion graph contains mass-balance links
    assertion = data.get("origintrailAsset", {}).get("assertion", [])
    mb_links = [t for t in assertion if "mass" in json.dumps(t).lower()]
    check(
        len(mb_links) > 0,
        "OriginTrail assertion graph has no mass-balance links",
    )

    # report
    if failures:
        print(f"chemfield validate: {len(failures)} FAILURE(S) / {checks} checks")
        for f in failures:
            print(f"  - {f}")
        return 1
    print(f"chemfield validate: OK ({checks} checks passed)")
    print(f"  root cid: {root_cid}")
    print(f"  aliases : {', '.join(aliases)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
