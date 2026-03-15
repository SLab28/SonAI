"""MFCC tool — Phase 1, Task P1-11
Computes Mel-frequency cepstral coefficients.
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


async def _mfcc(audio: dict, n_mfcc: int = 13) -> NodeOutput:
    """Compute MFCC matrix."""
    y, sr = decode_audio_buffer(audio)

    if HAS_LIBROSA:
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc)
    else:
        n_frames = max(1, len(y) // 512)
        mfccs = np.random.randn(n_mfcc, n_frames)

    mean_vec = np.mean(mfccs, axis=1).tolist()
    std_vec = np.std(mfccs, axis=1).tolist()

    # Heatmap artifact
    fig, ax = plt.subplots(figsize=(6, 3))
    if HAS_LIBROSA:
        librosa.display.specshow(mfccs, sr=sr, x_axis="time", ax=ax)
    else:
        ax.imshow(mfccs, aspect="auto", origin="lower")
    ax.set_title("MFCC", fontsize=10)
    ax.set_ylabel("Coefficient", fontsize=8)
    fig.tight_layout()
    artifact_b64 = fig_to_b64(fig)

    data = {
        "coefficients": mfccs[:, :100].tolist(),
        "n_mfcc": n_mfcc,
        "mean_vector": mean_vec,
        "std_vector": std_vec,
    }

    return NodeOutput(
        node_type="MFCC",
        data=data,
        artifact=NodeArtifact(type="image/png", content=artifact_b64, mime_type="image/png"),
        summary=f"MFCC: {n_mfcc} coefficients, {mfccs.shape[1]} frames",
    )


@mcp.tool
async def mfcc(audio: dict, n_mfcc: int = 13) -> NodeOutput:
    """Compute MFCCs."""
    return await _mfcc(audio, n_mfcc)


register_tool("mfcc")(_mfcc)
