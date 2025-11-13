DEBUG=True
from flask import Flask, render_template, request, redirect, url_for, flash
import os, json, threading, time
import subprocess
from ftplib import FTP
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "change_this_secret"

CONFIG_FILE = "config.json"
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
DEST_DIR = os.path.join(os.path.dirname(__file__), "clax_files")
os.makedirs(DEST_DIR, exist_ok=True)

# -----------------------------
# CONFIG YÖNETİMİ
# -----------------------------
def read_config():
    if not os.path.exists(CONFIG_FILE):
        return {"ftp_host": "", "ftp_user": "", "ftp_pass": "", "ftp_path": "", "clax_filename": ""}
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def write_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=2)

# -----------------------------
# FTP İNDİRME İŞLEMLERİ
# -----------------------------
def ftp_download_loop():
    """Arka planda sürekli FTP'den CLAX dosyasını indirir."""
    while True:
        cfg = read_config()
        if not cfg.get("ftp_host") or not cfg.get("clax_filename"):
            print("[INFO] FTP bilgisi eksik, bekleniyor...")
        else:
            filename = cfg["clax_filename"]
            ftp_path = cfg.get("ftp_path", "/")
            # 💡 Çalıştırıldığı dizine kaydet
            dest = os.path.join(os.getcwd(), filename)
            try:
                ftp = FTP(cfg["ftp_host"], timeout=10)
                ftp.login(cfg["ftp_user"], cfg["ftp_pass"])

                if ftp_path and ftp_path != "/":
                    ftp.cwd(ftp_path)

                # Binary mode
                ftp.voidcmd('TYPE I')

                # Dosyayı indir
                with open(dest, "wb") as f:
                    ftp.retrbinary(f"RETR " + filename, f.write)

                ftp.quit()

                # Boyutu göster
                size = os.path.getsize(dest)
                kb = round(size / 1024, 1)
                print(f"[OK] {ftp_path}/{filename} indirildi → {dest} ({kb} KB)")

            except Exception as e:
                print(f"[ERROR] FTP bağlantı hatası: {e}")

        time.sleep(90)

def start_background_tasks():
    """Gunicorn altında sadece 1 kez başlat."""
    if not any(t.name == "ftp_thread" for t in threading.enumerate()):
        t = threading.Thread(target=ftp_download_loop, name="ftp_thread", daemon=True)
        t.start()
        print("[INIT] FTP background thread başlatıldı.")

# -----------------------------
# FLASK ROUTE'ları
# -----------------------------
@app.route("/admin", methods=["GET", "POST"])
def admin():
    config = read_config()

    # Silme isteği (GET parametresiyle gelir)
    delete_file = request.args.get("delete")
    if delete_file in ["sponsor_logo.png", "race_logo.png"]:
        try:
            path = os.path.join(STATIC_DIR, delete_file)
            if os.path.exists(path):
                os.remove(path)
                flash(f"{delete_file} silindi.", "success")
            else:
                flash(f"{delete_file} bulunamadı.", "warning")
        except Exception as e:
            flash(f"{delete_file} silinemedi: {e}", "error")
        return redirect(url_for("admin"))

    if request.method == "POST":
        config["ftp_host"] = request.form.get("ftp_host", "").strip()
        config["ftp_user"] = request.form.get("ftp_user", "").strip()
        config["ftp_pass"] = request.form.get("ftp_pass", "").strip()
        config["ftp_path"] = request.form.get("ftp_path", "").strip()
        config["clax_filename"] = request.form.get("clax_filename", "").strip()

        for field, target in [
            ("sponsor_logo", "sponsor_logo.png"),
            ("race_logo", "race_logo.png")
        ]:
            file = request.files.get(field)
            if file and file.filename:
                save_path = os.path.join(STATIC_DIR, target)
                file.save(save_path)
                flash(f"{target} yüklendi.", "success")

        write_config(config)
        try:
            subprocess.run(["sudo", "systemctl", "restart", "rfid-web.service"], check=True)
            flash("rfid-web.service başarıyla yeniden başlatıldı.", "success")
        except subprocess.CalledProcessError as e:
            flash(f"Servis yeniden başlatılamadı: {e}", "error")
        flash("Ayarlar güncellendi.", "success")
        return redirect(url_for("admin"))

    # Dosyalar var mı, template'e gönder
    sponsor_exists = os.path.exists(os.path.join(STATIC_DIR, "sponsor_logo.png"))
    race_exists = os.path.exists(os.path.join(STATIC_DIR, "race_logo.png"))

    return render_template("admin.html", config=config,
                           sponsor_exists=sponsor_exists,
                           race_exists=race_exists)


@app.route("/")
def index():
    return render_template("index.html")

# -----------------------------
#  💡 GÜNCEL GUNICORN / FLASK 3 UYUMU
# -----------------------------
# Gunicorn uygulamayı import ettiğinde bu blok çalışır
start_background_tasks()

# Flask local run için
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

