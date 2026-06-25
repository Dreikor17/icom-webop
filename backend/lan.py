"""
LAN (network) transport for Icom radios using the proprietary RS-BA1 UDP
protocol — the same one wfview / RS-BA1 / kappanhang speak to the IC-9700.

This gives full CI-V control + the spectrum/waterfall over the network. The
CI-V byte stream tunneled over UDP port 50002 is identical to the USB CI-V
stream, so everything above this layer (civ.py, radio.py) is unchanged — a
LanTransport just feeds the same on_bytes(data) callback.

Three UDP streams (all to the radio's IP):
  * control 50001 — handshake, login/auth, keepalives, "open serial+audio"
  * serial  50002 — the CI-V byte tunnel (what we actually use)
  * audio   50003 — opened and drained for now (real audio is a later phase)

Protocol ported from the reverse-engineered, open-source kappanhang
(github.com/nonoo/kappanhang, MIT) and wfview. Not from any Icom spec.

Audio is NOT decoded yet; the stream is opened so the radio's session is happy.
"""
from __future__ import annotations

import random
import socket
import struct
import threading
import time
from typing import Callable, Optional

from .transport import Transport

CONTROL_PORT = 50001
SERIAL_PORT = 50002
AUDIO_PORT = 50003

_AUDIO_SAMPLE_RATE = 16000
_AUDIO_TX_CHUNK = (_AUDIO_SAMPLE_RATE // 50) * 2   # 20 ms of 16-bit mono = 640 B @ 16 kHz
_TX_SEQ_BUF_MS = 150
_MAX_SERIAL_CHUNK = 64           # split long CI-V frames across packets (radio re-joins on FE..FD)


# ---------------------------------------------------------------------------
# Login obfuscation (NOT encryption) — ported verbatim from kappanhang passcode.go
# ---------------------------------------------------------------------------
_SEQUENCE = {
    32: 0x47, 33: 0x5d, 34: 0x4c, 35: 0x42, 36: 0x66, 37: 0x20, 38: 0x23, 39: 0x46,
    40: 0x4e, 41: 0x57, 42: 0x45, 43: 0x3d, 44: 0x67, 45: 0x76, 46: 0x60, 47: 0x41,
    48: 0x62, 49: 0x39, 50: 0x59, 51: 0x2d, 52: 0x68, 53: 0x7e, 54: 0x7c, 55: 0x65,
    56: 0x7d, 57: 0x49, 58: 0x29, 59: 0x72, 60: 0x73, 61: 0x78, 62: 0x21, 63: 0x6e,
    64: 0x5a, 65: 0x5e, 66: 0x4a, 67: 0x3e, 68: 0x71, 69: 0x2c, 70: 0x2a, 71: 0x54,
    72: 0x3c, 73: 0x3a, 74: 0x63, 75: 0x4f, 76: 0x43, 77: 0x75, 78: 0x27, 79: 0x79,
    80: 0x5b, 81: 0x35, 82: 0x70, 83: 0x48, 84: 0x6b, 85: 0x56, 86: 0x6f, 87: 0x34,
    88: 0x32, 89: 0x6c, 90: 0x30, 91: 0x61, 92: 0x6d, 93: 0x7b, 94: 0x2f, 95: 0x4b,
    96: 0x64, 97: 0x38, 98: 0x2b, 99: 0x2e, 100: 0x50, 101: 0x40, 102: 0x3f, 103: 0x55,
    104: 0x33, 105: 0x37, 106: 0x25, 107: 0x77, 108: 0x24, 109: 0x26, 110: 0x74, 111: 0x6a,
    112: 0x28, 113: 0x53, 114: 0x4d, 115: 0x69, 116: 0x22, 117: 0x5c, 118: 0x44, 119: 0x31,
    120: 0x36, 121: 0x58, 122: 0x3b, 123: 0x7a, 124: 0x51, 125: 0x5f, 126: 0x52,
}


def passcode(s: str) -> bytes:
    res = bytearray(16)
    for i in range(min(len(s), 16)):
        p = ord(s[i]) + i
        if p > 126:
            p = 32 + p % 127
        res[i] = _SEQUENCE.get(p, 0)
    return bytes(res)


def _local_ip_for(host: str) -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect((host, 1))
        return s.getsockname()[0]
    except Exception:
        return "0.0.0.0"
    finally:
        s.close()


# ---------------------------------------------------------------------------
# One UDP stream (shared logic for control / serial / audio)
# ---------------------------------------------------------------------------
class _Stream:
    def __init__(self, name: str, host: str, port: int,
                 on_error: Callable[[str], None]) -> None:
        self.name = name
        self.host = host
        self.port = port
        self.on_error = on_error
        self.sock: Optional[socket.socket] = None
        self.local_sid = 0
        self.remote_sid = 0
        self.handle: Optional[Callable[[bytes], None]] = None
        self.periodic_hook: Optional[Callable[[], None]] = None
        self.is_serial = False
        self.use_pkt0_idle = True

        self._lock = threading.Lock()
        self._pkt0_seq = 1
        self._serial_seq = 0
        self._audio_seq = 0
        self._pkt7_seq = 1
        self._pkt7_inner = 0x8304
        self._txbuf: dict[int, bytes] = {}
        self._txbuf_order: list[int] = []
        self._last_real = 0.0
        self._last_idle = 0.0
        self._last_ping = 0.0
        self._stop = threading.Event()
        self._reader: Optional[threading.Thread] = None
        self._keepalive: Optional[threading.Thread] = None

    # -- socket / sids -------------------------------------------------------
    def open(self) -> None:
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Use an ephemeral local port. (kappanhang binds local == remote port,
        # but on Windows the radio won't answer a source port equal to its own
        # listening port — it just drops us. wfview uses ephemeral ports too.)
        self.sock.bind(("", 0))
        self.sock.connect((self.host, self.port))
        ip, lport = self.sock.getsockname()[0], self.sock.getsockname()[1]
        if ip == "0.0.0.0":
            ip = _local_ip_for(self.host)
        ip_int = struct.unpack(">I", socket.inet_aton(ip))[0]
        self.local_sid = ((ip_int << 16) | (lport & 0xFFFF)) & 0xFFFFFFFF

    def _hdr(self) -> bytes:
        return struct.pack(">I", self.local_sid) + struct.pack(">I", self.remote_sid)

    # -- raw / tracked send --------------------------------------------------
    def _raw(self, d: bytes) -> None:
        if self.sock:
            self.sock.send(d)

    def _raw_twice(self, d: bytes) -> None:
        self._raw(d); self._raw(d)

    def _send_tracked(self, p: bytearray, is_idle: bool = False) -> None:
        with self._lock:
            seq = self._pkt0_seq
            p[6] = seq & 0xFF
            p[7] = (seq >> 8) & 0xFF
            data = bytes(p)
            self._txbuf[seq] = data
            self._txbuf_order.append(seq)
            if len(self._txbuf_order) > 512:
                self._txbuf.pop(self._txbuf_order.pop(0), None)
            self._raw(data)
            self._pkt0_seq = (self._pkt0_seq + 1) & 0xFFFF
            now = time.monotonic()
            self._last_idle = now
            if not is_idle:
                self._last_real = now

    # -- handshake (synchronous; before reader thread starts) ----------------
    def handshake(self, timeout: float = 2.0) -> None:
        self._raw_twice(bytes([0x10, 0, 0, 0, 0x03, 0, 0, 0]) + self._hdr())
        r = self._expect(16, b"\x10\x00\x00\x00\x04\x00\x00\x00", timeout)
        self.remote_sid = struct.unpack(">I", r[8:12])[0]
        self._raw_twice(bytes([0x10, 0, 0, 0, 0x06, 0, 1, 0]) + self._hdr())
        self._expect(16, b"\x10\x00\x00\x00\x06\x00\x01\x00", timeout)

    def _expect(self, length: int, prefix: bytes, timeout: float) -> bytes:
        assert self.sock is not None
        self.sock.settimeout(timeout)
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            try:
                r = self.sock.recv(1600)
            except socket.timeout:
                break
            if len(r) == length and r[: len(prefix)] == prefix:
                return r
        raise RuntimeError(f"{self.name}: no answer from radio (check IP / network function / firewall)")

    # -- background threads --------------------------------------------------
    def start_threads(self) -> None:
        assert self.sock is not None
        self.sock.settimeout(0.4)
        self._reader = threading.Thread(target=self._read_loop, name=f"lan-{self.name}-rx", daemon=True)
        self._keepalive = threading.Thread(target=self._keepalive_loop, name=f"lan-{self.name}-ka", daemon=True)
        self._reader.start()
        self._keepalive.start()

    def _read_loop(self) -> None:
        while not self._stop.is_set():
            try:
                r = self.sock.recv(1600)  # type: ignore[union-attr]
            except socket.timeout:
                continue
            except OSError:
                break
            if not r:
                continue
            if _is_pkt7(r):
                self._handle_pkt7(r)
                continue
            if _is_retransmit(r):
                self._handle_retransmit(r)
                continue
            if _is_idle_pkt0(r):
                continue
            if self.handle:
                try:
                    self.handle(r)
                except Exception as exc:  # noqa: BLE001
                    self.on_error(f"{self.name}: {exc}")

    def _keepalive_loop(self) -> None:
        while not self._stop.is_set():
            now = time.monotonic()
            if self.use_pkt0_idle:
                interval = 0.1 if (now - self._last_real) < 1.0 else 1.0
                if now - self._last_idle >= interval:
                    self._send_idle(tracked=True)
            if now - self._last_ping >= 3.0:
                self._send_pkt7_initiate()
                self._last_ping = now
            if self.periodic_hook:
                try:
                    self.periodic_hook()
                except Exception as exc:  # noqa: BLE001
                    self.on_error(f"{self.name}: {exc}")
            time.sleep(0.05)

    # -- pkt0 idle + retransmit ---------------------------------------------
    def _send_idle(self, tracked: bool = True, seq: int = 0) -> None:
        p = bytearray([0x10, 0, 0, 0, 0, 0, seq & 0xFF, (seq >> 8) & 0xFF]) + self._hdr()
        if tracked:
            self._send_tracked(p, is_idle=True)
        else:
            self._raw(bytes(p))

    def _handle_retransmit(self, r: bytes) -> None:
        if r[:6] == b"\x10\x00\x00\x00\x01\x00":
            self._retransmit(r[6] | (r[7] << 8))
        elif r[:6] == b"\x18\x00\x00\x00\x01\x00":
            body = r[16:]
            for i in range(0, len(body) - 3, 4):
                start = body[i] | (body[i + 1] << 8)
                end = body[i + 2] | (body[i + 3] << 8)
                s = start
                for _ in range(0, 64):                 # bounded
                    self._retransmit(s)
                    if s == end:
                        break
                    s = (s + 1) & 0xFFFF

    def _retransmit(self, seq: int) -> None:
        d = self._txbuf.get(seq)
        if d:
            self._raw_twice(d)
        else:
            self._send_idle(tracked=False, seq=seq)
            self._send_idle(tracked=False, seq=seq)

    # -- pkt7 ping -----------------------------------------------------------
    def _send_pkt7(self, reply_id: bytes, seq: int, is_reply: bool) -> None:
        flag = 0x01 if is_reply else 0x00
        p = bytes([0x15, 0, 0, 0, 0x07, 0, seq & 0xFF, (seq >> 8) & 0xFF]) + self._hdr() + bytes([flag]) + reply_id
        self._raw(p)

    def _send_pkt7_initiate(self) -> None:
        rid = bytes([random.randint(0, 255), self._pkt7_inner & 0xFF, (self._pkt7_inner >> 8) & 0xFF, 0x06])
        self._pkt7_inner = (self._pkt7_inner + 1) & 0xFFFF
        self._send_pkt7(rid, self._pkt7_seq, is_reply=False)
        self._pkt7_seq = (self._pkt7_seq + 1) & 0xFFFF

    def _handle_pkt7(self, r: bytes) -> None:
        if r[16] == 0x00:                              # radio is pinging us -> reply
            self._send_pkt7(bytes(r[17:21]), r[6] | (r[7] << 8), is_reply=True)

    # -- serial (CI-V) framing ----------------------------------------------
    def send_serial_open(self, close: bool = False) -> None:
        magic = 0x00 if close else 0x05
        p = bytearray([0x16, 0, 0, 0, 0, 0, 0, 0]) + self._hdr() + bytearray(
            [0xC0, 0x01, 0x00, (self._serial_seq >> 8) & 0xFF, self._serial_seq & 0xFF, magic])
        self._send_tracked(p)
        self._serial_seq = (self._serial_seq + 1) & 0xFFFF

    def send_civ(self, data: bytes) -> None:
        for i in range(0, len(data), _MAX_SERIAL_CHUNK):
            chunk = data[i:i + _MAX_SERIAL_CHUNK]
            l = len(chunk)
            p = bytearray([(0x15 + l) & 0xFF, 0, 0, 0, 0, 0, 0, 0]) + self._hdr() + bytearray(
                [0xC1, l, 0x00, (self._serial_seq >> 8) & 0xFF, self._serial_seq & 0xFF]) + chunk
            self._send_tracked(p)
            self._serial_seq = (self._serial_seq + 1) & 0xFFFF

    # -- audio (TX) ----------------------------------------------------------
    def send_audio_packet(self, pcm: bytes) -> None:
        # TX audio packet mirroring the radio's RX format: total length at [0:2],
        # marker 0x80 (PC->radio), audio seq at [18:20], PCM length at [22:24],
        # PCM at [24:]. (At 16 kHz the radio uses single ~640-byte PCM packets.)
        n = len(pcm)
        total = 24 + n
        p = bytearray([total & 0xFF, (total >> 8) & 0xFF, 0, 0, 0, 0, 0, 0]) + self._hdr() + bytearray(
            [0x80, 0x00, (self._audio_seq >> 8) & 0xFF, self._audio_seq & 0xFF,
             0x00, 0x00, (n >> 8) & 0xFF, n & 0xFF]) + pcm
        self._send_tracked(p)
        self._audio_seq = (self._audio_seq + 1) & 0xFFFF

    # -- shutdown ------------------------------------------------------------
    def close(self) -> None:
        self._stop.set()
        try:
            if self.is_serial and self.sock:
                self.send_serial_open(close=True)
            if self.sock:
                self._raw_twice(bytes([0x10, 0, 0, 0, 0x05, 0, 0, 0]) + self._hdr())
        except Exception:  # noqa: BLE001
            pass
        for t in (self._reader, self._keepalive):
            if t:
                t.join(timeout=1.0)
        if self.sock:
            try:
                self.sock.close()
            except Exception:  # noqa: BLE001
                pass
            self.sock = None


# ---- packet predicates -----------------------------------------------------
def _is_pkt7(r: bytes) -> bool:
    return len(r) == 21 and r[1:6] == b"\x00\x00\x00\x07\x00"


def _is_idle_pkt0(r: bytes) -> bool:
    return len(r) == 16 and r[:6] == b"\x10\x00\x00\x00\x00\x00"


def _is_retransmit(r: bytes) -> bool:
    return len(r) >= 16 and (r[:6] == b"\x10\x00\x00\x00\x01\x00" or r[:6] == b"\x18\x00\x00\x00\x01\x00")


# ---------------------------------------------------------------------------
# LanTransport — orchestrates the three streams behind the Transport interface
# ---------------------------------------------------------------------------
class LanTransport(Transport):
    supports_audio = True

    def __init__(self, host: str, port: int = CONTROL_PORT,
                 user: str = "", password: str = "") -> None:
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self._on_bytes: Optional[Callable[[bytes], None]] = None
        self.on_audio: Optional[Callable[[bytes], None]] = None
        self._tx_audio_buf = bytearray()
        self._tx_audio_pkts = 0   # diagnostics: audio packets sent to the radio
        self._tx_audio_bytes = 0
        self._rx_audio_pkts = 0   # diagnostics: audio packets received from the radio

    def audio_stats(self) -> dict:
        return {"audio_open": self._audio is not None,
                "tx_pkts": self._tx_audio_pkts, "tx_bytes": self._tx_audio_bytes,
                "rx_pkts": self._rx_audio_pkts}

        self._ctrl: Optional[_Stream] = None
        self._serial: Optional[_Stream] = None
        self._audio: Optional[_Stream] = None

        self._serial_ready = threading.Event()
        self._error: Optional[str] = None

        self._auth_lock = threading.Lock()
        self._auth_inner = 0
        self._auth_id = b"\x00" * 6
        self._a8 = b"\x00" * 16
        self._auth_ok = False
        self._got_a8 = False
        self._requested = False
        self._serial_opened = False
        self._last_reauth = 0.0

    @property
    def name(self) -> str:
        return f"LAN {self.host}"

    # -- Transport interface -------------------------------------------------
    def start(self, on_bytes: Callable[[bytes], None]) -> None:
        self._on_bytes = on_bytes
        self._connect_control()
        self._serial_ready.wait(timeout=10.0)
        if self._serial is None:                       # opened? (event can also fire on error)
            self.stop()
            raise RuntimeError(self._error or
                "LAN connect timed out — no serial stream. Check the radio's IP, that "
                "Network Function is ON, the Control port (50001), and the network "
                "user/password.")

    def write(self, data: bytes) -> None:
        s = self._serial
        if s is None or not self._serial_ready.is_set():
            return
        try:
            s.send_civ(data)
        except Exception as exc:  # noqa: BLE001
            self._on_stream_error(f"serial write: {exc}")

    def stop(self) -> None:
        # Proper logout: deauth the control session so the radio releases it
        # immediately. Without this the radio holds the session until its idle
        # timeout and rejects the next login ("auth failed, try rebooting").
        c = self._ctrl
        if c is not None and c.sock is not None and self._auth_id != b"\x00" * 6:
            try:
                self._send_auth(c, 0x01)
                time.sleep(0.5)        # let the radio process the deauth / any retransmit
            except Exception:  # noqa: BLE001
                pass
        for s in (self._serial, self._audio, self._ctrl):
            if s:
                try:
                    s.close()
                except Exception:  # noqa: BLE001
                    pass
        self._serial = self._audio = self._ctrl = None

    # -- control stream bring-up --------------------------------------------
    def _connect_control(self) -> None:
        c = _Stream("control", self.host, self.port, self._on_stream_error)
        c.open()
        c.handshake()
        c._pkt0_seq = 1

        self._send_login(c)
        r = c._expect(96, b"\x60\x00\x00\x00\x00\x00\x01\x00", 3.0)
        if r[48:52] == b"\xff\xff\xff\xfe":
            raise RuntimeError("LAN login rejected — invalid network username/password.")
        self._auth_id = bytes(r[26:32])

        self._send_auth(c, 0x02)
        self._send_auth(c, 0x05)

        c.handle = self._on_control_packet
        c.periodic_hook = self._control_periodic
        c.start_threads()
        self._ctrl = c

    def _control_periodic(self) -> None:
        if self._auth_ok:
            now = time.monotonic()
            if now - self._last_reauth >= 60.0:
                self._last_reauth = now
                if self._ctrl:
                    self._send_auth(self._ctrl, 0x05)

    # -- control packet builders --------------------------------------------
    def _send_login(self, c: _Stream) -> None:
        with self._auth_lock:
            seq = self._auth_inner
            self._auth_inner += 1
        sid = random.randint(0, 0xFFFF)
        p = bytearray(128)
        p[0] = 0x80
        p[8:12] = struct.pack(">I", c.local_sid)
        p[12:16] = struct.pack(">I", c.remote_sid)
        p[16:25] = bytes([0x00, 0x00, 0x00, 0x70, 0x01, 0x00, 0x00, seq & 0xFF, (seq >> 8) & 0xFF])
        p[26] = sid & 0xFF
        p[27] = (sid >> 8) & 0xFF
        p[64:80] = passcode(self.user)
        p[80:96] = passcode(self.password)
        p[96:104] = b"\x69\x63\x6f\x6d\x2d\x70\x63\x00"   # "icom-pc"
        c._send_tracked(p)

    def _send_auth(self, c: _Stream, magic: int) -> None:
        with self._auth_lock:
            seq = self._auth_inner
            self._auth_inner += 1
        p = bytearray(64)
        p[0] = 0x40
        p[8:12] = struct.pack(">I", c.local_sid)
        p[12:16] = struct.pack(">I", c.remote_sid)
        p[16:26] = bytes([0x00, 0x00, 0x00, 0x30, 0x01, magic, 0x00, seq & 0xFF, (seq >> 8) & 0xFF, 0x00])
        p[26:32] = self._auth_id
        c._send_tracked(p)

    def _send_request_serial_audio(self, c: _Stream) -> None:
        with self._auth_lock:
            seq = self._auth_inner
            self._auth_inner += 1
        sr = _AUDIO_SAMPLE_RATE
        tx = _TX_SEQ_BUF_MS
        p = bytearray(144)
        p[0] = 0x90
        p[8:12] = struct.pack(">I", c.local_sid)
        p[12:16] = struct.pack(">I", c.remote_sid)
        p[16:26] = bytes([0x00, 0x00, 0x00, 0x80, 0x01, 0x03, 0x00, seq & 0xFF, (seq >> 8) & 0xFF, 0x00])
        p[26:32] = self._auth_id
        p[32:48] = self._a8
        # client identifier (kappanhang uses the literal "IC-705"; the radio
        # identifies itself separately, so this field is not validated by rig type)
        p[64:70] = b"\x49\x43\x2d\x37\x30\x35"
        p[96:112] = passcode(self.user)
        p[112:120] = bytes([0x01, 0x01, 0x04, 0x04, 0x00, 0x00, (sr >> 8) & 0xFF, sr & 0xFF])
        p[120:124] = bytes([0x00, 0x00, (sr >> 8) & 0xFF, sr & 0xFF])
        p[124:128] = bytes([0x00, 0x00, (SERIAL_PORT >> 8) & 0xFF, SERIAL_PORT & 0xFF])
        p[128:132] = bytes([0x00, 0x00, (AUDIO_PORT >> 8) & 0xFF, AUDIO_PORT & 0xFF])
        p[132:136] = bytes([0x00, 0x00, (tx >> 8) & 0xFF, tx & 0xFF])
        p[136] = 0x01
        c._send_tracked(p)

    # -- control inbound -----------------------------------------------------
    def _on_control_packet(self, r: bytes) -> None:
        n = len(r)
        if n == 168 and r[:6] == b"\xa8\x00\x00\x00\x00\x00":
            self._a8 = bytes(r[66:82])
            self._got_a8 = True
            self._maybe_request()
        elif n == 64 and r[:6] == b"\x40\x00\x00\x00\x00\x00":
            if r[21] == 0x05:
                self._auth_ok = True
                self._last_reauth = time.monotonic()
                self._maybe_request()
        elif n == 80 and r[:6] == b"\x50\x00\x00\x00\x00\x00":
            if r[48:51] == b"\xff\xff\xff":
                self._on_stream_error("auth failed — try rebooting the radio")
            elif r[48:51] == b"\x00\x00\x00" and r[64] == 0x01:
                self._on_stream_error("radio reported disconnected")
        elif n == 144 and r[:6] == b"\x90\x00\x00\x00\x00\x00" and r[96] == 1 and not self._serial_opened:
            if self._ctrl:
                self._ctrl.remote_sid = struct.unpack(">I", r[8:12])[0]
                self._ctrl.local_sid = struct.unpack(">I", r[12:16])[0]
            self._auth_id = bytes(r[26:32])
            self._serial_opened = True
            self._open_serial_and_audio()

    def _maybe_request(self) -> None:
        if not self._requested and self._auth_ok and self._got_a8 and self._ctrl:
            self._requested = True
            self._send_request_serial_audio(self._ctrl)

    def _open_serial_and_audio(self) -> None:
        try:
            s = _Stream("serial", self.host, SERIAL_PORT, self._on_stream_error)
            s.is_serial = True
            s.open()
            s.handshake()
            s.handle = self._on_serial_packet
            s.start_threads()
            s.send_serial_open(close=False)
            self._serial = s
            self._serial_ready.set()
        except Exception as exc:  # noqa: BLE001
            self._on_stream_error(f"serial open: {exc}")
            return

        # audio: RX (radio -> us) is parsed and handed to on_audio; TX (mic ->
        # radio) goes out via write_audio. Non-fatal: control + serial (CI-V +
        # scope) still work if audio fails to open.
        try:
            a = _Stream("audio", self.host, AUDIO_PORT, self._on_stream_error)
            a.use_pkt0_idle = False
            a.open()
            a.handshake()
            a.handle = self._on_audio_packet
            a.start_threads()
            self._audio = a
        except Exception as exc:  # noqa: BLE001
            self._error = f"audio open failed (non-fatal): {exc}"

    def _on_serial_packet(self, r: bytes) -> None:
        # CI-V data packet: 0xc1 marker at [16], CI-V bytes from [21] to the end.
        # The data-length byte at [17] is only the low byte and overflows for big
        # frames (e.g. ~497-byte scope sweeps), so take everything to the packet
        # end (the UDP packet length == 21 + CI-V length).
        if len(r) >= 22 and r[16] == 0xC1:
            if self._on_bytes:
                self._on_bytes(bytes(r[21:]))

    def _on_audio_packet(self, r: bytes) -> None:
        # RX audio: 24-byte header then PCM (16-bit LE mono). The packet size
        # depends on the negotiated sample rate (e.g. 16 kHz -> 664-byte packets
        # with 640 PCM bytes), so detect by structure, not a hardcoded length:
        # marker [16] in {0x80,0x81}, PCM length at [22:24], PCM at [24:].
        if len(r) >= 26 and r[16] in (0x80, 0x81) and r[2:6] == b"\x00\x00\x00\x00":
            pcm_len = (r[22] << 8) | r[23]
            if pcm_len and len(r) >= 24 + pcm_len and self.on_audio:
                self._rx_audio_pkts += 1
                self.on_audio(bytes(r[24:24 + pcm_len]))

    def write_audio(self, pcm: bytes) -> None:
        # TX (mic) audio: buffer and emit 1920-byte frames (radio's frame size).
        a = self._audio
        if a is None:
            return
        self._tx_audio_buf += pcm
        while len(self._tx_audio_buf) >= _AUDIO_TX_CHUNK:
            chunk = bytes(self._tx_audio_buf[:_AUDIO_TX_CHUNK])
            del self._tx_audio_buf[:_AUDIO_TX_CHUNK]
            try:
                a.send_audio_packet(chunk)
                self._tx_audio_pkts += 1
                self._tx_audio_bytes += len(chunk)
            except Exception as exc:  # noqa: BLE001
                self._on_stream_error(f"audio tx: {exc}")
                return

    def _on_stream_error(self, msg: str) -> None:
        if self._error is None:
            self._error = msg
        # unblock a waiting start() so the UI gets a prompt failure
        self._serial_ready.set()
