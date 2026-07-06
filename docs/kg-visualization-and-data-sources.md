# 3D-visualiseerbare Knowledge Graphs met (mogelijk) chemische data — Geannoteerde lijst voor ChemField

> Research-referentie (2026-07-06). Achtergrond voor de ChemField 3D-graafvisualisatie
> (`species-graph.html` / `3d-force-graph`) en de externe-bronnen-catalogus
> (`data/chemfield-kg-sources.json`). Licentie-aandachtspunten per bron staan expliciet;
> houd graaf-*data* (eigen licenties) gescheiden van de Apache-2.0-*code*.

## TL;DR
- **Deel A**: De praktische kern voor 3D-graafvisualisatie is de open-source `3d-force-graph`-stack van Vasco Asturiano (three.js/WebGL, 2D/3D/VR/AR-bindings, leest JSON nodes/links); voor GPU-schaal is Graphistry (deels open source, PyGraphistry) de beste keuze, en Kineviz GraphXR de sterkste commerciële 3D/VR-graaftool met Neo4j-koppeling. Let op: Mol*/NGL zijn 3D-*moleculaire*-structuurviewers, geen knowledge-graph-viewers — dat is een fundamenteel onderscheid.
- **Deel B**: De meest waardevolle databronnen voor ChemFields hydrometallurgie/leaching/slak/vanadium-focus zijn de **Materials Project** (kristalstructuren, thermodynamica én Pourbaix/Eh-pH via API), **OPTIMADE** (federatief, 26.856.234 structuren over 27 bekende / 19 beschikbare providers), **MatKG** (70.000 entities / 5,4M triples uit literatuur), **Wikidata** (elementen/mineralen/verbindingen via SPARQL) en **PubChemRDF** (~80 miljard triples). Speciatiedata voor V/Cr zit vooral in tabulaire thermodynamische databases (PHREEQC, GEMS, FactSage), niet in graphs.
- **Belangrijke bevinding/gat**: Er bestaat géén dedicated hydrometallurgie-/leaching-knowledge-graph of V/Cr/slak-speciatie-KG. Dit is een reëel gat en een kans voor ChemField. Voor een eigen semantische laag zijn EMMO (CC BY 4.0, OWL/RDF; v1.0.0 feb 2025) + EMMO domain-electrochemistry + MSEO (MIT) de aangewezen ontologie-bouwstenen.

---

## Key Findings

1. **3D-graafvisualisatie ≠ 3D-molecuulvisualisatie.** De taak vraagt om het visualiseren van *knowledge graphs* (nodes+edges in force-directed/ruimtelijke layout). Tools als `3d-force-graph`, GraphXR en Graphistry doen dit. Mol*/NGL visualiseren daarentegen atoomcoördinaten van moleculen/eiwitten — nuttig voor ChemField's moleculaire data, maar het is geen graaf-relatie-viz. Beide categorieën zijn relevant maar dienen verschillende doelen.

2. **De open-source route is volwassen genoeg voor productie.** `3d-force-graph` + `d3-force-3d`/`ngraph`, react-force-graph en de VR/AR-varianten dekken interactieve 3D-exploratie volledig, en lezen simpel JSON (nodes/links). Voor grote graphs is `ngraph` de performante engine. Dit past bij een Apache-2.0-project (de bibliotheken zijn MIT).

3. **Voor chemie-relevante KG-data zijn er twee sterke families**: (a) *life-science RDF* (PubChemRDF, ChEBI, ChEMBL-RDF, Bio2RDF, Hetionet) — enorm maar biomedisch/organisch gericht; (b) *materials science* (Materials Project, OPTIMADE-federatie, COD, MatKG, JARVIS, OQMD, AFLOW, NOMAD) — direct relevanter voor anorganische/metallurgische chemie.

4. **The World Avatar (TWA)** is het meest ambitieuze chemie-KG-initiatief: een dynamische, cross-domein KG met chemie-ontologieën (OntoSpecies, OntoKin, OntoCompChem, OntoPESScan, OntoMOPs) plus stad-/energie-/procesdomeinen — zeer relevant als architectuurinspiratie voor ChemField's field/1-laag.

5. **Speciatie/thermodynamica voor leaching is tabulair, niet graaf-gestructureerd.** PHREEQC (public domain), GEMS/GEM-Selektor (GPL v3), FactSage (commercieel) bevatten de kern-thermodata voor V/Cr-speciatie, maar zijn geen KG's. De enige turnkey machine-toegankelijke V/Cr-redox/Pourbaix-bron is de Materials Project REST API + pymatgen.

---

## Deel A — 3D-visualisatietools voor knowledge graphs

### A1. Open-source / three.js-gebaseerd (de kern-aanrader)

**3d-force-graph (Vasturiano)** — Web-component die een graaf in 3D rendert met een force-directed layout; ThreeJS/WebGL voor rendering, `d3-force-3d` of `ngraph` als physics-engine. Er zijn parallelle varianten: 2D canvas (`force-graph`), VR (`3d-force-graph-vr`, A-Frame) en AR (`3d-force-graph-ar`, AR.js), plus React-bindings (`react-force-graph`). Leest data direct als JSON `{nodes:[{id,name,val}], links:[{source,target}]}` of via `jsonUrl`. Open source (MIT). Geschikt voor grote graphs via de `ngraph`-engine. URL: https://github.com/vasturiano/3d-force-graph . **Oordeel: de standaard-startkeuze voor ChemField.**

**three-forcegraph / d3-force-3d** — Onderliggende bouwstenen: `three-forcegraph` is de ThreeJS 3D-object-klasse; `d3-force-3d` doet de force-simulatie in 1D/2D/3D (velocity Verlet). Handig als je een eigen renderer bouwt. Open source. URL: https://github.com/vasturiano/d3-force-3d .

**Formaten inlezen**: Deze tools verwachten JSON nodes/links. RDF/Neo4j/GraphML/GEXF/CSV-edges moeten eerst worden omgezet (bv. SPARQL→JSON, of Cypher→JSON). Dat is een lichte ETL-stap.

### A2. GPU-versnelde en commerciële platforms

**Graphistry** — End-to-end GPU visuele graaf-analytics (NVIDIA RAPIDS/Apache Arrow). PyGraphistry (Python-client) is open source; laadt pandas/cuDF/Spark-dataframes, doet UMAP-embeddings, GFQL-graafquery, en visualiseert miljoenen edges. Rendering via Graphistry-server (Hub cloud of self-hosted). URL: https://github.com/graphistry/pygraphistry . **Oordeel: beste optie voor grote/dichte chemische graphs.**

**Kineviz GraphXR** — Web-based platform voor 2D/3D én VR graaf-analytics, nauw geïntegreerd met Neo4j (één-klik import). Leest graph/relationele DB's, CSV, JSON, 3rd-party API's. Prijsmodel (historisch): Explorer gratis, Analyst $70/maand/user, Enterprise op aanvraag. Gratis "GraphXR Lite" Docker-stack. Ondersteunt VR. URL: https://www.kineviz.com/graphxr . **Oordeel: sterkste commerciële 3D/VR-graaftool.**

**Cambridge Intelligence — KeyLines / ReGraph / KronoGraph** — WebGL/Canvas graaf-viz-SDK's; backend-agnostisch (Neo4j, Neptune, Gremlin, SPARQL/RDF, Cosmos DB, TigerGraph). Proprietary. Overwegend 2D/2.5D — niet primair 3D. URL: https://cambridge-intelligence.com/keylines/ .

**Linkurious / Ogma** — Ogma is een commerciële WebGL-first JS-library voor grootschalige graaf-viz; Neo4j/CSV/JSON-connectors. Commercieel. URL: https://doc.linkurious.com/ogma/latest/ .

**Tom Sawyer Perspectives/Explorations, Metaphacts** — Tom Sawyer: low-code graaf-viz+analyse. Metaphacts: open platform (metaphactory, RDF-georiënteerd). Beide commercieel/enterprise.

### A3. Neo4j-ecosysteem

**Neo4j Bloom / NeoDash / yFiles** — Bloom is de officiële viz-tool (overwegend 2D). NeoDash is open-source dashboard. yFiles (commercieel) is een krachtige diagram-/graaf-library. Voor echte 3D binnen Neo4j is GraphXR (A2) de route.

### A4. Klassieke netwerk-tools (grotendeels 2D)

**Gephi** (open, primair 2D; GEXF/GraphML/CSV) · **Sigma.js** (JS, grote graphs, 2D WebGL) · **Cytoscape / Cytoscape.js** (open; biologische netwerken / JS-toolkit, 2D).

### A5. Chemie-specifiek: 3D-moleculaire structuur (GEEN knowledge-graph-viz)

**Mol\* (Mol-star) en NGL Viewer** — Web-native 3D-viewers voor macromoleculaire/moleculaire *structuren* (atoomcoördinaten, cryo-EM, MD). Mol* combineert LiteMol (PDBe) en NGL (RCSB PDB); open source. **Onderscheid**: dit visualiseert de 3D-geometrie van *één molecuul*, NIET een kennisnetwerk. Complementair aan `3d-force-graph`/GraphXR. URL: https://molstar.org/ .

### A6. Embedding-visualisatie als "3D graph"-alternatief

**TensorFlow Embedding Projector + PyKEEN/pykg2vec** — Train knowledge-graph-embeddings (TransE, RotatE, DistMult, ComplEx via PyKEEN — 40 modellen, 37 datasets) en projecteer met UMAP/t-SNE/PCA naar 3D. Toont *semantische clustering* i.p.v. expliciete edges. PyKEEN open source (Python). Graphistry doet UMAP ingebouwd. **Oordeel: waardevol voor V/Cr-speciatie- of materiaal-similariteit.**

### Tabel A — 3D/graaf-visualisatietools

| Tool | Open/commercieel | 3D/VR | Formaten | Grote graphs | ChemField-relevantie |
|---|---|---|---|---|---|
| 3d-force-graph (Vasturiano) | Open (MIT) | 3D + VR + AR | JSON nodes/links | ja (ngraph) | Hoog — startkeuze |
| Graphistry / PyGraphistry | Deels open (client) | 3D-achtig, GPU | dataframes, CSV | ja (miljoenen edges) | Hoog — schaal |
| Kineviz GraphXR | Commercieel (gratis tier) | 3D + VR | Neo4j, CSV, JSON, API | ja | Hoog — VR/Neo4j |
| KeyLines/ReGraph | Commercieel | 2D/2.5D | Neo4j, Neptune, RDF/SPARQL | ja | Midden |
| Ogma/Linkurious | Commercieel | 2D (WebGL) | Neo4j, CSV, JSON | ja | Midden |
| Neo4j Bloom | Commercieel | 2D | Neo4j | ja | Midden |
| Gephi | Open | 2D (3D beperkt) | GEXF, GraphML, CSV | midden | Laag-midden |
| Cytoscape.js / Sigma.js | Open | 2D | JSON, diverse | midden-ja | Midden |
| Mol* / NGL | Open | 3D moleculair | PDB, mmCIF, SDF | n.v.t. | Hoog (maar molecuulviz, geen KG) |
| Embedding Projector + PyKEEN | Open | 3D (t-SNE/UMAP) | TSV/vectors | ja | Midden-hoog |

---

## Deel B — Knowledge graphs / gelinkte datasets met (mogelijk) chemische data

### B1. Algemene/encyclopedische KG's met chemie

**Wikidata** — Collaboratieve KG; chemische elementen (P246, P1086), verbindingen (Q11173), mineralen, identifiers (CAS P231, InChIKey P235, PubChem CID P662, ChemSpider P661). Toegang: publiek SPARQL-endpoint (https://query.wikidata.org/sparql), REST, RDF-dumps. Licentie: **CC0** — ideaal voor Apache-2.0-hergebruik. 3D via SPARQL→JSON→force-graph. **Relevantie: midden-hoog** (backbone elementen/mineralen; ondiep voor procesdetails).

**DBpedia / YAGO** — RDF-KG's uit Wikipedia; chemie met beperkte diepte. CC BY-SA. Relevantie: laag-midden.

**ConceptNet / BabelNet** — Algemene semantische netwerken; chemie oppervlakkig. Relevantie: laag.

### B2. Chemie-specifieke RDF/linked-data KG's

**PubChemRDF (NIH)** — RDF van PubChem. Omvang: ~80 miljard triples (V1.6.3 beta, ~13 TB). Toegang: FTP, triplestore, REST (SPARQL via IDSM/ChemWebRDF). Open (NIH). **Relevantie: midden** (organisch/bioassay-gericht).

**ChEBI** — Open ontologie van "chemical entities of biological interest". >195.000 entries; is_a/has_role/has_functional_parent. OWL/OBO, EBI SPARQL, REST. **CC BY 4.0**. **Relevantie: midden** (classificatie/rollen).

**ChEMBL-RDF** — Bioactieve moleculen, ~539M triples (r27). CC BY-SA. Laag-midden.

**Bio2RDF** — ~35 life-science datasets, ~11 miljard triples. Open. Laag-midden.

**The World Avatar (TWA) / J-Park Simulator** — Dynamische cross-domein KG met agents. Chemie-ontologieën: OntoSpecies, OntoKin, OntoCompChem, OntoPESScan, OntoMOPs, OntoChemExp; plus OntoCityGML/OntoCAPE/OntoEIP/OntoPowerSys. Query-interface "Marie". **Relevantie: hoog (architectuurinspiratie)** voor field/1 (agents + cross-domein + content-linking). URL: https://theworldavatar.io .

**Nanopublications** — Kleine citeerbare RDF-asserties met provenance. **Relevantie: midden** — inspiratie voor content-addressed verifieerbare mini-graphs (field/1).

**Open PHACTS** — Drug-discovery linked-data (IMI); live platform niet meer volledig operationeel. Laag (historisch).

**Commercieel: CAS / SciFinder / Reaxys / SciBite** — Reacties/stoffen/ontologieën; commercieel/licentie sluit Apache-2.0-hergebruik uit. CAS Common Chemistry is een kleine open subset (CC BY-NC 4.0).

### B3. Materials science & vaste stof (hoog relevant voor slak/metallurgie)

**Materials Project** — Open DB van berekende materiaal-eigenschappen. REST API (mp-api/pymatgen), AWS Open Data. **CC BY 4.0** (GNoME-subset **BY-NC**). **Cruciaal: `MPRester.get_pourbaix_entries()` levert Eh-pH/Pourbaix voor V, Cr** (DFT-vaste-stof + experimentele aqueuze-ion-vrije energieën, pH 0-14). **Relevantie: HOOG** — belangrijkste turnkey V/Cr-redoxspeciatie + slak-oxiden.

**OPTIMADE** — Federatieve REST-standaard over meerdere DB's. Omvang: 26.856.234 structuren over 27 bekende / 19 beschikbare providers (AFLOW, MP, OQMD, COD, JARVIS, NOMAD, Materials Cloud, Alexandria). Open. **Relevantie: HOOG** — één toegangspunt voor anorganische structuren. URL: https://www.optimade.org/ .

**Crystallography Open Database (COD)** — Open kristalstructuren. 533.828 entries. Web/REST/OPTIMADE/dumps. **CC0**. **Relevantie: hoog** (mineralen/metaal-oxiden). 3D via Mol*.

**MatKG / MatKG-2** — Grootste materials-science KG uit literatuur (MatBERT). >70.000 entities, 5,4M triples. CSV+RDF, linkt naar Wikidata/DBpedia/MP. Open (CC). DOI 10.1038/s41597-024-03039-z. **Relevantie: HOOG** — direct te 3D-visualiseren (RDF→JSON→force-graph), filterbaar op "leaching"/"vanadium"/"slag".

**NOMAD, AFLOW, OQMD, JARVIS-DFT (NIST), Materials Cloud** — Grote DFT-databases; REST + OPTIMADE; grotendeels open (CC BY). **Relevantie: midden-hoog** (thermo/stabiliteit anorganische fasen).

**ICSD** — Commercieel (FIZ Karlsruhe); zeer volledig, maar sluit open hergebruik uit. Hoog qua inhoud, laag qua toegankelijkheid.

**Matscholar / Mat2Vec / Propnet** — Text-mined materials-kennis + eigenschappen-relatie-netwerk. Open. Midden (inspiratie).

### B4. Reacties, thermodynamica, hydrometallurgie/proceschemie

**Open Reaction Database (ORD)** — Open schema+repo voor organische reactiedata (Protocol Buffers; SMILES/SMARTS). Data CC-BY-SA, code Apache 2.0. **Relevantie: laag-midden** (organisch; schema-inspiratie). URL: https://open-reaction-database.org/ .

**Thermodynamische/speciatie-databases (TABULAIR, geen KG's — maar cruciaal voor leaching)**:
- **PHREEQC (USGS)** — speciatie, batch-reactie, reactief transport. Databases als plain-text `.dat` (llnl.dat, minteq.v4.dat, wateq4f.dat, phreeqc.dat, pitzer.dat, sit.dat). **Public domain** (USGS); R-package `phreeqc`. **Relevantie: HOOG voor leaching-speciatie**, tabulair.
- **GEMS / GEM-Selektor (PSI)** — Gibbs-energy-minimalisatie; PSI-Nagra TDB + Cemdata. GUI **GPL v3** (v3.6.0+); GEMS3K-solver op GitHub; Python via xGEMS. **Relevantie: HOOG voor slak/leaching-thermodynamica**, tabulair.
- **FactSage / FACT** — Grootste geïntegreerde thermochemie (FactPS, FToxid voor slakken, FSstel, FTsalt); EpH (Pourbaix)/Predom. Expliciet toegepast op hydrometallurgie/slak. **Commercieel**. **Relevantie: HOOG qua inhoud (slak!), maar commercieel en tabulair.**

**Mineralogie/geochemie**: **Mindat.org** (grootste mineralen-DB, API), **RRUFF** (Raman/XRD/chemie; open), **AMCSD**, **Raman Open Database (ROD)** (gekoppeld aan COD). **Relevantie: midden-hoog** (mineralogie van ertsen/slak).

**Geoscience/mining KG's**: **USGS MRDATA** (MRDS mineraalvoorkomens, USMIN, geochemie) — geospatiaal/tabulair; academische KG-constructies bestaan (bv. porphyry-copper-deposit KG in Neo4j). **Relevantie: midden** (critical raw materials).

### B5. Biomedische/life-science KG's die chemie bevatten (voor volledigheid)

**Hetionet** — Biomedische KG (Neo4j). 47.031 entities (11 types, incl. compound) / 2.250.197 edges (24 types), Himmelstein et al., eLife 2017, DOI 10.7554/eLife.26726. Publiek Neo4j + JSON/TSV. **CC0**. **Relevantie: laag** (drug repurposing), maar exemplarisch voor KG-bouw.

**PrimeKG, PharMeBINet, CKG, SPOKE, OpenBioLink, PubMed KG, BIKG, KEGG, Reactome, UniChem** — bevatten compound/drug-nodes; licentie variabel. **Relevantie: laag-midden** (biomedisch gekaderd).

### Tabel B — Chemie-relevante knowledge graphs (kernselectie)

| Bron | Type chemie | Omvang | Toegang | Licentie | ChemField-relevantie | 3D-viz |
|---|---|---|---|---|---|---|
| Materials Project | Kristalstructuren, thermo, Pourbaix V/Cr | 200k+ materialen | REST API, AWS, pymatgen | CC BY 4.0 (GNoME: BY-NC) | **Hoog** | via pymatgen/Mol*; eigen graaf |
| OPTIMADE (federatie) | Anorg. structuren | 26.856.234 structuren, 27/19 providers | Uniforme REST | Open | **Hoog** | na query→graaf |
| MatKG | Materiaal-eigenschap-proces | 70k entities / 5,4M triples | Download (RDF/CSV) | Open (CC) | **Hoog** | RDF→JSON→force-graph |
| COD | Kristalstructuren, mineralen | 533.828 entries | REST, OPTIMADE, dumps | CC0 | Hoog | structuren via Mol* |
| Wikidata | Elementen, mineralen, verbindingen | miljoenen items | SPARQL, dumps | CC0 | Midden-hoog | SPARQL→force-graph |
| PubChemRDF | Verbindingen, bioassays | ~80 miljard triples | FTP, triplestore, REST | Open (NIH) | Midden | subset→graaf |
| The World Avatar | Species, kinetiek, kwantumchemie | cross-domein KG | SPARQL, agents | Open | **Hoog (architectuur)** | linked-data→graaf |
| ChEBI | Chem. entiteiten, rollen | >195.000 entries | SPARQL, OWL, REST | CC BY 4.0 | Midden | ontologie→force-graph |
| RRUFF / ROD | Mineralen, Raman/XRD | duizenden mineralen | Web, download | Open | Midden-hoog | structuren via Mol* |
| USGS MRDATA | Ertsen, mineraalvoorkomens | wereldwijd | Download, WMS | Open (US gov) | Midden | zelf tot graaf bouwen |
| Hetionet | Compounds/drugs | 47.031 nodes / 2,25M edges | Neo4j, JSON | CC0 | Laag | Neo4j→GraphXR |
| PHREEQC/GEMS/FactSage | Speciatie/thermo (V/Cr, slak) | n.v.t. (tabulair) | .dat/API/commercieel | PD / GPL / commercieel | **Hoog (data), geen KG** | n.v.t. |

---

## Aanvullende analyse voor ChemField

### Meest waardevolle 3-5 bronnen (hydrometallurgie/leaching/slak/V/Cr)

1. **Materials Project** — Enige turnkey machine-toegankelijke bron voor V/Cr-Pourbaix/Eh-pH-speciatie én slak-oxide-thermodynamica; open (CC BY 4.0), pymatgen. Hoogste prioriteit.
2. **OPTIMADE-federatie** — Eén API voor 26,86M anorganische structuren over AFLOW/OQMD/COD/JARVIS/NOMAD. Breedte + open.
3. **MatKG** — Relatie-netwerk uit literatuur (5,4M triples); direct te 3D-visualiseren en te filteren op "leaching"/"vanadium"/"slag".
4. **PHREEQC + GEMS** (evt. FactSage) — De feitelijke leaching-/slak-speciatie-thermodynamica. Tabulair → te wrappen als field/1-graaf-nodes (species, fasen, reacties, log K).
5. **COD + RRUFF** — Open mineralogie/kristalstructuren van ertsen/slak-mineralen; CC0/open, 3D via Mol*.

### Praktisch pad: inladen → filteren → 3D-visualiseren

1. **Materials Project → Pourbaix-graaf**: `pip install mp-api pymatgen`; `MPRester.get_pourbaix_entries(["V"])` (of "Cr"); node-per-species + edges naar elementen/fasen; exporteer JSON `{nodes,links}`; render in `3d-force-graph`. Kleur op oxidatietoestand.
2. **MatKG → thematische subgraaf**: download RDF/CSV; filter op "vanadium"/"chromium"/"slag"/"leaching"; converteer naar force-graph-JSON. Grote subgraphs → Graphistry (UMAP).
3. **Wikidata → mineralen/metalen backbone**: SPARQL (elementen + mineralen met formule) → JSON → force-graph als referentie-skelet.
4. **Tool-keuze**: begin met `3d-force-graph` (JSON) voor MVP; schaal naar Graphistry (GPU) bij >50k edges; GraphXR voor VR-demo's.

### Licentie-aandachtspunten (Apache 2.0-project)

- **Veilig te hergebruiken**: CC0 (Wikidata, COD, Hetionet), publiek domein (PubChemRDF/NIH, PHREEQC/USGS), CC BY 4.0 (Materials Project non-GNoME, ChEBI) — mits attributie. Apache 2.0 is compatibel met CC BY.
- **Let op share-alike**: CC BY-SA (DBpedia, ChEMBL-RDF, ORD-data) legt copyleft op afgeleide *data* — houd gescheiden van Apache-2.0-code.
- **Niet-commercieel/gesloten**: GNoME-subset (CC BY-NC), CAS/Reaxys/SciFinder/ICSD/FactSage (commercieel) — niet distribueren.
- **GPL**: GEM-Selektor GUI (GPL v3) — de *software* is GPL; roep het als los proces aan. Thermodata apart beoordelen.
- **Code vs. data**: Houd graaf-*data* (eigen licenties) strikt gescheiden van ChemField's Apache-2.0-*code*; documenteer per bron de licentie in metadata (zie `data/chemfield-kg-sources.json`).

### Aansluiting op een eigen field/1-graaf-datalaag (P2P/Plexus)

- **Formaat**: Modelleer records als kleine, zelfbeschrijvende RDF-achtige/JSON-LD-fragmenten (subject–predicate–object), geïnspireerd op **Nanopublications** (assertie + provenance) en **The World Avatar** (cross-domein ontologieën + agents). Elk field/1-record = een mini-graaf met eigen ID.
- **Content-addressing**: Gebruik content-hashes (CID's) als node-ID's; verwijs naar externe KG-nodes via canonieke IRI's (Wikidata Q-ID, MP mp-id, PubChem CID, ChEBI-ID, InChIKey). InChIKey is krachtig als content-addressed chemische identifier.
- **Externe KG-nodes refereren**: `owl:sameAs`/`skos:exactMatch`-links naar Wikidata/MP/PubChem — ChemField wordt een overlay bovenop bestaande open KG's zonder duplicatie.
- **Visualisatie**: field/1 is al nodes+edges → `3d-force-graph` sluit direct aan; externe gerefereerde nodes lazy-loaden.
- **EMMO als semantische ruggengraat**: EMMO (CC BY 4.0, OWL/RDF; v1.0.0 feb 2025; w3id.org/emmo) + EMMO domain-electrochemistry om field/1-termen (species, fase, proces, eigenschap) consistent te typeren; MSEO (MIT) voor experiment-metadata.

## Recommendations (gefaseerd)

**Fase 1 (MVP, weken):** `3d-force-graph`-prototype dat (a) een V- en Cr-Pourbaix-graaf uit Materials Project (pymatgen) en (b) een gefilterde MatKG-subgraaf toont. Benchmark: >5.000 nodes vloeiend in de browser. Drempel: >50k edges of <30 fps → Graphistry (GPU).

**Fase 2 (data-integratie):** Wrap PHREEQC/GEMS-thermodata (species, fasen, log K, reacties) als field/1-nodes met InChIKey/formule-ID's en `sameAs`-links naar Wikidata/MP/PubChem. Voeg COD/RRUFF-mineraalstructuren toe (Mol*-embed per node). Benchmark: elke leaching-species linkt aan ≥1 externe open-KG-node.

**Fase 3 (semantiek + demo):** EMMO + domain-electrochemistry als typering; GraphXR- of WebXR-demo voor VR. Overweeg PyKEEN-embeddings (RotatE) + Embedding Projector voor V/Cr-similariteit.

**Wat de aanpak zou veranderen:** Verschijnt er een dedicated hydrometallurgie-KG (nu afwezig) → prioriteer integratie. Budget voor FactSage/ICSD → voeg commerciële slak-thermodynamica toe, maar isoleer wegens licentie. Wordt de graaf voornamelijk moleculair → verschuif naar Mol*-centrische viz.

## Caveats
- **Speciatie-data is tabulair, geen KG.** PHREEQC/GEMS/FactSage → omzetten naar graaf; er bestaat geen kant-en-klare hydrometallurgie-KG. Grootste inhoudelijke gat (en kans).
- **"3D" bij veel commerciële tools is beperkt.** KeyLines/ReGraph/Ogma/Neo4j Bloom zijn overwegend 2D/2.5D; echte 3D: `3d-force-graph`, Graphistry, GraphXR.
- **Mol*/NGL zijn geen KG-viewers.** Verwar moleculaire structuur-3D niet met kennisgraaf-3D.
- **Omvangscijfers zijn momentopnamen per release** (PubChemRDF ~80 mld triples, COD 533.828 entries, OPTIMADE 26.856.234 structuren) — verifieer bij implementatie. Het exacte OntoSpecies-species-aantal is niet consistent gedocumenteerd.
- **Licenties variëren sterk**; GNoME (BY-NC), CAS/Reaxys/ICSD/FactSage (commercieel) en share-alike-bronnen vergen zorgvuldige scheiding van Apache-2.0-code.
- **The World Avatar** is krachtig maar complex; meerwaarde vooral in architectuur-inspiratie, niet kant-en-klare hydrometallurgie-data.
