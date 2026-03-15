# AGENTS.md — SonAI Audio Intelligence Node Editor

## Project Identity
SonAI is an AI-native node editor for audio signal analysis and non-vocal soundscape generation.
It combines a React Flow canvas (frontend), a FastAPI/FastMCP backend (analysis tools), and
SuperCollider (synthesis engine) to let an AI agent analyse audio files, derive insights,
and assemble a generation graph that produces flow-state music.

## Stack
| Layer | Technology |
|---|---|
| Frontend | React 18 + TypeScript, Vite, React Flow, Zustand, Tailwind CSS |
| Backend | Python 3.12, FastAPI, Uvicorn, FastMCP |
| Analysis | librosa, Essentia, Aubio |
| Synthesis | SuperCollider 3 (scsynth port 57110, sclang port 57120) via python-osc |
| Agent | Claude (tool-calling via MCP) |
| Package manager | uv (Python), pnpm (JS) |

## Commands
- `pnpm dev` — start Vite frontend on :5173
- `uv run uvicorn backend.main:app --reload --port 8000` — start FastAPI backend
- `uv run mcp run backend/mcp_server.py` — start MCP tool server
- `pnpm test` — run Vitest frontend tests
- `uv run pytest backend/tests/` — run Python backend tests
- `python -m backend.sc.boot` — boot SuperCollider server

## Project Structure
```
sonai/
├── AGENTS.md              ← this file (read first)
├── SPEC.md                ← product spec and data contracts
├── TASKS.md               ← phase-gated task list (update as you complete)
├── ARCHITECTURE.md        ← system diagrams and API contracts
├── .claude/
│   └── skills/            ← agent skill files (load before working on that domain)
│       ├── react-flow-node.md
│       ├── audio-analysis-node.md
│       ├── mcp-tool-creation.md
│       ├── supercollider-osc.md
│       └── generation-pipeline.md
├── docs/
│   ├── node-schemas.md    ← typed JSON schemas for all nodes
│   ├── mcp-tool-registry.md ← all registered MCP tools with signatures
│   ├── sc-synth-library.md  ← SuperCollider SynthDef catalogue
│   └── flow-state-parameters.md ← neuroscience parameters for flow generation
├── backend/
│   ├── main.py            ← FastAPI app, WebSocket endpoints
│   ├── mcp_server.py      ← FastMCP server (tool registration)
│   ├── graph/             ← graph state management (place_node, connect_nodes)
│   ├── tools/             ← one file per analysis tool (mirrors node palette)
│   │   ├── load_audio.py
│   │   ├── stft.py
│   │   ├── spectral_stats.py
│   │   ├── temporal_stats.py
│   │   ├── onsets.py
│   │   ├── pitch_tonal.py
│   │   ├── hpss.py
│   │   ├── mfcc.py
│   │   ├── segment_map.py
│   │   └── insight_composer.py
│   ├── generation/
│   │   ├── binaural_beat.py
│   │   ├── texture_layer.py
│   │   ├── instrument_layer.py
│   │   ├── granular_cloud.py
│   │   └── mix_render.py
│   └── sc/
│       ├── osc_client.py  ← python-osc wrapper
│       ├── boot.py        ← SC server boot
│       └── synthdefs/     ← .scd SynthDef files
├── frontend/
│   └── src/
│       ├── nodes/         ← one React component per node type
│       ├── store/         ← Zustand graph store
│       ├── ws/            ← WebSocket client
│       └── App.tsx
└── tests/
    ├── backend/
    └── frontend/
```

## Boundaries
✅ Always:
- Run `uv run pytest` before marking any backend task complete
- Run `pnpm test` before marking any frontend task complete
- Keep one tool per file in `backend/tools/` and `backend/generation/`
- All node output must conform to the 3-part schema in `docs/node-schemas.md`
- Load the relevant skill file before working on a new domain

⚠️ Ask first:
- Adding a new Python dependency (update pyproject.toml, explain why)
- Adding a new npm dependency
- Changing a node output schema (downstream nodes depend on it)
- Modifying any SuperCollider SynthDef (audio output will change)
- Changing WebSocket message format

🚫 Never:
- Hardcode file paths — use config or env vars
- Commit audio files or large model weights
- Skip the 3-part node output schema
- Implement vocals or lyric-based features
- Call scsynth directly — always go through `sc/osc_client.py`
- Access `node_modules/`, `.venv/`, or `dist/` directories

## Working Style
- Prefer thin vertical slices: one node end-to-end before moving to the next
- When implementing a tool, write the schema first (docs/node-schemas.md), then the tool, then the test
- The SPEC.md is the source of truth for requirements; TASKS.md is the execution plan
- Load only the relevant section of SPEC.md for each task — do not load the entire file
