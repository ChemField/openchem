# Deploy OpenHydroChem to www.5mart.ml/openhydrochem

The canonical site lives in this repo (also published to `chemfield.github.io/openchem`).
`www.5mart.ml/openhydrochem/` is a second, owner-controlled deploy target.

## One command (owner runs — needs the 5mart SSH credential)
```bash
export CHEMFIELD_5MART_SSH="user@5martm.ssh.transip.me"   # never committed
tools/deploy-openhydrochem-5mart.sh --dry-run   # preview
tools/deploy-openhydrochem-5mart.sh             # rsync --checksum --delete → /openhydrochem/
```
The SSH target comes only from `$CHEMFIELD_5MART_SSH` (or an ssh config alias); no host
or secret is stored in git. Override the remote path with `REMOTE_DIR=/some/path`.

## What ships
The full static tree minus dev/CI/server-only dirs (`.git`, `tools`, `tests`, `docs`, `5mart`
PHP relay, `*.md`): `index.html`, the root games (`slag-run.html`, `speciation-quest.html`,
`species-graph.html`), and everything under `molgang/` — the **3D ChemField chem-web**
(`molgang/knitweb-graph-3d.html`), **The Bench** and the labs (`molgang/lab-immersive.html`,
`lab-3d.html`, `lab-analyze.html` + `molgang/data/`), the bar, and `data/`.

## Verify (after deploy)
- `https://www.5mart.ml/openhydrochem/#knowledge-graph` — the live 3D chem-web renders.
- `https://www.5mart.ml/openhydrochem/#play` → **The Bench** (`molgang/lab-immersive.html`) loads.
- The reactive lab (`lab-3d.html`) needs a live MOLGANG API (`window.MOLGANG_API` in
  `molgang/config.js`); The Bench and the chem-web graph are static and need no backend.
