"""SonAI Agent Loop — Claude tool-use integration with deterministic fallback.

Uses the Anthropic API to drive a real tool-calling loop: Claude picks which
analysis/generation tools to run, receives results, and decides the next step.
When ANTHROPIC_API_KEY is unset or the API is unreachable, the agent falls back
to the original deterministic pipeline so the app still works offline.
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
from typing import Any

from backend.graph import graph
from backend.tool_registry import TOOL_REGISTRY

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# System prompt for Claude
# ---------------------------------------------------------------------------
AGENT_SYSTEM_PROMPT = """\
You are SonAI, an AI audio analysis and flow-state soundscape generation agent.

You operate on a node-based canvas. Your workflow:
1. ANALYSE: Load audio → Preprocess → run STFT, SpectralStats, TemporalStats, \
Onsets, PitchTonal, MFCC, Chroma → SegmentMap → InsightComposer
2. COMPOSE: Read the ScenePlan from InsightComposer, then place generation \
nodes (BinauralBeatGen, TextureLayer, InstrumentLayer, GranularCloud)
3. RENDER: Place a MixRender node that collects all SCJobs and produces the \
final audio file

Rules:
- Place nodes one at a time and wait for results before placing dependent nodes
- Never place generation nodes until InsightComposer returns a ScenePlan
- Never generate vocals, speech, or lyric-based content
- Explain your reasoning for each node placement
- Use the ScenePlan's flow_targets to configure binaural beats
- Keep the output non-rhythmic and flow-state oriented unless the analysis \
suggests otherwise
"""

# ---------------------------------------------------------------------------
# Tool schema for Claude (mirrors TOOL_REGISTRY names and parameters)
# ---------------------------------------------------------------------------

TOOL_SCHEMAS: list[dict[str, Any]] = [
    {
        "name": "load_audio",
        "description": "Load an audio file from disk. Returns AudioBuffer.",
        "input_schema": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "Path to audio file"},
                "sr": {"type": "integer", "description": "Sample rate", "default": 22050},
            },
            "required": ["file_path"],
        },
    },
    {
        "name": "preprocess",
        "description": "Normalise, convert to mono, and trim silence from audio.",
        "input_schema": {
            "type": "object",
            "properties": {
                "audio": {"type": "object", "description": "AudioBuffer dict"},
            },
            "required": ["audio"],
        },
    },
    {
        "name": "stft",
        "description": "Compute Short-Time Fourier Transform of audio.",
        "input_schema": {
            "type": "object",
            "properties": {
                "audio": {"type": "object", "description": "AudioBuffer dict"},
            },
            "required": ["audio"],
        },
    },
    {
        "name": "hpss",
        "description": "Harmonic-Percussive Source Separation.",
        "input_schema": {
            "type": "object",
            "properties": {
                "audio": {"type": "object", "description": "AudioBuffer dict"},
            },
            "required": ["audio"],
        },
    },
    {
        "name": "spectral_stats",
        "description": "Compute spectral features: centroid, flatness, bandwidth, ZCR.",
        "input_schema": {
            "type": "object",
            "properties": {
                "audio": {"type": "object", "description": "AudioBuffer dict"},
            },
            "required": ["audio"],
        },
    },
    {
        "name": "temporal_stats",
        "description": "Compute temporal features: RMS, loudness, dynamic range.",
        "input_schema": {
            "type": "object",
            "properties": {
                "audio": {"type": "object", "description": "AudioBuffer dict"},
            },
            "required": ["audio"],
        },
    },
    {
        "name": "onsets",
        "description": "Detect onsets and beat structure.",
        "input_schema": {
            "type": "object",
            "properties": {
                "audio": {"type": "object", "description": "AudioBuffer dict"},
            },
            "required": ["audio"],
        },
    },
    {
        "name": "pitch_tonal",
        "description": "Track pitch and estimate musical key.",
        "input_schema": {
            "type": "object",
            "properties": {
                "audio": {"type": "object", "description": "AudioBuffer dict"},
            },
            "required": ["audio"],
        },
    },
    {
        "name": "mfcc",
        "description": "Compute Mel-frequency cepstral coefficients.",
        "input_schema": {
            "type": "object",
            "properties": {
                "audio": {"type": "object", "description": "AudioBuffer dict"},
            },
            "required": ["audio"],
        },
    },
    {
        "name": "chroma",
        "description": "Compute chroma features (pitch class profile).",
        "input_schema": {
            "type": "object",
            "properties": {
                "audio": {"type": "object", "description": "AudioBuffer dict"},
            },
            "required": ["audio"],
        },
    },
    {
        "name": "segment_map",
        "description": "Segment audio structure into sections.",
        "input_schema": {
            "type": "object",
            "properties": {
                "spectral": {"type": "object", "description": "SpectralFeatureVector dict"},
                "audio": {"type": "object", "description": "AudioBuffer dict"},
            },
            "required": ["spectral", "audio"],
        },
    },
    {
        "name": "insight_composer",
        "description": "Compose a ScenePlan from all analysis results.",
        "input_schema": {
            "type": "object",
            "properties": {
                "spectral": {"type": "object"},
                "temporal": {"type": "object"},
                "events": {"type": "object"},
                "pitch": {"type": "object"},
                "segments": {"type": "object"},
            },
            "required": ["spectral", "temporal", "events", "pitch", "segments"],
        },
    },
    {
        "name": "binaural_beat_gen",
        "description": "Generate binaural beat layer for flow-state entrainment.",
        "input_schema": {
            "type": "object",
            "properties": {
                "carrier_hz": {"type": "number", "default": 110.0},
                "beat_hz": {"type": "number", "default": 40.0},
                "duration_s": {"type": "number", "default": 30.0},
            },
            "required": [],
        },
    },
    {
        "name": "texture_layer",
        "description": "Generate texture layer from ScenePlan texture profile.",
        "input_schema": {
            "type": "object",
            "properties": {
                "scene": {"type": "object", "description": "ScenePlan dict"},
                "duration_s": {"type": "number", "default": 30.0},
            },
            "required": ["scene"],
        },
    },
    {
        "name": "instrument_layer",
        "description": "Generate instrument layer from ScenePlan pitched profile.",
        "input_schema": {
            "type": "object",
            "properties": {
                "scene": {"type": "object", "description": "ScenePlan dict"},
                "duration_s": {"type": "number", "default": 30.0},
            },
            "required": ["scene"],
        },
    },
    {
        "name": "granular_cloud",
        "description": "Generate granular cloud layer from ScenePlan.",
        "input_schema": {
            "type": "object",
            "properties": {
                "scene": {"type": "object", "description": "ScenePlan dict"},
                "duration_s": {"type": "number", "default": 30.0},
            },
            "required": ["scene"],
        },
    },
    {
        "name": "mix_render",
        "description": "Render multiple SCJob layers into a final mix.",
        "input_schema": {
            "type": "object",
            "properties": {
                "jobs": {"type": "array", "items": {"type": "object"}},
                "output_path": {"type": "string", "default": "output/render.wav"},
                "duration_s": {"type": "number", "default": 30.0},
            },
            "required": ["jobs"],
        },
    },
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _broadcast(manager: Any, event: dict) -> None:
    """Safely broadcast to a WebSocket connection manager."""
    try:
        await manager.broadcast(event)
    except Exception as e:
        logger.warning("Broadcast failed: %s", e)


async def _execute_tool(tool_name: str, params: dict) -> dict:
    """Run a registered tool and return its result as a dict."""
    if tool_name not in TOOL_REGISTRY:
        return {"error": f"Tool {tool_name!r} not found in registry"}
    try:
        result = await TOOL_REGISTRY[tool_name](**params)
        return result.model_dump() if hasattr(result, "model_dump") else result
    except Exception as e:
        logger.error("Tool %s failed: %s", tool_name, e)
        return {"error": str(e)}


def _result_summary(result: dict) -> str:
    """Extract a short summary from a tool result for the Claude context."""
    if "error" in result:
        return f"Error: {result['error']}"
    summary = result.get("summary", "")
    data = result.get("data", {})
    # Truncate large data blobs (like base64 samples) to keep context small
    compact = {}
    for k, v in data.items():
        if isinstance(v, str) and len(v) > 200:
            compact[k] = f"<{len(v)} chars>"
        elif isinstance(v, list) and len(v) > 20:
            compact[k] = f"<list of {len(v)} items>"
        else:
            compact[k] = v
    return json.dumps({"summary": summary, "data": compact}, default=str)


def _get_anthropic_client():
    """Create an Anthropic client if the API key is available."""
    api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not api_key or api_key == "your-api-key-here":
        return None
    try:
        import anthropic
        return anthropic.Anthropic(api_key=api_key)
    except Exception as e:
        logger.warning("Failed to create Anthropic client: %s", e)
        return None


# ---------------------------------------------------------------------------
# Claude-driven agent loop
# ---------------------------------------------------------------------------

MAX_TOOL_CALLS = 25  # Safety cap to prevent runaway loops


async def _run_claude_agent(
    file_path: str,
    objective: str,
    agent_ws: Any,
    graph_ws: Any,
    render_ws: Any,
) -> dict:
    """Run the real Claude tool-use loop.

    Sends the system prompt + user objective to Claude, then iterates:
    Claude requests tool calls → we execute them → feed results back.
    """
    client = _get_anthropic_client()
    if client is None:
        raise RuntimeError("Anthropic client unavailable")

    results: dict[str, dict] = {}
    node_counter = 0

    # Build initial user message
    user_msg = (
        f"Audio file: {file_path}\n"
        f"Objective: {objective}\n\n"
        "Begin by loading the audio file, then run the full analysis pipeline, "
        "compose a ScenePlan, and generate the soundscape. "
        "Call tools one at a time and explain each step."
    )

    messages: list[dict] = [{"role": "user", "content": user_msg}]

    await _broadcast(agent_ws, {
        "event": "agent_reasoning",
        "step": "start",
        "reasoning": f"Starting Claude-driven analysis of '{file_path}'. Objective: {objective}",
    })

    for iteration in range(MAX_TOOL_CALLS):
        # Call Claude
        response = await asyncio.to_thread(
            client.messages.create,
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            system=AGENT_SYSTEM_PROMPT,
            tools=TOOL_SCHEMAS,
            messages=messages,
        )

        # Collect text reasoning and tool-use blocks
        assistant_content = response.content
        messages.append({"role": "assistant", "content": assistant_content})

        # Broadcast any text reasoning
        for block in assistant_content:
            if block.type == "text" and block.text.strip():
                await _broadcast(agent_ws, {
                    "event": "agent_reasoning",
                    "step": f"iteration_{iteration}",
                    "reasoning": block.text,
                })

        # If no tool use, Claude is done
        tool_use_blocks = [b for b in assistant_content if b.type == "tool_use"]
        if not tool_use_blocks:
            break

        # Execute each tool call
        tool_results_for_claude = []
        for tool_block in tool_use_blocks:
            tool_name = tool_block.name
            tool_input = tool_block.input or {}

            # Place node on graph canvas
            node_counter += 1
            x = 100 + (node_counter % 6) * 200
            y = 100 + (node_counter // 6) * 150
            node_id = graph.place_node(tool_name, x, y, tool_input)
            await _broadcast(graph_ws, {
                "event": "node_placed",
                "node_id": node_id,
                "node_type": tool_name,
                "x": x, "y": y,
                "params": tool_input,
                "reasoning": f"Claude called {tool_name}",
            })

            # Execute tool
            result = await _execute_tool(tool_name, tool_input)
            graph.set_node_result(node_id, result)
            results[f"{tool_name}_{node_counter}"] = result

            # Broadcast result
            await _broadcast(graph_ws, {
                "event": "node_result",
                "node_id": node_id,
                "summary": result.get("summary", ""),
                "artifact_type": result.get("artifact", {}).get("type", "none"),
                "artifact_b64": result.get("artifact", {}).get("content"),
            })

            # Prepare tool result for Claude
            tool_results_for_claude.append({
                "type": "tool_result",
                "tool_use_id": tool_block.id,
                "content": _result_summary(result),
            })

        messages.append({"role": "user", "content": tool_results_for_claude})

        # Check for end_turn
        if response.stop_reason == "end_turn":
            break

    # Signal completion
    await _broadcast(agent_ws, {
        "event": "agent_complete",
        "message": "Claude-driven soundscape generation complete.",
        "results": {k: v.get("summary", "") for k, v in results.items()},
    })
    return results


# ---------------------------------------------------------------------------
# Deterministic fallback (original pipeline, no LLM needed)
# ---------------------------------------------------------------------------

async def _run_deterministic_agent(
    file_path: str,
    objective: str,
    agent_ws: Any,
    graph_ws: Any,
    render_ws: Any,
) -> dict:
    """Execute the fixed analysis → insight → generation pipeline.

    This is the original deterministic orchestration that requires no API key.
    """
    results: dict[str, dict] = {}

    async def _step(
        name: str, reasoning: str, tool_name: str, params: dict
    ) -> dict:
        await _broadcast(agent_ws, {
            "event": "agent_reasoning",
            "step": name,
            "reasoning": reasoning,
        })

        node_id = graph.place_node(
            name, params.get("_x", 0), params.get("_y", 0), params
        )
        await _broadcast(graph_ws, {
            "event": "node_placed",
            "node_id": node_id,
            "node_type": name,
            "x": params.get("_x", 0),
            "y": params.get("_y", 0),
            "params": params,
            "reasoning": reasoning,
        })

        clean_params = {k: v for k, v in params.items() if not k.startswith("_")}
        result_dict = await _execute_tool(tool_name, clean_params)

        graph.set_node_result(node_id, result_dict)
        await _broadcast(graph_ws, {
            "event": "node_result",
            "node_id": node_id,
            "summary": result_dict.get("summary", ""),
            "artifact_type": result_dict.get("artifact", {}).get("type", "none"),
            "artifact_b64": result_dict.get("artifact", {}).get("content"),
        })

        results[name] = result_dict
        return result_dict

    # ── Phase 1: Analysis Pipeline ──
    await _broadcast(agent_ws, {
        "event": "agent_reasoning",
        "step": "start",
        "reasoning": (
            f"Starting deterministic analysis of '{file_path}'. "
            f"Objective: {objective}"
        ),
    })

    load_result = await _step(
        "LoadAudio",
        f"Loading audio file: {file_path}",
        "load_audio",
        {"file_path": file_path, "_x": 100, "_y": 200},
    )
    audio_data = load_result.get("data", {})

    prep_result = await _step(
        "Preprocess",
        "Preprocessing: normalise, mono, trim silence",
        "preprocess",
        {"audio": audio_data, "_x": 300, "_y": 200},
    )
    audio_clean = prep_result.get("data", audio_data)

    await _step(
        "STFT",
        "Computing STFT for spectral analysis",
        "stft",
        {"audio": audio_clean, "_x": 500, "_y": 100},
    )

    spectral_result = await _step(
        "SpectralStats",
        "Measuring spectral features: centroid, flatness, bandwidth",
        "spectral_stats",
        {"audio": audio_clean, "_x": 700, "_y": 100},
    )
    spectral_data = spectral_result.get("data", {})

    temporal_result = await _step(
        "TemporalStats",
        "Measuring temporal features: RMS, loudness, dynamic range",
        "temporal_stats",
        {"audio": audio_clean, "_x": 700, "_y": 200},
    )
    temporal_data = temporal_result.get("data", {})

    onset_result = await _step(
        "Onsets",
        "Detecting onsets and beat structure",
        "onsets",
        {"audio": audio_clean, "_x": 700, "_y": 300},
    )
    events_data = onset_result.get("data", {})

    pitch_result = await _step(
        "PitchTonal",
        "Tracking pitch and estimating key",
        "pitch_tonal",
        {"audio": audio_clean, "_x": 700, "_y": 400},
    )
    pitch_data = pitch_result.get("data", {})

    seg_result = await _step(
        "SegmentMap",
        "Segmenting audio structure",
        "segment_map",
        {"spectral": spectral_data, "audio": audio_clean, "_x": 900, "_y": 200},
    )
    seg_data = seg_result.get("data", {})

    insight_result = await _step(
        "InsightComposer",
        "Composing ScenePlan from all analysis results",
        "insight_composer",
        {
            "spectral": spectral_data,
            "temporal": temporal_data,
            "events": events_data,
            "pitch": pitch_data,
            "segments": seg_data,
            "_x": 1100,
            "_y": 200,
        },
    )
    scene_plan = insight_result.get("data", {})

    # ── Approval gate ──
    await _broadcast(agent_ws, {
        "event": "approval_required",
        "scene_plan": scene_plan,
        "message": "Analysis complete. Ready to generate flow-state soundscape.",
    })
    await asyncio.sleep(0.5)

    # ── Phase 2: Generation Pipeline ──
    await _broadcast(agent_ws, {
        "event": "agent_reasoning",
        "step": "generation_start",
        "reasoning": (
            f"Generating soundscape based on ScenePlan: "
            f"{scene_plan.get('semantic_label', '')}"
        ),
    })

    flow_targets = scene_plan.get("flow_targets", {})

    binaural_result = await _step(
        "BinauralBeatGen",
        f"Creating binaural beat layer: {flow_targets.get('target_band', 'gamma')} entrainment",
        "binaural_beat_gen",
        {
            "carrier_hz": flow_targets.get("carrier_hz", 110.0),
            "beat_hz": flow_targets.get("binaural_beat_hz", 40.0),
            "duration_s": 30.0,
            "_x": 1300,
            "_y": 100,
        },
    )

    texture_result = await _step(
        "TextureLayer",
        "Creating texture layer from ScenePlan texture profile",
        "texture_layer",
        {"scene": scene_plan, "duration_s": 30.0, "_x": 1300, "_y": 200},
    )

    instrument_result = await _step(
        "InstrumentLayer",
        "Creating instrument layer from ScenePlan pitched profile",
        "instrument_layer",
        {"scene": scene_plan, "duration_s": 30.0, "_x": 1300, "_y": 300},
    )

    jobs = []
    for r in [binaural_result, texture_result, instrument_result]:
        if r.get("data"):
            jobs.append(r["data"])

    render_result = await _step(
        "MixRender",
        f"Rendering {len(jobs)} layers into final mix",
        "mix_render",
        {
            "jobs": jobs,
            "output_path": "output/render.wav",
            "duration_s": 30.0,
            "_x": 1500,
            "_y": 200,
        },
    )

    await _broadcast(render_ws, {
        "event": "render_complete",
        "file_path": render_result.get("data", {}).get(
            "file_path", "output/render.wav"
        ),
        "duration_s": 30.0,
    })

    await _broadcast(agent_ws, {
        "event": "agent_complete",
        "message": "Deterministic soundscape generation complete.",
        "results": {k: v.get("summary", "") for k, v in results.items()},
    })
    return results


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

async def run_agent(
    file_path: str,
    objective: str,
    agent_ws: Any,
    graph_ws: Any,
    render_ws: Any,
) -> dict:
    """Run the agent loop.

    Attempts the Claude-driven path first. Falls back to deterministic
    pipeline if the API key is missing or the API call fails.
    """
    client = _get_anthropic_client()
    if client is not None:
        try:
            logger.info("Running Claude-driven agent loop")
            return await _run_claude_agent(
                file_path, objective, agent_ws, graph_ws, render_ws
            )
        except Exception as e:
            logger.warning(
                "Claude agent failed (%s), falling back to deterministic pipeline",
                e,
            )

    logger.info("Running deterministic fallback agent loop")
    return await _run_deterministic_agent(
        file_path, objective, agent_ws, graph_ws, render_ws
    )
