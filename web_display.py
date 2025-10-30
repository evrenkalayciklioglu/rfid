#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
web_display.py
--------------
RFID okuyucudan gelen bib_no'yu CLAX dosyasında bulur ve
web arayüzünde canlı olarak gösterir.
"""

import time
import threading
import subprocess
import re
import xml.etree.ElementTree as ET
from flask import Flask, render_template, jsonify

CLAX_PATH = "efes_ultra_2025.clax"
RFID_SCRIPT = "bib_id.py"
TIMEOUT = 60  # saniye

app = Flask(__name__)
last_runner = {"time": 0, "data": None}


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


participants = load_clax(CLAX_PATH)
print(f"✅ {len(participants)} katılımcı yüklendi.")


def reader_thread():
    """bib_id.py çıktısını sürekli okur ve son koşucuyu günceller."""
    global last_runner
    with subprocess.Popen(
        ["python3", "-u", RFID_SCRIPT],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    ) as proc:
        for line in proc.stdout:
            bib = line.strip()
            if not bib.isdigit():
                continue
            print(f"[RFID] Okunan bib: {bib}")
            runner = participants.get(bib)
            if runner:
                last_runner["time"] = time.time()
                last_runner["data"] = runner


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/status")
def status():
    now = time.time()
    delta = now - last_runner["time"]
    if delta > TIMEOUT or not last_runner["data"]:
        return jsonify({"timeout": True})
    return jsonify({"timeout": False, "runner": last_runner["data"]})


if __name__ == "__main__":
    t = threading.Thread(target=reader_thread, daemon=True)
    t.start()
    app.run(host="0.0.0.0", port=8080, debug=False)

