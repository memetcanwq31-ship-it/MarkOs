#!/usr/bin/env python3
import datetime
import random
import subprocess
import platform
import shutil
import os
import time

class TerminalEngineReal:
    def __init__(self):
        self.history = []
        self.forbidden_patterns = [
            "rat","sms_bomber","sms_bomb","ddos","dos","icmp_flood","imei","attack","exploit",
            "credential","brute","phone_spam","spam","harm","malware","virus","rootkit"
        ]
        self.security_log = []

    def start(self):
        return """\
╔════════════════════════╗
   MarkOS Terminal v1.0
   Android Shell
╚════════════════════════╝

Type help for commands.

markos@android:~$
""".strip()

    def execute(self, command: str) -> str:
        cmd = command.strip()
        lower = cmd.lower()
        self.history.append(cmd)

        # Güvenlik: Zararlı anahtar kelimeler tespit edilirse engelle
        for pat in self.forbidden_patterns:
            if pat in lower:
                self.security_log.append((cmd, "blocked", pat, datetime.datetime.now()))
                return "Bu komut güvenlik politikaları nedeniyle engellendi.\n"

        if cmd == "help":
            return """\
Available Commands:

help
about
version
clear
time
date
uname
uptime
disk
mem
whoami
hostname
netstat
ipaddr
ping
ls
pwd
cat
echo
history
run <cmd>  (whitelisted commands)
sysinfo
cpuinfo
meminfo
ipinfo
"""
        if cmd == "about":
            return """\
MarkOS Terminal
Real OS Commands (local, safe)

Version: 1.0
Engine: MarkShell
""".strip()

        if cmd == "version":
            return "MarkOS Terminal v1.0 (real commands)\n"

        if cmd in ("time","date"):
            now = datetime.datetime.now()
            return now.strftime("Current Time: %H:%M:%S\n")

        if cmd == "uname":
            return self.run(["uname","-a"])

        if cmd == "uptime":
            try:
                with open("/proc/uptime","r") as f:
                    uptime_seconds = float(f.read().split()[0])
                    m, s = divmod(int(uptime_seconds), 60)
                    h, m = divmod(m, 60)
                    return f"Up: {h}h {m}m {s}s\n"
            except Exception:
                return self.run(["uptime"])

        if cmd == "disk" or cmd == "df":
            return self.run(["df","-h"])

        if cmd == "mem":
            return self.run(["free","-h"])

        if cmd == "meminfo":
            # Daha detaylı bellek bilgisi için /proc/meminfo
            try:
                with open("/proc/meminfo","r", encoding="utf-8") as f:
                    return f.read()
            except Exception:
                return self.run(["cat","/proc/meminfo"])

        if cmd == "whoami":
            return (self.run(["whoami"]) or "Unknown user\n")

        if cmd == "hostname":
            return self.run(["hostname"])

        if cmd == "netstat":
            return self.run(["netstat","-tulnp"]) if self._which("netstat") else "netstat not found\n"

        if cmd == "ipaddr" or cmd == "ip":
            if self._which("ip"):
                return self.run(["ip","addr"])
            else:
                return "ip command not found\n"

        if cmd.startswith("ping "):
            target = cmd.split(" ",1)[1]
            if self._which("ping"):
                return self.run(["ping","-c","2",target])
            else:
                return "ping not found\n"

        if cmd == "ls" or cmd == "pwd" or cmd.startswith("cat ") or cmd.startswith("echo "):
            if cmd.startswith("echo "):
                return cmd[5:] + "\n"
            else:
                return self.run(cmd.split())

        if cmd == "clear":
            return "\033[2J\033[H"

        if cmd == "history":
            return "\n".join(self.history) + "\n"

        if cmd.startswith("run "):
            full = cmd[4:]
            allowed = {"pwd","date","uname","uptime","df","disk","whoami","hostname","ls","cat","echo","time","meminfo","sysinfo","cpuinfo","ipinfo","ip","netstat","ping"}
            parts = full.split()
            if parts and parts[0] in allowed:
                return self.run(parts)
            else:
                return "Command not allowed in safe mode\n"

        if cmd == "sysinfo":
            return "\n".join(filter(None, [
                self.run(["uname","-a"]),
                self.run(["uptime"]),
                self.run(["df","-h"]),
                self.run(["free","-h"])
            ]))

        if cmd == "cpuinfo":
            return self.run(["cat","/proc/cpuinfo"]) if os.path.exists("/proc/cpuinfo") else "cpuinfo not available\n"

        if cmd == "ipinfo" or cmd == "ipaddrinfo":
            return self.run(["ip","addr"]) if self._which("ip") else "ip not found\n"

        return f"Command not found: {cmd}\n"

    def run(self, parts):
        try:
            res = subprocess.run(parts, capture_output=True, text=True)
            out = res.stdout
            err = res.stderr
            if err:
                out += err
            return out
        except FileNotFoundError:
            return "Command not found\n"
        except Exception as e:
            return f"Error: {e}\n"

    def _which(self, cmd):
        return shutil.which(cmd) is not None

def main():
    engine = TerminalEngineReal()
    print(engine.start())
    while True:
        try:
            command = input("markos@android:~$ ")
        except (EOFError, KeyboardInterrupt):
            print("\nÇıkış yapılıyor...")
            break

        if not command.strip():
            continue
        if command.strip() in ("exit","quit"):
            print("Çıkış yapılıyor...")
            break

        print(engine.execute(command), end="")

if __name__ == "__main__":
    main()
