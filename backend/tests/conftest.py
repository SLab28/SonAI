"""Shared fixtures for backend tests."""
import pytest
import numpy as np
import base64
import io
import os
import tempfile


@pytest.fixture
def sample_audio_buffer():
    """Create a synthetic AudioBuffer dict for testing."""
    sr = 22050
    duration = 2.0
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    # Mix of sine waves for interesting spectral content
    y = (0.5 * np.sin(2 * np.pi * 440 * t) +
         0.3 * np.sin(2 * np.pi * 880 * t) +
         0.1 * np.random.randn(len(t))).astype(np.float32)
    # Normalize
    y = y / np.max(np.abs(y))

    buf = io.BytesIO()
    np.save(buf, y)
    samples_b64 = base64.b64encode(buf.getvalue()).decode()

    return {
        "samples": samples_b64,
        "sr": sr,
        "channels": 1,
        "duration_s": duration,
        "file_path": None,
    }


@pytest.fixture
def sample_wav_file():
    """Create a temporary WAV file for testing load_audio."""
    try:
        import soundfile as sf
    except ImportError:
        sf = None

    sr = 22050
    duration = 1.0
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    y = (0.5 * np.sin(2 * np.pi * 440 * t)).astype(np.float32)

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        path = f.name
        if sf:
            sf.write(path, y, sr)
        else:
            # Write a minimal WAV without soundfile
            import struct
            n_samples = len(y)
            data_size = n_samples * 2  # 16-bit
            samples_16 = (y * 32767).astype(np.int16)
            with open(path, 'wb') as wf:
                wf.write(b'RIFF')
                wf.write(struct.pack('<I', 36 + data_size))
                wf.write(b'WAVE')
                wf.write(b'fmt ')
                wf.write(struct.pack('<I', 16))  # chunk size
                wf.write(struct.pack('<H', 1))   # PCM
                wf.write(struct.pack('<H', 1))   # mono
                wf.write(struct.pack('<I', sr))   # sample rate
                wf.write(struct.pack('<I', sr * 2))  # byte rate
                wf.write(struct.pack('<H', 2))   # block align
                wf.write(struct.pack('<H', 16))  # bits per sample
                wf.write(b'data')
                wf.write(struct.pack('<I', data_size))
                wf.write(samples_16.tobytes())

    yield path
    os.unlink(path)


@pytest.fixture
def sample_spectral_data():
    """Sample SpectralFeatureVector dict for testing."""
    return {
        "centroid_mean": 2500.0,
        "centroid_std": 500.0,
        "rolloff_mean": 4000.0,
        "flatness_mean": 0.2,
        "bandwidth_mean": 1800.0,
        "contrast_bands": [10.0, 15.0, 20.0, 18.0, 12.0, 8.0, 5.0],
        "zcr_mean": 0.05,
        "zcr_std": 0.02,
        "frame_times": [0.0, 0.5, 1.0, 1.5, 2.0],
        "per_frame_centroid": [2400.0, 2500.0, 2600.0, 2450.0, 2550.0],
    }


@pytest.fixture
def sample_temporal_data():
    return {
        "rms_mean": 0.15,
        "rms_std": 0.03,
        "loudness_lufs": -20.0,
        "dynamic_range_db": 15.0,
        "envelope": [0.1, 0.15, 0.2, 0.12, 0.18],
        "envelope_times": [0.0, 0.5, 1.0, 1.5, 2.0],
    }


@pytest.fixture
def sample_events_data():
    return {
        "onsets_s": [0.5, 1.0, 1.5],
        "onset_strength": [0.8, 0.6, 0.7],
        "bpm": 120.0,
        "beat_times_s": [0.5, 1.0, 1.5, 2.0],
        "transient_density": 1.5,
        "beat_regularity": 0.8,
    }


@pytest.fixture
def sample_pitch_data():
    return {
        "times_s": [0.0, 0.5, 1.0],
        "frequencies_hz": [440.0, 440.0, 440.0],
        "confidence": [0.9, 0.8, 0.85],
        "dominant_pitch_hz": 440.0,
        "hpcp": [0.1] * 12,
        "key": "A",
        "scale": "major",
        "key_confidence": 0.75,
    }


@pytest.fixture
def sample_segments_data():
    return {
        "boundaries_s": [0.0, 1.0, 2.0],
        "labels": ["section_0", "section_1"],
        "n_segments": 2,
        "segment_features": [
            {"centroid_mean": 2500, "flatness_mean": 0.2},
            {"centroid_mean": 2800, "flatness_mean": 0.3},
        ],
    }
