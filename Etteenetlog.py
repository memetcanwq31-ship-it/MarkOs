#!/usr/bin/env python3
"""
Etternetlog Güvenlik Araçları Paketi Oluşturucu
Güvenli, eğitim amaçlı araçlar içeren bir paket üretir (zararlı içerik içermez).
"""

import os
import zipfile

BASE_PATH = os.environ.get("ETNET_BASE", "/mnt/agents/output/etternetlog")

CYBERSEC_DIR = os.path.join(BASE_PATH, "cybersec_tools")
PENTEST_DIR = os.path.join(BASE_PATH, "pentest_tools")
CUSTOM_DIR = os.path.join(BASE_PATH, "custom_tools")

os.makedirs(CYBERSEC_DIR, exist_ok=True)
os.makedirs(PENTEST_DIR, exist_ok=True)
os.makedirs(CUSTOM_DIR, exist_ok=True)

def make_tool_content(name: str, title: str, description: str) -> str:
    return """#!/usr/bin/env python3
"""\"\"\"{title}
{description}
\"\"\""
import argparse

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--target", default="localhost")
    args = p.parse_args()
    print("[+] {title} running against", args.target)

if __name__ == "__main__":
    main()
""".format(title=title, description=description)

def write_tool(path: str, content: str):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    os.chmod(path, 0o755)

def main():
    # Cybersecurity araçları (40 adet)
    cybersec_tools = {}
    for i in range(1, 41):
        fname = f"{i:02d}_tool.py"
        title = f"Güvenlik Aracı {i:02d}"
        description = f"Eğitsel güvenlik aracı {i:02d} (gerçek güvenlik görevlerini simüle etmez)."
        cybersec_tools[fname] = make_tool_content(fname, title, description)

    for fname, content in cybersec_tools.items():
        write_tool(os.path.join(CYBERSEC_DIR, fname), content)

    # Sızma test araçları (40 adet) - simüle çıktı üreten basit araçlar
    pentest_tools = {}
    for i in range(1, 41):
        fname = f"{i:02d}_tool.py"
        title = f"Pentest Aracı {i:02d}"
        description = f"Eğitsel pentest aracı {i:02d} (simüle)."
        pentest_tools[fname] = make_tool_content(fname, title, description)

    for fname, content in pentest_tools.items():
        write_tool(os.path.join(PENTEST_DIR, fname), content)

    # Custom araçlar (örnek iki dosya)
    readme_path = os.path.join(CUSTOM_DIR, "README.txt")
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(
            "Etternetlog - Özelleştirme\n"
            "Bu klasörde kendi özel araçlarınızı ekleyebilirsiniz.\n"
            "Güvenli ve eğitim amaçlı içerikler için bu klasörü kullanın.\n"
        )
    template_path = os.path.join(CUSTOM_DIR, "template_tool.py")
    with open(template_path, "w", encoding="utf-8") as f:
        f.write("""#!/usr/bin/env python3
"""Custom Tool Template."""
import argparse

def main():
    p = argparse.ArgumentParser()
    p.add_argument("target", help="Hedef host")
    args = p.parse_args()
    print(f"[+] Custom tool running against {args.target}")

if __name__ == "__main__":
    main()
""")
    os.chmod(template_path, 0o755)

    # Arşiv oluştur
    archive_path = os.path.join(BASE_PATH, "etternetlog_suite.zip")
    with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for folder in [CYBERSEC_DIR, PENTEST_DIR, CUSTOM_DIR]:
            for root, _, files in os.walk(folder):
                for fname in files:
                    fpath = os.path.join(root, fname)
                    arcname = os.path.relpath(fpath, BASE_PATH)
                    zf.write(fpath, arcname)

    total = 40 + 40 + 2
    print(f"[+] BUILD COMPLETE: {total} araç yazıldı ve {archive_path} oluşturuldu.")

if __name__ == "__main__":
    main()
```
