#!/usr/bin/env python3
"""Compile data/kg-sources.seed.json into data/chemfield-kg-sources.json.

For every curated external knowledge-graph / linked-data source this:

  * computes a STABLE content id  cid = sha256(canonical(descriptor))
    and an OriginTrail UAL  did:dkg:knitweb/sha256-<cid>  — identical
    canonicalisation to the SmartSlag composition web
    (json.dumps(obj, sort_keys=True, separators=(",",":")), cid/ual excluded);
  * emits a `@graph` of provenance triples (hasSource / hasLicense / hasAccess /
    hasDistribution / providesData / hasRelevance) so the catalog renders in
    3d-force-graph directly;
  * links every source into an `origintrailAsset` (linked_sources) so each
    source is coupled to OriginTrail, ready for DKG publication via the
    5mart.ml laptop gateway.

Volatile live metrics (structure/entry/triple counts, versions) are NOT part of
the stable source identity; they live in `snapshotStats` and are refreshed by
tools/refresh_kg_sources.py. The catalog root cid therefore changes when either
the curated seed OR the observed snapshot changes, while individual source UALs
stay stable.

Usage:
    python3 tools/build_kg_sources.py [--date YYYY-MM-DD] [--check]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
SEED = REPO / "data" / "kg-sources.seed.json"
OUT = REPO / "data" / "chemfield-kg-sources.json"
POINTER = REPO / "kg-sources.json"

NAMESPACE = "did:dkg:knitweb"
CANONICAL_FIELD = "chemfield:kg-sources"
CATALOG_ID = "chemfield:kg-source-catalog:v1"

CONTEXT = {
    "@vocab": "https://schema.org/",
    "chemfield": "https://chemfield.github.io/openchem/vocab#",
    "prov": "http://www.w3.org/ns/prov#",
    "dcterms": "http://purl.org/dc/terms/",
}


def canonical(obj: Any) -> str:
    """Stable JSON used for hashing (matches the composition-web cid rule)."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def strip_ids(obj: Any) -> Any:
    """Recursively drop cid/ual so a container hash is independent of them."""
    if isinstance(obj, dict):
        return {k: strip_ids(v) for k, v in obj.items() if k not in ("cid", "ual")}
    if isinstance(obj, list):
        return [strip_ids(v) for v in obj]
    return obj


def cid_of(obj: Any) -> str:
    digest = hashlib.sha256(canonical(strip_ids(obj)).encode("utf-8")).hexdigest()
    return f"sha256:{digest}"


def ual_of(cid: str) -> str:
    return f"{NAMESPACE}/sha256-{cid.split('sha256:')[1]}"


def source_triples(src: dict[str, Any]) -> list[dict[str, Any]]:
    sid = src["id"]
    triples = [
        {"subject": CATALOG_ID, "predicate": "chemfield:hasSource", "object": sid, "type": "Dataset", "weight": 1},
        {"subject": sid, "predicate": "chemfield:hasLicense", "object": src["license"], "type": "Dataset", "weight": 1},
        {"subject": sid, "predicate": "chemfield:hasAccessStatus", "object": src["accessStatus"], "type": "Dataset", "weight": 1},
        {"subject": sid, "predicate": "chemfield:hasDistribution", "object": src["distribution"], "type": "Dataset", "weight": 1},
        {"subject": sid, "predicate": "chemfield:hasRelevance", "object": src["relevance"], "type": "Dataset", "weight": 1},
    ]
    for use in src.get("usedFor", []):
        triples.append({"subject": sid, "predicate": "chemfield:providesData", "object": use, "type": "Dataset", "weight": 1})
    return triples


def linked_source(src: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": src["id"],
        "type": src["type"],
        "title": src["title"],
        "url": src.get("api") or src["homepage"],
        "homepage": src["homepage"],
        "maintainer": src.get("maintainer"),
        "license": src["license"],
        "distribution": src["distribution"],
        "cid": src["cid"],
        "ual": src["ual"],
    }


def build(date: str | None, prior: dict[str, Any] | None) -> dict[str, Any]:
    seed = json.loads(SEED.read_text(encoding="utf-8"))
    sources: list[dict[str, Any]] = []
    graph: list[dict[str, Any]] = []

    for raw in seed["sources"]:
        src = dict(raw)  # curated descriptor, no cid/ual yet
        cid = cid_of(src)
        src["cid"] = cid
        src["ual"] = ual_of(cid)
        sources.append(src)
        graph.extend(source_triples(src))

    # Redistribution split — makes the licence posture queryable.
    redistributable = [s["id"] for s in sources if s["distribution"] == "redistributable"]
    reference_only = [s["id"] for s in sources if s["distribution"] == "reference_only"]

    origintrail_asset = {
        "origintrail_id": CATALOG_ID,
        "originator": "ChemField OpenChem",
        "namespace": NAMESPACE,
        "assertion": (
            "Curated catalog of external chemical knowledge-graph / linked-data sources for ChemField. "
            "Each source carries a stable cid/ual; redistributable sources may seed field/1 graphs, "
            "reference_only sources are cited but never vendored."
        ),
        "redistributableSourceIds": redistributable,
        "referenceOnlySourceIds": reference_only,
        "linked_sources": [linked_source(s) for s in sources],
    }
    asset_cid = cid_of(origintrail_asset)
    origintrail_asset["cid"] = asset_cid
    origintrail_asset["ual"] = ual_of(asset_cid)

    updated_at = date or (prior or {}).get("updatedAt") or "unset"
    snapshot = (prior or {}).get("snapshotStats", {})

    doc: dict[str, Any] = {
        "@context": CONTEXT,
        "kind": "chemfield-kg-source-catalog",
        "schemaVersion": "chemfield-kg-source-catalog-v1",
        "id": CATALOG_ID,
        "title": "ChemField external knowledge-graph & linked-data source catalog",
        "updatedAt": updated_at,
        "canonicalField": CANONICAL_FIELD,
        "originTrail": {
            "status": "prepared_not_published",
            "namespace": NAMESPACE,
            "publishBlocker": "Publish to the DKG via the 5mart.ml laptop gateway once OriginTrail node credentials are present.",
            "localIdentityRule": "sha256 over stable JSON (sort_keys, compact) with cid/ual excluded; identical to the composition-web rule.",
            "sourceLinking": "Every source is linked in origintrailAsset.linked_sources with its own cid/ual.",
            "gateway": "https://www.5mart.ml/Slag/origintrail-gateway.php",
        },
        "counts": {
            "sources": len(sources),
            "redistributable": len(redistributable),
            "referenceOnly": len(reference_only),
        },
        "sources": sources,
        "visualizationStack": seed.get("visualizationStack", []),
        "snapshotStats": snapshot,
        "@graph": graph,
        "origintrailAsset": origintrail_asset,
    }
    root_cid = cid_of(doc)
    doc["cid"] = root_cid
    doc["ual"] = ual_of(root_cid)
    return doc


def dump(doc: dict[str, Any]) -> str:
    return json.dumps(doc, indent=2, ensure_ascii=False) + "\n"


def pointer_of(doc: dict[str, Any]) -> str:
    """Root alias pointer, matching the composition-web pointer convention."""
    return dump({
        "kind": "chemfield_alias_pointer",
        "alias": "kg-sources",
        "canonicalField": doc["canonicalField"],
        "href": "data/chemfield-kg-sources.json",
        "targetCid": doc["cid"],
        "targetUal": doc["ual"],
        "updatedAt": doc["updatedAt"],
    })


def main() -> int:
    ap = argparse.ArgumentParser(description="Build ChemField KG source catalog")
    ap.add_argument("--date", help="updatedAt value (YYYY-MM-DD); default reuses existing")
    ap.add_argument("--check", action="store_true", help="fail if the on-disk catalog is stale")
    args = ap.parse_args()

    prior = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else None
    doc = build(args.date, prior)
    text = dump(doc)

    pointer_text = pointer_of(doc)

    if args.check:
        drift = []
        if (OUT.read_text(encoding="utf-8") if OUT.exists() else "") != text:
            drift.append("data/chemfield-kg-sources.json")
        if (POINTER.read_text(encoding="utf-8") if POINTER.exists() else "") != pointer_text:
            drift.append("kg-sources.json")
        if drift:
            print(f"DRIFT: {', '.join(drift)} stale — run tools/build_kg_sources.py", file=sys.stderr)
            return 1
        print(f"OK: catalog up to date ({doc['counts']['sources']} sources, root {doc['cid']})")
        return 0

    OUT.write_text(text, encoding="utf-8")
    POINTER.write_text(pointer_text, encoding="utf-8")
    print(f"wrote {OUT.relative_to(REPO)} + {POINTER.name}  sources={doc['counts']['sources']}  root={doc['cid']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
