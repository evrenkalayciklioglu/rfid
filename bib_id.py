#!/usr/bin/env python3
import os
import sys

BIB_LIST_FILE = "bib_list.txt"
CURSOR_FILE = ".bib_cursor"

def next_bib():
    if not os.path.exists(BIB_LIST_FILE):
        return None

    with open(BIB_LIST_FILE, "r", encoding="utf-8") as f:
        bibs = [x.strip() for x in f if x.strip()]

    if not bibs:
        return None

    # kaldığı yeri oku
    index = 0
    if os.path.exists(CURSOR_FILE):
        try:
            index = int(open(CURSOR_FILE).read().strip())
        except Exception:
            index = 0

    # sıradaki bib'i seç
    bib = bibs[index % len(bibs)]

    # bir sonrakine ilerlet
    with open(CURSOR_FILE, "w", encoding="utf-8") as f:
        f.write(str((index + 1) % len(bibs)))

    return bib


if __name__ == "__main__":
    bib = next_bib()
    if bib:
        print(bib)
        sys.exit(0)
    else:
        # dosya yoksa ya da boşsa, normal RFID koduna geç
        try:
            from bib_id_real import main as real_main
            real_main()
        except Exception as e:
            sys.stderr.write(f"[bib_id] Error: {e}\n")
            sys.exit(1)

