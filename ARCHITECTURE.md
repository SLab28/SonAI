# ARCHITECTURE.md — SonAI System Architecture

## System Overview

```
┌─────────────────────────────────────────────────┐
│                  BROWSER                         │
│  ┌──────────────┐   ┌──────────────────────────┐│
│  │  React Flow  │   │  Agent Activity Panel    ││
│  │  Node Canvas │   │  (reasoning stream)      ││
│  └──────┬───────┘   └──────────────────────────┘│
│         │ WebSocket /ws/graph                    │
└─────────┼───────────────────────────────────────┘
          │
┌─────────▼───────────────────────────────────────┐
│              FastAPI Backend (:8000)             │
│  ┌─────────────┐  ┌──────────────────────────┐  │
│  │  /ws/graph  │  │  /ws/render              │  │
│  │  /ws/agent  │  │  POST /api/graph/place   │  │
│  └─────────────┘  └──────────────────────────┘  │
│                                                  │
│  ┌─────────────────────────────────────────────┐ │
│  │           FastMCP Tool Server               │ │
│  │  Tools: load_audio | stft | spectral_stats  │ │
│  │         onsets | pitch_tonal | hpss | mfcc  │ │
│  │         chroma | segment_map | insight      │ │
│  │         binaural_beat | texture | granular  │ │
│  │         instrument | mix_render             │ │
│  └───────────────────┬─────────────────────────┘ │
└────────────────────── ┼ ──────────────────────────┘
                        │
          ┌─────────────▼──────────┐
          │   AI Agent (Claude)    │
          │   tool-calling loop    │
          │   graph mutation API   │
          └─────────────┬──────────┘
                        │ OSC UDP
          ┌─────────────▼──────────┐
          │   SuperCollider        │
          │   scsynth :57110       │
          │   sclang  :57120       │
          │   SynthDefs catalogue  │
          └────────────────────────┘
```

---

## WebSocket Message Contracts

### /ws/graph — Node Placement Events

**NodePlacedEvent** (server → client)
```json
{
  "event": "node_placed",
  "node_id": "uuid",
  "node_type": "STFT",
  "x": 400,
  "y": 200,
  "params": { "n_fft": 2048, "hop_length": 512 },
  "reasoning": "Placed STFT to decompose frequency content over time"
}
```

**NodeConnectedEvent** (server → client)
```json
{
  "event": "node_connected",
  "source_id": "uuid",
  "source_port": "AudioBuffer",
  "target_id": "uuid",
  "target_port": "AudioBuffer"
}
```

**NodeResultEvent** (server → client)
```json
{
  "event": "node_result",
  "node_id": "uuid",
  "summary": "Spectral centroid mean: 2340 Hz, flatness: 0.12 — bright, moderately harmonic",
  "artifact_type": "image/png",
  "artifact_b64": "..."
}
```

### /ws/render — Render Events

**RenderProgressEvent**
```json
{ "event": "render_progress", "pct": 45, "message": "Generating binaural layer..." }
```

**RenderCompleteEvent**
```json
{ "event": "render_complete", "file_path": "output/session_001.wav", "duration_s": 120.0 }
```

---

## API Endpoints

### Graph Mutation
- `POST /api/graph/place` — body: `{ node_type, x, y, params }` → returns `node_id`
- `POST /api/graph/connect` — body: `{ source_id, source_port, target_id, target_port }`
- `GET  /api/graph/state` — returns full current graph JSON
- `DELETE /api/graph/reset` — clears canvas

### Tool Execution (called by agent via MCP, also directly callable)
- `POST /api/tools/{tool_name}` — body: tool-specific params → returns NodeOutput

### Session
- `POST /api/session/load` — load audio file, returns session_id
- `GET  /api/session/{id}/files` — list loaded files

---

## OSC Message Contracts (Python → SuperCollider)

| Address | Args | Description |
|---|---|---|
| /sonai/synth/play | defName, ...params | Instantiate a SynthDef |
| /sonai/synth/set | nodeId, param, value | Update running synth param |
| /sonai/synth/free | nodeId | Release synth |
| /sonai/binaural | carrier_hz, beat_hz, dur | Play binaural beat layer |
| /sonai/texture | density, brightness, dur | Trigger texture SynthDef |
| /sonai/granular | bufNum, density, pitchVar, dur | Trigger granular cloud |
| /sonai/render/start | outPath, dur | Begin non-realtime render |
| /sonai/render/done | — | SC confirms render complete |

---

## Node Execution Order
The graph is a DAG. Execution order is determined by topological sort.
The backend graph module maintains adjacency list and resolves execution order
before dispatching tool calls. Circular connections are rejected at connect time.

---

## Flow-State Audio Parameters Reference
| Target State | EEG Band | Binaural Beat | Carrier | Texture Style |
|---|---|---|---|---|
| Deep focus / flow | Gamma (35-45Hz) | 40 Hz | 110 Hz | Sparse, stable, dark |
| Alert focus | Beta (15-25Hz) | 20 Hz | 200 Hz | Medium, evolving, neutral |
| Creative/relaxed | Alpha (9-12Hz) | 10 Hz | 300 Hz | Dense, warm, slow |
| Meditation | Theta (4-8Hz) | 6 Hz | 100 Hz | Very sparse, airy |

Source: Gamma entrainment research; carrier frequency choices from production practice.
