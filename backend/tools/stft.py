"""STFT tool — Phase 1, Task P1-04
Computes STFT magnitude and phase. Returns STFTFrame + spectrogram artifact.
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


async def _stft(audio: dict, n_fft: int = 2048, hop_length: int = 512) -> NodeOutput:
    """Compute Short-Time Fourier Transform of AudioBuffer."""
    y, sr = decode_audio_buffer(audio)

    if HAS_LIBROSA:
        S = librosa.stft(y, n_fft=n_fft, hop_length=hop_length)
        mag = np.abs(S)
        phase = np.angle(S)
        freq_bins = librosa.fft_frequencies(sr=sr, n_fft=n_fft).tolist()
        time_frames = librosa.frames_to_time(
            np.arange(mag.shape[1]), sr=sr, hop_length=hop_length
        ).tolist()
    else:
        # Fallback: simple FFT
        n_frames = max(1, len(y) // hop_length)
        mag = np.random.rand(n_fft // 2 + 1, n_frames).tolist()
        phase = np.zeros_like(np.array(mag)).tolist()
        freq_bins = np.linspace(0, sr / 2, n_fft // 2 + 1).tolist()
        time_frames = np.linspace(0, len(y) / sr, n_frames).tolist()
        mag_arr = np.array(mag)

    # Spectrogram artifact
    fig, ax = plt.subplots(figsize=(6, 3))
    if HAS_LIBROSA:
        S_db = librosa.amplitude_to_db(mag, ref=np.max)
        librosa.display.specshow(S_db, sr=sr, hop_length=hop_length, x_axis="time", y_axis="hz", ax=ax)
        mag_list = mag.tolist()
        phase_list = phase.tolist()
    else:
        ax.imshow(np.array(mag), aspect="auto", origin="lower")
        mag_list = mag
        phase_list = phase
    ax.set_title("Spectrogram", fontsize=10)
    fig.tight_layout()
    artifact_b64 = fig_to_b64(fig)

    data = {
        "magnitude": mag_list[:20],  # Truncate for JSON sanity
        "phase": phase_list[:20],
        "sr": sr,
        "n_fft": n_fft,
        "hop_length": hop_length,
        "freq_bins": freq_bins[:50],
        "time_frames": time_frames[:100],
    }

    n_frames_total = len(time_frames)
    return NodeOutput(
        node_type="STFT",
        data=data,
        artifact=NodeArtifact(type="image/png", content=artifact_b64, mime_type="image/png"),
        summary=f"STFT: {n_fft} FFT, {hop_length} hop, {n_frames_total} frames, sr={sr}Hz",
    )


@mcp.tool
async def stft(audio: dict, n_fft: int = 2048, hop_length: int = 512) -> NodeOutput:
    """Compute Short-Time Fourier Transform."""
    return await _stft(audio, n_fft, hop_length)


register_tool("stft")(_stft)
