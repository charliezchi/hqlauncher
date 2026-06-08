"""Launch HqFpga tools."""

import os
import subprocess
import sys
from typing import Dict


def launch_tool(version: Dict, tool: str, extra_args: list) -> None:
    """
    Launch hqfpga or hqui for a given version.

    Args:
        version: Version dict from scanner.
        tool: 'hqfpga' or 'hqui'.
        extra_args: Additional command-line arguments to pass to the tool.
    """
    if tool == 'hqfpga':
        exe_path = version['hqfpga_path']
        if not version['has_hqfpga']:
            print(f"Error: hqfpga.exe not found in {version['path']}")
            sys.exit(1)
    elif tool == 'hqui':
        exe_path = version['hqui_path']
        if not version['has_hqui']:
            print(f"Error: hqui.exe not found in {version['path']}")
            sys.exit(1)
    else:
        print(f"Error: Unknown tool '{tool}'")
        sys.exit(1)

    if not os.path.exists(exe_path):
        print(f"Error: Executable not found: {exe_path}")
        sys.exit(1)

    cmd = [exe_path] + extra_args

    try:
        if tool == 'hqui':
            # GUI tool: detach so we don't block the terminal
            creationflags = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
            subprocess.Popen(cmd, creationflags=creationflags, close_fds=True)
            print(f"Launched {tool} v{version['semver']} (build {version['build']})")
        else:
            # CLI tool: run in foreground, inherit stdin/stdout/stderr
            proc = subprocess.Popen(cmd)
            try:
                proc.wait()
            except KeyboardInterrupt:
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait()
                raise
    except Exception as e:
        print(f"Error launching {tool}: {e}")
        sys.exit(1)


def open_path(path: str) -> None:
    """Open a file or directory with the default application."""
    if not os.path.exists(path):
        print(f"Error: Path not found: {path}")
        sys.exit(1)
    try:
        os.startfile(path)
    except Exception as e:
        print(f"Error opening path: {e}")
        sys.exit(1)


def print_env(version: Dict) -> None:
    """Print environment variables for a version."""
    print(f"HQFPGA_PATH={version['path']}")
