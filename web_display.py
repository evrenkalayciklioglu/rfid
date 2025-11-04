#!/usr/bin/env python3
import time, subprocess, threading, atexit, re, xml.etree.ElementTree as ET
from flask import Flask, jsonify, render_template
import mimetypes
mimetypes.add_type('text/css', '.css')
from config_utils import read_config


#CLAX_PATH = "efes_ultra_2025.clax"
RFID_SCRIPT = "bib_id.py"
TIMEOUT = 60

app = Flask(__name__, static_folder='static', template_folder='templates')
#app = Flask(__name__)
last_runner = {"time": 0, "data": None}

cfg = read_config()
CLAX_PATH = cfg.get("clax_filename")

def extract_engages_block(text):
    m = re.search(r"<Engages>.*?</Engages>", text, re.DOTALL | re.IGNORECASE)
    if not m:
        raise ValueError("<Engages> bloğu bulunamadı.")
    return m.group(0)

def parse_clax(xml_text):
    import xml.etree.ElementTree as ET

    root = ET.fromstring(xml_text)
    result = {}

    for e in root.findall("E"):
        bib = e.get("d", "").strip()
        gender_raw = e.get("x", "").strip().lower()

        # Normalize gender (farklı yazımlara toleranslı)
        if gender_raw in ["m", "male", "man"]:
            gender_tr = "Erkek"
            gender_en = "Man"
        elif gender_raw in ["f", "w", "woman", "female"]:
            gender_tr = "Kadın"
            gender_en = "Woman"
        else:
            gender_tr = ""
            gender_en = ""

        result[bib] = {
            "bib_no": bib,
            "name": e.get("n", "").strip(),
            "category": e.get("ca", "").strip(),
            "course": e.get("p", "").strip(),
            "team": e.get("c", "").strip(),
            "country": e.get("na", "").strip(),
            "gender": f"{gender_tr} / {gender_en}" if gender_tr else "",
        }

    return result

def load_clax(path):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        xml_data = extract_engages_block(f.read())
    return parse_clax(xml_data)

def get_result_from_clax(bib_no):
    """Resultats bloğu içinde bib_no'ya ait t ve b değerlerini bulur"""
    try:
        with open(CLAX_PATH, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
        m = re.search(r"<Resultats>.*?</Resultats>", text, re.DOTALL | re.IGNORECASE)
        if not m:
            return "", ""
        xml_part = m.group(0)
        root = ET.fromstring(xml_part)
        for r in root.findall("R"):
            if r.get("d", "").strip() == bib_no:
                return r.get("t", "").strip(), r.get("b", "").strip()
    except Exception as e:
        print(f"[WARN] Resultats parse hatası: {e}")
    return "", ""

participants = load_clax(CLAX_PATH)
print(f"✅ {len(participants)} katılımcı yüklendi.")

def reader_thread():
    global last_runner
    print("[INFO] RFID reader thread başladı.")
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
               # CLAX içinden sonuçları da oku
               t_val, b_val = get_result_from_clax(bib)
               if t_val or b_val:
                   runner["status"] = "Tamamlandı / Finished"
                   runner["time_total"] = t_val
                   runner["finish_time"] = b_val
               else:
                   runner["status"] = "Yarışınız tamamlanmadı. / Your race is not complete."
                   runner["time_total"] = ""
                   runner["finish_time"] = ""

               last_runner["time"] = time.time()
               last_runner["data"] = runner
               print(f"[INFO] Yeni runner: {runner['name']} (BIB {bib}) -> t={t_val}, b={b_val}")

            else:
                print(f"[WARN] BIB {bib} CLAX içinde bulunamadı.")

def start_reader_thread_once():
    global _reader_started
    if globals().get("_reader_started"):
        return
    t = threading.Thread(target=reader_thread, daemon=True)
    t.start()
    print("[INFO] RFID listener thread started (universal init).")
    _reader_started = True
    atexit.register(lambda: print("[INFO] RFID thread stopped."))

start_reader_thread_once()

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

