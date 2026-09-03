from pymodbus.client import ModbusTcpClient
from scripts.config import get
from utils.colors import ok, err, info, warn, green, red, yellow, cyan, white
from utils import logger

STAGE = {
    'name': 'Unit ID Scanner',
    'key':  '7',
    'desc': 'brute force all Modbus unit IDs 1-247',
}

BANNER = f"""
{cyan("  ╔══════════════════════════════════════╗")}
{cyan("  ║")} {white("STAGE 7 -- UNIT ID SCANNER             ")}{cyan("║")}
{cyan("  ╚══════════════════════════════════════╝")}
"""


def run(cfg=None):
    if cfg is None:
        cfg = get()
    ip   = cfg['target_ip']
    port = cfg['target_port']

    print(BANNER)
    print(info(f"Scanning all Modbus unit IDs (1-247) on {ip}:{port}"))
    print(info("This maps every accessible slave device on the network."))
    print()

    client = ModbusTcpClient(ip, port=port)
    if not client.connect():
        print(err("Connection failed."))
        logger.error(f"Scanner failed -- could not connect to {ip}:{port}")
        return

    logger.info(f"Unit ID scan started on {ip}:{port}")
    found = []

    for uid in range(1, 248):
        print(f"\r  {info('')}Scanning unit ID {yellow(str(uid)):<6} / 247  ", end='', flush=True)
        try:
            r = client.read_coils(address=0, count=1, slave=uid)
            if not r.isError():
                found.append(uid)
        except Exception:
            pass

    print()
    print()

    if found:
        print(ok(f"Found {len(found)} responsive unit ID(s): {found}"))
        logger.success(f"Unit IDs found: {found}")

        print()
        print(info("Probing each responsive unit..."))
        for uid in found:
            print()
            print(f"  {cyan(f'Unit ID {uid}')}")
            print(f"  {'─'*40}")
            try:
                cr = client.read_coils(address=0, count=8, slave=uid)
                rr = client.read_holding_registers(address=0, count=4, slave=uid)
                if not cr.isError():
                    print(f"  Coils 0-7     : {cr.bits[:8]}")
                if not rr.isError():
                    print(f"  Registers 0-3 : {rr.registers}")
                logger.info(f"Unit {uid} probed: coils={cr.bits[:8] if not cr.isError() else 'error'}")
            except Exception as e:
                print(err(f"Probe failed: {e}"))
    else:
        print(warn("No responsive unit IDs found beyond default."))

    print()
    client.close()
