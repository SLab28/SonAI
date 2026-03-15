"""Tests for the FastAPI REST endpoints."""
import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.graph import graph


@pytest.fixture(autouse=True)
def reset_graph():
    graph.reset()
    yield
    graph.reset()


client = TestClient(app)


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_place_node():
    resp = client.post("/api/graph/place", json={
        "node_type": "LoadAudio",
        "x": 100,
        "y": 200,
        "params": {"file_path": "test.wav"},
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "node_id" in data


def test_graph_state():
    client.post("/api/graph/place", json={"node_type": "LoadAudio", "x": 0, "y": 0})
    resp = client.get("/api/graph/state")
    assert resp.status_code == 200
    state = resp.json()
    assert len(state["nodes"]) == 1


def test_connect_nodes():
    r1 = client.post("/api/graph/place", json={"node_type": "LoadAudio", "x": 0, "y": 0})
    r2 = client.post("/api/graph/place", json={"node_type": "STFT", "x": 200, "y": 0})
    n1 = r1.json()["node_id"]
    n2 = r2.json()["node_id"]
    resp = client.post("/api/graph/connect", json={
        "source_id": n1, "source_port": "AudioBuffer",
        "target_id": n2, "target_port": "AudioBuffer",
    })
    assert resp.status_code == 200


def test_graph_reset():
    client.post("/api/graph/place", json={"node_type": "LoadAudio", "x": 0, "y": 0})
    resp = client.delete("/api/graph/reset")
    assert resp.status_code == 200
    state = client.get("/api/graph/state").json()
    assert len(state["nodes"]) == 0


def test_session_load():
    resp = client.post("/api/session/load", json={"file_path": "/tmp/test.wav"})
    assert resp.status_code == 200
    assert "session_id" in resp.json()
