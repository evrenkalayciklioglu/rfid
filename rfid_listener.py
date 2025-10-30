# rfid_listener.py
# Continuous RFID reader for bib chip quick check stations
# Runs indefinitely until user stops (Ctrl + C)

import time
from rfid_reader import RFIDReader
from rfid_utils import log

def main():
    port = "/dev/ttyUSB0"
    reader = RFIDReader(port=port)
    if not reader.connect():
        print("❌ Unable to open serial port.")
        return

    print(f"✅ Connected to {port}")
    print("📡 Waiting for tags... (press Ctrl+C to stop)")

    # --- temel ayarlar ---
    reader.send_command(0x76, bytes([0x1A]))  # Power 26 dBm
    reader.send_command(0x93)                 # Clear buffer

    seen = {}
    cooldown = 1.0  # aynı EPC’yi 1 saniye içinde tekrar gösterme

    try:
        reader.send_command(0x89, bytes([0xFF]))  # Real-time continuous inventory
        while True:
            raw = reader.ser.read_all()
            if not raw:
                time.sleep(0.05)
                continue

            # Veri içindeki tüm EPC'leri ara
            i = 0
            while i < len(raw):
                if raw[i] == 0xA0:
                    if i + 4 < len(raw):
                        ln = raw[i + 1]
                        cmd = raw[i + 3]
                        end = i + 2 + ln
                        if end <= len(raw) and cmd == 0x89:
                            payload = raw[i + 6:end - 2]
                            epc = payload.hex().upper()
                            if epc:
                                now = time.time()
                                if epc not in seen or now - seen[epc] > cooldown:
                                    seen[epc] = now
                                    print(f"🏷️  EPC: {epc}")
                        i = end
                    else:
                        break
                else:
                    i += 1

    except KeyboardInterrupt:
        print("\n🛑 Stopped by user.")
    finally:
        reader.disconnect()
        print("🔌 Reader disconnected.")

if __name__ == "__main__":
    main()

