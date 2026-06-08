"""CLI entry point for hqlauncher."""

import json
import os
import sys

from . import __version__, config, scanner, launcher


def show_help():
    """Print help message."""
    print("""Usage: hqlauncher [options]

Options:
  -h              Show this help message
  -v              Show version
  -ls             List all discovered versions
  -cfg [action]   Manage configuration (default: show)
  -b <build>      Specify build ID (e.g., FT041226)
  -cmd <file>     Launch hqfpga with cmd file
  -doc            Open user manual
  -cd             Open installation directory in file explorer
  -env            Print installation directory path

Examples:
  hqlauncher                  Launch latest hqui (GUI)
  hqlauncher -b FT041226      Launch hqui with specific build
  hqlauncher -cmd xx.tcl      Launch hqfpga with cmd file
  hqlauncher -b FT041226 -cmd xx.tcl
  hqlauncher -doc             Open user manual
  hqlauncher -cd              Open installation directory
  hqlauncher -env             Print installation directory path
""")


def show_version():
    """Print version."""
    print(__version__)


def cmd_list():
    """List all discovered versions."""
    versions = scanner.scan_all(config.load_config())
    if not versions:
        print("No HqFpga versions found.")
        print("Tip: Check your scan_roots configuration with 'hqlauncher -cfg'")
        return

    print(f"{'#':<4} {'Version':<10} {'Build':<12} {'Name':<40}")
    print("-" * 70)
    for i, v in enumerate(versions, 1):
        marker = "  <-- latest" if i == 1 else ""
        print(f"{i:<4} {v['semver']:<10} {v['build']:<12} {v['name']:<40}{marker}")


def cmd_config(raw_args):
    """Manage configuration."""
    cfg = config.load_config()
    cfg_path = config.get_config_path()

    action = raw_args[0] if raw_args else 'show'
    value = raw_args[1] if len(raw_args) > 1 else None

    if action == 'show':
        print(f"Config file: {cfg_path}")
        print(json.dumps(cfg, indent=2, ensure_ascii=False))

    elif action == 'set-root':
        if not value:
            print("Usage: hqlauncher -cfg set-root <path>")
            sys.exit(1)
        path = os.path.abspath(value)
        if 'scan_roots' not in cfg:
            cfg['scan_roots'] = []
        if path not in cfg['scan_roots']:
            cfg['scan_roots'].append(path)
        config.save_config(cfg)
        print(f"Config file: {cfg_path}")
        print(f"Added scan root: {path}")

    elif action == 'remove-root':
        if not value:
            print("Usage: hqlauncher -cfg remove-root <path>")
            sys.exit(1)
        path = value
        if 'scan_roots' in cfg and path in cfg['scan_roots']:
            cfg['scan_roots'].remove(path)
            config.save_config(cfg)
            print(f"Config file: {cfg_path}")
            print(f"Removed scan root: {path}")
        else:
            print(f"Config file: {cfg_path}")
            print(f"Root not found in config: {path}")

    elif action == 'init':
        config.save_config(config.DEFAULT_CONFIG)
        print(f"Config file: {cfg_path}")
        print("Configuration reset to defaults.")

    else:
        print(f"Unknown config action: {action}")
        print("Valid actions: show, set-root, remove-root, init")
        sys.exit(1)


def _resolve_version(versions, build):
    """Find a version by build ID."""
    if build:
        for v in versions:
            if build == v['build']:
                return v
        print(f"Version not found: {build}")
        print("Run 'hqlauncher -ls' to see available versions.")
        sys.exit(1)
    return versions[0]


def _build_supports_project_open(build: str) -> bool:
    """Check if build >= FT051426 (2026-05-14)."""
    if not (build.startswith('FT') and len(build) == 8):
        return False
    mm = build[2:4]
    dd = build[4:6]
    yy = build[6:8]
    return int(f"20{yy}{mm}{dd}") >= 20260514


def main():
    args = sys.argv[1:]

    # Help
    if '-h' in args:
        show_help()
        return

    # Version
    if '-v' in args:
        show_version()
        return

    # List
    if '-ls' in args:
        cmd_list()
        return

    # Config
    if '-cfg' in args:
        idx = args.index('-cfg')
        cfg_args = args[idx + 1:]
        cmd_config(cfg_args)
        return

    # Parse build ID
    build = None
    i = 0
    while i < len(args):
        if args[i] == '-b':
            if i + 1 < len(args):
                build = args[i + 1]
                i += 2
            else:
                print("Error: -b requires a build ID")
                sys.exit(1)
        else:
            break

    remaining = args[i:]

    # Resolve version early (needed for feature check)
    versions = scanner.scan_all(config.load_config())
    if not versions:
        print("No HqFpga versions found.")
        print("Tip: Check your scan_roots configuration with 'hqlauncher -cfg'")
        sys.exit(1)

    matched = _resolve_version(versions, build)
    if not build:
        print(f"Auto-selected latest version: {matched['semver']} (build {matched['build']})",
              file=sys.stderr, flush=True)

    # Handle utility commands
    if remaining and remaining[0] == '-doc':
        doc_path = matched['doc_chs_path']
        if not matched['has_doc_chs']:
            print(f"Error: User manual not found for build {matched['build']}")
            sys.exit(1)
        launcher.open_path(doc_path)
        print(f"Opened user manual for v{matched['semver']} (build {matched['build']})")
        return

    if remaining and remaining[0] == '-cd':
        launcher.open_path(matched['path'])
        print(f"Opened directory for v{matched['semver']} (build {matched['build']})")
        return

    if remaining and remaining[0] == '-env':
        print(matched['path'])
        return

    # Determine tool mode
    if remaining and remaining[0] == '-cmd':
        tool = 'hqfpga'
        extra_args = remaining  # Pass -cmd and everything after to hqfpga
    else:
        tool = 'hqui'
        if remaining:
            if not any(a.startswith('-') for a in remaining) and _build_supports_project_open(matched['build']):
                extra_args = remaining
            else:
                print(f"Warning: Ignoring unknown arguments: {remaining}")
                extra_args = []
        else:
            extra_args = []

    launcher.launch_tool(matched, tool, extra_args)


if __name__ == '__main__':
    main()
