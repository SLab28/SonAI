"""Tests for the SonAI agent loop — Claude integration and deterministic fallback."""
import asyncio
import json
import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.agent import (
    AGENT_SYSTEM_PROMPT,
    MAX_TOOL_CALLS,
    TOOL_SCHEMAS,
    _execute_tool,
    _get_anthropic_client,
    _result_summary,
    _run_deterministic_agent,
    run_agent,
)
from backend.graph import graph


# ── Fixtures ────────────────────────────────────────────────────────


@pytest.fixture(autouse=True)
def reset_graph():
    graph.reset()
    yield
    graph.reset()


@pytest.fixture
def mock_ws():
    """Return a mock WebSocket connection manager."""
    ws = MagicMock()
    ws.broadcast = AsyncMock()
    return ws


# ── Unit tests ──────────────────────────────────────────────────────


class TestToolSchemas:
    """Verify the tool schemas exposed to Claude."""

    def test_all_tools_have_schemas(self):
        schema_names = {s["name"] for s in TOOL_SCHEMAS}
        expected = {
            "load_audio", "preprocess", "stft", "hpss",
            "spectral_stats", "temporal_stats", "onsets", "pitch_tonal",
            "mfcc", "chroma", "segment_map", "insight_composer",
            "binaural_beat_gen", "texture_layer", "instrument_layer",
            "granular_cloud", "mix_render",
        }
        assert expected == schema_names

    def test_schemas_have_required_fields(self):
        for schema in TOOL_SCHEMAS:
            assert "name" in schema
            assert "description" in schema
            assert "input_schema" in schema
            assert schema["input_schema"]["type"] == "object"


class TestSystemPrompt:
    def test_system_prompt_contains_key_instructions(self):
        assert "ANALYSE" in AGENT_SYSTEM_PROMPT
        assert "COMPOSE" in AGENT_SYSTEM_PROMPT
        assert "RENDER" in AGENT_SYSTEM_PROMPT
        assert "Never generate vocals" in AGENT_SYSTEM_PROMPT

    def test_max_tool_calls_is_sensible(self):
        assert 10 <= MAX_TOOL_CALLS <= 50


class TestResultSummary:
    def test_summary_with_error(self):
        result = {"error": "something broke"}
        summary = _result_summary(result)
        assert "Error:" in summary

    def test_summary_truncates_large_strings(self):
        result = {"summary": "ok", "data": {"big": "x" * 500}}
        summary = _result_summary(result)
        parsed = json.loads(summary)
        assert "<500 chars>" in parsed["data"]["big"]

    def test_summary_truncates_large_lists(self):
        result = {"summary": "ok", "data": {"many": list(range(100))}}
        summary = _result_summary(result)
        parsed = json.loads(summary)
        assert "list of 100" in parsed["data"]["many"]


class TestGetAnthropicClient:
    def test_returns_none_without_key(self):
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": ""}, clear=False):
            assert _get_anthropic_client() is None

    def test_returns_none_with_placeholder_key(self):
        with patch.dict(
            os.environ, {"ANTHROPIC_API_KEY": "your-api-key-here"}, clear=False
        ):
            assert _get_anthropic_client() is None


class TestExecuteTool:
    @pytest.mark.asyncio
    async def test_missing_tool_returns_error(self):
        result = await _execute_tool("nonexistent_tool", {})
        assert "error" in result
        assert "not found" in result["error"]


# ── Deterministic fallback integration test ─────────────────────────


@pytest.mark.asyncio
async def test_deterministic_fallback_runs(mock_ws):
    """The deterministic pipeline should run end-to-end without an API key."""
    results = await _run_deterministic_agent(
        file_path="/tmp/fake.wav",
        objective="Analyse and generate",
        agent_ws=mock_ws,
        graph_ws=mock_ws,
        render_ws=mock_ws,
    )
    # Should have placed many nodes
    assert len(results) > 0
    # Graph should have nodes
    state = graph.get_state()
    assert len(state["nodes"]) > 0
    # broadcast should have been called multiple times
    assert mock_ws.broadcast.call_count > 5


@pytest.mark.asyncio
async def test_run_agent_falls_back_without_api_key(mock_ws):
    """run_agent should fall back to deterministic when no key is set."""
    with patch.dict(os.environ, {"ANTHROPIC_API_KEY": ""}, clear=False):
        results = await run_agent(
            file_path="/tmp/fake.wav",
            objective="test",
            agent_ws=mock_ws,
            graph_ws=mock_ws,
            render_ws=mock_ws,
        )
    assert len(results) > 0


# ── Claude integration test (mocked) ───────────────────────────────


def _make_text_block(text: str):
    block = MagicMock()
    block.type = "text"
    block.text = text
    return block


def _make_tool_use_block(tool_id: str, name: str, input_dict: dict):
    block = MagicMock()
    block.type = "tool_use"
    block.id = tool_id
    block.name = name
    block.input = input_dict
    return block


@pytest.mark.asyncio
async def test_claude_agent_loop_with_mock(mock_ws):
    """Simulate a Claude tool-use loop with mocked API responses."""
    # First response: Claude calls load_audio
    resp1 = MagicMock()
    resp1.content = [
        _make_text_block("I'll start by loading the audio."),
        _make_tool_use_block("call_1", "load_audio", {"file_path": "/tmp/test.wav"}),
    ]
    resp1.stop_reason = "tool_use"

    # Second response: Claude says it's done
    resp2 = MagicMock()
    resp2.content = [
        _make_text_block("Analysis complete."),
    ]
    resp2.stop_reason = "end_turn"

    mock_client = MagicMock()
    mock_client.messages.create = MagicMock(side_effect=[resp1, resp2])

    with patch("backend.agent._get_anthropic_client", return_value=mock_client):
        results = await run_agent(
            file_path="/tmp/test.wav",
            objective="analyse this",
            agent_ws=mock_ws,
            graph_ws=mock_ws,
            render_ws=mock_ws,
        )

    assert len(results) > 0
    # Should have called Claude twice (initial + tool result)
    assert mock_client.messages.create.call_count == 2
    # Verify Claude was called with tool schemas
    call_kwargs = mock_client.messages.create.call_args_list[0]
    assert "tools" in call_kwargs.kwargs
