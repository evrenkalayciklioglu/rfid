# rfid_listener.py
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
        reader.listen_realtime_inventory(callback=on_tag)
    except KeyboardInterrupt:
        print("\n🛑 Stopping...")
        reader.disconnect()
        log("[INFO] Reader stopped by user.")

if __name__ == "__main__":
    main()

