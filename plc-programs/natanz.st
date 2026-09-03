(*
  NatanzCentrifuge.st
  Simulated centrifuge control program.

  Register map:
    Coils:
      %QX0.0  Centrifuge_Motor
      %QX0.1  Cascade_Stage1
      %QX0.2  Cascade_Stage2
      %QX0.3  Cascade_Stage3
      %QX0.4  Alarm_Status

    Holding registers:
      %QW0    Centrifuge_RPM      (actual)
      %QW1    UF6_Pressure        (actual)
      %QW2    Monitor_RPM         (operator view -- can be masked by cover)
      %QW3    Monitor_Pressure    (operator view -- can be masked by cover)

  Normal operating values:
    Motor=TRUE, all stages=TRUE, Alarm=FALSE
    RPM=1064 Hz, Pressure=485 mbar

  Alarm triggers:
    RPM  > 1200 or < 100
    Pressure > 600 or < 100
*)

PROGRAM NatanzCentrifuge
  VAR
    Init_Done  : BOOL;
    Scan_Count : INT;
  END_VAR
  VAR_EXTERNAL
    Centrifuge_Motor  : BOOL;
    Cascade_Stage1    : BOOL;
    Cascade_Stage2    : BOOL;
    Cascade_Stage3    : BOOL;
    Alarm_Status      : BOOL;
    Centrifuge_RPM    : INT;
    UF6_Pressure      : INT;
    Monitor_RPM       : INT;
    Monitor_Pressure  : INT;
  END_VAR

  IF NOT Init_Done THEN
    Centrifuge_Motor  := TRUE;
    Cascade_Stage1    := TRUE;
    Cascade_Stage2    := TRUE;
    Cascade_Stage3    := TRUE;
    Alarm_Status      := FALSE;
    Centrifuge_RPM    := 1064;
    UF6_Pressure      := 485;
    Monitor_RPM       := 1064;
    Monitor_Pressure  := 485;
    Init_Done         := TRUE;
  END_IF;

  Scan_Count := Scan_Count + 1;

  IF NOT Centrifuge_Motor THEN
    Cascade_Stage1 := FALSE;
    Cascade_Stage2 := FALSE;
    Cascade_Stage3 := FALSE;
  END_IF;

  IF Centrifuge_RPM > 1200 OR Centrifuge_RPM < 100 THEN
    Alarm_Status := TRUE;
  END_IF;

  IF UF6_Pressure > 600 OR UF6_Pressure < 100 THEN
    Alarm_Status := TRUE;
  END_IF;

END_PROGRAM

CONFIGURATION Config0
  VAR_GLOBAL
    Centrifuge_Motor  AT %QX0.0 : BOOL;
    Cascade_Stage1    AT %QX0.1 : BOOL;
    Cascade_Stage2    AT %QX0.2 : BOOL;
    Cascade_Stage3    AT %QX0.3 : BOOL;
    Alarm_Status      AT %QX0.4 : BOOL;
    Centrifuge_RPM    AT %QW0   : INT;
    UF6_Pressure      AT %QW1   : INT;
    Monitor_RPM       AT %QW2   : INT;
    Monitor_Pressure  AT %QW3   : INT;
  END_VAR
  RESOURCE Res0 ON PLC
    TASK task0(INTERVAL := T#100ms, PRIORITY := 0);
    PROGRAM inst0 WITH task0 : NatanzCentrifuge;
  END_RESOURCE
END_CONFIGURATION
