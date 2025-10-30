from rfid_reader import RFIDReader
from rfid_utils import log

def on_tag(packet):
    print(f"[{packet['timestamp']}] EPC={packet['epc']} RSSI={packet['rssi']}dBm Ant={packet['antenna']}")

def main():
    reader = RFIDReader(port="/dev/ttyUSB0")
    if not reader.connect():
        print("❌ Unable to open serial port.")
        return
    try:
        # --- Power 26dBm + ETSI band + buffer reset + S1 taraması ---
        reader.send_command(0x76, bytes([0x1A]))  # Power 26 dBm
        region = 0x04
        freq_space = 20
        qty = 16
        start_khz = 865000
        start_hex = start_khz.to_bytes(3, 'big')
        reader.send_command(0x78, bytes([region, freq_space, qty]) + start_hex)
        reader.send_command(0x85, bytes([0x01]))  # EPC match clear
        reader.send_command(0x93)                 # Buffer reset
        reader.send_command(0x8B, bytes([0x01, 0x00, 0x08]))  # Session S1 A
        reader.send_command(0x8B, bytes([0x01, 0x01, 0x08]))  # Session S1 B

        reader.listen_realtime_inventory(callback=on_tag)
    except KeyboardInterrupt:
        print("\n🛑 Stopping...")
        reader.disconnect()
        log("[INFO] Reader stopped by user.")

if __name__ == "__main__":
    main()

