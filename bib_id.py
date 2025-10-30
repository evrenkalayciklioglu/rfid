#!/usr/bin/env python3
# rfid_listener_tag_cycle_rf_off.py
# Behavior:
# - Start inventory
# - When a tag is read -> print only BIB number (decimal)
# - Stop RF completely for 10 seconds
# - Restart RF after cooldown

import time
from rfid_reader import RFIDReader
from rfid_utils import log

PORT = "/dev/ttyUSB0"
POWER_DBM = 20
POWER_BYTE = 0x14
USER_COOLDOWN = 10.0

def extract_bib_decimal(epc_hex: str) -> int:
    """EPC'nin son 6 hex karakterini decimal bib numarasına çevirir."""
    tail = epc_hex[-6:]
    try:
        return int(tail, 16)
    except ValueError:
        return 0

def main():
    reader = RFIDReader(port=PORT)
    if not reader.connect():
        print("❌ Unable to open serial port.")
        return

    print(f"✅ Connected to {PORT}")
    print("📡 Ready — waiting for a tag...")

    reader.send_command(0x76, bytes([POWER_BYTE]))  # 20 dBm
    reader.send_command(0x93)                       # clear buffer

    buffer = bytearray()
    active_inventory = False

    try:
        while True:
            # Inventory aktif değilse başlat
            if not active_inventory:
                reader.send_command(0x89, bytes([0x01]))  # single scan
                active_inventory = True
                buffer.clear()

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

                    # Tag bulunduysa
                    if pkt[3] == 0x89 and len(pkt) > 8:
                        epc = pkt[6:-2].hex().upper()
                        if epc:
                            bib = extract_bib_decimal(epc)
                            print(bib)  # sadece decimal bib numarası
                            log(f"[TAG] EPC={epc} BIB={bib}")

                            # Reader'ı tamamen durdur (RF off)
                            reader.send_command(0x8A)
                            active_inventory = False

                            # 10 saniyelik RF kapalı bekleme
                            reader.ser.reset_input_buffer()
                            time.sleep(USER_COOLDOWN)

                            # Yeniden başlat
                            reader.send_command(0x93)  # clear buffer
                            reader.send_command(0x89, bytes([0x01]))
                            active_inventory = True
                            buffer.clear()

            time.sleep(0.01)

    except KeyboardInterrupt:
        print("\n🛑 Stopped by user.")
    finally:
        reader.send_command(0x8A)  # ensure RF off
        reader.disconnect()
        print("🔌 Reader disconnected.")

if __name__ == "__main__":
    main()

