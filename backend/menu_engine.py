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
def yaesu_read_cmd(item) -> str:
    return f"EX{item.num:03d};"


def yaesu_encode(item, value) -> str:
    if getattr(item, "readonly", False):
        raise MenuError(f"menu {item.num:03d} ({item.name}) is read-only")
    return f"EX{item.num:03d}{_encode_field(item, value)};"


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
    if len(s) < 3 or not s[:3].isdigit() or int(s[:3]) != item.num:
        return None
    return s[3:]


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
