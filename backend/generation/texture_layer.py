"""TextureLayer tool — Phase 2, Task P2-03
Generates a procedural texture layer via SC based on ScenePlan texture_profile.
"""
from __future__ import annotations
import uuid

from backend.mcp_instance import mcp
from backend.schemas import NodeOutput, SCJob, NodeArtifact
from backend.tool_registry import register_tool
from backend.sc.osc_client import sc_send

DENSITY_MAP = {"sparse": 0.2, "medium": 0.5, "dense": 0.8}
BRIGHTNESS_MAP = {"dark": 0.2, "neutral": 0.5, "bright": 0.8}


async def _texture_layer(scene: dict, duration_s: float = 30.0) -> NodeOutput:
    """Generate a texture layer from ScenePlan."""
    tp = scene.get("texture_profile", {})
    density = DENSITY_MAP.get(tp.get("density", "medium"), 0.5)
    brightness = BRIGHTNESS_MAP.get(tp.get("brightness", "neutral"), 0.5)

    job_id = str(uuid.uuid4())
    params = {
        "density": density,
        "brightness": brightness,
        "amp": 0.3,
        "dur": duration_s,
        "pan": 0.0,
    }

    await sc_send("/sonai/texture", [density, brightness, 0.3, duration_s, 0.0])

    job = SCJob(
        id=job_id,
        synthdef="SonaiTexture",
        params=params,
        duration_s=duration_s,
        status="queued",
    )

    return NodeOutput(
        node_type="TextureLayer",
        data=job.model_dump(),
        artifact=NodeArtifact(type="none", mime_type="none"),
        summary=f"Texture layer: density={tp.get('density','medium')}, brightness={tp.get('brightness','neutral')}, {duration_s}s",
    )


@mcp.tool
async def texture_layer(scene: dict, duration_s: float = 30.0) -> NodeOutput:
    """Generate a texture layer from ScenePlan."""
    return await _texture_layer(scene, duration_s)


register_tool("texture_layer")(_texture_layer)
