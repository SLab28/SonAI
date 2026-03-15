# docs/sc-synth-library.md — SuperCollider SynthDef Catalogue

All SynthDef files live in `backend/sc/synthdefs/`. Load them via `backend/sc/boot.py`.

---

## SonaiTexture
File: `backend/sc/synthdefs/texture.scd`
Purpose: Filtered noise drone for texture layers

Parameters:
| Param | Range | Default | Description |
|---|---|---|---|
| density | 0–1 | 0.5 | Noise density (grain rate) |
| brightness | 0–1 | 0.5 | Low-pass filter cutoff (mapped 200–8000 Hz) |
| amp | 0–1 | 0.3 | Output amplitude |
| dur | seconds | 30 | Synth duration before freeing |
| pan | -1–1 | 0 | Stereo pan position |

OSC address: `/sonai/texture`

---

## SonaiBinaural
File: `backend/sc/synthdefs/binaural.scd`
Purpose: Stereo binaural beat generator

Parameters:
| Param | Range | Default | Description |
|---|---|---|---|
| carrier_hz | 60–500 | 110 | Carrier frequency (same-ish for both ears) |
| beat_hz | 1–50 | 40 | Binaural beat interval (difference between ears) |
| amp | 0–1 | 0.2 | Output amplitude |
| dur | seconds | 60 | Duration |

Note: left ear = carrier_hz, right ear = carrier_hz + beat_hz. Requires headphones.
OSC address: `/sonai/binaural`

---

## SonaiGranular
File: `backend/sc/synthdefs/granular.scd`
Purpose: Granular synthesis cloud from a loaded buffer

Parameters:
| Param | Range | Default | Description |
|---|---|---|---|
| bufNum | int | — | SC buffer number (loaded source audio) |
| density | 0–1 | 0.5 | Grain density (grains/sec mapped 2–80) |
| pitch_var | 0–1 | 0.1 | Pitch scatter (semitones * 12 * pitch_var) |
| dur | seconds | 30 | Duration |
| amp | 0–1 | 0.4 | Output amplitude |

OSC address: `/sonai/granular`

---

## SonaiPad
File: `backend/sc/synthdefs/pad.scd`
Purpose: Soft pad instrument, sustained and slowly evolving

Parameters:
| Param | Range | Default | Description |
|---|---|---|---|
| freq_hz | 20–2000 | 220 | Fundamental frequency |
| detune | 0–0.1 | 0.02 | Oscillator detuning ratio |
| cutoff | 200–8000 | 1200 | Low-pass filter cutoff Hz |
| amp | 0–1 | 0.3 | Output amplitude |
| dur | seconds | 30 | Duration |
| attack | seconds | 3.0 | Envelope attack |
| release | seconds | 5.0 | Envelope release |

OSC address: `/sonai/pad`

---

## SonaiDrone
File: `backend/sc/synthdefs/drone.scd`
Purpose: Sub-bass or fundamental drone, very long sustain

Parameters:
| Param | Range | Default | Description |
|---|---|---|---|
| freq_hz | 20–300 | 55 | Drone fundamental |
| harmonics | 1–8 | 3 | Number of harmonics added |
| amp | 0–1 | 0.4 | Output amplitude |
| dur | seconds | 120 | Duration |

OSC address: `/sonai/drone`

---

## Adding a New SynthDef
1. Write the .scd file in `backend/sc/synthdefs/`
2. Add it to the load block in `backend/sc/boot.py`
3. Add an entry to this file
4. Add the OSC address to ARCHITECTURE.md OSC table
5. Write the Python tool in `backend/generation/`
