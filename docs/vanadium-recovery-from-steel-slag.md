# Vanadium recovery from steel slag — the real process

Reference flowsheet behind the **Slag Run** game. Every game mechanic maps to a
real unit operation; this document is the ground truth so the game teaches the
actual hydrometallurgy rather than invented steps. Chromium safety is treated as
a first-class concern throughout.

> Scope: BOF/LD converter steel slag and vanadiferous slags (the Dutch
> Tata Steel IJmuiden / SmartSlag / VANELEX context). Vanadium in fresh steel
> slag is typically **~1–2 wt% as V₂O₅**, locked in spinel/oxide phases as
> V(III), which is **not** directly leachable — it must first be oxidised to
> soluble V(V). Vanadium is an EU/US critical raw material.

---

## Flowsheet at a glance

```
 steel slag
   │  1. comminution (crush + mill)            → liberate V-bearing phases
   ▼
 sized feed
   │  2. roast/activation (oxidise V(III)→V(V))
   │       ├─ salt (sodium) roast   Na₂CO₃/NaCl, 750–850 °C → water-soluble NaVO₃
   │       └─ calcification roast    CaO/CaCO₃,   ~850 °C    → Ca-vanadate (acid-leach)
   ▼
 activated feed
   │  3. leaching                              → pregnant V solution
   │       ├─ water leach (after Na roast)
   │       ├─ acid leach (H₂SO₄)
   │       ├─ alkaline leach (NaOH, high-Ca slags)
   │       └─ pressure / autoclave leach (higher T/P, faster, higher recovery)
   ▼
 pregnant leach solution (PLS)  ── + Cr(VI) hazard to manage
   │  4. purification / separation            → clean V solution
   │       ├─ Fe/Si/P/Al removal (pH, precipitation, settling)
   │       ├─ solvent extraction (amines / D2EHPA) — selective V, separates Cr
   │       └─ ion exchange (anion resins for vanadate)
   ▼
 purified vanadate
   │  5. precipitation                         → ammonium (poly)vanadate
   │       NH₄⁺ addition → NH₄VO₃ (AMV) / APV "red cake"
   ▼
 AMV / APV
   │  6. calcination (~450–550 °C)             → V₂O₅ "black flake" (product)
   ▼
 V₂O₅  ──► 7. electrolyte: dissolve in H₂SO₄, reduce to V³·⁵⁺ → VRFB electrolyte
            (this is the Speciation Quest redox ladder)
```

Leach residue (Ca/Fe/Si-rich) is valorised to cement/aggregate — the circular
tail of the process.

---

## 1. Comminution

Crushing and milling liberate the fine V-bearing spinel phases and create
surface area. **Two levers the game models directly:**

- **Recovery ∝ fineness** — more exposed surface leaches more V.
- **Leach time ∝ particle size** — dissolution is surface-controlled, so coarse
  feed leaches far slower. The game uses *1 week per 0.1 mm at 20 °C*.

Equipment ladder: hand breakage → hammer mill (~mm) → ball mill (sub-mm, with
grinding media). Trade-off: capital + grinding energy vs. downstream leach speed
and recovery.

## 2. Roasting / activation — oxidise V(III) → V(V)

The key chemical unlock. Fresh-slag vanadium is V(III) in spinel and insoluble;
oxidative roasting converts it to soluble V(V):

- **Salt (sodium) roast** — with Na₂CO₃ / Na₂SO₄ / NaCl in air at 750–850 °C:
  `V₂O₃ + Na₂CO₃ + O₂ → 2 NaVO₃ + CO₂`. Product is **water-soluble sodium
  metavanadate**. Cheap and classic, but NaCl variants release chlorine and the
  oxidising roast also mobilises **Cr(VI)** (hazard, §7).
- **Calcification roast** — with CaO/CaCO₃ at ~850 °C → calcium vanadates
  (Ca(VO₃)₂ / Ca₃(VO₄)₂), then recovered by acid leach. Na-free, lower emissions,
  favoured environmentally; needs an acid-leach step.
- **Salt-free / direct routes** — skip roasting via aggressive acid or alkaline
  **pressure** leaching (see §3, autoclave). Lower emissions, higher capital.

## 3. Leaching

Dissolve the activated vanadium into solution (the **PLS**, pregnant leach
solution). Rate and recovery depend on **particle size, temperature, reagent
concentration, liquid/solid ratio, and agitation** — all game levers.

- **Water leach** after sodium roast → NaVO₃ solution (simplest).
- **Acid leach** (H₂SO₄) — direct or post-calcification; also dissolves Fe, Ca,
  Mn (impurities to remove in §4).
- **Alkaline leach** (NaOH) — selective for V, leaves Fe/Ca in residue; good for
  high-Ca steel slags.
- **Pressure / autoclave leach** — elevated T (≈120–200 °C) and pressure sharply
  accelerate kinetics and lift recovery, and can leach directly without roasting.
  In the game this is the **€7000 autoclave**: a capital route that beats the
  fine-mill-plus-manual-agitation path on both time and recovery.

**Agitation.** Stirring/lifting renews the boundary layer and speeds dissolution.
The game models *manual lift-agitation* of the leach tank: it shortens leach
time and adds recovery, but sloshing of a flexible tank causes **leachate loss +
local contamination** — a real environmental trade-off (spill = cleanup +
reputation cost). Tank fill is limited by liftable weight (mass = fill volume ×
solution density, checked against player strength under gravity).

## 4. Purification / separation

Clean the PLS before making product:

- **Impurity removal** — Fe by pH adjustment/precipitation (goethite/jarosite),
  Si by settling/coagulation, P and Al by precipitation.
- **Solvent extraction (SX)** — extract vanadate with tertiary amines
  (e.g. Alamine 336) or D2EHPA from sulfate media; strip with ammonia/soda.
  This is also the main **V/Cr separation** step.
- **Ion exchange** — anion-exchange resins load vanadate; elute concentrated.

## 5. Precipitation

From the purified solution, add ammonium salts (NH₄Cl / (NH₄)₂SO₄) at controlled
pH and temperature to precipitate **ammonium metavanadate (NH₄VO₃, AMV)** or
**ammonium polyvanadate (APV, "red cake")**:
`VO₃⁻ + NH₄⁺ → NH₄VO₃↓`.

## 6. Calcination

Calcine AMV/APV at ~450–550 °C to drive off ammonia/water and form the product:
`2 NH₄VO₃ → V₂O₅ + 2 NH₃ + H₂O`. Output is **V₂O₅** ("black flake", ~98–99%+;
higher grades for battery use). This is the Slag Run end-product.

## 7. Chromium safety (cross-cutting)

Oxidative roasting/leaching can mobilise **Cr(VI)** — chromate/dichromate, toxic
and carcinogenic. Real plants must monitor Cr(VI), **reduce it to benign Cr(III)**
(with Fe(II) sulfate, sulfite, or other reductants) and separate/immobilise the
chromium. This is exactly the Speciation Quest **"Chroom onschadelijk maken"**
level (Cr(VI) → Cr(III) → Cr₂O₃), and a scored safety constraint in Slag Run.

## 8. Electrolyte production (hand-off to the Speciation Quest)

Dissolve V₂O₅ in sulfuric acid and reduce (chemically or electrochemically) to
the mixed-valence **V³·⁵⁺** electrolyte (equimolar V(III)/V(IV)) used in the
**vanadium redox flow battery (VRFB)**. Driving V down and up its oxidation
ladder is the Speciation Quest redox puzzle — Slag Run makes the V₂O₅ that feeds
it.

---

## Mechanic ↔ chemistry map

| Game mechanic | Real unit operation |
|---|---|
| Foraging / ordering ekoliet 0/8mm | Feedstock sourcing (path/bank slag; graded aggregate) |
| Mill tiers, output mm | Comminution / liberation |
| (planned) roasting stage | Salt / calcification roast — V(III)→V(V) activation |
| Recovery-by-size, time-by-size | Surface-controlled leach kinetics |
| Leach-tank volume + liftability | L/S ratio, batch size, vessel handling |
| Lift-agitation + sloshing loss/contamination | Agitation kinetics + spill/environmental cost |
| €7000 autoclave | Pressure/temperature (hydrothermal) leaching |
| (planned) SX / precipitation / calcination | Purification → AMV/APV → V₂O₅ |
| Cr(VI) handling / Speciation Quest L2 | Chromium reduction & separation (safety) |
| Speciation Quest redox ladder | V₂O₅ → VRFB electrolyte (V³·⁵⁺) |

## Sources & further reading

Grounded in the standard vanadium-extraction literature (sodium/calcification
roast–leach, SX, red-cake precipitation, calcination) and the ChemField KG
source catalog (`data/chemfield-kg-sources.json`): Materials Project (Pourbaix/
oxide thermo), PHREEQC (aqueous speciation / log K), COD & RRUFF (slag/mineral
structures), USGS MRDATA (vanadium resources). Numbers in the game are tuned for
play, not process design.
