"""Preprocess tool — Phase 1, Task P1-03
Normalises amplitude, resamples, converts to mono, optionally trims silence.
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


async def _preprocess(
    audio: dict, target_sr: int = 22050, trim_silence: bool = True
) -> NodeOutput:
    """Normalise, resample, mono, and optionally trim silence."""
    y, sr = decode_audio_buffer(audio)

    # Mono
    if y.ndim > 1:
        y = np.mean(y, axis=0)

    # Resample
    if HAS_LIBROSA and sr != target_sr:
        y = librosa.resample(y, orig_sr=sr, target_sr=target_sr)
        sr = target_sr

    # Normalise
    peak = np.max(np.abs(y))
    if peak > 0:
        y = y / peak

    # Trim silence
    if trim_silence and HAS_LIBROSA:
        y, _ = librosa.effects.trim(y)

    samples_b64 = encode_samples(y)
    ab = AudioBuffer(
        samples=samples_b64, sr=sr, channels=1,
        duration_s=len(y) / sr, file_path=audio.get("file_path"),
    )

    return NodeOutput(
        node_type="Preprocess",
        data=ab.model_dump(),
        artifact=NodeArtifact(type="none", mime_type="none"),
        summary=f"Preprocessed to {len(y)/sr:.1f}s mono at {sr}Hz, peak-normalised",
    )


@mcp.tool
async def preprocess(audio: dict, target_sr: int = 22050, trim_silence: bool = True) -> NodeOutput:
    """Normalise, resample, mono, and optionally trim silence."""
    return await _preprocess(audio, target_sr, trim_silence)


register_tool("preprocess")(_preprocess)
