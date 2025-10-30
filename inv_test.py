#!/usr/bin/env python3
import serial, binascii, time

PORT = "/dev/ttyUSB0"
BAUDRATE = 115200

def checksum(data):
    cs = 0
    for b in data:
        cs ^= b
    return cs

def main():
    with serial.Serial(PORT, BAUDRATE, timeout=0.5) as ser:
        # Typical SB19 / AA-protocol inventory command:
        cmd = bytes.fromhex("AA002700000000")  # Start Inventory
        cmd = cmd[:-1] + bytes([checksum(cmd[:-1])])
        print(f"[TX] {binascii.hexlify(cmd).decode()}")
        ser.write(cmd)
        ser.flush()
        time.sleep(0.5)
        resp = ser.read_all()
        if resp:
            print(f"[RX] {binascii.hexlify(resp).decode()}")
        else:
            print("[NO RESPONSE]")

if __name__ == "__main__":
    main()

