# TASKS.md — SonAI Phase-Gated Task List

> Rule: Do not start a phase until all tasks in the previous phase are marked ✅.
> Update this file as you complete tasks. One task = one thin vertical slice.

---

## Phase 0 — Project Scaffolding

- [x] P0-01: Initialise Python project with uv, pyproject.toml, FastAPI, FastMCP, librosa, essentia, aubio, python-osc
- [x] P0-02: Initialise frontend with Vite + React 18 + TypeScript + React Flow + Zustand + Tailwind
- [x] P0-03: Create folder structure as defined in AGENTS.md
- [x] P0-04: Create FastAPI app (main.py) with health endpoint and CORS for :5173
- [x] P0-05: Create WebSocket endpoint /ws/graph (broadcasts NodePlacedEvent, NodeConnectedEvent)
- [x] P0-06: Create WebSocket endpoint /ws/render (broadcasts RenderProgressEvent, RenderCompleteEvent)
- [x] P0-07: Create React Flow canvas with empty node palette and Zustand store
- [x] P0-08: Connect frontend WebSocket client to /ws/graph — nodes placed by backend appear on canvas
- [x] P0-09: Create FastMCP server skeleton (mcp_server.py) with one stub tool: ping()
- [x] P0-10: Create SC boot script and verify scsynth starts on port 57110
- [x] P0-11: Create osc_client.py wrapper with send_message() and verify Python→SC round-trip

---

## Phase 1 — Analysis Engine

> Load skill: `.claude/skills/audio-analysis-node.md` before starting this phase.

### Source
- [x] P1-01: Implement LoadAudio node (load_audio.py) — returns AudioBuffer, registers as MCP tool
- [x] P1-02: Add LoadAudio React node component (grey header, file drop zone, summary display)
- [x] P1-03: Implement Preprocess node — mono, resample, normalise, trim silence

### Transform
- [x] P1-04: Implement STFT node (librosa.stft) — returns STFTFrame + spectrogram artifact PNG
- [x] P1-05: Add STFT React node component — shows inline spectrogram thumbnail
- [x] P1-06: Implement HPSS node (librosa.effects.hpss) — returns HarmonicPercussiveSplit

### Measure
- [x] P1-07: Implement SpectralStats node (centroid, rolloff, flatness, bandwidth, contrast, ZCR)
- [x] P1-08: Implement TemporalStats node (RMS envelope, loudness, dynamic range)
- [x] P1-09: Implement Onsets node (aubio onset detection + beat tracking) — returns EventList
- [x] P1-10: Implement PitchTonal node (aubio pitch + Essentia HPCP + key estimation)
- [x] P1-11: Implement MFCC node (librosa, 13 coefficients) — returns MFCCMatrix + heatmap artifact
- [x] P1-12: Implement Chroma node (librosa CQT chroma) — returns ChromaMatrix + plot artifact

### Infer
- [x] P1-13: Implement SegmentMap node (librosa structural segmentation) — returns SegmentMap
- [x] P1-14: Implement InsightComposer node — aggregates all Measure outputs into ScenePlan JSON
- [x] P1-15: Write pytest tests for all Phase 1 tools with a fixture audio file

### Agent integration
- [x] P1-16: Register all Phase 1 tools in mcp_server.py
- [x] P1-17: Write graph.place_node() and graph.connect_nodes() API endpoints
- [x] P1-18: Test manual agent prompt: "Analyse this file and tell me its spectral character"

---

## Phase 2 — Generation Engine

> Load skill: `.claude/skills/generation-pipeline.md` and `.claude/skills/supercollider-osc.md`

- [x] P2-01: Write BinauralBeatGen SynthDef in SC — carrier_hz, beat_hz, duration params
- [x] P2-02: Implement binaural_beat.py tool — calls SC via OSC, returns AudioBuffer + waveform artifact
- [x] P2-03: Write TextureLayer SynthDef (drone + filtered noise) and implement texture_layer.py
- [x] P2-04: Write InstrumentLayer SynthDef (sample playback + pad) and implement instrument_layer.py
- [x] P2-05: Write GranularCloud SynthDef and implement granular_cloud.py
- [x] P2-06: Implement MixRender node — receives SCJob[], triggers SC mix, saves audio file
- [x] P2-07: Add generation React node components (purple header, SCJob preview)
- [x] P2-08: Register all Phase 2 tools in mcp_server.py
- [x] P2-09: End-to-end test: ScenePlan → TextureLayer + BinauralBeatGen → MixRender → audio file

---

## Phase 3 — Agent Loop

> Load skill: `.claude/skills/mcp-tool-creation.md`

- [x] P3-01: Write agent system prompt (grounded in node registry from docs/mcp-tool-registry.md)
- [x] P3-02: Implement agent orchestration loop in backend/agent.py
- [x] P3-03: Agent places Phase 1 nodes on canvas given a file path + objective
- [x] P3-04: Agent reads ScenePlan and proposes Phase 2 generation graph
- [x] P3-05: User approval gate before render executes
- [x] P3-06: Stream agent reasoning to frontend /ws/agent panel
- [x] P3-07: End-to-end demo: drop file → state objective → watch agent build graph → play result

---

## Phase 4 — EEG Integration (Future)

- [ ] P4-01: ControlSource node accepts EEG VAD (valence/arousal/dominance) JSON stream
- [ ] P4-02: Flow console bridges to existing EEG analysis project
- [ ] P4-03: Generation nodes accept real-time ControlEnvelope from EEG stream
