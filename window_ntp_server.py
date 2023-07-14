import os
import winreg
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--firewall', action='store_true', help='add firewall inbound rule')
parser.add_argument('-e', '--registry', action='store_true', help='edit registry')
parser.add_argument('-c', '--check', action='store_true', help='check NTP server setting')
parser.add_argument('-r', '--run', action='store_true', help='run w32time')
args = parser.parse_args()

# 방화벽 인바운드 규칙 추가
if args.firewall:
    print('[INFO] Add Inbound Rule of Firewall')
    os.system("netsh advfirewall firewall add rule name=\"NTP_SERVER\" description=\"UDP 123 Port\" dir=in protocol=udp localport=123 action=allow")
    print('-' * 60)

# 레지스트리 편집기 값 설정
if args.registry:
    keypath = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Services\w32time\Config", 0, winreg.KEY_ALL_ACCESS)
    winreg.SetValueEx(keypath, "AnnounceFlags", 0, winreg.REG_DWORD, 5)
    print('[INFO] AnnounceFlags value setting complete')
    print(winreg.QueryValueEx(keypath, "AnnounceFlags"))
    print('-' * 60)
    winreg.CloseKey(keypath)

    keypath = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Services\w32time\TimeProviders\NtpServer", 0, winreg.KEY_ALL_ACCESS)
    winreg.SetValueEx(keypath, "Enabled", 0, winreg.REG_DWORD, 1)
    print('[INFO] Enabled value setting complete')
    print(winreg.QueryValueEx(keypath, "Enabled"))
    print('-' * 60)
    winreg.CloseKey(keypath)

# windows NTP Server 설정 확인
if args.check:
    print('[INFO] Check UDP 123 PORT')
    terminal_command = "netstat -ano | findstr 123"
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


