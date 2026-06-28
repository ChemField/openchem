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
