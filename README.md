# Stealer Parsing Automation

Repository ini menyediakan script Python untuk mengotomatisasi parsing data **stealer leaks** berdasarkan daftar subdomain.  
Workflow-nya melibatkan 3 komponen utama:

1. **`list.txt`** → berisi daftar domain/subdomain (satu per baris).  
2. **`stealer.txt`** → file dump data stealer (cred leaks).  
3. **`stealerparsing.py`** → script utama untuk mengolah data.

---

## Fitur Utama

- Membaca daftar domain dari `list.txt` (default) atau file custom via `-l`.
- Menjalankan parsing dengan **`parsingCredsLeak.py`** untuk setiap subdomain.
- Menghasilkan output per subdomain berupa file `subdomain.type-1.txt` s/d `subdomain.type-5.txt`.
- Menggabungkan seluruh hasil **type-1 s/d type-4** ke `allsubdomain.txt` (type-5 diabaikan).
- Menghapus file sementara (`*.type-1.txt` s/d `*.type-5.txt`) setelah digabung.
- Menjalankan **`txt2csv-stealer.py`** untuk mengonversi `allsubdomain.txt` ke format CSV.

---

## Struktur File
├── list.txt # Daftar domain/subdomain (input utama)
├── stealer.txt # Dump data stealer (cred leaks)
├── stealerparsing.py # Script utama
├── parsingCredsLeak.py # (script parser eksternal - dipanggil otomatis)
└── txt2csv-stealer.py # (script konversi eksternal - dipanggil otomatis)

---

## Cara Pakai

### 1. Persiapan
- Pastikan Python 3 terpasang (`python3 --version`).
- Letakkan semua file (`list.txt`, `stealer.txt`, `stealerparsing.py`, `parsingCredsLeak.py`, `txt2csv-stealer.py`) dalam satu folder.

### 2. Isi File `list.txt`
Contoh:
sub1.example.com
sub2.example.net
test.example.org

perl
Copy code

### 3. Isi File `stealer.txt`
File ini berisi data hasil dump stealer (credential leaks).  
Format mengikuti kebutuhan script `parsingCredsLeak.py`.

### 4. Jalankan Script
Default (pakai `list.txt` dan `stealer.txt`):
```bash
python3 stealerparsing.py
Custom file:

bash
Copy code
python3 stealerparsing.py -l mylist.txt -f mystealer.txt
Output
subdomain.type-1.txt s/d subdomain.type-5.txt → hasil parsing per subdomain.
⚠️ Otomatis dihapus setelah digabung.

allsubdomain.txt → gabungan semua hasil type-1 s/d type-4.

CSV Output → dihasilkan oleh txt2csv-stealer.py.

Contoh Alur
Isi list.txt dengan:

css
Copy code
a.example.com
b.example.com
Jalankan:

bash
Copy code
python3 stealerparsing.py -l list.txt -f stealer.txt
Script akan:

Menjalankan parsingCredsLeak.py untuk a.example.com dan b.example.com.

Menggabungkan hasil type-1..4 ke allsubdomain.txt.

Menghapus semua file *.type-1.txt s/d *.type-5.txt.

Menjalankan txt2csv-stealer.py untuk mengonversi ke CSV.

Catatan
Script ini tidak akan berjalan tanpa parsingCredsLeak.py dan txt2csv-stealer.py. Pastikan keduanya tersedia.

stealerparsing.py hanya mengorkestrasi workflow otomatis.

