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
    print("📡 RFID check station running (Ctrl+C to stop)")

    reader.send_command(0x76, bytes([0x1A]))  # Power 26 dBm
    reader.send_command(0x93)                 # Clear buffer

    seen = {}
    cooldown = 1.0  # same tag cooldown (seconds)
    buffer = bytearray()
    last_scan = 0

    try:
        while True:
            now = time.time()

            # Her 2 saniyede bir taramayı yeniden başlat
            if now - last_scan > 2:
                reader.send_command(0x89, bytes([0x01]))  # tek seferlik inventory
                last_scan = now

            n = reader.ser.in_waiting
            if n:
                data = reader.ser.read(n)
                buffer.extend(data)

                # Paketleri ayrıştır
                while len(buffer) > 5:
                    if buffer[0] != 0xA0:
                        buffer.pop(0)
                        continue
                    length = buffer[1]
                    end = 2 + length
                    if len(buffer) < end:
                        break
                    pkt = buffer[:end]
                    del buffer[:end]

                    if pkt[3] == 0x89 and len(pkt) > 8:
                        epc = pkt[6:-2].hex().upper()
                        if epc:
                            t = time.time()
                            if epc not in seen or t - seen[epc] > cooldown:
                                seen[epc] = t
                                print(f"🏷️ EPC: {epc}")

            time.sleep(0.05)

    except KeyboardInterrupt:
        print("\n🛑 Stopped by user.")
    finally:
        reader.disconnect()
        print("🔌 Reader disconnected.")

if __name__ == "__main__":
    main()

