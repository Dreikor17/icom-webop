"""FT-891 SET-menu table — all 159 items across 18 groups, for the data-driven Settings tab.

Compiled from the *FT-891 CAT Operation Reference Book* (docs/FT-891_CAT_OM_ENG_1909-C.pdf),
which lists every menu function with its parameter set and on-the-wire ``Digits`` width.

The FT-891 menu is grouped (GG-NN, e.g. 05-14 TX TOT) and read/written over CAT as
``EX<GGNN><value>;`` — a 4-digit menu number, so every item carries ``ex_width=4`` (the
FT-991A uses a flat 3-digit EXNNN). See backend/menu_engine.py. `digits` is the manual's
value-field width verbatim; for ``signed-int`` it includes the leading sign char.

`critical=True` marks connection/transmit-sensitive items (CAT link, PC keying, PTT/port
routing, TX time-out, per-band max power, tuner select, factory reset) so the UI confirms
before writing. 18-xx VERSION items are read-only.

Built + adversarially verified from the manual, then cross-checked against a deterministic
parse of the manual table. VERIFY a sample of `digits` on the real radio (read -> echo)
before fully trusting the table — a wrong width is silently ignored (see docs/ADDING-A-RADIO.md).
"""
from ..profiles import MenuItem

FT891_MENU = [

    # --- AGC ---
    MenuItem(101, "AGC FAST DELAY", "AGC", kind="int", digits=4, ex_width=4, min=20, max=4000, step=20, unit="ms"),
    MenuItem(102, "AGC MID DELAY", "AGC", kind="int", digits=4, ex_width=4, min=20, max=4000, step=20, unit="ms"),
    MenuItem(103, "AGC SLOW DELAY", "AGC", kind="int", digits=4, ex_width=4, min=20, max=4000, step=20, unit="ms"),
    # --- Display ---
    MenuItem(201, "LCD CONTRAST", "Display", kind="int", digits=2, ex_width=4, min=1, max=15),
    MenuItem(202, "DIMMER BACKLIT", "Display", kind="int", digits=2, ex_width=4, min=1, max=15),
    MenuItem(203, "DIMMER LCD", "Display", kind="int", digits=2, ex_width=4, min=1, max=15),
    MenuItem(204, "DIMMER TX/BUSY", "Display", kind="int", digits=2, ex_width=4, min=1, max=15),
    MenuItem(205, "PEAK HOLD", "Display", kind="enum", digits=1, ex_width=4, options=["OFF", "0.5 sec", "1.0 sec", "2.0 sec"]),
    MenuItem(206, "ZIN LED", "Display", kind="enum", digits=1, ex_width=4, options=["DISABLE", "ENABLE"]),
    MenuItem(207, "POP-UP MENU", "Display", kind="enum", digits=1, ex_width=4, options=["UPPER", "LOWER"]),
    # --- DVS ---
    MenuItem(301, "DVS RX OUT LVL", "DVS", kind="int", digits=3, ex_width=4, min=0, max=100),
    MenuItem(302, "DVS TX OUT LVL", "DVS", kind="int", digits=3, ex_width=4, min=0, max=100),
    # --- CW Keyer ---
    MenuItem(401, "KEYER TYPE", "CW Keyer", kind="enum", digits=1, ex_width=4, options=["OFF", "BUG", "ELEKEY-A", "ELEKEY-B", "ELEKEY-Y", "ACS"]),
    MenuItem(402, "KEYER DOT/DASH", "CW Keyer", kind="enum", digits=1, ex_width=4, options=["NOR", "REV"]),
    MenuItem(403, "CW WEIGHT", "CW Keyer", kind="int", digits=2, ex_width=4, min=25, max=45, note="display = value/10"),
    MenuItem(404, "BEACON INTERVAL", "CW Keyer", kind="int", digits=3, ex_width=4, min=0, max=690, unit="s", note="0 = OFF"),
    MenuItem(405, "NUMBER STYLE", "CW Keyer", kind="enum", digits=1, ex_width=4, options=["1290", "AUNO", "AUNT", "A2NO", "A2NT", "12NO", "12NT"]),
    MenuItem(406, "CONTEST NUMBER", "CW Keyer", kind="int", digits=4, ex_width=4, min=0, max=9999),
    MenuItem(407, "CW MEMORY 1", "CW Keyer", kind="enum", digits=1, ex_width=4, options=["TEXT", "MESSAGE"]),
    MenuItem(408, "CW MEMORY 2", "CW Keyer", kind="enum", digits=1, ex_width=4, options=["TEXT", "MESSAGE"]),
    MenuItem(409, "CW MEMORY 3", "CW Keyer", kind="enum", digits=1, ex_width=4, options=["TEXT", "MESSAGE"]),
    MenuItem(410, "CW MEMORY 4", "CW Keyer", kind="enum", digits=1, ex_width=4, options=["TEXT", "MESSAGE"]),
    MenuItem(411, "CW MEMORY 5", "CW Keyer", kind="enum", digits=1, ex_width=4, options=["TEXT", "MESSAGE"]),
    # --- General ---
    MenuItem(501, "NB WIDTH", "General", kind="enum", digits=1, ex_width=4, options=["1 msec", "3 msec", "10 msec"]),
    MenuItem(502, "NB REJECTION", "General", kind="enum", digits=1, ex_width=4, options=["10 dB", "30 dB", "50 dB"]),
    MenuItem(503, "NB LEVEL", "General", kind="int", digits=2, ex_width=4, min=0, max=10),
    MenuItem(504, "BEEP LEVEL", "General", kind="int", digits=3, ex_width=4, min=0, max=100),
    MenuItem(505, "RF/SQL VR", "General", kind="enum", digits=1, ex_width=4, options=["RF", "SQL"]),
    MenuItem(506, "CAT RATE", "General", kind="enum", digits=1, ex_width=4, options=["4800 bps", "9600 bps", "19200 bps", "38400 bps"], critical=True),
    MenuItem(507, "CAT TOT", "General", kind="enum", digits=1, ex_width=4, options=["10 msec", "100 msec", "1000 msec", "3000 msec"], critical=True),
    MenuItem(508, "CAT RTS", "General", kind="enum", digits=1, ex_width=4, options=["DISABLE", "ENABLE"], critical=True),
    MenuItem(509, "MEM GROUP", "General", kind="enum", digits=1, ex_width=4, options=["DISABLE", "ENABLE"]),
    MenuItem(510, "FM SETTING", "General", kind="enum", digits=1, ex_width=4, options=["DISABLE", "ENABLE"]),
    MenuItem(511, "REC SETTING", "General", kind="enum", digits=1, ex_width=4, options=["DISABLE", "ENABLE"]),
    MenuItem(512, "ATAS SETTING", "General", kind="enum", digits=1, ex_width=4, options=["DISABLE", "ENABLE"]),
    MenuItem(513, "QUICK SPL FREQ", "General", kind="signed-int", digits=3, ex_width=4, min=-20, max=20, unit="kHz"),
    MenuItem(514, "TX TOT", "General", kind="int", digits=2, ex_width=4, min=0, max=30, unit="min", critical=True, note="0 = OFF"),
    MenuItem(515, "MIC SCAN", "General", kind="enum", digits=1, ex_width=4, options=["DISABLE", "ENABLE"]),
    MenuItem(516, "MIC SCAN RESUME", "General", kind="enum", digits=1, ex_width=4, options=["PAUSE", "TIME"]),
    MenuItem(517, "REF FREQ ADJ", "General", kind="signed-int", digits=3, ex_width=4, min=-25, max=25),
    MenuItem(518, "CLAR SELECT", "General", kind="enum", digits=1, ex_width=4, options=["RX", "TX", "TRX"]),
    MenuItem(519, "APO", "General", kind="enum", digits=1, ex_width=4, options=["OFF", "1 h", "2 h", "4 h", "6 h", "8 h", "10 h", "12 h"]),
    MenuItem(520, "FAN CONTROL", "General", kind="enum", digits=1, ex_width=4, options=["NORMAL", "CONTEST"]),
    # --- AM ---
    MenuItem(601, "AM LCUT FREQ", "AM", kind="enum", digits=2, ex_width=4, options=["OFF", "100 Hz", "150 Hz", "200 Hz", "250 Hz", "300 Hz", "350 Hz", "400 Hz", "450 Hz", "500 Hz", "550 Hz", "600 Hz", "650 Hz", "700 Hz", "750 Hz", "800 Hz", "850 Hz", "900 Hz", "950 Hz", "1000 Hz"]),
    MenuItem(602, "AM LCUT SLOPE", "AM", kind="enum", digits=1, ex_width=4, options=["6 dB/oct", "18 dB/oct"]),
    MenuItem(603, "AM HCUT FREQ", "AM", kind="enum", digits=2, ex_width=4, options=["OFF", "700 Hz", "750 Hz", "800 Hz", "850 Hz", "900 Hz", "950 Hz", "1000 Hz", "1050 Hz", "1100 Hz", "1150 Hz", "1200 Hz", "1250 Hz", "1300 Hz", "1350 Hz", "1400 Hz", "1450 Hz", "1500 Hz", "1550 Hz", "1600 Hz", "1650 Hz", "1700 Hz", "1750 Hz", "1800 Hz", "1850 Hz", "1900 Hz", "1950 Hz", "2000 Hz", "2050 Hz", "2100 Hz", "2150 Hz", "2200 Hz", "2250 Hz", "2300 Hz", "2350 Hz", "2400 Hz", "2450 Hz", "2500 Hz", "2550 Hz", "2600 Hz", "2650 Hz", "2700 Hz", "2750 Hz", "2800 Hz", "2850 Hz", "2900 Hz", "2950 Hz", "3000 Hz", "3050 Hz", "3100 Hz", "3150 Hz", "3200 Hz", "3250 Hz", "3300 Hz", "3350 Hz", "3400 Hz", "3450 Hz", "3500 Hz", "3550 Hz", "3600 Hz", "3650 Hz", "3700 Hz", "3750 Hz", "3800 Hz", "3850 Hz", "3900 Hz", "3950 Hz", "4000 Hz"]),
    MenuItem(604, "AM HCUT SLOPE", "AM", kind="enum", digits=1, ex_width=4, options=["6 dB/oct", "18 dB/oct"]),
    MenuItem(605, "AM MIC SELECT", "AM", kind="enum", digits=1, ex_width=4, options=["MIC", "REAR"]),
    MenuItem(606, "AM OUT LEVEL", "AM", kind="int", digits=3, ex_width=4, min=0, max=100),
    MenuItem(607, "AM PTT SELECT", "AM", kind="enum", digits=1, ex_width=4, options=["DAKY", "RTS", "DTR"], critical=True),
    # --- CW ---
    MenuItem(701, "CW LCUT FREQ", "CW", kind="enum", digits=2, ex_width=4, options=["OFF", "100 Hz", "150 Hz", "200 Hz", "250 Hz", "300 Hz", "350 Hz", "400 Hz", "450 Hz", "500 Hz", "550 Hz", "600 Hz", "650 Hz", "700 Hz", "750 Hz", "800 Hz", "850 Hz", "900 Hz", "950 Hz", "1000 Hz"]),
    MenuItem(702, "CW LCUT SLOPE", "CW", kind="enum", digits=1, ex_width=4, options=["6 dB/oct", "18 dB/oct"]),
    MenuItem(703, "CW HCUT FREQ", "CW", kind="enum", digits=2, ex_width=4, options=["OFF", "700 Hz", "750 Hz", "800 Hz", "850 Hz", "900 Hz", "950 Hz", "1000 Hz", "1050 Hz", "1100 Hz", "1150 Hz", "1200 Hz", "1250 Hz", "1300 Hz", "1350 Hz", "1400 Hz", "1450 Hz", "1500 Hz", "1550 Hz", "1600 Hz", "1650 Hz", "1700 Hz", "1750 Hz", "1800 Hz", "1850 Hz", "1900 Hz", "1950 Hz", "2000 Hz", "2050 Hz", "2100 Hz", "2150 Hz", "2200 Hz", "2250 Hz", "2300 Hz", "2350 Hz", "2400 Hz", "2450 Hz", "2500 Hz", "2550 Hz", "2600 Hz", "2650 Hz", "2700 Hz", "2750 Hz", "2800 Hz", "2850 Hz", "2900 Hz", "2950 Hz", "3000 Hz", "3050 Hz", "3100 Hz", "3150 Hz", "3200 Hz", "3250 Hz", "3300 Hz", "3350 Hz", "3400 Hz", "3450 Hz", "3500 Hz", "3550 Hz", "3600 Hz", "3650 Hz", "3700 Hz", "3750 Hz", "3800 Hz", "3850 Hz", "3900 Hz", "3950 Hz", "4000 Hz"]),
    MenuItem(704, "CW HCUT SLOPE", "CW", kind="enum", digits=1, ex_width=4, options=["6 dB/oct", "18 dB/oct"]),
    MenuItem(705, "CW OUT LEVEL", "CW", kind="int", digits=3, ex_width=4, min=0, max=100),
    MenuItem(706, "CW AUTO MODE", "CW", kind="enum", digits=1, ex_width=4, options=["OFF", "50M", "ON"]),
    MenuItem(707, "CW BFO", "CW", kind="enum", digits=1, ex_width=4, options=["USB", "LSB", "AUTO"]),
    MenuItem(708, "CW BK-IN TYPE", "CW", kind="enum", digits=1, ex_width=4, options=["SEMI", "FULL"]),
    MenuItem(709, "CW BK-IN DELAY", "CW", kind="int", digits=4, ex_width=4, min=30, max=3000, step=10, unit="ms"),
    MenuItem(710, "CW WAVE SHAPE", "CW", kind="enum", digits=1, ex_width=4, options=["", "2 msec", "4 msec"], note="index 0 unused; options start at index 1"),
    MenuItem(711, "CW FREQ DISPLAY", "CW", kind="enum", digits=1, ex_width=4, options=["FREQ", "PITCH"]),
    MenuItem(712, "PC KEYING", "CW", kind="enum", digits=1, ex_width=4, options=["OFF", "DAKY", "RTS", "DTR"], critical=True),
    MenuItem(713, "QSK DELAY TIME", "CW", kind="enum", digits=1, ex_width=4, options=["15 msec", "20 msec", "25 msec", "30 msec"]),
    # --- DATA ---
    MenuItem(801, "DATA MODE", "DATA", kind="enum", digits=1, ex_width=4, options=["PSK", "OTHERS"]),
    MenuItem(802, "PSK TONE", "DATA", kind="enum", digits=1, ex_width=4, options=["1000 Hz", "1500 Hz", "2000 Hz"]),
    MenuItem(803, "OTHER DISP", "DATA", kind="signed-int", digits=5, ex_width=4, min=-3000, max=3000, step=10, unit="Hz"),
    MenuItem(804, "OTHER SHIFT", "DATA", kind="signed-int", digits=5, ex_width=4, min=-3000, max=3000, step=10, unit="Hz"),
    MenuItem(805, "DATA LCUT FREQ", "DATA", kind="enum", digits=2, ex_width=4, options=["OFF", "100 Hz", "150 Hz", "200 Hz", "250 Hz", "300 Hz", "350 Hz", "400 Hz", "450 Hz", "500 Hz", "550 Hz", "600 Hz", "650 Hz", "700 Hz", "750 Hz", "800 Hz", "850 Hz", "900 Hz", "950 Hz", "1000 Hz"]),
    MenuItem(806, "DATA LCUT SLOPE", "DATA", kind="enum", digits=1, ex_width=4, options=["6 dB/oct", "18 dB/oct"]),
    MenuItem(807, "DATA HCUT FREQ", "DATA", kind="enum", digits=2, ex_width=4, options=["OFF", "700 Hz", "750 Hz", "800 Hz", "850 Hz", "900 Hz", "950 Hz", "1000 Hz", "1050 Hz", "1100 Hz", "1150 Hz", "1200 Hz", "1250 Hz", "1300 Hz", "1350 Hz", "1400 Hz", "1450 Hz", "1500 Hz", "1550 Hz", "1600 Hz", "1650 Hz", "1700 Hz", "1750 Hz", "1800 Hz", "1850 Hz", "1900 Hz", "1950 Hz", "2000 Hz", "2050 Hz", "2100 Hz", "2150 Hz", "2200 Hz", "2250 Hz", "2300 Hz", "2350 Hz", "2400 Hz", "2450 Hz", "2500 Hz", "2550 Hz", "2600 Hz", "2650 Hz", "2700 Hz", "2750 Hz", "2800 Hz", "2850 Hz", "2900 Hz", "2950 Hz", "3000 Hz", "3050 Hz", "3100 Hz", "3150 Hz", "3200 Hz", "3250 Hz", "3300 Hz", "3350 Hz", "3400 Hz", "3450 Hz", "3500 Hz", "3550 Hz", "3600 Hz", "3650 Hz", "3700 Hz", "3750 Hz", "3800 Hz", "3850 Hz", "3900 Hz", "3950 Hz", "4000 Hz"]),
    MenuItem(808, "DATA HCUT SLOPE", "DATA", kind="enum", digits=1, ex_width=4, options=["6 dB/oct", "18 dB/oct"]),
    MenuItem(809, "DATA IN SELECT", "DATA", kind="enum", digits=1, ex_width=4, options=["MIC", "REAR"]),
    MenuItem(810, "DATA PTT SELECT", "DATA", kind="enum", digits=1, ex_width=4, options=["DAKY", "RTS", "DTR"], critical=True),
    MenuItem(811, "DATA OUT LEVEL", "DATA", kind="int", digits=3, ex_width=4, min=0, max=100),
    MenuItem(812, "DATA BFO", "DATA", kind="enum", digits=1, ex_width=4, options=["USB", "LSB"]),
    # --- FM ---
    MenuItem(901, "FM MIC SELECT", "FM", kind="enum", digits=1, ex_width=4, options=["MIC", "REAR"]),
    MenuItem(902, "FM OUT LEVEL", "FM", kind="int", digits=3, ex_width=4, min=0, max=100),
    MenuItem(903, "PKT PTT SELECT", "FM", kind="enum", digits=1, ex_width=4, options=["DAKY", "RTS", "DTR"], critical=True),
    MenuItem(904, "RPT SHIFT 28MHz", "FM", kind="int", digits=4, ex_width=4, min=0, max=1000, step=10, unit="kHz"),
    MenuItem(905, "RPT SHIFT 50MHz", "FM", kind="int", digits=1, ex_width=4, min=0, max=4000, step=10, unit="kHz"),
    MenuItem(906, "DCS POLARITY", "FM", kind="enum", digits=1, ex_width=4, options=["Tn-Rn", "Tn-Riv", "Tiv-Rn", "Tiv-Riv"]),
    # --- RTTY ---
    MenuItem(1001, "RTTY LCUT FREQ", "RTTY", kind="enum", digits=2, ex_width=4, options=["OFF", "100 Hz", "150 Hz", "200 Hz", "250 Hz", "300 Hz", "350 Hz", "400 Hz", "450 Hz", "500 Hz", "550 Hz", "600 Hz", "650 Hz", "700 Hz", "750 Hz", "800 Hz", "850 Hz", "900 Hz", "950 Hz", "1000 Hz"]),
    MenuItem(1002, "RTTY LCUT SLOPE", "RTTY", kind="enum", digits=1, ex_width=4, options=["6 dB/oct", "18 dB/oct"]),
    MenuItem(1003, "RTTY HCUT FREQ", "RTTY", kind="enum", digits=2, ex_width=4, options=["OFF", "700 Hz", "750 Hz", "800 Hz", "850 Hz", "900 Hz", "950 Hz", "1000 Hz", "1050 Hz", "1100 Hz", "1150 Hz", "1200 Hz", "1250 Hz", "1300 Hz", "1350 Hz", "1400 Hz", "1450 Hz", "1500 Hz", "1550 Hz", "1600 Hz", "1650 Hz", "1700 Hz", "1750 Hz", "1800 Hz", "1850 Hz", "1900 Hz", "1950 Hz", "2000 Hz", "2050 Hz", "2100 Hz", "2150 Hz", "2200 Hz", "2250 Hz", "2300 Hz", "2350 Hz", "2400 Hz", "2450 Hz", "2500 Hz", "2550 Hz", "2600 Hz", "2650 Hz", "2700 Hz", "2750 Hz", "2800 Hz", "2850 Hz", "2900 Hz", "2950 Hz", "3000 Hz", "3050 Hz", "3100 Hz", "3150 Hz", "3200 Hz", "3250 Hz", "3300 Hz", "3350 Hz", "3400 Hz", "3450 Hz", "3500 Hz", "3550 Hz", "3600 Hz", "3650 Hz", "3700 Hz", "3750 Hz", "3800 Hz", "3850 Hz", "3900 Hz", "3950 Hz", "4000 Hz"]),
    MenuItem(1004, "RTTY HCUT SLOPE", "RTTY", kind="enum", digits=1, ex_width=4, options=["6 dB/oct", "18 dB/oct"]),
    MenuItem(1005, "RTTY SHIFT PORT", "RTTY", kind="enum", digits=1, ex_width=4, options=["SHIFT", "DTR", "RTS"], critical=True),
    MenuItem(1006, "RTTY POLARITY-R", "RTTY", kind="enum", digits=1, ex_width=4, options=["NOR", "REV"]),
    MenuItem(1007, "RTTY POLARITY-T", "RTTY", kind="enum", digits=1, ex_width=4, options=["NOR", "REV"]),
    MenuItem(1008, "RTTY OUT LEVEL", "RTTY", kind="int", digits=3, ex_width=4, min=0, max=100),
    MenuItem(1009, "RTTY SHIFT FREQ", "RTTY", kind="enum", digits=1, ex_width=4, options=["170 Hz", "200 Hz", "425 Hz", "850 Hz"]),
    MenuItem(1010, "RTTY MARK FREQ", "RTTY", kind="enum", digits=1, ex_width=4, options=["1275 Hz", "2125 Hz"]),
    MenuItem(1011, "RTTY BFO", "RTTY", kind="enum", digits=1, ex_width=4, options=["USB", "LSB"]),
    # --- SSB ---
    MenuItem(1101, "SSB LCUT FREQ", "SSB", kind="enum", digits=2, ex_width=4, options=["OFF", "100 Hz", "150 Hz", "200 Hz", "250 Hz", "300 Hz", "350 Hz", "400 Hz", "450 Hz", "500 Hz", "550 Hz", "600 Hz", "650 Hz", "700 Hz", "750 Hz", "800 Hz", "850 Hz", "900 Hz", "950 Hz", "1000 Hz"]),
    MenuItem(1102, "SSB LCUT SLOPE", "SSB", kind="enum", digits=1, ex_width=4, options=["6 dB/oct", "18 dB/oct"]),
    MenuItem(1103, "SSB HCUT FREQ", "SSB", kind="enum", digits=2, ex_width=4, options=["OFF", "700 Hz", "750 Hz", "800 Hz", "850 Hz", "900 Hz", "950 Hz", "1000 Hz", "1050 Hz", "1100 Hz", "1150 Hz", "1200 Hz", "1250 Hz", "1300 Hz", "1350 Hz", "1400 Hz", "1450 Hz", "1500 Hz", "1550 Hz", "1600 Hz", "1650 Hz", "1700 Hz", "1750 Hz", "1800 Hz", "1850 Hz", "1900 Hz", "1950 Hz", "2000 Hz", "2050 Hz", "2100 Hz", "2150 Hz", "2200 Hz", "2250 Hz", "2300 Hz", "2350 Hz", "2400 Hz", "2450 Hz", "2500 Hz", "2550 Hz", "2600 Hz", "2650 Hz", "2700 Hz", "2750 Hz", "2800 Hz", "2850 Hz", "2900 Hz", "2950 Hz", "3000 Hz", "3050 Hz", "3100 Hz", "3150 Hz", "3200 Hz", "3250 Hz", "3300 Hz", "3350 Hz", "3400 Hz", "3450 Hz", "3500 Hz", "3550 Hz", "3600 Hz", "3650 Hz", "3700 Hz", "3750 Hz", "3800 Hz", "3850 Hz", "3900 Hz", "3950 Hz", "4000 Hz"]),
    MenuItem(1104, "SSB HCUT SLOPE", "SSB", kind="enum", digits=1, ex_width=4, options=["6 dB/oct", "18 dB/oct"]),
    MenuItem(1105, "SSB MIC SELECT", "SSB", kind="enum", digits=1, ex_width=4, options=["MIC", "REAR"]),
    MenuItem(1106, "SSB OUT LEVEL", "SSB", kind="int", digits=3, ex_width=4, min=0, max=100),
    MenuItem(1107, "SSB BFO", "SSB", kind="enum", digits=1, ex_width=4, options=["USB", "LSB", "AUTO"]),
    MenuItem(1108, "SSB PTT SELECT", "SSB", kind="enum", digits=1, ex_width=4, options=["DAKY", "RTS", "DTR"], critical=True),
    MenuItem(1109, "SSB TX BPF", "SSB", kind="enum", digits=1, ex_width=4, options=["100-3000", "100-2900", "200-2800", "300-2700", "400-2600"]),
    # --- Contour/Notch ---
    MenuItem(1201, "APF WIDTH", "Contour/Notch", kind="enum", digits=1, ex_width=4, options=["NARROW", "MEDIUM", "WIDE"]),
    MenuItem(1202, "CONTOUR LEVEL", "Contour/Notch", kind="signed-int", digits=3, ex_width=4, min=-40, max=20),
    MenuItem(1203, "CONTOUR WIDTH", "Contour/Notch", kind="int", digits=2, ex_width=4, min=1, max=11),
    MenuItem(1204, "IF NOTCH WIDTH", "Contour/Notch", kind="enum", digits=1, ex_width=4, options=["NARROW", "WIDE"]),
    # --- Scope ---
    MenuItem(1301, "SCP START CYCLE", "Scope", kind="enum", digits=1, ex_width=4, options=["OFF", "3 sec", "5 sec", "10 sec"]),
    MenuItem(1302, "SCP SPAN FREQ", "Scope", kind="enum", digits=1, ex_width=4, options=["37.5 kHz", "75 kHz", "150 kHz", "375 kHz", "750 kHz"]),
    # --- Tuning ---
    MenuItem(1401, "QUICK DIAL", "Tuning", kind="enum", digits=1, ex_width=4, options=["50 kHz", "100 kHz", "500 kHz"]),
    MenuItem(1402, "SSB DIAL STEP", "Tuning", kind="enum", digits=1, ex_width=4, options=["2 Hz", "5 Hz", "10 Hz"]),
    MenuItem(1403, "AM DIAL STEP", "Tuning", kind="enum", digits=1, ex_width=4, options=["10 Hz", "100 Hz"]),
    MenuItem(1404, "FM DIAL STEP", "Tuning", kind="enum", digits=1, ex_width=4, options=["10 Hz", "100 Hz"]),
    MenuItem(1405, "DIAL STEP", "Tuning", kind="enum", digits=1, ex_width=4, options=["2 Hz", "5 Hz", "10 Hz"]),
    MenuItem(1406, "AM CH STEP", "Tuning", kind="enum", digits=1, ex_width=4, options=["2.5 kHz", "5 kHz", "9 kHz", "10 kHz", "12.5 kHz", "25 kHz"]),
    MenuItem(1407, "FM CH STEP", "Tuning", kind="enum", digits=1, ex_width=4, options=["5 kHz", "6.25 kHz", "10 kHz", "12.5 kHz", "15 kHz", "20 kHz", "25 kHz"]),
    # --- Equalizer ---
    MenuItem(1501, "EQ1 FREQ", "Equalizer", kind="enum", digits=2, ex_width=4, options=["OFF", "100 Hz", "200 Hz", "300 Hz", "400 Hz", "500 Hz", "600 Hz", "700 Hz"]),
    MenuItem(1502, "EQ1 LEVEL", "Equalizer", kind="signed-int", digits=3, ex_width=4, min=-20, max=10),
    MenuItem(1503, "EQ1 BWTH", "Equalizer", kind="int", digits=2, ex_width=4, min=1, max=10),
    MenuItem(1504, "EQ2 FREQ", "Equalizer", kind="enum", digits=2, ex_width=4, options=["OFF", "700 Hz", "800 Hz", "900 Hz", "1000 Hz", "1100 Hz", "1200 Hz", "1300 Hz", "1400 Hz", "1500 Hz"]),
    MenuItem(1505, "EQ2 LEVEL", "Equalizer", kind="signed-int", digits=3, ex_width=4, min=-20, max=10),
    MenuItem(1506, "EQ2 BWTH", "Equalizer", kind="int", digits=2, ex_width=4, min=1, max=10),
    MenuItem(1507, "EQ3 FREQ", "Equalizer", kind="enum", digits=2, ex_width=4, options=["OFF", "1500 Hz", "1600 Hz", "1700 Hz", "1800 Hz", "1900 Hz", "2000 Hz", "2100 Hz", "2200 Hz", "2300 Hz", "2400 Hz", "2500 Hz", "2600 Hz", "2700 Hz", "2800 Hz", "2900 Hz", "3000 Hz", "3100 Hz", "3200 Hz"]),
    MenuItem(1508, "EQ3 LEVEL", "Equalizer", kind="signed-int", digits=3, ex_width=4, min=-20, max=10),
    MenuItem(1509, "EQ3 BWTH", "Equalizer", kind="int", digits=2, ex_width=4, min=1, max=10),
    MenuItem(1510, "P-EQ1 FREQ", "Equalizer", kind="enum", digits=2, ex_width=4, options=["OFF", "100 Hz", "200 Hz", "300 Hz", "400 Hz", "500 Hz", "600 Hz", "700 Hz"]),
    MenuItem(1511, "P-EQ1 LEVEL", "Equalizer", kind="signed-int", digits=3, ex_width=4, min=-20, max=10),
    MenuItem(1512, "P-EQ1 BWTH", "Equalizer", kind="int", digits=2, ex_width=4, min=1, max=10),
    MenuItem(1513, "P-EQ2 FREQ", "Equalizer", kind="enum", digits=2, ex_width=4, options=["OFF", "700 Hz", "800 Hz", "900 Hz", "1000 Hz", "1100 Hz", "1200 Hz", "1300 Hz", "1400 Hz", "1500 Hz"]),
    MenuItem(1514, "P-EQ2 LEVEL", "Equalizer", kind="signed-int", digits=3, ex_width=4, min=-20, max=10),
    MenuItem(1515, "P-EQ2 BWTH", "Equalizer", kind="int", digits=2, ex_width=4, min=1, max=10),
    MenuItem(1516, "P-EQ3 FREQ", "Equalizer", kind="enum", digits=2, ex_width=4, options=["OFF", "1500 Hz", "1600 Hz", "1700 Hz", "1800 Hz", "1900 Hz", "2000 Hz", "2100 Hz", "2200 Hz", "2300 Hz", "2400 Hz", "2500 Hz", "2600 Hz", "2700 Hz", "2800 Hz", "2900 Hz", "3000 Hz", "3100 Hz", "3200 Hz"]),
    MenuItem(1517, "P-EQ3 LEVEL", "Equalizer", kind="signed-int", digits=3, ex_width=4, min=-20, max=10),
    MenuItem(1518, "P-EQ3 BWTH", "Equalizer", kind="int", digits=2, ex_width=4, min=1, max=10),
    # --- TX/Audio ---
    MenuItem(1601, "HF SSB PWR", "TX/Audio", kind="int", digits=3, ex_width=4, min=5, max=100, unit="W", critical=True),
    MenuItem(1602, "HF AM PWR", "TX/Audio", kind="int", digits=3, ex_width=4, min=5, max=40, unit="W", critical=True),
    MenuItem(1603, "HF PWR", "TX/Audio", kind="int", digits=3, ex_width=4, min=5, max=100, unit="W", critical=True),
    MenuItem(1604, "50M SSB PWR", "TX/Audio", kind="int", digits=3, ex_width=4, min=5, max=100, unit="W", critical=True),
    MenuItem(1605, "50M AM PWR", "TX/Audio", kind="int", digits=3, ex_width=4, min=5, max=40, unit="W", critical=True),
    MenuItem(1606, "50M PWR", "TX/Audio", kind="int", digits=3, ex_width=4, min=5, max=100, unit="W", critical=True),
    MenuItem(1607, "SSB MIC GAIN", "TX/Audio", kind="int", digits=3, ex_width=4, min=0, max=100),
    MenuItem(1608, "AM MIC GAIN", "TX/Audio", kind="int", digits=3, ex_width=4, min=0, max=100),
    MenuItem(1609, "FM MIC GAIN", "TX/Audio", kind="int", digits=3, ex_width=4, min=0, max=100),
    MenuItem(1610, "DATA MIC GAIN", "TX/Audio", kind="int", digits=3, ex_width=4, min=0, max=100),
    MenuItem(1611, "SSB DATA GAIN", "TX/Audio", kind="int", digits=3, ex_width=4, min=0, max=100),
    MenuItem(1612, "AM DATA GAIN", "TX/Audio", kind="int", digits=3, ex_width=4, min=0, max=100),
    MenuItem(1613, "FM DATA GAIN", "TX/Audio", kind="int", digits=3, ex_width=4, min=0, max=100),
    MenuItem(1614, "DATA DATA GAIN", "TX/Audio", kind="int", digits=3, ex_width=4, min=0, max=100),
    MenuItem(1615, "TUNER SELECT", "TX/Audio", kind="enum", digits=1, ex_width=4, options=["OFF", "EXTERNAL", "ATAS", "LAMP"], critical=True),
    MenuItem(1616, "VOX SELECT", "TX/Audio", kind="enum", digits=1, ex_width=4, options=["MIC", "DATA"]),
    MenuItem(1617, "VOX GAIN", "TX/Audio", kind="int", digits=3, ex_width=4, min=0, max=100),
    MenuItem(1618, "VOX DELAY", "TX/Audio", kind="int", digits=4, ex_width=4, min=30, max=3000, step=10, unit="ms"),
    MenuItem(1619, "ANTI VOX GAIN", "TX/Audio", kind="int", digits=3, ex_width=4, min=0, max=100),
    MenuItem(1620, "DATA VOX GAIN", "TX/Audio", kind="int", digits=3, ex_width=4, min=0, max=100),
    MenuItem(1621, "DATA VOX DELAY", "TX/Audio", kind="int", digits=4, ex_width=4, min=30, max=3000, unit="ms"),
    MenuItem(1622, "ANTI DVOX GAIN", "TX/Audio", kind="int", digits=3, ex_width=4, min=0, max=100),
    MenuItem(1623, "EMERGENCY FREQ", "TX/Audio", kind="enum", digits=1, ex_width=4, options=["DISABLE", "ENABLE"]),
    # --- Reset ---
    MenuItem(1701, "RESET", "Reset", kind="enum", digits=1, ex_width=4, options=["ALL", "DATA", "FUNC"], critical=True),
    # --- Version ---
    MenuItem(1801, "MAIN VERSION", "Version", kind="int", digits=4, ex_width=4, min=0, max=9999, readonly=True, note="display = value/100 (V01-23 = 0123)"),
    MenuItem(1802, "DSP VERSION", "Version", kind="int", digits=4, ex_width=4, min=0, max=9999, readonly=True, note="display = value/100 (V01-23 = 0123)"),
    MenuItem(1803, "LCD VERSION", "Version", kind="int", digits=4, ex_width=4, min=0, max=9999, readonly=True, note="display = value/100 (V01-23 = 0123)"),
]
