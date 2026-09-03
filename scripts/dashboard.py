import time
import os
import datetime
from pymodbus.client import ModbusTcpClient
from scripts.config import get
from utils.colors import ok, err, info, red, green, yellow, cyan, white, magenta
from utils import logger

STAGE = {
    'name': 'Live Dashboard',
    'key':  'd',
    'desc': 'real vs operator view, updates every second',
}

INTERVAL = 1


def _clear():
    os.system('cls' if os.name == 'nt' else 'clear')


def _val_color(val, normal, danger_above=None, danger_below=None):
    if danger_above and val > danger_above:
        return red(str(val))
    if danger_below and val < danger_below:
        return red(str(val))
    if val == normal:
        return green(str(val))
    return yellow(str(val))


def _coil_color(val, normal=True):
    return green(str(val)) if val == normal else red(str(val))


def run(cfg=None):
    if cfg is None:
        cfg = get()
    ip   = cfg['target_ip']
    port = cfg['target_port']

    client = ModbusTcpClient(ip, port=port)
    if not client.connect():
        print(err("Connection failed."))
        logger.error(f"Dashboard failed -- could not connect to {ip}:{port}")
        return

    logger.info(f"Dashboard started for {ip}:{port}")
    print(info("Dashboard starting. Press Ctrl+C to exit."))
    time.sleep(1)

    tick = 0

    try:
        while True:
            tick += 1
            try:
                coils = client.read_coils(address=0, count=5)
                regs  = client.read_holding_registers(address=0, count=4)
                c = coils.bits
                r = regs.registers
                ts           = datetime.datetime.now().strftime('%H:%M:%S')
                cover_active = (r[0] != r[2]) or (r[1] != r[3])

                _clear()

                print(cyan("  ╔══════════════════════════════════════════════════════╗"))
                print(cyan("  ║") + white("   NATANZ CENTRIFUGE -- LIVE MONITORING DASHBOARD   ") + cyan("║"))
                print(cyan("  ╚══════════════════════════════════════════════════════╝"))
                print()
                print(f"  Target : {yellow(ip+':'+str(port))}   Tick : {yellow(str(tick))}   Time : {cyan(ts)}")
                print()
                print(f"  {'─'*54}")
                print(f"  {'CONTROL STATUS':<30}{'REAL VALUE':<14}OPERATOR VIEW")
                print(f"  {'─'*54}")
                print(f"  {'Centrifuge Motor':<30}{_coil_color(c[0]):<14}N/A")
                print(f"  {'Cascade Stage 1':<30}{_coil_color(c[1]):<14}N/A")
                print(f"  {'Cascade Stage 2':<30}{_coil_color(c[2]):<14}N/A")
                print(f"  {'Cascade Stage 3':<30}{_coil_color(c[3]):<14}N/A")
                print(f"  {'Alarm Status':<30}{_coil_color(c[4], normal=False):<14}")
                print(f"  {'─'*54}")
                print(f"  {'Centrifuge RPM (Hz)':<30}{_val_color(r[0], 1064, danger_above=1200):<14}{_val_color(r[2], 1064, danger_above=1200)}")
                print(f"  {'UF6 Pressure (mbar)':<30}{_val_color(r[1], 485, danger_above=600):<14}{_val_color(r[3], 485, danger_above=600)}")
                print(f"  {'─'*54}")
                print()

                if cover_active:
                    print(f"  {magenta('[COVER ACTIVE]')} Operator view is masked. Real values differ.")
                    print(f"  {red('Real RPM:')} {r[0]} Hz   {red('Real Pressure:')} {r[1]} mbar")
                    print(f"  {green('Operator RPM:')} {r[2]} Hz   {green('Operator Pressure:')} {r[3]} mbar")
                else:
                    print(f"  {green('[NO COVER]')} Operator view matches real values.")

                print()
                print(f"  {info('Press Ctrl+C to exit dashboard')}")

            except Exception as e:
                _clear()
                print(err(f"Read error: {e}. Reconnecting..."))
                client.close()
                client = ModbusTcpClient(ip, port=port)
                client.connect()

            time.sleep(INTERVAL)

    except KeyboardInterrupt:
        print()
        print(ok("Dashboard exited."))
        logger.info("Dashboard stopped.")
        client.close()
