#!/usr/bin/env python3
# stealerparsing.py

import argparse
import subprocess
import sys
from pathlib import Path

def run(cmd: list[str]) -> int:
    try:
        proc = subprocess.run(cmd, check=False)
        return proc.returncode
    except FileNotFoundError:
        print(f"[!] Command not found: {cmd[0]}", file=sys.stderr)
        return 127
    except Exception as e:
        print(f"[!] Error running {' '.join(cmd)}: {e}", file=sys.stderr)
        return 1

def read_domains(list_path: Path) -> list[str]:
    if not list_path.exists():
        print(f"[!] File list tidak ditemukan: {list_path}", file=sys.stderr)
        sys.exit(2)
    domains: list[str] = []
    with list_path.open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            d = line.strip()
            if not d or d.startswith("#"):
                continue
            domains.append(d)
    if not domains:
        print(f"[!] Tidak ada domain valid di {list_path}", file=sys.stderr)
        sys.exit(3)
    return domains

def append_file(src: Path, dst_handle) -> int:
    try:
        with src.open("r", encoding="utf-8", errors="ignore") as f:
            data = f.read()
            if data:
                dst_handle.write(data)
                if not data.endswith("\n"):
                    dst_handle.write("\n")
                return len(data)
    except FileNotFoundError:
        return 0
    return 0

def main():
    parser = argparse.ArgumentParser(
        description="Parse stealer leaks per subdomain, gabungkan type-1..type-4, hapus file sementara, lalu convert ke CSV."
    )
    parser.add_argument("-l", "--list", default="list.txt", help="File list domain (default: list.txt)")
    parser.add_argument("-f", "--file", default="stealer.txt", help="File data stealer (default: stealer.txt)")
    args = parser.parse_args()

    list_path = Path(args.list).expanduser().resolve()
    stealer_path = Path(args.file).expanduser().resolve()

    if not stealer_path.exists():
        print(f"[!] File stealer tidak ditemukan: {stealer_path}", file=sys.stderr)
        sys.exit(4)

    domains = read_domains(list_path)

    print(f"[*] Mulai parsing {len(domains)} domain dari {list_path.name} menggunakan {stealer_path.name}")

    # Run parsingCredsLeak.py
    fail_count = 0
    for idx, subdomain in enumerate(domains, start=1):
        cmd = ["python3", "parsingCredsLeak.py", "-s", subdomain, "-f", str(stealer_path)]
        print(f"[*] ({idx}/{len(domains)}) Run: {' '.join(cmd)}")
        rc = run(cmd)
        if rc != 0:
            print(f"[!] parsingCredsLeak.py exit code {rc} untuk {subdomain}", file=sys.stderr)
            fail_count += 1

    # Gabung type-1..4 ke allsubdomain.txt
    out_file = Path("allsubdomain.txt").resolve()
    appended_bytes = 0
    appended_files = 0
    all_generated_files = []  # untuk tracking file sementara

    with out_file.open("w", encoding="utf-8") as outfh:
        for subdomain in domains:
            for t in (1, 2, 3, 4, 5):  # type-1..5 tetap ditrack untuk delete
                candidate = Path(f"{subdomain}.type-{t}.txt").resolve()
                if candidate.exists():
                    all_generated_files.append(candidate)
                if t in (1, 2, 3, 4):  # hanya 1..4 digabung
                    size = append_file(candidate, outfh)
                    if size > 0:
                        appended_bytes += size
                        appended_files += 1
                        print(f"    [+] Append: {candidate.name} ({size} bytes)")

    print(f"[*] Gabungan selesai: {appended_files} file -> {out_file.name} ({appended_bytes} bytes)")

    # Hapus semua file sementara type-1..5
    for f in all_generated_files:
        try:
            f.unlink()
            print(f"    [-] Hapus: {f.name}")
        except Exception as e:
            print(f"[!] Gagal hapus {f.name}: {e}", file=sys.stderr)

    # Jalankan txt2csv-stealer.py
    cmd_csv = ["python3", "txt2csv-stealer.py", "-d", ":| ", str(out_file)]
    print(f"[*] Run: {' '.join(cmd_csv)}")
    rc_csv = run(cmd_csv)
    if rc_csv != 0:
        print(f"[!] txt2csv-stealer.py exit code {rc_csv}", file=sys.stderr)
        sys.exit(rc_csv)

    print("\n[+] Ringkasan:")
    print(f"    - Domain diproses : {len(domains)}")
    print(f"    - Gagal parsing   : {fail_count}")
    print(f"    - File digabung   : {appended_files}")
    print(f"    - Output gabungan : {out_file.name}")
    print("    - CSV             : dihasilkan oleh txt2csv-stealer.py")

if __name__ == "__main__":
    main()

