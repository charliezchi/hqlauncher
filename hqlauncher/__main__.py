"""CLI entry point for hqlauncher."""

import argparse
import json
import os
import sys

from . import config, scanner, launcher


def cmd_list(args):
    """List all discovered versions."""
    versions = scanner.scan_all(config.load_config())
    if not versions:
        print("No HqFpga versions found.")
        print("Tip: Check your scan_roots configuration with 'hqlauncher config show'")
        return

    print(f"{'#':<4} {'Version':<10} {'Build':<12} {'Name':<40}")
    print("-" * 70)
    for i, v in enumerate(versions, 1):
        marker = "  <-- latest" if i == 1 else ""
        print(f"{i:<4} {v['semver']:<10} {v['build']:<12} {v['name']:<40}{marker}")


def _cmd_launch_tool(tool, raw_args):
    """Launch hqfpga or hqui with manual argument parsing."""
    versions = scanner.scan_all(config.load_config())
    if not versions:
        print("No HqFpga versions found.")
        print("Tip: Check your scan_roots configuration with 'hqlauncher config show'")
        sys.exit(1)

    matched = None
    extra_args = raw_args

    if raw_args:
        first = raw_args[0]
        # Only exact match by build ID
        for v in versions:
            if first == v['build']:
                matched = v
                extra_args = raw_args[1:]
                break

    if matched is None:
        if raw_args:
            print(f"Version not found: {raw_args[0]}")
            print("Run 'hqlauncher list' to see available versions.")
            sys.exit(1)
        matched = versions[0]
        print(f"Auto-selected latest version: {matched['semver']} (build {matched['build']})", file=sys.stderr, flush=True)

    launcher.launch_tool(matched, tool, extra_args)


def cmd_config(args):
    """Manage configuration."""
    cfg = config.load_config()
    cfg_path = config.get_config_path()

    if args.action is None or args.action == 'show':
        print(f"Config file: {cfg_path}")
        print(json.dumps(cfg, indent=2, ensure_ascii=False))

    elif args.action == 'set-root':
        if not args.value:
            print("Usage: hqlauncher config set-root <path>")
            sys.exit(1)
        path = os.path.abspath(args.value)
        if 'scan_roots' not in cfg:
            cfg['scan_roots'] = []
        if path not in cfg['scan_roots']:
            cfg['scan_roots'].append(path)
        config.save_config(cfg)
        print(f"Config file: {cfg_path}")
        print(f"Added scan root: {path}")

    elif args.action == 'remove-root':
        if not args.value:
            print("Usage: hqlauncher config remove-root <path>")
            sys.exit(1)
        path = args.value
        if 'scan_roots' in cfg and path in cfg['scan_roots']:
            cfg['scan_roots'].remove(path)
            config.save_config(cfg)
            print(f"Config file: {cfg_path}")
            print(f"Removed scan root: {path}")
        else:
            print(f"Config file: {cfg_path}")
            print(f"Root not found in config: {path}")

    elif args.action == 'init':
        config.save_config(config.DEFAULT_CONFIG)
        print(f"Config file: {cfg_path}")
        print("Configuration reset to defaults.")


def main():
    parser = argparse.ArgumentParser(
        prog='hqlauncher',
        description='HqFpga Version Launcher for XiST FPGA tools',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=r'''examples:
  hqlauncher                            Launch the latest hqui (GUI)
  hqlauncher hqui                       Same as above (explicit)
  hqlauncher list                       List all discovered versions
  hqlauncher hqfpga                     Launch the latest hqfpga (CLI, foreground)
  hqlauncher hqfpga FT041226            Launch hqfpga by build ID
  hqlauncher hqui FT041226              Launch hqui by build ID
  hqlauncher config                     Show current configuration
  hqlauncher config show                Same as above
  hqlauncher config set-root "C:\hq"    Add a scan root directory
  hqlauncher config remove-root "C:\hq" Remove a scan root directory
  hqlauncher config init                Reset configuration to defaults'''
    )
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # list
    p_list = subparsers.add_parser('list', aliases=['ls'], help='List all discovered versions')
    p_list.set_defaults(func=cmd_list)

    # hqfpga - no arguments defined here; we parse manually to support --args
    p_hqfpga = subparsers.add_parser('hqfpga', help='Launch hqfpga CLI tool', add_help=False)

    # hqui - no arguments defined here; we parse manually to support --args
    p_hqui = subparsers.add_parser('hqui', help='Launch hqui GUI tool', add_help=False)

    # config
    p_config = subparsers.add_parser('config', help='Manage configuration')
    p_config.add_argument('action', nargs='?', choices=['show', 'set-root', 'remove-root', 'init'],
                         default=None, help='Config action (default: show)')
    p_config.add_argument('value', nargs='?', help='Value for set/remove actions')
    p_config.set_defaults(func=cmd_config)

    args, unknown = parser.parse_known_args()

    if not args.command:
        _cmd_launch_tool('hqui', [])
        return

    if args.command in ('hqfpga', 'hqui'):
        _cmd_launch_tool(args.command, unknown)
        return

    # For other commands, reject unknown arguments
    if unknown:
        parser.error(f"unrecognized arguments: {' '.join(unknown)}")

    args.func(args)


if __name__ == '__main__':
    main()
