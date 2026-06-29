"""Round-trip tests for menu_engine — run: python -m backend.menu_engine_test"""
from backend.profiles import MenuItem
from backend import menu_engine as me

CAT_RTS = MenuItem(33, "CAT RTS", "CAT", kind="enum", digits=1, options=["DISABLE", "ENABLE"], critical=True)
TX_TOT = MenuItem(36, "TX TOT", "MISC", kind="int", digits=2, min=0, max=30, unit="min")
PC_KEY = MenuItem(60, "PC KEYING", "CW", kind="enum", digits=1, options=["OFF", "DAKY", "RTS", "DTR"], critical=True)
CAT_RATE = MenuItem(31, "CAT RATE", "CAT", kind="enum", digits=1, options=["4800", "9600", "19200", "38400"], critical=True)
OTHER_DISP = MenuItem(64, "OTHER DISP (SSB)", "MODE-SSB", kind="signed-int", digits=5, min=-3000, max=3000, step=10, unit="Hz")
RADIO_ID = MenuItem(87, "RADIO ID", "MISC", kind="enum", digits=1, options=[], readonly=True)
AGC_FAST = MenuItem(1, "AGC FAST DELAY", "AGC", kind="int", digits=4, min=20, max=4000, step=20, unit="msec")

_ok = True


def C(label, got, want):
    global _ok
    good = got == want
    _ok = _ok and good
    print(("PASS" if good else "FAIL"), label, "->", repr(got), "" if good else f"(want {want!r})")


# the three commands the working app already sends prove the wire format:
C("read EX033", me.yaesu_read_cmd(CAT_RTS), "EX033;")
C("EX033 DISABLE", me.yaesu_encode(CAT_RTS, "DISABLE"), "EX0330;")
C("EX033 ENABLE", me.yaesu_encode(CAT_RTS, "ENABLE"), "EX0331;")
C("EX033 idx 0", me.yaesu_encode(CAT_RTS, 0), "EX0330;")
C("EX033 decode", me.yaesu_decode(CAT_RTS, "EX0330;"), "DISABLE")
C("EX036 set 2 (=tot_cat)", me.yaesu_encode(TX_TOT, 2), "EX03602;")
C("EX036 decode", me.yaesu_decode(TX_TOT, "EX03602;"), 2)
C("EX036 clamp 45->30", me.yaesu_encode(TX_TOT, 45), "EX03630;")
C("EX060 DTR", me.yaesu_encode(PC_KEY, "DTR"), "EX0603;")
C("EX060 OFF", me.yaesu_encode(PC_KEY, "OFF"), "EX0600;")
C("EX060 decode", me.yaesu_decode(PC_KEY, "EX0603;"), "DTR")
C("EX031 38400", me.yaesu_encode(CAT_RATE, "38400"), "EX0313;")
C("EX031 decode", me.yaesu_decode(CAT_RATE, "EX0313;"), "38400")
C("EX064 signed -1500", me.yaesu_encode(OTHER_DISP, -1500), "EX064-1500;")
C("EX064 signed +0", me.yaesu_encode(OTHER_DISP, 0), "EX064+0000;")
C("EX064 signed +1500", me.yaesu_encode(OTHER_DISP, 1500), "EX064+1500;")
C("EX064 decode -1500", me.yaesu_decode(OTHER_DISP, "EX064-1500;"), -1500)
C("EX064 decode +0", me.yaesu_decode(OTHER_DISP, "EX064+0000;"), 0)
C("EX001 int 1000", me.yaesu_encode(AGC_FAST, 1000), "EX0011000;")
C("EX001 decode", me.yaesu_decode(AGC_FAST, "EX0011000;"), 1000)
C("decode wrong num -> None", me.yaesu_decode(CAT_RTS, "EX0361;"), None)

try:
    me.yaesu_encode(RADIO_ID, 0)
    C("RADIO_ID readonly raises", "no-raise", "MenuError")
except me.MenuError:
    C("RADIO_ID readonly raises", "MenuError", "MenuError")

print("\nALL PASS" if _ok else "\nSOME FAILED")
