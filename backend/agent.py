"""SonAI Agent Loop — Phase 3
Orchestrates analysis → insight → generation flow.
Uses the tool registry to execute tools and the graph module to place nodes.
"""
from __future__ import annotations
import asyncio
import logging
from typing import Any

from backend.graph import graph
from backend.tool_registry import TOOL_REGISTRY

logger = logging.getLogger(__name__)

# System prompt for the agent (used when wired to Claude via MCP)
AGENT_SYSTEM_PROMPT = """You are SonAI, an AI audio analysis and flow-state soundscape generation agent.

You operate on a node-based canvas. Your workflow:
1. ANALYSE: Load audio → Preprocess → run STFT, SpectralStats, TemporalStats, Onsets, PitchTonal, MFCC, Chroma → SegmentMap → InsightComposer
2. COMPOSE: Read the ScenePlan from InsightComposer, then place generation nodes (BinauralBeatGen, TextureLayer, InstrumentLayer, GranularCloud)
3. RENDER: Place a MixRender node that collects all SCJobs and produces the final audio file

Rules:
- Place nodes one at a time and wait for results before placing dependent nodes
- Never place generation nodes until InsightComposer returns a ScenePlan
- Never generate vocals, speech, or lyric-based content
- Explain your reasoning for each node placement
- Use the ScenePlan's flow_targets to configure binaural beats
- Keep the output non-rhythmic and flow-state oriented unless the analysis suggests otherwise

Available tools: load_audio, preprocess, stft, hpss, spectral_stats, temporal_stats,
onsets, pitch_tonal, mfcc, chroma, segment_map, insight_composer,
binaural_beat_gen, texture_layer, instrument_layer, granular_cloud, mix_render
"""


async def _broadcast(manager, event: dict):
    """Safely broadcast to a connection manager."""
    try:
        await manager.broadcast(event)
    except Exception as e:
        logger.warning(f"Broadcast failed: {e}")


async def run_agent(
    file_path: str,
    objective: str,
    agent_ws: Any,
    graph_ws: Any,
    render_ws: Any,
) -> dict:
    """Execute the full agent loop: analyse → insight → generate → render.

    This is a deterministic orchestration loop (MVP). A future version would
    use Claude tool-calling via MCP for adaptive reasoning.
    """
    results = {}

    async def _step(name: str, reasoning: str, tool_name: str, params: dict) -> dict:
        """Place a node, run the tool, broadcast results."""
        # Broadcast reasoning
        await _broadcast(agent_ws, {
            "event": "agent_reasoning",
            "step": name,
            "reasoning": reasoning,
        })

        # Place node on canvas
        node_id = graph.place_node(name, params.get("_x", 0), params.get("_y", 0), params)
        await _broadcast(graph_ws, {
            "event": "node_placed",
            "node_id": node_id,
            "node_type": name,
            "x": params.get("_x", 0),
            "y": params.get("_y", 0),
            "params": params,
            "reasoning": reasoning,
        })

        # Execute tool
        clean_params = {k: v for k, v in params.items() if not k.startswith("_")}
        if tool_name in TOOL_REGISTRY:
            try:
                result = await TOOL_REGISTRY[tool_name](**clean_params)
                result_dict = result.model_dump() if hasattr(result, "model_dump") else result
            except Exception as e:
                logger.error(f"Tool {tool_name} failed: {e}")
                result_dict = {"error": str(e)}
        else:
            result_dict = {"error": f"Tool {tool_name} not found"}

        # Broadcast result
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
        "reasoning": f"Starting analysis of '{file_path}'. Objective: {objective}",
    })

    # 1. Load audio
    load_result = await _step(
        "LoadAudio",
        f"Loading audio file: {file_path}",
        "load_audio",
        {"file_path": file_path, "_x": 100, "_y": 200},
    )
    audio_data = load_result.get("data", {})

    # 2. Preprocess
    prep_result = await _step(
        "Preprocess",
        "Preprocessing: normalise, mono, trim silence",
        "preprocess",
        {"audio": audio_data, "_x": 300, "_y": 200},
    )
    audio_clean = prep_result.get("data", audio_data)

    # 3. STFT
    stft_result = await _step(
        "STFT",
        "Computing STFT for spectral analysis",
        "stft",
        {"audio": audio_clean, "_x": 500, "_y": 100},
    )

    # 4. Spectral stats
    spectral_result = await _step(
        "SpectralStats",
        "Measuring spectral features: centroid, flatness, bandwidth",
        "spectral_stats",
        {"audio": audio_clean, "_x": 700, "_y": 100},
    )
    spectral_data = spectral_result.get("data", {})

    # 5. Temporal stats
    temporal_result = await _step(
        "TemporalStats",
        "Measuring temporal features: RMS, loudness, dynamic range",
        "temporal_stats",
        {"audio": audio_clean, "_x": 700, "_y": 200},
    )
    temporal_data = temporal_result.get("data", {})

    # 6. Onsets
    onset_result = await _step(
        "Onsets",
        "Detecting onsets and beat structure",
        "onsets",
        {"audio": audio_clean, "_x": 700, "_y": 300},
    )
    events_data = onset_result.get("data", {})

    # 7. Pitch/Tonal
    pitch_result = await _step(
        "PitchTonal",
        "Tracking pitch and estimating key",
        "pitch_tonal",
        {"audio": audio_clean, "_x": 700, "_y": 400},
    )
    pitch_data = pitch_result.get("data", {})

    # 8. Segment map
    seg_result = await _step(
        "SegmentMap",
        "Segmenting audio structure",
        "segment_map",
        {"spectral": spectral_data, "audio": audio_clean, "_x": 900, "_y": 200},
    )
    seg_data = seg_result.get("data", {})

    # 9. Insight Composer
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

    # ── User approval gate ──
    await _broadcast(agent_ws, {
        "event": "approval_required",
        "scene_plan": scene_plan,
        "message": "Analysis complete. Ready to generate flow-state soundscape. Approve to proceed.",
    })

    # In the MVP, auto-approve after a brief pause
    await asyncio.sleep(0.5)

    # ── Phase 2: Generation Pipeline ──

    await _broadcast(agent_ws, {
        "event": "agent_reasoning",
        "step": "generation_start",
        "reasoning": f"Generating soundscape based on ScenePlan: {scene_plan.get('semantic_label', '')}",
    })

    flow_targets = scene_plan.get("flow_targets", {})

    # 10. Binaural beat
    binaural_result = await _step(
        "BinauralBeatGen",
        f"Creating binaural beat layer: {flow_targets.get('target_band', 'gamma')} entrainment",
        "binaural_beat_gen",
        {
            "carrier_hz": flow_targets.get("carrier_hz", 110.0),
            "beat_hz": flow_targets.get("binaural_beat_hz", 40.0),
            "duration_s": 30.0,
            "_x": 1300, "_y": 100,
        },
    )

    # 11. Texture layer
    texture_result = await _step(
        "TextureLayer",
        "Creating texture layer from ScenePlan texture profile",
        "texture_layer",
        {"scene": scene_plan, "duration_s": 30.0, "_x": 1300, "_y": 200},
    )

    # 12. Instrument layer
    instrument_result = await _step(
        "InstrumentLayer",
        "Creating instrument layer from ScenePlan pitched profile",
        "instrument_layer",
        {"scene": scene_plan, "duration_s": 30.0, "_x": 1300, "_y": 300},
    )

    # 13. Mix render
    jobs = []
    for r in [binaural_result, texture_result, instrument_result]:
        if r.get("data"):
            jobs.append(r["data"])

    render_result = await _step(
        "MixRender",
        f"Rendering {len(jobs)} layers into final mix",
        "mix_render",
        {"jobs": jobs, "output_path": "output/render.wav", "duration_s": 30.0, "_x": 1500, "_y": 200},
    )

    # Broadcast render complete
    await _broadcast(render_ws, {
        "event": "render_complete",
        "file_path": render_result.get("data", {}).get("file_path", "output/render.wav"),
        "duration_s": 30.0,
    })

    await _broadcast(agent_ws, {
        "event": "agent_complete",
        "message": "Flow-state soundscape generation complete.",
        "results": {k: v.get("summary", "") for k, v in results.items()},
    })

    return results
