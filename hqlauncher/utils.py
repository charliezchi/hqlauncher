"""Utility functions for version parsing and comparison."""

import re
from typing import Tuple, Optional


def parse_version_info(dir_name: str) -> Optional[Tuple[int, str, str]]:
    """
    Parse directory name like 'hqv3_xist_3.1.1_FT041226_win64'.
    
    Returns:
        Tuple of (main_version, semver, build) or None if not matched.
    """
    pattern = r'^hqv(\d+)_xist_([\d.]+)_(.+)_win64$'
    m = re.match(pattern, dir_name)
    if m:
        return int(m.group(1)), m.group(2), m.group(3)
    return None


def semver_to_tuple(semver: str) -> Tuple[int, ...]:
    """Convert semver string '3.1.1' to tuple (3, 1, 1)."""
    parts = semver.split('.')
    return tuple(int(p) for p in parts)


def version_sort_key(v: dict) -> Tuple:
    """
    Return a sort key for version dict.
    Sorts descending by: main_ver, semver tuple, build string.
    """
    s = semver_to_tuple(v['semver'])
    # Pad semver to 4 parts for consistent comparison
    padded = s + (0,) * (4 - len(s)) if len(s) < 4 else s[:4]
    return (v['main_ver'], padded, v['build'])
