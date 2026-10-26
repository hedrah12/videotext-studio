# 🎬 VideoText Studio v1.0

> **Sistem Ekstraksi Subtitle Video dan Deteksi Kesalahan Penulisan Berbasis OCR dan NLP untuk Konten Agensi**  
> *Capstone Project Kelompok 4*

[![Python Version](https://img.shields.io/badge/Python-3.9%20%7C%203.10%20%7C%203.11-blue.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/Frontend-React%20%2B%20Vite-61dafb.svg)](https://react.dev/)
[![OCR Engine](https://img.shields.io/badge/OCR-RapidOCR%20(ONNX)-orange.svg)](https://github.com/RapidAI/RapidOCR)
[![NLP Engine](https://img.shields.io/badge/NLP-PySastrawi%20%2B%20Levenshtein-brightgreen.svg)](https://github.com/harispc/PySastrawi)

---

## 📌 Ringkasan Sistem

**VideoText Studio** adalah platform *full-stack* terpadu yang dirancang untuk membantu agensi kreatif, video editor, dan tim QA konten dalam memvalidasi subtitle video promosi/iklan secara otomatis.

Sistem menggabungkan teknologi **Computer Vision (Deep Learning OCR)** untuk mengekstrak teks langsung dari frame video dengan **Natural Language Processing (NLP)** untuk mendeteksi kesalahan ejaan (*typo*) berbahasa Indonesia dan Inggris serta menyajikan saran koreksi kata secara akurat.

---

## 🏗️ Arsitektur Proyek

Sistem dibangun menggunakan pendekatan **Monorepo** yang memisahkan tanggung jawab modul secara bersih:

```text
videotext/
├── frontend/               # [FRONTEND] Source code UI berbasis React 18 + Vite
│   ├── src/                # Komponen antarmuka (Video Player, Editor, Typo Panel)
│   └── package.json        # Dependensi dan build script
│
├── web_app/                # [BACKEND] Server HTTP & REST API Python
│   ├── server.py           # Multi-threaded HTTP Server + Range Request (HTTP 206)
│   ├── database.py         # Lapisan integrasi database SQLite
│   ├── schema.sql          # Skema database riwayat analisis
│   ├── static/             # Bundle statis UI (disajikan langsung oleh server)
│   └── uploads/            # Direktori penyimpanan video yang diunggah
│
├── videotext/              # [CORE ENGINE] Modul Ekstraksi & Kecerdasan Buatan
│   ├── video_subtitle_reader.py # Ekstraksi frame video, filter kemasan, RapidOCR
│   ├── typo_checker.py     # Deteksi typo bilingual (KBBI Sastrawi + Levenshtein)
│   └── whitelist.txt       # Kamus istilah khusus agensi / brand names
│
├── docs/                   # [DOKUMENTASI LENGKAP]
│   ├── SRS_Capstone_Kelompok_4_Revisi_Terpadu.md # Software Requirements Specification
│   └── PANDUAN_SERVER_LINUX.md                   # Panduan deployment VPS Linux
│
├── RUN_SYSTEM_MASTER.bat   # Script interaktif launcher sistem (Windows)
├── requirements.txt        # Dependensi pustaka Python
└── .gitignore              # Konfigurasi file terabaikan git
```

---

## ⚡ Fitur Utama

1. **Ekstraksi Subtitle Berbasis OCR (RapidOCR DBNet + SVTR ONNX Runtime)**:
   - Sangat cepat dan akurat membaca teks video promosi/reels/TikTok.
   - **Auto Packaging Filter**: Otomatis mengabaikan teks kemasan botol/produk tanpa perlu tagging manual.
   - **Typewriter Smoothing**: Meleburkan animasi teks karaoake/ketik bertahap menjadi satu baris subtitle utuh.

2. **Deteksi Typo Bilingual & Smart Suggestions (NLP)**:
   - Validasi ejaan Bahasa Indonesia (KBBI via PySastrawi + istilah percakapan kasual) dan Bahasa Inggris.
   - **OCR Confusion Matrix**: Mengatasi kerancuan optik akibat font miring (*italic*) dan ligature (`l+a` $\rightarrow$ `b`, `c+l` $\rightarrow$ `d`, `r+n` $\rightarrow$ `m`, `v+v` $\rightarrow$ `w`).
   - Saran perbaikan kata otomatis berbasis jarak Damerau-Levenshtein.

3. **Video Player Sinkron Milidetik (HTTP 206 Partial Content)**:
   - Mengklik kata atau timestamp di transkrip langsung melompatkan video ke detik terjadinya typo secara presisi.

4. **Ekspor Multi-Format**:
   - Mendukung unduh transkrip dalam format **TXT**, **SRT (Subtitle Standar)**, dan **JSON**.

---

## 🚀 Panduan Instalasi & Menjalankan (Tanpa Docker)

### 1. Prasyarat Sistem
- **Python**: Versi `3.9`, `3.10`, atau `3.11` ([Download Python](https://www.python.org/downloads/))
  > *Pastikan opsi "Add Python to PATH" dicentang saat instalasi.*
- **Node.js** *(Opsional, hanya jika ingin memodifikasi tampilan UI React)*: Versi 18+

---

### 2. Instalasi Dependensi Python

Buka terminal di direktori proyek dan jalankan:
```bash
pip install -r requirements.txt
```

---

### 3. Menjalankan Aplikasi

#### 🖥️ Cara Cepat (Windows):
Cukup klik ganda (double-click) file:
```cmd
RUN_SYSTEM_MASTER.bat
```
Pilih opsi `[0]` untuk membuka Web Studio di browser secara otomatis.

#### ⌨️ Cara Manual (Semua Sistem Operasi / Linux / macOS):
Jalankan backend server:
```bash
python web_app/server.py
```
Buka browser dan akses:  
👉 **`http://localhost:5000`**

---

### 4. Pengembangan Frontend UI (Opsional)

Jika Anda ingin mengubah komponen antarmuka React:
```bash
cd frontend
npm install
npm run dev
```
Setelah selesai mengubah kode UI, lakukan kompilasi agar masuk ke backend:
```bash
npm run build
```

---

## 📡 Dokumentasi Endpoint REST API

| Method | Endpoint | Deskripsi |
|---|---|---|
| `GET` | `/api/status` | Memeriksa status engine OCR, OpenCV, dan kamus NLP |
| `GET` | `/api/samples` | Mengambil daftar video sampel agensi bawaan |
| `GET` | `/api/video/<filename>` | Streaming video dengan dukungan seek milidetik (HTTP 206) |
| `POST` | `/api/upload` | Mengunggah video baru (`multipart/form-data`) |
| `POST` | `/api/process` | Menjalankan pipeline OCR dan deteksi typo pada video |
| `POST` | `/api/check-typo` | Menguji kalimat/kata langsung terhadap pemeriksa ejaan |
| `POST` | `/api/export` | Mengunduh hasil transkrip (format: `.txt`, `.srt`, `.json`) |

---

## 👥 Tim Pengembang (Kelompok 4)
- **Proyek**: Capstone Project & Skripsi
- **Topik**: Computer Vision (OCR) + Natural Language Processing (NLP)
