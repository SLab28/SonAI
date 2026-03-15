"""Tests for Phase 1 analysis tools and Phase 2 generation tools."""
import pytest
import asyncio

# Import tool functions directly (not MCP-wrapped versions)
from backend.tools.load_audio import _load_audio
from backend.tools.preprocess import _preprocess
from backend.tools.stft import _stft
from backend.tools.hpss import _hpss
from backend.tools.spectral_stats import _spectral_stats
from backend.tools.temporal_stats import _temporal_stats
from backend.tools.onsets import _onsets
from backend.tools.pitch_tonal import _pitch_tonal
from backend.tools.mfcc import _mfcc
from backend.tools.chroma import _chroma
from backend.tools.segment_map import _segment_map
from backend.tools.insight_composer import _insight_composer
from backend.generation.binaural_beat import _binaural_beat_gen
from backend.generation.texture_layer import _texture_layer
from backend.generation.instrument_layer import _instrument_layer
from backend.generation.granular_cloud import _granular_cloud
from backend.generation.mix_render import _mix_render


# ── Phase 1: Analysis Tools ──────────────────────────────────────────

@pytest.mark.asyncio
async def test_load_audio(sample_wav_file):
    result = await _load_audio(sample_wav_file)
    assert result.node_type == "LoadAudio"
    assert result.data["sr"] == 22050
    assert result.data["channels"] == 1
    assert result.data["duration_s"] > 0
    assert result.artifact.type == "image/png"
    assert result.summary.startswith("Loaded")


@pytest.mark.asyncio
async def test_preprocess(sample_audio_buffer):
    result = await _preprocess(sample_audio_buffer)
    assert result.node_type == "Preprocess"
    assert result.data["sr"] == 22050
    assert result.data["channels"] == 1
    assert "Preprocessed" in result.summary


@pytest.mark.asyncio
async def test_stft(sample_audio_buffer):
    result = await _stft(sample_audio_buffer)
    assert result.node_type == "STFT"
    assert "n_fft" in result.data
    assert result.data["n_fft"] == 2048
    assert result.artifact.type == "image/png"


@pytest.mark.asyncio
async def test_hpss(sample_audio_buffer):
    result = await _hpss(sample_audio_buffer)
    assert result.node_type == "HPSS"
    assert "harmonic" in result.data
    assert "percussive" in result.data
    assert result.data["margin"] == 1.0


@pytest.mark.asyncio
async def test_spectral_stats(sample_audio_buffer):
    result = await _spectral_stats(sample_audio_buffer)
    assert result.node_type == "SpectralStats"
    assert "centroid_mean" in result.data
    assert "flatness_mean" in result.data
    assert "zcr_mean" in result.data
    assert result.artifact.type == "image/png"


@pytest.mark.asyncio
async def test_temporal_stats(sample_audio_buffer):
    result = await _temporal_stats(sample_audio_buffer)
    assert result.node_type == "TemporalStats"
    assert "rms_mean" in result.data
    assert "dynamic_range_db" in result.data
    assert result.artifact.type == "image/png"


@pytest.mark.asyncio
async def test_onsets(sample_audio_buffer):
    result = await _onsets(sample_audio_buffer)
    assert result.node_type == "Onsets"
    assert "bpm" in result.data
    assert "onsets_s" in result.data
    assert "transient_density" in result.data


@pytest.mark.asyncio
async def test_pitch_tonal(sample_audio_buffer):
    result = await _pitch_tonal(sample_audio_buffer)
    assert result.node_type == "PitchTonal"
    assert "dominant_pitch_hz" in result.data
    assert "key" in result.data
    assert "hpcp" in result.data
    assert len(result.data["hpcp"]) == 12


@pytest.mark.asyncio
async def test_mfcc(sample_audio_buffer):
    result = await _mfcc(sample_audio_buffer)
    assert result.node_type == "MFCC"
    assert result.data["n_mfcc"] == 13
    assert "mean_vector" in result.data
    assert result.artifact.type == "image/png"


@pytest.mark.asyncio
async def test_chroma(sample_audio_buffer):
    result = await _chroma(sample_audio_buffer)
    assert result.node_type == "Chroma"
    assert "dominant_class" in result.data
    assert "pitch_classes" in result.data
    assert len(result.data["pitch_classes"]) == 12


@pytest.mark.asyncio
async def test_segment_map(sample_spectral_data):
    result = await _segment_map(sample_spectral_data)
    assert result.node_type == "SegmentMap"
    assert "boundaries_s" in result.data
    assert "n_segments" in result.data
    assert result.data["n_segments"] >= 1


@pytest.mark.asyncio
async def test_insight_composer(
    sample_spectral_data, sample_temporal_data, sample_events_data,
    sample_pitch_data, sample_segments_data
):
    result = await _insight_composer(
        sample_spectral_data, sample_temporal_data,
        sample_events_data, sample_pitch_data, sample_segments_data
    )
    assert result.node_type == "InsightComposer"
    data = result.data
    assert "texture_profile" in data
    assert "pitched_profile" in data
    assert "rhythm_profile" in data
    assert "flow_targets" in data
    assert "semantic_label" in data
    assert data["texture_profile"]["density"] in ("sparse", "medium", "dense")
    assert data["flow_targets"]["target_band"] in ("delta", "theta", "alpha", "beta", "gamma")


# ── Phase 2: Generation Tools ────────────────────────────────────────

@pytest.mark.asyncio
async def test_binaural_beat_gen():
    result = await _binaural_beat_gen(carrier_hz=110, beat_hz=40, duration_s=10)
    assert result.node_type == "BinauralBeatGen"
    assert result.data["synthdef"] == "SonaiBinaural"
    assert result.data["status"] == "queued"
    assert result.data["duration_s"] == 10


@pytest.mark.asyncio
async def test_texture_layer():
    scene = {
        "texture_profile": {"density": "sparse", "brightness": "dark"},
        "pitched_profile": {"dominant_pitch_hz": 110},
        "rhythm_profile": {"bpm": 60},
        "flow_targets": {"binaural_beat_hz": 40, "carrier_hz": 110, "target_band": "gamma"},
    }
    result = await _texture_layer(scene, duration_s=10)
    assert result.node_type == "TextureLayer"
    assert result.data["synthdef"] == "SonaiTexture"
    assert result.data["status"] == "queued"


@pytest.mark.asyncio
async def test_instrument_layer():
    scene = {
        "pitched_profile": {"dominant_pitch_hz": 220, "instrument_role": "pad"},
    }
    result = await _instrument_layer(scene, duration_s=10)
    assert result.node_type == "InstrumentLayer"
    assert result.data["synthdef"] in ("SonaiPad", "SonaiDrone")
    assert result.data["status"] == "queued"


@pytest.mark.asyncio
async def test_granular_cloud(sample_audio_buffer):
    result = await _granular_cloud(sample_audio_buffer, density=0.5, pitch_variation=0.1, duration_s=10)
    assert result.node_type == "GranularCloud"
    assert result.data["synthdef"] == "SonaiGranular"
    assert result.data["status"] == "queued"


@pytest.mark.asyncio
async def test_mix_render():
    jobs = [
        {"id": "j1", "synthdef": "SonaiBinaural", "params": {"carrier_hz": 110, "amp": 0.2}, "duration_s": 10, "status": "queued"},
        {"id": "j2", "synthdef": "SonaiTexture", "params": {"density": 0.5, "amp": 0.3}, "duration_s": 10, "status": "queued"},
    ]
    result = await _mix_render(jobs, output_path="output/test_render.wav", duration_s=10)
    assert result.node_type == "MixRender"
    assert result.data["sr"] == 22050
    assert result.data["duration_s"] > 0
    assert result.artifact.type == "image/png"
