"""
Icom WebOp server.

ASGI app (Starlette on uvicorn):
  GET  /              -> the radio UI
  GET  /api/ports     -> available COM ports (+ "sim")
  POST /api/connect   -> {transport:"sim"} or {transport:"serial",port,baud}
  POST /api/disconnect
  WS   /ws            -> JSON state in/out + binary scope sweeps out

Scope sweeps are pushed as a single self-contained binary frame:
  <BBBH IIIIII> header then N amplitude bytes (see _pack_scope).
"""
from __future__ import annotations

import asyncio
import json
import struct
from pathlib import Path
from typing import Optional, Set

from starlette.applications import Starlette
from starlette.responses import FileResponse, JSONResponse
from starlette.routing import Mount, Route, WebSocketRoute
from starlette.staticfiles import StaticFiles
from starlette.websockets import WebSocket, WebSocketDisconnect

from . import civ
from .lan import LanTransport
from .radio import Radio
from .transport import SerialTransport, SimTransport, available_ports

FRONTEND = Path(__file__).resolve().parent.parent / "frontend"

LEVEL_TARGETS = {"af": 0x01, "rf": 0x02, "sql": 0x03, "rfpwr": 0x0A}

radio = Radio()


class Hub:
    """Bridges radio threads -> websocket clients via the asyncio loop."""

    def __init__(self) -> None:
        self.clients: Set[asyncio.Queue] = set()
        self.loop: Optional[asyncio.AbstractEventLoop] = None

    def add(self) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue(maxsize=64)   # room for scope + audio
        self.clients.add(q)
        return q

    def remove(self, q: asyncio.Queue) -> None:
        self.clients.discard(q)

    def _push(self, item) -> None:
        if not self.loop:
            return
        def deliver():
            for q in list(self.clients):
                if q.full():
                    try:
                        q.get_nowait()       # drop oldest, keep stream live
                    except asyncio.QueueEmpty:
                        pass
                try:
                    q.put_nowait(item)
                except asyncio.QueueFull:
                    pass
        self.loop.call_soon_threadsafe(deliver)

    def broadcast_state(self, state: dict) -> None:
        self._push(("text", json.dumps({"type": "state", **state})))

    def broadcast_scope(self, sweep: civ.ScopeSweep) -> None:
        self._push(("bytes", _pack_scope(sweep, radio.state)))

    def broadcast_audio(self, pcm: bytes) -> None:
        # 'A' tag + channels + sample-rate header, then 16-bit LE mono PCM
        self._push(("bytes", struct.pack("<BBH", 0x41, 1, AUDIO_RATE) + pcm))


AUDIO_RATE = 16000

hub = Hub()
radio.on_state = hub.broadcast_state
radio.on_scope = hub.broadcast_scope
radio.on_audio = hub.broadcast_audio


def _pack_scope(sweep: civ.ScopeSweep, state: dict) -> bytes:
    data = sweep.data[: civ.SCOPE_POINTS]
    header = struct.pack(
        "<BBBH IIIIII",
        0x53,                          # 'S' magic
        1 if sweep.mode == 1 else 0,   # 0 center / 1 fixed
        1 if sweep.out_of_range else 0,
        len(data),
        sweep.center_hz or 0,
        sweep.span_hz or state.get("span", 0),
        sweep.lower_hz or 0,
        sweep.upper_hz or 0,
        state.get("freq", 0),          # tuned freq (channel marker)
        state.get("filter_bw", 0),
    )
    return header + data


# -- HTTP routes -------------------------------------------------------------
async def index(request):
    return FileResponse(FRONTEND / "index.html")


async def api_ports(request):
    ports = available_ports()
    return JSONResponse({
        "ports": ports,
        "connected": radio.state["connected"],
        "transport": radio.state["transport"],
    })


async def api_connect(request):
    body = await request.json()
    kind = body.get("transport", "sim")
    try:
        if kind == "serial":
            port = body["port"]
            baud = int(body.get("baud", 115200))
            tp = SerialTransport(port, baud)
        elif kind == "lan":
            host = (body.get("host") or "").strip()
            if not host:
                raise ValueError("LAN host/IP is required")
            tp = LanTransport(host, int(body.get("port", 50001)),
                              body.get("user", ""), body.get("password", ""))
        else:
            tp = SimTransport()
        radio.connect(tp)
        return JSONResponse({"ok": True, "transport": radio.state["transport"]})
    except Exception as exc:
        return JSONResponse({"ok": False, "error": str(exc)}, status_code=400)


async def api_disconnect(request):
    radio.disconnect()
    return JSONResponse({"ok": True})


# -- WebSocket ---------------------------------------------------------------
async def ws_endpoint(ws: WebSocket):
    await ws.accept()
    q = hub.add()
    await ws.send_text(json.dumps({"type": "state", **radio.state}))

    async def sender():
        try:
            while True:
                kind, payload = await q.get()
                if kind == "text":
                    await ws.send_text(payload)
                else:
                    await ws.send_bytes(payload)
        except (WebSocketDisconnect, RuntimeError):
            pass

    send_task = asyncio.create_task(sender())
    try:
        while True:
            msg = await ws.receive()
            if msg["type"] == "websocket.disconnect":
                break
            if msg.get("text") is not None:
                _handle_cmd(json.loads(msg["text"]))
            elif msg.get("bytes") is not None:
                radio.write_audio(msg["bytes"])      # mic PCM (16-bit LE mono)
    except WebSocketDisconnect:
        pass
    finally:
        send_task.cancel()
        hub.remove(q)
        # safety: never leave the radio keyed if the last client drops
        if not hub.clients and radio.state.get("ptt"):
            radio.set_ptt(False)


def _handle_cmd(cmd: dict) -> None:
    action = cmd.get("action")
    try:
        if action == "set_freq":
            radio.set_freq(int(cmd["hz"]))
        elif action == "tune":
            radio.tune(int(cmd["delta"]))
        elif action == "set_mode":
            code = civ.MODE_CODES.get(cmd["mode"])
            if code is not None:
                radio.set_mode(code, cmd.get("filter"))
        elif action == "set_filter":
            radio.set_filter(int(cmd["filter"]))
        elif action == "vfo":
            radio.select_vfo(int(cmd["code"]))
        elif action == "set_level":
            sub = LEVEL_TARGETS.get(cmd["target"])
            if sub is not None:
                radio.set_level(sub, int(cmd["value"]))
        elif action == "band":
            radio.set_band(str(cmd["band"]))
        elif action == "set_span":
            radio.set_span(int(cmd["span"]))
        elif action == "scope_mode":
            radio.set_scope_mode(bool(cmd["center"]))
        elif action == "ptt":
            radio.set_ptt(bool(cmd["tx"]))
    except (KeyError, ValueError, TypeError):
        pass


async def _startup():
    hub.loop = asyncio.get_running_loop()


routes = [
    Route("/", index),
    Route("/api/ports", api_ports),
    Route("/api/connect", api_connect, methods=["POST"]),
    Route("/api/disconnect", api_disconnect, methods=["POST"]),
    WebSocketRoute("/ws", ws_endpoint),
    Mount("/static", StaticFiles(directory=str(FRONTEND)), name="static"),
]

app = Starlette(debug=False, routes=routes, on_startup=[_startup])
