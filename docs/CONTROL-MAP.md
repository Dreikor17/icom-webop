# IC-9700 Web UI — Master Control Map

This is the authoritative map of every IC-9700 control we can drive (or read) over CI-V, assembled from the per-area extractions. Each control lists its CI-V command (exact bytes), a UI **Type** (action / toggle / enum / level / number / readout), the **View** it belongs in (`radio` = TFT-style main screen, `menus` = SET-mode lists, `both` = surfaced in both), the value encoding, current build **Status**, and notes.

Conventions:
- **CI-V** bytes are hex, exactly as sent after the controller/radio address preamble. `1A 05 nnnn` items are 4-digit SET-mode menu indices.
- **Status** is `done` (already in the app), or `TODO`.
- Duplicated controls that appeared in more than one extraction are listed **once** in their primary area; cross-references are noted.
- Items explicitly marked NOT AVAILABLE on the IC-9700 are collected under *Front-panel-only / not on CI-V*.

---

## VFO / Frequency / Band / Memory / Scan

| Control | CI-V | Type | View | Values | Status | Notes |
|---|---|---|---|---|---|---|
| Set operating frequency | `05` | number | both | 5-byte LE BCD, 1Hz–1GHz; 100MHz digit 0–4, 1GHz 0–1 | done | SET to current VFO |
| Read operating frequency | `03` | readout | both | 5-byte BCD | done | |
| Frequency transceive (broadcast) | `00` | readout | both | 5-byte BCD when dial changes (CI-V Transceive ON) | TODO | Track radio-side dial; pair with `1A 05 0127` |
| Read transmit frequency | `1C 03` | readout | both | 5-byte BCD (TX side, split/dup) | TODO | Read-only |
| Read band edge frequencies | `02` | readout | menus | edge#01–30 + lower(5B) + `2D` + higher(5B); edge# not echoed | TODO | Validate freq entry / band limits |
| Read number of TX freq bands | `1E 00` | readout | menus | count | TODO | Read-only |
| Read TX band edge frequencies | `1E 01` | readout | menus | edge# + lower + `2D` + higher | TODO | Read-only TX limits |
| Read number of user TX bands | `1E 02` | readout | menus | count | TODO | Read-only |
| Set user TX band edge freqs | `1E 03` | number | menus | edge# + lower + `2D` + higher BCD | TODO | Custom TX band edges |
| Select VFO A | `07 00` | action | both | (sat mode: selects VFO mode) | done | |
| Select VFO B | `07 01` | action | both | (NG in sat mode) | done | |
| Equalize VFO A=B | `07 A0` | action | both | copy active → other | done | A=B |
| Exchange MAIN/SUB (swap) | `07 B0` | action | both | swap | done | VFO swap |
| Select MAIN band | `07 D0` | action | both | make MAIN operating | TODO | |
| Select SUB band | `07 D1` | action | both | make SUB operating | TODO | |
| Read MAIN band selection | `07 D2 00` | readout | both | 00 = main-band state | TODO | UI state sync |
| Read SUB band selection | `07 D2 01` | readout | both | 01 = sub-band state | TODO | |
| Set selected/unselected VFO freq (MAIN) | `25` | number | both | sel/unsel byte (00=sel,01=unsel) + 5B BCD | TODO | Set inactive VFO without swap |
| Set selected/unselected VFO mode+filter (MAIN) | `26` | enum | both | sel/unsel + mode + data + filter | TODO | Mode/filter of inactive VFO |
| Band stacking register (read/write) | `1A 01` | readout | both | band(01=144,02=430,03=1.2G)+reg(01=L,02=C,03=R); write appends freq/mode/dup/tone/calls/name | TODO | 3 registers/band |
| Select memory channel | `08` | enum | both | 0001–0099 = M-CH; 0100/0101 = PSE1A/1B; 0102/03 = 2A/2B; 0104/05 = 3A/3B; 0106 = C1; 0107 = C2 | TODO | Enters memory mode at channel |
| Enter memory mode | `08` | action | both | `08` alone (no data) | TODO | V/M → MEMO |
| Memory write (MW) | `08 09` | action | both | writes VFO → selected M-CH | TODO | |
| Memory copy to VFO (M→V) | `08 0A` | action | both | selected M-CH → VFO | TODO | |
| Memory clear | `08 0B` | action | both | clears selected M-CH | TODO | |
| Memory contents (full read/write) | `1A 00` | readout | both | band+ch+selflag+freq(5B)+mode(2B)+dataflag+dup/tone+DSQL+rpt-tone+tsql+DTCS+DVcsql+offset+UR/R1/R2(8 ea)+name(16); clear = ch+`FF`+no body | TODO | Memory keeper; also stores PSE-edges (0100–0105) and call ch C1/C2 (0106/0107) |
| Satellite memory contents | `1A 07` | readout | menus | sat-ch 0001–0099 + uplink + downlink + tone/DSQL/calls/name | TODO | Uplink+downlink pair |
| Memory keyer (CW) contents | `1A 02` | readout | menus | ch 01=M1..08=M8 + text (ASCII; `^`=no-space, `*`=contest#) | TODO | CW M1–M8 (see CW/RTTY) |
| Tuning step | `10` | enum | both | 00=OFF(10/1Hz),01=100Hz,02=500Hz,03=1k,04=5k,05=6.25k,06=10k,07=12.5k,08=20k,09=25k,10=50k,11=100k | TODO | 00 = fine |
| Dial lock | `16 50` | toggle | both | 00=OFF,01=ON | TODO | |
| Lock Function target | `1A 05 0059` | enum | menus | 00=MAIN DIAL,01=PANEL | TODO | |
| [SPEECH/LOCK] switch behavior | `1A 05 0058` | enum | menus | 00=SPEECH/LOCK,01=LOCK/SPEECH | TODO | |
| MAIN DIAL Auto TS | `1A 05 0061` | enum | menus | 00=OFF,01=Low,02=High | TODO | |
| Split ON/OFF (set) | `0F 00`/`0F 01` | toggle | both | 00=OFF,01=ON | TODO | See TX area |
| Split status (read) | `0F` | readout | both | 00=OFF,01=ON,11=DUP-,12=DUP+,13=RPS | TODO | |
| Quick SPLIT enable | `1A 05 0043` | toggle | menus | 00=OFF,01=ON | TODO | |
| SPLIT LOCK | `1A 05 0045` | toggle | menus | 00=OFF,01=ON | TODO | |
| FM SPLIT Offset | `1A 05 0044` | number | menus | dir(00=+,01=-)+offset BCD | TODO | FM quick-split default |
| Duplex/simplex (set) | `0F 10`/`11`/`12`/`13` | enum | both | 10=Simplex,11=DUP-,12=DUP+,13=RPS(DD) | TODO | See TX area |
| Read duplex offset | `0C` | readout | both | 3-byte BCD (1kHz–10MHz; 10MHz only 1.2G) | TODO | |
| Set duplex offset | `0D` | number | both | 3-byte BCD (1kHz–10MHz) | TODO | |
| Cancel scan | `0E 00` | action | both | stop scan | TODO | |
| Start Programmed/Memory scan | `0E 01` | action | both | per V/M mode | TODO | |
| Start Programmed scan | `0E 02` | action | both | between program edges | TODO | |
| Start dF scan | `0E 03` | action | both | ± span around center | TODO | |
| Start Fine Programmed scan | `0E 12` | action | both | fine-step program | TODO | |
| Start Fine dF scan | `0E 13` | action | both | fine-step delta-F | TODO | |
| Start Memory scan | `0E 22` | action | both | all M-CH | TODO | |
| Start Select-Memory scan | `0E 23` | action | both | select-marked only | TODO | |
| Start Mode-Select scan | `0E 24` | action | both | selected-mode channels | TODO | |
| dF scan span | `0E Ax` | enum | both | A1=±5k,A2=10k,A3=20k,A4=50k,A5=100k,A6=500k,A7=1MHz | TODO | x=1..7 |
| Clear Select-channel marks | `0E B0` | action | both | clears marks | TODO | |
| Set channel as Select channel | `0E B1` | enum | both | 01=SEL1,02=SEL2,03=SEL3 (none = last) | TODO | |
| Select-Memory scan group | `0E B2` | enum | both | 00=ALL,01=SEL1,02=SEL2,03=SEL3 | TODO | |
| Scan resume OFF (legacy) | `0E D0` | action | both | resume off | TODO | See `1A 05 0250` |
| Scan resume ON (Close&Delay) | `0E D3` | action | both | resume on | TODO | |
| SCAN Speed | `1A 05 0249` | enum | menus | 00=Slow,01=Fast | TODO | |
| SCAN Resume | `1A 05 0250` | toggle | menus | 00=OFF,01=ON | TODO | |
| Scan Pause Timer | `1A 05 0251` | enum | menus | 00=2s..09=20s (2s), 10=HOLD | TODO | |
| Scan Resume Timer | `1A 05 0252` | enum | menus | 00=0s..05=5s, 06=HOLD | TODO | |
| Temporary Skip Timer | `1A 05 0253` | enum | menus | 00=5m,01=10m,02=15m,03=While Scanning,04=While Powered ON | TODO | |
| MAIN DIAL Operation (SCAN) | `1A 05 0254` | enum | menus | 00=OFF,01=Up/Down | TODO | |
| Memo Pad Quantity | `1A 05 0060` | enum | menus | 00=5ch,01=10ch | TODO | Pad contents not CI-V |
| Display Memory Name | `1A 05 0156` | toggle | menus | 00=OFF,01=ON | TODO | |
| Attenuator | `11` | enum | both | 00=OFF,10=10dB | TODO | See RX-DSP area (single ATT) |

---

## Mode + Receive DSP

Mode/data-mode/filter, twin-PBT, notch, NB, NR, AGC, RF/SQL, preamp, dualwatch.

| Control | CI-V | Type | View | Values | Status | Notes |
|---|---|---|---|---|---|---|
| Operating mode + filter (SET) | `06` | enum | both | 00=LSB,01=USB,02=AM,03=CW,04=RTTY,05=FM,07=CW-R,08=RTTY-R,17=DV,22=DD; opt filter 01–03 | done | |
| Operating mode + filter (READ) | `04` | readout | both | mode byte + filter byte | done | |
| Mode data (transceive broadcast) | `01` | enum | both | same as `06`; FIL1 default | done | Covered by mode handling |
| DATA mode ON/OFF (+filter) | `1A 06` | enum | both | data 00=OFF/01=ON + filter 01–03 | TODO | SSB-DATA/RTTY-DATA flag |
| Selected IF filter width | `1A 03` | level | both | SSB/CW: 0–9=50–500Hz, 10–40=600Hz–3.6k; RTTY 10–31=600–2.7k; AM 0–49=200Hz–10k | done | Passband of selected FILx |
| DSP IF filter shape | `16 56` | enum | menus | 00=SHARP,01=SOFT | TODO | Per-mode |
| Twin PBT — PBT1 (inner) | `14 07` | level | radio | 0000=CCW,0128=center,0255=CW | TODO | Shift+spread = IF shift/width |
| Twin PBT — PBT2 (outer) | `14 08` | level | radio | 0000=CCW,0128=center,0255=CW | TODO | No standalone IF-shift cmd |
| Manual NOTCH position | `14 0D` | level | radio | 0000=CCW,0128=center,0255=CW | TODO | Pairs with `16 48`/`16 57` |
| Noise Blanker ON/OFF | `16 22` | toggle | both | 00=OFF,01=ON | TODO | |
| NB level (legacy/global) | `14 12` | level | radio | 0000–0255 (0–100%) | TODO | Older single value |
| NB Level/Depth/Width 144M | `1A 05 0321`/`0322`/`0323` | level | menus | Lvl 0000–0255; Depth 00–09(1–10); Width 0000–0255(1–100) | TODO | Per-band |
| NB Level/Depth/Width 430M | `1A 05 0324`/`0325`/`0326` | level | menus | same encoding | TODO | |
| NB Level/Depth/Width 1200M | `1A 05 0327`/`0328`/`0329` | level | menus | same encoding | TODO | |
| Noise Reduction ON/OFF | `16 40` | toggle | both | 00=OFF,01=ON | TODO | |
| NR level | `14 06` | level | radio | 0000–0255 (0–100%) | TODO | |
| Auto Notch ON/OFF | `16 41` | toggle | both | 00=OFF,01=ON | TODO | SSB/AM |
| Manual Notch ON/OFF | `16 48` | toggle | both | 00=OFF,01=ON | TODO | Position `14 0D`, width `16 57` |
| Manual Notch width | `16 57` | enum | both | 00=WIDE,01=MID,02=NAR | TODO | |
| [NOTCH] switch behavior (SSB) | `1A 05 0064` | enum | menus | 00=Auto,01=Manual,02=Auto/Manual | TODO | |
| [NOTCH] switch behavior (AM) | `1A 05 0065` | enum | menus | 00=Auto,01=Manual,02=Auto/Manual | TODO | |
| Twin Peak Filter (RTTY) | `16 4F` | toggle | both | 00=OFF,01=ON (Mark=2125,Shift=170 only) | TODO | 9700's APF analog (see CW/RTTY) |
| AGC time constant (FAST/MID/SLOW) | `16 12` | enum | both | 01=FAST,02=MID,03=SLOW | TODO | Quick 3-way |
| AGC time (fine, selected) | `1A 04` | level | menus | SSB/CW/RTTY 0=OFF,1=0.1s..13=6.0s; AM 1=0.3s..13=8.0s | TODO | Seconds for selected slot |
| RF gain | `14 02` | level | both | 0000–0255 | done | |
| Squelch level | `14 03` | level | both | 0000–0255 | done | |
| RF/SQL knob behavior | `1A 05 0036` | enum | both | 00=Auto,01=SQL,02=RF+SQL | TODO | Governs `14 02`/`14 03` |
| Attenuator | `11` | enum | both | 00=OFF,10=10dB | TODO | Single 10dB pad |
| Preamp / External Preamp | `16 02` | enum | both | 00=both off,01=P.AMP,02=EXT,03=P.AMP+EXT | TODO | EXT enable per band `1A 05 0093–0095` |
| Dualwatch (sub band) ON/OFF | `16 59` | toggle | both | 00=OFF,01=ON | TODO | Enables sub receiver |
| AF level (volume) | `14 01` | level | both | 0000–0255 | done | Per selected band |
| Main/Sub scope target | `27 12` | enum | radio | 00=Main,01=Sub | done | Selects scope receiver |
| OVF (ADC overflow) status | `1A 0A` | readout | radio | 00=OFF,01=ON | TODO | Duplicate of `15 07` |

---

## Transmit + Metering

Power, mic/comp, VOX, BK-IN, monitor, tone/squelch, split, RIT, PTT, meters.

| Control | CI-V | Type | View | Values | Status | Notes |
|---|---|---|---|---|---|---|
| RF Power | `14 0A` | level | both | 0000–0255 (Min–Max) | done | |
| TX Power Limit 144M on/off | `1A 05 0332` | toggle | menus | 00=OFF,01=ON | TODO | |
| TX Power Limit 144M value | `1A 05 0333` | level | menus | 0000–0255 (1–100%) | TODO | |
| TX Power Limit 430M on/off | `1A 05 0334` | toggle | menus | 00=OFF,01=ON | TODO | |
| TX Power Limit 430M value | `1A 05 0335` | level | menus | 0000–0255 | TODO | |
| TX Power Limit 1200M on/off | `1A 05 0336` | toggle | menus | 00=OFF,01=ON | TODO | |
| TX Power Limit 1200M value | `1A 05 0337` | level | menus | 0000–0255 | TODO | |
| MIC Gain | `14 0B` | level | both | 0000–0255 | TODO | |
| Speech Compressor on/off | `16 44` | toggle | both | 00=OFF,01=ON | TODO | Picks SSB TBW set 0017/18/19 |
| COMP Level | `14 0E` | level | both | 0000–0255 = 0–10 | TODO | |
| VOX on/off | `16 46` | toggle | both | 00=OFF,01=ON | TODO | |
| VOX Gain | `14 16` | level | both | 0000–0255 (0–100%) | TODO | |
| Anti-VOX Gain | `14 17` | level | both | 0000–0255 (0–100%) | TODO | |
| VOX Delay | `1A 05 0330` | level | menus | 00–20 = 0.0–2.0s | TODO | |
| VOX Voice Delay | `1A 05 0331` | enum | menus | 00=OFF,01=Short,02=Mid,03=Long | TODO | |
| Break-In (CW) mode | `16 47` | enum | both | 00=OFF,01=Semi,02=Full | TODO | CW only (see CW/RTTY) |
| Break-In Delay | `14 0F` | level | both | 0000–0255 = 2.0d–13.0d (dots) | TODO | Semi BK hang (see CW/RTTY) |
| Monitor on/off | `16 45` | toggle | both | 00=OFF,01=ON | TODO | |
| Monitor Level | `14 15` | level | both | 0000–0255 (0–100%) | TODO | |
| SSB TX Bandwidth (quick select) | `16 58` | enum | both | 00=WIDE,01=MID,02=NAR | TODO | Edges in 0017/18/19 |
| SSB TX Bandwidth edges WIDE | `1A 05 0017` | enum | menus | Lo(0=100,1=200,2=300,3=500)+Hi(0=2500,1=2700,2=2800,3=2900) | TODO | |
| SSB TX Bandwidth edges MID | `1A 05 0018` | enum | menus | Lo+Hi as 0017 | TODO | |
| SSB TX Bandwidth edges NAR | `1A 05 0019` | enum | menus | Lo+Hi as 0017 | TODO | |
| SSB-D TX passband width | `1A 05 0020` | enum | menus | Lo+Hi as 0017 | TODO | |
| SSB TX Tone Bass/Treble | `1A 05 0015`/`0016` | level | menus | 00–10 = -5..+5 | TODO | |
| AM TX Tone Bass/Treble | `1A 05 0021`/`0022` | level | menus | 00–10 | TODO | |
| FM TX Tone Bass/Treble | `1A 05 0023`/`0024` | level | menus | 00–10 | TODO | |
| DV TX Tone Bass/Treble | `1A 05 0025`/`0026` | level | menus | 00–10 | TODO | |
| Repeater Tone (TONE) on/off | `16 42` | toggle | both | 00=OFF,01=ON | TODO | CTCSS encode |
| Tone Squelch (TSQL) on/off | `16 43` | toggle | both | 00=OFF,01=ON | TODO | |
| DTCS on/off | `16 4B` | toggle | both | 00=OFF,01=ON | TODO | |
| Tone Squelch type (combined) | `16 5D` | enum | both | 00=OFF,01=TONE,02=TSQL,03=DTCS,06=DTCS(T),07=TONE(T)/DTCS(R),08=DTCS(T)/TSQL(R),09=TONE(T)/TSQL(R) | TODO | Single full-mode set |
| Repeater Tone frequency | `1B 00` | enum | both | BCD `00 XX XX`, e.g. 0885 = 88.5Hz | TODO | CTCSS list |
| TSQL Tone frequency | `1B 01` | enum | both | same as `1B 00` | TODO | |
| DTCS code + polarity | `1B 02` | enum | both | [TXpol\|RXpol] + 0 + 3 octal digits; pol 0=Norm,1=Rev | TODO | |
| CSQL code (DV) | `1B 07` | enum | both | 2 digits 00–99 | TODO | DV only (see DV area) |
| Duplex direction (set) | `0F 10`/`11`/`12`/`13` | enum | both | 10=Simplex,11=DUP-,12=DUP+,13=RPS(DD) | TODO | Read via `0F` |
| Duplex offset freq | `0D` (set) / `0C` (read) | number | both | 3-byte BCD (1kHz–10MHz; 10MHz only 1.2G) | TODO | |
| Auto Repeater (USA) | `1A 05 0046` | toggle | menus | 00=OFF,01=ON | TODO | |
| FM SPLIT Offset | `1A 05 0044` | number | menus | dir 00=+/01=- + BCD | TODO | (also in VFO area) |
| Split on/off | `0F 00`/`0F 01` | toggle | both | read `0F` → 00/01 | TODO | |
| Quick Split | `1A 05 0043` | toggle | menus | 00=OFF,01=ON | TODO | |
| Split Lock | `1A 05 0045` | toggle | menus | 00=OFF,01=ON | TODO | |
| RIT frequency | `21 00` | number | both | BCD 1k/100/10/1Hz + sign 00=+/01=-, ±9.999 kHz | TODO | Only clarifier (no XIT) |
| RIT on/off | `21 01` | toggle | both | 00=OFF,01=ON | TODO | |
| Transmit on/off (PTT) | `1C 00` | toggle | both | 00=RX,01=TX | done | |
| TX frequency monitor (XFC) | `1C 02` | toggle | radio | 00=OFF,01=ON | TODO | Monitor TX freq while split |
| Read transmit frequency | `1C 03` | readout | radio | BCD freq (split/dup applied) | TODO | (also in VFO area) |
| TX Delay 144M | `1A 05 0038` | enum | menus | 00=OFF,01=10,02=15,03=20,04=25,05=30ms | TODO | |
| TX Delay 430M | `1A 05 0039` | enum | menus | 00=OFF..05=30ms | TODO | |
| TX Delay 1200M | `1A 05 0040` | enum | menus | 00=OFF..05=30ms | TODO | |
| Time-Out Timer | `1A 05 0041` | enum | both | 00=OFF,01=3,02=5,03=10,04=20,05=30min | TODO | |
| PTT Lock | `1A 05 0042` | toggle | menus | 00=OFF,01=ON | TODO | |
| TX output power on/off (transceive) | `24 00` | toggle | menus | `24 00 00`=read 00/01; `24 00 01`=set | TODO | Separate from RF power level |
| Meter: S-meter | `15 02` | readout | both | 0000=S0,0120=S9,0241=S9+60 | TODO | |
| Meter: PO | `15 11` | readout | both | 0000=0%,0143=50%,0213=100% | TODO | |
| Meter: SWR | `15 12` | readout | both | 0000=1.0,0048=1.5,0080=2.0,0120=3.0 | TODO | |
| Meter: ALC | `15 13` | readout | both | 0000–0120 | TODO | |
| Meter: COMP (dB) | `15 14` | readout | both | 0000=0,0130=15,0210=25.5dB | TODO | |
| Meter: Vd | `15 15` | readout | both | 0000=0V,0013=10V,0241=16V | TODO | |
| Meter: Id | `15 16` | readout | both | 0000=0A,0121=10A,0241=20A | TODO | |
| OVF status | `15 07` | readout | both | 00=OFF,01=ON | TODO | Duplicate of `1A 0A` |
| Squelch (S-meter) status | `15 01` | readout | radio | 00=Close,01=Open | TODO | |
| Various squelch (tone/code) status | `15 05` | readout | radio | 00=Close,01=Open | TODO | |
| Meter Peak Hold (Bar) | `1A 05 0155` | toggle | menus | 00=OFF,01=ON | TODO | No meter-type-select cmd |
| Sub Band Mute on TX — Spk/Phones | `1A 05 0033` | toggle | menus | 00=OFF,01=ON | TODO | |
| Sub Band Mute on TX — USB | `1A 05 0034` | toggle | menus | 00=OFF,01=ON | TODO | |
| Sub Band Mute on TX — LAN | `1A 05 0035` | toggle | menus | 00=OFF,01=ON | TODO | |

---

## Spectrum Scope + Waterfall

| Control | CI-V | Type | View | Values | Status | Notes |
|---|---|---|---|---|---|---|
| Scope ON/OFF | `27 10` | toggle | both | 00=OFF,01=ON | done | Master enable for waveform |
| Scope wave data output | `27 11` | toggle | both | 00=OFF,01=ON | done | Must be ON with `27 10` |
| Read scope waveform data | `27 00` | readout | both | frame: Main/Sub, div, max-div, mode, freq info, in/out, 475 pts 0–160; USB 11 frames, LAN 1 | done | Push only when 10&11 ON |
| Main/Sub scope select | `27 12` | toggle | both | 00=Main,01=Sub | done | (shared with RX-DSP area) |
| Scope mode | `27 14` | enum | both | scope byte (00 Main/01 Sub) + 00=Center,01=Fixed,02=SCROLL-C,03=SCROLL-F | TODO | Primary mode switch |
| Scope span (Center/SCROLL-C) | `27 15` | enum | both | Main/Sub + BCD span: 2.5k/5k/10k/25k/50k/100k/250k/500k | TODO | ±value, 8 steps |
| Scope Edge number (Fixed/SCROLL-F) | `27 16` | enum | both | Main/Sub + 01–04 | TODO | Active fixed-edge set |
| Scope Hold (peak) | `27 17` | toggle | both | Main/Sub + 00=OFF,01=ON | TODO | See Max Hold `1A 05 0188` |
| Scope Reference level | `27 19` | level | both | 3 bytes: 10dB/1dB BCD + 0.1dB(0/5) + sign; -20.0..+20.0 in 0.5dB | TODO | Common Main/Sub |
| Scope Sweep speed | `27 1A` | enum | both | Main/Sub + 00=FAST,01=MID,02=SLOW | TODO | |
| Scope during TX (CENTER) | `27 1B` | toggle | both | 00=OFF,01=ON | TODO | Mirror of `1A 05 0187` |
| CENTER Type Display | `27 1C` | enum | both | 00=Filter center,01=Carrier,02=Carrier(Abs) | TODO | Mirror of `1A 05 0189` |
| Scope VBW | `27 1D` | enum | both | Main/Sub + 00=Narrow,01=Wide | TODO | Mirror of `1A 05 0191` |
| Scope Fixed edge freqs (live) | `27 1E` | number | both | range(01=144M,02=430M,03=1200M)+edge 01–04+lower(5B)+higher(5B) | TODO | Live twin of `1A 05 0202..` |
| Marker Position (FIX/SCROLL) | `27 20` | enum | both | 00=Filter Center,01=Carrier Point | TODO | Mirror of `1A 05 0190` |
| Scope during TX (menu) | `1A 05 0187` | toggle | menus | 00=OFF,01=ON | TODO | Twin of `27 1B` |
| Max Hold | `1A 05 0188` | enum | menus | 00=OFF,01=10s,02=ON | TODO | Richer than `27 17` |
| CENTER Type Display (menu) | `1A 05 0189` | enum | menus | 00=Filter,01=Carrier,02=Carrier(Abs) | TODO | Twin of `27 1C` |
| Marker Position (menu) | `1A 05 0190` | enum | menus | 00=Filter,01=Carrier | TODO | Twin of `27 20` |
| Scope VBW (menu) | `1A 05 0191` | enum | menus | 00=Narrow,01=Wide | TODO | Twin of `27 1D` |
| Averaging | `1A 05 0192` | enum | menus | 00=OFF,01=2,02=3,03=4 | TODO | |
| Waveform Type | `1A 05 0193` | enum | menus | 00=Fill,01=Fill+Line | TODO | |
| Waveform Color (Current) | `1A 05 0194` | number | menus | RGB (R/G/B 0–255) | TODO | |
| Waveform Color (Line) | `1A 05 0195` | number | menus | RGB | TODO | |
| Waveform Color (Max Hold) | `1A 05 0196` | number | menus | RGB | TODO | |
| Waterfall Display | `1A 05 0197` | toggle | both | 00=OFF,01=ON | TODO | Master waterfall enable |
| Waterfall Speed | `1A 05 0198` | enum | menus | 00=Slow,01=Mid,02=Fast | TODO | |
| Waterfall Size (Expand) | `1A 05 0199` | enum | menus | 00=Small,01=Mid,02=Large | TODO | |
| Waterfall Peak Color Level | `1A 05 0200` | enum | menus | 00=Grid1..07=Grid8 | TODO | |
| Waterfall Marker Auto-hide | `1A 05 0201` | toggle | menus | 00=OFF,01=ON | TODO | |
| Fixed Edges 144M No.1–4 | `1A 05 0202`/`0203`/`0204`/`0348` | number | menus | lower+higher BCD pair (144–148MHz) | TODO | No.4 lives at 0348 |
| Fixed Edges 430M No.1–4 | `1A 05 0205`/`0206`/`0207`/`0349` | number | menus | lower+higher (430–450MHz) | TODO | No.4 at 0349 |
| Fixed Edges 1200M No.1–4 | `1A 05 0208`/`0209`/`0210`/`0350` | number | menus | lower+higher (1240–1300MHz) | TODO | No.4 at 0350 |
| Audio Scope FFT Waveform Type | `1A 05 0211` | enum | menus | 00=Line,01=Fill | TODO | AUDIO SCOPE (distinct from RF) |
| Audio Scope FFT Waveform Color | `1A 05 0212` | number | menus | RGB | TODO | |
| Audio Scope FFT Waterfall | `1A 05 0213` | toggle | menus | 00=OFF,01=ON | TODO | |
| Audio Scope Oscilloscope Color | `1A 05 0214` | number | menus | RGB | TODO | |

---

## CW + RTTY

| Control | CI-V | Type | View | Values | Status | Notes |
|---|---|---|---|---|---|---|
| CW keyer speed | `14 0C` | level | both | 0000–0255 = 6–48 WPM | TODO | |
| CW pitch | `14 09` | level | both | 0000=300,0128=600,0255=900Hz (5Hz) | TODO | |
| Break-In Delay | `14 0F` | level | both | 0000–0255 = 2.0d–13.0d | TODO | (also TX area) |
| Break-In mode | `16 47` | enum | both | 00=OFF,01=Semi,02=Full | TODO | (also TX area) |
| Keyer Type | `1A 05 0227` | enum | menus | 00=Straight,01=Bug,02=Paddle | TODO | |
| Paddle Polarity | `1A 05 0226` | toggle | menus | 00=Normal,01=Reverse | TODO | |
| MIC Up/Down as paddle | `1A 05 0228` | toggle | menus | 00=OFF,01=ON | TODO | |
| Side Tone Level | `1A 05 0221` | level | menus | 0000–0255 (0–100%) | TODO | |
| Side Tone Level Limit | `1A 05 0222` | toggle | menus | 00=OFF,01=ON | TODO | |
| Keyer Repeat Time | `1A 05 0223` | level | menus | 01–60 = 1–60s | TODO | |
| Dot/Dash Ratio | `1A 05 0224` | level | menus | 28–45 = 1:1:2.8–4.5 (val/10) | TODO | |
| Rise Time | `1A 05 0225` | enum | menus | 00=2,01=4,02=6,03=8ms | TODO | |
| CW Normal Side | `1A 05 0067` | toggle | menus | 00=LSB,01=USB | TODO | |
| SSB/CW Synchronous Tuning | `1A 05 0066` | toggle | menus | 00=OFF,01=ON | TODO | |
| CW RX HPF/LPF | `1A 05 0013` | enum | menus | HPF 00=Through/01–20=100–2000Hz; LPF 05–24=500–2400Hz/25=Through | TODO | |
| Send CW message | `17` | action | both | ≤30 ASCII; `FF` stops; `^`=no inter-char space | TODO | Keyboard/macro TX |
| Memory keyer M1–M8 contents | `1A 02` | readout | menus | ch 01=M1..08=M8 + text; `*`=contest#, `^`=prosign | TODO | Play stored = re-send via `17` |
| Keyer contest number style | `1A 05 0218` | enum | menus | 00=Normal,01=190>ANO,02=190>ANT,03=90>NO,04=90>NT | TODO | |
| Keyer count-up trigger | `1A 05 0219` | enum | menus | 01=M1..08=M8 | TODO | |
| Keyer present number | `1A 05 0220` | number | menus | 0001–9999 | TODO | |
| RTTY Mark Frequency | `1A 05 0047` | enum | both | 00=1275,01=1615,02=2125Hz | TODO | TPF needs 2125 |
| RTTY Shift Width | `1A 05 0048` | enum | both | 00=170,01=200,02=425Hz | TODO | TPF needs 170 |
| RTTY Keying Polarity | `1A 05 0049` | toggle | both | 00=Normal,01=Reverse | TODO | |
| Twin Peak Filter (TPF) | `16 4F` | toggle | both | 00=OFF,01=ON (Mark=2125 & Shift=170 only) | TODO | (also RX-DSP area) |
| AFC function | `16 4A` | toggle | both | 00=OFF,01=ON | TODO | RTTY/FM AFC |
| AFC Limit | `1A 05 0063` | toggle | menus | 00=OFF,01=ON | TODO | |
| RTTY Decode USOS | `1A 05 0231` | toggle | menus | 00=OFF,01=ON | TODO | |
| RTTY Decode New Line | `1A 05 0232` | toggle | menus | 00=CR/LF/CR+LF,01=CR+LF | TODO | |
| RTTY TX USOS | `1A 05 0233` | toggle | menus | 00=OFF,01=ON | TODO | |
| RTTY FFT scope averaging | `1A 05 0229` | enum | menus | 00=OFF,01=2,02=3,03=4 | TODO | |
| RTTY FFT scope waveform color | `1A 05 0230` | number | menus | RGB | TODO | |
| RTTY decode font color (RX) | `1A 05 0235` | number | menus | RGB | TODO | |
| RTTY decode font color (TX) | `1A 05 0236` | number | menus | RGB | TODO | |
| RTTY chars during TX (sat) | `1A 05 0234` | toggle | menus | 00=RX,01=TX | TODO | |
| RTTY decode log on/off | `1A 05 0237` | toggle | menus | 00=OFF,01=ON | TODO | |
| RTTY log file type | `1A 05 0238` | toggle | menus | 00=Text,01=HTML | TODO | |
| RTTY log time stamp | `1A 05 0239` | toggle | menus | 00=OFF,01=ON | TODO | |
| RTTY log time stamp Local/UTC | `1A 05 0240` | toggle | menus | 00=Local,01=UTC | TODO | |
| RTTY log time stamp freq | `1A 05 0241` | toggle | menus | 00=OFF,01=ON | TODO | |
| RTTY RX HPF/LPF | `1A 05 0014` | enum | menus | HPF 00=Through/01–20; LPF 05–24/25=Through | TODO | |
| RTTY IF filter width (FIL) | `1A 03` | enum | both | RTTY 0–9=50–500Hz,10–31=600–2700Hz | TODO | Mode-dependent (see RX-DSP) |
| DATA/USB(B) RTTY Decode function | `1A 05 0133` | enum | menus | 00=OFF,01=RTTY,02=DV Data,03=GPS/Wx,04=CI-V | TODO | Route DATA jack (USB(B)=0132) |
| RTTY Decode Baud Rate | `1A 05 0136` | enum | menus | 00=4800,01=9600,02=19200,03=38400 | TODO | |
| USB Keying (CW) | `1A 05 0121` | enum | menus | 00=OFF,01=USB(A)DTR,02=RTS,03=USB(B)DTR,04=RTS | TODO | |
| USB Keying (RTTY) | `1A 05 0122` | enum | menus | 00=OFF,01–04 DTR/RTS | TODO | |

---

## DV / D-STAR / DD

| Control | CI-V | Type | View | Values | Status | Notes |
|---|---|---|---|---|---|---|
| DV mode select | `04`/`06` | enum | both | mode 17=DV (+filter via `06`); DD = DV on 1.2G+RPS | done | No separate DD mode code |
| DV/DD mode+filter (selected VFO) | `26` | enum | both | op-mode+DATA+filter for MAIN band | done | |
| DD Repeater Simplex (RPS) | `0F 13` | action | both | set RPS; read via `0F`→13 | TODO | DD only; pairs with `0F 10` |
| MY Call Sign | `1F 00` | readout | both | 12 chars (8 call + 4 note); read=no data, write=12B | TODO | |
| UR (Destination) call | `1F 01` | readout | both | bytes 1–8 of 24-char block | TODO | Reflector link/unlink string |
| RPT1 / R1 call | `1F 01` | readout | both | bytes 9–16 | TODO | Same command |
| RPT2 / R2 call | `1F 01` | readout | both | bytes 17–24 | TODO | Same command |
| TX Message (DV) | `1F 02` | readout | both | ≤20 chars; `FF` stops | TODO | |
| TX Call Sign Display source | `1A 05 0165` | enum | menus | 00=OFF,01=Your,02=My | TODO | |
| RX Call Sign Display | `1A 05 0160` | enum | menus | 00=OFF,01=Normal,02=RX Hold,03=Hold | TODO | |
| Received Call Sign (Name/Call) | `1A 05 0338` | toggle | menus | 00=Call Sign,01=Name | TODO | |
| RX Call Signs auto-output | `20 00 00` | toggle | both | 00=OFF,01=ON (resets at power-on) | TODO | |
| RX Call Signs (read) | `20 00 02` | readout | both | caller/called/R1/R2 + notes + header flags | TODO | EMR/BK/Data bits |
| RX Message auto-output | `20 01 00` | toggle | both | 00=OFF,01=ON | TODO | |
| RX Message (read) | `20 01 02` | readout | both | 20-char msg + caller + note | TODO | |
| RX Status auto-output | `20 02 00` | toggle | both | 00=OFF,01=ON | TODO | |
| RX Status (read) | `20 02 02` | readout | both | voice/data/last/BK/EMR/non-DV bits | TODO | |
| RX GPS/D-PRS auto-output | `20 03 00` | toggle | both | 00=OFF,01=ON | TODO | |
| RX D-PRS Position (read) | `20 03 0200` | readout | both | lat/lon/symbol etc | TODO | 0201=Object,0202=Item,0203=Wx |
| RX D-PRS message auto-output | `20 04 00` | toggle | both | 00=OFF,01=ON | TODO | |
| RX D-PRS message (read) | `20 04 02` | readout | both | message + caller/SSID | TODO | |
| DV TX low-speed data | `22 00` | number | both | ≤30 bytes (FA–FF escaped) | TODO | |
| DV RX data auto-output | `22 01 00` | toggle | both | 00=OFF,01=ON (read `22 01 01`) | TODO | |
| DV Data TX trigger | `1A 05 0076` (`22 02`) | enum | menus | 00=PTT,01=Auto | TODO | |
| DV Fast Data | `1A 05 0077` (`22 03`) | toggle | menus | 00=OFF,01=ON | TODO | |
| DV GPS Data Speed | `1A 05 0078` (`22 04`) | enum | menus | 00=Slow,01=Fast | TODO | |
| DV Fast Data TX Delay (PTT) | `1A 05 0079` (`22 05`) | enum | menus | 00=OFF,01=1s..10=10s | TODO | |
| Digital squelch DSQL/CSQL | `16 5B` | enum | both | 00=OFF,01=DSQL,02=CSQL | TODO | DV only (QA fix: was 1A 05 5B) |
| DV Digital Code (CSQL) | `1B 07` | number | both | 2 digits 00–99 | TODO | (also TX area) |
| Standby Beep | `1A 05 0074` | enum | menus | 00=OFF,01=ON,02=ON(High),03=ON(Alarm/High) | TODO | |
| Auto Reply | `1A 05 0075` | enum | menus | 00=OFF,01=ON,02=Voice | TODO | |
| Digital Monitor | `1A 05 0080` | enum | menus | 00=Auto,01=Digital,02=Analog | TODO | |
| Digital Repeater Set | `1A 05 0081` | toggle | menus | 00=OFF,01=ON | TODO | |
| DV Auto Detect | `1A 05 0082` | toggle | menus | 00=OFF,01=ON | TODO | |
| RX Record (RPT) | `1A 05 0083` | enum | menus | 00=ALL,01=Latest Only | TODO | |
| DV BK (Break-in) | `1A 05 0084` | toggle | menus | 00=OFF,01=ON | TODO | Distinct from CW BK `16 47` |
| DV EMR | `1A 05 0085` | toggle | menus | 00=OFF,01=ON | TODO | |
| EMR AF Level | `1A 05 0086` | level | menus | 0000–0255 | TODO | |
| DD TX Inhibit (Power ON) | `1A 05 0087` | toggle | menus | 00=OFF,01=ON | TODO | |
| DD Packet Output | `1A 05 0088` | enum | menus | 00=Normal,01=All | TODO | |
| GPS Select | `1A 05 0255` | enum | menus | 00=OFF,01=External,02=Manual | TODO | |
| GPS Receiver Baud Rate | `1A 05 0256` | enum | menus | 00=4800,01=9600 | TODO | |
| GPS Manual Position | `1A 05 0257` | number | menus | lat/lon/altitude payload | TODO | |
| My Position (live GPS read) | `23 00` | readout | both | lat/lon/alt/course/speed/UTC | TODO | Set when Manual |
| GPS TX Mode | `1A 05 0258` (`16 5C`) | enum | both | 00=OFF,01=D-PRS,02=NMEA | TODO | 16 5C set-only; read via 0258 |
| D-PRS Unproto Address | `1A 05 0259` | number | menus | ≤56 chars (APRS path) | TODO | |
| D-PRS TX Format | `1A 05 0260` | enum | menus | 00=Position,01=Object,02=Item,03=Weather | TODO | Selects subtree |
| D-PRS Position Symbol | `1A 05 0261` | enum | menus | 00=No.1..03=No.4 (slots 0262–0265) | TODO | |
| D-PRS Position SSID | `1A 05 0266` | enum | menus | 00=---,01=(-0),02=-1..16=-15,17=-A..42=-Z | TODO | |
| D-PRS Position Comment | `1A 05 0267`/`0268–0271` | enum | menus | 0267 selects 1–4; 0268–0271 = 43-char strings | TODO | |
| D-PRS Position Time Stamp | `1A 05 0272` | enum | menus | 00=OFF,01=DHM,02=HMS | TODO | |
| D-PRS Position Altitude TX | `1A 05 0273` | toggle | menus | 00=OFF,01=ON | TODO | |
| D-PRS Position Data Extension | `1A 05 0274` | enum | menus | 00=OFF,01=Course/Speed,02=PHGD (0275–0278) | TODO | |
| D-PRS Object subtree | `1A 05 0279–0290` | enum | menus | name/Live-Kill/symbol/comment/position/ext... | TODO | |
| D-PRS Item subtree | `1A 05 0291–0304` | enum | menus | SSID/type/name/symbol/comment/position/ext... | TODO | |
| D-PRS Weather subtree | `1A 05 0305–0309` | enum | menus | SSID/.../time stamp (0309: 00=OFF,01=DHM,02=HMS) | TODO | |
| NMEA GPS Sentence selects | `1A 05 0310–0315` | toggle | menus | RMC/GGA/GLL/GSA/VTG/GSV (max 4 ON) | TODO | |
| NMEA GPS Message | `1A 05 0316` | number | menus | ≤20 chars | TODO | |
| GPS Alarm Area (Group) | `1A 05 0317` | number | menus | area coords | TODO | |
| GPS Alarm Area (RX/Memory) | `1A 05 0318` | enum | menus | 00=Limited,01=Extended,02=Both | TODO | |
| GPS Auto TX timer | `1A 05 0319` | enum | menus | 00=OFF,01=5s..08=30m | TODO | |
| GPS Time Correct | `1A 05 0183` | enum | menus | 00=OFF,01=Auto | TODO | |
| RX Position Indicator | `1A 05 0161` | toggle | menus | 00=OFF,01=ON | TODO | |
| RX Position Display | `1A 05 0162` | enum | menus | 00=OFF,01=ON(Main/Sub),02=ON(Main) | TODO | |
| RX Position Display Timer | `1A 05 0163` | enum | menus | 00=5s,01=10s,02=15s,03=30s,04=Hold | TODO | |
| Reply Position Display | `1A 05 0164` | toggle | menus | 00=OFF,01=ON | TODO | |
| RX Call Sign SPEECH | `1A 05 0053` | enum | menus | 00=OFF,01=ON(Kerchunk),02=ON(All) | TODO | |
| RX>CS SPEECH | `1A 05 0054` | toggle | menus | 00=OFF,01=ON | TODO | |
| RX History Log (to SD) | `1A 05 0090` | toggle | menus | 00=OFF,01=ON | TODO | |
| QSO Log | `1A 05 0089` | toggle | menus | 00=OFF,01=ON | TODO | |

---

## Satellite

| Control | CI-V | Type | View | Values | Status | Notes |
|---|---|---|---|---|---|---|
| Satellite Mode | `16 5A` | toggle | both | 00=OFF,01=ON | TODO | Reverse-tracking is a memory attribute |
| Satellite Memory Content | `1A 07` | number | menus | ch 0001–0099 + uplink/downlink freq/mode/tone/name | TODO | Full SAT channel incl tracking |
| Sub Band (Dualwatch) | `16 59` | toggle | both | 00=OFF,01=ON | TODO | Required for SAT (see RX-DSP) |

---

## SET-mode menu tree + System

Tone-control, beeps, speech, connectors, network, display, time, REF, power, etc. (RX/TX tone-control and many DV/scope items already appear in their functional areas above; listed here are the remaining SET-only items.)

| Control | CI-V | Type | View | Values | Status | Notes |
|---|---|---|---|---|---|---|
| SSB RX HPF/LPF | `1A 05 0001` | enum | menus | HPF 00=Through/01–20; LPF 05–24/25=Through | TODO | HPF < LPF |
| SSB RX Tone Bass/Treble | `1A 05 0002`/`0003` | level | menus | 00–10 (-5..+5) | TODO | |
| AM RX HPF/LPF | `1A 05 0004` | enum | menus | HPF/LPF | TODO | |
| AM RX Tone Bass/Treble | `1A 05 0005`/`0006` | level | menus | 00–10 | TODO | |
| FM RX HPF/LPF | `1A 05 0007` | enum | menus | HPF/LPF | TODO | |
| FM RX Tone Bass/Treble | `1A 05 0008`/`0009` | level | menus | 00–10 | TODO | |
| DV RX HPF/LPF | `1A 05 0010` | enum | menus | HPF/LPF | TODO | |
| DV RX Tone Bass/Treble (Auto) | `1A 05 0011`/`0012` | level | menus | 00–10 | TODO | |
| Beep Level | `1A 05 0027` | level | menus | 0000–0255 | TODO | |
| Beep Level Limit | `1A 05 0028` | toggle | menus | 00=OFF,01=ON | TODO | |
| Beep (Confirmation) | `1A 05 0029` | toggle | menus | 00=OFF,01=ON | TODO | |
| Band Edge Beep | `1A 05 0030` | enum | menus | 00=OFF,01=ON,02=ON(User),03=ON(User)&TX Limit | TODO | |
| Beep Sound MAIN/SUB | `1A 05 0031`/`0032` | level | menus | 0050–0200 (500–2000Hz) | TODO | |
| FM/DV Center Error | `1A 05 0037` | toggle | menus | 00=OFF,01=ON | TODO | |
| SPEECH Language | `1A 05 0050` | enum | menus | 00=English,01=Japanese | TODO | |
| SPEECH Alphabet | `1A 05 0051` | enum | menus | 00=Normal,01=Phonetic | TODO | |
| SPEECH Speed | `1A 05 0052` | enum | menus | 00=Slow,01=Fast | TODO | |
| S-Level SPEECH | `1A 05 0055` | toggle | menus | 00=OFF,01=ON | TODO | |
| MODE SPEECH | `1A 05 0056` | toggle | menus | 00=OFF,01=ON | TODO | |
| SPEECH Level | `1A 05 0057` | level | menus | 0000–0255 | TODO | |
| MIC Up/Down Speed | `1A 05 0062` | enum | menus | 00=Slow,01=Fast | TODO | |
| Screen Keyboard Type | `1A 05 0068` | enum | menus | 00=Ten-key,01=Full | TODO | |
| Screen Full Keyboard Layout | `1A 05 0069` | enum | menus | 00=English,01=German,02=French | TODO | |
| Screen Capture [POWER] Switch | `1A 05 0070` | toggle | menus | 00=OFF,01=ON | TODO | |
| Screen Capture File Type | `1A 05 0071` | enum | menus | 00=PNG,01=BMP | TODO | |
| REF Adjust | `1A 05 0072` | level | menus | 0000–0255 | TODO | |
| REF Adjust (FINE) | `1A 05 0073` | level | menus | 0000–0255 | TODO | |
| QSO Log CSV Separator/Decimal | `1A 05 0091` | enum | menus | 00=,/. 01=;/. 02=;/, | TODO | |
| QSO Log CSV Date | `1A 05 0092` | enum | menus | 00=yyyy/mm/dd,01=mm/dd/yyyy,02=dd/mm/yyyy | TODO | |
| External P.AMP 144/430/1200M | `1A 05 0093`/`0094`/`0095` | toggle | menus | 00=OFF,01=ON | TODO | EXT preamp enable per band |
| External Speaker Separate | `1A 05 0096` | enum | menus | 00=Separate,01=Mix | TODO | |
| Phones Level | `1A 05 0097` | level | menus | 00–30 (-15..+15dB) | TODO | |
| Phones L/R Mix | `1A 05 0098` | enum | menus | 00=Separate,01=Mix,02=Auto | TODO | |
| ACC AF/SQL Output Select | `1A 05 0099` | enum | menus | 00=MAIN,01=SUB | TODO | |
| ACC Output Select (AF/IF) | `1A 05 0100` | enum | menus | 00=AF,01=IF | TODO | |
| ACC AF Output Level | `1A 05 0101` | level | menus | 0000–0255 | TODO | |
| ACC AF SQL | `1A 05 0102` | enum | menus | 00=OFF(Open),01=ON | TODO | |
| ACC AF Beep/Speech Output | `1A 05 0103` | toggle | menus | 00=OFF,01=ON | TODO | |
| ACC IF Output Level | `1A 05 0104` | level | menus | 0000–0255 | TODO | |
| USB Output Select (AF/IF) | `1A 05 0105` | enum | menus | 00=AF,01=IF | TODO | |
| USB AF Output Level | `1A 05 0106` | level | menus | 0000–0255 | TODO | |
| USB AF SQL | `1A 05 0107` | enum | menus | 00=OFF(Open),01=ON | TODO | |
| USB AF Beep/Speech Output | `1A 05 0108` | toggle | menus | 00=OFF,01=ON | TODO | |
| USB IF Output Level | `1A 05 0109` | level | menus | 0000–0255 | TODO | |
| LAN Output Select (AF/IF) | `1A 05 0110` | enum | menus | 00=AF,01=IF | TODO | |
| LAN AF SQL | `1A 05 0111` | enum | menus | 00=OFF(Open),01=ON | TODO | |
| ACC MOD Level | `1A 05 0112` | level | menus | 0000–0255 | TODO | |
| USB MOD Level | `1A 05 0113` | level | menus | 0000–0255 | done | USB audio TX gain |
| LAN MOD Level | `1A 05 0114` | level | menus | 0000–0255 | done | LAN audio TX gain |
| DATA OFF MOD | `1A 05 0115` | enum | menus | 00=MIC,01=ACC,02=MIC,ACC,03=USB,04=MIC,USB,05=LAN | done | Audio source routing |
| DATA MOD | `1A 05 0116` | enum | menus | 00=MIC..05=LAN | TODO | |
| ACC SEND Output 144/430/1200M | `1A 05 0117`/`0118`/`0119` | toggle | menus | 00=OFF,01=ON | TODO | |
| USB SEND | `1A 05 0120` | enum | menus | 00=OFF,01=USB(A)DTR,02=RTS,03=USB(B)DTR,04=RTS | TODO | |
| USB Inhibit Timer at connection | `1A 05 0123` | toggle | menus | 00=OFF,01=ON | TODO | |
| External Keypad VOICE/KEYER/RTTY | `1A 05 0124`/`0125`/`0126` | toggle | menus | 00=OFF,01=ON | TODO | |
| CI-V Transceive | `1A 05 0127` | toggle | menus | 00=OFF,01=ON | TODO | Enables freq/mode broadcast |
| CI-V USB/LAN→REMOTE Transceive Addr | `1A 05 0128` | number | menus | 0000–0223 (00h–DFh) | TODO | |
| CI-V USB Port | `1A 05 0129` | enum | menus | 00=Link to REMOTE,01=Unlink | TODO | Read only |
| CI-V USB Echo Back | `1A 05 0130` | toggle | menus | 00=OFF,01=ON | TODO | |
| CI-V DATA Echo Back | `1A 05 0131` | toggle | menus | 00=OFF,01=ON | TODO | |
| USB(B) Function | `1A 05 0132` | enum | menus | 00=OFF,01=RTTY Decode,02=DV Data | TODO | |
| GPS Out (USB(B)/DATA) | `1A 05 0134` | enum | menus | 00=OFF,01=DATA→USB(B) | TODO | |
| DV Data/GPS Out Baud Rate | `1A 05 0135` | enum | menus | 00=4800,01=9600 | TODO | |
| Network DHCP | `1A 05 0137` | toggle | menus | 00=OFF,01=ON (after restart) | TODO | |
| IP Address (set) | `1A 05 0138` | number | menus | 16-digit; DHCP OFF | TODO | |
| IP Address (read assigned) | `1A 05 0139` | readout | menus | 16-digit | TODO | Read only |
| Subnet Mask | `1A 05 0140` | enum | menus | 01–30 (bits) | TODO | DHCP OFF |
| Default Gateway | `1A 05 0141` | number | menus | 16-digit or FF=Blank | TODO | |
| Primary/2nd DNS | `1A 05 0142`/`0143` | number | menus | 16-digit or FF=Blank | TODO | |
| Network Name | `1A 05 0144` | number | menus | ASCII ≤15 chars | TODO | |
| Network Control | `1A 05 0145` | toggle | menus | 00=OFF,01=ON (after restart) | TODO | Enables RS-BA1 |
| Power OFF Setting (Remote) | `1A 05 0146` | enum | menus | 00=Shutdown,01=Standby/Shutdown | TODO | |
| Control/Serial/Audio Port (UDP) | `1A 05 0147`/`0148`/`0149` | number | menus | 000001–065535 | TODO | After restart |
| Internet Access Line | `1A 05 0150` | enum | menus | 00=FTTH,01=ADSL/CATV | TODO | |
| Network Radio Name | `1A 05 0151` | number | menus | ASCII ≤16 chars | TODO | |
| LCD Backlight | `1A 05 0152` | level | both | 0000–0255 | TODO | Also via `19` |
| Display Type (Theme A/B) | `1A 05 0153` | enum | menus | 00=A,01=B | TODO | |
| Display Font | `1A 05 0154` | enum | menus | 00=Basic,01=Round | TODO | |
| MN-Q Popup | `1A 05 0157` | toggle | menus | 00=OFF,01=ON | TODO | |
| BW Popup (PBT) | `1A 05 0158` | toggle | menus | 00=OFF,01=ON | TODO | |
| BW Popup (FIL) | `1A 05 0159` | toggle | menus | 00=OFF,01=ON | TODO | |
| Scroll Speed | `1A 05 0166` | enum | menus | 00=Slow,01=Fast | TODO | |
| Screen Saver | `1A 05 0167` | enum | menus | 00=OFF,01=15,02=30,03=60min | TODO | |
| Opening Message | `1A 05 0168` | toggle | menus | 00=OFF,01=ON | TODO | |
| Power ON Check | `1A 05 0169` | toggle | menus | 00=OFF,01=ON | TODO | |
| Display Unit Lat/Lon | `1A 05 0170` | enum | menus | 00=ddd mm.mm,01=ddd mm ss,02=ddd.dddd | TODO | |
| Display Unit Altitude/Distance | `1A 05 0171` | enum | menus | 00=m,01=ft/mi | TODO | |
| Display Unit Speed | `1A 05 0172` | enum | menus | 00=km/h,01=mph,02=knots | TODO | |
| Display Unit Temperature | `1A 05 0173` | enum | menus | 00=C,01=F | TODO | |
| Display Unit Barometric | `1A 05 0174` | enum | menus | 00=hPa,01=mb,02=mmHg,03=inHg | TODO | |
| Display Unit Rainfall | `1A 05 0175` | enum | menus | 00=mm,01=inch | TODO | |
| Display Unit Wind Speed | `1A 05 0176` | enum | menus | 00=m/s,01=km/h,02=mph,03=knots | TODO | |
| Display Language | `1A 05 0177` | enum | menus | 00=English,01=Japanese | TODO | |
| System Language | `1A 05 0178` | enum | menus | 00=English,01=Japanese | TODO | |
| Date | `1A 05 0179` | number | menus | 20000101–20991231 | TODO | |
| Time | `1A 05 0180` | number | menus | 0000–2359 | TODO | |
| NTP Function | `1A 05 0181` | toggle | menus | 00=OFF,01=ON | TODO | |
| NTP Server Address | `1A 05 0182` | number | menus | ASCII string | TODO | |
| UTC Offset | `1A 05 0184` | number | menus | dir 00=+/01=- + 0000–1400 | TODO | |
| SD CSV Separator/Decimal | `1A 05 0185` | enum | menus | 00=,/. 01=;/. 02=;/, | TODO | |
| SD CSV Date | `1A 05 0186` | enum | menus | 00=yyyy/mm/dd,01=mm/dd/yyyy,02=dd/mm/yyyy | TODO | |
| Front Key [VOX/BK-IN] Customize | `1A 05 0343` | enum | menus | 00–08 (VOX/BK-IN, CD, PRESET, Home CH, Temp Skip, Mem1–4) | TODO | |
| Front Key [AUTOTUNE/AFC] Customize | `1A 05 0344` | enum | menus | 00–14 | TODO | |
| Front Key [TONE/RX>CS] Customize | `1A 05 0345` | enum | menus | 00–05 | TODO | |
| MIC Key [UP]/[DN] Customize | `1A 05 0346`/`0347` | enum | menus | 00–27 (28-entry list) | TODO | |
| Home CH Beep | `1A 05 0340` | toggle | menus | 00=OFF,01=ON | TODO | |
| PTT Port Function | `1A 05 0341` | enum | menus | 00=PTT Input,01=PTT Input+SEND | TODO | |
| RX Picture Indicator | `1A 05 0342` | toggle | menus | 00=OFF,01=ON | TODO | |
| Compass Direction | `1A 05 0339` | enum | menus | 00=Heading Up,01=North Up,02=South Up | TODO | |
| DTMF Speed | `1A 05 0320` | enum | menus | 00=100,01=200,02=300,03=500ms | TODO | |
| NTP server access trigger | `1A 08` | action | menus | 00=Terminate,01=Initiate | TODO | |
| NTP access result | `1A 09` | readout | menus | 00=accessing,01=Succeeded,02=Failed | TODO | Read only |
| Power ON | `18 01` | action | menus | send with FE preamble padding | TODO | |
| Power OFF | `18 00` | action | menus | turns off | TODO | |
| LCD Backlight (direct) | `19` | level | both | 0000–0255 | TODO | Mirrors `1A 05 0152` |

---

## Front-panel-only (no CI-V)

Genuinely cannot be driven remotely on the IC-9700 — surface as informational/disabled in the UI, not as controls:

- **APF (Audio Peak Filter, CW)** — no CI-V command; the 9700 has no CW APF. Closest analog is the RTTY Twin Peak Filter (`16 4F`).
- **RX antenna select** — no separate RX antenna jack or command.
- **MAIN/SUB AF balance** — no balance command; set AF per band via `14 01` after `07 D0`/`07 D1`.
- **Twin-PBT "clear" / PBT center reset** — no dedicated command; set `14 07` and `14 08` to `0128`.
- **Standalone IF SHIFT** — no command; emulate by moving PBT1 (`14 07`) and PBT2 (`14 08`) together.
- **XIT / ΔTX** — no XIT command; RIT (`21`) is the only clarifier.
- **RIT/CLEAR knob & zero action** — set value via `21 00`; no dedicated CLEAR command beyond writing 0.
- **Meter-type select** — no select command; read each meter individually via `15 11`–`15 16`.
- **Memo Pad write/recall ([MPAD])** — only quantity (`1A 05 0060`) is addressable; pad contents not on CI-V.
- **VFO/MEMO [V/M] key visual toggle, BAND-key band-stacking cycling, M-CH up/down rotary, 1Hz readout on/off** — registers/values are addressable but the physical cycling/toggle actions are not.
- **TS quick-toggle key** — step value via `10`; the enable-TS-mode toggle is front-panel.
- **RTTY decode display buffer & on-screen-keyboard/memory RTTY TX** — only decode settings are addressable; `17` is CW-only.
- **"Play memory keyer Mx" / "Send RTTY memory" buttons** — no trigger command; read text (`1A 02`) and re-send via `17` (CW only).
- **CW zero-in / [AUTOTUNE]** — momentary front-panel action, not a discrete CI-V set.
- **DR mode entry/exit, FROM/TO browse, Repeater List & Your-Call-Sign memory management, Reflector link/unlink/Echo Test, RX>CS, RX Call Sign History browse, Near Repeater search, Position Reset** — front-panel + SD-card CSV only. (Reflector linking achievable over the air by setting UR via `1F 01`.)
- **CI-V Address (default A2h) & CI-V Baud Rate (default Auto)** — SET-menu only; not `1A 05` items, no read/set command.
- **Bluetooth** — no hardware/menu on the IC-9700.
- **Satellite Normal/Reverse tracking link** — attribute of the SAT memory write (`1A 07`), not a standalone toggle.
- **SD Card Save/Load/Format/Unmount & file management** — radio SD menu only (only CSV-format items `0185`/`0186` are addressable).

---

## Build order

Phased milestones for the Hybrid layout (Radio view = TFT-style main screen; Menus/SET view = clean lists; Mobile = accordion). Each builds on the prior and is independently shippable.

- **M0 — Foundation (already shipped):** freq set/read (`03`/`05`), mode+filter (`04`/`06`/`01`), VFO A/B/swap/equalize (`07`), PTT (`1C 00`), AF/RF/SQL/RF-power (`14 01/02/03/0A`), scope stream (`27 10/11/00/12`), USB/LAN MOD + DATA routing (`1A 05 0113/0114/0115`).
- **M1 — Dual-watch + meters + core RX:** MAIN/SUB select & state (`07 D0/D1/D2`), Dualwatch (`16 59`), all meters (`15 02/11/12/13/14/15/16`), squelch/OVF status (`15 01/05/07`, `1A 0A`), attenuator (`11`), preamp (`16 02`), tuning step (`10`), dial lock (`16 50`). Radio view becomes a live TFT-style dashboard.
- **M2 — RX DSP:** NB (`16 22`, `14 12`, per-band `1A 05 0321–0329`), NR (`16 40`, `14 06`), notch (`16 41/48/57`, `14 0D`), AGC (`16 12`, `1A 04`), twin-PBT (`14 07/08`), IF filter shape (`16 56`), RF/SQL behavior (`1A 05 0036`).
- **M3 — TX / tone / split / RIT:** RF power limits, mic gain (`14 0B`), COMP (`16 44`/`14 0E`), VOX (`16 46`/`14 16/17`), monitor (`16 45`/`14 15`), tone/TSQL/DTCS (`16 42/43/4B/5D`, `1B 00/01/02`), split & duplex (`0F`, `0C/0D`), RIT (`21 00/01`), TX delays/TOT/PTT-lock, SSB TBW (`16 58`, `1A 05 0017–0020`).
- **M4 — SET-mode tree:** full `1A 05 nnnn` lists rendered as clean accordion sections — tone-control RX/TX, beeps/speech, connectors (ACC/USB/LAN/CI-V/network), display/units, time/NTP (`1A 08/09`), REF, power (`18 00/01`), backlight (`19`). Reuse the enum/level/toggle/number renderers from M1–M3.
- **M5 — Memories + scan:** memory channel select/write/clear (`08`, `08 09/0A/0B`), full memory keeper (`1A 00`), band-stacking (`1A 01`), program/call-edge channels, all scan starts/stops/spans (`0E xx`), scan SET items (`1A 05 0249–0254`).
- **M6 — CW + RTTY:** CW speed/pitch/BK-IN (`14 0C/09/0F`, `16 47`), keyer settings (`1A 05 0218–0228`), send CW (`17`), memory keyer (`1A 02`), RTTY mark/shift/polarity (`1A 05 0047–0049`), TPF (`16 4F`), AFC (`16 4A`), RTTY decode/log/HPF-LPF settings, USB keying (`1A 05 0121/0122`).
- **M7 — DV / D-STAR / DD:** mode/RPS (`0F 13`), call signs (`1F 00/01/02`), RX call/message/status/D-PRS read & auto-output (`20 xx`), DV data (`22 xx`), DV/DD SET items (`1A 05 0074–0090`), GPS/D-PRS subtree (`23 00`, `16 5C`, `1A 05 0255–0319`).
- **M8 — Satellite:** SAT mode (`16 5A`), SAT memory keeper (`1A 07`), uplink/downlink tracking UI on top of the M1 dual-watch foundation.

---
_QA pass (2026-06-25): 62 commands spot-checked against the CI-V reference; 4 corrections applied (DSQL 16 5B, RIT ±9.999 kHz, VOX-Delay view, GPS-TX-Mode note)._
