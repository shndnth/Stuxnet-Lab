#!/usr/bin/env python3
"""
stuxnet-lab -- Stuxnet ICS Attack Simulation Framework
IE4032 Information Warfare
Sri Lanka Institute of Information Technology
"""

import os
import sys
import argparse
import importlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scripts.config import get, reconfigure, load_targets
from utils.colors import red, green, yellow, cyan, white, magenta, ok, info, err, warn
from utils import logger


BANNER = f"""
{red("  ███████╗████████╗██╗   ██╗██╗  ██╗███╗   ██╗███████╗████████╗")}
{red("  ██╔════╝╚══██╔══╝██║   ██║╚██╗██╔╝████╗  ██║██╔════╝╚══██╔══╝")}
{red("  ███████╗   ██║   ██║   ██║ ╚███╔╝ ██╔██╗ ██║█████╗     ██║   ")}
{red("  ╚════██║   ██║   ██║   ██║ ██╔██╗ ██║╚██╗██║██╔══╝     ██║   ")}
{red("  ███████║   ██║   ╚██████╔╝██╔╝ ██╗██║ ╚████║███████╗   ██║   ")}
{red("  ╚══════╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝╚══════╝   ╚═╝   ")}

{cyan("  ICS Attack Simulation Framework")}
{white("  IE4032 Information Warfare -- SLIIT")}
"""


SCRIPTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scripts')


def discover_plugins():
    """Auto-discover all scripts in scripts/ that have a STAGE dict and run() function."""
    plugins = {}
    for fname in sorted(os.listdir(SCRIPTS_DIR)):
        if fname.startswith('_') or not fname.endswith('.py'):
            continue
        modname = fname[:-3]
        try:
            mod = importlib.import_module(f'scripts.{modname}')
            if hasattr(mod, 'STAGE') and hasattr(mod, 'run'):
                stage = mod.STAGE
                key   = stage.get('key', modname[0])
                plugins[key] = {
                    'name': stage.get('name', modname),
                    'desc': stage.get('desc', ''),
                    'run':  mod.run,
                }
        except Exception as e:
            pass
    return plugins


def build_menu(plugins):
    lines = []
    lines.append(f"  {cyan('┌' + '─'*51 + '┐')}")
    lines.append(f"  {cyan('│')} {white('SELECT STAGE'):<51}{cyan('│')}")
    lines.append(f"  {cyan('├' + '─'*51 + '┤')}")

    for key in sorted(plugins.keys(), key=lambda k: (k.isdigit() is False, k)):
        p = plugins[key]
        lines.append(
            f"  {cyan('│')}   {yellow('[' + key + ']'):<6} "
            f"{p['name']:<22} {white('--')} {p['desc']:<20}{cyan('│')}"
        )

    lines.append(f"  {cyan('├' + '─'*51 + '┤')}")
    lines.append(f"  {cyan('│')}   {yellow('[c]'):<6} {'Config':<22} {white('--')} {'change target IP':<20}{cyan('│')}")
    lines.append(f"  {cyan('│')}   {yellow('[0]'):<6} {'Exit':<22} {' ':<20}        {cyan('│')}")
    lines.append(f"  {cyan('└' + '─'*51 + '┘')}")
    return '\n'.join(lines)


def show_config(cfg):
    print(f"  {cyan('Target  :')} {yellow(cfg['target_ip'])}:{yellow(str(cfg['target_port']))}")
    print(f"  {cyan('Attacker:')} {white(cfg['attacker_ip'])}")
    print(f"  {cyan('Log     :')} logs/attack.log")
    print()


def parse_args(plugins):
    parser = argparse.ArgumentParser(
        prog='run.py',
        description='Stuxnet ICS Attack Simulation Framework'
    )
    parser.add_argument(
        '--stage', '-s',
        help=f"Run a single stage directly. Options: {', '.join(sorted(plugins.keys()))}",
        metavar='STAGE'
    )
    parser.add_argument(
        '--target', '-t',
        help='Override target IP (e.g. 192.168.56.101)',
        metavar='IP'
    )
    parser.add_argument(
        '--port', '-p',
        help='Override target port (default: 502)',
        type=int,
        metavar='PORT'
    )
    parser.add_argument(
        '--list', '-l',
        help='List all available stages and exit',
        action='store_true'
    )
    return parser.parse_args()


def main():
    plugins = discover_plugins()
    args    = parse_args(plugins)

    if args.list:
        print()
        print(cyan("  Available stages:"))
        for key in sorted(plugins.keys()):
            p = plugins[key]
            print(f"    {yellow(key):<6} {p['name']:<25} {p['desc']}")
        print()
        return

    print(BANNER)
    cfg = get()

    if args.target:
        cfg['target_ip']   = args.target
    if args.port:
        cfg['target_port'] = args.port

    show_config(cfg)
    logger.session_start(cfg['target_ip'], cfg['target_port'])

    if args.stage:
        key = args.stage.lower()
        if key not in plugins:
            print(err(f"Unknown stage '{key}'. Use --list to see available stages."))
            sys.exit(1)
        print(info(f"Running stage: {plugins[key]['name']}"))
        print()
        try:
            plugins[key]['run'](cfg)
        except KeyboardInterrupt:
            print()
            print(info("Interrupted."))
        logger.session_end()
        return

    while True:
        print(build_menu(plugins))
        print()
        choice = input(f"  {cyan('Select:')} ").strip().lower()
        print()

        if choice == '0':
            print(info("Exiting."))
            print()
            logger.session_end()
            break

        elif choice == 'c':
            reconfigure()
            cfg = get()
            show_config(cfg)
            if args.target:
                cfg['target_ip'] = args.target
            if args.port:
                cfg['target_port'] = args.port

        elif choice in plugins:
            name = plugins[choice]['name']
            print(info(f"Running: {name}"))
            print()
            try:
                plugins[choice]['run'](cfg)
            except KeyboardInterrupt:
                print()
                print(info("Interrupted."))
            except Exception as e:
                print(err(f"Error: {e}"))
            input(f"\n  {cyan('Press Enter to return to menu...')}")
            print()

        else:
            print(warn("Invalid selection."))
            print()


if __name__ == '__main__':
    main()
