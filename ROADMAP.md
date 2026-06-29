# Roadmap

Radio WebOp is a browser control panel for ham transceivers (Icom CI-V + Yaesu CAT).
Each radio is a **declarative `RadioProfile`** in `backend/profiles.py` — transports
(CAT/serial, RS-BA1 LAN, audio, scope), a **capability map** the UI adapts to, and a
**SET-menu table** — so adding a radio is mostly data (see `docs/ADDING-A-RADIO.md`).

## Done

### v0.2.13 — declarative profiles + full Setup menu
- **Declarative `RadioProfile`** is the single source of truth: structured `transports`
  (serial/network/audio/scope) + a `capabilities` map (synthesized from the flat flags when
  omitted). The **UI is adaptive** — it shows only the controls a rig reports (and fixed the
  FT-991A's dead VFO A/B buttons).
- **Data-driven Setup tab** — the **FT-991A's full 154-item SET menu** (001–154) as a grouped
  accordion: each section reads live from the radio on open (lazy), and writes back with a
  confirm-read. Connection/transmit-sensitive items (CAT rate/RTS, PC keying, PTT/port routing,
  per-band max power) are flagged and confirmed; CAT-RTS / PC-KEYING are protected so the menu
  can't break CW/PTT keying. Generic codec in `backend/menu_engine.py`; per-model table in
  `backend/menus/<id>_menu.py` (Icom CI-V `1A 05` menus are a stubbed seam for later).

### v0.2.2 — multi-manufacturer + overlay tools
- **Yaesu FT-991A** — first non-Icom radio (Yaesu CAT over USB, COM-only); profiles
  carry make/protocol/capabilities. Serial ports show Enhanced/Standard + auto-pick.
- **Band-plan overlay** (ARRL VHF/UHF + FCC license-class HF) with color key + tooltips.
- **CW decoder/coder** overlay tool (adaptive squelch/tone/WPM; Morse sidetone, no TX);
  **audio (AF) spectrum scope** from RX audio for radios with no CAT scope.
- **USB audio** RX-in/Mic-out pickers for COM radios; **per-radio connection memory**
  (+ "?" help) and **live panel re-sync** so the UI mirrors the radio's real state.

### v0.2.0 — unified multi-radio base
- **Multi-radio app** with a model selector (IC-9700, IC-7300MK2); bands/modes/
  steps render from the selected profile.
- Transports behind one interface: **USB CI-V**, **LAN** (RS-BA1 UDP), simulator.
- **Scope + waterfall** with the tuned marker + filter passband; tap-to-select and
  drag/slide tuning, step, direct entry, wheel.
- **RX audio** + **mic TX** over LAN (auto MOD-Input → LAN); **PTT** tap-to-toggle
  with a failsafe time-out; mobile-friendly; remembers radio + connection.

### v0.2.1 — IC-9700 build-out (M1–M3)
- **Dual-watch** MAIN/SUB Radio view + **multi-meter** + core RX (preamp/att/lock).
- **RX DSP** — NB, NR, auto/manual notch (+ width/position), AGC, twin-PBT.
- **TX** — mic / COMP / VOX / monitor / TBW, **RIT**, **split/duplex** (VOX bound by
  the same failsafe as PTT).
- **Skeuomorphic TFT Radio view** from the IC-9700 manual (mode/filter box, lit
  function-indicator strip, VFO + wavelength band labels); controls below the
  waterfall; full-travel sliders; abbreviation tooltips.
- Reference: full per-control map in `docs/CONTROL-MAP.md`, screen/menu blueprint
  in `docs/UI-SPEC.md`.

### Band-plan overlay
- **ARRL band plan / FCC license-class overlay** on the scope — a toggleable strip
  along the spectrum showing the segments for the band in view, aligned to the
  frequency axis, with a hover tooltip giving the range, type, modes and notes.
  VHF/UHF (2 m / 70 cm / 23 cm) is colored by **use** (CW / weak-signal / SSB / FM /
  repeater / simplex / satellite / beacon / digital, ARRL voluntary band plan); HF +
  6 m is colored by **license class** (Technician / General / Extra sub-bands, FCC
  Part 97). Data in `frontend/bandplan.js`, compiled + adversarially verified.

## Planned

### Operating
- **Band-plan overlay enhancements** (the overlay itself shipped): let the user pick
  their license class to highlight just their privileges and soft-flag tuning outside
  them; make the data region-aware so non-US band plans can drop in.
- **CW encoder / decoder / transmit** — *shipped*. The "CW" button pops a draggable panel
  over the waterfall with a **neural decoder** (the DeepCW ONNX model from e04/deepcw-engine,
  run in-browser via onnxruntime-web), a type-to-Morse soft-keyed off-air sidetone, and a
  **TX button** that sends the typed message as CW — operator-triggered, one bounded message,
  failsafe- and TOT-bound. Icom keys via CI-V `17` (semi break-in) so the rig generates the CW;
  the FT-991A is keyed by host-timed **DTR on its Standard USB port** (PC KEYING=DTR, CAT RTS
  disabled), since it has no arbitrary-text CW CAT command. The decoder is what relicensed the app to **AGPL-3.0** (a
  deliberate opt-in for the accuracy). *Follow-ups:* tune the streaming finalize so the last
  char of a discrete burst never slips; optional WebGPU backend.
- **Audio recorder** — capture the RX audio (and optionally TX) to a file from the browser:
  start/stop with an elapsed-time + level readout and download. `MediaRecorder` on the
  pre-volume `rxBus` → WebM/Opus (or WAV), so it works for every transport (LAN PCM, USB
  audio, AF). Foundation for QSO timestamping / a recording log later.
- **More overlay tools** over the waterfall (the framework is in place) — e.g. RTTY/FT8
  decode, a tuning/zero-beat aid, memory keyer.
- **Tone / DTCS** (CTCSS encode/decode) + an editable duplex offset (M3.5).
- **Memory channels**, band-stacking registers, scan control.
- **CW** keyer/memories, **RTTY** decode; **DV / D-STAR** (DR, call signs, GPS);
  **satellite** dual-scope.
- Read **true IF filter widths** (`1A 03`); scope **reference-level / sweep-speed /
  VBW** controls.

### UI
- The **FUNCTION-screen panel** — a clean modern panel of the IC-9700 FUNCTION-screen
  toggles grouped by category. *(The SET-mode menu tree shipped — see Done.)*

### Platform
- **More radios** — IC-705, IC-7610, IC-905, IC-7300, etc. (each is just a profile).
- **Authentication** for safe remote use (today there is no login — restrict by
  interface / firewall / VPN). *Built-in HTTPS shipped* — serve TLS directly with
  `run.py --ssl-certfile/--ssl-keyfile` (or `RADIO_WEBOP_SSL_CERT/_KEY`).
- **Remote power-on** from networked standby where the radio supports it.
- Audio: selectable **codec / sample-rate**, lower-latency options.

## Non-goals (for now)
- Non-Icom rigs / Hamlib backends — possible later via the transport+profile split,
  but not a near-term focus.
