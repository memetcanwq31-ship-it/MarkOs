#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MarkOS Terminal v2.0
Gelişmiş Android/Termux Shell Motoru
GitHub Entegrasyonu | Pkg Yönetimi | Genişletilmiş Komut Seti
"""

import datetime
import subprocess
import shutil
import os
import sys
import json
import urllib.request
import urllib.error
import re
import stat

# Renk kodları
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    DIM = "\033[2m"

C = Colors


class GitHubModule:
    """GitHub API entegrasyonu"""
    BASE = "https://api.github.com"
    HEADERS = {"User-Agent": "MarkOS-Terminal/2.0"}

    def _get(self, endpoint: str) -> dict:
        url = f"{self.BASE}{endpoint}"
        req = urllib.request.Request(url, headers=self.HEADERS)
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            return {"error": f"HTTP {e.code}: {e.reason}"}
        except Exception as e:
            return {"error": str(e)}

    def user(self, username: str) -> str:
        data = self._get(f"/users/{username}")
        if "error" in data:
            return f"{C.RED}GitHub Hatası: {data['error']}{C.RESET}\n"
        lines = [
            f"{C.CYAN}{C.BOLD}GitHub Kullanıcısı: @{data.get('login', 'N/A')}{C.RESET}",
            f"{'─' * 50}",
            f"  {C.GREEN}İsim:{C.RESET}        {data.get('name') or 'Belirtilmemiş'}",
            f"  {C.GREEN}Bio:{C.RESET}         {data.get('bio') or 'Yok'}",
            f"  {C.GREEN}Konum:{C.RESET}       {data.get('location') or 'Yok'}",
            f"  {C.GREEN}Şirket:{C.RESET}      {data.get('company') or 'Yok'}",
            f"  {C.GREEN}Blog:{C.RESET}        {data.get('blog') or 'Yok'}",
            f"  {C.GREEN}Takipçi:{C.RESET}     {data.get('followers', 0)}",
            f"  {C.GREEN}Takip:{C.RESET}       {data.get('following', 0)}",
            f"  {C.GREEN}Repo Sayısı:{C.RESET} {data.get('public_repos', 0)}",
            f"  {C.GREEN}Hesap Tipi:{C.RESET}  {data.get('type', 'N/A')}",
            f"  {C.GREEN}Oluşturulma:{C.RESET} {data.get('created_at', 'N/A')}",
            f"  {C.GREEN}Profil:{C.RESET}      {data.get('html_url', 'N/A')}",
        ]
        return "\n".join(lines) + "\n"

    def repo(self, repo_path: str) -> str:
        if "/" not in repo_path:
            return f"{C.RED}Hata: Format 'kullanici/repo' olmalıdır{C.RESET}\n"
        data = self._get(f"/repos/{repo_path}")
        if "error" in data:
            return f"{C.RED}GitHub Hatası: {data['error']}{C.RESET}\n"
        lines = [
            f"{C.CYAN}{C.BOLD}📦 {data.get('full_name', repo_path)}{C.RESET}",
            f"{'─' * 50}",
            f"  {C.GREEN}Açıklama:{C.RESET}  {data.get('description') or 'Yok'}",
            f"  {C.GREEN}Dil:{C.RESET}       {data.get('language') or 'Belirtilmemiş'}",
            f"  {C.GREEN}⭐ Yıldız:{C.RESET}  {data.get('stargazers_count', 0)}",
            f"  {C.GREEN}🍴 Fork:{C.RESET}    {data.get('forks_count', 0)}",
            f"  {C.GREEN}🐛 Issues:{C.RESET} {data.get('open_issues_count', 0)}",
            f"  {C.GREEN}Lisans:{C.RESET}    {data.get('license', {}).get('name') or 'Yok'}",
            f"  {C.GREEN}Varsayılan:{C.RESET} {data.get('default_branch', 'main')}",
            f"  {C.GREEN}Boyut:{C.RESET}     {data.get('size', 0)} KB",
            f"  {C.GREEN}Son Güncel.:{C.RESET} {data.get('updated_at', 'N/A')}",
            f"  {C.GREEN}URL:{C.RESET}       {data.get('html_url', 'N/A')}",
        ]
        return "\n".join(lines) + "\n"

    def repos(self, username: str) -> str:
        data = self._get(f"/users/{username}/repos?sort=updated&per_page=10")
        if "error" in data:
            return f"{C.RED}GitHub Hatası: {data['error']}{C.RESET}\n"
        if not isinstance(data, list):
            return f"{C.RED}Hata: Kullanıcı bulunamadı{C.RESET}\n"
        lines = [f"{C.CYAN}{C.BOLD}@{username} Son 10 Repo:{C.RESET}", f"{'─' * 50}"]
        for r in data:
            lang = r.get("language") or "?"
            stars = r.get("stargazers_count", 0)
            lines.append(f"  {C.YELLOW}⭐{stars:4d}{C.RESET} [{C.MAGENTA}{lang:10s}{C.RESET}] {C.GREEN}{r.get('name')}{C.RESET}")
            if r.get("description"):
                lines.append(f"         {C.DIM}{r['description'][:60]}{C.RESET}")
        return "\n".join(lines) + "\n"

    def trending(self, lang: str = "", since: str = "daily") -> str:
        q = f"?q=stars:>100+created:>2024-01-01&sort=stars&order=desc&per_page=10"
        if lang:
            q = f"?q=stars:>100+language:{lang}&sort=stars&order=desc&per_page=10"
        data = self._get(f"/search/repositories{q}")
        if "error" in data:
            return f"{C.RED}GitHub Hatası: {data['error']}{C.RESET}\n"
        items = data.get("items", [])
        lines = [f"{C.CYAN}{C.BOLD}🔥 Trending Repos{C.RESET}", f"{'─' * 50}"]
        for i, r in enumerate(items, 1):
            lines.append(f"  {C.YELLOW}{i:2d}. ⭐{r.get('stargazers_count', 0)}{C.RESET} {C.GREEN}{r.get('full_name')}{C.RESET}")
            desc = r.get("description") or "Açıklama yok"
            lines.append(f"      {C.DIM}{desc[:70]}{C.RESET}")
        return "\n".join(lines) + "\n"


class PkgManager:
    """Paket yönetim motoru (apt/pkg/pip/npm)"""
    
    def __init__(self):
        self.managers = {
            "apt": shutil.which("apt"),
            "pkg": shutil.which("pkg"),
            "pip": shutil.which("pip") or shutil.which("pip3"),
            "npm": shutil.which("npm"),
            "dpkg": shutil.which("dpkg"),
        }

    def _detect(self) -> str:
        if self.managers["pkg"]:
            return "pkg"
        if self.managers["apt"]:
            return "apt"
        return "none"

    def update(self) -> str:
        mgr = self._detect()
        if mgr == "none":
            return f"{C.RED}Hata: pkg veya apt bulunamadı{C.RESET}\n"
        return self._run([mgr, "update"])

    def upgrade(self) -> str:
        mgr = self._detect()
        if mgr == "none":
            return f"{C.RED}Hata: pkg veya apt bulunamadı{C.RESET}\n"
        if mgr == "pkg":
            return self._run([mgr, "upgrade"])
        return self._run([mgr, "upgrade", "-y"])

    def install(self, packages: list) -> str:
        if not packages:
            return f"{C.YELLOW}Kullanım: pkg install <paket1> [paket2 ...]{C.RESET}\n"
        mgr = self._detect()
        if mgr == "none":
            return f"{C.RED}Hata: Paket yöneticisi bulunamadı{C.RESET}\n"
        if mgr == "pkg":
            return self._run([mgr, "install", "-y"] + packages)
        return self._run([mgr, "install", "-y"] + packages)

    def remove(self, packages: list) -> str:
        if not packages:
            return f"{C.YELLOW}Kullanım: pkg remove <paket1> [paket2 ...]{C.RESET}\n"
        mgr = self._detect()
        if mgr == "none":
            return f"{C.RED}Hata: Paket yöneticisi bulunamadı{C.RESET}\n"
        if mgr == "pkg":
            return self._run([mgr, "remove"] + packages)
        return self._run([mgr, "remove", "-y"] + packages)

    def search(self, term: str) -> str:
        if not term:
            return f"{C.YELLOW}Kullanım: pkg search <anahtar kelime>{C.RESET}\n"
        mgr = self._detect()
        if mgr == "none":
            return f"{C.RED}Hata: Paket yöneticisi bulunamadı{C.RESET}\n"
        return self._run([mgr, "search", term])

    def list_installed(self) -> str:
        if self.managers["dpkg"]:
            return self._run(["dpkg", "-l"])
        if self.managers["pkg"]:
            return self._run([self.managers["pkg"], "list-installed"])
        if self.managers["pip"]:
            return self._run([self.managers["pip"], "list"])
        return f"{C.RED}Hata: Yüklü paket listesi alınamadı{C.RESET}\n"

    def _run(self, cmd: list) -> str:
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            out = res.stdout
            if res.stderr:
                out += res.stderr
            return out
        except subprocess.TimeoutExpired:
            return f"{C.RED}Zaman aşımı (120s){C.RESET}\n"
        except Exception as e:
            return f"{C.RED}Hata: {e}{C.RESET}\n"


class TerminalEngineReal:
    def __init__(self):
        self.history = []
        self.aliases = {}
        self.env = dict(os.environ)
        self.cwd = os.getcwd()
        self.github = GitHubModule()
        self.pkg = PkgManager()
        
        self.forbidden_patterns = [
            "rat", "sms_bomber", "sms_bomb", "ddos", "dos", "icmp_flood",
            "imei", "attack", "exploit", "credential", "brute", "phone_spam",
            "spam", "harm", "malware", "virus", "rootkit",
            "mkfs", "dd if=/dev/zero", ">:", "shutdown", "poweroff", "halt",
            "init 0", "rm -rf /", "rm -rf /*", "rm -rf ~", ":(){:|:&};:"
        ]
        self.security_log = []

    def start(self):
        uname = self._safe_run(["uname", "-o", "-m"], silent=True).strip()
        return f"""\
{C.CYAN}{C.BOLD}╔══════════════════════════════════════╗
║   MarkOS Terminal v2.0               ║
║   Gelişmiş Android Shell             ║
╚══════════════════════════════════════╝{C.RESET}

{C.DIM}Sistem: {uname}{C.RESET}
{C.DIM}Python: {sys.version.split()[0]}{C.RESET}

{C.YELLOW}Tip:{C.RESET} 'help' komutları listeler | 'github' ile GitHub'a bağlan
      'pkg' paket yönetimi | 'exit' ile çık

{C.GREEN}markos@android:{C.RESET}{C.BLUE}{self._short_cwd()}{C.RESET}$ """

    def _short_cwd(self):
        home = os.path.expanduser("~")
        cwd = self.cwd
        if cwd.startswith(home):
            cwd = "~" + cwd[len(home):]
        return cwd

    def _is_forbidden(self, cmd: str) -> tuple[bool, str]:
        lower = cmd.lower()
        for pat in self.forbidden_patterns:
            if pat in lower:
                return True, pat
        # Shell injection karakterleri kontrolü (sadece belirli komutlarda)
        return False, ""

    def _sanitize_path(self, path: str) -> str:
        """Path traversal ve shell injection kontrolü"""
        if any(c in path for c in ";|&$`><"):
            return ""
        path = os.path.expanduser(path)
        if not os.path.isabs(path):
            path = os.path.join(self.cwd, path)
        return os.path.normpath(path)

    def execute(self, command: str) -> str:
        cmd = command.strip()
        if not cmd:
            return ""

        # Alias çözümleme
        parts = cmd.split()
        if parts[0] in self.aliases:
            cmd = self.aliases[parts[0]] + " " + " ".join(parts[1:])
            parts = cmd.split()

        # Güvenlik kontrolü
        is_bad, pattern = self._is_forbidden(cmd)
        if is_bad:
            self.security_log.append((cmd, "blocked", pattern, datetime.datetime.now()))
            return f"{C.RED}[GÜVENLİK] Bu komut engellendi: '{pattern}'{C.RESET}\n"

        self.history.append(cmd)

        # ─── TEMEL KOMUTLAR ───
        if cmd in ("exit", "quit"):
            return f"{C.YELLOW}Çıkış yapılıyor...{C.RESET}\n"

        if cmd == "help":
            return self._cmd_help()

        if cmd == "about":
            return self._cmd_about()

        if cmd == "version":
            return f"{C.CYAN}MarkOS Terminal v2.0 (Gelişmiş){C.RESET}\n"

        if cmd == "time":
            return datetime.datetime.now().strftime(f"{C.GREEN}Saat:{C.RESET} %H:%M:%S\n")

        if cmd == "date":
            now = datetime.datetime.now()
            return now.strftime(f"{C.GREEN}Tarih:{C.RESET} %Y-%m-%d (%A)\n")

        if cmd == "clear":
            return "\033[2J\033[H"

        if cmd == "history":
            if not self.history:
                return ""
            return "\n".join(f"{C.YELLOW}{i+1:4d}{C.RESET}  {h}" for i, h in enumerate(self.history)) + "\n"

        # ─── DOSYA SİSTEMİ ───
        if cmd == "pwd":
            return self.cwd + "\n"

        if cmd.startswith("cd "):
            target = cmd[3:].strip() or os.path.expanduser("~")
            target = self._sanitize_path(target)
            if not target:
                return f"{C.RED}cd: Geçersiz yol{C.RESET}\n"
            if os.path.isdir(target):
                self.cwd = os.path.abspath(target)
                os.chdir(self.cwd)
                return ""
            return f"{C.RED}cd: {cmd[3:].strip()}: Böyle bir dizin yok{C.RESET}\n"

        if cmd == "ls" or cmd.startswith("ls "):
            args = ["ls", "-la", "--color=auto"] if cmd == "ls" else ["ls"] + cmd.split()[1:] + ["--color=auto"]
            return self._run_in_dir(args)

        if cmd.startswith("mkdir "):
            name = cmd[6:].strip()
            path = self._sanitize_path(name)
            if not path:
                return f"{C.RED}mkdir: Geçersiz isim{C.RESET}\n"
            try:
                os.makedirs(path, exist_ok=True)
                return f"{C.GREEN}Dizin oluşturuldu: {name}{C.RESET}\n"
            except Exception as e:
                return f"{C.RED}mkdir: {e}{C.RESET}\n"

        if cmd.startswith("touch "):
            name = cmd[6:].strip()
            path = self._sanitize_path(name)
            if not path:
                return f"{C.RED}touch: Geçersiz isim{C.RESET}\n"
            try:
                open(path, "a").close()
                os.utime(path, None)
                return ""
            except Exception as e:
                return f"{C.RED}touch: {e}{C.RESET}\n"

        if cmd.startswith("rm "):
            target = cmd[3:].strip()
            recursive = False
            if target.startswith("-r ") or target.startswith("-rf "):
                recursive = True
                target = target.split(" ", 1)[1] if " " in target else ""
            if not target:
                return f"{C.YELLOW}Kullanım: rm [-r] <dosya/dizin>{C.RESET}\n"
            path = self._sanitize_path(target)
            if not path or path == "/" or path == os.path.expanduser("~"):
                return f"{C.RED}rm: Bu dizin silinemez{C.RESET}\n"
            try:
                if os.path.isfile(path):
                    os.remove(path)
                    return f"{C.GREEN}Silindi: {target}{C.RESET}\n"
                elif os.path.isdir(path):
                    if recursive:
                        shutil.rmtree(path)
                        return f"{C.GREEN}Dizin silindi: {target}{C.RESET}\n"
                    return f"{C.RED}rm: '{target}' bir dizindir. -r kullanın{C.RESET}\n"
                return f"{C.RED}rm: '{target}' bulunamadı{C.RESET}\n"
            except Exception as e:
                return f"{C.RED}rm: {e}{C.RESET}\n"

        if cmd.startswith("cp "):
            args = cmd[3:].strip().split()
            if len(args) < 2:
                return f"{C.YELLOW}Kullanım: cp <kaynak> <hedef>{C.RESET}\n"
            src = self._sanitize_path(args[0])
            dst = self._sanitize_path(args[-1])
            if not src or not dst:
                return f"{C.RED}cp: Geçersiz yol{C.RESET}\n"
            try:
                if os.path.isdir(src):
                    shutil.copytree(src, dst, dirs_exist_ok=True)
                else:
                    shutil.copy2(src, dst)
                return f"{C.GREEN}Kopyalandı: {args[0]} → {args[-1]}{C.RESET}\n"
            except Exception as e:
                return f"{C.RED}cp: {e}{C.RESET}\n"

        if cmd.startswith("mv "):
            args = cmd[3:].strip().split()
            if len(args) < 2:
                return f"{C.YELLOW}Kullanım: mv <kaynak> <hedef>{C.RESET}\n"
            src = self._sanitize_path(args[0])
            dst = self._sanitize_path(args[-1])
            if not src or not dst:
                return f"{C.RED}mv: Geçersiz yol{C.RESET}\n"
            try:
                shutil.move(src, dst)
                return f"{C.GREEN}Taşındı: {args[0]} → {args[-1]}{C.RESET}\n"
            except Exception as e:
                return f"{C.RED}mv: {e}{C.RESET}\n"

        if cmd.startswith("cat "):
            filepath = cmd[4:].strip()
            path = self._sanitize_path(filepath)
            if not path:
                return f"{C.RED}cat: Geçersiz dosya adı{C.RESET}\n"
            if not os.path.exists(path):
                return f"{C.RED}cat: {filepath}: Böyle bir dosya yok{C.RESET}\n"
            if os.path.isdir(path):
                return f"{C.RED}cat: {filepath}: Bir dizindir{C.RESET}\n"
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    # Binary dosya kontrolü
                    if '\x00' in content[:1024]:
                        return f"{C.YELLOW}cat: {filepath}: Binary dosya (gösterilemez){C.RESET}\n"
                    return content
            except Exception as e:
                return f"{C.RED}cat: {e}{C.RESET}\n"

        if cmd.startswith("head "):
            filepath = cmd[5:].strip()
            path = self._sanitize_path(filepath)
            if not path or not os.path.isfile(path):
                return f"{C.RED}head: Dosya bulunamadı{C.RESET}\n"
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    return "".join(f.readlines()[:10])
            except Exception as e:
                return f"{C.RED}head: {e}{C.RESET}\n"

        if cmd.startswith("tail "):
            filepath = cmd[5:].strip()
            path = self._sanitize_path(filepath)
            if not path or not os.path.isfile(path):
                return f"{C.RED}tail: Dosya bulunamadı{C.RESET}\n"
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    lines = f.readlines()
                    return "".join(lines[-10:])
            except Exception as e:
                return f"{C.RED}tail: {e}{C.RESET}\n"

        if cmd.startswith("find "):
            args = cmd[5:].strip()
            try:
                result = []
                for root, dirs, files in os.walk(self.cwd):
                    for name in files + dirs:
                        if args.lower() in name.lower():
                            full = os.path.join(root, name)
                            rel = os.path.relpath(full, self.cwd)
                            result.append(rel)
                if not result:
                    return f"{C.YELLOW}Sonuç bulunamadı{C.RESET}\n"
                return "\n".join(result[:50]) + ("\n..." if len(result) > 50 else "") + "\n"
            except Exception as e:
                return f"{C.RED}find: {e}{C.RESET}\n"

        if cmd.startswith("grep "):
            args = cmd[5:].strip().split(" ", 1)
            if len(args) < 2:
                return f"{C.YELLOW}Kullanım: grep <anahtar> <dosya>{C.RESET}\n"
            keyword, filepath = args[0], args[1].strip()
            path = self._sanitize_path(filepath)
            if not path or not os.path.isfile(path):
                return f"{C.RED}grep: Dosya bulunamadı{C.RESET}\n"
            try:
                matches = []
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    for i, line in enumerate(f, 1):
                        if keyword in line:
                            hl = line.replace(keyword, f"{C.RED}{keyword}{C.RESET}")
                            matches.append(f"{C.YELLOW}{i:4d}{C.RESET}:{hl.rstrip()}")
                if not matches:
                    return f"{C.YELLOW}Eşleşme bulunamadı{C.RESET}\n"
                return "\n".join(matches[:50]) + "\n"
            except Exception as e:
                return f"{C.RED}grep: {e}{C.RESET}\n"

        if cmd.startswith("wc "):
            filepath = cmd[3:].strip()
            path = self._sanitize_path(filepath)
            if not path or not os.path.isfile(path):
                return f"{C.RED}wc: Dosya bulunamadı{C.RESET}\n"
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    lines = content.count("\n")
                    words = len(content.split())
                    chars = len(content)
                    return f"  {C.GREEN}{lines}{C.RESET} satır  {C.GREEN}{words}{C.RESET} kelime  {C.GREEN}{chars}{C.RESET} karakter  {filepath}\n"
            except Exception as e:
                return f"{C.RED}wc: {e}{C.RESET}\n"

        # ─── SİSTEM BİLGİSİ ───
        if cmd == "uname":
            return self._safe_run(["uname", "-a"]) or self._platform_info()

        if cmd == "uptime":
            if os.path.exists("/proc/uptime"):
                try:
                    with open("/proc/uptime", "r") as f:
                        uptime_seconds = float(f.read().split()[0])
                        m, s = divmod(int(uptime_seconds), 60)
                        h, m = divmod(m, 60)
                        d, h = divmod(h, 24)
                        return f"{C.GREEN}Çalışma Süresi:{C.RESET} {d}g {h}s {m}d {s}sn\n"
                except Exception:
                    pass
            return self._safe_run(["uptime"]) or f"{C.RED}uptime: komut bulunamadı{C.RESET}\n"

        if cmd in ("disk", "df"):
            return self._safe_run(["df", "-h"]) or f"{C.RED}df: komut bulunamadı{C.RESET}\n"

        if cmd == "mem":
            return self._safe_run(["free", "-h"]) or f"{C.RED}free: komut bulunamadı{C.RESET}\n"

        if cmd == "meminfo":
            if os.path.exists("/proc/meminfo"):
                try:
                    with open("/proc/meminfo", "r", encoding="utf-8") as f:
                        return f.read()
                except Exception as e:
                    return f"{C.RED}meminfo: {e}{C.RESET}\n"
            return f"{C.RED}meminfo: /proc/meminfo bulunamadı{C.RESET}\n"

        if cmd == "cpuinfo":
            if os.path.exists("/proc/cpuinfo"):
                try:
                    with open("/proc/cpuinfo", "r", encoding="utf-8") as f:
                        return f.read()
                except Exception as e:
                    return f"{C.RED}cpuinfo: {e}{C.RESET}\n"
            return f"{C.RED}cpuinfo: /proc/cpuinfo bulunamadı{C.RESET}\n"

        if cmd == "whoami":
            return (self._safe_run(["whoami"]) or "unknown").strip() + "\n"

        if cmd == "hostname":
            return (self._safe_run(["hostname"]) or "unknown").strip() + "\n"

        if cmd == "netstat":
            return self._safe_run(["netstat", "-tulnp"]) or f"{C.RED}netstat: komut bulunamadı{C.RESET}\n"

        if cmd in ("ipaddr", "ip"):
            if shutil.which("ip"):
                return self._safe_run(["ip", "addr"]) or ""
            return f"{C.RED}ip: komut bulunamadı{C.RESET}\n"

        if cmd.startswith("ping "):
            target = cmd[5:].strip()
            if not target or " " in target or any(c in target for c in ";|&$`"):
                return f"{C.RED}ping: Geçersiz hedef{C.RESET}\n"
            flag = "-n" if sys.platform == "win32" else "-c"
            return self._safe_run(["ping", flag, "3", target]) or f"{C.RED}ping: komut bulunamadı{C.RESET}\n"

        if cmd == "ps":
            return self._safe_run(["ps", "aux"]) or self._safe_run(["ps", "-ef"]) or f"{C.RED}ps: komut bulunamadı{C.RESET}\n"

        if cmd == "top":
            return f"{C.YELLOW}top: Etkileşimli mod desteklenmiyor. 'ps' kullanın.{C.RESET}\n"

        if cmd == "sysinfo":
            lines = []
            lines.append(f"{C.CYAN}{C.BOLD}Sistem Özeti{C.RESET}")
            lines.append(f"{'─' * 40}")
            lines.append(f"{C.GREEN}OS:{C.RESET}       {self._safe_run(['uname', '-o'], silent=True).strip()}")
            lines.append(f"{C.GREEN}Kernel:{C.RESET}   {self._safe_run(['uname', '-r'], silent=True).strip()}")
            lines.append(f"{C.GREEN}Makine:{C.RESET}   {self._safe_run(['uname', '-m'], silent=True).strip()}")
            lines.append(f"{C.GREEN}Python:{C.RESET}   {sys.version.split()[0]}")
            lines.append(f"{C.GREEN}Dizin:{C.RESET}    {self.cwd}")
            lines.append(f"{C.GREEN}Paket:{C.RESET}    {self.pkg._detect() or 'Yok'}")
            return "\n".join(lines) + "\n"

        # ─── ECHO & DEĞİŞKENLER ───
        if cmd.startswith("echo "):
            text = cmd[5:]
            # Ortam değişkeni çözümleme
            for key in self.env:
                text = text.replace(f"${key}", self.env[key])
            return text + "\n"

        if cmd.startswith("export "):
            expr = cmd[7:].strip()
            if "=" in expr:
                key, val = expr.split("=", 1)
                self.env[key.strip()] = val.strip().strip('"').strip("'")
                os.environ[key.strip()] = val.strip().strip('"').strip("'")
                return ""
            return f"{C.YELLOW}Kullanım: export KEY=value{C.RESET}\n"

        if cmd == "env":
            return "\n".join(f"{k}={v}" for k, v in sorted(self.env.items())) + "\n"

        # ─── ALIAS ───
        if cmd.startswith("alias "):
            expr = cmd[6:].strip()
            if "=" in expr:
                name, val = expr.split("=", 1)
                self.aliases[name.strip()] = val.strip().strip('"').strip("'")
                return f"{C.GREEN}Alias tanımlandı: {name.strip()}{C.RESET}\n"
            if expr in self.aliases:
                return f"{C.GREEN}{expr}='{self.aliases[expr]}'{C.RESET}\n"
            return "\n".join(f"{C.GREEN}{k}{C.RESET}='{v}'" for k, v in self.aliases.items()) + "\n"

        # ─── PAKET YÖNETİMİ ───
        if cmd == "pkg":
            return self._cmd_pkg_help()

        if cmd == "pkg update":
            return self.pkg.update()

        if cmd == "pkg upgrade":
            return self.pkg.upgrade()

        if cmd.startswith("pkg install "):
            pkgs = cmd[12:].strip().split()
            return self.pkg.install(pkgs)

        if cmd.startswith("pkg remove "):
            pkgs = cmd[11:].strip().split()
            return self.pkg.remove(pkgs)

        if cmd.startswith("pkg search "):
            term = cmd[11:].strip()
            return self.pkg.search(term)

        if cmd == "pkg list-installed":
            return self.pkg.list_installed()

        # apt komutları
        if cmd == "apt update":
            return self.pkg.update()

        if cmd == "apt upgrade":
            return self.pkg.upgrade()

        if cmd.startswith("apt install "):
            pkgs = cmd[12:].strip().split()
            return self.pkg.install(pkgs)

        if cmd.startswith("apt remove "):
            pkgs = cmd[11:].strip().split()
            return self.pkg.remove(pkgs)

        if cmd == "apt update && apt upgrade":
            out = self.pkg.update()
            out += "\n" + "="*40 + "\n"
            out += self.pkg.upgrade()
            return out

        # ─── GITHUB ───
        if cmd == "github":
            return self._cmd_github_help()

        if cmd.startswith("github user "):
            user = cmd[12:].strip()
            return self.github.user(user)

        if cmd.startswith("github repo "):
            repo = cmd[12:].strip()
            return self.github.repo(repo)

        if cmd.startswith("github repos "):
            user = cmd[13:].strip()
            return self.github.repos(user)

        if cmd == "github trending":
            return self.github.trending()

        if cmd.startswith("github trending "):
            lang = cmd[16:].strip()
            return self.github.trending(lang)

        # ─── DİĞER KOMUTLAR ───
        if cmd.startswith("python") or cmd.startswith("python3"):
            return f"{C.YELLOW}Python etkileşimli modu desteklenmiyor. 'python <dosya.py>' çalıştırın.{C.RESET}\n"

        if cmd.startswith("python ") or cmd.startswith("python3 "):
            return self._safe_run(cmd.split(), timeout=30) or ""

        if cmd.startswith("node "):
            return self._safe_run(cmd.split(), timeout=30) or ""

        if cmd.startswith("npm "):
            return self._safe_run(cmd.split(), timeout=60) or ""

        if cmd.startswith("git "):
            return self._safe_run(cmd.split(), timeout=30) or ""

        if cmd.startswith("run "):
            full = cmd[4:].strip()
            allowed = {
                "pwd", "date", "uname", "uptime", "df", "disk", "whoami",
                "hostname", "ls", "cat", "echo", "time", "meminfo", "sysinfo",
                "cpuinfo", "ipinfo", "ip", "netstat", "ping", "free", "mem",
                "ps", "env", "clear", "python", "python3", "node", "npm", "git"
            }
            fparts = full.split()
            if fparts and fparts[0] in allowed:
                return self.execute(full)
            return f"{C.RED}run: Komut güvenli modda çalıştırılamaz{C.RESET}\n"

        return f"{C.RED}{cmd}: Komut bulunamadı{C.RESET}\n"

    # ─── YARDIM METOTLARI ───
    def _cmd_help(self):
        return f"""\
{C.CYAN}{C.BOLD}╔══════════════════════════════════════════════════╗
║           MarkOS Terminal v2.0 Komutları         ║
╚══════════════════════════════════════════════════╝{C.RESET}

{C.YELLOW}{C.BOLD}Temel Komutlar:{C.RESET}
  help, about, version, clear, exit
  time, date, history, whoami, hostname

{C.YELLOW}{C.BOLD}Dosya Sistemi:{C.RESET}
  pwd, cd <dizin>, ls [-la], mkdir <dizin>
  touch <dosya>, cat <dosya>, head <dosya>, tail <dosya>
  rm [-r] <dosya/dizin>, cp <kaynak> <hedef>, mv <kaynak> <hedef>
  find <anahtar>, grep <anahtar> <dosya>, wc <dosya>

{C.YELLOW}{C.BOLD}Sistem Bilgisi:{C.RESET}
  uname, uptime, disk, mem, meminfo, cpuinfo
  netstat, ipaddr, ping <host>, ps, sysinfo

{C.YELLOW}{C.BOLD}Değişkenler & Alias:{C.RESET}
  echo <metin>, export KEY=value, env, alias [isim=değer]

{C.YELLOW}{C.BOLD}Paket Yönetimi (pkg/apt):{C.RESET}
  pkg update          - Paket listesini güncelle
  pkg upgrade         - Paketleri yükselt
  pkg install <p>     - Paket kur
  pkg remove <p>      - Paket kaldır
  pkg search <p>      - Paket ara
  pkg list-installed  - Yüklü paketleri listele
  apt update && apt upgrade  - Tam güncelleme

{C.YELLOW}{C.BOLD}GitHub Entegrasyonu:{C.RESET}
  github user <kullanici>      - Kullanıcı bilgisi
  github repo <kullanici/repo> - Repo detayı
  github repos <kullanici>     - Repo listesi
  github trending [dil]        - Trending repolar

{C.YELLOW}{C.BOLD}Diğer:{C.RESET}
  python <dosya.py>, node <dosya.js>, npm <komut>, git <komut>
  run <komut>  (güvenli modda çalıştır)
"""

    def _cmd_about(self):
        return f"""\
{C.CYAN}{C.BOLD}MarkOS Terminal v2.0{C.RESET}
Gelişmiş Android/Termux Shell Motoru

Özellikler:
  • Gerçek OS komutları (güvenli mod)
  • GitHub API entegrasyonu
  • pkg/apt paket yönetimi
  • Renkli terminal çıktısı
  • Dosya sistemi manipülasyonu
"""

    def _cmd_pkg_help(self):
        return f"""\
{C.CYAN}{C.BOLD}Paket Yönetimi (pkg/apt){C.RESET}

{C.GREEN}pkg update{C.RESET}              - Paket listesini güncelle
{C.GREEN}pkg upgrade{C.RESET}             - Paketleri yükselt
{C.GREEN}pkg install <paket...>{C.RESET}  - Paket kur
{C.GREEN}pkg remove <paket...>{C.RESET}   - Paket kaldır
{C.GREEN}pkg search <anahtar>{C.RESET}     - Paket ara
{C.GREEN}pkg list-installed{C.RESET}      - Yüklü paketleri listele

{C.YELLOW}Not: apt komutları da desteklenir.{C.RESET}
"""

    def _cmd_github_help(self):
        return f"""\
{C.CYAN}{C.BOLD}GitHub Entegrasyonu{C.RESET}

{C.GREEN}github user <kullanici>{C.RESET}        - Profil bilgisi
{C.GREEN}github repo <kullanici/repo>{C.RESET}  - Repo detayları
{C.GREEN}github repos <kullanici>{C.RESET}     - Son 10 repo
{C.GREEN}github trending [dil]{C.RESET}          - Trending repolar

{C.YELLOW}Örnek:{C.RESET}
  github user torvalds
  github repo python/cpython
  github trending python
"""

    def _platform_info(self):
        return f"{sys.platform} - {os.name}\n"

    def _safe_run(self, parts, timeout=10, silent=False):
        try:
            res = subprocess.run(parts, capture_output=True, text=True, timeout=timeout, cwd=self.cwd)
            out = res.stdout
            if res.stderr:
                out += res.stderr
            return out
        except FileNotFoundError:
            return "" if silent else f"{parts[0]}: Komut bulunamadı\n"
        except subprocess.TimeoutExpired:
            return "" if silent else f"{C.RED}Zaman aşımı ({timeout}s){C.RESET}\n"
        except Exception as e:
            return "" if silent else f"{C.RED}Hata: {e}{C.RESET}\n"

    def _run_in_dir(self, parts):
        return self._safe_run(parts)


def main():
    engine = TerminalEngineReal()
    print(engine.start(), end="")
    while True:
        try:
            prompt = f"{C.GREEN}markos@android{C.RESET}:{C.BLUE}{engine._short_cwd()}{C.RESET}$ "
            command = input(prompt)
        except (EOFError, KeyboardInterrupt):
            print(f"\n{C.YELLOW}Çıkış yapılıyor...{C.RESET}")
            break

        output = engine.execute(command)
        print(output, end="")

        if command.strip() in ("exit", "quit"):
            break


if __name__ == "__main__":
    main()
