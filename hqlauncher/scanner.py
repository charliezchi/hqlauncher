"""Scan disk for HqFpga installations."""

import os
import glob
from typing import List, Dict

from .utils import parse_version_info, version_sort_key


def find_versions_in_root(root_dir: str) -> List[Dict]:
    """
    Scan a single root directory for HqFpga versions.
    
    Returns:
        List of version dicts with keys:
        name, path, main_ver, semver, build, has_hqfpga, has_hqui,
        hqfpga_path, hqui_path
    """
    versions = []
    if not os.path.isdir(root_dir):
        return versions

    pattern = os.path.join(root_dir, 'hqv*_xist_*_win64')
    for dir_path in glob.glob(pattern):
        if not os.path.isdir(dir_path):
            continue

        dir_name = os.path.basename(dir_path)
        info = parse_version_info(dir_name)
        if info is None:
            continue

        main_ver, semver, build = info

        hqfpga_path = os.path.join(dir_path, 'build', 'win_x64', 'bin', 'hqfpga.exe')
        hqui_path = os.path.join(dir_path, 'build', 'win_x64', 'hqui', 'hqui.exe')

        versions.append({
            'name': dir_name,
            'path': dir_path,
            'main_ver': main_ver,
            'semver': semver,
            'build': build,
            'has_hqfpga': os.path.exists(hqfpga_path),
            'has_hqui': os.path.exists(hqui_path),
            'hqfpga_path': hqfpga_path,
            'hqui_path': hqui_path,
        })

    # Sort descending (newest first)
    versions.sort(key=version_sort_key, reverse=True)
    return versions


def scan_all(config: dict) -> List[Dict]:
    """
    Scan all configured root directories and merge results.
    
    Returns:
        Deduplicated and sorted list of all discovered versions.
    """
    all_versions = []
    seen_paths = set()

    for root in config.get('scan_roots', []):
        for v in find_versions_in_root(root):
            norm_path = os.path.normcase(os.path.normpath(v['path']))
            if norm_path not in seen_paths:
                seen_paths.add(norm_path)
                all_versions.append(v)

    all_versions.sort(key=version_sort_key, reverse=True)
    return all_versions
