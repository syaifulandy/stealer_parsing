import re
import argparse
import sys
import chardet

def make_type_patterns(keyword, mode="domain"):
    # Regex port web valid: 80–65535
    port_web = r"(?::(?:80|[1-9][0-9]{2,3}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5]))?"

    if mode == "fqdn":
        url_pat = rf"(?:https?://)?{re.escape(keyword)}{port_web}(?:/\S*)?"
    else:
        url_pat = rf"(?:https?://)?(?:[\w\.\-]+\.)?{re.escape(keyword)}{port_web}(?:/\S*)?"

    patterns = [
        re.compile(
            rf"(?P<file>.+?):\s*"
            rf"(?P<url>{url_pat}):"
            rf"(?P<user>[^: ]+):"
            rf"(?P<pass>[^\s:]+)$"
        ),
        re.compile(
            rf"(?P<file>.+?):\s*"
            rf"(?P<url>{url_pat})\s+"
            rf"(?P<user>[^: ]+):"
            rf"(?P<pass>[^\s:]+)$"
        ),
        re.compile(
            rf"(?P<file>.+?):\s*"
            rf"(?P<user>[^: ]+):"
            rf"(?P<pass>[^\s:]+):"
            rf"(?P<url>{url_pat})$"
        ),
        re.compile(
            rf"(?P<file>.+?):\s*"
            rf"(?P<user>[^: ]+):"
            rf"(?P<pass>[^\s:]+)\s+"
            rf"(?P<url>{url_pat})$"
        ),
    ]
    return patterns


def read_file_smart(filename):
    with open(filename, "rb") as f:
        raw = f.read()
        result = chardet.detect(raw)
        encoding = result['encoding']
        confidence = result.get('confidence', 0)
        print(f"[i] Detected encoding: {encoding} (confidence {confidence:.2f})")
        try:
            text = raw.decode(encoding)
        except Exception as e:
            print(f"[!] Error decode pakai {encoding}: {e}\n[!] Fallback ke latin1.")
            text = raw.decode("latin1")
    return text.splitlines()

def main():
    parser = argparse.ArgumentParser(
        description="Otomasi parsing data login dengan format custom. "
                    "Dapat mencari semua subdomain (-d) atau spesifik FQDN (-s).",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""
Contoh penggunaan:
  python script.py -d abc.co.id -f data.txt
    (mencari semua subdomain dari abc.co.id, misal: user.abc.co.id, x.abc.co.id)

  python script.py -s api.abc.co.id -f data.txt
    (hanya match domain persis api.abc.co.id dan path di belakangnya)
""")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-d", "--domain", help="Domain utama, match semua subdomain (contoh: abc.co.id)")
    group.add_argument("-s", "--subdomain", help="FQDN spesifik, hanya match persis domain ini (contoh: api.abc.co.id)")
    parser.add_argument("-f", "--file", required=True, help="File input (teks)")

    args = parser.parse_args()

    if args.domain:
        type_patterns = make_type_patterns(args.domain, mode="domain")
        keyword = args.domain
    else:
        type_patterns = make_type_patterns(args.subdomain, mode="fqdn")
        keyword = args.subdomain

    output_files = {
        1: f"{keyword}.type-1.txt",
        2: f"{keyword}.type-2.txt",
        3: f"{keyword}.type-3.txt",
        4: f"{keyword}.type-4.txt",
        5: f"{keyword}.type-5.txt",
    }
    results = {i: [] for i in range(1, 6)}

    lines = read_file_smart(args.file)

    for line in lines:
        line = line.strip()
        matched = False
        for i, pattern in enumerate(type_patterns, start=1):
            if pattern.match(line):
                results[i].append(line)
                matched = True
                break
        if not matched and keyword in line:
            results[5].append(line)

    for i in range(1, 6):
        if results[i]:
            with open(output_files[i], "w", encoding="utf-8") as f:
                for item in results[i]:
                    f.write(item + "\n")
            print(f"Type-{i}: {len(results[i])} data, file: {output_files[i]}")

if __name__ == "__main__":
    main()
