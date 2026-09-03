import os
import datetime

LOG_DIR  = os.path.join(os.path.dirname(__file__), '..', 'logs')
LOG_FILE = os.path.join(LOG_DIR, 'attack.log')

os.makedirs(LOG_DIR, exist_ok=True)


def _ts():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def log(level, message):
    line = f"[{_ts()}] [{level.upper():8}] {message}\n"
    with open(LOG_FILE, 'a') as f:
        f.write(line)


def info(msg):    log('INFO',    msg)
def success(msg): log('SUCCESS', msg)
def attack(msg):  log('ATTACK',  msg)
def warning(msg): log('WARNING', msg)
def error(msg):   log('ERROR',   msg)


def session_start(target_ip, target_port):
    log('SESSION', f"{'='*60}")
    log('SESSION', f"New session started -- target {target_ip}:{target_port}")
    log('SESSION', f"{'='*60}")


def session_end():
    log('SESSION', 'Session ended')
    log('SESSION', f"{'='*60}")
