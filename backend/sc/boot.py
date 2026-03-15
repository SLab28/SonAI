"""SuperCollider server boot script.
Usage: python -m backend.sc.boot

In the MVP, this provides a graceful fallback if SC is not installed.
"""
import logging
import os
import subprocess
import sys

logger = logging.getLogger(__name__)

SYNTHDEF_DIR = os.path.join(os.path.dirname(__file__), "synthdefs")


def boot_sc():
    """Attempt to boot scsynth. Logs warning if unavailable."""
    try:
        result = subprocess.run(
            ["scsynth", "-u", "57110"],
            capture_output=True,
            timeout=5,
        )
        logger.info("scsynth started on port 57110")
    except FileNotFoundError:
        logger.warning(
            "scsynth not found — SuperCollider is not installed. "
            "Generation tools will queue SCJobs but not render audio."
        )
    except subprocess.TimeoutExpired:
        logger.info("scsynth appears to be running (timeout = still alive)")
    except Exception as e:
        logger.warning(f"Could not boot scsynth: {e}")


def load_synthdefs():
    """Load all .scd SynthDef files via sclang (if available)."""
    if not os.path.isdir(SYNTHDEF_DIR):
        logger.info("No synthdefs directory found.")
        return
    for fname in sorted(os.listdir(SYNTHDEF_DIR)):
        if fname.endswith(".scd"):
            path = os.path.join(SYNTHDEF_DIR, fname)
            logger.info(f"Loading SynthDef: {fname}")
            try:
                subprocess.run(
                    ["sclang", path],
                    capture_output=True,
                    timeout=10,
                )
            except FileNotFoundError:
                logger.warning(f"sclang not available — cannot load {fname}")
            except Exception as e:
                logger.warning(f"Error loading {fname}: {e}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    boot_sc()
    load_synthdefs()
    print("SC boot complete (check logs for any warnings).")
