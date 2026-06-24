"""
CI-V protocol layer for Icom transceivers (IC-9700 first).

All knowledge here comes from the official Icom "IC-9700 CI-V Reference Guide"
(Mar. 2021 revision, A7508-3EX), a copy of which lives in ../docs.

Frame structure (controller <-> radio):
    FE FE <to> <from> <cmd> [<sub>] [<data...>] FD
    OK reply : FE FE E0 A2 FB FD
    NG reply : FE FE E0 A2 FA FD

Default addresses: IC-9700 = 0xA2, controller = 0xE0.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
PREAMBLE = 0xFE
EOM = 0xFD
OK = 0xFB
NG = 0xFA

DEFAULT_RADIO_ADDR = 0xA2      # IC-9700
DEFAULT_CTRL_ADDR = 0xE0       # PC / controller

# Operating mode codes (command 01/04/06 byte 1)
MODES = {
    0x00: "LSB",
    0x01: "USB",
    0x02: "AM",
    0x03: "CW",
    0x04: "RTTY",
    0x05: "FM",
    0x07: "CW-R",
    0x08: "RTTY-R",
    0x17: "DV",
    0x22: "DD",
}
MODE_CODES = {v: k for k, v in MODES.items()}

# Filter slot (command 06 byte 2)
FILTERS = {0x01: "FIL1", 0x02: "FIL2", 0x03: "FIL3"}

# Span settings (command 27 15) -> full span in Hz.  Data column from the
# reference guide is the value in Hz of the *full* displayed span.
SPANS_HZ = {
    2500: 2_500,
    5000: 5_000,
    10000: 10_000,
    25000: 25_000,
    50000: 50_000,
    100000: 100_000,
    250000: 250_000,
    500000: 500_000,
}
# Human label for each full-span value (Hz -> label)
SPAN_LABELS = {
    2_500: "±1.25k",
    5_000: "±2.5k",
    10_000: "±5k",
    25_000: "±12.5k",
    50_000: "±25k",
    100_000: "±50k",
    250_000: "±125k",
    500_000: "±250k",
}

# Scope waveform constants (command 27 00)
SCOPE_POINTS = 475          # documented data length
SCOPE_MAX = 160             # documented data range 0..160


# ---------------------------------------------------------------------------
# BCD frequency helpers  (5-byte little-endian digit pairs)
# byte0 = 10Hz/1Hz, byte1 = 1k/100, byte2 = 100k/10k, byte3 = 10M/1M, byte4 = 1G/100M
# ---------------------------------------------------------------------------
def freq_to_bcd(hz: int) -> bytes:
    hz = int(round(hz))
    digits = [0] * 10
    for i in range(10):
        digits[i] = hz % 10
        hz //= 10
    out = bytearray(5)
    for b in range(5):
        lo = digits[b * 2]
        hi = digits[b * 2 + 1]
        out[b] = (hi << 4) | lo
    return bytes(out)


def bcd_to_freq(data: bytes) -> int:
    hz = 0
    for b in range(len(data) - 1, -1, -1):
        hi = (data[b] >> 4) & 0x0F
        lo = data[b] & 0x0F
        hz = hz * 100 + hi * 10 + lo
    return hz


def level_to_bcd(value: int) -> bytes:
    """0..255 -> 2 BCD bytes, e.g. 255 -> 02 55."""
    value = max(0, min(255, int(value)))
    hundreds = value // 100
    rem = value % 100
    tens = rem // 10
    ones = rem % 10
    return bytes([hundreds, (tens << 4) | ones])


def bcd_to_level(data: bytes) -> int:
    if len(data) < 2:
        return 0
    hundreds = data[0] & 0x0F
    tens = (data[1] >> 4) & 0x0F
    ones = data[1] & 0x0F
    return hundreds * 100 + tens * 10 + ones


# ---------------------------------------------------------------------------
# Frame building
# ---------------------------------------------------------------------------
def build(cmd: int, sub: Optional[int] = None, data: bytes = b"",
          radio_addr: int = DEFAULT_RADIO_ADDR,
          ctrl_addr: int = DEFAULT_CTRL_ADDR) -> bytes:
    body = bytearray([PREAMBLE, PREAMBLE, radio_addr, ctrl_addr, cmd])
    if sub is not None:
        body.append(sub)
    body.extend(data)
    body.append(EOM)
    return bytes(body)


@dataclass
class Frame:
    to_addr: int
    from_addr: int
    cmd: int
    sub: Optional[int]
    data: bytes
    raw: bytes

    @property
    def is_ok(self) -> bool:
        return self.cmd == OK

    @property
    def is_ng(self) -> bool:
        return self.cmd == NG


def _parse_one(raw: bytes) -> Optional[Frame]:
    """Parse a single FE FE ... FD frame (without trailing FD)."""
    # raw includes leading FE FE and everything up to but not incl. FD
    if len(raw) < 5 or raw[0] != PREAMBLE or raw[1] != PREAMBLE:
        return None
    to_addr = raw[2]
    from_addr = raw[3]
    cmd = raw[4]
    if cmd in (OK, NG):
        return Frame(to_addr, from_addr, cmd, None, b"", raw)
    sub = raw[5] if len(raw) > 5 else None
    data = bytes(raw[6:]) if len(raw) > 6 else b""
    return Frame(to_addr, from_addr, cmd, sub, data, raw)


class FrameReader:
    """Accumulates a raw byte stream and yields complete CI-V frames."""

    def __init__(self) -> None:
        self._buf = bytearray()

    def feed(self, data: bytes) -> list[Frame]:
        self._buf.extend(data)
        frames: list[Frame] = []
        while True:
            try:
                end = self._buf.index(EOM)
            except ValueError:
                break
            chunk = bytes(self._buf[: end])
            del self._buf[: end + 1]
            # find the start of the frame (two consecutive preambles)
            start = chunk.find(b"\xfe\xfe")
            if start < 0:
                continue
            frame = _parse_one(chunk[start:] + b"")  # raw w/o FD
            if frame:
                frames.append(frame)
        # guard against runaway buffer if we never see an EOM
        if len(self._buf) > 8192:
            del self._buf[:-4096]
        return frames


# ---------------------------------------------------------------------------
# Scope (command 27 00) parsing & assembly
# ---------------------------------------------------------------------------
@dataclass
class ScopeSweep:
    main_sub: int = 0                 # 0 main, 1 sub
    mode: int = 0                     # 0 center, 1 fixed
    center_hz: Optional[int] = None
    span_hz: Optional[int] = None
    lower_hz: Optional[int] = None
    upper_hz: Optional[int] = None
    out_of_range: bool = False
    data: bytes = b""                 # amplitude bytes, ideally SCOPE_POINTS long

    @property
    def complete(self) -> bool:
        return len(self.data) >= SCOPE_POINTS - 8  # tolerate minor length jitter


class ScopeAssembler:
    """
    Re-assembles 27 00 scope frames into full ScopeSweep objects.

    LAN  : a single frame carries header + all waveform data (div_max == 1).
    USB  : 11 frames; frame 1 = header only, frames 2..11 = waveform chunks.
    """

    def __init__(self) -> None:
        self._cur: Optional[ScopeSweep] = None
        self._chunks = bytearray()

    def feed(self, payload: bytes) -> Optional[ScopeSweep]:
        # payload is the data area after `27 00` (i.e. starting at main/sub byte)
        if len(payload) < 3:
            return None
        main_sub = payload[0]
        div_cur = payload[1]
        div_max = payload[2]

        if div_max <= 1:
            # LAN single-frame: header + waveform all together
            sweep = self._parse_header(main_sub, payload, 3)
            sweep.data = self._extract_waveform(payload, sweep)
            self._cur = None
            self._chunks = bytearray()
            return sweep if sweep.data else None

        # USB multi-frame
        if div_cur == 1:
            # header frame, no waveform data
            self._cur = self._parse_header(main_sub, payload, 3)
            self._chunks = bytearray()
            return None

        if self._cur is None:
            return None  # mid-stream join; wait for next header

        # waveform chunk frame: data follows main/sub, div_cur, div_max
        self._chunks.extend(payload[3:])
        if div_cur >= div_max:
            sweep = self._cur
            sweep.data = self._normalize(bytes(self._chunks))
            self._cur = None
            self._chunks = bytearray()
            return sweep if sweep.data else None
        return None

    def _parse_header(self, main_sub: int, payload: bytes, off: int) -> ScopeSweep:
        sweep = ScopeSweep(main_sub=main_sub)
        if len(payload) <= off:
            return sweep
        sweep.mode = payload[off]      # 0 center, 1 fixed
        off += 1
        if sweep.mode == 0:
            # center freq (5) + span (5)
            sweep.center_hz = bcd_to_freq(payload[off:off + 5])
            off += 5
            sweep.span_hz = bcd_to_freq(payload[off:off + 5])
            off += 5
        else:
            sweep.lower_hz = bcd_to_freq(payload[off:off + 5])
            off += 5
            sweep.upper_hz = bcd_to_freq(payload[off:off + 5])
            off += 5
        if len(payload) > off:
            sweep.out_of_range = payload[off] == 1
        sweep._header_end = off + 1  # type: ignore[attr-defined]
        return sweep

    def _extract_waveform(self, payload: bytes, sweep: ScopeSweep) -> bytes:
        start = getattr(sweep, "_header_end", None)
        wf = b""
        if start is not None and len(payload) - start >= SCOPE_POINTS - 8:
            wf = payload[start:]
        # robustness: if our computed offset looks wrong, fall back to tail
        if len(wf) < SCOPE_POINTS - 8 and len(payload) >= SCOPE_POINTS:
            wf = payload[-SCOPE_POINTS:]
        return self._normalize(wf)

    @staticmethod
    def _normalize(wf: bytes) -> bytes:
        if not wf:
            return b""
        if len(wf) > SCOPE_POINTS:
            wf = wf[:SCOPE_POINTS]
        return wf
