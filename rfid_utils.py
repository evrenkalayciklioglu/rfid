# rfid_utils.py
import datetime

def calc_checksum(data: bytes) -> int:
    """RX checksum = (~sum(data)) + 1"""
    return ((~sum(data)) + 1) & 0xFF

def build_command(address: int, cmd: int, data: bytes = b'') -> bytes:
    """
    SB19 UHF Reader frame:
    Head(0xA0) | Len | Address | Cmd | Data... | Check
    Len = total_bytes - 2
    """
    length = 2 + len(data)  # address + cmd + data
    frame_wo_check = bytes([0xA0, length, address, cmd]) + data
    check = calc_checksum(frame_wo_check[1:])
    return frame_wo_check + bytes([check])

def parse_inventory_packet(packet: bytes):
    """
    Parse 0x89 real-time inventory packet.
    Expected: A0 xx FF 89 [FreqAnt][PC][EPC...][RSSI][Check]
    """
    if len(packet) < 10 or packet[0] != 0xA0:
        return None
    cmd = packet[3]
    if cmd != 0x89:
        return None

    try:
        freq_ant = packet[4]
        antenna_id = freq_ant & 0x03
        rssi = packet[-2]
        epc_data = packet[6:-2]  # Skip FreqAnt + PC(2)
        epc_hex = epc_data.hex().upper()
        return {
            "antenna": antenna_id,
            "rssi": rssi_to_dbm(rssi),
            "epc": epc_hex,
            "timestamp": datetime.datetime.now().isoformat(timespec="seconds")
        }
    except Exception:
        return None

def rssi_to_dbm(rssi_byte: int) -> int:
    """Approximate RSSI mapping from table"""
    return -70 + (rssi_byte - 90)  # roughly scale

def log(message: str):
    """Simple timestamped log writer"""
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(f"logs/rfid_{datetime.date.today()}.log", "a") as f:
        f.write(f"{ts} - {message}\n")

