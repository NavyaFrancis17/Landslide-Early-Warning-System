"""
Configuration Loader Module.

Provides robust reading and parsing of project YAML configuration files.
"""

import os
from pathlib import Path
from typing import Any, Dict, Union
import yaml


def load_config(config_path: Union[str, Path] = "config.yaml") -> Dict[str, Any]:
    """
    Loads and parses the project YAML configuration file.

    Args:
        config_path: File path to the configuration YAML file.

    Returns:
        Dict[str, Any]: Parsed configuration dictionary.

    Raises:
        FileNotFoundError: If the configuration file does not exist.
        ValueError: If the configuration file is empty or invalid YAML.
    """
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(
            f"Configuration file not found at: {path.resolve()}"
        )

    try:
        with open(path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
    except yaml.YAMLError as exc:
        raise ValueError(f"Error parsing configuration YAML file: {exc}") from exc

    if not isinstance(config, dict):
        raise ValueError(
            f"Invalid configuration format in {path}. Expected key-value dictionary."
        )

    return config
