"""SonAI FastMCP Tool Server — registers all analysis and generation tools.
This module imports the mcp instance and all tools so they get registered.
"""
from backend.mcp_instance import mcp  # noqa: F401

# Analysis tools (Phase 1) — importing registers them with MCP
from backend.tools.load_audio import load_audio  # noqa: F401
from backend.tools.preprocess import preprocess  # noqa: F401
from backend.tools.stft import stft  # noqa: F401
from backend.tools.hpss import hpss  # noqa: F401
from backend.tools.spectral_stats import spectral_stats  # noqa: F401
from backend.tools.temporal_stats import temporal_stats  # noqa: F401
from backend.tools.onsets import onsets  # noqa: F401
from backend.tools.pitch_tonal import pitch_tonal  # noqa: F401
from backend.tools.mfcc import mfcc  # noqa: F401
from backend.tools.chroma import chroma  # noqa: F401
from backend.tools.segment_map import segment_map  # noqa: F401
from backend.tools.insight_composer import insight_composer  # noqa: F401

# Generation tools (Phase 2)
from backend.generation.binaural_beat import binaural_beat_gen  # noqa: F401
from backend.generation.texture_layer import texture_layer  # noqa: F401
from backend.generation.instrument_layer import instrument_layer  # noqa: F401
from backend.generation.granular_cloud import granular_cloud  # noqa: F401
from backend.generation.mix_render import mix_render  # noqa: F401
