from pymodbus.client import ModbusTcpClient
from scripts.config import get
from utils.colors import ok, err, info, red, green, yellow, cyan, white, gray
from utils import logger

STAGE = {
    'name': 'Read PLC State',
    'key':  '2',
    'desc': 'full register map with cover detection',
}

BANNER = f"""
{cyan("  ╔══════════════════════════════════════╗")}
{cyan("  ║")} {white("STAGE 2 -- READ PLC STATE              ")}{cyan("║")}
{cyan("  ╚══════════════════════════════════════╝")}
"""


def _coil_str(val, true_label='ACTIVE', false_label='INACTIVE'):
    if val:
        return green(f"True   ({true_label})")
    return red(f"False  ({false_label})")


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
        logger.error(f"Read failed -- could not connect to {ip}:{port}")
        return

    print(ok("Connected."))
    print()

    try:
        coils = client.read_coils(address=0, count=5)
        regs  = client.read_holding_registers(address=0, count=4)

        c = coils.bits
        r = regs.registers

        logger.info(f"Read: coils={list(c[:5])} regs={list(r)}")

        print(f"  {cyan('NATANZ CENTRIFUGE CONTROL SYSTEM')}")
        print(f"  {'─'*48}")
        print(f"  {'Centrifuge Motor':<22}: {_coil_str(c[0])}")
        print(f"  {'Cascade Stage 1':<22}: {_coil_str(c[1])}")
        print(f"  {'Cascade Stage 2':<22}: {_coil_str(c[2])}")
        print(f"  {'Cascade Stage 3':<22}: {_coil_str(c[3])}")
        print(f"  {'Alarm Status':<22}: {_coil_str(c[4], 'TRIGGERED', 'NONE')}")
        print(f"  {'─'*48}")

        rpm_color = red if r[0] > 1200 else green
        prs_color = red if r[1] > 600  else green
        print(f"  {'Centrifuge RPM':<22}: {rpm_color(str(r[0]) + ' Hz')}")
        print(f"  {'UF6 Pressure':<22}: {prs_color(str(r[1]) + ' mbar')}")
        print(f"  {'─'*48}")

        mon_rpm_color = yellow if r[2] != r[0] else green
        mon_prs_color = yellow if r[3] != r[1] else green
        print(f"  {'Monitor RPM':<22}: {mon_rpm_color(str(r[2]) + ' Hz  (operator view)')}")
        print(f"  {'Monitor Pressure':<22}: {mon_prs_color(str(r[3]) + ' mbar (operator view)')}")
        print(f"  {'─'*48}")
        print()

        if r[0] != r[2] or r[1] != r[3]:
            print(f"  {red('MISMATCH DETECTED')} -- real values differ from operator view.")
            print(f"  {yellow('Cover layer is active. Operators are seeing false data.')}")
            logger.warning("Cover layer detected -- real vs monitor register mismatch.")
        else:
            print(ok("Real values match operator view. No cover layer active."))

        print()

    except Exception as e:
        print(err(f"Read error: {e}"))
        logger.error(f"Read error: {e}")

    client.close()
