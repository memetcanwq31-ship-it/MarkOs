
#!/usr/bin/env python3
import datetime
import random

class TerminalEngine:
    def __init__(self):
        self.tools = {
            "portscan": "Open ports: 22/tcp, 80/tcp, 443/tcp",
            "dnslookup": "example.com -> 93.184.216.34",
            "whois": "Domain: example.com, Registrar: Example Registrar",
            "banner_grab": "HTTP/1.1 200 OK, Server: ExampleServer/1.0",
            "subdomain_enum": "api.example.com, login.example.com, mail.example.com",
            "http_fingerprint": "Server: nginx/1.18.0",
            "ssl_check": "SSL: OK, cert valid until 2025-12-01",
            "smtp_check": "SMTP banner: ESmtp",
            "tcp_connect_test": "Connection to 93.184.216.34:80 - ok",
            "icmp_test": "Ping to 8.8.8.8 - responses: 4",
            "arp_scan": "ARP scan simulated: 3 hosts",
            "fingerprint": "OS: Linux-like, Kernel: 5.x (simulated)",
            "vulnerability_report": "No known vulnerabilities (simulated)",
            "config_discovery": "Discovered config: /etc/hosts (simulated)",
        }

    def start(self) -> str:
        return """\
╔══════════════════════╗
   MarkOS Terminal v1.0
   Android Shell
╚══════════════════════╝

Type help for commands.

markos@android:~$
""".strip()

    def execute(self, command: str) -> str:
        cmd = command.strip()

        if cmd == "help":
            return """\
Available Commands:

help
about
version
clear
time
echo
listtools
tool_<name>  (simulated tools)
""".strip()

        if cmd == "about":
            return """\
MarkOS Terminal
Created for Android (simulated safe training)

Version: 1.0
Engine: MarkShell (simulated)
""".strip()

        if cmd == "version":
            return "MarkOS Terminal v1.0 (simulated)\n"

        if cmd == "time":
            now = datetime.datetime.now()
            return f"Current Time: {now.strftime('%H:%M:%S')}\n"

        if cmd.startswith("echo "):
            return cmd[len("echo "):] + "\n"

        if cmd == "clear":
            # UI tarafında temizlemek için çıktı olarak temizleme işareti döner
            return "\033[2J\033[H"

        if cmd == "listtools":
            names = sorted(self.tools.keys())
            return "Available tools (simulated):\n" + "\n".join(names) + "\n"

        if cmd.startswith("tool_"):
            toolname = cmd[len("tool_"):]
            return self.run_simulated_tool(toolname)

        if cmd.startswith("tool "):
            toolname = cmd[len("tool "):]
            return self.run_simulated_tool(toolname)

        return f"Command not found: {cmd}\n"

    def run_simulated_tool(self, name: str) -> str:
        # Basit bir simülasyon çıktısı üret
        base = f"Simulated tool: {name}\n"
        # Random bir güvenlik/zararlı içerik yok; tamamen eğitim amacıyla çıktı üretir
        outputs = [
            f"Output: {name} executed in sandbox (no real network activity).",
            f"Output: {name} results may vary in real environments.",
            f"Output: {name} simulated success with dummy data.",
        ]
        detail = random.choice(outputs)
        # Rastgele, ama zararsız ek bilgiler
        extra = [
            "Note: This is a safe educational mock.",
            "Warning: This is a simulated tool. No real actions performed.",
            "Info: Use real tools only in controlled labs with proper authorization."
        ]
        return base + detail + "\n" + random.choice(extra) + "\n"

def main():
    terminal = TerminalEngine()
    print(terminal.start())

    while True:
        try:
            command = input("markos@android:~$ ")
        except (EOFError, KeyboardInterrupt):
            print("\nÇıkış yapılıyor...")
            break

        if not command.strip():
            continue

        if command.strip() in ("exit", "quit"):
            print("Çıkış yapılıyor...")
            break

        print(terminal.execute(command), end="")

if __name__ == "__main__":
    main()
