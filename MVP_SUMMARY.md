# SonAI MVP Build Summary

## What Was Built

A complete first-pass SonAI application implementing Phases 0–3 from the task list: project scaffolding, analysis engine, generation engine, and agent loop.

### Backend (Python / FastAPI / FastMCP)

**Core infrastructure:**
- `backend/main.py` — FastAPI app with health endpoint, CORS, REST APIs for graph mutation (`/api/graph/place`, `/api/graph/connect`, `/api/graph/state`, `/api/graph/reset`), tool execution (`/api/tools/{name}`), and session management
- `backend/mcp_instance.py` + `backend/mcp_server.py` — FastMCP tool server with all 17 tools registered (split into two files to avoid circular imports)
- `backend/schemas.py` — Full Pydantic models for AudioBuffer, STFTFrame, SpectralFeatureVector, TemporalFeatureVector, EventList, PitchTrack, MFCCMatrix, ChromaMatrix, SegmentMap, ScenePlan, SCJob, NodeOutput, NodeArtifact
- `backend/graph/__init__.py` — In-memory DAG state manager with node placement, edge connection, cycle detection, topological sort, and result storage
- `backend/tool_registry.py` — Tool name → callable registry for REST-based tool execution

**WebSocket endpoints:**
- `/ws/graph` — Bidirectional: broadcasts NodePlacedEvent, NodeConnectedEvent, NodeResultEvent; accepts place/connect commands from frontend
- `/ws/render` — Broadcasts RenderProgressEvent, RenderCompleteEvent
- `/ws/agent` — Streams agent reasoning; accepts run_agent commands

**Phase 1 — Analysis tools (12 tools, one per file in `backend/tools/`):**
- `load_audio.py` — Loads audio via librosa, returns base64 AudioBuffer + waveform PNG
- `preprocess.py` — Normalise, resample, mono, trim silence
- `stft.py` — STFT magnitude/phase + spectrogram PNG artifact
- `hpss.py` — Harmonic-percussive source separation
- `spectral_stats.py` — Centroid, rolloff, flatness, bandwidth, contrast, ZCR
- `temporal_stats.py` — RMS, loudness (LUFS approx), dynamic range
- `onsets.py` — Onset detection + beat tracking via librosa
- `pitch_tonal.py` — Pitch tracking (pYIN) + key estimation (Krumhansl-Kessler)
- `mfcc.py` — 13-coefficient MFCC + heatmap PNG
- `chroma.py` — CQT chroma features + chromagram PNG
- `segment_map.py` — Agglomerative structural segmentation
- `insight_composer.py` — Aggregates all measure outputs into a ScenePlan

**Phase 2 — Generation tools (5 tools in `backend/generation/`):**
- `binaural_beat.py` — Queues binaural beat SCJob via OSC
- `texture_layer.py` — Maps ScenePlan texture_profile → SC texture parameters
- `instrument_layer.py` — Maps instrument_role → SonaiPad/SonaiDrone SynthDef
- `granular_cloud.py` — Queues granular synthesis SCJob
- `mix_render.py` — Collects SCJobs and renders (placeholder sine mix in MVP)

**Phase 3 — Agent loop (`backend/agent.py`):**
- Deterministic orchestration loop: LoadAudio → Preprocess → analysis pipeline → InsightComposer → generation pipeline → MixRender
- Broadcasts reasoning to `/ws/agent` at each step
- Includes approval gate before generation (auto-approves in MVP)
- Full system prompt for future Claude MCP integration

**SuperCollider layer (`backend/sc/`):**
- `osc_client.py` — Graceful OSC wrapper; logs warnings if SC unavailable
- `boot.py` — Attempts SC boot with fallback logging
- `synthdefs/` — 5 SynthDef files: binaural.scd, texture.scd, granular.scd, pad.scd, drone.scd

### Frontend (React 18 + TypeScript + Vite)

- `frontend/src/App.tsx` — Main layout: ControlBar + NodePalette + ReactFlow canvas + AgentPanel
- `frontend/src/nodes/SonaiNode.tsx` — Universal node component with colour-coded headers, summary text, inline artifact previews, and input/output handles
- `frontend/src/store/graphStore.ts` — Zustand store managing nodes, edges, and agent messages; supports node colour/category mapping for all 17 node types
- `frontend/src/ws/useWebSocket.ts` — Two WebSocket hooks: `useGraphWebSocket` (graph events) and `useAgentWebSocket` (agent reasoning + commands)
- `frontend/src/components/NodePalette.tsx` — Draggable node palette organised by category (Source, Transform, Measure, Infer, Compose, Render)
- `frontend/src/components/AgentPanel.tsx` — Right sidebar showing agent reasoning stream with event-type styling
- `frontend/src/components/ControlBar.tsx` — Top bar with SonAI logo, file path input, objective input, Run Agent button

### Tests

**Backend (36 tests, all passing):**
- `backend/tests/test_tools.py` — 23 async tests covering all 12 analysis tools + 5 generation tools
- `backend/tests/test_graph.py` — 7 tests for graph state management (place, connect, cycle detection, topo sort, reset)
- `backend/tests/test_api.py` — 6 tests for REST endpoints (health, place, connect, state, reset, session)

**Frontend (6 tests, all passing):**
- `frontend/src/store/graphStore.test.ts` — Tests for node addition, result updates, agent messages, clear, colour mapping

## Simplifications & Fallbacks

1. **Essentia / Aubio not used directly** — Pitch tracking uses librosa's pYIN instead of Aubio YIN. Key estimation uses a custom Krumhansl-Kessler correlator against chroma features instead of Essentia HPCP. All tools have `HAS_LIBROSA` fallbacks that produce synthetic data if librosa is unavailable.

2. **SuperCollider not running** — The OSC client (`sc/osc_client.py`) degrades gracefully with logged warnings when SC is unreachable. Generation tools still produce valid SCJob objects. MixRender produces a placeholder sine-mix WAV instead of triggering real SC NRT render.

3. **Agent loop is deterministic** — The MVP agent (`backend/agent.py`) runs a fixed analysis → generation pipeline rather than adaptive Claude tool-calling. A system prompt is provided for future MCP-based Claude integration. The approval gate auto-approves after 0.5s.

4. **STFT data truncated** — Magnitude/phase arrays are truncated to first 20 rows and 100 columns in the NodeOutput JSON to avoid multi-MB responses.

5. **Loudness is simplified** — `temporal_stats.py` uses mean RMS-to-dB as a LUFS approximation rather than full ITU-R BS.1770 measurement.

6. **No file drop zone** — Frontend supports drag-from-palette but not audio file drag-and-drop (file path is entered in the ControlBar text input instead).

7. **Node-type-specific React components** — All node types use a single `SonaiNode` component with colour-coded headers. Individual per-node-type components (e.g., file drop zone for LoadAudio) are not implemented.

## Commands

```bash
# Backend
uv run uvicorn backend.main:app --reload --port 8000
# or: python -m uvicorn backend.main:app --reload --port 8000

# Frontend
cd frontend && pnpm dev

# Backend tests
python -m pytest backend/tests/ -v

# Frontend tests
cd frontend && pnpm test

# MCP server
uv run mcp run backend/mcp_server.py

# SC boot (if SuperCollider installed)
python -m backend.sc.boot
```

## Known Limitations

- No audio file upload endpoint (files must be accessible on the server filesystem)
- No WAV file output persistence without running SuperCollider
- The `CorpusLoader`, `FilterBank`, `SourceRoleClassifier`, and `NoiseDesigner` nodes from SPEC.md are not implemented (lower priority for MVP)
- Frontend WebSocket reconnection on disconnect is not implemented
- No dark mode
- Phase 4 (EEG Integration) is not implemented per the build brief
