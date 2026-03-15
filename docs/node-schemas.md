# docs/node-schemas.md — SonAI Node Type Schemas

All tools must return `NodeOutput`. All inputs must use typed schemas from this file.

---

## NodeOutput (universal — every tool returns this)
```typescript
{
  node_id: string          // assigned by backend graph module
  node_type: string        // e.g. "STFT"
  data: Record<string, any> // type-specific payload (see below)
  artifact: {
    type: "image/png" | "audio/wav" | "application/json" | "none"
    content: string | null  // base64 encoded
    mime_type: string
  }
  summary: string          // one sentence, must include key numbers
}
```

---

## AudioBuffer
```typescript
{
  samples: string          // base64 float32 array
  sr: number               // sample rate Hz
  channels: number         // 1 = mono
  duration_s: number
  file_path: string | null
}
```

## STFTFrame
```typescript
{
  magnitude: number[][]    // shape [n_fft/2+1, n_frames]
  phase: number[][]
  sr: number
  n_fft: number
  hop_length: number
  freq_bins: number[]      // Hz per bin
  time_frames: number[]    // seconds per frame
}
```

## HarmonicPercussiveSplit
```typescript
{
  harmonic: AudioBuffer
  percussive: AudioBuffer
  margin: number
}
```

## SpectralFeatureVector
```typescript
{
  centroid_mean: number    // Hz
  centroid_std: number
  rolloff_mean: number     // Hz (85% energy rolloff)
  flatness_mean: number    // 0–1, 1=white noise
  bandwidth_mean: number   // Hz
  contrast_bands: number[] // 7 values
  zcr_mean: number
  zcr_std: number
  frame_times: number[]
  per_frame_centroid: number[]
}
```

## TemporalFeatureVector
```typescript
{
  rms_mean: number
  rms_std: number
  loudness_lufs: number
  dynamic_range_db: number
  envelope: number[]       // frame-level RMS
  envelope_times: number[]
}
```

## EventList
```typescript
{
  onsets_s: number[]
  onset_strength: number[]
  bpm: number
  beat_times_s: number[]
  transient_density: number  // onsets per second
  beat_regularity: number    // 0–1
}
```

## PitchTrack
```typescript
{
  times_s: number[]
  frequencies_hz: number[]
  confidence: number[]
  dominant_pitch_hz: number
  hpcp: number[]           // 12-bin harmonic pitch class profile
  key: string              // e.g. "C"
  scale: string            // "major" | "minor" | "unknown"
  key_confidence: number
}
```

## MFCCMatrix
```typescript
{
  coefficients: number[][]  // shape [n_mfcc, n_frames]
  n_mfcc: number
  mean_vector: number[]     // per-coefficient mean
  std_vector: number[]
}
```

## ChromaMatrix
```typescript
{
  chroma: number[][]        // shape [12, n_frames]
  pitch_classes: string[]   // ["C","C#","D",...]
  mean_vector: number[]
  dominant_class: string
}
```

## SegmentMap
```typescript
{
  boundaries_s: number[]
  labels: string[]
  n_segments: number
  segment_features: SpectralFeatureVector[]  // one per segment
}
```

## ScenePlan
```typescript
{
  texture_profile: {
    density: "sparse" | "medium" | "dense"
    brightness: "dark" | "neutral" | "bright"
    noisiness: number        // 0–1
    stability: "stable" | "evolving" | "turbulent"
    space: "intimate" | "room" | "expansive"
  }
  pitched_profile: {
    dominant_pitch_hz: number
    key: string
    harmonic_complexity: "simple" | "modal" | "complex"
    instrument_role: "drone" | "melodic" | "percussive" | "pad"
  }
  rhythm_profile: {
    bpm: number
    regularity: "arrhythmic" | "loose" | "strict"
    onset_density: number
  }
  flow_targets: {
    binaural_beat_hz: number  // e.g. 40.0 for gamma
    carrier_hz: number        // e.g. 110.0
    target_band: "delta" | "theta" | "alpha" | "beta" | "gamma"
  }
  semantic_label: string
}
```

## SCJob
```typescript
{
  id: string               // uuid
  synthdef: string         // SynthDef name in SC
  params: Record<string, number>
  duration_s: number
  status: "queued" | "playing" | "complete" | "error"
}
```
