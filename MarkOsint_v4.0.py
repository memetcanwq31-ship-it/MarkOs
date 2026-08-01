import os
import sys
import socket
import time
import threading
import json
import random
import re

# Renklendirme fonksiyonları (Kütüphane bağımlılığını azaltmak için ham ANSI kodları)
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
WHITE = "\033[97m"
RESET = "\033[0m"

SÜRÜM = "2026.1.4.9"
DB_DOSYASI = "markos_net_logs.json"
analiz_sayaci = 0
test_calisiyor = False

def ekran_temizle():
    os.system("clear" if os.name != "nt" else "cls")

def station_banner():
    ekran_temizle()
    print(f"""{RED}
  ███╗   ███╗ █████╗ ██████╗ ██╗  ██╗ ██████╗ ███████╗
  ████╗ ████║██╔══██╗██╔══██╗██║ ██╔╝██╔═══██╗██╔════╝
  ██╔████╔██║███████║██████╔╝█████╔╝ ██║   ██║███████╗
  ██║╚██╔╝██║██╔══██║██╔══██╗██╔═██╗ ██║   ██║╚════██║
  ██║ ╚═╝ ██║██║  ██║██║  ██║██║  ██╗╚██████╔╝███████║
  ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝
    {YELLOW}--- MarkOs NETWORK & PACKET STATION v{SÜRÜM} ---
    {WHITE}Modüller: Socket Engine, Regex Scanner, Thread Pool, JSON DB
    {GREEN}[+] Durum: İstasyon Aktif | Log Havuzu: {DB_DOSYASI}
    """)

# ==========================================
# 🗄️ JSON VERİTABANI MOTORU
# ==========================================
def log_kaydet(hedef, islem_tipi, detaylar):
    mevcut_db = []
    if os.path.exists(DB_DOSYASI):
        try:
            with open(DB_DOSYASI, "r", encoding="utf-8") as f:
                mevcut_db = json.load(f)
        except:
            mevcut_db = []
            
    kayit = {
        "zaman_damgasi": time.strftime("%Y-%m-%d %H:%M:%S"),
        "hedef": hedef,
        "islem": islem_tipi,
        "detaylar": detaylar
    }
    mevcut_db.append(kayit)
    
    with open(DB_DOSYASI, "w", encoding="utf-8") as f:
        json.dump(mevcut_db, f, indent=4, ensure_ascii=False)

def log_goruntule():
    station_banner()
    print(f"{BLUE}[ 🗄️ MARKOS SİSTEM LOG GEÇMİŞİ ]{RESET}\n")
    if not os.path.exists(DB_DOSYASI):
        print(f"{RED}[- ] Log veritabanı henüz boş.{RESET}")
    else:
        with open(DB_DOSYASI, "r", encoding="utf-8") as f:
            print(json.dumps(json.load(f), indent=4, ensure_ascii=False))
    input(f"\n{YELLOW}Ana menüye dönmek için Enter'a basın...{RESET}")

# ==========================================
# 🔍 MODÜL 1: REGEX TABANLI VERİ VE BAĞLANTI ANALİZÖRÜ
# ==========================================
def regex_veri_analizi():
    global analiz_sayaci
    station_banner()
    print(f"{BLUE}[ 🔍 REGEX TABANLI AG VE VERI ANALIZORU ]{RESET}\n")
    
    metin = input(f"{GREEN}Analiz edilecek ham metni veya log verisini yapıştırın:\n>{RESET} ")
    
    # Düzenli İfadeler (Regex) ile kritik veri avı
    ip_sablonu = r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b"
    e_posta_sablonu = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    url_sablonu = r"https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+"
    
    bulunan_ipler = re.findall(ip_sablonu, metin)
    bulunan_mailler = re.findall(e_posta_sablonu, metin)
    bulunan_urller = re.findall(url_sablonu, metin)
    
    print(f"\n{YELLOW}[*] Regex Tarama Sonuçları:{RESET}")
    print(f"{WHITE}- Bulunan IP Adresleri   : {bulunan_ipler if bulunan_ipler else 'Yok'}")
    print(f"- Bulunan E-Postalar     : {bulunan_mailler if bulunan_mailler else 'Yok'}")
    print(f"- Bulunan URL Adresleri  : {bulunan_urller if bulunan_urller else 'Yok'}{RESET}")
    
    analiz_sayaci += 1
    log_kaydet("Yerel_Metin", "Regex_Taramasi", {
        "bulunan_ip_sayisi": len(bulunan_ipler),
        "bulunan_mail_sayisi": len(bulunan_mailler),
        "bulunan_url_sayisi": len(bulunan_urller)
    })
    input(f"\n{YELLOW}Devam etmek için Enter'a basın...{RESET}")

# ==========================================
# 🔥 MODÜL 2: KONTROLLÜ AĞ YÜKLEME VE STRES MOTORU
# ==========================================
def asenkron_paket_motoru(hedef_ip, hedef_port):
    global test_calisiyor
    # Rastgele HTTP User-Agent listesi (WAF atlatma senaryosu için)
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Mozilla/5.0 (Android; Mobile; rv:40.0)",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X)"
    ]
    
    while test_calisiyor:
        try:
            # Gerçek soket bağlantısı açılıyor
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1.5)
            s.connect((hedef_ip, hedef_port))
            
            # Dinamik ve rastgele HTTP başlık paketi oluşturma
            secilen_ua = random.choice(user_agents)
            paket = f"GET /?id={random.randint(1,9999)} HTTP/1.1\r\nHost: {hedef_ip}\r\nUser-Agent: {secilen_ua}\r\n\r\n"
            
            s.send(paket.encode("utf-8"))
            s.close()
        except socket.error:
            # Sunucu kapandıysa veya yanıt vermiyorsa kısa süreli bekleme
            time.sleep(0.1)

def network_stress_menu():
    global test_calisiyor
    station_banner()
    print(f"{BLUE}[ 🔥 KONTROLLÜ AG MUKAVEMET VE STRES TESTI ]{RESET}\n")
    
    hedef_ip = input(f"{GREEN}Hedef IP veya Alan Adı (Örn: 127.0.0.1): {RESET}").strip()
    if not hedef_ip: return
    
    try:
        hedef_port = int(input(f"{GREEN}Hedef Port (Örn: 80 veya 443): {RESET}").strip())
        thread_sayisi = int(input(f"{GREEN}Thread Pool (Eşzamanlı İşlemci) Sayısı: {RESET}").strip())
    except ValueError:
        print(f"{RED}[-] Hata: Geçersiz sayısal değer girdiniz.{RESET}")
        time.sleep(1.5)
        return

    print(f"\n{YELLOW}[*] İşlem havuzu hazırlanıyor...{RESET}")
    print(f"{YELLOW}[*] Test başlatıldı. Durdurmak için ENTER tuşuna basın.{RESET}\n")
    
    test_calisiyor = True
    threads = []
    
    # Belirtilen sayı kadar eşzamanlı iş parçacığı (Threading) başlatılıyor
    for i in range(thread_sayisi):
        t = threading.Thread(target=asenkron_paket_motoru, args=(hedef_ip, hedef_port))
        t.daemon = True
        threads.append(t)
        t.start()
        
    input(f"{RED}[🚨] TEST SÜRÜYOR. Durdurmak için Enter...{RESET}")
    test_calisiyor = False
    
    print(f"\n{GREEN}[+] Motor durduruldu. Test verileri log dosyasına yazılıyor...{RESET}")
    log_kaydet(hedef_ip, "Network_Stress_Test", {"port": hedef_port, "thread_havuzu": thread_sayisi, "durum": "Başarılı"})
    time.sleep(1.5)

# ==========================================
# 💻 ANA KONTROL PANELİ
# ==========================================
def ana_menu():
    while True:
        station_banner()
        print(f"{BLUE}[ 🛠️ ANA SEÇENEKLER MERKEZİ ]{RESET}")
        print(f"{GREEN}1 -{WHITE} Regex Tabanlı Log ve Ağ Verisi Analizörü (Kritik Veri Avı){RESET}")
        print(f"{GREEN}2 -{WHITE} Soket Tabanlı Ağ Yükleme ve Güvenlik Mukavemet Testi{RESET}")
        print(f"{GREEN}3 -{WHITE} [🗄️] MarkOs Sistem Log Geçmişini İncele (JSON Database){RESET}")
        print(f"{GREEN}0 -{WHITE} Çıkış Yap / Ana Kabuğa Dön{RESET}")
        print("-" * 65)
        
        secim = input(f"{YELLOW}MarkOs/NetStation > {RESET}").strip()
        
        if secim == "1":
            regex_veri_analizi()
        elif secim == "2":
            network_stress_menu()
        elif secim == "3":
            log_goruntule()
        elif secim == "0":
            print(f"\n{GREEN}[+] Ağ istasyonu güvenle kapatıldı. MarkOs kabuğuna dönülüyor...{RESET}")
            time.sleep(1)
            break
        else:
            print(f"{RED}[-] Bilinmeyen modül seçimi.{RESET}")
            time.sleep(1)

if __name__ == "__main__":
    ana_menu()
