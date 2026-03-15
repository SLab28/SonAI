"""Onsets tool — Phase 1, Task P1-09
Onset detection and beat tracking.
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


async def _onsets(audio: dict, method: str = "default") -> NodeOutput:
    """Detect onsets and beats. Returns EventList."""
    y, sr = decode_audio_buffer(audio)

    if HAS_LIBROSA:
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        onset_frames = librosa.onset.onset_detect(y=y, sr=sr, onset_envelope=onset_env)
        onset_times = librosa.frames_to_time(onset_frames, sr=sr)
        tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr, onset_envelope=onset_env)
        beat_times = librosa.frames_to_time(beat_frames, sr=sr)
        # Handle tempo array (librosa >= 0.10)
        if hasattr(tempo, '__len__'):
            bpm = float(tempo[0]) if len(tempo) > 0 else 120.0
        else:
            bpm = float(tempo)
        strength = onset_env[onset_frames].tolist() if len(onset_frames) > 0 else []
    else:
        # Fallback
        duration = len(y) / sr
        n_onsets = max(1, int(duration * 2))
        onset_times = np.linspace(0.5, duration - 0.5, n_onsets)
        strength = np.ones(n_onsets).tolist()
        bpm = 120.0
        beat_times = np.linspace(0, duration, int(duration * 2))

    duration_s = len(y) / sr
    transient_density = len(onset_times) / max(duration_s, 0.01)

    # Beat regularity
    if len(beat_times) > 1:
        ibi = np.diff(beat_times)
        beat_regularity = float(1.0 - min(1.0, np.std(ibi) / (np.mean(ibi) + 1e-6)))
    else:
        beat_regularity = 0.0

    data = {
        "onsets_s": onset_times.tolist() if hasattr(onset_times, 'tolist') else list(onset_times),
        "onset_strength": strength[:200],
        "bpm": bpm,
        "beat_times_s": beat_times.tolist() if hasattr(beat_times, 'tolist') else list(beat_times),
        "transient_density": transient_density,
        "beat_regularity": beat_regularity,
    }

    # Artifact: onset markers on waveform
    fig, ax = plt.subplots(figsize=(6, 2))
    t = np.linspace(0, duration_s, len(y))
    ax.plot(t, y, color="#888", linewidth=0.3)
    for ot in (onset_times if hasattr(onset_times, '__iter__') else []):
        ax.axvline(x=float(ot), color="#dc2626", linewidth=0.5, alpha=0.7)
    ax.set_facecolor("white")
    fig.patch.set_facecolor("white")
    ax.axis("off")
    fig.tight_layout()
    artifact_b64 = fig_to_b64(fig)

    return NodeOutput(
        node_type="Onsets",
        data=data,
        artifact=NodeArtifact(type="image/png", content=artifact_b64, mime_type="image/png"),
        summary=f"Onsets: {len(data['onsets_s'])} detected, {bpm:.0f} BPM, density={transient_density:.1f}/s, regularity={beat_regularity:.2f}",
    )


@mcp.tool
async def onsets(audio: dict, method: str = "default") -> NodeOutput:
    """Detect onsets and beats."""
    return await _onsets(audio, method)


register_tool("onsets")(_onsets)
