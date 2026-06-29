"""IC-7300MK2 SET-menu table — the data-driven Setup tab for the IC-7300MK2.

Icom CI-V `1A 05 <data-number>` items (see backend/menu_engine.py); `MenuItem.num` IS the
4-digit data number and `digits` is the value's BCD digit count (2 = one byte, 4 = two bytes,
6 = three bytes). Compiled from the official Icom *IC-7300MK2 CI-V Reference Guide*
(docs/IC-7300MK2_ENG_CI-V_0.pdf). The data numbers are MODEL-SPECIFIC and differ from the
IC-9700's (e.g. Beep Level = 0022 here vs 0027 on the 9700).

Covers the 137 simple toggle/enum/int items; the special multi-byte ones (RGB scope colours,
fixed-edge frequency pairs, IP-address octets, free-text strings, date/time, HPF/LPF & TBW
passband packed fields) are intentionally omitted — the engine supports adding them later.

`critical` marks connection/transmit-sensitive items (TOT, PTT/keying routing, MOD routing,
CI-V address, network connectivity). A handful flagged VERIFY in the source text (OCR dropped a
digit, or a wide value) should be confirmed against the real radio before trusting writes.
"""
from ..profiles import MenuItem

_OFFON = ["OFF", "ON"]
_TXDELAY = ["OFF", "10 ms", "15 ms", "20 ms", "25 ms", "30 ms"]
_AFIF = ["AF", "IF"]
_OPENON = ["OFF (Open)", "ON"]
_USBSEND = ["OFF", "USB (A) DTR", "USB (A) RTS", "USB (B) DTR", "USB (B) RTS"]
_MODSRC = ["MIC", "USB", "ACC", "MIC, USB", "MIC, ACC", "LAN"]


def _toggle(num, name, group, **kw):
    return MenuItem(num, name, group, kind="enum", digits=2, options=_OFFON, **kw)


def _enum(num, name, group, options, **kw):
    return MenuItem(num, name, group, kind="enum", digits=2, options=options, **kw)


def _lvl255(num, name, group, **kw):
    return MenuItem(num, name, group, kind="int", digits=4, min=0, max=255, **kw)


def _int(num, name, group, lo, hi, digits=2, **kw):
    return MenuItem(num, name, group, kind="int", digits=digits, min=lo, max=hi, **kw)


def _tone(num, name, group):
    return MenuItem(num, name, group, kind="int", digits=2, min=0, max=10, note="display -5..+5")


IC7300MK2_MENU = [
    # --- Function (Beep / TX Delay / TOT / SPLIT) ---
    _lvl255(22, "Beep Level", "Function"),
    _toggle(23, "Beep Level Limit", "Function"),
    _toggle(24, "Beep (Confirmation)", "Function"),
    _enum(25, "Band Edge Beep", "Function", ["OFF", "ON (Default)", "ON (User)", "ON (User) & TX Limit"]),
    _enum(26, "RF/SQL Control", "Function", ["Auto", "SQL", "RF+SQL"]),
    _enum(27, "Cancel CI-V Remote Set Levels", "Function", ["All Volume Levels", "Operated Volume Level"]),
    _toggle(28, "MF Band ATT", "Function"),
    _enum(29, "TX Delay (HF)", "Function", _TXDELAY),
    _enum(30, "TX Delay (50M)", "Function", _TXDELAY),
    _enum(31, "TX Delay (70M)", "Function", _TXDELAY),
    _enum(32, "Time-Out Timer (CI-V)", "Function", ["OFF", "3 min", "5 min", "10 min", "20 min", "30 min"],
          critical=True, note="TX safety backstop"),
    _toggle(33, "Quick SPLIT", "Function"),
    _toggle(36, "SPLIT LOCK", "Function"),
    # --- Tone Control RX ---
    _tone(2, "RX Tone Bass (SSB)", "Tone RX"),
    _tone(3, "RX Tone Treble (SSB)", "Tone RX"),
    _tone(5, "RX Tone Bass (AM)", "Tone RX"),
    _tone(6, "RX Tone Treble (AM)", "Tone RX"),
    _tone(8, "RX Tone Bass (FM)", "Tone RX"),
    _tone(9, "RX Tone Treble (FM)", "Tone RX"),
    # --- Tone Control TX ---
    _tone(12, "TX Tone Bass (SSB)", "Tone TX"),
    _tone(13, "TX Tone Treble (SSB)", "Tone TX"),
    _tone(18, "TX Tone Bass (AM)", "Tone TX"),
    _tone(19, "TX Tone Treble (AM)", "Tone TX"),
    _tone(20, "TX Tone Bass (FM)", "Tone TX"),
    _tone(21, "TX Tone Treble (FM)", "Tone TX"),
    # --- Speech ---
    _enum(42, "SPEECH Language", "Speech", ["English", "Japanese"]),
    _enum(43, "SPEECH Speed", "Speech", ["Slow", "Fast"]),
    _toggle(44, "S-Level SPEECH", "Speech"),
    _toggle(45, "MODE SPEECH", "Speech"),
    _lvl255(46, "SPEECH Level", "Speech"),
    _enum(47, "[SPEECH/LOCK] Switch", "Speech", ["SPEECH/LOCK", "LOCK/SPEECH"]),
    # --- General ---
    _enum(37, "[TUNER] Switch", "General", ["Manual", "Auto"]),
    _toggle(38, "PTT Start", "General", critical=True),
    _enum(39, "RTTY Mark Frequency", "General", ["1275 Hz", "1615 Hz", "2125 Hz"]),
    _enum(40, "RTTY Shift Width", "General", ["170 Hz", "200 Hz", "425 Hz"]),
    _enum(41, "RTTY Keying Polarity", "General", ["Normal", "Reverse"]),
    _enum(48, "Lock Function", "General", ["MAIN DIAL", "PANEL"]),
    _enum(49, "Memo Pad Quantity", "General", ["5 ch", "10 ch"]),
    _enum(50, "MAIN DIAL Auto TS", "General", ["OFF", "Low", "High"]),
    _enum(51, "MIC Up/Down Speed", "General", ["Slow", "Fast"]),
    _toggle(52, "Quick RIT/dTX Clear", "General"),
    _enum(53, "[NOTCH] Switch (SSB)", "General", ["Auto", "Manual", "Auto/Manual"]),
    _enum(54, "[NOTCH] Switch (AM)", "General", ["Auto", "Manual", "Auto/Manual"]),
    _toggle(55, "SSB/CW Synchronous Tuning", "General"),
    _enum(56, "CW Normal Side", "General", ["LSB", "USB"]),
    _toggle(63, "Screen Capture [POWER] Switch", "General"),
    _enum(64, "Screen Capture File Type", "General", ["PNG", "BMP"]),
    _enum(65, "Keyboard Type", "General", ["Ten-key", "Full Keyboard"]),
    _enum(66, "Full Keyboard Layout", "General", ["English", "German", "French"]),
    _toggle(67, "Calibration Marker", "General"),
    _lvl255(68, "REF Adjust", "General"),
    # --- Connectors (USB / ACC / LAN AF-IF, MOD, keypad, CI-V, keying) ---
    _enum(69, "USB AF/IF Output Select", "Connectors", _AFIF),
    _lvl255(70, "USB AF Output Level", "Connectors"),
    _enum(71, "USB AF SQL", "Connectors", _OPENON),
    _toggle(72, "USB AF Beep/Speech Output", "Connectors"),
    _lvl255(73, "USB IF Output Level", "Connectors"),
    _enum(74, "ACC AF/IF Output Select", "Connectors", _AFIF),
    _lvl255(75, "ACC AF Output Level", "Connectors"),
    _enum(76, "ACC AF SQL", "Connectors", _OPENON),
    _toggle(77, "ACC AF Beep/Speech Output", "Connectors"),
    _lvl255(78, "ACC IF Output Level", "Connectors"),
    _enum(79, "LAN AF/IF Output Select", "Connectors", _AFIF),
    _enum(80, "LAN AF SQL", "Connectors", _OPENON),
    _lvl255(81, "USB MOD Level", "Connectors"),
    _lvl255(82, "ACC MOD Level", "Connectors"),
    _lvl255(83, "LAN MOD Level", "Connectors", critical=True, note="app manages MOD routing on LAN"),
    _enum(84, "DATA OFF MOD", "Connectors", _MODSRC, critical=True, note="app manages MOD routing on LAN"),
    _enum(85, "DATA MOD", "Connectors", _MODSRC, critical=True),
    _toggle(86, "External Keypad VOICE", "Connectors"),
    _toggle(87, "External Keypad KEYER", "Connectors"),
    _toggle(88, "External Keypad RTTY", "Connectors"),
    _toggle(89, "CI-V Transceive", "Connectors"),
    _int(90, "USB/LAN->REMOTE Transceive Address", "Connectors", 0, 223, digits=4, critical=True, note="0-223 = 00h-DFh"),
    _toggle(91, "CI-V Output (for ANT)", "Connectors"),
    _toggle(92, "CI-V USB (A) Echo Back", "Connectors"),
    _toggle(93, "CI-V USB (B) Echo Back", "Connectors"),
    _enum(94, "USB (B) Function", "Connectors", ["RTTY Decode", "CI-V"]),
    _toggle(95, "SEND Relay Output", "Connectors", critical=True),
    _enum(96, "USB SEND", "Connectors", _USBSEND, critical=True),
    _enum(97, "USB Keying (CW)", "Connectors", _USBSEND, critical=True),
    _enum(98, "USB Keying (RTTY)", "Connectors", _USBSEND, critical=True),
    _enum(99, "PTT Port Function", "Connectors", ["PTT Input", "PTT Input + SEND Output"], critical=True),
    # --- Network (valid after restart) ---
    _toggle(100, "DHCP", "Network", critical=True, note="valid after restart"),
    _int(103, "Subnet Mask (prefix bits)", "Network", 1, 30, critical=True, note="valid after restart"),
    _toggle(108, "Network Control", "Network", critical=True, note="valid after restart"),
    _enum(109, "Power OFF Setting (Remote)", "Network", ["Only Shutdown", "Standby/Shutdown"]),
    _int(110, "Control Port (UDP)", "Network", 1, 65535, digits=6, critical=True, note="valid after restart"),
    _int(111, "Serial Port (UDP)", "Network", 1, 65535, digits=6, critical=True, note="valid after restart"),
    _int(112, "Audio Port (UDP)", "Network", 1, 65535, digits=6, critical=True, note="valid after restart"),
    _enum(113, "Internet Access Line", "Network", ["FTTH (Fiber To The Home)", "ADSL/CATV"]),
    # --- Display ---
    _lvl255(115, "LCD Backlight", "Display"),
    _enum(116, "Display Type", "Display", ["A (Black background)", "B (Blue background)"]),
    _enum(117, "Display Font", "Display", ["Square", "Round"]),
    _toggle(118, "Meter Peak Hold", "Display"),
    _toggle(119, "Memory Name", "Display"),
    _toggle(120, "MN-Q Popup (MN OFF->ON)", "Display"),
    _toggle(121, "BW Popup (PBT)", "Display"),
    _toggle(122, "BW Popup (FIL)", "Display"),
    _enum(123, "Screen Saver", "Display", ["OFF", "15 minutes", "30 minutes", "60 minutes"]),
    _toggle(124, "External Display", "Display"),
    _enum(125, "External Display Resolution", "Display", ["640x480", "1024x768", "1280x720"]),
    _toggle(126, "External Display Audio Output", "Display"),
    _toggle(127, "Opening Message", "Display"),
    _toggle(129, "Power ON Check", "Display"),
    _enum(130, "Display Language", "Display", ["English", "Japanese"]),
    _enum(131, "System Language", "Display", ["English", "Japanese"]),
    _toggle(134, "NTP Function", "Display"),
    # --- Scope ---
    _toggle(137, "Scope during TX (CENTER Type)", "Scope"),
    _enum(138, "Max Hold", "Scope", ["OFF", "10s Hold", "ON"]),
    _enum(139, "CENTER Type Display", "Scope", ["Filter Center", "Carrier Point", "Carrier Point (Abs. Freq.)"]),
    _enum(140, "Marker Position (Fix/SCROLL)", "Scope", ["Filter Center", "Carrier Point"]),
    _enum(141, "VBW", "Scope", ["Narrow", "Wide"]),
    _enum(142, "Averaging", "Scope", ["OFF", "2", "3", "4"]),
    _enum(143, "Waveform Type", "Scope", ["Fill", "Fill + Line"]),
    _toggle(147, "Waterfall Display", "Scope"),
    _enum(148, "Waterfall Speed", "Scope", ["Slow", "Mid", "Fast"]),
    _enum(149, "Waterfall Size (Expand)", "Scope", ["Small", "Mid", "Large"]),
    _enum(150, "Waterfall Peak Color Level", "Scope",
          ["Grid 1", "Grid 2", "Grid 3", "Grid 4", "Grid 5", "Grid 6", "Grid 7", "Grid 8"]),
    _toggle(151, "Waterfall Marker Auto-hide", "Scope"),
    _enum(204, "Audio Scope FFT Waveform Type", "Scope", ["Line", "Fill"]),
    _toggle(206, "Audio Scope FFT Waterfall", "Scope"),
    # --- CW Keyer ---
    _enum(208, "Number Style", "CW Keyer", ["Normal", "190->ANO", "190->ANT", "90->NO", "90->NT"]),
    _toggle(209, "Count Up Trigger (M1)", "CW Keyer"),
    _toggle(210, "Count Up Trigger (M2)", "CW Keyer"),
    _toggle(211, "Count Up Trigger (M3)", "CW Keyer"),
    _toggle(212, "Count Up Trigger (M4)", "CW Keyer"),
    _toggle(213, "Count Up Trigger (M5)", "CW Keyer"),
    _toggle(214, "Count Up Trigger (M6)", "CW Keyer"),
    _toggle(215, "Count Up Trigger (M7)", "CW Keyer"),
    _toggle(216, "Count Up Trigger (M8)", "CW Keyer"),
    _int(217, "Present Number (Keyer)", "CW Keyer", 1, 9999, digits=4),
    _lvl255(218, "Side Tone Level", "CW Keyer", note="VERIFY max on radio"),
    _toggle(219, "Side Tone Level Limit", "CW Keyer"),
    _int(220, "Keyer Repeat Time", "CW Keyer", 1, 60, unit="s"),
    _int(221, "Dot/Dash Ratio", "CW Keyer", 28, 45, note="1:1:2.8-4.5"),
    _enum(222, "Rise Time", "CW Keyer", ["2 ms", "4 ms", "6 ms", "8 ms"]),
    _enum(223, "Paddle Polarity", "CW Keyer", ["Normal", "Reverse"]),
    _enum(224, "Key Type", "CW Keyer", ["Straight", "Bug", "Paddle"]),
    _toggle(225, "MIC Up/Down Keyer", "CW Keyer"),
    _toggle(226, "CW Decode Display", "CW Keyer"),
    _toggle(227, "Japanese Morse Decode", "CW Keyer"),
    # --- RTTY ---
    _enum(228, "RTTY FFT Scope Averaging", "RTTY", ["OFF", "2", "3", "4"]),
    _toggle(230, "RTTY Decode USOS", "RTTY"),
    _enum(231, "RTTY Decode New Line Code", "RTTY", ["CR, LF, CR+LF", "CR+LF"]),
    _toggle(232, "RTTY TX USOS", "RTTY"),
    _toggle(235, "RTTY Count Up Trigger (RT1)", "RTTY"),
    _toggle(236, "RTTY Count Up Trigger (RT2)", "RTTY"),
    _toggle(237, "RTTY Count Up Trigger (RT3)", "RTTY"),
    _toggle(238, "RTTY Count Up Trigger (RT4)", "RTTY"),
    _toggle(239, "RTTY Count Up Trigger (RT5)", "RTTY"),
    _toggle(240, "RTTY Count Up Trigger (RT6)", "RTTY"),
    _toggle(241, "RTTY Count Up Trigger (RT7)", "RTTY"),
    _toggle(242, "RTTY Count Up Trigger (RT8)", "RTTY"),
    _int(243, "Present Number (RTTY)", "RTTY", 1, 9999, digits=4),
    # --- Logs ---
    _toggle(244, "Decode Log", "Logs"),
    _enum(245, "Log File Type", "Logs", ["Text", "HTML"]),
    _toggle(246, "Time Stamp", "Logs"),
    _enum(247, "Time Stamp (Time)", "Logs", ["Local", "UTC"]),
    _toggle(248, "Time Stamp (Frequency)", "Logs"),
    # --- Scan ---
    _enum(253, "SCAN Speed", "Scan", ["Slow", "Fast"]),
    _toggle(254, "SCAN Resume", "Scan"),
    # --- Voice / Record ---
    _lvl255(255, "Voice TX Level", "Voice/Rec", note="VERIFY max on radio"),
    _toggle(256, "Auto Monitor", "Voice/Rec"),
    _int(257, "Repeat Time (Voice)", "Voice/Rec", 1, 15, unit="s"),
    _enum(258, "TX REC Audio", "Voice/Rec", ["Direct", "Monitor"]),
    _enum(259, "RX REC Condition", "Voice/Rec", ["Always", "Squelch Auto"]),
    _toggle(260, "File Split", "Voice/Rec"),
    _toggle(261, "PTT Auto REC", "Voice/Rec"),
    _enum(262, "PRE-REC for PTT Auto REC", "Voice/Rec", ["OFF", "5 sec", "10 sec", "15 sec"]),
    _enum(263, "Player Skip Time", "Voice/Rec", ["3 sec", "5 sec", "10 sec", "30 sec"]),
    # --- NB / VOX / APF ---
    _enum(265, "NB Depth", "NB/VOX/APF", ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]),
    _lvl255(266, "NB Width", "NB/VOX/APF", note="VERIFY max on radio"),
    _int(267, "VOX Delay", "NB/VOX/APF", 0, 20, note="0.0-2.0 s"),
    _enum(268, "VOX Voice Delay", "NB/VOX/APF", ["OFF", "Short", "Mid", "Long"]),
    _enum(269, "APF Type", "NB/VOX/APF", ["SHARP", "SOFT"]),
    _enum(270, "APF AF Level", "NB/VOX/APF", ["0 dB", "1 dB", "2 dB", "3 dB", "4 dB", "5 dB", "6 dB"]),
]
