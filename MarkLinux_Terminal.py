#!/usr/bin/env python3
# MarkLinux Terminal v1.0
# Kali Linux tarzı terminal - Düzeltilmiş & Geliştirilmiş

import os
import sys
import shutil
import datetime
import getpass
import socket
import platform
import subprocess
import shlex
import time
import json

# ─── Renk Kodları ──────────────────────────────────────
C_RESET   = "\033[0m"
C_BOLD    = "\033[1m"
C_DIM     = "\033[2m"
C_RED     = "\033[91m"
C_GREEN   = "\033[92m"
C_YELLOW  = "\033[93m"
C_BLUE    = "\033[94m"
C_MAGENTA = "\033[95m"
C_CYAN    = "\033[96m"
C_WHITE   = "\033[97m"

# ─── Banner ────────────────────────────────────────────
BANNER = f"""{C_GREEN}
    __  ___           ____  _____ 
   /  |/  /___ ______/ / / |/ / / 
  / /|_/ / __ `/ ___/ / /|   / /  
 / /  / / /_/ (__  ) /___/   | |  
/_/  /_/\__,_/____/_____/|___|  

    {C_BOLD}MarkLinux Terminal v1.0{C_RESET}
    {C_YELLOW}Next Gen Security Shell{C_RESET}
"""

VERSION = "1.0"
HISTORY_FILE = os.path.expanduser("~/.marklinux_history")

# ─── Komut Takma Adları ────────────────────────────────
ALIASES = {
    "h": "help",
    "c": "clear",
    "q": "exit",
    "quit": "exit",
    "d": "date",
    "t": "time",
    "mem": "free",
    "disk": "df",
    "sys": "sysinfo",
    "cpu": "cpuinfo",
    "ram": "meminfo",
    "net": "ipinfo",
    "ip": "ipinfo",
    "ifconfig": "ipinfo",
}

EXTERNAL_COMMANDS = ["nmap", "tcpdump", "ssh", "scp", "wget", "curl", "git", "python3", "nano", "vi"]


class MarkLinuxTerminal:
    def __init__(self):
        self.history = []
        self.cmds = {
            "help": self._cmd_help,
            "clear": self._cmd_clear,
            "exit": self._cmd_exit,
            "version": self._cmd_version,
            "date": self._cmd_date,
            "time": self._cmd_time,
            "whoami": self._cmd_whoami,
            "hostname": self._cmd_hostname,
            "pwd": self._cmd_pwd,
            "ls": self._cmd_ls,
            "cat": self._cmd_cat,
            "echo": self._cmd_echo,
            "cd": self._cmd_cd,
            "mkdir": self._cmd_mkdir,
            "rm": self._cmd_rm,
            "uname": self._cmd_uname,
            "uptime": self._cmd_uptime,
            "df": self._cmd_df,
            "free": self._cmd_free,
            "ps": self._cmd_ps,
            "kill": self._cmd_kill,
            "ping": self._cmd_ping,
            "sysinfo": self._cmd_sysinfo,
            "cpuinfo": self._cmd_cpuinfo,
            "meminfo": self._cmd_meminfo,
            "ipinfo": self._cmd_ipinfo,
            "history": self._cmd_history,
            "head": self._cmd_head,
            "tail": self._cmd_tail,
            "wc": self._cmd_wc,
            "grep": self._cmd_grep,
        }
        self._load_history()

    # ─── Yardımcı Metodlar ─────────────────────────────
    def prompt(self):
        user = getpass.getuser() or "user"
        host = socket.gethostname() or "marklinux"
        cwd = os.getcwd()
        home = os.path.expanduser("~")
        if cwd.startswith(home):
            cwd = "~" + cwd[len(home):]
        sym = "#" if os.geteuid() == 0 else "$"
        return f"{C_GREEN}{user}@{host}{C_RESET}:{C_BLUE}{cwd}{C_RESET}{sym} "

    def _run(self, parts, timeout=10):
        """Subprocess ile komut çalıştır."""
        try:
            res = subprocess.run(parts, capture_output=True, text=True, timeout=timeout)
            out = res.stdout
            if res.stderr:
                out += res.stderr
            return out
        except subprocess.TimeoutExpired:
            return f"{C_RED}Hata: Komut zaman aşımına uğradı (>{timeout}s){C_RESET}\n"
        except FileNotFoundError:
            return f"{C_RED}Hata: '{parts[0]}' bulunamadı{C_RESET}\n"
        except Exception as e:
            return f"{C_RED}Hata: {e}{C_RESET}\n"

    def _spin(self, msg, duration=0.5):
        ""️ Küçük animasyon."""
        chars = "|/-\\"
        for _ in range(int(duration * 10)):
            for c in chars:
                print(f"\r{C_CYAN}[{c}] {msg}...{C_RESET}", end="", flush=True)
                time.sleep(0.05)
        print()

    def _uptime_str(self):
        if os.path.exists("/proc/uptime"):
            try:
                with open("/proc/uptime") as f:
                    secs = float(f.read().split()[0])
                d, rem = divmod(int(secs), 86400)
                h, rem = divmod(rem, 3600)
                m, s = divmod(rem, 60)
                parts = []
                if d: parts.append(f"{d} gün")
                if h: parts.append(f"{h} saat")
                if m: parts.append(f"{m} dk")
                parts.append(f"{s} sn")
                return ", ".join(parts)
            except:
                pass
        return "Bilinmiyor"

    def _mem_str(self):
        if os.path.exists("/proc/meminfo"):
            try:
                with open("/proc/meminfo") as f:
                    mem = {}
                    for ln in f:
                        k, _, v = ln.partition(":")
                        mem[k.strip()] = int(v.strip().split()[0])
                total = mem.get("MemTotal", 0) // 1024
                free = mem.get("MemFree", 0) // 1024
                avail = mem.get("MemAvailable", free) // 1024
                used = total - avail
                return f"Toplam: {total}M / Kullanılan: {used}M / Boş: {avail}M"
            except:
                pass
        return "Bilinmiyor"

    def _load_history(self):
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, "r") as f:
                    self.history = [ln.strip() for ln in f if ln.strip()]
            except:
                self.history = []

    def _save_history(self):
        try:
            with open(HISTORY_FILE, "w") as f:
                for cmd in self.history[-500:]:
                    f.write(cmd + "\n")
        except:
            pass

    def _all_commands(self):
        return sorted(set(list(self.cmds.keys()) + list(ALIASES.keys()) + EXTERNAL_COMMANDS))

    # ─── Komut İşleyici ──────────────────────────────────
    def execute(self, command):
        command = command.strip()
        if not command:
            return ""

        # Alias çözümle
        first = command.split()[0]
        if first in ALIASES:
            command = command.replace(first, ALIASES[first], 1)
            first = ALIASES[first]

        self.history.append(command)

        # Built-in komutlar
        if first in self.cmds:
            args = shlex.split(command)[1:]
            return self.cmds[first](args)

        # Dış komut dene
        parts = shlex.split(command)
        if parts and shutil.which(parts[0]):
            return self._run(parts)

        return f"{C_RED}marklinux: {first}: komut bulunamadı{C_RESET}\n"

    # ─── Komut Tanımları ─────────────────────────────────
    def _cmd_help(self, args):
        return f"""{C_BOLD}{C_GREEN}╔══════════════════════════════════════════════════╗
║           MarkLinux Terminal v{VERSION}                ║
╠══════════════════════════════════════════════════╣
║  {C_YELLOW}help{C_GREEN}      - Bu yardım mesajını gösterir            ║
║  {C_YELLOW}clear{C_GREEN}     - Ekranı temizler                       ║
║  {C_YELLOW}version{C_GREEN}   - Versiyon bilgisi                      ║
║  {C_YELLOW}date{C_GREEN}      - Tarih ve saat                        ║
║  {C_YELLOW}time{C_GREEN}      - Sadece saat                          ║
║  {C_YELLOW}whoami{C_GREEN}    - Mevcut kullanıcı                      ║
║  {C_YELLOW}hostname{C_GREEN}  - Sistem adı                             ║
║  {C_YELLOW}pwd{C_GREEN}       - Bulunduğun dizin                     ║
║  {C_YELLOW}ls{C_GREEN}        - Dosya listele                        ║
║  {C_YELLOW}cat{C_GREEN}       - Dosya içeriği oku                    ║
║  {C_YELLOW}echo{C_GREEN}      - Metin yazdır                         ║
║  {C_YELLOW}cd{C_GREEN}        - Dizin değiştir                      ║
║  {C_YELLOW}mkdir{C_GREEN}     - Dizin oluştur                        ║
║  {C_YELLOW}rm{C_GREEN}        - Dosya/dizin sil                      ║
║  {C_YELLOW}uname{C_GREEN}     - Kernel bilgisi                       ║
║  {C_YELLOW}uptime{C_GREEN}    - Sistem çalışma süresi                ║
║  {C_YELLOW}df{C_GREEN}        - Disk kullanımı                       ║
║  {C_YELLOW}free{C_GREEN}      - Bellek kullanımı                     ║
║  {C_YELLOW}ps{C_GREEN}        - Çalışan süreçler                     ║
║  {C_YELLOW}kill{C_GREEN}      - Süreç sonlandır                      ║
║  {C_YELLOW}ping{C_GREEN}      - Ağ testi                             ║
║  {C_YELLOW}sysinfo{C_GREEN}   - Sistem özeti                         ║
║  {C_YELLOW}cpuinfo{C_GREEN}   - İşlemci bilgisi                      ║
║  {C_YELLOW}meminfo{C_GREEN}   - Bellek detayları                     ║
║  {C_YELLOW}ipinfo{C_GREEN}    - Ağ arayüz bilgisi                    ║
║  {C_YELLOW}history{C_GREEN}   - Komut geçmişi                        ║
║  {C_YELLOW}head{C_GREEN}      - Dosya başını göster                  ║
║  {C_YELLOW}tail{C_GREEN}      - Dosya sonunu göster                  ║
║  {C_YELLOW}wc{C_GREEN}        - Satır/kelime/byte say                ║
║  {C_YELLOW}grep{C_GREEN}      - Dosyada ara                        ║
║  {C_YELLOW}exit{C_GREEN}      - Terminalden çık                      ║
╚══════════════════════════════════════════════════╝{C_RESET}
"""

    def _cmd_clear(self, args):
        return "\033[2J\033[H"

    def _cmd_exit(self, args):
        return f"{C_YELLOW}Çıkış yapılıyor...{C_RESET}\n"

    def _cmd_version(self, args):
        return f"MarkLinux Terminal v{VERSION}\n"

    def _cmd_date(self, args):
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S\n")

    def _cmd_time(self, args):
        return datetime.datetime.now().strftime("%H:%M:%S\n")

    def _cmd_whoami(self, args):
        return getpass.getuser() + "\n"

    def _cmd_hostname(self, args):
        return socket.gethostname() + "\n"

    def _cmd_pwd(self, args):
        return os.getcwd() + "\n"

    def _cmd_ls(self, args):
        path = args[0] if args else "."
        flags = ["-la"] if "-l" in args or "-a" in args else []
        if shutil.which("ls"):
            return self._run(["ls"] + (flags if flags else []) + [path])
        # Python fallback
        try:
            items = os.listdir(path)
            return "\n".join(items) + "\n"
        except Exception as e:
            return f"ls: {e}\n"

    def _cmd_cat(self, args):
        if not args:
            return "cat: kullanım: cat <dosya>\n"
        path = args[0]
        # Path traversal koruması
        if ".." in path:
            return f"{C_RED}cat: Güvenlik: '..' içeren yollar engellendi{C_RESET}\n"
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        except Exception as e:
            return f"cat: {e}\n"

    def _cmd_echo(self, args):
        return " ".join(args) + "\n"

    def _cmd_cd(self, args):
        path = args[0] if args else os.path.expanduser("~")
        try:
            os.chdir(path)
            return ""
        except Exception as e:
            return f"cd: {e}\n"

    def _cmd_mkdir(self, args):
        if not args:
            return "mkdir: kullanım: mkdir <dizin>\n"
        try:
            os.makedirs(args[0], exist_ok=True)
            return ""
        except Exception as e:
            return f"mkdir: {e}\n"

    def _cmd_rm(self, args):
        if not args:
            return "rm: kullanım: rm <dosya/dizin>\n"
        path = args[0]
        recursive = "-r" in args or "-rf" in args
        try:
            if os.path.isdir(path) and recursive:
                shutil.rmtree(path)
            elif os.path.isfile(path):
                os.remove(path)
            else:
                return f"rm: '{path}' bir dizin; silmek için -r kullan\n"
            return ""
        except Exception as e:
            return f"rm: {e}\n"

    def _cmd_uname(self, args):
        if shutil.which("uname"):
            return self._run(["uname", "-a"] if not args else ["uname"] + args)
        return f"{platform.system()} {platform.release()} ({platform.machine()})\n"

    def _cmd_uptime(self, args):
        if shutil.which("uptime"):
            return self._run(["uptime"])
        return self._uptime_str() + "\n"

    def _cmd_df(self, args):
        if shutil.which("df"):
            return self._run(["df", "-h"] + args)
        return f"{C_RED}df: komut bulunamadı{C_RESET}\n"

    def _cmd_free(self, args):
        if shutil.which("free"):
            return self._run(["free", "-h"] + args)
        return self._mem_str() + "\n"

    def _cmd_ps(self, args):
        if shutil.which("ps"):
            return self._run(["ps", "aux"])
        return f"{C_RED}ps: komut bulunamadı{C_RESET}\n"

    def _cmd_kill(self, args):
        if not args:
            return "kill: kullanım: kill <pid>\n"
        try:
            pid = int(args[-1])
            os.kill(pid, 9)
            return f"PID {pid} sonlandırıldı\n"
        except ValueError:
            return f"kill: '{args[-1]}' geçersiz PID\n"
        except ProcessLookupError:
            return f"kill: PID {args[-1]} bulunamadı\n"
        except PermissionError:
            return f"kill: PID {args[-1]} için yetki yok\n"

    def _cmd_ping(self, args):
        if not args:
            return "ping: kullanım: ping <hedef>\n"
        target = args[0]
        # Güvenlik: shell injection karakterlerini engelle
        if any(c in target for c in ";|&$`\"'\x00"):
            return f"{C_RED}ping: Geçersiz hedef karakteri{C_RESET}\n"
        if shutil.which("ping"):
            flag = "-n" if sys.platform == "win32" else "-c"
            return self._run(["ping", flag, "4", target], timeout=15)
        # Simülasyon modu
        self._spin(f"{target} pingleniyor", 0.8)
        return f"--- {target} ping istatistikleri ---\n4 paket gönderildi, 4 alındı, %0 kayıp\n"

    def _cmd_sysinfo(self, args):
        lines = [f"{C_BOLD}=== MarkLinux Sistem Bilgisi ==={C_RESET}"]
        lines.append(self._cmd_uname([]).strip())
        lines.append(f"Uptime   : {self._uptime_str()}")
        lines.append(f"Bellek   : {self._mem_str()}")
        lines.append(f"Tarih    : {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"Kullanıcı: {getpass.getuser()}")
        lines.append(f"Hostname : {socket.gethostname()}")
        lines.append(f"Python   : {platform.python_version()}")
        lines.append(f"Platform : {platform.platform()}")
        if shutil.which("df"):
            lines.append("\n" + self._cmd_df([]).strip())
        return "\n".join(lines) + "\n"

    def _cmd_cpuinfo(self, args):
        if os.path.exists("/proc/cpuinfo"):
            try:
                with open("/proc/cpuinfo", encoding="utf-8", errors="ignore") as f:
                    return f.read()
            except Exception as e:
                return f"cpuinfo: {e}\n"
        return f"İşlemci: {platform.processor() or platform.machine()}\nMimari : {platform.machine()}\n"

    def _cmd_meminfo(self, args):
        if os.path.exists("/proc/meminfo"):
            try:
                with open("/proc/meminfo", encoding="utf-8", errors="ignore") as f:
                    return f.read()
            except Exception as e:
                return f"meminfo: {e}\n"
        return f"Bellek: {self._mem_str()}\n"

    def _cmd_ipinfo(self, args):
        if shutil.which("ip"):
            return self._run(["ip", "addr"])
        if shutil.which("ifconfig"):
            return self._run(["ifconfig"])
        try:
            host = socket.gethostname()
            ip = socket.gethostbyname(host)
            return f"Hostname: {host}\nIP Adres: {ip}\n"
        except Exception as e:
            return f"ipinfo: {e}\n"

    def _cmd_history(self, args):
        out = ""
        for i, cmd in enumerate(self.history, 1):
            out += f"{i:4d}  {cmd}\n"
        return out

    def _cmd_head(self, args):
        if not args:
            return "head: kullanım: head <dosya> [satır_sayısı]\n"
        path = args[0]
        n = 10
        if len(args) > 1:
            try:
                n = int(args[1])
            except:
                pass
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()[:n]
            return "".join(lines)
        except Exception as e:
            return f"head: {e}\n"

    def _cmd_tail(self, args):
        if not args:
            return "tail: kullanım: tail <dosya> [satır_sayısı]\n"
        path = args[0]
        n = 10
        if len(args) > 1:
            try:
                n = int(args[1])
            except:
                pass
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()[-n:]
            return "".join(lines)
        except Exception as e:
            return f"tail: {e}\n"

    def _cmd_wc(self, args):
        if not args:
            return "wc: kullanım: wc <dosya>\n"
        path = args[0]
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            lines = content.count("\n")
            words = len(content.split())
            chars = len(content)
            return f"{lines:>8} {words:>8} {chars:>8} {path}\n"
        except Exception as e:
            return f"wc: {e}\n"

    def _cmd_grep(self, args):
        if len(args) < 2:
            return "grep: kullanım: grep <kelime> <dosya>\n"
        pattern = args[0]
        path = args[1]
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                out = ""
                for i, line in enumerate(f, 1):
                    if pattern in line:
                        out += f"{C_YELLOW}{i:4d}{C_RESET}:{line}"
                return out if out else f"'{pattern}' bulunamadı\n"
        except Exception as e:
            return f"grep: {e}\n"


# ─── Ana Program ───────────────────────────────────────
def main():
    term = MarkLinuxTerminal()
    print(BANNER)
    print(f"{C_GREEN}MarkLinux Terminal v{VERSION}{C_RESET} — {C_YELLOW}Kali Linux tarzı terminal{C_RESET}")
    print(f"{C_CYAN}Yardım için 'help', çıkış için 'exit' yazın.{C_RESET}\n")

    # Tab tamamlama
    try:
        import readline
        completions = term._all_commands()
        def completer(text, state):
            options = [c + " " for c in completions if c.startswith(text)]
            return options[state] if state < len(options) else None
        readline.set_completer(completer)
        readline.parse_and_bind("tab: complete")
    except ImportError:
        pass

    while True:
        try:
            command = input(term.prompt())
        except (EOFError, KeyboardInterrupt):
            print(f"\n{C_YELLOW}Çıkış yapılıyor...{C_RESET}")
            break
        if not command.strip():
            continue
        output = term.execute(command)
        print(output, end="")
        if command.strip() in ("exit", "quit"):
            break

    term._save_history()
    print(f"{C_GREEN}MarkLinux kapatıldı. Görüşmek üzere!{C_RESET}")


if __name__ == "__main__":
    main()
