# rfid_listener.py
# Continuous RFID reader (streaming mode, low latency)

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
    print("📡 Real-time scanning... (Ctrl+C to stop)")

    reader.send_command(0x76, bytes([0x1A]))  # Power 26 dBm
    reader.send_command(0x93)                 # Buffer reset
    reader.send_command(0x89, bytes([0xFF]))  # Start continuous inventory

    buffer = bytearray()
    seen = {}
    cooldown = 1.0  # same tag cooldown (seconds)

    try:
        while True:
            n = reader.ser.in_waiting
            if n:
                data = reader.ser.read(n)
                buffer.extend(data)

                # Paket başlangıcı/bitişi kontrolü
                while True:
                    if len(buffer) < 5:
                        break
                    if buffer[0] != 0xA0:
                        buffer.pop(0)
                        continue

                    length = buffer[1]
                    end = 2 + length
                    if len(buffer) < end:
                        break  # incomplete packet

                    pkt = buffer[:end]
                    del buffer[:end]

                    # parse only inventory (0x89)
                    if pkt[3] == 0x89 and len(pkt) > 8:
                        epc = pkt[6:-2].hex().upper()
                        if epc:
                            now = time.time()
                            if epc not in seen or now - seen[epc] > cooldown:
                                seen[epc] = now
                                print(f"🏷️  EPC: {epc}")
            else:
                time.sleep(0.01)

    except KeyboardInterrupt:
        print("\n🛑 Stopped by user.")
    finally:
        reader.disconnect()
        print("🔌 Reader disconnected.")

if __name__ == "__main__":
    main()

