# Changelog

- #7 · Dataset-validatie: `tools/validate.mjs` + `npm run validate` / `make validate` + CI (`.github/workflows/ci.yml`). Controleert cid/ual-vorm & -consistentie, referentiële integriteit, alias-pointers → huidige root-CID/UAL, elk clay-record locked (`not_measured`) met een `clay_dry_mass_balance_template`, en mass-balance-links in de OriginTrail-assertion-graph. Rood = geen merge.
