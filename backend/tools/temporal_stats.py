"""TemporalStats tool — Phase 1, Task P1-08
Computes RMS envelope, loudness, dynamic range.
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
    HAS_LIBROSA = True
except ImportError:
    HAS_LIBROSA = False


async def _temporal_stats(audio: dict) -> NodeOutput:
    """Compute temporal feature vector from AudioBuffer."""
    y, sr = decode_audio_buffer(audio)

    if HAS_LIBROSA:
        rms = librosa.feature.rms(y=y)[0]
        times = librosa.frames_to_time(np.arange(len(rms)), sr=sr)
    else:
        frame_len = 2048
        hop = 512
        n_frames = max(1, (len(y) - frame_len) // hop + 1)
        rms = np.array([
            np.sqrt(np.mean(y[i * hop:i * hop + frame_len] ** 2))
            for i in range(n_frames)
        ])
        times = np.linspace(0, len(y) / sr, n_frames)

    rms_mean = float(np.mean(rms))
    rms_std = float(np.std(rms))
    rms_db = 20 * np.log10(rms + 1e-10)
    loudness_lufs = float(np.mean(rms_db))  # Simplified LUFS approximation
    dynamic_range = float(np.max(rms_db) - np.min(rms_db))

    data = {
        "rms_mean": rms_mean,
        "rms_std": rms_std,
        "loudness_lufs": loudness_lufs,
        "dynamic_range_db": dynamic_range,
        "envelope": rms.tolist()[:200],
        "envelope_times": times.tolist()[:200],
    }

    # Artifact: RMS envelope
    fig, ax = plt.subplots(figsize=(6, 2))
    ax.plot(times[:200], rms[:200], color="#16a34a", linewidth=0.8)
    ax.fill_between(times[:200], rms[:200], alpha=0.2, color="#16a34a")
    ax.set_ylabel("RMS", fontsize=8)
    ax.set_xlabel("Time (s)", fontsize=8)
    ax.set_facecolor("white")
    fig.patch.set_facecolor("white")
    fig.tight_layout()
    artifact_b64 = fig_to_b64(fig)

    return NodeOutput(
        node_type="TemporalStats",
        data=data,
        artifact=NodeArtifact(type="image/png", content=artifact_b64, mime_type="image/png"),
        summary=f"Temporal: RMS={rms_mean:.4f}, loudness≈{loudness_lufs:.1f}dB, dynamic range={dynamic_range:.1f}dB",
    )


@mcp.tool
async def temporal_stats(audio: dict) -> NodeOutput:
    """Compute temporal feature vector."""
    return await _temporal_stats(audio)


register_tool("temporal_stats")(_temporal_stats)
