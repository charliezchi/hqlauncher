"""Configuration management for hqlauncher."""

import os
import json
import sys

DEFAULT_CONFIG = {
    "scan_roots": ["C:\\"]
}


def get_config_dir() -> str:
    """Get the configuration directory path."""
    appdata = os.environ.get('APPDATA', os.path.expanduser('~'))
    return os.path.join(appdata, 'hqlauncher')


def get_config_path() -> str:
    """Get the full path to the config file."""
    return os.path.join(get_config_dir(), 'config.json')


def load_config() -> dict:
    """Load configuration from file, or return defaults if not exists."""
    config_path = get_config_path()
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            print(f"Warning: Failed to load config ({e}), using defaults.", file=sys.stderr)
            return DEFAULT_CONFIG.copy()
    return DEFAULT_CONFIG.copy()


def save_config(cfg: dict) -> None:
    """Save configuration to file."""
    config_dir = get_config_dir()
    os.makedirs(config_dir, exist_ok=True)
    config_path = get_config_path()
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)
