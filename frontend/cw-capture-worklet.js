/* CW capture worklet — runs on the realtime audio thread so it never drops buffers
 * (unlike ScriptProcessorNode, whose drops compress timing and wreck CW decoding).
 * Resamples the RX bus from the context rate down to 3200 Hz (linear interpolation,
 * matching the DeepCW reference) and posts Float32 chunks to the main thread.
 *
 * SPDX-License-Identifier: AGPL-3.0-only  (part of the AGPL CW decode feature)
 */
class CWCapture extends AudioWorkletProcessor {
  constructor(opts) {
    super();
    const target = (opts && opts.processorOptions && opts.processorOptions.targetSR) || 3200;
    this.step = sampleRate / target;     // sampleRate = the audio context's rate (global)
    this.pos = 0;                         // read position relative to the current block
    this.last = 0;                        // last sample of the previous block (boundary interp)
  }

  process(inputs) {
    const ch = inputs[0] && inputs[0][0];
    if (!ch || ch.length === 0) return true;
    const n = ch.length;
    const out = [];
    let pos = this.pos;
    while (pos < n - 1) {
      const i = Math.floor(pos), frac = pos - i;
      const s0 = i < 0 ? this.last : ch[i];
      out.push(s0 * (1 - frac) + ch[i + 1] * frac);
      pos += this.step;
    }
    this.pos = pos - n;                   // carry into the next block
    this.last = ch[n - 1];
    if (out.length) this.port.postMessage(Float32Array.from(out));
    return true;                          // keep the processor alive
  }
}

registerProcessor("cw-capture", CWCapture);
