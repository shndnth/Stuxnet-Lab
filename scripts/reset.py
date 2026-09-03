from pymodbus.client import ModbusTcpClient
from scripts.config import get, REGISTERS
from utils.colors import ok, err, info, green, cyan, white
from utils import logger

STAGE = {
    'name': 'Reset',
    'key':  '6',
    'desc': 'restore all registers to normal state',
}

BANNER = f"""
{green("  ╔══════════════════════════════════════╗")}
{green("  ║")} {white("RESET -- RESTORE NORMAL STATE          ")}{green("║")}
{green("  ╚══════════════════════════════════════╝")}
"""

NORMAL = REGISTERS['normal']


def run(cfg=None):
    if cfg is None:
        cfg = get()
    ip   = cfg['target_ip']
    port = cfg['target_port']

    print(BANNER)
    print(info(f"Connecting to {ip}:{port}..."))

    client = ModbusTcpClient(ip, port=port)
    if not client.connect():
        print(err("Connection failed."))
        logger.error(f"Reset failed -- could not connect to {ip}:{port}")
        return

    print(ok("Connected. Restoring normal operating state..."))
    print()
    logger.info(f"Reset started on {ip}:{port}")

    for addr, val in NORMAL['coils'].items():
        client.write_coil(address=addr, value=val)

    for addr, val in NORMAL['holding'].items():
        client.write_register(address=addr, value=val)

    print(f"  {green('Centrifuge Motor    : True   (RUNNING)')}")
    print(f"  {green('Cascade Stage 1     : True   (ACTIVE)')}")
    print(f"  {green('Cascade Stage 2     : True   (ACTIVE)')}")
    print(f"  {green('Cascade Stage 3     : True   (ACTIVE)')}")
    print(f"  {green('Alarm Status        : False  (NONE)')}")
    print(f"  {green('Centrifuge RPM      : 1064 Hz')}")
    print(f"  {green('UF6 Pressure        : 485 mbar')}")
    print(f"  {green('Monitor RPM         : 1064 Hz')}")
    print(f"  {green('Monitor Pressure    : 485 mbar')}")
    print()
    print(ok("Reset complete."))
    logger.success(f"Reset complete on {ip}:{port}")
    print()

    client.close()
