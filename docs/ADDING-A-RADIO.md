# Adding a radio — and the transmit‑safety contract

Radio WebOp is **profile‑driven**: each model is a `RadioProfile` in
`backend/profiles.py`, driven by a protocol handler (`Radio` = Icom CI‑V,
`YaesuRadio` = Yaesu CAT). Adding a model of an existing make is usually just a new
profile; a new make/protocol is a new handler class exposing the same method surface the
server dispatches (`set_freq` / `set_mode` / `set_level` / `set_ptt` / …).

## ⚠️ Transmit‑safety contract — MANDATORY for any radio that can key TX

Remote operation puts a real transmitter on the air over a network, so **every keyed path
needs a backstop**. A radio is **not "done"** until every applicable item below is wired —
or explicitly marked N/A with a reason. When in doubt, **fail safe** (don't transmit / unkey).

1. **Operator‑triggered only — no *unattended* transmission.** Every keyed path is the
   direct result of an operator action *now*: **PTT** (press = key, release = unkey) and the
   **CW message send** (one bounded message per TX press — the rig's own keyer generates it,
   the operator can stop it). What is **not** shipped is transmission the app *originates on
   its own*: auto‑CQ on a timer, beacons, scheduled/unattended keying — those would need
   explicit local‑control safeguards and are never an implicit feature. (Hard rule for the
   assistant maintaining this repo: it wires operator‑triggered transmit, but never
   triggers or tests a transmission itself — on‑air testing is the operator's.)
2. **PTT stuck‑TX failsafe (120 s).** Keying arms `PTT_TIMEOUT`; the poll loop auto‑unkeys
   past the deadline, the client shows a countdown and unkeys too, **disconnect unkeys**,
   and **ANY client drop while keyed unkeys**. Mirror `Radio.set_ptt`, the `_poll`
   failsafe, and the `disconnect` unkey.
3. **Auto‑keying paths bound to the same failsafe.** Any mode that can key TX off audio
   (VOX) arms the same deadline and is dropped on disconnect.
4. **Hardware TOT set on connect.** Set the radio's own time‑out timer to ≈120 s (closest
   the radio supports) as a backstop for **control‑link loss** — if the network drops
   mid‑transmit the app failsafe can't fire, but the rig's own timer will. The profile
   carries the command; `N/A` if the radio doesn't expose it over the control link (then
   the app‑level failsafe is the only backstop — note it).
5. **CW message send is bounded + stoppable** (if `cw_send` is set). The rig's keyer
   generates the CW at the WPM the app sets — never host‑timed PTT keying. Cap the message
   length, only fire in CW/CW‑R mode, arm an auto‑stop deadline (`_cw_deadline`, the poll
   stops it — Icom `17 FF`), expose a stop, and stop on disconnect / client‑drop. The
   hardware TOT (item 4) is the hard backstop where a clean CAT abort isn't available
   (FT‑991A keyer playback).
6. **High‑SWR cutoff + warning.** While keyed, read the SWR meter; warn in the UI and
   auto‑unkey above the threshold to protect the PA. Reads + a protective un‑key only.
7. **Safe power on connect.** RF power defaults to 0 % on connect.
8. **Unkey + restore on disconnect.** Never leave the radio keyed; restore any borrowed
   state (e.g. the MOD source on the Icom LAN path).

Items 1–5, 7, 8 ship today; 6 (high‑SWR cutoff) is being added per‑radio. The profile
fields make every safety feature inherit‑by‑filling for future radios.

## Steps to add a radio
1. Add a `RadioProfile` (id, name, make, protocol, address/baud, bands, modes, filters,
   steps, the `has_*` capability flags, `connect_help`, and the **safety/feature fields** —
   `tot_civ`/`tot_cat`, SWR meter source, and `cw_send`/`cw_line` for CW message TX).
2. **Same protocol** as an existing radio → done; the handler is shared.
3. **New protocol** → a new handler class exposing the server's method surface **and the
   full safety contract above**.
4. Register it in `PROFILES`; add any new frontend asset to `server.py`'s versioned‑asset
   list (or it 404s / serves stale).
5. Verify on real hardware **RX‑side only** (the maintainer never tests TX by
   transmitting). The operator verifies any transmit path — PTT, CW send — on the air.
