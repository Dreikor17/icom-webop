"""FT-991A SET-menu table — all 154 items (001-154) for the data-driven Setup tab.

Transcribed from the Yaesu *FT-991A CAT Operation Reference Manual*
(docs/CAT_CONTROL_ysu-ft-991a_us.pdf). Read/written over CAT as ``EX<NNN><value>;``
(see backend/menu_engine.py). `digits` is the manual's value-field width verbatim; for
``signed-int`` it includes the leading sign char.

087 RADIO ID is read-only. `critical=True` marks connection/transmit-sensitive items
(CAT link, PC keying, PTT/port routing, per-band max power) so the UI confirms before write.

A few items the manual numbers with index gaps (028, 072, 077) or that the source text
rendered ambiguously (102, 103) carry a placeholder/`note`; verify those on the radio
(read→echo) before trusting the index — see docs/ADDING-A-RADIO.md.
"""
from ..profiles import MenuItem

# ---- shared option lists / generators --------------------------------------
_SLOPE = ["6 dB/oct", "18 dB/oct"]
_COLOR = ["BLUE", "GRAY", "GREEN", "ORANGE", "PURPLE", "RED", "SKY BLUE"]
_COLOR_WF = _COLOR + ["MULTI"]
_MIC_SEL = ["MIC", "REAR"]
_PTT_SEL = ["DAKY", "RTS", "DTR"]
_DISEN = ["DISABLE", "ENABLE"]
_OFFON = ["OFF", "ON"]
_NORM_REV = ["NORMAL", "REVERSE"]
_BPS = ["4800 bps", "9600 bps", "19200 bps", "38400 bps"]
_TOT_MS = ["10 msec", "100 msec", "1000 msec", "3000 msec"]

# LCUT 01:100Hz..19:1000Hz / HCUT 01:700Hz..67:4000Hz, both with 00:OFF (50 Hz steps)
_LCUT = ["OFF"] + [f"{100 + 50 * i} Hz" for i in range(19)]
_HCUT = ["OFF"] + [f"{700 + 50 * i} Hz" for i in range(67)]
# parametric-EQ centre frequencies (00:OFF then the documented sweep)
_EQ1F = ["OFF"] + [f"{100 + 100 * i} Hz" for i in range(7)]    # 100..700
_EQ2F = ["OFF"] + [f"{700 + 100 * i} Hz" for i in range(9)]    # 700..1500
_EQ3F = ["OFF"] + [f"{1500 + 100 * i} Hz" for i in range(18)]  # 1500..3200


def _lcut(num, name, group):
    return MenuItem(num, name, group, kind="enum", digits=2, options=_LCUT, unit="Hz")


def _hcut(num, name, group):
    return MenuItem(num, name, group, kind="enum", digits=2, options=_HCUT, unit="Hz")


def _slope(num, name, group):
    return MenuItem(num, name, group, kind="enum", digits=1, options=_SLOPE)


def _level(num, name, group):
    return MenuItem(num, name, group, kind="int", digits=3, min=0, max=100)


def _eq_freq(num, name, group, opts):
    return MenuItem(num, name, group, kind="enum", digits=2, options=opts, unit="Hz")


def _eq_level(num, name, group):
    return MenuItem(num, name, group, kind="signed-int", digits=3, min=-20, max=10, unit="dB")


def _eq_bwth(num, name, group):
    return MenuItem(num, name, group, kind="int", digits=2, min=1, max=10)


FT991A_MENU = [
    # --- AGC ---
    MenuItem(1, "AGC FAST DELAY", "AGC", kind="int", digits=4, min=20, max=4000, step=20, unit="ms"),
    MenuItem(2, "AGC MID DELAY", "AGC", kind="int", digits=4, min=20, max=4000, step=20, unit="ms"),
    MenuItem(3, "AGC SLOW DELAY", "AGC", kind="int", digits=4, min=20, max=4000, step=20, unit="ms"),
    # --- Display ---
    MenuItem(4, "HOME FUNCTION", "Display", kind="enum", digits=1, options=["SCOPE", "FUNCTION"]),
    MenuItem(5, "MY CALL INDICATION", "Display", kind="int", digits=1, min=0, max=5, unit="s"),
    MenuItem(6, "DISPLAY COLOR", "Display", kind="enum", digits=1, options=_COLOR),
    MenuItem(7, "DIMMER LED", "Display", kind="enum", digits=1, options=["1", "2"]),
    MenuItem(8, "DIMMER TFT", "Display", kind="int", digits=2, min=0, max=15),
    MenuItem(9, "BAR MTR PEAK HOLD", "Display", kind="enum", digits=1, options=["OFF", "0.5 sec", "1.0 sec", "2.0 sec"]),
    # --- DVS (voice memory) ---
    _level(10, "DVS RX OUT LEVEL", "DVS"),
    _level(11, "DVS TX OUT LEVEL", "DVS"),
    # --- Keyer / Contest ---
    MenuItem(12, "KEYER TYPE", "Keyer/Contest", kind="enum", digits=1, options=["OFF", "BUG", "ELEKEY-A", "ELEKEY-B", "ELEKEY-Y", "ACS"]),
    MenuItem(13, "KEYER DOT/DASH", "Keyer/Contest", kind="enum", digits=1, options=_NORM_REV),
    MenuItem(14, "CW WEIGHT", "Keyer/Contest", kind="int", digits=2, min=25, max=45, unit="×0.1", note="ratio 2.5-4.5"),
    MenuItem(15, "BEACON INTERVAL", "Keyer/Contest", kind="int", digits=3, min=0, max=690, unit="s", note="0 = OFF"),
    MenuItem(16, "NUMBER STYLE", "Keyer/Contest", kind="enum", digits=1, options=["1290", "AUNO", "AUNT", "A2NO", "A2NT", "12NO", "12NT"]),
    MenuItem(17, "CONTEST NUMBER", "Keyer/Contest", kind="int", digits=4, min=0, max=9999),
    MenuItem(18, "CW MEMORY 1", "Keyer/Contest", kind="enum", digits=1, options=["TEXT", "MESSAGE"]),
    MenuItem(19, "CW MEMORY 2", "Keyer/Contest", kind="enum", digits=1, options=["TEXT", "MESSAGE"]),
    MenuItem(20, "CW MEMORY 3", "Keyer/Contest", kind="enum", digits=1, options=["TEXT", "MESSAGE"]),
    MenuItem(21, "CW MEMORY 4", "Keyer/Contest", kind="enum", digits=1, options=["TEXT", "MESSAGE"]),
    MenuItem(22, "CW MEMORY 5", "Keyer/Contest", kind="enum", digits=1, options=["TEXT", "MESSAGE"]),
    # --- Noise Blanker ---
    MenuItem(23, "NB WIDTH", "Noise Blanker", kind="enum", digits=1, options=["1 ms", "3 ms", "10 ms"]),
    MenuItem(24, "NB REJECTION", "Noise Blanker", kind="enum", digits=1, options=["10 dB", "30 dB", "50 dB"]),
    MenuItem(25, "NB LEVEL", "Noise Blanker", kind="int", digits=2, min=0, max=10),
    # --- General ---
    MenuItem(26, "BEEP LEVEL", "General", kind="int", digits=3, min=0, max=100),
    MenuItem(27, "TIME ZONE", "General", kind="signed-int", digits=5, min=-1200, max=1400, step=15, unit="HHMM", note="UTC offset"),
    MenuItem(28, "GPS/232C SELECT", "General", kind="enum", digits=1, options=["GPS1", "GPS2", "(reserved)", "RS232C"], note="index 2 reserved"),
    MenuItem(29, "232C RATE", "General", kind="enum", digits=1, options=_BPS),
    MenuItem(30, "232C TOT", "General", kind="enum", digits=1, options=_TOT_MS),
    # --- CAT ---
    MenuItem(31, "CAT RATE", "CAT", kind="enum", digits=1, options=_BPS, critical=True, note="changing drops the control link"),
    MenuItem(32, "CAT TOT", "CAT", kind="enum", digits=1, options=_TOT_MS),
    MenuItem(33, "CAT RTS", "CAT", kind="enum", digits=1, options=_DISEN, critical=True, readonly=True, note="managed by the app for CW keying"),
    # --- Memory / Scan / TX general ---
    MenuItem(34, "MEM GROUP", "Memory/Scan", kind="enum", digits=1, options=_DISEN),
    MenuItem(35, "QUICK SPLIT FREQ", "Memory/Scan", kind="signed-int", digits=3, min=-20, max=20, unit="kHz"),
    MenuItem(36, "TX TOT", "General TX", kind="int", digits=2, min=0, max=30, unit="min", note="0 = OFF; app sets 2 min on connect"),
    MenuItem(37, "MIC SCAN", "Memory/Scan", kind="enum", digits=1, options=_DISEN),
    MenuItem(38, "MIC SCAN RESUME", "Memory/Scan", kind="enum", digits=1, options=["PAUSE", "TIME"]),
    MenuItem(39, "REF FREQ ADJ", "General", kind="signed-int", digits=3, min=-25, max=25),
    MenuItem(40, "CLAR MODE SELECT", "General TX", kind="enum", digits=1, options=["RX", "TX", "TRX"]),
    # --- AM mode ---
    _lcut(41, "AM LCUT FREQ", "AM"),
    _slope(42, "AM LCUT SLOPE", "AM"),
    _hcut(43, "AM HCUT FREQ", "AM"),
    _slope(44, "AM HCUT SLOPE", "AM"),
    MenuItem(45, "AM MIC SELECT", "AM", kind="enum", digits=1, options=_MIC_SEL),
    _level(46, "AM OUT LEVEL", "AM"),
    MenuItem(47, "AM PTT SELECT", "AM", kind="enum", digits=1, options=_PTT_SEL, critical=True),
    MenuItem(48, "AM PORT SELECT", "AM", kind="enum", digits=1, options=["DATA", "USB"], critical=True),
    _level(49, "AM DATA GAIN", "AM"),
    # --- CW mode ---
    _lcut(50, "CW LCUT FREQ", "CW"),
    _slope(51, "CW LCUT SLOPE", "CW"),
    _hcut(52, "CW HCUT FREQ", "CW"),
    _slope(53, "CW HCUT SLOPE", "CW"),
    _level(54, "CW OUT LEVEL", "CW"),
    MenuItem(55, "CW AUTO MODE", "CW", kind="enum", digits=1, options=["OFF", "50 MHz", "ON"]),
    MenuItem(56, "CW BK-IN TYPE", "CW", kind="enum", digits=1, options=["SEMI BREAK-IN", "FULL BREAK-IN"]),
    MenuItem(57, "CW BK-IN DELAY", "CW", kind="int", digits=4, min=30, max=3000, step=10, unit="ms"),
    MenuItem(58, "CW WAVE SHAPE", "CW", kind="enum", digits=1, options=["1 msec", "2 msec", "4 msec", "6 msec"]),
    MenuItem(59, "CW FREQ DISPLAY", "CW", kind="enum", digits=1, options=["DIRECT FREQ", "PITCH OFFSET"]),
    MenuItem(60, "PC KEYING", "CW", kind="enum", digits=1, options=["OFF", "DAKY", "RTS", "DTR"], critical=True, readonly=True, note="managed by the app for CW keying"),
    MenuItem(61, "QSK DELAY TIME", "CW", kind="enum", digits=1, options=["15 msec", "20 msec", "25 msec", "30 msec"]),
    # --- DATA mode ---
    MenuItem(62, "DATA MODE", "DATA", kind="enum", digits=1, options=["PSK", "OTHER"]),
    MenuItem(63, "PSK TONE", "DATA", kind="enum", digits=1, options=["1000 Hz", "1500 Hz", "2000 Hz"]),
    MenuItem(64, "OTHER DISP (SSB)", "DATA", kind="signed-int", digits=5, min=-3000, max=3000, step=10, unit="Hz"),
    MenuItem(65, "OTHER SHIFT (SSB)", "DATA", kind="signed-int", digits=5, min=-3000, max=3000, step=10, unit="Hz"),
    _lcut(66, "DATA LCUT FREQ", "DATA"),
    _slope(67, "DATA LCUT SLOPE", "DATA"),
    _hcut(68, "DATA HCUT FREQ", "DATA"),
    _slope(69, "DATA HCUT SLOPE", "DATA"),
    MenuItem(70, "DATA IN SELECT", "DATA", kind="enum", digits=1, options=_MIC_SEL),
    MenuItem(71, "DATA PTT SELECT", "DATA", kind="enum", digits=1, options=_PTT_SEL, critical=True),
    MenuItem(72, "DATA PORT SELECT", "DATA", kind="enum", digits=1, options=["(reserved)", "DATA", "USB"], critical=True, note="index 0 reserved"),
    _level(73, "DATA OUT LEVEL", "DATA"),
    # --- FM mode ---
    MenuItem(74, "FM MIC SELECT", "FM", kind="enum", digits=1, options=_MIC_SEL),
    _level(75, "FM OUT LEVEL", "FM"),
    MenuItem(76, "FM PKT PTT SELECT", "FM", kind="enum", digits=1, options=_PTT_SEL, critical=True),
    MenuItem(77, "FM PKT PORT SELECT", "FM", kind="enum", digits=1, options=["(reserved)", "DATA", "USB"], critical=True, note="index 0 reserved"),
    _level(78, "FM PKT TX GAIN", "FM"),
    MenuItem(79, "FM PKT MODE", "FM", kind="enum", digits=1, options=["1200", "9600"]),
    # --- Repeater / ARS ---
    MenuItem(80, "RPT SHIFT 28MHz", "Repeater", kind="int", digits=4, min=0, max=1000, step=10, unit="kHz"),
    MenuItem(81, "RPT SHIFT 50MHz", "Repeater", kind="int", digits=4, min=0, max=4000, step=10, unit="kHz"),
    MenuItem(82, "RPT SHIFT 144MHz", "Repeater", kind="int", digits=4, min=0, max=4000, step=10, unit="kHz"),
    MenuItem(83, "RPT SHIFT 430MHz", "Repeater", kind="int", digits=5, min=0, max=10000, step=10, unit="kHz"),
    MenuItem(84, "ARS 144MHz", "Repeater", kind="enum", digits=1, options=_OFFON),
    MenuItem(85, "ARS 430MHz", "Repeater", kind="enum", digits=1, options=_OFFON),
    # --- Digital / GM / AMS ---
    MenuItem(86, "DCS POLARITY", "Digital/GM", kind="enum", digits=1, options=["Tn-Rn", "Tn-Riv", "Tiv-Rn", "Tiv-Riv"]),
    MenuItem(87, "RADIO ID", "Info", kind="int", digits=4, readonly=True, note="display only"),
    MenuItem(88, "DIGITAL SQL TYPE", "Digital/GM", kind="enum", digits=1, options=["OFF", "CODE", "BREAK"]),
    MenuItem(89, "DIGITAL SQL CODE", "Digital/GM", kind="int", digits=3, min=1, max=126),
    MenuItem(90, "GM DISPLAY", "Digital/GM", kind="enum", digits=1, options=["DISTANCE", "STRENGTH"]),
    MenuItem(91, "DISTANCE", "Digital/GM", kind="enum", digits=1, options=["km", "mile"]),
    MenuItem(92, "AMS TX MODE", "Digital/GM", kind="enum", digits=1, options=["AUTO", "MANUAL", "DN", "VW", "ANALOG"]),
    MenuItem(93, "STANDBY BEEP", "Digital/GM", kind="enum", digits=1, options=_OFFON),
    # --- RTTY mode ---
    _lcut(94, "RTTY LCUT FREQ", "RTTY"),
    _slope(95, "RTTY LCUT SLOPE", "RTTY"),
    _hcut(96, "RTTY HCUT FREQ", "RTTY"),
    _slope(97, "RTTY HCUT SLOPE", "RTTY"),
    MenuItem(98, "RTTY SHIFT PORT", "RTTY", kind="enum", digits=1, options=["SHIFT", "DTR", "RTS"]),
    MenuItem(99, "RTTY POLARITY-RX", "RTTY", kind="enum", digits=1, options=_NORM_REV),
    MenuItem(100, "RTTY POLARITY-TX", "RTTY", kind="enum", digits=1, options=_NORM_REV),
    _level(101, "RTTY OUT LEVEL", "RTTY"),
    MenuItem(102, "RTTY SHIFT FREQ", "RTTY", kind="enum", digits=1, options=["170 Hz", "200 Hz", "425 Hz", "850 Hz"]),
    MenuItem(103, "RTTY MARK FREQ", "RTTY", kind="enum", digits=1, options=["1275 Hz", "2125 Hz"], note="verify index on radio"),
    # --- SSB mode ---
    _lcut(104, "SSB LCUT FREQ", "SSB"),
    _slope(105, "SSB LCUT SLOPE", "SSB"),
    _hcut(106, "SSB HCUT FREQ", "SSB"),
    _slope(107, "SSB HCUT SLOPE", "SSB"),
    MenuItem(108, "SSB MIC SELECT", "SSB", kind="enum", digits=1, options=_MIC_SEL),
    _level(109, "SSB OUT LEVEL", "SSB"),
    MenuItem(110, "SSB PTT SELECT", "SSB", kind="enum", digits=1, options=_PTT_SEL, critical=True),
    MenuItem(111, "SSB PORT SELECT", "SSB", kind="enum", digits=1, options=["DATA", "USB"], critical=True),
    MenuItem(112, "SSB TX BPF", "SSB", kind="enum", digits=1, options=["50-3000", "100-2900", "200-2800", "300-2700", "400-2600"], unit="Hz"),
    # --- Contour / APF / Notch ---
    MenuItem(113, "APF WIDTH", "Contour/Notch", kind="enum", digits=1, options=["NARROW", "MEDIUM", "WIDE"]),
    MenuItem(114, "CONTOUR LEVEL", "Contour/Notch", kind="signed-int", digits=3, min=-40, max=20),
    MenuItem(115, "CONTOUR WIDTH", "Contour/Notch", kind="int", digits=2, min=1, max=11),
    MenuItem(116, "IF NOTCH WIDTH", "Contour/Notch", kind="enum", digits=1, options=["NARROW", "WIDE"]),
    # --- Scope ---
    MenuItem(117, "SCP DISPLAY MODE", "Scope", kind="enum", digits=1, options=["SPECTRUM", "WATER FALL"]),
    MenuItem(118, "SCP SPAN FREQ", "Scope", kind="enum", digits=2, options=["(03) 50 kHz", "(04) 100 kHz", "(05) 200 kHz", "(06) 500 kHz", "(07) 1000 kHz"], note="wire values 03-07", critical=False),
    MenuItem(119, "SPECTRUM COLOR", "Scope", kind="enum", digits=1, options=_COLOR),
    MenuItem(120, "WATER FALL COLOR", "Scope", kind="enum", digits=1, options=_COLOR_WF),
    # --- RX Parametric EQ ---
    _eq_freq(121, "PRMTRC EQ1 FREQ", "RX EQ", _EQ1F),
    _eq_level(122, "PRMTRC EQ1 LEVEL", "RX EQ"),
    _eq_bwth(123, "PRMTRC EQ1 BWTH", "RX EQ"),
    _eq_freq(124, "PRMTRC EQ2 FREQ", "RX EQ", _EQ2F),
    _eq_level(125, "PRMTRC EQ2 LEVEL", "RX EQ"),
    _eq_bwth(126, "PRMTRC EQ2 BWTH", "RX EQ"),
    _eq_freq(127, "PRMTRC EQ3 FREQ", "RX EQ", _EQ3F),
    _eq_level(128, "PRMTRC EQ3 LEVEL", "RX EQ"),
    _eq_bwth(129, "PRMTRC EQ3 BWTH", "RX EQ"),
    # --- Mic (processor) Parametric EQ ---
    _eq_freq(130, "P-PRMTRC EQ1 FREQ", "Mic EQ", _EQ1F),
    _eq_level(131, "P-PRMTRC EQ1 LEVEL", "Mic EQ"),
    _eq_bwth(132, "P-PRMTRC EQ1 BWTH", "Mic EQ"),
    _eq_freq(133, "P-PRMTRC EQ2 FREQ", "Mic EQ", _EQ2F),
    _eq_level(134, "P-PRMTRC EQ2 LEVEL", "Mic EQ"),
    _eq_bwth(135, "P-PRMTRC EQ2 BWTH", "Mic EQ"),
    _eq_freq(136, "P-PRMTRC EQ3 FREQ", "Mic EQ", _EQ3F),
    _eq_level(137, "P-PRMTRC EQ3 LEVEL", "Mic EQ"),
    _eq_bwth(138, "P-PRMTRC EQ3 BWTH", "Mic EQ"),
    # --- TX Max Power (critical) ---
    MenuItem(139, "HF TX MAX POWER", "TX Power", kind="int", digits=3, min=5, max=100, unit="W", critical=True),
    MenuItem(140, "50M TX MAX POWER", "TX Power", kind="int", digits=3, min=5, max=100, unit="W", critical=True),
    MenuItem(141, "144M TX MAX POWER", "TX Power", kind="int", digits=3, min=5, max=50, unit="W", critical=True),
    MenuItem(142, "430M TX MAX POWER", "TX Power", kind="int", digits=3, min=5, max=50, unit="W", critical=True),
    # --- Tuner ---
    MenuItem(143, "TUNER SELECT", "Tuner", kind="enum", digits=1, options=["OFF", "INTERNAL", "EXTERNAL", "ATAS", "LAMP"]),
    # --- VOX ---
    MenuItem(144, "VOX SELECT", "VOX", kind="enum", digits=1, options=["MIC", "DATA"]),
    MenuItem(145, "VOX GAIN", "VOX", kind="int", digits=3, min=0, max=100),
    MenuItem(146, "VOX DELAY", "VOX", kind="int", digits=4, min=30, max=3000, step=10, unit="ms"),
    MenuItem(147, "ANTI VOX GAIN", "VOX", kind="int", digits=3, min=0, max=100),
    MenuItem(148, "DATA VOX GAIN", "VOX", kind="int", digits=3, min=0, max=100),
    MenuItem(149, "DATA VOX DELAY", "VOX", kind="int", digits=4, min=30, max=3000, step=10, unit="ms"),
    MenuItem(150, "ANTI DVOX GAIN", "VOX", kind="int", digits=3, min=0, max=100),
    # --- Misc ---
    MenuItem(151, "EMERGENCY FREQ TX", "Misc", kind="enum", digits=1, options=_DISEN),
    MenuItem(152, "PRT/WIRES FREQ", "Misc", kind="enum", digits=1, options=["MANUAL", "PRESET"]),
    MenuItem(153, "PRESET FREQUENCY", "Misc", kind="int", digits=8, min=30000, max=47000000, unit="Hz"),
    MenuItem(154, "SEARCH SETUP", "Misc", kind="enum", digits=1, options=["HISTORY", "ACTIVITY"]),
]
