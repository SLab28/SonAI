"""SegmentMap tool — Phase 1, Task P1-13
Structural segmentation using spectral features.
"""
from __future__ import annotations
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from backend.mcp_instance import mcp
from backend.schemas import NodeOutput, NodeArtifact
from backend.tool_registry import register_tool
from backend.tools._audio_helpers import fig_to_b64

try:
    import librosa
    HAS_LIBROSA = True
except ImportError:
    HAS_LIBROSA = False


async def _segment_map(spectral: dict, audio: dict | None = None) -> NodeOutput:
    """Segment audio into structurally homogeneous sections."""
    # Extract frame times from spectral data
    frame_times = spectral.get("frame_times", [])
    duration = frame_times[-1] if frame_times else 10.0

    if HAS_LIBROSA and audio:
        from backend.tools._audio_helpers import decode_audio_buffer
        y, sr = decode_audio_buffer(audio)
        # Use recurrence-based segmentation
        try:
            mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            bounds = librosa.segment.agglomerative(mfcc, k=min(6, max(2, int(duration / 5))))
            bound_times = librosa.frames_to_time(bounds, sr=sr).tolist()
        except Exception:
            n_seg = max(2, int(duration / 10))
            bound_times = np.linspace(0, duration, n_seg + 1).tolist()
    else:
        n_seg = max(2, int(duration / 10))
        bound_times = np.linspace(0, duration, n_seg + 1).tolist()

    n_segments = len(bound_times) - 1
    labels = [f"section_{i}" for i in range(n_segments)]

    # Simplified segment features
    segment_features = []
    for i in range(n_segments):
        segment_features.append({
            "centroid_mean": spectral.get("centroid_mean", 0),
            "flatness_mean": spectral.get("flatness_mean", 0),
        })

    data = {
        "boundaries_s": bound_times,
        "labels": labels,
        "n_segments": n_segments,
        "segment_features": segment_features,
    }

    # Artifact: segment boundaries
    fig, ax = plt.subplots(figsize=(6, 1.5))
    for i, bt in enumerate(bound_times):
        ax.axvline(x=bt, color="#d97706", linewidth=1.5, alpha=0.8)
    for i in range(n_segments):
        mid = (bound_times[i] + bound_times[i + 1]) / 2
        ax.text(mid, 0.5, labels[i], ha="center", fontsize=7, color="#78350f")
    ax.set_xlim(0, duration)
    ax.set_facecolor("white")
    fig.patch.set_facecolor("white")
    ax.set_yticks([])
    fig.tight_layout()
    artifact_b64 = fig_to_b64(fig)

    return NodeOutput(
        node_type="SegmentMap",
        data=data,
        artifact=NodeArtifact(type="image/png", content=artifact_b64, mime_type="image/png"),
        summary=f"Segmentation: {n_segments} sections over {duration:.1f}s",
    )


@mcp.tool
async def segment_map(spectral: dict, audio: dict | None = None) -> NodeOutput:
    """Segment audio into structurally homogeneous sections."""
    return await _segment_map(spectral, audio)


register_tool("segment_map")(_segment_map)
