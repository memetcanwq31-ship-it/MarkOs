#!/usr/bin/env python3
import datetime
import subprocess
import shutil
import os
import sys

class TerminalEngineReal:
    def __init__(self):
        self.history = []
        self.forbidden_patterns = [
            "rat", "sms_bomber", "sms_bomb", "ddos", "dos", "icmp_flood",
            "imei", "attack", "exploit", "credential", "brute", "phone_spam",
            "spam", "harm", "malware", "virus", "rootkit", "rm ", "rm -rf",
            "mkfs", "dd if", ">:", "shutdown", "reboot", "poweroff"
        ]
        self.security_log = []

    def start(self):
        return """\
╔══════════════════════════════╗
║   MarkOS Terminal v1.1       ║
║   Android Shell              ║
╚══════════════════════════════╝

Type 'help' for available commands.

markos@android:~$ """

    def _is_forbidden(self, cmd: str) -> tuple[bool, str]:
        lower = cmd.lower()
        for pat in self.forbidden_patterns:
            if pat in lower:
                return True, pat
        return False, ""

    def execute(self, command: str) -> str:
        cmd = command.strip()
        if not cmd:
            return ""

        # Güvenlik kontrolü
        is_bad, pattern = self._is_forbidden(cmd)
        if is_bad:
            self.security_log.append((cmd, "blocked", pattern, datetime.datetime.now()))
            return "[SECURITY] Bu komut güvenlik politikaları nedeniyle engellendi.\n"

        self.history.append(cmd)

        if cmd in ("exit", "quit"):
            return "Çıkış yapılıyor...\n"

        if cmd == "help":
            return self._cmd_help()

        if cmd == "about":
            return self._cmd_about()

        if cmd == "version":
            return "MarkOS Terminal v1.1 (real commands)\n"

        if cmd == "time":
            now = datetime.datetime.now()
            return now.strftime("Current Time: %H:%M:%S\n")

        if cmd == "date":
            now = datetime.datetime.now()
            return now.strftime("Current Date: %Y-%m-%d (%A)\n")

        if cmd == "uname":
            return self._run(["uname", "-a"]) if self._which("uname") else self._platform_info()

        if cmd == "uptime":
            if os.path.exists("/proc/uptime"):
                try:
                    with open("/proc/uptime", "r") as f:
                        uptime_seconds = float(f.read().split()[0])
                        m, s = divmod(int(uptime_seconds), 60)
                        h, m = divmod(m, 60)
                        d, h = divmod(h, 24)
                        return f"Up: {d}d {h}h {m}m {s}s\n"
                except Exception:
                    pass
            return self._run(["uptime"]) if self._which("uptime") else "uptime: komut bulunamadı\n"

        if cmd in ("disk", "df"):
            return self._run(["df", "-h"]) if self._which("df") else "df: komut bulunamadı\n"

        if cmd == "mem":
            return self._run(["free", "-h"]) if self._which("free") else "free: komut bulunamadı\n"

        if cmd == "meminfo":
            if os.path.exists("/proc/meminfo"):
                try:
                    with open("/proc/meminfo", "r", encoding="utf-8") as f:
                        return f.read()
                except Exception as e:
                    return f"Error: {e}\n"
            return "meminfo: /proc/meminfo bulunamadı\n"

        if cmd == "whoami":
            return self._run(["whoami"]) or "unknown\n"

        if cmd == "hostname":
            return self._run(["hostname"]) or "unknown\n"

        if cmd == "netstat":
            return self._run(["netstat", "-tulnp"]) if self._which("netstat") else "netstat: komut bulunamadı\n"

        if cmd in ("ipaddr", "ip"):
            if self._which("ip"):
                return self._run(["ip", "addr"])
            return "ip: komut bulunamadı\n"

        if cmd.startswith("ping "):
            target = cmd[5:].strip()
            if not target or " " in target or any(c in target for c in ";|&$`"):
                return "ping: Geçersiz hedef\n"
            ping_flag = "-n" if sys.platform == "win32" else "-c"
            if self._which("ping"):
                return self._run(["ping", ping_flag, "2", target])
            return "ping: komut bulunamadı\n"

        if cmd == "ls":
            return self._run(["ls", "-la"]) if self._which("ls") else self._run(["dir"]) if sys.platform == "win32" else "ls: komut bulunamadı\n"

        if cmd.startswith("ls "):
            args = cmd[3:].strip().split()
            if self._which("ls"):
                return self._run(["ls"] + args)
            return "ls: komut bulunamadı\n"

        if cmd == "pwd":
            try:
                return os.getcwd() + "\n"
            except Exception as e:
                return f"pwd: {e}\n"

        if cmd.startswith("cat "):
            filepath = cmd[4:].strip()
            if not filepath or any(c in filepath for c in ";|&$`"):
                return "cat: Geçersiz dosya adı\n"
            if not os.path.exists(filepath):
                return f"cat: {filepath}: Böyle bir dosya veya dizin yok\n"
            if os.path.isdir(filepath):
                return f"cat: {filepath}: Bir dizindir\n"
            try:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    return f.read()
            except Exception as e:
                return f"cat: {filepath}: {e}\n"

        if cmd.startswith("echo "):
            return cmd[5:] + "\n"

        if cmd == "clear":
            return "\033[2J\033[H"

        if cmd == "history":
            if not self.history:
                return ""
            return "\n".join(f"{i+1:4d}  {h}" for i, h in enumerate(self.history)) + "\n"

        if cmd.startswith("run "):
            full = cmd[4:].strip()
            allowed = {
                "pwd", "date", "uname", "uptime", "df", "disk", "whoami",
                "hostname", "ls", "cat", "echo", "time", "meminfo", "sysinfo",
                "cpuinfo", "ipinfo", "ip", "netstat", "ping", "free", "mem"
            }
            parts = full.split()
            if parts and parts[0] in allowed:
                return self.execute(full)
            return "run: Komut güvenli modda çalıştırılamaz\n"

        if cmd == "sysinfo":
            lines = []
            if self._which("uname"):
                lines.append(self._run(["uname", "-a"]))
            else:
                lines.append(self._platform_info())
            if self._which("uptime"):
                lines.append(self._run(["uptime"]))
            if self._which("df"):
                lines.append(self._run(["df", "-h"]))
            if self._which("free"):
                lines.append(self._run(["free", "-h"]))
            return "\n".join(filter(None, lines)) + "\n"

        if cmd == "cpuinfo":
            if os.path.exists("/proc/cpuinfo"):
                try:
                    with open("/proc/cpuinfo", "r", encoding="utf-8") as f:
                        return f.read()
                except Exception as e:
                    return f"cpuinfo: {e}\n"
            return "cpuinfo: /proc/cpuinfo bulunamadı\n"

        if cmd in ("ipinfo", "ipaddrinfo"):
            if self._which("ip"):
                return self._run(["ip", "addr"])
            return "ip: komut bulunamadı\n"

        return f"{cmd}: Komut bulunamadı\n"

    def _cmd_help(self):
        return """\
Kullanılabilir Komutlar:
  help      - Bu yardım mesajını gösterir
  about     - Terminal hakkında bilgi
  version   - Sürüm bilgisi
  clear     - Ekranı temizler
  time      - Saati gösterir
  date      - Tarihi gösterir
  uname     - Sistem bilgisi
  uptime    - Sistem çalışma süresi
  disk      - Disk kullanımı (df -h)
  mem       - Bellek kullanımı (free -h)
  whoami    - Mevcut kullanıcı
  hostname  - Makine adı
  netstat   - Ağ bağlantıları
  ipaddr    - IP adres bilgisi
  ping <h>  - Ping testi (2 paket)
  ls        - Dizin listesi
  pwd       - Mevcut dizin
  cat <f>   - Dosya içeriğini gösterir
  echo <t>  - Metin yazar
  history   - Komut geçmişi
  run <c>   - Güvenli modda komut çalıştırır
  sysinfo   - Sistem özeti
  cpuinfo   - İşlemci bilgisi
  meminfo   - Detaylı bellek bilgisi
  ipinfo    - Detaylı ağ bilgisi
  exit      - Terminalden çıkar
"""

    def _cmd_about(self):
        return """\
MarkOS Terminal
Gerçek OS Komutları (güvenli mod)

Version: 1.1
Engine: MarkShell
"""

    def _platform_info(self):
        return f"{sys.platform} - {os.name}\n"

    def _run(self, parts):
        try:
            res = subprocess.run(parts, capture_output=True, text=True, timeout=10)
            out = res.stdout
            if res.stderr:
                out += res.stderr
            return out
        except FileNotFoundError:
            return f"{parts[0]}: Komut bulunamadı\n"
        except subprocess.TimeoutExpired:
            return f"{parts[0]}: Zaman aşımı\n"
        except Exception as e:
            return f"Error: {e}\n"

    def _which(self, cmd):
        return shutil.which(cmd) is not None


def main():
    engine = TerminalEngineReal()
    print(engine.start(), end="")
    while True:
        try:
            command = input("markos@android:~$ ")
        except (EOFError, KeyboardInterrupt):
            print("\nÇıkış yapılıyor...")
            break

        output = engine.execute(command)
        print(output, end="")

        if command.strip() in ("exit", "quit"):
            break


if __name__ == "__main__":
    main()
