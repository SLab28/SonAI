"""GranularCloud tool — Phase 2, Task P2-05
Creates a granular cloud from source audio.
"""
from __future__ import annotations
import uuid

from backend.mcp_instance import mcp
from backend.schemas import NodeOutput, SCJob, NodeArtifact
from backend.tool_registry import register_tool
from backend.sc.osc_client import sc_send


async def _granular_cloud(
    audio: dict,
    density: float = 0.5,
    pitch_variation: float = 0.1,
    duration_s: float = 30.0,
) -> NodeOutput:
    """Create a granular cloud from source audio."""
    job_id = str(uuid.uuid4())
    params = {
        "bufNum": 0,  # Would be assigned by SC buffer allocation
        "density": density,
        "pitch_var": pitch_variation,
        "dur": duration_s,
        "amp": 0.4,
    }

    await sc_send("/sonai/granular", [0, density, pitch_variation, duration_s, 0.4])

    job = SCJob(
        id=job_id,
        synthdef="SonaiGranular",
        params=params,
        duration_s=duration_s,
        status="queued",
    )

    return NodeOutput(
        node_type="GranularCloud",
        data=job.model_dump(),
        artifact=NodeArtifact(type="none", mime_type="none"),
        summary=f"Granular cloud: density={density}, pitch_var={pitch_variation}, {duration_s}s",
    )


@mcp.tool
async def granular_cloud(
    audio: dict,
    density: float = 0.5,
    pitch_variation: float = 0.1,
    duration_s: float = 30.0,
) -> NodeOutput:
    """Create a granular cloud from source audio."""
    return await _granular_cloud(audio, density, pitch_variation, duration_s)


register_tool("granular_cloud")(_granular_cloud)
