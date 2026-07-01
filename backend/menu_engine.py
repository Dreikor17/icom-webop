"""Generic radio SET-menu codec.

Turns a declarative ``profiles.MenuItem`` into the wire command to read or write it, and
parses replies back into Python values. Protocol-dispatched so other makes slot in later.

Yaesu CAT (the only protocol implemented now):
    read   ``EX<NNN>;``            -> reply ``EX<NNN><field>;``
    write  ``EX<NNN><field>;``
where ``<NNN>`` is the zero-padded 3-digit menu number and ``<field>`` is a fixed-width
value field whose width is ``MenuItem.digits`` (the manual's "Digits" column, verbatim):
    * enum        -> the 0-based option index, zero-padded to ``digits``.
    * int         -> the number, zero-padded to ``digits``.
    * signed-int  -> a leading '+'/'-' sign then the magnitude zero-padded to ``digits-1``
                     (so the whole field, sign included, is ``digits`` wide — matching the
                     manual, e.g. item 064 OTHER DISP = 5 digits -> "+1500" / "-1500").

A wrong ``digits`` makes the radio silently ignore the command, so callers should
confirm-read after every write.
"""
from __future__ import annotations

from typing import Optional


class MenuError(ValueError):
    """Invalid menu value, read-only write, or unsupported protocol."""


# ---- protocol dispatch -----------------------------------------------------
def read_cmd(item, protocol: str = "yaesu") -> str:
    if protocol == "yaesu":
        return yaesu_read_cmd(item)
    raise MenuError(f"menus not implemented for protocol {protocol!r}")


def encode(item, value, protocol: str = "yaesu") -> str:
    if protocol == "yaesu":
        return yaesu_encode(item, value)
    raise MenuError(f"menus not implemented for protocol {protocol!r}")


def decode(item, reply: str, protocol: str = "yaesu"):
    if protocol == "yaesu":
        return yaesu_decode(item, reply)
    raise MenuError(f"menus not implemented for protocol {protocol!r}")


# ---- Yaesu CAT EX ----------------------------------------------------------
# The menu-number field width varies by model: the FT-991A uses a flat 3-digit EXNNN, the
# FT-891 a 4-digit group/item EXGGNN (e.g. 07-12 -> EX0712). `item.ex_width` carries it.
def _exw(item) -> int:
    return getattr(item, "ex_width", 3)


def yaesu_read_cmd(item) -> str:
    w = _exw(item)
    return f"EX{item.num:0{w}d};"


def yaesu_encode(item, value) -> str:
    if getattr(item, "readonly", False):
        raise MenuError(f"menu {item.num} ({item.name}) is read-only")
    w = _exw(item)
    return f"EX{item.num:0{w}d}{_encode_field(item, value)};"


def yaesu_decode(item, reply: str):
    body = _ex_body(item, reply)
    if body is None:
        return None
    return _decode_field(item, body)


def _ex_body(item, reply: str) -> Optional[str]:
    """Strip ``EX<NNN>`` prefix and trailing ';' from a reply; None if it isn't this item."""
    s = (reply or "").strip()
    if not s.startswith("EX"):
        return None
    s = s[2:]
    if s.endswith(";"):
        s = s[:-1]
    w = _exw(item)
    if len(s) < w or not s[:w].isdigit() or int(s[:w]) != item.num:
        return None
    return s[w:]


# ---- value field encode / decode -------------------------------------------
def _encode_field(item, value) -> str:
    kind = item.kind
    if kind == "enum":
        return f"{_enum_index(item, value):0{item.digits}d}"
    if kind == "int":
        return f"{_clamp_snap(item, int(value)):0{item.digits}d}"
    if kind == "signed-int":
        v = _clamp_snap(item, int(value))
        mag = max(1, item.digits - 1)
        return f"{'-' if v < 0 else '+'}{abs(v):0{mag}d}"
    raise MenuError(f"menu {item.num:03d}: unknown kind {kind!r}")


def _decode_field(item, body: str):
    if item.kind == "enum":
        if not body.isdigit():
            return None
        idx = int(body)
        return item.options[idx] if 0 <= idx < len(item.options) else idx
    try:
        return int(body.strip())            # int() handles leading zeros and +/-
    except ValueError:
        return None


def _enum_index(item, value) -> int:
    """Accept an option label, an index int, or a digit string. Labels are matched FIRST
    because option labels can themselves be numeric (e.g. CAT RATE "4800".."38400")."""
    if isinstance(value, bool):
        idx = int(value)
    elif isinstance(value, int):
        idx = value
    elif value in item.options:
        idx = item.options.index(value)
    elif isinstance(value, str) and value.isdigit():
        idx = int(value)                    # a bare index passed as a string
    else:
        raise MenuError(f"menu {item.num:03d}: {value!r} not in options")
    if not 0 <= idx < len(item.options):
        raise MenuError(f"menu {item.num:03d}: index {idx} out of range")
    return idx


def _clamp_snap(item, v: int) -> int:
    lo, hi = item.min, item.max
    if lo or hi:
        v = max(lo, min(hi, v))
    step = item.step or 1
    if step > 1:
        v = lo + round((v - lo) / step) * step
        if lo or hi:
            v = max(lo, min(hi, v))
    return v


# ---- Icom CI-V (1A 05 <data-number>) ---------------------------------------
# Icom SET-mode menus are addressed by a 4-digit data number carried as 2 BCD bytes
# after `1A 05`; the value follows as BCD. `MenuItem.num` IS the data number (e.g.
# num=321 -> "0321" -> 03 21). `MenuItem.digits` is the value's BCD digit count
# (2 = one byte, 4 = two bytes). enum = 1 BCD byte index; signed = a sign byte
# (00=+, 01=-) then the magnitude BCD. The Radio handler frames these with `1A 05`.
def civ_datanum(num) -> bytes:
    n = int(num)
    return bytes([(((n // 1000) % 10) << 4) | ((n // 100) % 10),
                  (((n // 10) % 10) << 4) | (n % 10)])


def civ_read_data(item) -> bytes:
    """Data area for the `1A 05 <dn>` READ frame (just the data number)."""
    return civ_datanum(item.num)


def civ_write_data(item, value) -> bytes:
    """Data area for the `1A 05 <dn> <value>` WRITE frame."""
    if getattr(item, "readonly", False):
        raise MenuError(f"menu {item.num} ({item.name}) is read-only")
    return civ_datanum(item.num) + _civ_value_bytes(item, value)


def civ_decode(item, frame_data: bytes):
    """Decode a `1A 05` reply's data area: data number (2 bytes) + value bytes."""
    if frame_data is None or len(frame_data) < 2:
        return None
    return _civ_decode_value(item, frame_data[2:])


def _civ_value_bytes(item, value) -> bytes:
    if item.kind == "enum":
        return bytes([_bcd1(_enum_index(item, value))])
    if item.kind == "int":
        return _bcd(_clamp_snap(item, int(value)), item.digits)
    if item.kind == "signed-int":
        v = _clamp_snap(item, int(value))
        return bytes([1 if v < 0 else 0]) + _bcd(abs(v), item.digits)
    raise MenuError(f"menu {item.num}: unknown kind {item.kind!r}")


def _civ_decode_value(item, val: bytes):
    if not val:
        return None
    if item.kind == "enum":
        idx = _unbcd1(val[0])
        return item.options[idx] if 0 <= idx < len(item.options) else idx
    if item.kind == "signed-int":
        return (-1 if val[0] == 1 else 1) * _unbcd(val[1:])
    return _unbcd(val)


def _bcd1(v) -> int:
    """One byte of packed BCD for a 0-99 value."""
    v = int(v) % 100
    return ((v // 10) << 4) | (v % 10)


def _unbcd1(b: int) -> int:
    return ((b >> 4) & 0x0F) * 10 + (b & 0x0F)


def _bcd(v, digits) -> bytes:
    """Big-endian packed BCD; byte count = ceil(digits/2)."""
    nbytes = max(1, (int(digits) + 1) // 2)
    v = int(v)
    out = bytearray(nbytes)
    for i in range(nbytes - 1, -1, -1):
        out[i] = _bcd1(v % 100)
        v //= 100
    return bytes(out)


def _unbcd(data: bytes) -> int:
    n = 0
    for b in data:
        n = n * 100 + _unbcd1(b)
    return n
