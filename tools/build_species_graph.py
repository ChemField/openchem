#!/usr/bin/env python3
"""Compile data/species-graph.seed.json into data/chemfield-species-graph.json.

Produces a field/1 knowledge graph of vanadium & chromium speciation that is
BOTH provenance-anchored and 3d-force-graph-ready:

  * `forceGraph` — {nodes, links} that data/species-graph.html renders directly
    (nodes coloured by species colour / grouped by oxidation state);
  * `@graph` — provenance triples (hasElement / hasOxidationState / hasPhase /
    attestedBy) in the same shape as the composition web;
  * per-node `cid`/`ual` and a root `origintrailAsset` whose `linked_sources`
    cross-reference the UALs already minted in data/chemfield-kg-sources.json —
    so this graph's provenance chains straight back to the source catalog.

Only structural facts (species identity, oxidation state, phase) are asserted;
no free energies / Pourbaix boundaries are invented (factPolicy: no invented
measurements). Thermodynamic enrichment is a separate, live step.

Usage:
    python3 tools/build_species_graph.py [--date YYYY-MM-DD] [--check]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
SEED = REPO / "data" / "species-graph.seed.json"
CATALOG = REPO / "data" / "chemfield-kg-sources.json"
OUT = REPO / "data" / "chemfield-species-graph.json"

NAMESPACE = "did:dkg:knitweb"
CANONICAL_FIELD = "chemfield:speciation:v-cr"
GRAPH_ID = "chemfield:species-graph:v-cr:v1"

CONTEXT = {
    "@vocab": "https://schema.org/",
    "chemfield": "https://chemfield.github.io/openchem/vocab#",
    "prov": "http://www.w3.org/ns/prov#",
    "dcterms": "http://purl.org/dc/terms/",
}

OXIDATION_COLOR = {2: "#8e44ad", 3: "#27ae60", 4: "#2980b9", 5: "#f39c12", 6: "#e74c3c"}


def canonical(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def strip_ids(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: strip_ids(v) for k, v in obj.items() if k not in ("cid", "ual")}
    if isinstance(obj, list):
        return [strip_ids(v) for v in obj]
    return obj


def cid_of(obj: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical(strip_ids(obj)).encode("utf-8")).hexdigest()


def ual_of(cid: str) -> str:
    return f"{NAMESPACE}/sha256-{cid.split('sha256:')[1]}"


def source_uals() -> dict[str, dict[str, str]]:
    """Map kg-source id -> {ual, title} from the built source catalog."""
    cat = json.loads(CATALOG.read_text(encoding="utf-8"))
    return {s["id"]: {"ual": s["ual"], "title": s["title"]} for s in cat["sources"]}


def build(date: str | None, prior: dict[str, Any] | None) -> dict[str, Any]:
    seed = json.loads(SEED.read_text(encoding="utf-8"))
    catalog = source_uals()

    nodes: list[dict[str, Any]] = []
    links: list[dict[str, Any]] = []
    graph: list[dict[str, Any]] = []
    used_source_ids: set[str] = set()

    # Element nodes
    for el in seed["elements"]:
        node = {"id": el["id"], "name": el["symbol"], "label": el["name"],
                "group": "element", "kind": "element", "val": 8, "color": "#ecf0f1"}
        node["cid"] = cid_of({k: node[k] for k in ("id", "kind", "label")})
        node["ual"] = ual_of(node["cid"])
        nodes.append(node)
        for sid in el.get("sourceIds", []):
            used_source_ids.add(sid)
            links.append({"source": el["id"], "target": sid, "label": "attestedBy"})
            graph.append({"subject": el["id"], "predicate": "chemfield:attestedBy", "object": sid, "type": "Dataset", "weight": 1})

    # Species nodes
    for sp in seed["species"]:
        ox = int(sp["oxidationState"])
        color = sp.get("color") or OXIDATION_COLOR.get(ox, "#95a5a6")
        node = {
            "id": sp["id"], "name": sp["formula"], "label": sp["name"],
            "group": f"ox{ox}", "kind": "species", "element": sp["element"],
            "oxidationState": ox, "phase": sp["phase"], "color": color,
            "val": 5 if sp["phase"] == "aqueous" else 6,
            "tags": sp.get("tags", []),
        }
        node["cid"] = cid_of({k: v for k, v in node.items() if k not in ("cid", "ual", "color", "val")})
        node["ual"] = ual_of(node["cid"])
        nodes.append(node)

        el_id = f"element:{sp['element']}"
        links.append({"source": sp["id"], "target": el_id, "label": "hasElement"})
        graph.append({"subject": sp["id"], "predicate": "chemfield:hasElement", "object": el_id, "type": "Dataset", "weight": 1})
        graph.append({"subject": sp["id"], "predicate": "chemfield:hasOxidationState", "object": str(ox), "type": "Dataset", "weight": 1})
        graph.append({"subject": sp["id"], "predicate": "chemfield:hasPhase", "object": sp["phase"], "type": "Dataset", "weight": 1})
        for sid in sp.get("sourceIds", []):
            used_source_ids.add(sid)
            links.append({"source": sp["id"], "target": sid, "label": "attestedBy"})
            graph.append({"subject": sp["id"], "predicate": "chemfield:attestedBy", "object": sid, "type": "Dataset", "weight": 1})

    # Source nodes (carry the catalog UAL so the viewer shows provenance)
    for sid in sorted(used_source_ids):
        meta = catalog.get(sid, {})
        nodes.append({
            "id": sid, "name": sid.replace("kg:", ""), "label": meta.get("title", sid),
            "group": "source", "kind": "source", "val": 7, "color": "#34495e",
            "ual": meta.get("ual"),
        })

    linked_sources = [
        {"id": sid, "title": catalog.get(sid, {}).get("title", sid), "ual": catalog.get(sid, {}).get("ual")}
        for sid in sorted(used_source_ids)
    ]
    origintrail_asset = {
        "origintrail_id": GRAPH_ID,
        "originator": "ChemField OpenChem",
        "namespace": NAMESPACE,
        "assertion": (
            "Structural speciation graph for vanadium and chromium (species identity, oxidation state, phase). "
            "Reference facts only; thermodynamic values are enriched live from the linked sources. "
            "Provenance chains to data/chemfield-kg-sources.json UALs."
        ),
        "linked_sources": linked_sources,
    }
    origintrail_asset["cid"] = cid_of(origintrail_asset)
    origintrail_asset["ual"] = ual_of(origintrail_asset["cid"])

    doc: dict[str, Any] = {
        "@context": CONTEXT,
        "kind": "chemfield-species-graph",
        "schemaVersion": "chemfield-species-graph-v1",
        "id": GRAPH_ID,
        "title": "ChemField V/Cr speciation field graph",
        "updatedAt": date or (prior or {}).get("updatedAt") or "unset",
        "canonicalField": CANONICAL_FIELD,
        "factPolicy": {
            "noInventedMeasurements": True,
            "assertedScope": "species identity, oxidation state, phase (structural reference facts)",
            "enrichmentPending": "free energies / Pourbaix boundaries from Materials Project + PHREEQC log K",
        },
        "originTrail": {
            "status": "prepared_not_published",
            "namespace": NAMESPACE,
            "sourceLinking": "linked_sources reference the cid/ual minted in data/chemfield-kg-sources.json",
            "gateway": "https://www.5mart.ml/Slag/origintrail-gateway.php",
        },
        "counts": {
            "nodes": len(nodes), "links": len(links),
            "species": len(seed["species"]), "elements": len(seed["elements"]),
            "sources": len(used_source_ids),
        },
        "forceGraph": {"nodes": nodes, "links": links},
        "@graph": graph,
        "origintrailAsset": origintrail_asset,
    }
    doc["cid"] = cid_of(doc)
    doc["ual"] = ual_of(doc["cid"])
    return doc


def dump(doc: dict[str, Any]) -> str:
    return json.dumps(doc, indent=2, ensure_ascii=False) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description="Build ChemField V/Cr speciation graph")
    ap.add_argument("--date")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    prior = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else None
    doc = build(args.date, prior)
    text = dump(doc)

    if args.check:
        if (OUT.read_text(encoding="utf-8") if OUT.exists() else "") != text:
            print("DRIFT: data/chemfield-species-graph.json stale — run tools/build_species_graph.py", file=sys.stderr)
            return 1
        print(f"OK: species graph up to date ({doc['counts']['nodes']} nodes / {doc['counts']['links']} links)")
        return 0

    OUT.write_text(text, encoding="utf-8")
    print(f"wrote {OUT.relative_to(REPO)}  nodes={doc['counts']['nodes']} links={doc['counts']['links']} root={doc['cid']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
