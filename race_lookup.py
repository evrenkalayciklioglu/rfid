#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
race_lookup.py
---------------
RFID'den gelen bib no'yu (bib_id.py üzerinden) dinler,
CLAX dosyasında o bib'e ait koşucu bilgilerini bulur.
"""

import sys
import subprocess
import xml.etree.ElementTree as ET
import re

def extract_engages_block(text: str) -> str:
    match = re.search(r"<Engages>.*?</Engages>", text, re.DOTALL | re.IGNORECASE)
    if not match:
        raise ValueError("❌ <Engages> bloğu bulunamadı.")
    return match.group(0)

def parse_clax(xml_content: str):
    root = ET.fromstring(xml_content)
    participants = {}
    for e in root.findall("E"):
        bib = e.get("d", "").strip()
        participants[bib] = {
            "bib_no": bib,
            "name": e.get("n", "").strip(),
            "category": e.get("ca", "").strip(),
            "course": e.get("p", "").strip(),
            "team": e.get("c", "").strip(),
            "country": e.get("na", "").strip(),
        }
    return participants

def load_clax(path: str):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        data = f.read()
    engages = extract_engages_block(data)
    return parse_clax(engages)

def show_runner(info):
    print("\n✅ Katılımcı bulundu:")
    print(f"  Ad Soyad  : {info['name']}")
    print(f"  Göğüs No  : {info['bib_no']}")
    print(f"  Kategori  : {info['category'] or '-'}")
    print(f"  Parkur    : {info['course'] or '-'}")
    print(f"  Takım     : {info['team'] or '-'}")
    print(f"  Ülke      : {info['country'] or '-'}")
    print("====================================")

def main():
    if len(sys.argv) < 2:
        print("Kullanım: python3 race_lookup.py <clax_dosyası_yolu>")
        sys.exit(1)

    clax_path = sys.argv[1]
    print(f"📁 CLAX dosyası yükleniyor: {clax_path}")
    participants = load_clax(clax_path)
    print(f"✅ {len(participants)} katılımcı yüklendi.\n")

    print("📡 RFID Reader dinleniyor (Ctrl+C ile çık)...")
    # bib_id.py çıktısını sürekli okuyacağız
    with subprocess.Popen(
        ["python3", "-u", "bib_id.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    ) as proc:
        try:
            for line in proc.stdout:
                bib = line.strip()
                if not bib.isdigit():
                    continue
                print(f"\n🏷️  Okunan BIB: {bib}")
                runner = participants.get(bib)
                if runner:
                    show_runner(runner)
                else:
                    print(f"⚠️  {bib} numaralı katılımcı CLAX içinde bulunamadı.")
        except KeyboardInterrupt:
            print("\n🛑 Kullanıcı tarafından durduruldu.")
        finally:
            proc.terminate()

if __name__ == "__main__":
    main()

