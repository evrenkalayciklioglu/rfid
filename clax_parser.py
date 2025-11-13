#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLAX Participant Parser
-----------------------
Verilen CLAX XML dosyasından <Engages> içindeki katılımcıları okur.
Belirtilen bib_no (d attribute) ile eşleşen kişiyi döndürür.

Kullanım:
    python3 clax_parser.py /path/to/file.clax 222
"""

import sys
import re
import xml.etree.ElementTree as ET

def extract_engages_block(text: str) -> str:
    """
    CLAX dosyasında sadece <Engages>...</Engages> bölümünü ayıklar.
    Dosyanın başında/sonunda başka içerik olabilir.
    """
    match = re.search(r"<Engages>.*?</Engages>", text, re.DOTALL | re.IGNORECASE)
    if not match:
        raise ValueError("❌ <Engages> bloğu bulunamadı.")
    return match.group(0)

def parse_clax(xml_content: str):
    """
    <Engages> XML bloğundaki tüm <E> elemanlarını parse eder.
    """
    root = ET.fromstring(xml_content)
    participants = []
    for e in root.findall("E"):
        participant = {
            "bib_no": e.get("d", "").strip(),
            "name": e.get("n", "").strip(),
            "category": e.get("ca", "").strip(),
            "course": e.get("p", "").strip(),
            "team": e.get("c", "").strip(),
            "country": e.get("na", "").strip(),
            "birthyear": e.get("a", "").strip(),
        }
        participants.append(participant)
    return participants

def find_participant_by_bib(participants, bib_no: str):
    """
    Bib numarasına göre katılımcıyı döndürür.
    """
    for p in participants:
        if p["bib_no"] == str(bib_no):
            return p
    return None

def main():
    if len(sys.argv) < 3:
        print("Kullanım: python3 clax_parser.py <dosya_yolu> <bib_no>")
        sys.exit(1)

    clax_path = sys.argv[1]
    bib_no = sys.argv[2]

    with open(clax_path, "r", encoding="utf-8", errors="ignore") as f:
        raw_data = f.read()

    engages_block = extract_engages_block(raw_data)
    participants = parse_clax(engages_block)
    result = find_participant_by_bib(participants, bib_no)

    if result:
        print("✅ Katılımcı bulundu:")
        print(f"  Ad Soyad  : {result['name']}")
        print(f"  Göğüs No  : {result['bib_no']}")
        print(f"  Kategori  : {result['category'] or '-'}")
        print(f"  Parkur    : {result['course'] or '-'}")
        print(f"  Takım     : {result['team'] or '-'}")
        print(f"  Ülke      : {result['country'] or '-'}")
    else:
        print(f"⚠️  {bib_no} numaralı katılımcı bulunamadı.")

if __name__ == "__main__":
    main()

