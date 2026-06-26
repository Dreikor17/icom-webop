# IC-9700 UI spec (from the Basic Manual)

Visual blueprint for the skeuomorphic **Radio view** + the FUNCTION / MENU panels.
Source: `IC-9700_ENG_Basic_3.pdf` (Basic Manual, §1 Panel Description, rendered
pages 12–14). Copyrighted — not redistributed; `_manual_text.txt` / `_render/` are
gitignored working copies.

## Main screen (the 4.3" TFT) — dual MAIN (top) / SUB (bottom)

Each band block, left→right:

- **Left:** big **MODE** (e.g. `FM`) with the **IF FILTER** (`FIL1`/2/3) under it; an
  **RFG** (RF-gain) marker at the far-left edge.
- **Top indicator strip** (above the frequency), lit when active, in this order:
  `OVF` · `P.AMP`/`ATT` · `NB` · `AN`/`MN` (notch) · `D-TSQL` (tone/digital sql) ·
  `NR` · `EMR`/`BK` · `AGC-F`/`AGC-M`/`AGC-S` · `AFC` · `1/4` (quarter tuning).
- **Center:** the **big frequency** readout (Hz/kHz digits smaller).
- **Right:** `RIT` + RIT offset value, `AFC`, and the **VFO** indicator
  (`VFO A` / `VFO B` / `MEMO` + memory ch#).
- **Bottom:** the **band label** (`2 m band` / `70 cm band`) + the **multi-function
  meter** strip (Po/SWR/ALC/… with the S/Po scale).
- **TX/RX status** box at the band's top-left (`TX` red on transmit; flags band-edge
  / inhibited).

Top status bar (across the very top): `LMT` (PA temp), `DUP-`/`SPLIT`, `VOX`,
`BK-IN`, `M1–M8`/`T1–T8`/`COMP`, GPS, alarm, `LAN`, picture-share, SD, and a clock.

> Our backend already tracks most strip states (P.AMP/ATT, NB, NR, AN/MN, AGC). TONE/
> VOX/COMP/RIT/AFC arrive with M3. Strip states are per the **operating band** in our
> model, so the active band's strip is live; the inactive band shows mode/filter/freq.

## FUNCTION screen (push FUNCTION) — a touch grid of cycle-buttons

Each button = name (top) + current value (below), highlighted when active. Items
and the values they cycle:

| Button | Values |
|---|---|
| P.AMP/ATT | OFF · P.AMP · ATT |
| AGC | FAST · MID · SLOW |
| NOTCH | OFF · AN · MN |
| NB | OFF · ON |
| IP+ | OFF · ON |
| VOX | OFF · ON |
| TONE | OFF · TONE · TSQL · DTCS · TONE(T/DTCS R)… |
| BK-IN | OFF · ON(SEMI) · BKIN(FULL) · F-BKIN |
| COMP | OFF · ON |
| D.SQL | OFF · DSQL · CSQL |
| TBW (TX bandwidth) | WIDE · MID · NAR |
| MON | OFF · ON |
| DUP | OFF · DUP- · DUP+ |
| EXT P.AMP | OFF · ON |
| RPS / TX POWER LIMIT | … |

This maps almost 1:1 onto our M1/M2/M3 controls — it's the "quick controls" panel.

## MENU screen (push MENU) — category icons (2 pages)

`SCOPE` · `AUDIO` · `VOICE` · `METER` · `SATELLITE` · `MEMORY` · `SCAN` · `MPAD` ·
`RECORD` · `SET` — then — `CS` · `CD` · `DV A/B/PV` · `DV GW` · `PICTURE` · `GPS` ·
`DTMF` · `PRESET` · `SET`. `SET` opens the deep set-mode tree (see
`docs/CONTROL-MAP.md` for the CI-V items behind each).

## QUICK MENU (push QUICK)

A contextual list popup: VFO/MEMORY, Meter Select, GPS Information, GPS Position, …

## Build notes

- **Radio view** mirrors the main screen above (skeuomorphic). Drives the strip from
  existing state; mode/filter box + VFO + band label per band.
- **FUNCTION panel** = the cycle-button grid (our existing toggles, restyled).
- **Menus/SET** = clean modern lists generated from CONTROL-MAP, grouped by the MENU
  categories.
