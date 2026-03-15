# SonAI build brief

Build a complete first-pass SonAI application in the current workspace using the attached specification files as the source of truth.

## Core sources
- /home/user/workspace/AGENTS.md
- /home/user/workspace/TASKS.md
- /home/user/workspace/SPEC.md
- /home/user/workspace/ARCHITECTURE.md
- /home/user/workspace/node-schemas.md
- /home/user/workspace/mcp-tool-registry.md
- /home/user/workspace/sc-synth-library.md
- /home/user/workspace/flow-state-parameters.md
- /home/user/workspace/schemas.py
- /home/user/workspace/main.py
- /home/user/workspace/mcp_server.py
- /home/user/workspace/osc_client.py
- /home/user/workspace/load_audio.py
- /home/user/workspace/pyproject.toml

## Important constraints
- No vocals, speech, voice synthesis, or lyric features.
- Every tool must return NodeOutput matching node-schemas.md.
- Never call scsynth directly from tool files. Go through backend/sc/osc_client.py.
- One tool per file in backend/tools/ and backend/generation/.
- Do not access or depend on node_modules, .venv, or dist paths.
- The local .claude/skills files referenced in AGENTS.md are missing from the workspace. Proceed using the spec/docs instead.

## Desired scope
Implement Phases 0–3 from TASKS.md as a coherent MVP. Do not implement Phase 4 EEG integration.

## Deliverables to create
- Expected project structure under backend/, frontend/, docs/, and tests/.
- Backend FastAPI app with health endpoint, graph/render/agent WebSockets, graph mutation APIs, and session/tool endpoints as reasonable from ARCHITECTURE.
- FastMCP server with registered analysis and generation tools.
- Analysis tools for the documented Phase 1 nodes.
- Generation tools and SC wrappers/synthdefs for the documented Phase 2 nodes.
- Frontend Vite React app with React Flow canvas, node palette, Zustand store, WebSocket client, inline node summaries/artifact previews, and agent activity panel.
- Tests for backend tools and basic frontend behavior.
- Update TASKS.md to reflect completed work where appropriate.

## Implementation notes
- Reuse the existing root files as reference implementations, but put code in the AGENTS.md folder structure.
- If some advanced audio libraries are unavailable in the environment, implement graceful fallbacks so the app still runs and tests pass.
- Keep the app runnable with the documented commands as closely as possible.
- Prefer a thin but end-to-end working MVP over exhaustive completeness.

## Validation
- Run backend tests with uv.
- Run frontend tests with pnpm.
- Return a concise summary of what was built, what was simplified, and any known limitations.
