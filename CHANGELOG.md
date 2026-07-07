# Changelog

- Slag Run: zwaartekracht + spierkracht-tilcontrole — gevuld vat-massa = `emptyKg` + liters × dichtheid (slag 1.8 / leachate 1.15 kg/L); handmatig tillen/keren alleen als kracht ≥ massa, met g=9.81 inspanning-readout (N). Arbeid ontgrendelt zwaardere vaten. Getallen uit `data/production-chain.json` (`physics`/`tanks.emptyKg`). Closes #15
- Docs: `docs/kg-visualization-and-data-sources.md` — research-referentie 3D-KG-visualisatie + chemie-databronnen (voor `species-graph.html` / kg-sources-catalogus).
- Add reproducible 5mart sync/verify: `tools/deploy-manifest.json` + `sync-5mart.sh` (rsync, SSH target via env) + `verify-5mart.sh` (byte-identity for static files, optional route-liveness for the gateway) — closes #4
- Add `tools/validate.py` + CI: repeatable dataset/alias validation (content-CID, alias targets, clay fact-boundary lock, mass-balance assertion links) — closes #7
