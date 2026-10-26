# Video Subtitle Reader & Typo Detector CLI (Python)

Aplikasi Python berbasis Command Line Interface (CLI) untuk:
1. **Membaca & mengekstrak teks subtitle dari video** secara otomatis.
2. **Auto Packaging Filter**: Otomatis mengabaikan teks kemasan botol/produk tanpa perlu mengetik kata kunci manual.
3. **Deteksi Kesalahan Penulisan (Typo Detection)**: Otomatis mendeteksi kata salah tulis/salah eja dalam subtitle (Bahasa Indonesia & Inggris) serta memberikan rekomendasi kata yang benar.
4. **Ekspor Multi-Format**: Menyimpan hasil ke format **JSON**, **SRT**, **TXT**, dan **Laporan Typo**.

---

## 🚀 Fitur Utama

1. **Deteksi Kesalahan Penulisan (Typo Detection & Smart Suggestions)**:
   - Menganalisis setiap kata dalam subtitle terhadap kamus Bahasa Indonesia (KBBI kata dasar & imbuhan via PySastrawi + kosakata percakapan kasual) dan Bahasa Inggris.
   - **OCR Character Confusion Matrix**: Menyelesaikan kerancuan optik akibat font miring (*italic ligature* `l+a` $\rightarrow$ `b`, `c+l` $\rightarrow$ `d`, `r+n` $\rightarrow$ `m`, `v+v` $\rightarrow$ `w`, leet numbers `0` $\rightarrow$ `o`, `1` $\rightarrow$ `l/i`).
   - Mengenali kata berimbuhan (*me-*, *di-*, *ber-*, *-kan*, *-an*), kata ulang (*sehari-hari*), pemisahan kata majemuk tanpa spasi (*membantumembersihkan* -> *membantu membersihkan*, *makeit* -> *make it*), dan istilah populer (*glossy*, *shampoo*, *hairfall*, dll).
   - Memberikan saran perbaikan (*suggestions*) otomatis menggunakan jarak Levenshtein dan morfologi kata.
2. **Auto Packaging Filter (Otomatis Mengabaikan Teks Kemasan)**:
   - Membedakan teks subtitle dari teks botol/kemasan produk secara cerdas berdasarkan simetri posisi tengah horizontal (`center_x`), rasio lebar kalimat, dan pola satuan kemasan.
3. **Multi-Platform High Accuracy OCR (RapidOCR ONNX Runtime)**:
   - Menggunakan model deep learning ONNX Runtime (**RapidOCR**) yang sangat ringan, cepat, dan bekerja secara konsisten di **Linux Server** maupun **macOS** tanpa memerlukan GPU besar.
   - Mendukung opsi mesin lain: Apple Vision (khusus macOS) dan Tesseract.
4. **Peleburan Animasi Teks Otomatis (Typewriter / Karaoke Smoothing)**:
   - Kalimat yang muncul bertahap per frame otomatis disatukan menjadi kalimat subtitle utuh.
5. **Laporan & Ekspor Lengkap**:
   - `<video>_subtitles.txt`: Transkrip bersih dengan timestamp dan laporan typo terintegrasi (Default).
   - Format opsional (`--export all` / `json` / `srt`): file JSON dan SRT.

---

## 🛠️ Persyaratan Sistem

- Python 3.9+
- Paket dependensi yang dibutuhkan:
  ```bash
  pip install opencv-python rapidocr-onnxruntime onnxruntime pyspellchecker PySastrawi
  ```
  *(Opsional jika di macOS dan ingin menggunakan Apple Vision: `pip install pyobjc-framework-Vision`)*

---

## 📖 Cara Penggunaan

### 1. Ekstraksi Subtitle Sekaligus Deteksi Typo Otomatis
Tambahkan flag `--check-typo` saat memproses video:
```bash
# Windows:
python video_subtitle_reader.py salah.mp4 --check-typo

# Linux / macOS:
python3 video_subtitle_reader.py salah.mp4 --check-typo
```

Contoh output di terminal:
```text
========================================================
🔍 LAPORAN PEMERIKSAAN TYPO: salah.mp4
========================================================
 • Total Subtitle Dianalisis : 5
 • Total Kata Dianalisis     : 39
 • Total Typo Ditemukan      : 1
--------------------------------------------------------
⚠️  DAFTAR KATA YANG DIDUGA SALAH TULIS (TYPO):

[ID #4] Waktu: 00:00:08,500 --> 00:00:11,500
  Teks Asli : "Tekstur ringan Gampang diblend engandung Gardenia Extract, Vitamin E & SPF 20"
  ❌ Kata Typo : 'engandung'  👉  Saran Perbaikan: 'mengandung', 'senandung', 'nandung'
========================================================
```

### 2. Memproses Banyak Video Sekaligus (Batch Processing)
Sistem mendukung pemrosesan banyak video secara otomatis sekaligus dalam sekali jalan:

```bash
# Opsi A: Memproses seluruh video di dalam sebuah folder (misal folder 'Video')
python video_subtitle_reader.py Video --check-typo

# Opsi B: Memproses menggunakan pola wildcard (*.mp4)
python video_subtitle_reader.py "Video/*.mp4" --check-typo

# Opsi C: Memproses dengan membatasi jumlah video (misal 5 video pertama saja untuk pengujian cepat)
python video_subtitle_reader.py Video --check-typo --limit 5

# Opsi D: Menyebutkan beberapa file video secara spesifik
python video_subtitle_reader.py salah.mp4 benar.mp4 --check-typo
```

Ringkasan hasil akhir akan langsung menampilkan tabel statistik eksekutif lengkap:
```text
========================================================
✨ RINGKASAN HASIL PROSES (BATCH REPORT)
========================================================
 • test (1).mp4              :  5 subtitle terdeteksi | 1 typo (Waktu: 6.2s)
 • test (2).mp4              :  4 subtitle terdeteksi | 0 typo (Waktu: 4.8s)
 • test (3).mp4              :  5 subtitle terdeteksi | 0 typo (Waktu: 5.5s)
--------------------------------------------------------
 📊 STATISTIK TOTAL : 3 video | 14 subtitle | 1 typo
 📂 Output Folder    : C:\Users\bnhed\Downloads\videotext\videotext\output
```

### 3. Menjalankan Typo Checker Batch pada Seluruh File Subtitle yang Sudah Ada
Jika Anda sudah mengekstrak subtitle dan ingin memeriksa seluruh hasil di folder `output` secara instan:
```bash
# Memeriksa seluruh file subtitle di dalam folder output sekaligus:
python typo_checker.py output/

# Atau memeriksa file tertentu saja:
python typo_checker.py output/salah_subtitles.txt output/benar_subtitles.txt
```

### 4. Menambahkan Kata Khusus ke Whitelist
Jika video Anda mengandung istilah merek tertentu atau istilah baru yang ingin dianggap benar:
- **Cara 1 (Rekomendasi)**: Tulis kata-kata Anda di berkas `whitelist.txt` (satu kata per baris, otomatis terbaca).
- **Cara 2 (Flag CLI)**:
```bash
python video_subtitle_reader.py Video --check-typo --typo-whitelist "skintific,somethinc,sariayu"
```

---

## ⚙️ Daftar Opsi Lengkap

| Argumen / Flag | Deskripsi | Nilai Default |
| :--- | :--- | :--- |
| `videos` | Satu atau lebih path file video (`video.mp4` atau `*.mp4`) | *Wajib* |
| `--engine` | Mesin OCR yang digunakan (`rapidocr`, `vision`, `tesseract`, `auto`) | `rapidocr` |
| `--check-typo` | Jalankan deteksi kesalahan ketik/ejaan secara otomatis | `False` |
| `--typo-whitelist` | Daftar kata tambahan yang dianggap benar (dipisahkan koma) | `""` |
| `-o`, `--output-dir` | Folder direktori penyimpanan file output | `./output` |
| `--roi` | Preset area (`top`, `bottom`, `middle`, `full`) atau custom `ymin,ymax` | `15,80` |
| `--no-auto-filter` | Nonaktifkan filter otomatis teks kemasan | `False` |
| `--min-width` | Lebar minimum teks dalam persen lebar video | `25.0` |
| `--min-words` | Jumlah kata minimum per baris teks | `1` |
| `--fps-sample` | Frekuensi sampling frame per detik | `2.0` |
| `--min-duration` | Durasi minimum subtitle dalam detik | `0.8` |
| `--export` | Format ekspor (`txt`, `json`, `srt`, atau `all`) | `txt` |
| `--preview` | Generate file gambar preview beranotasi bounding box | `False` |

---

## 📄 Format Laporan Typo JSON (`output/salah_typo_report.json`)

```json
{
  "total_subtitles_analyzed": 5,
  "total_words_analyzed": 39,
  "total_typos_found": 1,
  "has_typo": true,
  "typo_details": [
    {
      "subtitle_id": 4,
      "timestamp": "00:00:08,500 --> 00:00:11,500",
      "text": "Tekstur ringan Gampang diblend engandung Gardenia Extract, Vitamin E & SPF 20",
      "typos": [
        {
          "word": "engandung",
          "suggestions": [
            "mengandung",
            "senandung",
            "nandung"
          ]
        }
      ]
    }
  ]
}
```
