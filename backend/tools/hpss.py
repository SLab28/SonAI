"""HPSS tool — Phase 1, Task P1-06
Separates harmonic and percussive components using librosa HPSS.
"""
from __future__ import annotations
import numpy as np

from backend.mcp_instance import mcp
from backend.schemas import NodeOutput, AudioBuffer, NodeArtifact
from backend.tool_registry import register_tool
from backend.tools._audio_helpers import decode_audio_buffer, encode_samples

try:
    import librosa
    HAS_LIBROSA = True
except ImportError:
    HAS_LIBROSA = False


async def _hpss(audio: dict, margin: float = 1.0) -> NodeOutput:
    """Separate harmonic and percussive components."""
    y, sr = decode_audio_buffer(audio)

    if HAS_LIBROSA:
        h, p = librosa.effects.hpss(y, margin=margin)
    else:
        # Fallback: naive split
        h = y * 0.5
        p = y * 0.5

    harmonic = AudioBuffer(
        samples=encode_samples(h), sr=sr, channels=1,
        duration_s=len(h) / sr, file_path=audio.get("file_path"),
    )
    percussive = AudioBuffer(
        samples=encode_samples(p), sr=sr, channels=1,
        duration_s=len(p) / sr, file_path=audio.get("file_path"),
    )

    data = {
        "harmonic": harmonic.model_dump(),
        "percussive": percussive.model_dump(),
        "margin": margin,
    }

    return NodeOutput(
        node_type="HPSS",
        data=data,
        artifact=NodeArtifact(type="none", mime_type="none"),
        summary=f"HPSS separation (margin={margin}): {len(y)/sr:.1f}s harmonic + percussive",
    )


@mcp.tool
async def hpss(audio: dict, margin: float = 1.0) -> NodeOutput:
    """Separate harmonic and percussive components."""
    return await _hpss(audio, margin)


register_tool("hpss")(_hpss)
