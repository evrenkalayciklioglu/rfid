#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import serial, time, binascii

PORT = "/dev/ttyUSB0"
BAUDRATE = 115200
ORG_ID = "1CF"
RACE_ID = "12D8"
BIB_DECIMAL = 222

def build_epc(org_id, race_id, bib_number):
    bib_hex = format(bib_number, '08X')
    epc = f"000{org_id}{race_id}{bib_hex}"
    print(f"[EPC] {epc}")
    return bytes.fromhex(epc)

def send_cmd(ser, data):
    ser.write(data)
    ser.flush()
    time.sleep(0.3)
    resp = ser.read_all()
    if resp:
        print(f"[RX] {binascii.hexlify(resp).decode()}")
    else:
        print("[NO RESPONSE]")

def checksum(data: bytes) -> int:
    cs = 0
    for b in data:
        cs ^= b
    return cs

def rf_off_cmd():
    raw = b'\xA0\x03\x00\x00\xFF\x00'
    return raw + bytes([checksum(raw)])

def rf_on_cmd():
    raw = b'\xA0\x03\x00\x00\xFF\x01'
    return raw + bytes([checksum(raw)])

def build_write_epc(epc_bytes):
    antenna = 0x01
    access_pwd = bytes.fromhex("00000000")
    mem_bank = 0x01  # EPC
    word_ptr = 0x02
    word_count = len(epc_bytes) // 2

    payload = bytearray()
    payload += b'\x82\x00\xFF'
    payload += bytes([antenna])
    payload += access_pwd
    payload += bytes([mem_bank])
    payload += bytes([word_ptr])
    payload += bytes([word_count])
    payload += epc_bytes

    cmd = bytearray()
    cmd += b'\xA0'
    cmd += bytes([len(payload)])
    cmd += payload
    cmd.append(checksum(cmd))
    print(f"[TX] {binascii.hexlify(cmd).decode()}")
    return bytes(cmd)

def main():
    epc_bytes = build_epc(ORG_ID, RACE_ID, BIB_DECIMAL)
    cmd_rf_off = rf_off_cmd()
    cmd_rf_on  = rf_on_cmd()
    cmd_write  = build_write_epc(epc_bytes)

    with serial.Serial(PORT, BAUDRATE, timeout=0.5) as ser:
        print(f"[INFO] Connected to {PORT}")

        print("[STEP] RF OFF")
        send_cmd(ser, cmd_rf_off)
        time.sleep(0.5)

        print("[STEP] RF ON")
        send_cmd(ser, cmd_rf_on)
        time.sleep(0.5)

        print("[STEP] WRITE EPC")
        send_cmd(ser, cmd_write)
        print("[DONE] Write command sent.")

if __name__ == "__main__":
    main()

