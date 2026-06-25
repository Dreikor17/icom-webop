# Roadmap

Radio WebOp is a browser control panel for Icom CI-V transceivers. The protocol
(CI-V framing, the `27 00` scope, the RS-BA1 LAN transport, audio) is shared;
each supported radio is a **profile** in `backend/profiles.py` (address, bands,
modes, filter widths, MOD-Input numbers, power behaviour), so adding a radio is
just adding a profile.

## Done — v0.2.0
- **Unified multi-radio app** with a radio-model selector (IC-9700, IC-7300MK2);
  bands/modes/steps render from the selected profile.
- Transports behind one interface: **USB CI-V**, **LAN** (RS-BA1 UDP), and a
  built-in **simulator**.
- Spectrum **scope + waterfall** with the tuned-channel marker and filter
  passband overlaid.
- Tuning: main dial, **tap-to-select and drag/slide on the waterfall**, step
  select, direct entry, mouse wheel.
- **RX audio** playback + **mic TX** over LAN; MOD Input auto-set to LAN on
  connect (restored on disconnect).
- **PTT** tap-to-toggle with a **failsafe time-out** (client countdown + a
  server-side auto-unkey), plus release on background / disconnect.
- **Mobile-friendly** responsive layout; remembers radio + connection.

## Planned
- **More radios** — IC-705, IC-7610, IC-905, IC-7300, IC-9700 satellite, etc.
  (each is just a profile; help/PRs welcome).
- **Authentication + built-in HTTPS** for safe remote use (today there is no
  login — restrict by interface / Tailscale ACLs).
- **Remote power-on** from networked standby where the radio supports it.
- **Memory channels**, split/duplex + tone, RIT/XIT.
- **Satellite / dual-watch** (IC-9700 dual scope).
- Read **true IF filter widths** (`1A 03`) instead of per-mode defaults; scope
  **reference-level / sweep-speed / VBW** controls.
- Audio: selectable **codec / sample-rate**, recording, lower-latency options.
- Band-stacking registers, scan control, per-band memory.

## Non-goals (for now)
- Non-Icom rigs / Hamlib backends — possible later via the transport+profile
  split, but not a near-term focus.
