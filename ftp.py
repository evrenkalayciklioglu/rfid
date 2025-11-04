#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import json
import time
from ftplib import FTP
from datetime import datetime

# -----------------------------
# CONFIG DOSYASI
# -----------------------------
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

# -----------------------------
# CONFIG OKUMA
# -----------------------------
def read_config():
    if not os.path.exists(CONFIG_FILE):
        print("[WARN] config.json bulunamadı, FTP bağlantısı yapılamıyor.")
        return {}
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERROR] config.json okunamadı: {e}")
        return {}

# -----------------------------
# FTP İNDİRME İŞLEVİ
# -----------------------------
def download_clax():
    cfg = read_config()

    ftp_host = cfg.get("ftp_host", "").strip()
    ftp_user = cfg.get("ftp_user", "").strip()
    ftp_pass = cfg.get("ftp_pass", "").strip()
    ftp_path = cfg.get("ftp_path", "").strip()
    clax_filename = cfg.get("clax_filename", "").strip()

    if not all([ftp_host, ftp_user, ftp_pass, clax_filename]):
        print("[INFO] FTP yapılandırması eksik. Yeniden denenecek...")
        return

    # Dosyayı çalıştırılan dizine indir
    dest_path = os.path.join(os.getcwd(), clax_filename)

    try:
        ftp = FTP(ftp_host, timeout=15)
        ftp.login(user=ftp_user, passwd=ftp_pass)

        # Alt dizine geç (varsa)
        if ftp_path and ftp_path != "/":
            ftp.cwd(ftp_path)

        # Binary modda indir
        ftp.voidcmd('TYPE I')

        with open(dest_path, "wb") as f:
            ftp.retrbinary(f"RETR " + clax_filename, f.write)

        ftp.quit()

        # Boyutu göster
        size = os.path.getsize(dest_path)
        kb = round(size / 1024, 1)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [OK] {ftp_path}/{clax_filename} indirildi → {dest_path} ({kb} KB)")

    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [ERROR] FTP bağlantı hatası: {e}")

# -----------------------------
# ANA DÖNGÜ
# -----------------------------
def main():
    print("[INIT] FTP indirme servisi başlatıldı.")
    while True:
        download_clax()
        time.sleep(90)

# -----------------------------
# GİRİŞ NOKTASI
# -----------------------------
if __name__ == "__main__":
    main()

