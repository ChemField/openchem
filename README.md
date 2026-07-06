# OpenChem

Static landing page for the OpenHydroChem / ChemExtract AI project.

## Local preview

Open `index.html` directly in a browser, or run:

```sh
python3 -m http.server 8080
```

Then visit `http://localhost:8080/`.

## GitHub Pages

This repository is ready for GitHub Pages from the `main` branch root.

Project URL after Pages is enabled:

```text
https://chemfield.github.io/openchem/
```

## ChemField data aliases

The SmartSlag composition web is stored at:

```text
data/chemfield-compositions.json
```

The same dataset can be discovered through static alias pointers:

```text
fieldchem.json
openchem.json
webchem.json
chemweb.json
chemfield.json
```

Each composition record carries source, author/creator/publisher fields, content hashes, and a prepared OriginTrail-style UAL. Noord-Holland clay records are sampling targets until measured location/depth chemistry is attached.

The current `chemfield-composition-web-v1` schema is introduced with this dataset; no older OpenChem composition-web consumers are migrated in this PR.

## Laptop-backed OriginTrail gateway

For the current test setup, the MacBook can act as a headless OriginTrail publisher/gateway while `5mart.ml` stays the public web entrypoint. This is not a full DKG core node; it is a lightweight bridge that can serve status, manifest, and dataset routes through a reverse SSH tunnel.

Run the laptop service:

```sh
cp origintrail-laptop.env.example .origintrail-laptop.env
set -a
. ./.origintrail-laptop.env
set +a
node tools/origintrail-laptop-gateway.mjs
```

In a second terminal, keep a tunnel open. For a quick public test:

```sh
cloudflared tunnel --url http://127.0.0.1:8788 --no-autoupdate
```

Deploy the assigned URL to 5mart as `origintrail-tunnel.json` using the structure in `5mart/origintrail-tunnel.example.json`.

The SSH reverse tunnel is useful for shell-to-laptop testing, but on TransIP shared hosting the public PHP runtime may not share the SSH host's `127.0.0.1`:

```sh
ssh -N -R 127.0.0.1:18788:127.0.0.1:8788 5martml@5martm.ssh.transip.me
```

Public routes, after `5mart/origintrail-gateway.php` and `origintrail-node.json` are deployed to `/Slag/`:

```text
https://www.5mart.ml/Slag/origintrail-node.json
https://www.5mart.ml/Slag/origintrail-gateway.php?route=status
https://www.5mart.ml/Slag/origintrail-gateway.php?route=manifest
https://www.5mart.ml/Slag/origintrail-gateway.php?route=dataset
https://www.5mart.ml/Slag/origintrail-gateway.php?route=rewards
```

Only set `ORIGINTRAIL_OPERATIONAL_PRIVATE_KEY` in the local `.origintrail-laptop.env` file on the laptop. Do not upload wallet secrets to 5mart or commit them to Git.

The `rewards` route is a scenario calculator, not a yield promise. OriginTrail Core Node income depends on paid DKG activity, node ask, stake/delegation, uptime, proofs, operator fee, and the selected chain.

## External knowledge-graph source catalog

ChemField draws on public chemical knowledge graphs and linked-data sources
(Materials Project, OPTIMADE, MatKG, COD, Wikidata, PubChemRDF, ChEBI, RRUFF,
EMMO, PHREEQC/GEMS, USGS MRDATA, …). These are curated in:

```text
data/kg-sources.seed.json          # human-curated seed (identity, licence, access)
data/chemfield-kg-sources.json     # built catalog — OriginTrail-prepared asset
kg-sources.json                    # root alias pointer (cid/ual of the catalog)
```

Every source is **linked to OriginTrail**: the builder computes a stable
`cid = sha256(canonical(descriptor))` and `ual = did:dkg:knitweb/sha256-<cid>`
per source (identical canonicalisation to the composition web) and links all of
them into `origintrailAsset.linked_sources`, ready to publish to the DKG through
the 5mart.ml gateway. The catalog also carries a `@graph` of provenance triples
so it renders directly in `3d-force-graph`.

Licence posture is explicit: `distribution: "redistributable"` (open, attribution
kept — may seed field/1 graphs) vs `"reference_only"` (commercial/closed/GPL/
share-alike — cite and link, never vendor). Volatile live metrics live in
`snapshotStats`, separate from the stable source identity.

Build and validate:

```sh
python3 tools/build_kg_sources.py --date 2026-07-05   # rebuild catalog + pointer
python3 tools/build_kg_sources.py --check --date ...  # CI drift guard
```

### Regular data refresh (automation)

`tools/refresh_kg_sources.py` probes public no-auth endpoints (OPTIMADE providers,
COD structure count, …), writes the live metrics into `snapshotStats`, and
rebuilds so the catalog root cid/ual advance. Each probe is best-effort — a
network failure keeps the prior value and records `refreshStatus:"unreachable"`.

The GitHub Actions workflow `.github/workflows/refresh-kg-sources.yml` runs this
**weekly (Mon 06:00 UTC)** and on `workflow_dispatch`, committing only when the
catalog changed. `.github/workflows/ci.yml` fails any push/PR that leaves the
catalog stale. Add a new live metric by appending a probe to `PROBES` in
`refresh_kg_sources.py`; add a new source by editing the seed and rebuilding.

## V/Cr speciation field graph (3D)

The first field/1 graph built on the catalog: vanadium & chromium speciation
(species identity, oxidation state, phase) — structural reference facts only, no
invented thermodynamics. Directly supports the VANELEX thesis (V₂O₅ recovered
from BOF steel slag → VRFB electrolyte).

```text
data/species-graph.seed.json        # curated V/Cr species
data/chemfield-species-graph.json   # built graph (forceGraph + @graph + OriginTrail asset)
species-graph.html                  # 3d-force-graph viewer (GitHub Pages)
```

Every node carries a `cid`/`ual`, and the graph's `origintrailAsset.linked_sources`
chains straight back to the UALs minted in `data/chemfield-kg-sources.json`
(Materials Project, PHREEQC, COD, Wikidata, USGS MRDATA). Rebuild:

```sh
python3 tools/build_species_graph.py --date 2026-07-06
python3 tools/build_species_graph.py --check --date ...   # CI drift guard
```

Thermodynamic enrichment (Pourbaix boundaries, log K) is the next live step —
pulled from Materials Project `get_pourbaix_entries()` and PHREEQC, never invented.

## ClosedChem

ClosedChem is the permissioned counterpart for opted-in closed P2P chemistry knitworks.

ClosedChem assimilates OpenChem one way:

```text
OpenChem -> ClosedChem
```

Repository:

```text
https://github.com/ChemField/closedchem
```

## License

Apache License 2.0.
