<div align="center">

[![My Skills](https://skillicons.dev/icons?i=kali,linux,ubuntu,python,bash)](https://skillicons.dev)

# Stuxnet Lab

**Stuxnet ICS Attack Simulation Framework**

</div>

Full Stuxnet attack chain against a real OpenPLC runtime over Modbus TCP. Interactive menu, plugin auto-discovery, live dashboard, persistence loop, false telemetry cover, register fuzzer, unit ID scanner, coil toggler, multi-target support, automated full chain, session logging, and markdown report generation.

---

## 🖥️ Overview

```
  ┌─────────────────────┐     Modbus TCP      ┌──────────────────────────┐
  │   Kali Linux        │  port 502, no auth  │   Ubuntu Server 22.04    │
  │   192.168.56.102    │ ──────────────────► │   OpenPLC v3             │
  │                     │                     │   NatanzCentrifuge.st    │
  │   run.py            │ ◄────────────────── │   192.168.56.101         │
  │   pymodbus          │   coil / register   │   Modbus TCP :502        │
  └─────────────────────┘                     └──────────────────────────┘
```

---

## ⚔️ Stages

| Key | Stage | Description |
|---|---|---|
| 1 | Reconnaissance | nmap scan + unit ID probe + register fingerprint |
| 2 | Read PLC State | full register map with real vs operator view diff |
| 3 | Execute Attack | 3-phase: overspeed / motor cut / alarm trigger |
| 4 | Persistence | re-applies attack values every 3s, fights any reset |
| 5 | False Telemetry | masks real values in operator monitoring registers |
| 6 | Reset | restores all registers to normal operating state |
| 7 | Unit ID Scanner | brute forces all Modbus unit IDs 1-247 |
| 8 | Register Fuzzer | writes unexpected values across all registers |
| 9 | Coil Toggler | rapid coil toggling to simulate mechanical wear |
| a | Auto Chain | runs all stages in sequence automatically |
| d | Live Dashboard | real vs operator view, updates every second |
| m | Multi-Target | runs recon or read against all targets in targets.txt |
| r | Report Generator | generates markdown attack report from session log |

---

## 🛡️ MITRE ATT&CK for ICS

| Technique | ID | Stage |
|---|---|---|
| Network Service Scanning | T0840 | Recon |
| Point & Tag Identification | T0861 | Recon |
| Unauthorized Command Message | T0855 | Attack |
| Modify Parameter | T0836 | Attack |
| Denial of Control | T0813 | Attack (motor cut) |
| Modify Alarm Settings | T0838 | Attack (alarm trigger) |
| Rootkit | T0851 | Persistence |
| Masquerading | T0849 | Cover |
| Spoof Reporting Message | T0856 | Cover (monitor registers) |
| Scripting | T0853 | Auto chain |
| Remote System Discovery | T0846 | Unit ID scanner |

---

## 🌐 Environment

| Component | Details |
|---|---|
| Host | Windows 11, VirtualBox |
| Target VM | Ubuntu Server 22.04 + OpenPLC v3 |
| Attacker VM | Kali Linux |
| Protocol | Modbus TCP |
| Target IP | 192.168.56.101 |
| Attacker IP | 192.168.56.102 |
| PLC Port | 502 |

---

## 📁 Repository Structure

```
stuxnet-lab/
│
├── run.py                      # Main entry point -- interactive menu + CLI args
├── requirements.txt
├── targets.txt                 # Multi-target IP list
│
├── scripts/                    # Plugin directory -- auto-discovered by run.py
│   ├── config.py               # Target config, register map, first-run setup
│   ├── recon.py                # Stage 1: nmap + Modbus fingerprint
│   ├── read_plc.py             # Stage 2: full register map + cover detection
│   ├── attack.py               # Stage 3: 3-phase attack
│   ├── persist.py              # Stage 4: persistence loop
│   ├── cover.py                # Stage 5: false telemetry
│   ├── reset.py                # Stage 6: restore normal state
│   ├── scanner.py              # Stage 7: unit ID brute force
│   ├── fuzzer.py               # Stage 8: register fuzzer
│   ├── toggler.py              # Stage 9: coil toggler
│   ├── auto_chain.py           # Auto: full chain in sequence
│   ├── dashboard.py            # Live: real vs operator terminal dashboard
│   ├── multi_target.py         # Multi: run against targets.txt
│   └── reporter.py             # Report: generate markdown from session log
│
├── utils/
│   ├── colors.py               # colorama helpers
│   └── logger.py               # timestamped session log writer
│
├── plc-programs/
│   └── natanz.st               # Structured Text centrifuge control program
│
├── network/
│   └── topology.md             # Network topology diagram
│
└── logs/                       # Auto-created on first run
    ├── attack.log              # Timestamped session log
    └── report_<timestamp>.md   # Generated attack reports
```

---

## ⚙️ Setup

### Requirements

- VirtualBox on Windows 10/11
- Ubuntu Server 22.04 LTS
- Kali Linux VirtualBox image
- 8 GB RAM, 40 GB free disk

### Target VM (Ubuntu Server)

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y git openssh-server
git clone https://github.com/thiagoralves/OpenPLC_v3.git
cd OpenPLC_v3 && sudo ./install.sh linux
```

Network (each session):
```bash
sudo ip link set enp0s8 up && sudo dhclient enp0s8
cd ~/OpenPLC_v3 && sudo ./start_openplc.sh &
```

Upload `plc-programs/natanz.st` via `http://192.168.56.101:8080` (login: `openplc / openplc`).

> **Note:** The OpenPLC web interface is only needed to upload the program once. After that, `run.py` communicates directly with the OpenPLC runtime over Modbus TCP on port 502. The web interface does not need to be open during the attack and its monitoring page does not reflect Modbus register changes made externally.

### Attacker VM (Kali)

```bash
sudo ip link set eth1 up && sudo dhcpcd eth1
echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf
pip install -r requirements.txt --break-system-packages
```

---

## 🚀 Usage

### Interactive menu

```bash
python3 run.py
```

First run prompts for target IP, port, and attacker IP. Saved to `scripts/.config.json`.

### Run a single stage directly

```bash
python3 run.py --stage 3
python3 run.py --stage a
python3 run.py --stage d
```

### Override target at runtime

```bash
python3 run.py --target 192.168.1.50 --port 502
```

### List all stages

```bash
python3 run.py --list
```

### Recommended monitoring setup

Run the live dashboard alongside the attack menu for a split-screen view of real vs operator register values updating every second:

```bash
# Terminal 1 -- attack menu
python3 run.py

# Terminal 2 -- live dashboard
python3 run.py --stage d
```

The dashboard auto-detects when the cover layer is active and highlights the mismatch between real and operator-facing values in real time.

### Multi-target

Add targets to `targets.txt` (one per line, format `ip:port`) then select `m` from the menu.

### Add a custom plugin

Drop any `.py` file into `scripts/` with a `STAGE` dict and `run()` function. It appears in the menu automatically on next launch.

```python
STAGE = {
    'name': 'My Custom Stage',
    'key':  'x',
    'desc': 'does something custom',
}

def run(cfg=None):
    print("Custom stage running")
```

---

## 🗺️ Register Map

| Address | Type | Name | Normal | Attack |
|---|---|---|---|---|
| 0 | Coil | Centrifuge_Motor | True | False |
| 1 | Coil | Cascade_Stage1 | True | False |
| 2 | Coil | Cascade_Stage2 | True | False |
| 3 | Coil | Cascade_Stage3 | True | False |
| 4 | Coil | Alarm_Status | False | True |
| 0 | Holding | Centrifuge_RPM | 1064 Hz | 1410 Hz |
| 1 | Holding | UF6_Pressure | 485 mbar | 650 mbar |
| 2 | Holding | Monitor_RPM | 1064 Hz | 1064 Hz (masked) |
| 3 | Holding | Monitor_Pressure | 485 mbar | 485 mbar (masked) |

Registers 2 and 3 are operator-facing. The cover stage writes normal values here while real registers stay at attack values. Stage 2 (Read) detects and highlights the mismatch.

---

## 🔒 Security Controls

| Control | Standard | Stops Which Stage |
|---|---|---|
| OT network segmentation | IEC 62443 Zone/Conduit | Recon never reaches port 502 |
| Modbus protocol firewall | NIST SP 800-82 | Blocks unauthorized writes |
| PLC authentication | IEC 62443 SL-2 | Requires credentials on connect |
| Change control on PLC logic | IEC 62443 SR 3.4 | Detects unauthorized register writes |
| Out-of-band monitoring | IEC 62443 SR 6.1 | Detects real vs monitor register mismatch |
| Network anomaly detection | NIST SP 800-82 | Flags persistence loop traffic pattern |
| Rate limiting on port 502 | NIST SP 800-82 | Limits fuzzer and scanner effectiveness |

---

## ⚠️ Disclaimer

Built for academic purposes as part of an information assurance and auditing assignment. All commands target a locally hosted virtual machine with no connection to any real industrial system, network, or infrastructure.
