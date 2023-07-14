import os
import winreg
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--ip', type=str, help='ntp server ip')
parser.add_argument('-e', '--registry', action='store_true', help='edit registry')
parser.add_argument('-c', '--check', action='store_true', help='check NTP server setting')
parser.add_argument('-r', '--run', action='store_true', help='run w32time')
parser.add_argument('-o', '--offset', action='store_true', help='check offset')
args = parser.parse_args()

# 레지스트리 편집기 값 설정
if args.registry:
    keypath = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Services\w32time\Config", 0, winreg.KEY_ALL_ACCESS)
    winreg.SetValueEx(keypath, "MaxNegPhaseCorrection", 0, winreg.REG_DWORD, 258)
    print('[INFO] MaxNegPhaseCorrection value setting complete')
    print(winreg.QueryValueEx(keypath, "MaxNegPhaseCorrection"))
    winreg.SetValueEx(keypath, "MaxPosPhaseCorrection", 0, winreg.REG_DWORD, 258)
    print('[INFO] MaxPosPhaseCorrection value setting complete')
    print(winreg.QueryValueEx(keypath, "MaxPosPhaseCorrection"))
    print('-' * 60)
    winreg.CloseKey(keypath)

    keypath = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Services\w32time\TimeProviders\NtpClient", 0, winreg.KEY_ALL_ACCESS)
    winreg.SetValueEx(keypath, "SpecialPollInterval", 0, winreg.REG_DWORD, 258)
    print('[INFO] SpecialPollInterval value setting complete')
    print(winreg.QueryValueEx(keypath, "SpecialPollInterval"))
    print('-' * 60)
    winreg.CloseKey(keypath)

# windows NTP Server 설정 확인
if args.check:
    print('[INFO] Setting NtpServer IP')
    terminal_command = "w32tm /config /syncfromflags:manual /manualpeerlist:" + args.ip + " /update"
    os.system(terminal_command)
    print('-' * 60)

    print('[INFO] Check w32time STATE (RUNNING)')
    terminal_command = "sc query w32time"
    os.system(terminal_command)
    print('-' * 60)

    print('[INFO] Check NTP Synchronization')
    terminal_command = "w32tm /query /status"
    os.system(terminal_command)
    print('-' * 60)

# windows time 서비스가 자동으로 시작되도록 설정
if args.run:
    print('[INFO] Setting w32time auto start')
    terminal_command = "sc config w32time start=auto"
    os.system(terminal_command)

    terminal_command = "sc triggerinfo w32time start/networkon stop/networkoff"
    os.system(terminal_command)

    terminal_command = "net stop w32time"
    os.system(terminal_command)

    terminal_command = "net start w32time"
    os.system(terminal_command)

    terminal_command = "w32tm /resync"
    os.system(terminal_command)
    print('-' * 60)

# ntp server와의 offset 확인
if args.offset:
    print("[INFO] Check offset")
    terminal_command = "w32tm /stripchart /computer:" + args.ip + " /dataonly /samples:5"
    os.system(terminal_command)
