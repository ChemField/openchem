# Changelog

- Add reproducible 5mart sync/verify: `tools/deploy-manifest.json` + `sync-5mart.sh` (rsync, SSH target via env) + `verify-5mart.sh` (byte-identity for static files, optional route-liveness for the gateway) — closes #4
- Add `tools/validate.py` + CI: repeatable dataset/alias validation (content-CID, alias targets, clay fact-boundary lock, mass-balance assertion links) — closes #7
