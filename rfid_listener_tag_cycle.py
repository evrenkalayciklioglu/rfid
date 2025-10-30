#!/usr/bin/env python3
# rfid_listener_tag_cycle.py
# Behavior:
# 1. Start inventory
# 2. When a tag is read -> display info, stop reader
# 3. Wait 10s
# 4. Restart reader
# 5. Wait quietly for next tag

import time
from rfid_reader import RFIDReader
from rfid_utils import log

PORT = "/dev/ttyUSB0"
POWER_DBM = 20
POWER_BYTE = 0x14
USER_COOLDOWN = 10.0

def lookup_runner_info(epc_hex: str):
    # placeholder: here you can later integrate API/DB lookup
    return {
        "epc": epc_hex,
        "bib": epc_hex[-6:],
        "name": "Ali Veli",
        "age_group": "35-39",
        "course": "50K"
    }

def display_runner(info: dict):
    print("===================================")
    print("✅ TAG OKUNDU — KOŞUCU BİLGİLERİ")
    print(f"  EPC      : {info.get('epc')}")
    print(f"  Bib No   : {info.get('bib')}")
    print(f"  Name     : {info.get('name')}")
    print(f"  Age Group: {info.get('age_group')}")
    print(f"  Course   : {info.get('course')}")
    print("===================================\n")

def main():
    reader = RFIDReader(port=PORT)
    if not reader.connect():
        print("❌ Unable to open serial port.")
        return

    print(f"✅ Connected to {PORT}")
    print("📡 Ready — waiting for a tag...")

    reader.send_command(0x76, bytes([POWER_BYTE]))  # set power 20 dBm
    reader.send_command(0x93)                       # clear buffer

    buffer = bytearray()
    active_inventory = False

    try:
        while True:
            # Eğer inventory aktif değilse başlat
            if not active_inventory:
                reader.send_command(0x89, bytes([0x01]))  # single round
                active_inventory = True
                buffer.clear()

            # gelen veriyi oku
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

                    # Tag bulundu
                    if pkt[3] == 0x89 and len(pkt) > 8:
                        epc = pkt[6:-2].hex().upper()
                        if epc:
                            info = lookup_runner_info(epc)
                            display_runner(info)
                            log(f"[TAG] EPC={epc}")

                            # Reader'ı durdur
                            reader.send_command(0x8A)  # stop inventory (RF off)
                            active_inventory = False

                            # Bekleme süresi
                            time.sleep(USER_COOLDOWN)
                            print("📡 Ready again — waiting for next tag...\n")

            time.sleep(0.01)

    except KeyboardInterrupt:
        print("\n🛑 Stopped by user.")
    finally:
        reader.disconnect()
        print("🔌 Reader disconnected.")

if __name__ == "__main__":
    main()

