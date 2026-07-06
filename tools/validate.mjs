#!/usr/bin/env node
// validate.mjs — herhaalbare validatie van de ChemField-compositiedataset (issue #7).
// Vervangt de handmatige jq/JS-checks. Geen deps (node-builtin). Leest alleen; wijzigt niets.
//
//   node tools/validate.mjs      →  exit 0 groen, exit 1 met leesbare fouten
import { readFileSync, existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const COMP = join(ROOT, "data", "chemfield-compositions.json");

const errors = [];
const fail = (m) => errors.push(m);
const CID_RE = /^sha256:[0-9a-f]{64}$/;
const ualFromCid = (cid) => `did:dkg:knitweb/sha256-${cid.replace(/^sha256:/, "")}`;

// ── laad ────────────────────────────────────────────────────────────────────
let comp;
try {
  comp = JSON.parse(readFileSync(COMP, "utf8"));
} catch (e) {
  console.error(`✗ data/chemfield-compositions.json: ongeldige JSON — ${e.message}`);
  process.exit(1);
}

// ── AC1 · syntax + invarianten (cid/ual-vorm + consistentie + referenties) ──
const ENTITY_LISTS = ["sources", "materials", "records", "variables", "comparisons", "massBalances"];
const ids = new Set();
for (const cid of [comp.cid]) {
  if (!CID_RE.test(comp.cid)) fail(`root cid heeft verkeerde vorm: ${comp.cid}`);
  if (comp.ual !== ualFromCid(comp.cid)) fail(`root ual leidt niet af uit cid: ${comp.ual}`);
}
for (const list of ENTITY_LISTS) {
  for (const [i, e] of (comp[list] || []).entries()) {
    const at = `${list}[${i}] (${e.id ?? "?"})`;
    if (!e.cid || !CID_RE.test(e.cid)) fail(`${at}: cid ontbreekt/verkeerde vorm`);
    else if (e.ual !== ualFromCid(e.cid)) fail(`${at}: ual leidt niet af uit cid`);
    if (e.id) {
      if (ids.has(e.id)) fail(`${at}: dubbele id ${e.id}`);
      ids.add(e.id);
    }
  }
}
// referentiele integriteit: elke massBalance.recordId verwijst naar een bestaand record
const recordIds = new Set((comp.records || []).map((r) => r.id));
for (const mb of comp.massBalances || []) {
  if (!recordIds.has(mb.recordId)) fail(`massBalance ${mb.id}: recordId ${mb.recordId} bestaat niet`);
}

// ── AC2 · alias-pointerbestanden wijzen naar de huidige root-CID/UAL ────────
for (const a of comp.aliases || []) {
  const file = join(ROOT, `${a.alias}.json`);
  if (!existsSync(file)) { fail(`alias "${a.alias}": pointerbestand ${a.alias}.json ontbreekt`); continue; }
  let ptr;
  try { ptr = JSON.parse(readFileSync(file, "utf8")); }
  catch (e) { fail(`${a.alias}.json: ongeldige JSON — ${e.message}`); continue; }
  if (ptr.targetCid !== comp.cid) fail(`${a.alias}.json: targetCid ${ptr.targetCid} ≠ root cid ${comp.cid}`);
  if (ptr.targetUal !== comp.ual) fail(`${a.alias}.json: targetUal ≠ root ual`);
}

// ── AC3 · elk clay-record heeft een mass-balance-template en blijft locked ──
const clay = (comp.records || []).filter(
  (r) => r.recordType === "sampling_target_pending_lab_measurement" || /:nh-clay:/.test(r.id || ""),
);
if (clay.length === 0) fail("geen clay-records gevonden — verwacht Noord-Holland sampling targets");
const mbByRecord = new Map((comp.massBalances || []).map((m) => [m.recordId, m]));
for (const r of clay) {
  const mb = mbByRecord.get(r.id);
  if (!mb) { fail(`clay-record ${r.id}: mist mass-balance-template`); continue; }
  if (mb.kind !== "clay_dry_mass_balance_template")
    fail(`clay-record ${r.id}: mass-balance ${mb.id} is geen clay_dry_mass_balance_template (kind=${mb.kind})`);
  if (mb.status !== "structural_mass_balance_pending_lab_composition")
    fail(`clay mass-balance ${mb.id}: status niet 'pending' (${mb.status})`);
  // locked tot gemeten chemie is aangehecht (#6): mag niet als 'measured' gemarkeerd zijn
  if (r.measurementStatus !== "not_measured_in_attached_source")
    fail(`clay-record ${r.id}: measurementStatus moet locked blijven (kreeg ${r.measurementStatus})`);
}
// factPolicy moet de clay-lock-regel expliciet vastleggen
if (!comp.factPolicy || !/not marked measured/i.test(comp.factPolicy.clayChemistryRule || ""))
  fail("factPolicy.clayChemistryRule ontbreekt of legt de clay-lock niet vast");

// ── AC4 · OriginTrail-assertion-graph bevat mass-balance-links ─────────────
const graph = comp["@graph"] || [];
const MB_PREDS = ["chemfield:hasMassBalance", "chemfield:hasClayMassBalance", "chemfield:hasBofReferenceMassBalance"];
const mbObjects = new Set(graph.filter((t) => MB_PREDS.includes(t.predicate)).map((t) => t.object));
if (mbObjects.size === 0) fail("@graph bevat geen mass-balance-links (chemfield:hasMassBalance …)");
for (const mb of comp.massBalances || []) {
  if (!mbObjects.has(mb.id) && !mbObjects.has(mb.cid))
    fail(`massBalance ${mb.id} is niet gelinkt in de assertion-graph (@graph)`);
}

// ── rapport ─────────────────────────────────────────────────────────────────
if (errors.length) {
  console.error(`✗ dataset-validatie: ${errors.length} fout(en)\n` + errors.map((e) => `  - ${e}`).join("\n"));
  process.exit(1);
}
console.log(
  `✓ dataset-validatie ok — ${comp.records.length} records (${clay.length} clay locked), ` +
  `${comp.massBalances.length} mass-balances, ${(comp.aliases || []).length} aliases, ` +
  `${graph.length} assertion-triples. root ${comp.cid}`,
);
