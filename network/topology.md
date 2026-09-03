# Network Topology

```
  ┌──────────────────────────────────────────────────────────────────┐
  │                    HOST -- Windows 11                            │
  │                    VirtualBox                                    │
  │                                                                  │
  │  ┌──────────────────────┐      ┌───────────────────────────────┐ │
  │  │  Kali Linux          │      │  Ubuntu Server 22.04          │ │
  │  │  Attacker Machine    │      │  OpenPLC v3 Target            │ │
  │  │                      │      │                               │ │
  │  │  eth0: 10.0.2.15     │      │  enp0s3: 10.0.2.15 (NAT)    │ │
  │  │  (NAT -- internet)   │      │  enp0s8: 192.168.56.101      │ │
  │  │                      │      │  (Host-only -- ICS network)   │ │
  │  │  eth1: 192.168.56.102│      │                               │ │
  │  │  (Host-only)         │      │  OpenPLC Runtime              │ │
  │  │                      │      │  Modbus TCP -- port 502       │ │
  │  │  run.py              │      │  NatanzCentrifuge.st          │ │
  │  │  pymodbus            │      │                               │ │
  │  └──────────┬───────────┘      └───────────────┬───────────────┘ │
  │             │                                  │                  │
  │             │    VirtualBox Host-Only Network   │                  │
  │             │    192.168.56.0/24               │                  │
  │             └──────────── Modbus TCP ──────────┘                  │
  │                           port 502                                │
  │                           no authentication                       │
  └──────────────────────────────────────────────────────────────────┘
```

## Attack Flow

```
  Kali (192.168.56.102)
       │
       ├── [1] nmap -sV -p 502 192.168.56.101
       │        Identifies Modbus TCP on target
       │
       ├── [2] read_coils / read_holding_registers
       │        Reads centrifuge state, no credentials
       │
       ├── [3] write_register(0, 1410)  -- overspeed RPM
       │        write_coil(0, False)    -- kill motor
       │        write_coil(4, True)     -- trigger alarm
       │
       ├── [4] persist loop (3s interval)
       │        Re-applies attack values, fights any reset
       │
       ├── [5] cover loop (2s interval)
       │        Writes 1064/485 to monitor registers
       │        Operators see normal values on SCADA
       │
       └── [6] reset
                Restores all registers to normal state
```

## Notes

- The OpenPLC web interface (port 8080) is only required once to upload the PLC program.
- All attack stages communicate directly over Modbus TCP (port 502) and do not require the web interface to be running.
- The OpenPLC monitoring page does not reflect external Modbus register writes. Use stage `d` (Live Dashboard) for real-time monitoring during the attack.
