"""BinauralBeatGen tool — Phase 2, Task P2-02
Queues a binaural beat layer in SuperCollider.
"""
from __future__ import annotations
import uuid

from backend.mcp_instance import mcp
from backend.schemas import NodeOutput, SCJob, NodeArtifact
from backend.tool_registry import register_tool
from backend.sc.osc_client import sc_send


async def _binaural_beat_gen(
    carrier_hz: float = 110.0,
    beat_hz: float = 40.0,
    duration_s: float = 30.0,
    amplitude: float = 0.3,
) -> NodeOutput:
    """Queue a binaural beat layer."""
    job_id = str(uuid.uuid4())
    params = {
        "carrier_hz": carrier_hz,
        "beat_hz": beat_hz,
        "amp": amplitude,
        "dur": duration_s,
    }

    # Send to SC (graceful if unavailable)
    await sc_send("/sonai/binaural", [carrier_hz, beat_hz, amplitude, duration_s])

    job = SCJob(
        id=job_id,
        synthdef="SonaiBinaural",
        params=params,
        duration_s=duration_s,
        status="queued",
    )

    return NodeOutput(
        node_type="BinauralBeatGen",
        data=job.model_dump(),
        artifact=NodeArtifact(type="none", mime_type="none"),
        summary=f"Binaural beat: carrier={carrier_hz}Hz, beat={beat_hz}Hz, {duration_s}s",
    )


@mcp.tool
async def binaural_beat_gen(
    carrier_hz: float = 110.0,
    beat_hz: float = 40.0,
    duration_s: float = 30.0,
    amplitude: float = 0.3,
) -> NodeOutput:
    """Queue a binaural beat layer."""
    return await _binaural_beat_gen(carrier_hz, beat_hz, duration_s, amplitude)


register_tool("binaural_beat_gen")(_binaural_beat_gen)
