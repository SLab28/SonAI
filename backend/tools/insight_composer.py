"""InsightComposer tool — Phase 1, Task P1-14
Aggregates all Measure outputs into a ScenePlan for generation.
"""
from __future__ import annotations

from backend.mcp_instance import mcp
from backend.schemas import NodeOutput, NodeArtifact
from backend.tool_registry import register_tool


def _classify_density(flatness: float, onset_density: float) -> str:
    if onset_density < 1.0 and flatness < 0.3:
        return "sparse"
    elif onset_density > 4.0 or flatness > 0.6:
        return "dense"
    return "medium"


def _classify_brightness(centroid: float) -> str:
    if centroid < 1500:
        return "dark"
    elif centroid > 3500:
        return "bright"
    return "neutral"


def _classify_stability(rms_std: float, dynamic_range: float) -> str:
    if rms_std < 0.02 and dynamic_range < 10:
        return "stable"
    elif rms_std > 0.08 or dynamic_range > 30:
        return "turbulent"
    return "evolving"


def _classify_space(dynamic_range: float, flatness: float) -> str:
    if dynamic_range > 25 and flatness < 0.2:
        return "expansive"
    elif dynamic_range < 10:
        return "intimate"
    return "room"


def _classify_harmonic_complexity(key_confidence: float) -> str:
    if key_confidence > 0.7:
        return "simple"
    elif key_confidence < 0.3:
        return "complex"
    return "modal"


def _classify_instrument_role(onset_density: float, dominant_pitch: float) -> str:
    if onset_density < 0.5:
        return "drone"
    elif onset_density > 5.0:
        return "percussive"
    elif dominant_pitch > 400:
        return "melodic"
    return "pad"


def _classify_regularity(beat_regularity: float) -> str:
    if beat_regularity < 0.3:
        return "arrhythmic"
    elif beat_regularity > 0.7:
        return "strict"
    return "loose"


def _select_flow_targets(bpm: float, onset_density: float) -> dict:
    """Select binaural beat targets based on analysis."""
    # Default to gamma (flow state)
    if onset_density < 1.0 and bpm < 80:
        return {"binaural_beat_hz": 40.0, "carrier_hz": 110.0, "target_band": "gamma"}
    elif bpm > 100:
        return {"binaural_beat_hz": 20.0, "carrier_hz": 200.0, "target_band": "beta"}
    elif onset_density > 3.0:
        return {"binaural_beat_hz": 10.0, "carrier_hz": 300.0, "target_band": "alpha"}
    return {"binaural_beat_hz": 40.0, "carrier_hz": 110.0, "target_band": "gamma"}


async def _insight_composer(
    spectral: dict,
    temporal: dict,
    events: dict,
    pitch: dict,
    segments: dict,
) -> NodeOutput:
    """Synthesise all analysis outputs into a ScenePlan."""
    centroid = spectral.get("centroid_mean", 2000)
    flatness = spectral.get("flatness_mean", 0.2)
    rms_std = temporal.get("rms_std", 0.03)
    dynamic_range = temporal.get("dynamic_range_db", 15)
    bpm = events.get("bpm", 120)
    onset_density = events.get("transient_density", 2.0)
    beat_regularity = events.get("beat_regularity", 0.5)
    dominant_pitch = pitch.get("dominant_pitch_hz", 220)
    key = pitch.get("key", "C")
    key_confidence = pitch.get("key_confidence", 0.5)

    density = _classify_density(flatness, onset_density)
    brightness = _classify_brightness(centroid)
    stability = _classify_stability(rms_std, dynamic_range)
    space = _classify_space(dynamic_range, flatness)
    harmonic_complexity = _classify_harmonic_complexity(key_confidence)
    instrument_role = _classify_instrument_role(onset_density, dominant_pitch)
    regularity = _classify_regularity(beat_regularity)
    flow_targets = _select_flow_targets(bpm, onset_density)

    scene_plan = {
        "texture_profile": {
            "density": density,
            "brightness": brightness,
            "noisiness": round(flatness, 3),
            "stability": stability,
            "space": space,
        },
        "pitched_profile": {
            "dominant_pitch_hz": dominant_pitch,
            "key": key,
            "harmonic_complexity": harmonic_complexity,
            "instrument_role": instrument_role,
        },
        "rhythm_profile": {
            "bpm": bpm,
            "regularity": regularity,
            "onset_density": onset_density,
        },
        "flow_targets": flow_targets,
        "semantic_label": (
            f"{density} {brightness} {stability} soundscape with "
            f"{instrument_role} in {key}, targeting {flow_targets['target_band']} entrainment"
        ),
    }

    return NodeOutput(
        node_type="InsightComposer",
        data=scene_plan,
        artifact=NodeArtifact(type="application/json", content=None, mime_type="application/json"),
        summary=scene_plan["semantic_label"],
    )


@mcp.tool
async def insight_composer(
    spectral: dict, temporal: dict, events: dict, pitch: dict, segments: dict
) -> NodeOutput:
    """Synthesise analysis outputs into a ScenePlan."""
    return await _insight_composer(spectral, temporal, events, pitch, segments)


register_tool("insight_composer")(_insight_composer)
