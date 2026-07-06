# Slag Run — game design script

The full design for **Slag Run**, the resource-management / light-RPG game where
a player recovers vanadium from real steel slag and refines it toward VRFB
electrolyte. It is the *upstream* of the **Speciation Quest** (the redox puzzle).
Every mechanic maps to a real unit operation in
[`vanadium-recovery-from-steel-slag.md`](vanadium-recovery-from-steel-slag.md).

Status tags: **[v1]** shipped in `slag-run.html`; **[backlog]** specced here and
tracked as issues, config keys already present in `data/production-chain.json`.

---

## 1. Vision & core loop

You are a steel-slag researcher turning industrial waste into battery-grade
vanadium. The loop:

```
apply for research budget → acquire slag → comminute → (roast) → leach
   → purify → precipitate → calcine → V₂O₅ → refine in the Speciation Quest
```

Every action costs **game-days** (1 week = 1 day) and often **money** or
**physical effort**; smart researchers trade capital against time and labour.

## 2. Player state

| Stat | Meaning | Grows / shrinks by |
|---|---|---|
| **Speeldag** | Elapsed game-days (1 week each) | Every action that takes time |
| **Budget €** | Cash from the state grant + sales | Grant, purchases |
| **Kracht** (strength / muscle mass) **[v1]** | Physical capacity; gates lifting | +labour: dig, haul, hammer, lift |
| **Reputatie / vervuiling [backlog]** | Environmental standing | −spills/contamination; cleanup restores |
| **V₂O₅** | Product accumulated | Leach → (purify → calcine) |

### Strength / muscle progression **[v1 partial]**
Repeated **physical labour builds muscle mass**: digging slag from the
Amsterdamse Bos paths, hauling it off the Zeeland bank, hand-hammering, and
lifting/agitating leach tanks each add `strengthPerLabourAction`. Strength then
**gates what you can lift** (§4). Early game you are weak → small tanks / can't
agitate big batches; grind and haul enough and you unlock heavier handling.
Mechanised routes (mills, autoclave) bypass labour but cost capital.

### Gravity & human-strength model **[backlog]**
A filled tank's mass = `emptyTankMass + fill_litres × density`, where slag bulk
density ≈ 1.8 kg/L and leach solution ≈ 1.15 kg/L (`physics` block). The player
can lift it only if **strength ≥ filled mass** (with `gravity = 9.81 m/s²` used
for the effort/energy readout). This turns the abstract "kracht" stat into a
concrete physics check on every manual handling action.

## 3. Stages

### Stage 1 — Research budget **[v1]**
Apply to the state (Big Chemistry / Oost-NL flavour). Award takes **4 weeks = 4
game-days**, then grants €3000. Unlocks ordering graded **ekoliet** feedstock.
You may skip it and forage for free immediately (slower, more labour).

### Stage 2 — Acquire feedstock **[v1]**
- **Order ekoliet 0/8mm** (needs budget): 12.5 kg buckets, €45 each, 2-day
  delivery, consistent V grade. Pre-graded 0–8 mm → less milling.
- **Forage Amsterdamse Bos (paths)**: free, 1-day trip, 3×5 kg, ~16 mm, **digging
  builds muscle**.
- **Forage Zeeland (Oosterschelde bank)**: free, 3-day trip, 6×5 kg, ~24 mm,
  **hauling builds muscle**. More material but coarser & farther.

### Stage 3 — Comminution **[v1]**
| Equipment | Cost | Output | Days/bucket | Note |
|---|---|---|---|---|
| Hand hammer | €0 | 8 mm | 1.5 | free, slow, **builds muscle** |
| Hammer mill | €2000 | 2 mm | 0.25 | fast |
| Ball mill + V/Cr media | €200 + €500 | 0.1 mm | 1.0 | finest; dear media |
| Large hammer mill **[tier 2]** | €6000 | 2 mm | 0.1 | high throughput |
| Large ball mill **[tier 2]** | €10000 | 0.1 mm | 0.4 | fine + fast |

Finer output → higher recovery **and** much shorter leach (§4).

### Stage 4 — Roasting / activation **[backlog]**
Fresh-slag V(III) is insoluble; an oxidative **roast** (salt or calcification,
750–850 °C) converts it to soluble V(V) before leaching. Ekoliet may arrive
partly weathered/activated; fresh forage needs roasting for good recovery. Roast
mobilises **Cr(VI)** → feeds the safety mechanic (§7). *Design:* a roaster
purchase + per-batch fuel/time cost; roasting multiplies achievable recovery.

### Stage 5 — Leaching: vessel, volume & agitation **[v1 core; tank/agitation backlog]**
Dissolve V into the pregnant leach solution. **Recovery rises with fineness;
leach time = coarsest particle size ÷ 0.1 mm days at 20 °C** (0.1 mm → 1 day;
2 mm → 20 days; 8 mm → 80 days). **[v1]**

**Leach tanks [backlog].** Two flexible-plastic vessels:
- **Platte loogbak 80 L** — 100×60×20 cm. High capacity, but above **40 L fill**
  it is too heavy/floppy to lift → no manual agitation.
- **Bak 40 L** — 50×40×40 cm. Full 40 L still liftable.

**Manual lift-agitation [backlog].** Lifting/rocking the tank renews the
boundary layer: `×0.7` leach time and `+0.05` recovery — but a flexible tank
**sloshes**: ~3% leachate loss **and** local **contamination** (+cleanup cost /
−reputation) per agitation. Liftability is gated by fill volume **and** strength
vs. filled mass (§2 physics). So: small tank = agitate freely but low throughput;
big tank = high throughput but no agitation unless split into liftable batches.

**Autoclave route [backlog].** The **€7000 autoclave** does pressure/temperature
leaching: recovery floor ~0.9 and ~1 day/batch with **no manual agitation and no
spill** — a capital alternative to the fine-mill-plus-lift path.

### Stage 6 — Purification / separation **[backlog]**
Remove Fe/Si/P/Al; **solvent extraction** (amines / D2EHPA) or ion exchange to
concentrate V and **separate Cr**. Purity gates the grade (and price) of the
final V₂O₅.

### Stage 7 — Precipitation → calcination **[backlog]**
Add ammonium salts → **AMV/APV ("red cake")**; calcine ~450–550 °C → **V₂O₅**
black flake. Grade depends on purification quality.

### Stage 8 — Electrolyte → Speciation Quest **[v1 hand-off]**
V₂O₅ dissolved in H₂SO₄ and reduced to the V³·⁵⁺ VRFB electrolyte — the redox
ladder of the **Speciation Quest**. Slag Run passes its V₂O₅ yield forward.

## 7. Chromium safety **[backlog]**
Oxidative roast/leach can mobilise toxic **Cr(VI)**. Managing it (reduce to
Cr(III), separate) is a scored safety constraint and is playable as the Speciation
Quest "Chroom onschadelijk maken" level. Ignoring it costs reputation/penalty.

## 8. Economy, progression & scoring

- **Tier 1** (starting €3000 grant): hand hammer / hammer mill / ball mill; small
  tanks; manual agitation. The **ball mill (€790)** is the sweet spot — fine feed
  makes leaching 1 day instead of 80.
- **Tier 2** (reinvest V₂O₅ sales / bigger grants): large mills, autoclave,
  roaster, SX line — trade capital for throughput and grade.
- **Score**: V₂O₅ produced, days elapsed, budget left, strength gained, and
  (backlog) environmental reputation. Winning mints a signed **field/1**
  production record (SHA-256 → `cid`/`ual`), OriginTrail-ready.

## 9. Config & build map

All numbers live in [`data/production-chain.json`](../data/production-chain.json)
(blocks: `research`, `feedstocks`, `comminution`, `leach`, `tanks`, `agitation`,
`player`, `physics`, `autoclave`, `product`). `tools/build_production.py`
balance-checks that a viable strategy exists within the grant.

**v1 shipped:** budget → acquire → mill → leach (size→recovery, size→time),
strength-from-labour, signed record.
**Backlog:** gravity/strength lift check, leach tanks + agitation + sloshing,
roasting, autoclave, purification/SX, precipitation/calcination, Cr(VI) safety,
tier-2 economy. Tracked as GitHub issues in `ChemField/openchem`.
