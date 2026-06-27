/* CW decoder / coder — an overlay tool that pops up over the waterfall.
 *
 * Decoder: a NEURAL decoder (DeepCW). It taps the pre-volume RX bus
 * (RadioAudio.bus()), resamples to 3200 Hz, and re-runs the ONNX model in
 * cw-worker.js over a growing window, committing text at pauses. Far more
 * robust than a timing decoder under QSB/QRM/weak signals.
 *
 * Coder: types -> Morse -> a soft-keyed sidetone (NO transmit; it never keys the
 * radio). The sidetone feeds the same rxBus, so playing it self-tests the decoder.
 *
 * SPDX-License-Identifier: AGPL-3.0-only
 * The decode path links the AGPL-3.0 DeepCW model (github.com/e04/deepcw-engine),
 * so the CW feature is AGPL-3.0. See cw-worker.js. onnxruntime-web is MIT.
 */
(function () {
  "use strict";
  const $ = (id) => document.getElementById(id);
  const RA = () => window.RadioAudio || null;
  const RC = () => window.RadioControl || null;   // WS command channel + live radio state
  const CW_WORKER_V = "1";                       // bump when cw-worker.js changes (cache-bust)

  const MORSE = {
    A: ".-", B: "-...", C: "-.-.", D: "-..", E: ".", F: "..-.", G: "--.", H: "....",
    I: "..", J: ".---", K: "-.-", L: ".-..", M: "--", N: "-.", O: "---", P: ".--.",
    Q: "--.-", R: ".-.", S: "...", T: "-", U: "..-", V: "...-", W: ".--", X: "-..-",
    Y: "-.--", Z: "--..",
    "0": "-----", "1": ".----", "2": "..---", "3": "...--", "4": "....-", "5": ".....",
    "6": "-....", "7": "--...", "8": "---..", "9": "----.",
    ".": ".-.-.-", ",": "--..--", "?": "..--..", "/": "-..-.", "=": "-...-", "+": ".-.-.",
    "-": "-....-", ":": "---...", "(": "-.--.", ")": "-.--.-", '"': ".-..-.", "@": ".--.-.",
    "'": ".----.",
  };

  const panel = $("cwTool"), btn = $("cwToolBtn"), head = $("cwHead");
  if (!panel || !btn) return;
  let open = false;

  // ---- show / hide ----
  function setOpen(v) {
    open = v;
    panel.hidden = !v;
    btn.classList.toggle("active", v);
    if (v) startDecoder(); else stopDecoder();
  }
  btn.addEventListener("click", () => setOpen(!open));
  $("cwClose").addEventListener("click", () => setOpen(false));

  // ---- drag the panel by its header ----
  (function () {
    let down = false, sx = 0, sy = 0, baseL = 0, baseT = 0;
    const prect = () => (panel.offsetParent || panel.parentElement).getBoundingClientRect();
    head.addEventListener("pointerdown", (e) => {
      if (e.target.closest(".tp-close")) return;
      const p = prect(), r = panel.getBoundingClientRect();
      baseL = r.left - p.left; baseT = r.top - p.top;
      panel.style.left = baseL + "px"; panel.style.top = baseT + "px";
      panel.style.right = "auto"; panel.style.bottom = "auto";
      sx = e.clientX; sy = e.clientY; down = true;
      try { head.setPointerCapture(e.pointerId); } catch (_) {}
      e.preventDefault();
    });
    head.addEventListener("pointermove", (e) => {
      if (!down || !(e.buttons & 1)) return;
      const p = prect();
      let x = baseL + (e.clientX - sx), y = baseT + (e.clientY - sy);
      x = Math.max(0, Math.min(p.width - panel.offsetWidth, x));
      y = Math.max(0, Math.min(p.height - 30, y));
      panel.style.left = x + "px"; panel.style.top = y + "px";
    });
    const end = () => { down = false; };
    head.addEventListener("pointerup", end);
    head.addEventListener("pointercancel", end);
    head.addEventListener("lostpointercapture", end);
  })();

  // ---- resize the panel by dragging any edge / corner ----
  (function () {
    const MINW = 240, MINH = 160;
    const prect = () => (panel.offsetParent || panel.parentElement).getBoundingClientRect();
    for (const dir of ["n", "s", "e", "w", "ne", "nw", "se", "sw"]) {
      const h = document.createElement("div");
      h.className = "tp-resize tp-resize-" + dir;
      h.dataset.dir = dir;
      panel.appendChild(h);                          // absolute -> stays out of the flex flow
    }
    let dir = null, sx = 0, sy = 0, sw = 0, sh = 0, sl = 0, st = 0;
    panel.addEventListener("pointerdown", (e) => {
      const t = e.target.closest(".tp-resize"); if (!t) return;
      dir = t.dataset.dir;
      const p = prect(), r = panel.getBoundingClientRect();
      sx = e.clientX; sy = e.clientY; sw = r.width; sh = r.height;
      sl = r.left - p.left; st = r.top - p.top;
      panel.style.left = sl + "px"; panel.style.top = st + "px";   // pin to left/top so resize is predictable
      panel.style.right = "auto"; panel.style.bottom = "auto";
      panel.style.width = sw + "px"; panel.style.height = sh + "px";
      try { t.setPointerCapture(e.pointerId); } catch (_) {}
      e.preventDefault(); e.stopPropagation();
    });
    panel.addEventListener("pointermove", (e) => {
      if (!dir || !(e.buttons & 1)) return;
      const p = prect();
      const dx = e.clientX - sx, dy = e.clientY - sy;
      let w = sw, h = sh, l = sl, t = st;
      if (dir.includes("e")) w = sw + dx;
      if (dir.includes("s")) h = sh + dy;
      if (dir.includes("w")) { w = sw - dx; l = sl + dx; }
      if (dir.includes("n")) { h = sh - dy; t = st + dy; }
      if (w < MINW) { if (dir.includes("w")) l -= (MINW - w); w = MINW; }   // keep the anchored edge fixed
      if (h < MINH) { if (dir.includes("n")) t -= (MINH - h); h = MINH; }
      w = Math.min(w, p.width); h = Math.min(h, p.height);                  // never exceed the scope pane
      l = Math.max(0, Math.min(l, p.width - w));
      t = Math.max(0, Math.min(t, p.height - h));
      panel.style.width = w + "px"; panel.style.height = h + "px";
      panel.style.left = l + "px"; panel.style.top = t + "px";
    });
    const end = () => { dir = null; };
    panel.addEventListener("pointerup", end);
    panel.addEventListener("pointercancel", end);
    panel.addEventListener("lostpointercapture", end);
  })();

  // ---- neural decoder ----
  const SR = 3200;                               // model sample rate
  const INFER_MS = 1200;                         // re-decode cadence
  const MIN_SEC = 5;                             // pad short windows to the model's min length
  const MAX_SEC = 11;                            // finalize + reset before the model's 20 s cap
  const PAUSE_STABLE = 3;                        // identical decodes in a row -> a settled pause -> commit
  const SILENCE = 1.5e-3;                        // |sample| below this for the whole window = no RX

  let worker = null, workerReady = false;
  let capNode = null, ticker = 0, workletReady = false;  // realtime capture worklet
  let buf = new Float32Array(MAX_SEC * SR), winLen = 0;   // current window @ 3200 Hz
  let peak = 0;                                  // |sample| peak seen this window (RX-present gate)
  let committed = "", live = "", prevLive = "", stable = 0;
  let inflight = false, lastInferLen = -1, reqId = 0;
  const out = $("cwOut"), hint = $("cwHint"), statusEl = $("cwStatus");

  function setStatus(s) { if (statusEl) statusEl.textContent = s; }

  function ensureWorker() {
    if (worker) return;
    setStatus("loading model…");
    worker = new Worker("/static/cw-worker.js?v=" + CW_WORKER_V);
    worker.onmessage = (e) => {
      const m = e.data;
      if (m.type === "ready") { workerReady = true; setStatus("ready"); render(); }
      else if (m.type === "error") { setStatus("model failed"); }
      else if (m.type === "result") onResult(m);
    };
    worker.onerror = () => setStatus("model error");
  }

  async function startDecoder() {
    ensureWorker();
    const ra = RA(); if (!ra) return;
    ra.ensure();
    const ctx = ra.ctx(), bus = ra.bus();
    if (!ctx || !bus) return;
    stopCapture();
    winLen = 0; peak = 0; committed = ""; live = ""; prevLive = ""; stable = 0;
    inflight = false; lastInferLen = -1;
    render();
    try {
      if (!workletReady) { await ctx.audioWorklet.addModule("/static/cw-capture-worklet.js?v=" + CW_WORKER_V); workletReady = true; }
      if (!open) return;                                  // panel was closed while the module loaded
      capNode = new AudioWorkletNode(ctx, "cw-capture", { processorOptions: { targetSR: SR } });
      capNode.port.onmessage = (e) => appendSamples(e.data);
      bus.connect(capNode); capNode.connect(ctx.destination);   // worklet emits no output -> silent
    } catch (err) {
      setStatus("audio capture unavailable");
      return;
    }
    if (!ticker) ticker = setInterval(tick, INFER_MS);
  }
  function stopDecoder() { stopCapture(); if (ticker) { clearInterval(ticker); ticker = 0; } }
  function stopCapture() {
    if (capNode) { try { capNode.disconnect(); capNode.port.onmessage = null; } catch (_) {} capNode = null; }
  }

  // 3200 Hz chunks from the realtime capture worklet -> append to the current window
  function appendSamples(arr) {
    for (let i = 0; i < arr.length; i++) {
      if (winLen >= buf.length) break;
      const v = arr[i]; buf[winLen++] = v;
      const a = v < 0 ? -v : v; if (a > peak) peak = a;
    }
  }

  function tick() {
    if (!workerReady || inflight || !winLen) return;
    if (peak < SILENCE) {                          // no signal: keep only a short lead, never accumulate
      const keep = (0.4 * SR) | 0;                 // silence must not fill the window (-> premature finalize)
      if (winLen > keep) { buf.copyWithin(0, winLen - keep, winLen); winLen = keep; lastInferLen = -1; }
      peak = 0;
      return;
    }
    if (winLen === lastInferLen) return;          // nothing new since the last decode
    lastInferLen = winLen;
    const lead = (SR / 4) | 0;                     // 0.25 s leading silence: CTC context for the 1st char
    const L = Math.max(winLen + lead, MIN_SEC * SR);
    const a = new Float32Array(L);
    a.set(buf.subarray(0, winLen), lead);         // [silence | window | trailing silence]
    inflight = true;
    worker.postMessage({ type: "decode", id: ++reqId, audio: a }, [a.buffer]);
  }

  function onResult(m) {
    inflight = false;
    if (m.err) { return; }
    const D = m.text || "";
    if (D === prevLive) stable += 1; else { stable = 0; prevLive = D; }
    live = D;
    const paused = stable >= PAUSE_STABLE && winLen >= 3 * SR && D.trim();
    const full = winLen >= (MAX_SEC - 0.5) * SR;
    if (paused || full) finalize(D);
    else render();
  }

  // commit the window's decode to the transcript and start a fresh window, keeping
  // the audio captured during the inference so nothing is dropped at the seam.
  function finalize(D) {
    const t = D.trim();
    if (t) committed += (committed && !committed.endsWith(" ") ? " " : "") + t;
    if (committed.length > 800) committed = committed.slice(-700);
    const sent = lastInferLen, tail = winLen - sent;
    if (tail > 0) buf.copyWithin(0, sent, winLen);
    winLen = Math.max(0, tail);
    peak = 0; live = ""; prevLive = ""; stable = 0; lastInferLen = -1;
    render();
  }

  function render() {
    if (out) {
      out.innerHTML = esc(committed) +
        (live ? (committed ? " " : "") + '<span class="cw-live">' + esc(live) + "</span>" : "");
      out.scrollTop = out.scrollHeight;
    }
    if (hint) {
      hint.textContent = !workerReady ? "loading neural model…"
        : (peak < SILENCE ? "turn on 🔊 RX to decode the receiver audio" : "decoding…");
    }
  }
  function esc(s) { return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;"); }

  $("cwClear").addEventListener("click", () => { committed = ""; live = ""; render(); });

  // ---- coder (text -> Morse sidetone; never transmits) ----
  $("cwPlay").addEventListener("click", () => playMorse($("cwSend").value));
  $("cwSend").addEventListener("keydown", (e) => { if (e.key === "Enter") playMorse($("cwSend").value); });
  function playMorse(text) {
    const ra = RA(); if (!ra) return;
    ra.ensure();
    const ctx = ra.ctx(), bus = ra.bus();
    if (!ctx || !bus || !text) return;
    const wpm = Math.max(5, Math.min(40, +$("cwWpmSet").value || 18));
    const dot = 1.2 / wpm;
    const tone = +$("cwToneSet").value || 600;
    const osc = ctx.createOscillator(); osc.type = "sine"; osc.frequency.value = tone;
    const g = ctx.createGain(); g.gain.value = 0.0001;
    osc.connect(g); g.connect(bus);              // -> rxBus -> speakers AND the decoder's tap
    let t = ctx.currentTime + 0.05;
    for (const chRaw of text.toUpperCase()) {
      if (chRaw === " ") { t += dot * 7; continue; }
      const m = MORSE[chRaw]; if (!m) continue;
      for (const el of m) {
        const dur = el === "-" ? dot * 3 : dot;
        g.gain.setValueAtTime(0, t);                        // raised-edge keying to true 0/1
        g.gain.linearRampToValueAtTime(0.3, t + 0.005);
        g.gain.setValueAtTime(0.3, t + dur - 0.005);
        g.gain.linearRampToValueAtTime(0, t + dur);
        t += dur + dot;
      }
      t += dot * 2;
    }
    osc.start(); osc.stop(t + 0.1);
  }

  // ---- transmit (operator-triggered): key the message on the radio as CW ----
  // Same act as pressing PTT — one bounded message, fully operator-controlled. The
  // backend hands the text to the rig's own keyer, which generates clean CW at the
  // WPM and drops back to RX. Press again to stop. Bound by the 120 s failsafe + TOT.
  const txBtn = $("cwTx"), txRow = $("cwTxRow"), txHint = $("cwTxHint");
  function setTxHint(s) {
    if (!txRow || !txHint) return;
    txHint.textContent = s || "";
    txRow.hidden = !s;
  }
  if (txBtn) {
    txBtn.addEventListener("click", () => {
      const rc = RC(); if (!rc) return;
      const st = rc.state() || {};
      if (st.cw_tx) { rc.send({ action: "cw_stop" }); return; }   // already sending -> stop
      if (!st.connected) { setTxHint("connect a radio to transmit"); return; }
      if (!st.cw_tx_ready) { setTxHint("CW key port not found — check the radio's 2nd USB (Standard) COM port"); return; }
      const m = st.mode_name || "";
      if (m !== "CW" && m !== "CW-R") { setTxHint("set the radio to CW / CW-R to transmit"); return; }
      const text = $("cwSend").value;
      if (!text.trim()) { setTxHint("type a message first"); return; }
      const wpm = Math.max(5, Math.min(40, +$("cwWpmSet").value || 18));
      setTxHint("");
      rc.send({ action: "cw_tx", text, wpm });
    });
  }
  // keep the TX button in step with the live radio state (shown only when the
  // connected radio supports CW message TX; reflects the transmitting state)
  function syncTx() {
    if (!txBtn) return;
    const st = (RC() && RC().state()) || {};
    const supported = !!st.has_cw_tx;
    txBtn.hidden = !supported;
    if (!supported) { setTxHint(""); return; }
    const tx = !!st.cw_tx;
    const ready = !!st.cw_tx_ready;
    txBtn.textContent = tx ? "■" : "TX";
    txBtn.classList.toggle("on", tx);
    txBtn.disabled = !tx && (!st.connected || !ready);
    txBtn.title = tx ? "Stop transmitting"
      : !st.connected ? "Connect a radio to transmit"
      : !ready ? "CW key port not found"
      : "Transmit this message as CW on the radio";
    if (tx) setTxHint("on air — sending CW");
    else if (st.connected && !ready) setTxHint("CW key port not found — check the radio's 2nd USB (Standard) COM port");
    else if (txHint && (txHint.textContent === "on air — sending CW" || txHint.textContent.indexOf("CW key port") === 0)) setTxHint("");
  }
  setInterval(syncTx, 400);
  syncTx();
})();
