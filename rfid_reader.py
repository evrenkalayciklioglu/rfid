import serial
import time
from rfid_utils import build_command, parse_inventory_packet, log

class RFIDReader:
    def __init__(self, port="/dev/ttyUSB0", baud=115200, address=0xFF):
        self.port = port
        self.baud = baud
        self.address = address
        self.ser = None
        self.running = False

    def connect(self):
        self.ser = serial.Serial(self.port, self.baud, timeout=0.1)
        if self.ser.is_open:
            log(f"[INFO] Connected to {self.port} at {self.baud} bps.")
            return True
        else:
            log("[ERROR] Serial port failed to open.")
            return False

    def disconnect(self):
        self.running = False
        if self.ser:
            self.ser.close()
            log("[INFO] Serial port closed.")

    def send_command(self, cmd, data=b''):
        frame = build_command(self.address, cmd, data)
        self.ser.write(frame)
        log(f"[TX] {frame.hex(' ').upper()}")

    def listen_realtime_inventory(self, callback=None):
        self.send_command(0x89, bytes([0x01]))  # Repeat=1
        self.running = True
        log("[INFO] Listening for tag responses...")
        while self.running:
            raw = self.ser.read_all()
            if raw:
                log(f"[RX] {raw.hex(' ').upper()}")
                packet = parse_inventory_packet(raw)
                if packet:
                    log(f"[TAG] EPC={packet['epc']} RSSI={packet['rssi']}dBm ANT={packet['antenna']}")
                    if callback:
                        callback(packet)
            time.sleep(0.05)

