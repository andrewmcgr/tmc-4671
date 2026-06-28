from typing import Any

from . import tmc4671


def load_config_prefix(config: Any) -> Any:
    """Load the TMC4671 plugin.

    Args:
        config: The Klipper/Kalico configuration object.

    Returns:
        The loaded TMC4671 plugin instance.
    """
    return tmc4671.load_config_prefix(config)
