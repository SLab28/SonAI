"""Tests for the graph state manager."""
import pytest
from backend.graph import GraphState


def test_place_node():
    g = GraphState()
    nid = g.place_node("LoadAudio", 100, 200, {"file_path": "test.wav"})
    assert nid in g.nodes
    assert g.nodes[nid]["node_type"] == "LoadAudio"
    assert g.nodes[nid]["x"] == 100
    assert g.nodes[nid]["y"] == 200


def test_connect_nodes():
    g = GraphState()
    n1 = g.place_node("LoadAudio")
    n2 = g.place_node("STFT")
    edge = g.connect_nodes(n1, "AudioBuffer", n2, "AudioBuffer")
    assert edge["source_id"] == n1
    assert edge["target_id"] == n2
    assert len(g.edges) == 1


def test_cycle_detection():
    g = GraphState()
    n1 = g.place_node("A")
    n2 = g.place_node("B")
    n3 = g.place_node("C")
    g.connect_nodes(n1, "out", n2, "in")
    g.connect_nodes(n2, "out", n3, "in")
    with pytest.raises(ValueError, match="cycle"):
        g.connect_nodes(n3, "out", n1, "in")


def test_topo_sort():
    g = GraphState()
    n1 = g.place_node("A")
    n2 = g.place_node("B")
    n3 = g.place_node("C")
    g.connect_nodes(n1, "out", n2, "in")
    g.connect_nodes(n2, "out", n3, "in")
    order = g.topo_sort()
    assert order.index(n1) < order.index(n2) < order.index(n3)


def test_get_state():
    g = GraphState()
    n1 = g.place_node("LoadAudio")
    state = g.get_state()
    assert len(state["nodes"]) == 1
    assert state["nodes"][0]["node_id"] == n1


def test_reset():
    g = GraphState()
    g.place_node("A")
    g.place_node("B")
    g.reset()
    assert len(g.nodes) == 0
    assert len(g.edges) == 0


def test_set_node_result():
    g = GraphState()
    nid = g.place_node("LoadAudio")
    g.set_node_result(nid, {"summary": "test"})
    assert g.nodes[nid]["result"]["summary"] == "test"
