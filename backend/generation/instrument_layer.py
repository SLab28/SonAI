"""InstrumentLayer tool — Phase 2, Task P2-04
Renders an instrument layer (pad, drone, melodic) using SC synthesis.
"""
from __future__ import annotations
import uuid

from backend.mcp_instance import mcp
from backend.schemas import NodeOutput, SCJob, NodeArtifact
from backend.tool_registry import register_tool
from backend.sc.osc_client import sc_send

ROLE_SYNTHDEF = {
    "drone": "SonaiDrone",
    "pad": "SonaiPad",
    "melodic": "SonaiPad",
    "percussive": "SonaiPad",
}


async def _instrument_layer(
    scene: dict, duration_s: float = 30.0, instrument_type: str = "pad"
) -> NodeOutput:
    """Render an instrument layer from ScenePlan."""
    pp = scene.get("pitched_profile", {})
    role = pp.get("instrument_role", instrument_type)
    synthdef = ROLE_SYNTHDEF.get(role, "SonaiPad")
    freq = pp.get("dominant_pitch_hz", 220.0)

    job_id = str(uuid.uuid4())
    if synthdef == "SonaiDrone":
        params = {"freq_hz": freq, "harmonics": 3, "amp": 0.4, "dur": duration_s}
        osc_addr = "/sonai/drone"
    else:
        params = {
            "freq_hz": freq,
            "detune": 0.02,
            "cutoff": 1200.0,
            "amp": 0.3,
            "dur": duration_s,
            "attack": 3.0,
            "release": 5.0,
        }
        osc_addr = "/sonai/pad"

    await sc_send(osc_addr, list(params.values()))

    job = SCJob(
        id=job_id,
        synthdef=synthdef,
        params=params,
        duration_s=duration_s,
        status="queued",
    )

    return NodeOutput(
        node_type="InstrumentLayer",
        data=job.model_dump(),
        artifact=NodeArtifact(type="none", mime_type="none"),
        summary=f"Instrument layer: {synthdef} at {freq:.0f}Hz, role={role}, {duration_s}s",
    )


@mcp.tool
async def instrument_layer(
    scene: dict, duration_s: float = 30.0, instrument_type: str = "pad"
) -> NodeOutput:
    """Render an instrument layer from ScenePlan."""
    return await _instrument_layer(scene, duration_s, instrument_type)


register_tool("instrument_layer")(_instrument_layer)
