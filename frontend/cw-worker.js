/* DeepCW inference worker — runs the neural CW decoder off the main thread.
 *
 * SPDX-License-Identifier: AGPL-3.0-only
 * The spectrogram (STFT) and greedy-CTC steps are adapted from the AGPL-3.0 engine
 * github.com/e04/deepcw-engine (examples/nodejs/decode_morse.mjs); the ONNX model
 * (frontend/models/deepcw/model.onnx) is that engine's weights, AGPL-3.0. Because this
 * file links the AGPL model, it and the CW feature are AGPL-3.0. onnxruntime-web is MIT.
 *
 * Protocol: main thread posts {type:'decode', id, audio:Float32Array@3200Hz};
 * worker replies {type:'result', id, text} (and {type:'ready'} once the model loads).
 */
"use strict";

/* global ort */
importScripts("/static/vendor/ort/ort.wasm.min.js");      // UMD -> self.ort
ort.env.wasm.wasmPaths = "/static/vendor/ort/";
ort.env.wasm.numThreads = 1;                              // single-thread -> no SharedArrayBuffer / COOP-COEP
ort.env.wasm.simd = true;

let session = null, meta = null, spaceIndex = -1;
let hann = null, basisCos = null, basisSin = null, startBin = 0, stopBin = 0, BINS = 0;

async function init() {
  meta = await (await fetch("/static/models/deepcw/model.onnx.json")).json();
  const N = meta.fft_length, sr = meta.sample_rate, binHz = sr / N;
  startBin = Math.ceil(meta.spectrogram_min_freq_hz / binHz);
  stopBin = Math.floor(meta.spectrogram_max_freq_hz / binHz) + 1;
  BINS = stopBin - startBin;
  hann = new Float32Array(N);                             // periodic Hann (np.hanning(N+1)[:-1])
  for (let i = 0; i < N; i++) hann[i] = 0.5 - 0.5 * Math.cos((2 * Math.PI * i) / N);
  basisCos = []; basisSin = [];                           // precomputed DFT basis for the kept bins
  for (let bin = startBin; bin < stopBin; bin++) {
    const c = new Float32Array(N), s = new Float32Array(N);
    for (let n = 0; n < N; n++) { const a = (-2 * Math.PI * bin * n) / N; c[n] = Math.cos(a); s[n] = Math.sin(a); }
    basisCos.push(c); basisSin.push(s);
  }
  spaceIndex = meta.chars.indexOf(" ");
  session = await ort.InferenceSession.create("/static/models/deepcw/model.onnx", { executionProviders: ["wasm"] });
  self.postMessage({ type: "ready", bins: BINS, hop: meta.hop_length, fft: meta.fft_length, sr: meta.sample_rate });
}

function spectrogram(audio) {
  const N = meta.fft_length, hop = meta.hop_length, pad = N >> 1;
  const padded = new Float32Array(audio.length + pad * 2);   // reflect-pad (centered STFT)
  for (let i = 0; i < pad; i++) {
    padded[i] = audio[pad - i] || 0;
    padded[pad + audio.length + i] = audio[audio.length - 2 - i] || 0;
  }
  padded.set(audio, pad);
  const frames = 1 + Math.floor((padded.length - N) / hop);
  const data = new Float32Array(frames * BINS);
  const fr = new Float32Array(N);
  for (let f = 0; f < frames; f++) {
    const st = f * hop;
    for (let i = 0; i < N; i++) fr[i] = padded[st + i] * hann[i];
    const base = f * BINS;
    for (let b = 0; b < BINS; b++) {
      const C = basisCos[b], S = basisSin[b];
      let re = 0, im = 0;
      for (let n = 0; n < N; n++) { const x = fr[n]; re += x * C[n]; im += x * S[n]; }
      data[base + b] = Math.log1p(Math.hypot(re, im));     // magnitude -> log1p
    }
  }
  return { data, frames };
}

// Greedy CTC -> collapsed text PLUS frame spans for each character and each word-space run.
// (Adapted from e04/web-deep-cw-decoder src/utils/textDecoder.ts.) The spans carry frame
// timing so the streaming caller can commit at a settled word gap and slide the audio buffer
// to that exact point — decoding the live stream with no mid-word seam.
function decodeWithSpans(logProbs, dims) {
  const frames = dims[1], classes = dims[2], blank = meta.blank_index;
  const pred = new Int16Array(frames);
  for (let f = 0; f < frames; f++) {
    let bi = 0, bv = -Infinity, base = f * classes;
    for (let k = 0; k < classes; k++) { const v = logProbs[base + k]; if (v > bv) { bv = v; bi = k; } }
    pred[f] = bi;
  }
  let text = "", prev = -1, active = -1;
  const characterSpans = [], wordSpaceSpans = [];
  for (let f = 0; f < frames; f++) {                 // collapsed text + per-character spans
    const bi = pred[f];
    if (bi === blank) { prev = -1; active = -1; continue; }
    if (bi === prev) { if (active >= 0) characterSpans[active].endFrame = f; continue; }
    prev = bi;
    const ch = meta.chars[bi];
    text += ch;
    characterSpans.push({ char: ch, startFrame: f, endFrame: f });
    active = characterSpans.length - 1;
  }
  let wsStart = -1;                                  // runs of frames the model labels "space"
  for (let f = 0; f < frames; f++) {
    if (pred[f] === spaceIndex) { if (wsStart < 0) wsStart = f; }
    else if (wsStart >= 0) { wordSpaceSpans.push({ startFrame: wsStart, endFrame: f - 1 }); wsStart = -1; }
  }
  if (wsStart >= 0) wordSpaceSpans.push({ startFrame: wsStart, endFrame: frames - 1 });
  return { text, characterSpans, wordSpaceSpans };
}

self.onmessage = async (e) => {
  const m = e.data;
  if (m.type !== "decode") return;
  if (!session) { self.postMessage({ type: "result", id: m.id, text: "", err: "not-ready" }); return; }
  try {
    const { data, frames } = spectrogram(m.audio);
    const input = new ort.Tensor("float32", data, [1, 1, frames, BINS]);
    const out = await session.run({ [meta.onnx_input_name]: input });
    const o = out[meta.onnx_output_name];
    const r = decodeWithSpans(o.data, o.dims);
    self.postMessage({ type: "result", id: m.id, text: r.text,
      characterSpans: r.characterSpans, wordSpaceSpans: r.wordSpaceSpans });
  } catch (err) {
    self.postMessage({ type: "result", id: m.id, text: "", err: String(err) });
  }
};

init().catch((err) => self.postMessage({ type: "error", err: String(err) }));
