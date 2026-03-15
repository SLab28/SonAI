# SonAI — Audio Intelligence Node Editor

## Demo assets
- [Demo video](https://github.com/SLab28/SonAI/blob/main/artifacts/demo/sonai-frequency-analysis-recording.mp4)
- [Screenshot](https://github.com/SLab28/SonAI/blob/main/artifacts/demo/step-5-complete-graph.png)

AI-native node editor for general audio signal analysis and non-vocal, flow-state soundscape generation.

## What it does
1. Drop audio files onto the canvas
2. State an objective (e.g. "Analyse this ambient recording and generate a calmer gamma-flow version")
3. An AI agent places analysis nodes, runs them, derives insights, and assembles a generation graph
4. SuperCollider renders the result as a non-vocal soundscape

## Stack
- Frontend: React 18 + TypeScript + React Flow + Vite
- Backend: Python 3.12 + FastAPI + FastMCP
- Analysis: librosa + Essentia + Aubio
- Synthesis: SuperCollider 3 via python-osc

## Quick Start
```bash
# Install Python deps
uv sync

# Install frontend deps
pnpm install

# Start SuperCollider server (must be running first)
python -m backend.sc.boot

# Start backend
uv run uvicorn backend.main:app --reload --port 8000

# Start MCP server
uv run mcp run backend/mcp_server.py

# Start frontend
pnpm dev
```

## Read First
- AGENTS.md — project rules and boundaries for coding agents
- SPEC.md — product specification and data contracts
- TASKS.md — phase-gated task list (start here)
- ARCHITECTURE.md — system diagrams and API contracts

## Docs
- docs/node-schemas.md — all typed schemas
- docs/mcp-tool-registry.md — all MCP tools
- docs/sc-synth-library.md — SuperCollider SynthDef catalogue
- docs/flow-state-parameters.md — neuroscience parameters

## Skills (for coding agents)
- .claude/skills/audio-analysis-node.md
- .claude/skills/generation-pipeline.md
- .claude/skills/mcp-tool-creation.md
- .claude/skills/supercollider-osc.md
- .claude/skills/react-flow-node.md
