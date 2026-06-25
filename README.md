# Icom WebOp

A browser-based control panel for Icom CI-V transceivers, starting with the
**IC-9700**. It recreates the radio's front panel — button-for-button mode,
band, filter and VFO control, a tuning dial, level controls — and renders a
live **spectrum scope + waterfall** with the tuned-channel marker and receive
filter passband drawn over it, just like the IC-9700's own display.

It ships with a built-in **simulator**, so the full interface and waterfall run
with no radio attached. Point it at a real COM port when you're ready.

## Features

- **Live bandscope + waterfall** decoded from CI-V `27 00` scope data (475
  points, range 0–160), reassembled from the USB 11-frame format (or the LAN
  single-frame format) and streamed to the browser over a WebSocket.
- **Channel & filter overlay** — the tuned-frequency marker and the receive
  passband (offset by mode: USB above, LSB below, CW centered) shaded over the
  scope and waterfall.
- **Button-for-button control** — Band (144 / 430 / 1200), Mode (LSB/USB/CW/
  CW-R/AM/FM/RTTY/DV), Filter (FIL1–3), VFO A/B/A=B/swap.
- **Tuning** — draggable main dial, mouse-wheel tuning, click-to-tune on the
  scope, selectable tuning step, and direct frequency entry.
- **Live readouts** — frequency, mode, filter, and a real-time S-meter.
- **Levels** — AF, RF, SQL and RF power.
- **Scope controls** — center/fixed mode and span (±1.25 k … ±250 k).
- **Simulator** built in for development and demos with no hardware.

## How it talks to the radio

Control uses Icom's **CI-V** protocol (the official *IC-9700 CI-V Reference
Guide* is the source of truth for every command). Frames look like:

```
FE FE A2 E0 <cmd> [<sub>] [<data…>] FD      controller → radio (A2 = IC-9700)
FE FE E0 A2 <cmd> [<sub>] [<data…>] FD      radio → controller
```

Key commands used: `05/03` frequency, `06/04` mode+filter, `07` VFO, `14`
levels, `15` meters, and `27` for the scope (`27 10` scope on, `27 11` data
output on, `27 14` center/fixed, `27 15` span, `27 00` waveform data).

Two transports are supported behind one interface:

- **USB CI-V** — a COM port.
- **LAN (network)** — the IC-9700's Ethernet port, speaking Icom's proprietary
  RS-BA1 UDP protocol (the one `wfview`/RS-BA1 use): three UDP streams — control
  (50001), CI-V/serial (50002) and audio (50003). The CI-V tunnel over the
  network is byte-identical to USB, so full control + the scope/waterfall work
  over LAN with no change to the layers above the transport. Audio is opened but
  not yet decoded (a later phase).

## Run it (Windows)

```
pip install -r requirements.txt
run.bat
```

Then open <http://localhost:8700>. It auto-starts the **Simulator** so the
waterfall is live immediately.

To control a real IC-9700 over **USB**:

1. Connect the radio by USB and set **SET → Connectors → USB (B)/DATA Function
   → CI-V**, note its CI-V address (default `A2`) and baud rate.
2. In the top bar, pick the radio's **COM port**, set the baud rate, and click
   **Connect**.

To control it over **LAN**:

1. On the radio: **SET → Network → Network Function = ON**, note the **Control
   Port** (default 50001), and register a **Network User** name + password
   (SET → Network → Network User1).
2. Make sure the radio is **on or in standby** (it can't be cold-powered over
   the network).
3. In the top bar, choose **LAN (network)**, enter the radio's **IP**, the
   **network user** and **password**, and click **Connect**.

(From the command line: `python run.py --port 8700`.)

## Architecture

```
backend/
  civ.py        CI-V protocol: framing, BCD freq/levels, mode codes,
                and the 27 00 scope parser/assembler (USB + LAN formats)
  transport.py  SerialTransport (real COM port) + SimTransport (synthetic
                IC-9700 that speaks CI-V, including USB 11-frame scope sweeps)
  lan.py        LanTransport — Icom RS-BA1 UDP protocol (control/serial/audio
                streams, login, keepalives); tunnels CI-V over the network
  radio.py      Radio controller: decodes the inbound stream into live state +
                scope sweeps, exposes button-level actions, polls meters
  server.py     Starlette/uvicorn app: REST connect/ports + WebSocket that
                streams state (JSON) and scope sweeps (compact binary)
frontend/
  index.html    Icom-themed panel
  style.css     IC-9700 dark/TFT theme
  waterfall.js  spectrum + scrolling waterfall + channel/filter overlay
  app.js        WebSocket client, state binding, tuning, controls
```

The transport interface means the simulator and a real radio are
interchangeable — everything above `transport.py` is identical for both.

## Roadmap

- **Audio over LAN** (RX playback + TX mic) — the audio stream is already opened;
  next is decoding/encoding LPCM/µLaw and wiring browser Web Audio + mic.
- Read true IF filter widths (`1A 03`) instead of per-mode defaults.
- Memory channels, split/duplex + tone, satellite mode (the 9700's dual scope).
- Per-control menus to cover more of the CI-V command set.

## Notes

This is an independent project and is not affiliated with or endorsed by Icom.
The LAN protocol implementation is a clean-room port informed by the
reverse-engineered, open-source [wfview](https://gitlab.com/eliggett/wfview) and
[kappanhang](https://github.com/nonoo/kappanhang) projects; there is no official
Icom network-protocol specification.
"CI-V" and "IC-9700" are referenced for interoperability only. The CI-V
Reference Guide PDF is **not** redistributed here — download it from Icom (see
`docs/README.md`).
