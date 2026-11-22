[English](README.md) | [简体中文](README.zh-CN.md) | [Português](README.pt-BR.md) | [日本語](README.ja.md) | [Español](README.es.md) | [Bahasa Indonesia](README.id.md)

# PulseLex

<p align="center">
  <img src="pLex-SocialPreview.png" alt="PulseLex" width="100%">
</p>

Alfabet panjang tetap yang terinspirasi dari Morse dengan koreksi kesalahan sistematis Hamming (9,5) dan SECDED yang diperluas (10,5).

[![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)](pyproject.toml)
[![Python](https://img.shields.io/badge/python-%3E%3D3.10-blue.svg)](pyproject.toml)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-51%20passed-brightgreen.svg)](tests/)
[![Coverage](https://img.shields.io/badge/coverage-98%25-brightgreen.svg)](tests/)

PulseLex adalah prototipe penelitian telekomunikasi dan teori pengkodean eksperimental. Ini menyelidiki penggantian karakter panjang variabel dan bergantung waktu dari kode Morse Internasional dengan muatan lima bit yang seragam, merender status biner sebagai pulsa titik dan garis, serta menerapkan kode blok linier untuk menjamin koreksi kesalahan satu bit dan deteksi kesalahan dua bit.

Ini adalah artefak penelitian pendidikan dan mikro-telemetri, bukan pengganti untuk pensinyalan RF bandwidth tinggi operasional dan bukan cipher kriptografi.

---

## Gambaran Umum

Kode Morse Internasional tradisional (Rekomendasi ITU-R M.1677-1) dioptimalkan untuk pengoperasian kunci manual manusia melalui saluran yang jernih. Namun, ia sangat bergantung pada presisi temporal (celah elemen 1 unit, celah karakter 3 unit, celah kata 7 unit) dan tidak menyediakan koreksi kesalahan forward yang bersifat bawaan. Jitter waktu atau noise saluran dapat menyebabkan hilangnya pembingkaian di seluruh kata.

PulseLex mengeksplorasi desain alternatif:
- Setiap karakter menempati blok sembilan pulsa yang invarian (atau sepuluh pulsa SECDED).
- Pembingkaian karakter bersifat deterministik setelah sinkronisasi aliran terbentuk.
- Pembalikan satu bit terisolasi yang diperkenalkan selama transmisi terdeteksi dan dikoreksi secara matematis.
- Protokol menyediakan mode SECDED Hamming yang diperluas (10,5) yang mendeteksi kesalahan dua bit untuk menghilangkan koreksi yang salah.
- Sinkronisasi jendela geser aliran bit kontinu bawaan memulihkan kunci frame pada aliran pulsa yang tidak tersegmentasi.
- Sintesis audio CW akustik tanpa dependensi menghasilkan ledakan nada WAV yang bersih dan berbentuk cosinus yang ditingkatkan untuk transmisi celah udara dari speaker ke mikrofon.

---

## Fitur Utama

- **Codec Hamming yang Dipersingkat (9,5) dan SECDED (10,5):** Kode blok sistematis menggunakan empat bit paritas untuk melindungi lima bit data ($d_{\min} = 3$), dengan bit paritas keseluruhan ke-10 opsional yang menyediakan Koreksi Kesalahan Tunggal dan Deteksi Kesalahan Ganda (SECDED, $d_{\min} = 4$).
- **Sinkronizer Preamble Aliran Bit Kontinu:** Korelator jendela geser mengunci aliran pulsa mentah yang tidak tersegmentasi tanpa bergantung pada pemisah spasi putih buatan.
- **Sintetizer Bentuk Gelombang CW Akustik:** Keyboarder audio pustaka standar mengekspor file WAV PCM mono 16-bit dengan selubung naik/turun jendela Hann yang halus untuk mencegah percikan spektral dan klik kunci.
- **Alfabet 32 Simbol:** Pemetaan komprehensif dari 26 huruf kapital bahasa Inggris, spasi, tiga tanda baca, dan penanda pembingkaian mulai/akhir yang didedikasikan.
- **Dekoding Sindrom Defensif:** Membedakan antara nol kesalahan, kesalahan satu bit, dan kesalahan dua bit yang tidak dapat dikoreksi, memunculkan `DoubleErrorDetected` daripada merusak bit yang tidak rusak.
- **Simulator Saluran Simetris Biner:** Model saluran pembalikan bit Bernoulli yang dapat dikonfigurasi untuk eksperimen transmisi stokastik.
- **Tolok Ukur Monte Carlo yang Dapat Direproduksi:** Perlengkapan simulasi otomatis yang melaporkan tingkat kesalahan simbol empiris terhadap baseline yang tidak dikodekan ke CSV.
- **Naskah Akademik:** Makalah penelitian LaTeX lengkap (`paper/pulselex_paper.tex`) dengan turunan formal, diagram TikZ, dan kutipan BibTeX.
- **Tanpa Dependensi Eksternal:** Dibangun sepenuhnya dengan Pustaka Standar Python.

---

## Alfabet Simbol

Setiap simbol dipetakan ke muatan biner 5 bit ($2^5 = 32$ status unik):

| Nilai Desimal | Muatan 5-Bit | Simbol | Deskripsi |
|---:|:---:|:---:|---|
| 0–25 | `00000`–`11001` | A–Z | Alfabet Latin kapital |
| 26 | `11010` | Space | Pembatas kata |
| 27 | `11011` | `.` | Titik penuh |
| 28 | `11100` | `,` | Koma |
| 29 | `11101` | `?` | Tanda tanya |
| 30 | `11110` | `START` | Penanda preamble pesan |
| 31 | `11111` | `END` | Penanda postamble pesan |

Biner `0` dirender sebagai titik (`.`), dan biner `1` dirender sebagai garis (`-`).

---

## Arsitektur Teknis

Kata kode menggunakan pengindeksan sistematis berbasis 1 dari 1 hingga 9 (atau 10 dalam mode SECDED). Bit paritas ditetapkan ke pangkat dua (posisi 1, 2, 4, 8), dan lima bit muatan menempati posisi yang tersisa (3, 5, 6, 7, 9):

```text
Standard (9,5):
Codeword Index:   1    2    3    4    5    6    7    8    9
Content Type:    p1   p2   d1   p4   d2   d3   d4   p8   d5
Bit Allocation: [ Parity ] [Data] [Parity] [   Data   ] [Parity] [Data]

Extended SECDED (10,5):
Codeword Index:   1    2    3    4    5    6    7    8    9   10
Content Type:    p1   p2   d1   p4   d2   d3   d4   p8   d5  p0 (Overall)
```

Di bawah paritas genap, persamaan pemeriksaannya adalah:

$$\begin{aligned}
p_1 &= d_1 \oplus d_2 \oplus d_4 \oplus d_5 \\
p_2 &= d_1 \oplus d_3 \oplus d_4 \\
p_4 &= d_2 \oplus d_3 \oplus d_4 \\
p_8 &= d_5 \\
p_0 &= \bigoplus_{i=1}^9 c_i \quad \text{(SECDED mode only)}
\end{aligned}$$

### Alur Kerja End-to-End

```mermaid
flowchart LR
    A[Text Input] --> B[Normalize & Frame]
    B --> C[5-Bit Payloads]
    C --> D[Hamming 9,5 / 10,5 SECDED]
    D --> E[Pulse Stream .-.-]
    E --> F[Continuous Synchronizer / Audio WAV]
    F --> G[Channel Noise / Air Gap]
    G --> H[Syndrome & Parity Validator]
    H --> I[Single-Bit Corrector / Double Error Guard]
    I --> J[Recovered Text]
```

---

## Dasar-Dasar Matematis

- **Tingkat Kode ($R$):**
  $$R_{(9,5)} = \frac{5}{9} \approx 0.556, \quad R_{(10,5)} = \frac{5}{10} = 0.500$$
- **Overhead Redundansi:**
  $$\text{Overhead}_{(9,5)} = \frac{9 - 5}{5} \times 100\% = 80\%, \quad \text{Overhead}_{(10,5)} = 100\%$$
- **Jarak Hamming Minimum dan Batas Kesalahan:**
  - Standar $(9,5)$: $d_{\min} = 3 \implies t = 1$ koreksi bit.
  - Diperluas $(10,5)$: $d_{\min} = 4 \implies t = 1$ koreksi bit, $2$ bit deteksi kesalahan ganda yang tidak dapat dikoreksi (SECDED).
- **Tingkat Kesalahan Simbol Tidak Berkode (SER):** Untuk probabilitas pembalikan bit independen $p$:
  $$P_{\text{uncoded}} = 1 - (1 - p)^5$$
  Pada $p = 0.01$, $P_{\text{uncoded}} \approx 0.04901$ (4,90%).
- **Tingkat Kegagalan Blok Hamming ($P_{\ge 2}$):** Probabilitas dua atau lebih kesalahan bit dalam blok 9 bit:
  $$P_{\ge 2} = 1 - (1 - p)^9 - 9p(1 - p)^8$$
  Pada $p = 0.01$, $P_{\ge 2} \approx 0.00344$ (0,34%), memberikan pengurangan ~14,3x dalam probabilitas kesalahan simbol.

---

## Instalasi

### Prasyarat
- Python 3.10 atau lebih baru.

### Instalasi Pengembangan yang Dapat Diedit
```bash
git clone https://github.com/hasheramin5-cyber/pLex.git
cd pLex
python -m pip install -e .
```

### Dependensi Pengembangan
Untuk menginstal utilitas pengujian:
```bash
python -m pip install -e ".[dev]"
```

---

## Mulai Cepat dan Penggunaan

### 1. Antarmuka Baris Perintah

#### Pengkodean Standar dan SECDED
```bash
# Standard 9-bit encoding
pulselex encode "HELLO, WORLD?"

# Extended 10-bit SECDED encoding (Double-Error Detection)
pulselex encode --extended "HELLO, WORLD?"
```

#### Mendekode Blok yang Dipisahkan Spasi
```bash
pulselex decode "-------.. .....---- .-.-.-... --..-.--- --..-.--- ...----.. ..-.--... -.-.-.-.. .--..--.. ...----.. .--....-- --..-.--- .-.-..--- -.-.--.-- .--------"
```

#### Sinkronisasi Aliran Kontinu dan Deframing
Pulihkan pesan dari aliran bit yang tidak tersegmentasi dan berisik dengan noise awal/akhir:
```bash
pulselex sync-decode "..noise..-------..-..-..-..-....-.--------...noise.." --verbose
```

#### Sintesis Audio CW Akustik (Ekspor WAV)
Hasilkan nada audio 750 Hz yang halus dan berbentuk Hann:
```bash
pulselex audio "EMERGENCY" -o results/beacon.wav --freq 750 --dot-duration 0.050
```

### 2. Contoh API Python

```python
from pulselex import encode_text, decode_pulses, sync_and_decode, text_to_wav

# 1. Standard encoding & decoding
stream = encode_text("PULSELEX")
recovered = decode_pulses(stream)

# 2. Extended SECDED mode with 2-bit error detection
secded_stream = encode_text("AIR GAP MSG", extended=True)
recovered_secded = decode_pulses(secded_stream)

# 3. Synchronize continuous bitstream with arbitrary noise
raw_bitstream = "...noise..." + secded_stream.replace(" ", "") + "---noise---"
text = sync_and_decode(raw_bitstream, extended=True)
print("Deframed:", text)

# 4. Synthesize acoustic CW audio WAV file
wav_path = text_to_wav("SOS", "sos_beacon.wav", frequency_hz=800.0)
print(f"Audio exported to {wav_path}")
```

---

## Tolok Ukur Empiris

Proyek ini mencakup alat tolok ukur Monte Carlo empiris yang mengevaluasi tingkat kesalahan simbol di berbagai tingkat noise.

### Jalankan Eksperimen
```bash
python -m pulselex.experiment --trials 50000 --seed 7 --output results/bit_error_experiment.csv
```

### Hasil Referensi (50.000 percobaan per probabilitas, benih 7)

| Prob. Kesalahan Bit ($p$) | SER 5-Bit Tidak Berkode | PulseLex (9,5) SER | Blok yang Dikoreksi | Pengurangan SER |
|---:|---:|---:|---:|---:|
| 0.001 | 0.004740 | 0.000000 | 421 | Lengkap (0 kesalahan) |
| 0.005 | 0.024440 | 0.001000 | 2.183 | 24,4x |
| 0.010 | 0.048720 | 0.003260 | 4.329 | 14,9x |
| 0.020 | 0.095600 | 0.012260 | 8.303 | 7,8x |
| 0.050 | 0.229600 | 0.068120 | 17.175 | 3,4x |
| 0.100 | 0.409200 | 0.211820 | 26.360 | 1,9x |

*Data referensi disimpan di `results/bit_error_experiment.csv` dan dirangkum di `results/experiment_summary.txt`.*

---

## Pengujian

Jalankan rangkaian pengujian otomatis menggunakan pytest:

```bash
pytest
```

51 unit test (98% cakupan baris) mencakup:
- Koreksi kesalahan satu bit yang exhaustif di semua 32 muatan valid dan semua 9 posisi bit (288 kasus pengujian).
- Koreksi kesalahan satu bit SECDED (320 kasus pengujian) dan deteksi kesalahan dua bit yang exhaustif (1.440 kasus pengujian).
- Sinkronisasi aliran kontinu, korelasi jendela geser preamble, dan deframing batas noise.
- Sintesis sampel audio, pembentukan selubung Hann, dan validasi header file WAV PCM 16-bit standar.
- Subperintah antarmuka baris perintah (`encode`, `decode`, `sync-decode`, `audio`) dan penanganan kode keluar.
- Pemangkin tolok ukur eksperimen Monte Carlo dan ekspor dataset CSV.
- Kasus tepi, pemeriksaan batas parameter, dan status saluran tanpa noise/noise penuh.

---

## Mengompilasi Makalah Penelitian

Repositori berisi naskah akademik (`paper/pulselex_paper.tex`) yang merinci bukti matematis dan temuan protokol.

Untuk mengompilasi menggunakan distribusi LaTeX standar:
```bash
pdflatex -output-directory=paper paper/pulselex_paper.tex
bibtex paper/pulselex_paper
pdflatex -output-directory=paper paper/pulselex_paper.tex
pdflatex -output-directory=paper paper/pulselex_paper.tex
```

---

## Struktur Repositori

```text
PulseLex/
├── .github/
│   └── workflows/
│       └── ci.yml                   # Multi-OS, multi-version GitHub Actions CI
├── docs/
│   ├── MATHEMATICAL_QUESTIONS.txt   # Analytical coding theory exercises
│   ├── PulseLex_Technical_Report.md # Full architectural report (Markdown)
│   ├── PulseLex_Technical_Report.pdf# Full architectural report (PDF)
│   └── RESEARCH_BRIEF.txt           # High-level specification & hypotheses
├── paper/
│   └── pulselex_paper.tex           # LaTeX research paper
├── pulselex/
│   ├── __init__.py                  # Public exports
│   ├── audio.py                     # Acoustic CW WAV synthesizer
│   ├── channel.py                   # Binary symmetric channel model
│   ├── cli.py                       # Command-line interface
│   ├── codec.py                     # Alphabet mappings & (9,5)/(10,5) codec
│   ├── experiment.py                # Monte Carlo benchmark runner
│   └── sync.py                      # Continuous bitstream deframer & synchronizer
├── results/
│   ├── bit_error_experiment.csv     # 50,000-trial benchmark results
│   ├── experiment_summary.txt       # Benchmark summary
│   └── test_run.txt                 # Recorded test execution log
├── tests/
│   ├── test_audio.py                # Audio waveform unit tests
│   ├── test_channel.py              # Channel unit tests
│   ├── test_cli.py                  # CLI command unit tests
│   ├── test_codec.py                # Codec unit tests
│   ├── test_experiment.py           # Experiment runner unit tests
│   ├── test_secded.py               # SECDED 10-bit unit tests
│   └── test_sync.py                 # Synchronization & deframing tests
├── CONTRIBUTING.md                  # Development & contribution guidelines
├── LICENSE                          # MIT License
├── pyproject.toml                   # Project metadata & build configuration
├── references.bib                   # BibTeX bibliographic records
└── SECURITY.md                     # Security policy & reporting guidelines
```

---

## Keterbatasan dan Ruang Lingkup

- **Realisme Saluran:** Simulator saluran mengimplementasikan Saluran Simetris Biner yang independen dan tanpa memori.
- **Batas Alfabet:** Alfabet dibatasi pada 32 status (huruf kapital bahasa Inggris, spasi, titik, koma, tanda tanya, mulai, akhir). Angka dan huruf kecil dinormalisasi atau ditolak.
- **Deteksi Akustik:** Modul audio saat ini hanya mensintesis bentuk gelombang akustik; demodulasi nada mikrofon yang didefinisikan perangkat lunak direncanakan untuk fase-fase berikutnya.

---

## Berkontribusi

Kontribusi, laporan bug, dan perluasan penelitian disambut baik:

1. Fork repositori.
2. Buat cabang fitur (`git checkout -b feature/extension-name`).
3. Pastikan semua pengujian lulus (`pytest`).
4. Commit perubahan Anda dengan pesan commit yang deskriptif.
5. Buka Pull Request.

---

## Referensi dan Kutipan

Jika Anda merujuk atau membangun di atas PulseLex dalam karya akademis, harap kutip:

```bibtex
@misc{pulselex2026,
  author       = {{PulseLex Research Prototype}},
  title        = {PulseLex: A Morse-Inspired Fixed-Length Alphabet with Single-Bit Error Correction},
  year         = {2026},
  howpublished = {\url{https://github.com/hasheramin5-cyber/pLex}}
}
```

Literatur dasar utama:
- International Telecommunication Union, *Recommendation ITU-R M.1677-1: International Morse Code*, 2009.
- R. W. Hamming, *Error Detecting and Error Correcting Codes*, Bell System Technical Journal, 1950.
- T. M. Cover and J. A. Thomas, *Elements of Information Theory*, Wiley, 2006.

---

## Lisensi

Proyek ini dilisensikan di bawah ketentuan [MIT License](LICENSE).
