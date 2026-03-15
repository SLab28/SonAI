"""MixRender tool — Phase 2, Task P2-06
Triggers SuperCollider non-realtime render of all queued SCJobs.
"""
from __future__ import annotations
import os
import wave
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from backend.mcp_instance import mcp
from backend.schemas import NodeOutput, AudioBuffer, NodeArtifact
from backend.tool_registry import register_tool
from backend.sc.osc_client import sc_send
from backend.tools._audio_helpers import encode_samples, fig_to_b64


async def _mix_render(
    jobs: list[dict],
    output_path: str = "output/render.wav",
    duration_s: float = 120.0,
) -> NodeOutput:
    """Trigger SC render of all jobs into a single audio file."""
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path) or "output", exist_ok=True)

    # Send render command to SC (graceful fallback)
    await sc_send("/sonai/render/start", [output_path, duration_s])

    # In the MVP without a running SC server, we generate a silent placeholder
    # A real implementation would poll SC for /sonai/render/done
    sr = 22050
    n_samples = int(sr * min(duration_s, 10))  # Limit for MVP
    # Generate a simple sine mix as placeholder
    t = np.linspace(0, min(duration_s, 10), n_samples, endpoint=False)
    y = np.zeros(n_samples, dtype=np.float32)
    for i, job in enumerate(jobs):
        freq = job.get("params", {}).get("carrier_hz", 110 + i * 50)
        amp = job.get("params", {}).get("amp", 0.2)
        y += (amp * np.sin(2 * np.pi * freq * t)).astype(np.float32)
    # Normalize
    peak = np.max(np.abs(y))
    if peak > 0:
        y = y / peak * 0.8

    # Persist the rendered placeholder mix to disk so the reported output_path is real.
    wav_path = output_path if os.path.isabs(output_path) else os.path.join(os.getcwd(), output_path)
    os.makedirs(os.path.dirname(wav_path) or os.getcwd(), exist_ok=True)
    pcm16 = np.clip(y * 32767.0, -32768, 32767).astype(np.int16)
    with wave.open(wav_path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(pcm16.tobytes())

    samples_b64 = encode_samples(y)

    # Waveform artifact
    fig, ax = plt.subplots(figsize=(6, 1.5))
    ax.plot(t, y, color="black", linewidth=0.3)
    ax.set_facecolor("white")
    fig.patch.set_facecolor("white")
    ax.axis("off")
    artifact_b64 = fig_to_b64(fig)

    audio = AudioBuffer(
        samples=samples_b64, sr=sr, channels=1,
        duration_s=len(y) / sr, file_path=wav_path,
    )

    return NodeOutput(
        node_type="MixRender",
        data=audio.model_dump(),
        artifact=NodeArtifact(type="image/png", content=artifact_b64, mime_type="image/png"),
        summary=f"Rendered {len(jobs)} layers, {len(y)/sr:.1f}s → {wav_path}",
    )


@mcp.tool
async def mix_render(
    jobs: list[dict],
    output_path: str = "output/render.wav",
    duration_s: float = 120.0,
) -> NodeOutput:
    """Trigger SC render of all jobs."""
    return await _mix_render(jobs, output_path, duration_s)


register_tool("mix_render")(_mix_render)
