import argparse
import csv
import re
import os

def parse_file(input_file, delimiter):
    with open(input_file, 'r') as file:
        lines = file.readlines()
        
    parsed_data = []
    
    # Buat pola regex berdasarkan delimiter
    delimiter_parts = list(delimiter)
    delimiter_pattern = '|'.join([re.escape(part) for part in delimiter_parts])
    
    for line in lines:
        if not line.strip():
            continue

        original_line = line.strip()

        # Ambil bagian sebelum ":" pertama → dianggap sebagai filename
        filename = None
        if ":" in original_line:
            filename, rest = original_line.split(":", 1)
            line = "FILENAME_PLACEHOLDER:" + rest
        else:
            line = original_line

        # Normalisasi http: / https:
        line = re.sub(r'http:(?!//)', 'http://', line)
        line = re.sub(r'https:(?!//)', 'https://', line)

        # Placeholder agar tidak pecah saat split
        line = re.sub(r'http://', 'URL_PROTOCOL_http_PLACEHOLDER', line)
        line = re.sub(r'https://', 'URL_PROTOCOL_https_PLACEHOLDER', line)

        # Split pakai delimiter
        parts = re.split(delimiter_pattern, line.strip())

        # Balikin http/https
        for idx, part in enumerate(parts):
            if 'URL_PROTOCOL_http_PLACEHOLDER' in part:
                parts[idx] = part.replace('URL_PROTOCOL_http_PLACEHOLDER', 'http://')
            elif 'URL_PROTOCOL_https_PLACEHOLDER' in part:
                parts[idx] = part.replace('URL_PROTOCOL_https_PLACEHOLDER', 'https://')

        # Balikin filename ke kolom pertama
        if parts and parts[0] == "FILENAME_PLACEHOLDER":
            parts[0] = filename if filename else "FILENAME_PLACEHOLDER,"

        parsed_data.append(parts)
    
    return parsed_data


def write_csv(output_file, data):
    with open(output_file, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(data)


def main():
    parser = argparse.ArgumentParser(description="Convert target file to CSV with custom delimiters")
    parser.add_argument('input_file', type=str, help="Input file to process")
    parser.add_argument('-d', '--delimiter', type=str, required=True, help="Delimiter sequence to split by")
    parser.add_argument('output_file', type=str, nargs='?', help="Output CSV file (default: same name as input with .csv extension)")
    
    args = parser.parse_args()

    # Kalau output_file tidak diberikan → otomatis buat dari nama input
    if args.output_file is None:
        base, _ = os.path.splitext(args.input_file)
        args.output_file = base + ".csv"
    
    parsed_data = parse_file(args.input_file, args.delimiter)
    write_csv(args.output_file, parsed_data)
    
    print(f"File telah diproses dan disimpan di {args.output_file}")


if __name__ == "__main__":
    main()
