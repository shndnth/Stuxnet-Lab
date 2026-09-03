import os
from scripts.config import get, load_targets
from scripts import recon, read_plc
from utils.colors import ok, err, info, warn, cyan, yellow, white, red
from utils import logger

STAGE = {
    'name': 'Multi-Target',
    'key':  'm',
    'desc': 'run against all targets in targets.txt',
}

BANNER = f"""
{cyan("  ╔══════════════════════════════════════╗")}
{cyan("  ║")} {white("MULTI-TARGET MODE                      ")}{cyan("║")}
{cyan("  ╚══════════════════════════════════════╝")}
"""

TARGETS_FILE = os.path.join(os.path.dirname(__file__), '..', 'targets.txt')


def _ensure_targets_file():
    if not os.path.exists(TARGETS_FILE):
        with open(TARGETS_FILE, 'w') as f:
            f.write("# targets.txt -- one target per line\n")
            f.write("# Format: ip:port  (port defaults to 502 if omitted)\n")
            f.write("# Example:\n")
            f.write("# 192.168.56.101:502\n")
            f.write("# 192.168.56.102\n")
        print(info(f"Created targets.txt at {TARGETS_FILE}"))
        print(info("Add your targets to this file and run again."))
        return False
    return True


def run(cfg=None):
    print(BANNER)

    if not _ensure_targets_file():
        return

    targets = load_targets()

    if not targets:
        print(warn("targets.txt is empty or has no valid entries."))
        print(info(f"Edit {TARGETS_FILE} and add targets, one per line."))
        return

    print(info(f"Loaded {len(targets)} target(s):"))
    for t in targets:
        print(f"    {cyan(t['target_ip'])}:{yellow(str(t['target_port']))}")

    print()
    print("  What to run against all targets?")
    print(f"  {cyan('[1]')} Recon only")
    print(f"  {cyan('[2]')} Read PLC state only")
    print(f"  {cyan('[3]')} Recon + Read")
    print()
    choice = input("  Select: ").strip()

    print()
    logger.info(f"Multi-target run started -- {len(targets)} targets, mode={choice}")

    for i, target in enumerate(targets, 1):
        print(f"  {cyan('━'*50)}")
        print(f"  Target {i}/{len(targets)}: {yellow(target['target_ip'])}:{target['target_port']}")
        print(f"  {cyan('━'*50)}")
        print()

        if choice in ('1', '3'):
            recon.run(target)

        if choice in ('2', '3'):
            read_plc.run(target)

        print()

    print(ok(f"Multi-target run complete. {len(targets)} targets processed."))
    logger.success(f"Multi-target run complete -- {len(targets)} targets.")
    print()
