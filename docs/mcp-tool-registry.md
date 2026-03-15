# docs/mcp-tool-registry.md — MCP Tool Registry

All tools registered in backend/mcp_server.py. Update this file when adding tools.

---

## load_audio
- File: backend/tools/load_audio.py
- Input: file_path: str, sr: int = 22050, mono: bool = True
- Output: NodeOutput → data: AudioBuffer
- Summary: Loads an audio file from disk and returns a normalised mono AudioBuffer.

## preprocess
- File: backend/tools/preprocess.py
- Input: audio: AudioBuffer, target_sr: int = 22050, trim_silence: bool = True
- Output: NodeOutput → data: AudioBuffer
- Summary: Normalises amplitude, resamples, converts to mono, optionally trims silence.

## stft
- File: backend/tools/stft.py
- Input: audio: AudioBuffer, n_fft: int = 2048, hop_length: int = 512
- Output: NodeOutput → data: STFTFrame, artifact: spectrogram PNG
- Summary: Computes STFT magnitude and phase. Returns frequency/time grid + spectrogram image.

## hpss
- File: backend/tools/hpss.py
- Input: audio: AudioBuffer, margin: float = 1.0
- Output: NodeOutput → data: HarmonicPercussiveSplit
- Summary: Separates harmonic (tonal) and percussive (transient) components.

## spectral_stats
- File: backend/tools/spectral_stats.py
- Input: stft_frame: STFTFrame
- Output: NodeOutput → data: SpectralFeatureVector, artifact: centroid overlay PNG
- Summary: Computes centroid, rolloff, flatness, bandwidth, contrast per frame.

## temporal_stats
- File: backend/tools/temporal_stats.py
- Input: audio: AudioBuffer
- Output: NodeOutput → data: TemporalFeatureVector, artifact: RMS envelope PNG
- Summary: Computes RMS energy, loudness (LUFS), dynamic range, and frame envelope.

## onsets
- File: backend/tools/onsets.py
- Input: audio: AudioBuffer, method: str = "default"
- Output: NodeOutput → data: EventList, artifact: onset markers on waveform PNG
- Summary: Detects onsets and beats using Aubio. Returns timestamps, BPM, regularity.

## pitch_tonal
- File: backend/tools/pitch_tonal.py
- Input: audio: AudioBuffer, method: str = "yin"
- Output: NodeOutput → data: PitchTrack, artifact: pitch track plot PNG
- Summary: Tracks pitch using Aubio YIN, computes HPCP and key via Essentia.

## mfcc
- File: backend/tools/mfcc.py
- Input: audio: AudioBuffer, n_mfcc: int = 13
- Output: NodeOutput → data: MFCCMatrix, artifact: MFCC heatmap PNG
- Summary: Computes Mel-frequency cepstral coefficients. Returns matrix + per-coeff statistics.

## chroma
- File: backend/tools/chroma.py
- Input: stft_frame: STFTFrame
- Output: NodeOutput → data: ChromaMatrix, artifact: chroma plot PNG
- Summary: Computes CQT chroma features. Reveals pitch class distribution and tonal centre.

## segment_map
- File: backend/tools/segment_map.py
- Input: spectral: SpectralFeatureVector
- Output: NodeOutput → data: SegmentMap, artifact: segment boundary plot PNG
- Summary: Segments audio into structurally homogeneous sections using librosa.

## insight_composer
- File: backend/tools/insight_composer.py
- Input: spectral: SpectralFeatureVector, temporal: TemporalFeatureVector, events: EventList, pitch: PitchTrack, segments: SegmentMap
- Output: NodeOutput → data: ScenePlan
- Summary: Synthesises all analysis outputs into a ScenePlan for the generation pipeline.

---

## Generation Tools

## binaural_beat_gen
- File: backend/generation/binaural_beat.py
- Input: carrier_hz: float = 110.0, beat_hz: float = 40.0, duration_s: float = 30.0, amplitude: float = 0.3
- Output: NodeOutput → data: SCJob
- Summary: Queues a binaural beat layer in SuperCollider at the given carrier and interval frequency.

## texture_layer
- File: backend/generation/texture_layer.py
- Input: scene: ScenePlan, duration_s: float = 30.0
- Output: NodeOutput → data: SCJob
- Summary: Generates a procedural texture layer in SC based on ScenePlan texture_profile.

## instrument_layer
- File: backend/generation/instrument_layer.py
- Input: scene: ScenePlan, duration_s: float = 30.0, instrument_type: str = "pad"
- Output: NodeOutput → data: SCJob
- Summary: Renders an instrument layer (pad, drone, melodic) using SC sample playback and synthesis.

## granular_cloud
- File: backend/generation/granular_cloud.py
- Input: audio: AudioBuffer, density: float = 0.5, pitch_variation: float = 0.1, duration_s: float = 30.0
- Output: NodeOutput → data: SCJob
- Summary: Creates a granular cloud from source audio. Density and pitch_variation control character.

## mix_render
- File: backend/generation/mix_render.py
- Input: jobs: SCJob[], output_path: str, duration_s: float = 120.0
- Output: NodeOutput → data: AudioBuffer (rendered file), artifact: waveform PNG
- Summary: Triggers SuperCollider non-realtime render of all queued SCJobs into a single audio file.
