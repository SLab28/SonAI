"""SonAI FastAPI Backend — main application."""
from __future__ import annotations
import asyncio
import json
from typing import Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.graph import graph
from backend.schemas import NodeOutput

# Import tool modules at startup so the shared TOOL_REGISTRY is populated
# for REST execution and the agent loop.
import backend.mcp_server  # noqa: F401

app = FastAPI(title="SonAI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Connection managers ──────────────────────────────────────────────

class ConnectionManager:
    def __init__(self):
        self.active: list[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active.append(ws)

    def disconnect(self, ws: WebSocket):
        self.active.remove(ws)

    async def broadcast(self, data: dict):
        for ws in self.active:
            try:
                await ws.send_json(data)
            except Exception:
                pass


graph_manager = ConnectionManager()
render_manager = ConnectionManager()
agent_manager = ConnectionManager()


# ── REST endpoints ───────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "ok"}


class PlaceNodeRequest(BaseModel):
    node_type: str
    x: float = 0
    y: float = 0
    params: dict[str, Any] = {}
    reasoning: str = ""


class ConnectNodesRequest(BaseModel):
    source_id: str
    source_port: str
    target_id: str
    target_port: str


@app.post("/api/graph/place")
async def place_node(req: PlaceNodeRequest):
    node_id = graph.place_node(req.node_type, req.x, req.y, req.params)
    event = {
        "event": "node_placed",
        "node_id": node_id,
        "node_type": req.node_type,
        "x": req.x,
        "y": req.y,
        "params": req.params,
        "reasoning": req.reasoning,
    }
    await graph_manager.broadcast(event)
    return {"node_id": node_id}


@app.post("/api/graph/connect")
async def connect_nodes(req: ConnectNodesRequest):
    edge = graph.connect_nodes(
        req.source_id, req.source_port, req.target_id, req.target_port
    )
    event = {"event": "node_connected", **edge}
    await graph_manager.broadcast(event)
    return edge


@app.get("/api/graph/state")
async def graph_state():
    return graph.get_state()


@app.delete("/api/graph/reset")
async def graph_reset():
    graph.reset()
    return {"status": "cleared"}


@app.post("/api/tools/{tool_name}")
async def execute_tool(tool_name: str, params: dict[str, Any] | None = None):
    """Execute a tool by name. Delegates to the tool registry."""
    from backend.tool_registry import TOOL_REGISTRY
    if tool_name not in TOOL_REGISTRY:
        return {"error": f"Unknown tool: {tool_name}"}
    try:
        result = await TOOL_REGISTRY[tool_name](**(params or {}))
        return result.model_dump() if isinstance(result, NodeOutput) else result
    except Exception as e:
        return {"error": str(e)}


class SessionLoadRequest(BaseModel):
    file_path: str


_sessions: dict[str, dict] = {}
_session_counter = 0


@app.post("/api/session/load")
async def session_load(req: SessionLoadRequest):
    global _session_counter
    _session_counter += 1
    sid = f"session_{_session_counter:03d}"
    _sessions[sid] = {"files": [req.file_path]}
    return {"session_id": sid}


@app.get("/api/session/{session_id}/files")
async def session_files(session_id: str):
    s = _sessions.get(session_id)
    if not s:
        return {"error": "Session not found"}
    return {"files": s["files"]}


# ── WebSocket endpoints ──────────────────────────────────────────────

@app.websocket("/ws/graph")
async def graph_ws(ws: WebSocket):
    await graph_manager.connect(ws)
    try:
        while True:
            data = await ws.receive_text()
            msg = json.loads(data)
            # Client can send place / connect commands
            if msg.get("action") == "place":
                node_id = graph.place_node(
                    msg["node_type"], msg.get("x", 0), msg.get("y", 0), msg.get("params", {})
                )
                await graph_manager.broadcast({
                    "event": "node_placed",
                    "node_id": node_id,
                    "node_type": msg["node_type"],
                    "x": msg.get("x", 0),
                    "y": msg.get("y", 0),
                    "params": msg.get("params", {}),
                })
            elif msg.get("action") == "connect":
                edge = graph.connect_nodes(
                    msg["source_id"], msg["source_port"],
                    msg["target_id"], msg["target_port"]
                )
                await graph_manager.broadcast({"event": "node_connected", **edge})
    except WebSocketDisconnect:
        graph_manager.disconnect(ws)


@app.websocket("/ws/render")
async def render_ws(ws: WebSocket):
    await render_manager.connect(ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        render_manager.disconnect(ws)


@app.websocket("/ws/agent")
async def agent_ws(ws: WebSocket):
    await agent_manager.connect(ws)
    try:
        while True:
            data = await ws.receive_text()
            msg = json.loads(data)
            # Agent commands come through here
            if msg.get("action") == "run_agent":
                from backend.agent import run_agent
                asyncio.create_task(
                    run_agent(
                        file_path=msg.get("file_path", ""),
                        objective=msg.get("objective", ""),
                        agent_ws=agent_manager,
                        graph_ws=graph_manager,
                        render_ws=render_manager,
                    )
                )
    except WebSocketDisconnect:
        agent_manager.disconnect(ws)
