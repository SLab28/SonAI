# SPEC.md — SonAI Product Specification

## Product Vision
SonAI is an AI-native node editor for audio signal analysis and flow-state soundscape generation.
The user drops audio files onto a canvas, states an objective in natural language, and an AI agent
places analysis nodes, runs them, derives insights, then assembles a generation graph producing
non-vocal instrumental and textural output (synths, modified noise, environmental sounds, instruments).

## Non-Goals
- No vocals, voice, or lyrics at any point in the pipeline
- Not a DAW — no timeline, no MIDI piano roll in v1
- Not a music recommendation or streaming tool

---

## Phase 1 — Analysis Engine (MVP)

### 1.1 Source Nodes
| Node | Tool file | Input | Output |
|---|---|---|---|
| LoadAudio | load_audio.py | file_path: str, sr: int=22050 | AudioBuffer |
| CorpusLoader | corpus_loader.py | folder_path: str | AudioBuffer[] |

### 1.2 Transform Nodes
| Node | Tool file | Input | Output |
|---|---|---|---|
| Preprocess | preprocess.py | AudioBuffer | AudioBuffer (normalised, mono, resampled) |
| STFT | stft.py | AudioBuffer, n_fft, hop_length | STFTFrame |
| FilterBank | filterbank.py | AudioBuffer, bands: int | FilterBankOutput |
| HPSS | hpss.py | AudioBuffer | HarmonicPercussiveSplit |

### 1.3 Measure Nodes
| Node | Tool file | Input | Output |
|---|---|---|---|
| SpectralStats | spectral_stats.py | STFTFrame | SpectralFeatureVector |
| TemporalStats | temporal_stats.py | AudioBuffer | TemporalFeatureVector |
| Onsets | onsets.py | AudioBuffer | EventList |
| PitchTonal | pitch_tonal.py | AudioBuffer | PitchTrack + HPCP |
| MFCC | mfcc.py | AudioBuffer, n_mfcc: int=13 | MFCCMatrix |
| Chroma | chroma.py | STFTFrame | ChromaMatrix |

### 1.4 Infer Nodes
| Node | Tool file | Input | Output |
|---|---|---|---|
| SegmentMap | segment_map.py | SpectralFeatureVector + EventList | SegmentMap |
| SourceRoleClassifier | source_role.py | SegmentMap + SpectralFeatureVector | SourceRoleMap |
| InsightComposer | insight_composer.py | all Measure outputs | ScenePlan |

---

## Phase 2 — Generation Engine (MVP)

### 2.1 Compose Nodes
| Node | Tool file | Input | Output |
|---|---|---|---|
| BinauralBeatGen | binaural_beat.py | carrier_hz, beat_hz, duration_s | AudioBuffer |
| TextureLayer | texture_layer.py | ScenePlan.texture_profile | SCJob |
| InstrumentLayer | instrument_layer.py | ScenePlan.pitched_profile | SCJob |
| GranularCloud | granular_cloud.py | AudioBuffer (source), density, pitch_var | SCJob |
| NoiseDesigner | noise_designer.py | color: str, filter_params | SCJob |

### 2.2 Render Node
| Node | Tool file | Input | Output |
|---|---|---|---|
| MixRender | mix_render.py | SCJob[] | AudioFile path + waveform artifact |

---

## Phase 3 — Agent Loop

### 3.1 Agent Capabilities
The agent receives:
- Audio file path(s)
- Objective string (natural language)
- Node registry (from docs/mcp-tool-registry.md)

The agent may call:
- Any tool in backend/tools/ or backend/generation/
- graph.place_node(type, x, y, params) — places a node on the canvas
- graph.connect_nodes(source_id, port, target_id, port) — wires two nodes
- graph.get_state() — reads current graph

### 3.2 Agent Constraints
- Agent must place nodes one at a time and await the result before placing dependent nodes
- Agent must not place generation nodes until InsightComposer has returned a ScenePlan
- Agent should explain its reasoning in a `reasoning` field returned with each graph action

---

## Phase 4 — EEG Integration (Future)
- ControlSource node accepts EEG state signals (valence/arousal/dominance)
- Flow console bridges to Phase 1 EEG analysis project
- Generation nodes accept real-time control envelopes from EEG stream

---

## Data Contracts

### AudioBuffer
```json
{
  "samples": "[float32 array — base64 encoded]",
  "sr": 22050,
  "channels": 1,
  "duration_s": 12.3,
  "file_path": "string"
}
```

### SpectralFeatureVector
```json
{
  "centroid_mean": 0.0,
  "centroid_std": 0.0,
  "rolloff_mean": 0.0,
  "flatness_mean": 0.0,
  "bandwidth_mean": 0.0,
  "contrast_mean": "[7 floats]",
  "zcr_mean": 0.0,
  "frame_times": "[float array]"
}
```

### EventList
```json
{
  "onsets_s": "[float array]",
  "onset_strength": "[float array]",
  "bpm": 0.0,
  "beat_times_s": "[float array]",
  "transient_density": 0.0
}
```

### PitchTrack
```json
{
  "times_s": "[float array]",
  "frequencies_hz": "[float array]",
  "confidence": "[float array]",
  "dominant_pitch_hz": 0.0,
  "hpcp": "[12 floats — harmonic pitch class profile]",
  "key": "C",
  "scale": "major"
}
```

### ScenePlan
```json
{
  "texture_profile": {
    "density": "sparse|medium|dense",
    "brightness": "dark|neutral|bright",
    "noisiness": 0.0,
    "stability": "stable|evolving|turbulent",
    "space": "intimate|room|expansive"
  },
  "pitched_profile": {
    "dominant_pitch_hz": 0.0,
    "key": "C",
    "harmonic_complexity": "simple|modal|complex",
    "instrument_role": "drone|melodic|percussive|pad"
  },
  "rhythm_profile": {
    "bpm": 0.0,
    "regularity": "arrhythmic|loose|strict",
    "onset_density": 0.0
  },
  "flow_targets": {
    "binaural_beat_hz": 40.0,
    "carrier_hz": 110.0,
    "target_band": "gamma"
  },
  "semantic_label": "sparse airy drone with distant metallic transients"
}
```

### NodeOutput (universal wrapper — all nodes must return this)
```json
{
  "node_id": "string",
  "node_type": "string",
  "data": { "...type-specific payload..." },
  "artifact": {
    "type": "image|audio|midi|none",
    "content": "base64 or null",
    "mime_type": "image/png"
  },
  "summary": "one sentence semantic description of what this node found"
}
```

---

## UI Rules
- Canvas: white background, black node headers, Inter font, minimal chrome
- Node body: shows summary string + small artifact preview inline
- Agent activity panel: right sidebar, shows agent reasoning stream
- No modal dialogs for standard operations — all inline
- Colour coding: Source = grey, Transform = blue, Measure = green, Infer = amber, Compose = purple, Render = red
