"""Shared helpers for audio tool files."""
from __future__ import annotations
import base64
import io
import numpy as np


def decode_audio_buffer(audio_data: dict) -> tuple[np.ndarray, int]:
    """Decode an AudioBuffer dict → (samples_array, sample_rate)."""
    buf = base64.b64decode(audio_data["samples"])
    samples = np.load(io.BytesIO(buf), allow_pickle=False)
    return samples.astype(np.float32), int(audio_data["sr"])


def encode_samples(y: np.ndarray) -> str:
    """Encode a float32 numpy array → base64 string."""
    buf = io.BytesIO()
    np.save(buf, y.astype(np.float32))
    return base64.b64encode(buf.getvalue()).decode()


def fig_to_b64(fig) -> str:
    """Convert a matplotlib figure to base64 PNG string."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=80)
    import matplotlib.pyplot as plt
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode()
