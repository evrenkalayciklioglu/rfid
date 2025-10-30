#!/usr/bin/env python3
# rfid_listener_userflow.py
# Continuous "check station" behavior:
# - set power = 20 dBm
# - always-on listener (auto-restart inventory if reader idle)
# - when a tag is read -> lookup & display runner info
# - ignore all subsequent tags for USER_COOLDOWN seconds (global)

import time
from rfid_reader import RFIDReader
from rfid_utils import log

# CONFIG
PORT = "/dev/ttyUSB0"
POWER_DBM = 20                # 20 dBm
POWER_BYTE = 0x14             # hex for 20
RESTART_INTERVAL = 2.5        # if reader silent this long, restart inventory
USER_COOLDOWN = 10.0          # after serving one user, wait this many seconds for next
EPG_COOLDOWN = 1.0            # per-epc de-bounce (within same session read)

def lookup_runner_info(epc_hex: str):
    """
    Replace this stub with a real server call or DB lookup.
    Return a dict with fields to show on screen.
    """
    # EXAMPLE: pretend we query local DB or HTTP API
    # response = requests.get(f"https://race.example/api/tag/{epc_hex}")
    # return response.json()
    # For now return demo data:
    return {
        "epc": epc_hex,
        "bib": epc_hex[-6:],                # fake bib from epc tail
        "name": "Ali Veli",
        "age_group": "35-39",
        "course": "50K"
    }

def display_runner(info: dict):
    """
    Show the runner details. Adapt to GUI or HTTP upload as needed.
    """
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
    print("📡 Check-station running. After each read, next user allowed after", USER_COOLDOWN, "s")

    # set power once
    reader.send_command(0x76, bytes([POWER_BYTE]))
    # clear buffer initial
    reader.send_command(0x93)

    buffer = bytearray()
    per_epc_seen = {}     # epc => last_seen_time (for micro-debounce)
    last_rx = time.time()
    last_user_served_at = 0.0
    user_block_until = 0.0

    try:
        # We will use looped 0x89 single-shot triggers (to avoid long continuous bug)
        while True:
            now = time.time()
            # If reader idle for a while, (re)trigger a short inventory
            if now - last_rx > RESTART_INTERVAL:
                reader.send_command(0x89, bytes([0x01]))  # single inventory round
                last_rx = now

            # read all available
            n = reader.ser.in_waiting
            if n:
                data = reader.ser.read(n)
                buffer.extend(data)
                last_rx = time.time()

                # parse packets from buffer
                while len(buffer) > 5:
                    if buffer[0] != 0xA0:
                        buffer.pop(0)
                        continue
                    length = buffer[1]
                    end = 2 + length
                    if len(buffer) < end:
                        break
                    pkt = bytes(buffer[:end])
                    del buffer[:end]

                    # only process inventory packets (0x89), ignore others
                    if pkt[3] == 0x89 and len(pkt) > 8:
                        epc = pkt[6:-2].hex().upper()
                        if not epc:
                            continue

                        # micro-debounce same epc spam
                        t = time.time()
                        last_epc = per_epc_seen.get(epc, 0)
                        if t - last_epc < EPG_COOLDOWN:
                            continue
                        per_epc_seen[epc] = t

                        # if currently in global user-cooldown, ignore and continue
                        if t < user_block_until:
                            # optionally log ignored epc
                            # log(f"[IGNORED] {epc} during user-cooldown")
                            continue

                        # Serve this runner: lookup & display
                        info = lookup_runner_info(epc)
                        display_runner(info)
                        log(f"[SERVE] EPC={epc} BIB={info.get('bib')}")

                        # set global cooldown so next user must wait USER_COOLDOWN seconds
                        user_block_until = time.time() + USER_COOLDOWN

            else:
                time.sleep(0.01)

    except KeyboardInterrupt:
        print("\n🛑 Stopped by user.")
    finally:
        reader.disconnect()
        print("🔌 Reader disconnected.")

if __name__ == "__main__":
    main()

