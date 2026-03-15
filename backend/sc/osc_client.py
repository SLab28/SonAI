"""SuperCollider OSC client wrapper.
Always use this module — never import python-osc directly in tool files.
scsynth: port 57110  |  sclang: port 57120

In the MVP, SuperCollider may not be available. All methods are async-safe
and degrade gracefully (log a warning) if SC is unreachable.
"""
from __future__ import annotations
import logging
import os

logger = logging.getLogger(__name__)

SC_SYNTH_PORT = int(os.environ.get("SC_SYNTH_PORT", "57110"))
SC_LANG_PORT = int(os.environ.get("SC_LANG_PORT", "57120"))
SC_HOST = os.environ.get("SC_HOST", "127.0.0.1")

# Lazy-init to avoid import crash when python-osc is missing
_sc_client = None
_sc_synth_client = None


def _get_lang_client():
    global _sc_client
    if _sc_client is None:
        try:
            from pythonosc.udp_client import SimpleUDPClient
            _sc_client = SimpleUDPClient(SC_HOST, SC_LANG_PORT)
        except Exception as e:
            logger.warning(f"Could not create SC lang client: {e}")
    return _sc_client


def _get_synth_client():
    global _sc_synth_client
    if _sc_synth_client is None:
        try:
            from pythonosc.udp_client import SimpleUDPClient
            _sc_synth_client = SimpleUDPClient(SC_HOST, SC_SYNTH_PORT)
        except Exception as e:
            logger.warning(f"Could not create SC synth client: {e}")
    return _sc_synth_client


async def sc_send(address: str, args: list | None = None) -> None:
    """Send an OSC message to SuperCollider sclang."""
    client = _get_lang_client()
    if client:
        try:
            client.send_message(address, args or [])
        except Exception as e:
            logger.warning(f"OSC send failed ({address}): {e}")
    else:
        logger.info(f"SC not available — would send {address} {args}")


async def sc_send_synth(address: str, args: list | None = None) -> None:
    """Send an OSC message to SuperCollider scsynth."""
    client = _get_synth_client()
    if client:
        try:
            client.send_message(address, args or [])
        except Exception as e:
            logger.warning(f"OSC synth send failed ({address}): {e}")
    else:
        logger.info(f"scsynth not available — would send {address} {args}")
