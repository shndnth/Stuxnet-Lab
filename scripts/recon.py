import subprocess
from pymodbus.client import ModbusTcpClient
from scripts.config import get
from utils.colors import ok, err, info, dim, cyan, white
from utils import logger

STAGE = {
    'name': 'Reconnaissance',
    'key':  '1',
    'desc': 'nmap scan + Modbus fingerprint',
}

BANNER = f"""
{cyan("  ╔══════════════════════════════════════╗")}
{cyan("  ║")} {white("STAGE 1 -- RECONNAISSANCE              ")}{cyan("║")}
{cyan("  ╚══════════════════════════════════════╝")}
"""


def run(cfg=None):
    if cfg is None:
        cfg = get()
    ip   = cfg['target_ip']
    port = cfg['target_port']

    print(BANNER)
    logger.info(f"Recon started against {ip}:{port}")

    print(info(f"Running nmap scan against {ip} port {port}..."))
    print()
    try:
        result = subprocess.run(
            ['nmap', '-sV', '-p', str(port), ip],
            capture_output=True, text=True, timeout=90
        )
        for line in result.stdout.splitlines():
            print(dim(line))
        logger.info(f"nmap complete: {ip}:{port}")
    except FileNotFoundError:
        print(err("nmap not found. Skipping port scan."))
    except subprocess.TimeoutExpired:
        print(err("nmap timed out."))

    print()
    print(info(f"Connecting to Modbus on {ip}:{port}..."))
    client = ModbusTcpClient(ip, port=port)
    if not client.connect():
        print(err("Could not connect to target."))
        logger.error(f"Modbus connection failed to {ip}:{port}")
        return

    print(ok("Connected. No credentials required."))
    print()

    try:
        rr = client.read_device_information()
        if not rr.isError():
            print(ok("Device Identification:"))
            for k, v in rr.information.items():
                print(dim(f"{k}: {v}"))
            logger.info(f"Device identification retrieved from {ip}")
        else:
            print(info("Device identification not supported (non-standard device)."))
    except Exception:
        print(info("Device identification unavailable."))

    print()
    print(info("Scanning unit IDs 1-10..."))
    found = []
    for uid in range(1, 11):
        try:
            r = client.read_coils(address=0, count=1, slave=uid)
            if not r.isError():
                found.append(uid)
        except Exception:
            pass
    if found:
        print(ok(f"Responsive unit IDs: {found}"))
        logger.info(f"Unit IDs found: {found}")
    else:
        print(info("No additional unit IDs found."))

    print()
    print(info("Probing coil range 0-9..."))
    try:
        rr = client.read_coils(address=0, count=10)
        if not rr.isError():
            print(ok(f"Coils 0-9 accessible: {rr.bits[:10]}"))
            logger.info(f"Coil probe success: {rr.bits[:10]}")
    except Exception as e:
        print(err(f"Coil probe failed: {e}"))

    print()
    print(info("Probing holding registers 0-9..."))
    try:
        rr = client.read_holding_registers(address=0, count=10)
        if not rr.isError():
            print(ok(f"Holding registers 0-9 accessible: {rr.registers}"))
            logger.info(f"Register probe success: {rr.registers}")
    except Exception as e:
        print(err(f"Register probe failed: {e}"))

    print()
    print(ok("Recon complete. Target accessible with no authentication."))
    logger.success(f"Recon complete on {ip}:{port}")
    print()

    client.close()
