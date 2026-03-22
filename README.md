# SonAI — Automated Audio Node Editor

## Website
- [SonaAI](https://slab28.github.io/SonAI)
## Demo assets
- [Demo video](https://slab28.github.io/SonAI/#demo)
- [Screenshot](https://github.com/SLab28/SonAI/blob/main/artifacts/demo/step-5-complete-graph.png)

Open source, AI-native node editor for general audio signal analysis and soundscape generation.


![alt text](artifacts/demo/demo-screen.png)

## Utility
1. Upload audio files
2. Ask (e.g. "Analyse this ambient recording and generate a calmer gamma-flow version")
3. An AI agent places analysis nodes, runs them, derives insights, and assembles a generation graph
4. SuperCollider renders the result

## Stack
- Frontend: React 18 + TypeScript + React Flow + Vite
- Backend: Python 3.12 + FastAPI + FastMCP
- Analysis: librosa
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

## Development state
- UI in beta
- Project rules and boundaries for coding agents in beta

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
