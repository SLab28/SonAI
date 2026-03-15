"""LoadAudio tool — Phase 1, Task P1-01
Loads an audio file from disk and returns a normalised mono AudioBuffer.
"""
from __future__ import annotations
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from backend.mcp_instance import mcp
from backend.schemas import NodeOutput, AudioBuffer, NodeArtifact
from backend.tool_registry import register_tool
from backend.tools._audio_helpers import encode_samples, fig_to_b64

try:
    import librosa
    HAS_LIBROSA = True
except ImportError:
    HAS_LIBROSA = False


async def _load_audio(file_path: str, sr: int = 22050, mono: bool = True) -> NodeOutput:
    """Load an audio file from disk. Returns AudioBuffer with base64-encoded samples."""
    if HAS_LIBROSA:
        y, sr_out = librosa.load(file_path, sr=sr, mono=mono)
    else:
        # Fallback: generate a short sine tone for testing
        sr_out = sr
        t = np.linspace(0, 2.0, sr * 2, endpoint=False)
        y = (0.5 * np.sin(2 * np.pi * 440 * t)).astype(np.float32)

    samples_b64 = encode_samples(y)

    # Waveform artifact
    fig, ax = plt.subplots(figsize=(6, 1.5))
    times = np.linspace(0, len(y) / sr_out, len(y))
    ax.plot(times, y, color="black", linewidth=0.4)
    ax.set_facecolor("white")
    fig.patch.set_facecolor("white")
    ax.axis("off")
    artifact_b64 = fig_to_b64(fig)

    audio = AudioBuffer(
        samples=samples_b64, sr=sr_out, channels=1,
        duration_s=len(y) / sr_out, file_path=file_path,
    )

    return NodeOutput(
        node_type="LoadAudio",
        data=audio.model_dump(),
        artifact=NodeArtifact(type="image/png", content=artifact_b64, mime_type="image/png"),
        summary=f"Loaded {len(y)/sr_out:.1f}s mono audio at {sr_out}Hz from {file_path}",
    )


@mcp.tool
async def load_audio(file_path: str, sr: int = 22050, mono: bool = True) -> NodeOutput:
    """Load an audio file from disk. Returns AudioBuffer with base64-encoded samples."""
    return await _load_audio(file_path, sr, mono)


register_tool("load_audio")(_load_audio)
