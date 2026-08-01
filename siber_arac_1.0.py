#!/usr/bin/env python3
import base64
import hashlib
import hmac
import os
import re
import socket
import sys
import time
from concurrent.futures import ThreadPoolExecutor

# -------------------------------
# TEMEL YARDIMCI FONKSİYONLAR
# -------------------------------

def _print_banner():
    print("===============================================")
    print(" SafeLab Security Toolkit - Ethical Lab Edition ")
    print(" 1) Port Scanner (Localhost + Allowed Hosts)")
    print(" 2) File Hash Calculator (SHA-256, SHA-1, SHA-512)")
    print(" 3) OTP (TOTP) Generator/Verifier (Etik Lab)")
    print(" 4) Password Strength Evaluator")
    print(" 5) Log Analyzer (Failed Login Attempts)")
    print(" 6) Exit")
    print("===============================================")

def _prompt(msg, default=None):
    if default is not None:
        return input(f"{msg} [{default}]: ") or default
    return input(f"{msg}: ")

# -------------------------------
# 1) Port Scanner (Localhost safely)
# -------------------------------
def scan_ports(host: str, start_port: int, end_port: int, timeout: float = 0.3, max_workers: int = 200):
    ports = list(range(start_port, end_port + 1))
    open_ports = []

    def probe(p):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            try:
                result = sock.connect_ex((host, p))
                if result == 0:
                    open_ports.append(p)
            except Exception:
                pass

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for p in ports:
            executor.submit(probe, p)

    open_ports.sort()
    return open_ports

# -------------------------------
# 2) Dosya Hash Hesaplayıcı
# -------------------------------
def _hash_file(path: str, algo: str) -> str:
    hash_func = getattr(hashlib, algo)
    h = hash_func()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def hash_file_cli(path: str):
    try:
        sha256 = _hash_file(path, "sha256")
        sha1 = _hash_file(path, "sha1")
        sha512 = _hash_file(path, "sha512")
        return {"sha256": sha256, "sha1": sha1, "sha512": sha512}
    except FileNotFoundError:
        return None

# -------------------------------
# 3) OTP (TOTP) - Basit Uygulama
# -------------------------------
def _totp_secret_generate(length: int = 16) -> str:
    secret = base64.b32encode(os.urandom(length)).decode("utf-8").replace("=", "")
    return secret

def _totp_code(secret: str, counter: int, digits: int = 6) -> str:
    key = base64.b32decode(secret.upper() + ("=" * ((8 - len(secret) % 8) % 8)))
    msg = counter.to_bytes(8, "big")
    h = hmac.new(key, msg, hashlib.sha1).digest()
    o = h[19] & 0x0F
    token = int.from_bytes(h[o:o+4], "big") & 0x7fffffff
    return str(token % (10 ** digits)).zfill(digits)

def generate_totp(secret: str, time_step: int = 30, digits: int = 6, t=None) -> str:
    if t is None:
        t = int(time.time())
    counter = int(t // time_step)
    return _totp_code(secret, counter, digits)

def verify_totp(code: str, secret: str, time_step: int = 30, digits: int = 6, window: int = 1, t=None) -> bool:
    if t is None:
        t = int(time.time())
    for w in range(-window, window + 1):
        counter = int((t // time_step) + w)
        expected = _totp_code(secret, counter, digits)
        if constant_time_equal(code, expected):
            return True
    return False

def constant_time_equal(a: str, b: str) -> bool:
    if len(a) != len(b):
        return False
    result = 0
    for x, y in zip(a.encode(), b.encode()):
        result |= x ^ y
    return result == 0

# -------------------------------
# 4) Parola Güçlendirici
# -------------------------------
def password_strength(pw: str) -> dict:
    score = 0
    length = len(pw)

    if length >= 8:
        score += 1
    if length >= 12:
        score += 1
    if re.search(r"[a-z]", pw) and re.search(r"[A-Z]", pw):
        score += 1
    if re.search(r"[0-9]", pw):
        score += 1
    if re.search(r"[^A-Za-z0-9]", pw):
        score += 1

    levels = {0: "Very Weak", 1: "Weak", 2: "Fair", 3: "Good", 4: "Strong", 5: "Very Strong"}
    rating = levels.get(score, "Unknown")
    return {"score": score, "rating": rating}

# -------------------------------
# 5) Log Analizörü (Basit Failed Login)
# -------------------------------
def analyze_logs(log_path: str) -> dict:
    pattern = re.compile(r"Failed|authentication failure|Invalid user|Login failed", re.IGNORECASE)
    ip_pattern = re.compile(r"(?:\d{1,3}\.){3}\d{1,3}")
    counts = {}
    try:
        with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                if pattern.search(line):
                    ip = ip_pattern.findall(line)
                    if ip:
                        ip = ip[0]
                        counts[ip] = counts.get(ip, 0) + 1
        top = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)[:5]
        return {"top_failed_ips": top}
    except FileNotFoundError:
        return {"error": "log file not found"}

# -------------------------------
# Ana Menu İşleyicisi
# -------------------------------
def main_menu():
    _print_banner()
    choice = input("Bir seçenek girin (1-6): ").strip()
    if choice == "1":
        host = _prompt("Hedef host (varsayılan: 127.0.0.1)", "127.0.0.1")
        start = int(_prompt("Başlangıç portu", "1"))
        end = int(_prompt("Bitiş portu", "1024"))
        print(f"Tarama {host}:{start}-{end} için başlatılıyor...")
        if host not in ("127.0.0.1", "localhost"):
            confirm = input("Uyarı: Bu hedef güvenlik riski taşıyabilir. Devam etmek istiyor musunuz? (y/n): ")
            if confirm.lower() != "y":
                return
        open_ports = scan_ports(host, start, end)
        print("Açık Portlar:", open_ports if open_ports else "Yok")
    elif choice == "2":
        path = _prompt("Hash'ını hesaplamak istediğiniz dosya yolu")
        result = hash_file_cli(path)
        if result:
            print("SHA-256 :", result["sha256"])
            print("SHA-1   :", result["sha1"])
            print("SHA-512 :", result["sha512"])
        else:
            print("Dosya bulunamadı.")
    elif choice == "3":
        secret = _totp_secret_generate()
        print("SECRET (saklanması için):", secret)
        print("Not: Bu basit demo için secret saklanabilir veya kullanıcıya güvenli bir şekilde iletilir.")
        print("OTP üretiyoruz: ", generate_totp(secret))
        code = input("OTP kodunu girin (deney): ").strip()
        if verify_totp(code, secret):
            print("Doğrulama başarılı.")
        else:
            print("Doğrulama başarısız.")
    elif choice == "4":
        pw = _prompt("Değerlendirmek istediğiniz parola")
        res = password_strength(pw)
        print("Puan:", res["score"], "| Seviye:", res["rating"])
    elif choice == "5":
        log_path = _prompt("Analiz etmek istediğiniz log dosyası yolu")
        result = analyze_logs(log_path)
        if "error" in result:
            print("Hata:", result["error"])
        else:
            print("En çok başarısız giriş denemesi yapan IP'ler:")
            for ip, count in result["top_failed_ips"]:
                print(f"{ip} -> {count} kez")
    elif choice == "6":
        print("Çıkış yapılıyor.")
        sys.exit(0)
    else:
        print("Geçersiz seçim. Lütfen 1-6 arasında bir değer girin.")

# -------------------------------
# Çalıştırma
# -------------------------------
if __name__ == "__main__":
    while True:
        main_menu()
        print("")
