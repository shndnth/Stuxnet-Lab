import os
import json

BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, '.config.json')
TARGETS_FILE = os.path.join(os.path.dirname(BASE_DIR), 'targets.txt')

DEFAULTS = {
    'target_ip':   '192.168.56.101',
    'target_port':  502,
    'attacker_ip': '192.168.56.102',
}

REGISTERS = {
    'coils': {
        0: 'Centrifuge_Motor',
        1: 'Cascade_Stage1',
        2: 'Cascade_Stage2',
        3: 'Cascade_Stage3',
        4: 'Alarm_Status',
    },
    'holding': {
        0: 'Centrifuge_RPM',
        1: 'UF6_Pressure',
        2: 'Monitor_RPM',
        3: 'Monitor_Pressure',
    },
    'normal': {
        'coils':   {0: True, 1: True, 2: True, 3: True, 4: False},
        'holding': {0: 1064, 1: 485, 2: 1064, 3: 485},
    },
    'attack': {
        'coils':   {0: False, 1: False, 2: False, 3: False, 4: True},
        'holding': {0: 1410, 1: 650},
    },
}


def load():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            return json.load(f)
    return DEFAULTS.copy()


def save(cfg):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(cfg, f, indent=2)


def first_run():
    from utils.colors import cyan, white
    print()
    print(cyan('  First run -- configure target details.'))
    print(cyan('  Press Enter to accept the default value.'))
    print()
    cfg = {}
    for key, default in DEFAULTS.items():
        val = input(f'  {key} [{default}]: ').strip()
        cfg[key] = val if val else str(default)
    cfg['target_port'] = int(cfg['target_port'])
    save(cfg)
    print()
    print(white('  Configuration saved.'))
    print()
    return cfg


def get():
    if not os.path.exists(CONFIG_FILE):
        return first_run()
    return load()


def reconfigure():
    if os.path.exists(CONFIG_FILE):
        os.remove(CONFIG_FILE)
    return first_run()


def load_targets():
    if not os.path.exists(TARGETS_FILE):
        return []
    with open(TARGETS_FILE) as f:
        lines = [l.strip() for l in f if l.strip() and not l.startswith('#')]
    targets = []
    for line in lines:
        parts = line.split(':')
        ip   = parts[0]
        port = int(parts[1]) if len(parts) > 1 else 502
        targets.append({'target_ip': ip, 'target_port': port})
    return targets
