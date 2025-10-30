# Stable buffered mode for SB19 (avoids real-time hang)
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
    print("📡 Buffered inventory mode started (Ctrl+C to stop)")

    # Bölge ve güç ayarları (bir kere yapılmalı)
    region = 0x04
    freq_space = 20
    qty = 16
    start_khz = 865000
    start_hex = start_khz.to_bytes(3, 'big')
    reader.send_command(0x78, bytes([region, freq_space, qty]) + start_hex)
    reader.send_command(0x76, bytes([0x1A]))  # Power 26 dBm
    reader.send_command(0x93)  # Clear buffer

    seen = {}
    cooldown = 1.0

    try:
        while True:
            # Inventory başlat (0x80)
            reader.send_command(0x80)
            time.sleep(0.1)
            # Buffer'daki tag'leri çek (0x91 = get_and_reset_inventory_buffer)
            reader.send_command(0x91)
            time.sleep(0.05)
            data = reader.ser.read_all()

            i = 0
            while i < len(data):
                if data[i] == 0xA0 and i + 4 < len(data):
                    ln = data[i + 1]
                    end = i + 2 + ln
                    if end > len(data):
                        break
                    pkt = data[i:end]
                    i = end
                    if pkt[3] in (0x90, 0x91) and len(pkt) > 8:
                        epc = pkt[6:-2].hex().upper()
                        if epc:
                            now = time.time()
                            if epc not in seen or now - seen[epc] > cooldown:
                                seen[epc] = now
                                print(f"🏷️ EPC: {epc}")
                else:
                    i += 1

            time.sleep(0.2)

    except KeyboardInterrupt:
        print("\n🛑 Stopped by user.")
    finally:
        reader.disconnect()
        print("🔌 Reader disconnected.")

if __name__ == "__main__":
    main()

