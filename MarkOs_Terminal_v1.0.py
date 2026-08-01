#!/usr/bin/env python3
import datetime

def start():
    return """\
╔══════════════════════╗
   MarkOS Terminal v1.0
   Android Shell
╚══════════════════════╝

Type help for commands.

markos@android:~$
""".strip()

def execute(command: str) -> str:
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

""".strip()

    if cmd == "about":
        return """\
MarkOS Terminal
Created for Android

Version: 1.0
Engine: MarkShell
""".strip()

    if cmd == "version":
        return "MarkOS Terminal v1.0\n"

    if cmd == "time":
        time_str = datetime.datetime.now().strftime("%H:%M:%S")
        return f"Current Time: {time_str}\n"

    if cmd.startswith("echo "):
        return cmd[len("echo "):] + "\n"

    if cmd == "clear":
        # ANSI ile temizleme komutu
        return "\033[2J\033[H"

    return f"Command not found: {cmd}\n"

def main():
    print(start())
    while True:
        try:
            command = input("markos@android:~$ ")
        except (EOFError, KeyboardInterrupt):
            print("\nÇıkış yapılıyor...")
            break

        if command.strip() == "":
            continue

        if command.strip() in ("exit", "quit"):
            print("Çıkış yapılıyor...")
            break

        print(execute(command), end="")

if __name__ == "__main__":
    main()
