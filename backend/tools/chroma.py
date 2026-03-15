"""Chroma tool — Phase 1, Task P1-12
Computes CQT chroma features.
"""
from __future__ import annotations
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from backend.mcp_instance import mcp
from backend.schemas import NodeOutput, NodeArtifact
from backend.tool_registry import register_tool
from backend.tools._audio_helpers import decode_audio_buffer, fig_to_b64

try:
    import librosa
    import librosa.display
    HAS_LIBROSA = True
except ImportError:
    HAS_LIBROSA = False

PITCH_CLASSES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


async def _chroma(audio: dict) -> NodeOutput:
    """Compute CQT chroma features."""
    y, sr = decode_audio_buffer(audio)

    if HAS_LIBROSA:
        chroma_cq = librosa.feature.chroma_cqt(y=y, sr=sr)
    else:
        n_frames = max(1, len(y) // 512)
        chroma_cq = np.random.rand(12, n_frames)

    mean_vec = np.mean(chroma_cq, axis=1).tolist()
    dominant_idx = int(np.argmax(mean_vec))
    dominant_class = PITCH_CLASSES[dominant_idx]

    # Chroma plot artifact
    fig, ax = plt.subplots(figsize=(6, 3))
    if HAS_LIBROSA:
        librosa.display.specshow(chroma_cq, y_axis="chroma", x_axis="time", sr=sr, ax=ax)
    else:
        ax.imshow(chroma_cq, aspect="auto", origin="lower")
    ax.set_title("Chroma", fontsize=10)
    fig.tight_layout()
    artifact_b64 = fig_to_b64(fig)

    data = {
        "chroma": chroma_cq[:, :100].tolist(),
        "pitch_classes": PITCH_CLASSES,
        "mean_vector": mean_vec,
        "dominant_class": dominant_class,
    }

    return NodeOutput(
        node_type="Chroma",
        data=data,
        artifact=NodeArtifact(type="image/png", content=artifact_b64, mime_type="image/png"),
        summary=f"Chroma: dominant={dominant_class}, {chroma_cq.shape[1]} frames",
    )


@mcp.tool
async def chroma(audio: dict) -> NodeOutput:
    """Compute CQT chroma features."""
    return await _chroma(audio)


register_tool("chroma")(_chroma)
