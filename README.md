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
