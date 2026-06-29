"""IC-9700 SET-menu table — a representative, useful subset for the data-driven Setup tab.

Icom menus are CI-V `1A 05 <data-number>` items (see backend/menu_engine.py); `MenuItem.num`
IS the 4-digit data number and `digits` is the value's BCD digit count (2 = one byte,
4 = two bytes / 0000-0255). Sourced from docs/CONTROL-MAP.md + the IC-9700 CI-V Reference.

This covers the clean toggle / enum / level items across the common categories. The niche
ones with special wire encodings (RGB colours, fixed-edge frequency pairs, GPS/D-PRS strings,
compound Lo+Hi nibbles) are intentionally left out for now — the engine supports adding them.
"""
from ..profiles import MenuItem

_OFFON = ["OFF", "ON"]


def _toggle(num, name, group, **kw):
    return MenuItem(num, name, group, kind="enum", digits=2, options=_OFFON, **kw)


def _enum(num, name, group, options, **kw):
    return MenuItem(num, name, group, kind="enum", digits=2, options=options, **kw)


def _lvl255(num, name, group, **kw):
    return MenuItem(num, name, group, kind="int", digits=4, min=0, max=255, **kw)


def _int(num, name, group, lo, hi, **kw):
    return MenuItem(num, name, group, kind="int", digits=2, min=lo, max=hi, **kw)


IC9700_MENU = [
    # --- CW Keyer ---
    _enum(227, "Keyer Type", "CW Keyer", ["Straight", "Bug", "Paddle"]),
    _enum(226, "Paddle Polarity", "CW Keyer", ["Normal", "Reverse"]),
    _toggle(228, "MIC Up/Down as Paddle", "CW Keyer"),
    _lvl255(221, "Side Tone Level", "CW Keyer"),
    _toggle(222, "Side Tone Level Limit", "CW Keyer"),
    _int(223, "Keyer Repeat Time", "CW Keyer", 1, 60, unit="s"),
    _int(224, "Dot/Dash Ratio", "CW Keyer", 28, 45, unit="×0.1", note="1:1:2.8-4.5"),
    _enum(225, "Rise Time", "CW Keyer", ["2 ms", "4 ms", "6 ms", "8 ms"]),
    _enum(67, "CW Normal Side", "CW Keyer", ["LSB", "USB"]),
    _toggle(66, "SSB/CW Synchronous Tuning", "CW Keyer"),
    # --- Scan ---
    _enum(249, "Scan Speed", "Scan", ["Slow", "Fast"]),
    _toggle(250, "Scan Resume", "Scan"),
    _enum(251, "Scan Pause Timer", "Scan",
          ["2 s", "4 s", "6 s", "8 s", "10 s", "12 s", "14 s", "16 s", "18 s", "20 s", "HOLD"]),
    _enum(252, "Scan Resume Timer", "Scan", ["0 s", "1 s", "2 s", "3 s", "4 s", "5 s", "HOLD"]),
    _enum(253, "Temporary Skip Timer", "Scan",
          ["5 min", "10 min", "15 min", "While Scanning", "While Powered ON"]),
    # --- TX ---
    _enum(41, "Time-Out Timer", "TX", ["OFF", "3 min", "5 min", "10 min", "20 min", "30 min"],
          critical=True, note="app sets this to 3 min on connect (TX safety backstop)"),
    _toggle(42, "PTT Lock", "TX"),
    _enum(38, "TX Delay 144M", "TX", ["OFF", "10 ms", "15 ms", "20 ms", "25 ms", "30 ms"]),
    _enum(39, "TX Delay 430M", "TX", ["OFF", "10 ms", "15 ms", "20 ms", "25 ms", "30 ms"]),
    _enum(40, "TX Delay 1200M", "TX", ["OFF", "10 ms", "15 ms", "20 ms", "25 ms", "30 ms"]),
    _toggle(332, "TX Power Limit 144M", "TX", critical=True),
    _lvl255(333, "TX Power Limit 144M Value", "TX", critical=True),
    _toggle(334, "TX Power Limit 430M", "TX", critical=True),
    _lvl255(335, "TX Power Limit 430M Value", "TX", critical=True),
    _toggle(336, "TX Power Limit 1200M", "TX", critical=True),
    _lvl255(337, "TX Power Limit 1200M Value", "TX", critical=True),
    # --- Beep / Sound ---
    _lvl255(27, "Beep Level", "Beep", note="0-255"),
    _toggle(28, "Beep Level Limit", "Beep"),
    _toggle(29, "Beep (Confirmation)", "Beep"),
    _enum(30, "Band Edge Beep", "Beep", ["OFF", "ON", "ON (User)", "ON (User) & TX Limit"]),
    # --- Noise Blanker (144 MHz) ---
    _lvl255(321, "NB Level (144M)", "Noise Blanker"),
    _int(322, "NB Depth (144M)", "Noise Blanker", 0, 9, note="0-9 = 1-10"),
    _lvl255(323, "NB Width (144M)", "Noise Blanker"),
    # --- Display / General ---
    _enum(59, "Lock Function Target", "Display", ["MAIN DIAL", "PANEL"]),
    _enum(61, "MAIN DIAL Auto TS", "Display", ["OFF", "Low", "High"]),
    _enum(62, "MIC Up/Down Speed", "Display", ["Slow", "Fast"]),
    _toggle(156, "Display Memory Name", "Display"),
    _toggle(70, "Screen Capture [POWER] Switch", "Display"),
    _enum(71, "Screen Capture File Type", "Display", ["PNG", "BMP"]),
    # --- SPEECH ---
    _enum(50, "SPEECH Language", "Speech", ["English", "Japanese"]),
    _enum(51, "SPEECH Alphabet", "Speech", ["Normal", "Phonetic"]),
    _enum(52, "SPEECH Speed", "Speech", ["Slow", "Fast"]),
    _lvl255(57, "SPEECH Level", "Speech"),
    # --- Scope ---
    _enum(192, "Scope Averaging", "Scope", ["OFF", "2", "3", "4"]),
    _enum(193, "Scope Waveform Type", "Scope", ["Fill", "Fill + Line"]),
    _enum(188, "Scope Max Hold", "Scope", ["OFF", "10 s", "ON"]),
    _toggle(197, "Waterfall Display", "Scope"),
    _enum(198, "Waterfall Speed", "Scope", ["Slow", "Mid", "Fast"]),
    _enum(199, "Waterfall Size", "Scope", ["Small", "Mid", "Large"]),
    # --- Connectors ---
    _toggle(93, "External P.AMP 144M", "Connectors"),
    _toggle(94, "External P.AMP 430M", "Connectors"),
    _toggle(95, "External P.AMP 1200M", "Connectors"),
    _enum(96, "External Speaker Separate", "Connectors", ["Separate", "Mix"]),
    _enum(98, "Phones L/R Mix", "Connectors", ["Separate", "Mix", "Auto"]),
]
