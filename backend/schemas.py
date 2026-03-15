"""SonAI Pydantic schemas — canonical type definitions.
All tools must import from this module. See docs/node-schemas.md for full reference.
"""
from pydantic import BaseModel
from typing import Any, Literal, Optional


class AudioBuffer(BaseModel):
    samples: str           # base64 float32 array
    sr: int = 22050
    channels: int = 1
    duration_s: float
    file_path: Optional[str] = None


class STFTFrame(BaseModel):
    magnitude: list[list[float]]
    phase: list[list[float]]
    sr: int
    n_fft: int
    hop_length: int
    freq_bins: list[float]
    time_frames: list[float]


class HarmonicPercussiveSplit(BaseModel):
    harmonic: AudioBuffer
    percussive: AudioBuffer
    margin: float


class SpectralFeatureVector(BaseModel):
    centroid_mean: float
    centroid_std: float
    rolloff_mean: float
    flatness_mean: float
    bandwidth_mean: float
    contrast_bands: list[float]
    zcr_mean: float
    zcr_std: float
    frame_times: list[float]
    per_frame_centroid: list[float]


class TemporalFeatureVector(BaseModel):
    rms_mean: float
    rms_std: float
    loudness_lufs: float
    dynamic_range_db: float
    envelope: list[float]
    envelope_times: list[float]


class EventList(BaseModel):
    onsets_s: list[float]
    onset_strength: list[float]
    bpm: float
    beat_times_s: list[float]
    transient_density: float
    beat_regularity: float = 0.0


class PitchTrack(BaseModel):
    times_s: list[float]
    frequencies_hz: list[float]
    confidence: list[float]
    dominant_pitch_hz: float
    hpcp: list[float]
    key: str
    scale: str
    key_confidence: float = 0.0


class MFCCMatrix(BaseModel):
    coefficients: list[list[float]]
    n_mfcc: int
    mean_vector: list[float]
    std_vector: list[float]


class ChromaMatrix(BaseModel):
    chroma: list[list[float]]
    pitch_classes: list[str]
    mean_vector: list[float]
    dominant_class: str


class SegmentMap(BaseModel):
    boundaries_s: list[float]
    labels: list[str]
    n_segments: int
    segment_features: list[dict[str, Any]]


class TextureProfile(BaseModel):
    density: Literal["sparse", "medium", "dense"]
    brightness: Literal["dark", "neutral", "bright"]
    noisiness: float
    stability: Literal["stable", "evolving", "turbulent"]
    space: Literal["intimate", "room", "expansive"]


class PitchedProfile(BaseModel):
    dominant_pitch_hz: float
    key: str
    harmonic_complexity: Literal["simple", "modal", "complex"]
    instrument_role: Literal["drone", "melodic", "percussive", "pad"]


class RhythmProfile(BaseModel):
    bpm: float
    regularity: Literal["arrhythmic", "loose", "strict"]
    onset_density: float


class FlowTargets(BaseModel):
    binaural_beat_hz: float = 40.0
    carrier_hz: float = 110.0
    target_band: Literal["delta", "theta", "alpha", "beta", "gamma"] = "gamma"


class ScenePlan(BaseModel):
    texture_profile: TextureProfile
    pitched_profile: PitchedProfile
    rhythm_profile: RhythmProfile
    flow_targets: FlowTargets
    semantic_label: str


class NodeArtifact(BaseModel):
    type: Literal["image/png", "audio/wav", "application/json", "none"]
    content: Optional[str] = None  # base64
    mime_type: str = "none"


class NodeOutput(BaseModel):
    node_id: str = ""
    node_type: str
    data: dict[str, Any]
    artifact: NodeArtifact
    summary: str


class SCJob(BaseModel):
    id: str
    synthdef: str
    params: dict[str, float]
    duration_s: float
    status: Literal["queued", "playing", "complete", "error"] = "queued"
