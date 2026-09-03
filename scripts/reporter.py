import os
import datetime
from scripts.config import get
from utils.colors import ok, err, info, cyan, white
from utils import logger

STAGE = {
    'name': 'Report Generator',
    'key':  'r',
    'desc': 'generate markdown attack report from session log',
}

LOG_FILE    = os.path.join(os.path.dirname(__file__), '..', 'logs', 'attack.log')
REPORT_DIR  = os.path.join(os.path.dirname(__file__), '..', 'logs')

BANNER = f"""
{cyan("  ╔══════════════════════════════════════╗")}
{cyan("  ║")} {white("REPORT GENERATOR                       ")}{cyan("║")}
{cyan("  ╚══════════════════════════════════════╝")}
"""


def run(cfg=None):
    if cfg is None:
        cfg = get()

    print(BANNER)

    if not os.path.exists(LOG_FILE):
        print(err("No log file found. Run some stages first."))
        return

    with open(LOG_FILE) as f:
        lines = f.readlines()

    if not lines:
        print(err("Log file is empty."))
        return

    print(info(f"Parsing {len(lines)} log entries..."))

    ts       = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    filename = os.path.join(REPORT_DIR, f"report_{ts}.md")

    sessions = []
    current  = []
    for line in lines:
        if 'SESSION' in line and 'New session' in line:
            if current:
                sessions.append(current)
            current = [line]
        else:
            current.append(line)
    if current:
        sessions.append(current)

    attacks  = [l for l in lines if '[ATTACK  ]' in l]
    successes= [l for l in lines if '[SUCCESS ]' in l]
    errors   = [l for l in lines if '[ERROR   ]' in l]
    warnings = [l for l in lines if '[WARNING ]' in l]

    target = cfg['target_ip'] + ':' + str(cfg['target_port'])
    for l in lines:
        if 'target' in l.lower() and '--' in l:
            try:
                target = l.split('target')[-1].strip().split()[0]
            except Exception:
                pass
            break

    report = f"""# Stuxnet ICS Attack Simulation -- Session Report

**Generated :** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Target     :** {target}  
**Log file   :** attack.log  

---

## Summary

| Metric | Count |
|---|---|
| Total log entries | {len(lines)} |
| Sessions | {len(sessions)} |
| Attack actions | {len(attacks)} |
| Successful operations | {len(successes)} |
| Errors | {len(errors)} |
| Warnings | {len(warnings)} |

---

## Attack Actions

"""

    for line in attacks:
        line = line.strip()
        ts_part  = line[1:20] if line.startswith('[') else ''
        msg_part = line.split('] ')[-1] if '] ' in line else line
        report += f"- `{ts_part}` {msg_part}\n"

    report += "\n---\n\n## Successful Operations\n\n"
    for line in successes:
        line = line.strip()
        ts_part  = line[1:20] if line.startswith('[') else ''
        msg_part = line.split('] ')[-1] if '] ' in line else line
        report += f"- `{ts_part}` {msg_part}\n"

    if errors:
        report += "\n---\n\n## Errors\n\n"
        for line in errors:
            line = line.strip()
            ts_part  = line[1:20] if line.startswith('[') else ''
            msg_part = line.split('] ')[-1] if '] ' in line else line
            report += f"- `{ts_part}` {msg_part}\n"

    if warnings:
        report += "\n---\n\n## Warnings\n\n"
        for line in warnings:
            line = line.strip()
            ts_part  = line[1:20] if line.startswith('[') else ''
            msg_part = line.split('] ')[-1] if '] ' in line else line
            report += f"- `{ts_part}` {msg_part}\n"

    report += f"""
---

## MITRE ATT&CK for ICS Mapping

| Technique | ID | Observed |
|---|---|---|
| Network Service Scanning | T0840 | Recon stage -- nmap port scan |
| Point & Tag Identification | T0861 | Recon stage -- register probe |
| Unauthorized Command Message | T0855 | Attack stage -- unauthenticated writes |
| Modify Parameter | T0836 | Attack stage -- RPM and pressure registers |
| Denial of Control | T0813 | Attack stage -- motor coil cut |
| Modify Alarm Settings | T0838 | Attack stage -- alarm coil forced |
| Rootkit | T0851 | Persistence stage -- values re-applied on interval |
| Spoof Reporting Message | T0856 | Cover stage -- monitor registers masked |

---

## Notes

This report was generated automatically from the session log file.  
All actions were performed against a locally hosted virtual machine  
for academic purposes only.
"""

    os.makedirs(REPORT_DIR, exist_ok=True)
    with open(filename, 'w') as f:
        f.write(report)

    print(ok(f"Report saved to: {filename}"))
    logger.info(f"Report generated: {filename}")
    print()
