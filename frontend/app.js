/* Icom WebOp — UI controller */
(function () {
  "use strict";
  const $ = (id) => document.getElementById(id);

  const scope = new Scope($("spectrum"), $("waterfall"), $("overlay"), $("scopeWrap"));

  let ws = null, state = {}, step = 25000;

  // ---- frequency formatting (Icom dotted readout) ----
  function formatFreq(hz) {
    hz = Math.max(0, Math.round(hz));
    const mhz = Math.floor(hz / 1e6);
    const rem = hz % 1e6;
    const khz = String(Math.floor(rem / 1000)).padStart(3, "0");
    const h = String(rem % 1000).padStart(3, "0");
    return `${mhz}.${khz}.${h}`;
  }

  // ---- websocket ----
  function connectWS() {
    const proto = location.protocol === "https:" ? "wss" : "ws";
    ws = new WebSocket(`${proto}://${location.host}/ws`);
    ws.binaryType = "arraybuffer";
    ws.onmessage = onMessage;
    ws.onclose = () => setTimeout(connectWS, 1200);
  }

  function send(obj) {
    if (ws && ws.readyState === 1) ws.send(JSON.stringify(obj));
  }

  function onMessage(ev) {
    if (typeof ev.data === "string") {
      const msg = JSON.parse(ev.data);
      if (msg.type === "state") updateState(msg);
      return;
    }
    parseScope(ev.data);
  }

  function parseScope(buf) {
    const dv = new DataView(buf);
    if (dv.getUint8(0) !== 0x53) return;
    const npoints = dv.getUint16(3, true);
    const meta = {
      mode: dv.getUint8(1),
      out: dv.getUint8(2) === 1,
      center: dv.getUint32(5, true),
      span: dv.getUint32(9, true),
      lower: dv.getUint32(13, true),
      upper: dv.getUint32(17, true),
      tuned: dv.getUint32(21, true),
      filterBw: dv.getUint32(25, true),
    };
    const data = new Uint8Array(buf, 29, npoints);
    scope.pushSweep(meta, data);
    updateScopeLabels(meta);
  }

  function updateScopeLabels(m) {
    let lo, hi, c;
    if (m.mode === 1) { lo = m.lower; hi = m.upper; c = (lo + hi) / 2; }
    else { lo = m.center - m.span / 2; hi = m.center + m.span / 2; c = m.center; }
    $("lblLeft").textContent = formatFreq(lo);
    $("lblRight").textContent = formatFreq(hi);
    $("lblCenter").textContent = formatFreq(m.tuned || c);
  }

  // ---- state -> UI ----
  function updateState(s) {
    state = s;
    $("freq").textContent = formatFreq(s.freq);
    $("modeReadout").textContent = s.mode_name || "";
    $("filtReadout").textContent = s.filter_name || "";
    $("vfoLetter").textContent = "A";

    const pct = Math.min(100, (s.smeter || 0) / 240 * 100);
    $("meterFill").style.width = pct + "%";
    $("meterVal").textContent = s.smeter_s || "S0";

    // connection
    const on = !!s.connected;
    $("led").classList.toggle("on", on);
    $("connlabel").textContent = on ? (s.transport || "Connected") : "Disconnected";

    // PTT / TX tag
    $("txTag").textContent = s.ptt ? "TX" : "RX";
    $("txTag").classList.toggle("on", !!s.ptt);
    $("pttBtn").classList.toggle("on", !!s.ptt);

    // span + scope mode
    $("spanVal").textContent = s.span_label || "";
    $("btnCenter").classList.toggle("active", !!s.scope_center);
    $("btnFixed").classList.toggle("active", !s.scope_center);

    // active buttons
    setActive(".band", b => b.dataset.band === String(bandOf(s.freq)));
    setActive(".mode", b => b.dataset.mode === s.mode_name);
    setActive(".filt", b => b.dataset.filter === String(s.filter));

    // level sliders (don't fight an active drag)
    for (const t of ["af", "rf", "sql", "rfpwr"]) {
      const el = $(t);
      if (el && document.activeElement !== el && s[t] != null) el.value = s[t];
    }

    // keep overlay tracking between sweeps
    scope.setOpMode(s.mode_name);
    scope.meta.tuned = s.freq;
    scope.meta.filterBw = s.filter_bw;
    scope.drawOverlay();
  }

  function bandOf(hz) {
    if (hz >= 1_240_000_000) return 1200;
    if (hz >= 430_000_000) return 430;
    return 144;
  }
  function setActive(sel, pred) {
    document.querySelectorAll(sel).forEach(b => b.classList.toggle("active", pred(b)));
  }

  // ---- button delegation ----
  document.addEventListener("click", (e) => {
    const b = e.target.closest("[data-act]");
    if (!b) return;
    const act = b.dataset.act;
    if (act === "band") send({ action: "band", band: b.dataset.band });
    else if (act === "mode") send({ action: "set_mode", mode: b.dataset.mode });
    else if (act === "filter") send({ action: "set_filter", filter: +b.dataset.filter });
    else if (act === "vfo") send({ action: "vfo", code: +b.dataset.code });
    else if (act === "scope_mode") send({ action: "scope_mode", center: b.dataset.center === "1" });
  });

  // span +/- cycle through documented spans
  const SPANS = [2500, 5000, 10000, 25000, 50000, 100000, 250000, 500000];
  $("spanUp").onclick = () => stepSpan(+1);
  $("spanDn").onclick = () => stepSpan(-1);
  function stepSpan(dir) {
    let i = SPANS.indexOf(state.span || 50000);
    if (i < 0) i = 3;
    i = Math.max(0, Math.min(SPANS.length - 1, i + dir));
    send({ action: "set_span", span: SPANS[i] });
  }

  // frequency entry
  $("freqSet").onclick = setFreqFromEntry;
  $("freqEntry").addEventListener("keydown", e => { if (e.key === "Enter") setFreqFromEntry(); });
  function setFreqFromEntry() {
    const v = parseFloat($("freqEntry").value);
    if (!isNaN(v)) send({ action: "set_freq", hz: Math.round(v * 1e6) });
  }

  // step select
  $("step").onchange = () => { step = +$("step").value; };

  // level sliders
  for (const t of ["af", "rf", "sql", "rfpwr"]) {
    $(t).addEventListener("input", e => send({ action: "set_level", target: t, value: +e.target.value }));
  }

  // PTT momentary
  const ptt = $("pttBtn");
  const pttDown = () => send({ action: "ptt", tx: true });
  const pttUp = () => send({ action: "ptt", tx: false });
  ptt.addEventListener("mousedown", pttDown);
  ptt.addEventListener("mouseup", pttUp);
  ptt.addEventListener("mouseleave", () => { if (state.ptt) pttUp(); });

  // ---- tuning: click-to-tune + wheel on the scope ----
  const wrap = $("scopeWrap");
  wrap.addEventListener("click", (e) => {
    const r = wrap.getBoundingClientRect();
    const x = e.clientX - r.left;
    const m = scope.meta; let lo, hi;
    if (m.mode === 1 && m.lower && m.upper) { lo = m.lower; hi = m.upper; }
    else { lo = m.center - m.span / 2; hi = m.center + m.span / 2; }
    const freq = lo + (x / scope.W) * (hi - lo);
    send({ action: "set_freq", hz: Math.round(freq / step) * step });  // snap to step
  });
  wrap.addEventListener("wheel", (e) => {
    e.preventDefault();
    send({ action: "tune", delta: (e.deltaY < 0 ? 1 : -1) * step });
  }, { passive: false });

  // ---- main dial drag ----
  const dial = $("dial"), knob = $("dialKnob");
  let dragging = false, lastAngle = 0, accum = 0, rot = 0;
  function angleAt(e, rect) {
    const cx = rect.left + rect.width / 2, cy = rect.top + rect.height / 2;
    return Math.atan2(e.clientY - cy, e.clientX - cx) * 180 / Math.PI;
  }
  dial.addEventListener("pointerdown", (e) => {
    dragging = true; dial.setPointerCapture(e.pointerId);
    lastAngle = angleAt(e, dial.getBoundingClientRect());
  });
  dial.addEventListener("pointermove", (e) => {
    if (!dragging) return;
    const a = angleAt(e, dial.getBoundingClientRect());
    let d = a - lastAngle;
    if (d > 180) d -= 360; if (d < -180) d += 360;
    lastAngle = a; accum += d; rot += d;
    knob.style.transform = `rotate(${rot}deg)`;
    const PER = 6; // degrees per step
    while (Math.abs(accum) >= PER) {
      send({ action: "tune", delta: (accum > 0 ? 1 : -1) * step });
      accum -= (accum > 0 ? 1 : -1) * PER;
    }
  });
  const endDrag = () => { dragging = false; };
  dial.addEventListener("pointerup", endDrag);
  dial.addEventListener("pointercancel", endDrag);
  // wheel on dial too
  dial.addEventListener("wheel", (e) => {
    e.preventDefault();
    send({ action: "tune", delta: (e.deltaY < 0 ? 1 : -1) * step });
  }, { passive: false });

  // ---- connection controls ----
  async function loadPorts() {
    try {
      const r = await fetch("/api/ports");
      const j = await r.json();
      const sel = $("transport");
      sel.querySelectorAll("option:not([value='sim']):not([value='lan'])").forEach(o => o.remove());
      const lanOpt = sel.querySelector("option[value='lan']");
      for (const p of j.ports) {
        const o = document.createElement("option");
        o.value = p.device; o.dataset.kind = "serial";
        o.textContent = `${p.device} — ${p.description}`.slice(0, 48);
        sel.insertBefore(o, lanOpt);
      }
    } catch (_) {}
  }
  function updateConnFields() {
    const sel = $("transport");
    const opt = sel.options[sel.selectedIndex];
    const isSerial = opt && opt.dataset.kind === "serial";
    $("baud").hidden = !isSerial;
    $("lanFields").hidden = sel.value !== "lan";
  }
  $("transport").addEventListener("change", updateConnFields);
  $("connectBtn").onclick = async () => {
    const sel = $("transport");
    const opt = sel.options[sel.selectedIndex];
    let body;
    if (opt.value === "sim") body = { transport: "sim" };
    else if (opt.value === "lan") body = {
      transport: "lan", host: $("lanHost").value.trim(), port: 50001,
      user: $("lanUser").value, password: $("lanPass").value,
    };
    else body = { transport: "serial", port: opt.value, baud: +$("baud").value || 115200 };
    if (opt.value === "lan" && !body.host) { alert("Enter the radio's IP address."); return; }
    const btn = $("connectBtn"); btn.textContent = "Connecting…"; btn.disabled = true;
    try {
      const r = await fetch("/api/connect", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
      const j = await r.json();
      if (!j.ok) alert("Connect failed: " + (j.error || "unknown"));
    } finally { btn.textContent = "Connect"; btn.disabled = false; }
  };
  $("disconnectBtn").onclick = () => fetch("/api/disconnect", { method: "POST" });

  // ---- boot ----
  step = +$("step").value;
  updateConnFields();
  connectWS();
  loadPorts().then(() => {
    // auto-start the simulator so the waterfall is live immediately
    fetch("/api/connect", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ transport: "sim" }) });
  });
})();
