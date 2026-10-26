# 🎬 videotext Studio / v1.0 - Full-Stack React & Python
## Proyek Capstone Kelompok 4: Ekstraksi Subtitle Video (OCR) & Deteksi Typo (NLP)
**Universitas Asa Indonesia - Fakultas Teknologi Informasi & Sistem Informasi (2026)**  
**Anggota**: Muhammad Hanif & Iqbal Maulana

---

## 🌟 Ringkasan Sistem
Sistem Web Terpadu (**Frontend React 18 + Backend Python Multi-Threaded**) yang dirancang persis sesuai spesifikasi **Technical Design Document (TDD)** dan **Software Requirements Specification (SRS)** Kelompok 4, serta desain UI antarmuka Figma:
- **Frontend**: Single Page Application (SPA) berbasis **React 18** dengan Plus Jakarta Sans, JetBrains Mono, Dark Navy Theme (`#080c14`), dan styling CSS modern tanpa dependensi berat.
- **Backend**: Server HTTP Python multi-threaded mandiri (`server.py`) dengan dukungan **HTTP 206 Range Requests** untuk pemutaran video HTML5 seekable secara real-time pada timestamp milidetik.
- **Computer Vision & NLP**: Terintegrasi langsung dengan mesin inferensi OCR `video_subtitle_reader.py` dan pemeriksa ejaan `typo_checker.py` (PySastrawi 29.000 kata dasar KBBI, 4 pilar ortografis, dan jarak Damerau-Levenshtein berbobot QWERTY).

---

## 📸 Antarmuka & Alur Kerja (Sesuai Desain Figma TDD)

| Halaman / Fitur | Deskripsi Layar (Sesuai Dokumen TDD) |
| :--- | :--- |
| **1. Subtitle Review (STEP 03/03)** | Tampilan 3 kolom utama: **Video Preview** (frame 9:16 mockup & pemutar video MP4 tersinkronisasi), **Extracted Subtitles** (5 segmen linimasa dengan indikator alert oranye pada segmen bermasalah), dan **Result Summary** (5 Subtitle events, 1 Potential writing error, badge *NEEDS REVIEW*, serta tombol *Inspect typo →*). |
| **2. Typo Inspector (HUMAN IN THE LOOP)** | Tampilan 2 kolom detail: **Source Evidence** (bukti visual teks frame pada rentang `00:08.500 -> 00:11.500`) dan **Potential Typo** (kata *engandung* berukuran besar, 3 opsi saran koreksi ejaan dengan *01 mengandung* aktif, konteks naskah asli, serta tombol navigasi bolak-balik). |
| **3. Export Center (OUTPUT READY)** | Pusat unduh artefak hasil analisis dalam 3 format standar: **TXT export** (Default format), **JSON export** (Machine-readable), dan **SRT export** (Timed captions untuk editor video). Disertai preview daftar berkas keluaran dan tombol *Done · overview →*. |
| **4. Roadmap (Audio + Multimodal)** | Dokumentasi roadmap masa depan sistem: **Phase 01** (OCR + Subtitle QA - Tersedia di CLI saat ini), **Phase 02** (Audio ASR - Planned), **Phase 03** (Multimodal alignment - Planned), dan **Phase 04** (Creative evaluation - Research). |
| **5. Overview Dashboard** | Ringkasan metrik KPI (Videos Tested, Subtitle Events, Potential Typos, Clean Results) dan tabel riwayat pemrosesan 4 video sampel agensi. |
| **6. Import & OCR Settings** | Konfigurasi sampling FPS (2.0 FPS), Region of Interest (ROI Ymin 15% - Ymax 80%), Auto Packaging Filter, dan seleksi video sampel cepat. |
| **7. Processing Stepper** | Visualisasi animasi progress bar bertahap (0% s.d. 100%) dan live inference terminal logs. |

---

## 🚀 Cara Menjalankan Sistem

### Opsi 1: Klik 1x (Paling Cepat di Windows)
Cukup klik ganda file batch:
```text
web_app/run_web.bat
```
Atau melalui menu master di root proyek:
```text
RUN_SYSTEM_MASTER.bat -> Pilih [0]
```
Browser akan otomatis terbuka mengarah ke `http://localhost:5000`.

---

### Opsi 2: Menjalankan via Terminal / Command Prompt
```bash
cd web_app
python server.py
```
Output terminal akan menampilkan:
```text
============================================================================
 🎬 VIDEOTEXT STUDIO v1.0 - BACKEND SERVER BERJALAN
 Capstone Kelompok 4: Ekstraksi Subtitle Video & Deteksi Typo (OCR + NLP)
============================================================================
 💻 Akses di Komputer ini (Localhost) : http://localhost:5000
 📱 Akses dari Laptop / Smartphone Teman (Satu Wi-Fi):
    👉 http://192.168.1.45:5000
============================================================================
```

---

## 📁 Struktur Berkas Sistem Web

```text
videotext/
├── web_app/
│   ├── server.py              # Backend Python (ThreadingHTTPServer + Range Request + REST API)
│   ├── run_web.bat            # Script batch peluncur 1-klik Windows
│   ├── README_WEB.md          # Dokumentasi teknis sistem web
│   ├── uploads/               # Direktori penyimpanan video unggahan pengguna
│   └── static/
│       ├── index.html         # Template HTML utama mounting React 18
│       ├── css/
│       │   └── style.css      # Design system gelap (Figma Dark Navy Theme)
│       └── js/
│           ├── app.jsx        # Komponen dan State Management React 18
│           └── app.js         # Client bridge script
│
├── frontend/                  # Proyek Modular React + Vite (untuk repositori & build mandiri)
│   ├── package.json           # Dependensi React 18 & Vite
│   ├── vite.config.js         # Konfigurasi reverse proxy Vite ke port 5000
│   ├── index.html             # Entry point Vite SPA
│   └── src/
│       ├── main.jsx           # Mounting React Root
│       ├── App.jsx            # Master Orchestrator Component
│       ├── components/        # Modul komponen mandiri per layar
│       │   ├── Sidebar.jsx
│       │   ├── SubtitleReview.jsx
│       │   ├── TypoInspector.jsx
│       │   ├── ExportCenter.jsx
│       │   ├── Roadmap.jsx
│       │   ├── Overview.jsx
│       │   ├── ImportVideos.jsx
│       │   ├── OcrSettings.jsx
│       │   └── Processing.jsx
│       └── styles/
│           └── index.css      # Impor stylesheet terpadu
│
├── videotext/                 # Engine Inti Computer Vision & NLP
│   ├── video_subtitle_reader.py # Engine ekstraksi OCR frame
│   ├── typo_checker.py        # Engine deteksi typo bilingual KBBI
│   ├── whitelist.txt          # Kamus istilah khusus kecantikan & slang
│   └── Video/                 # Koleksi file video sampel (salah.mp4, benar.mp4, dsb)
│
├── salah.mp4                  # Berkas video uji utama (Tinted moisturizer - typo 'engandung')
├── RUN_SYSTEM_MASTER.bat      # Menu navigasi master Windows
├── SRS_Capstone_Kelompok_4_Revisi_Terpadu.docx # Dokumen SRS Akademik
└── TDD_Kelompok_4.docx        # Dokumen Technical Design Document
```

---

## 📡 Dokumentasi Endpoint REST API

| Method | Endpoint | Fungsi |
| :--- | :--- | :--- |
| `GET` | `/api/status` | Mengembalikan status kesehatan server dan dependensi OCR/NLP |
| `GET` | `/api/samples` | Mengembalikan data 4 video benchmark resmi beserta segmen linimasa |
| `GET` | `/api/video/<filename>` | Streaming berkas video dengan dukungan byte range request |
| `POST` | `/api/upload` | Mengunggah berkas video MP4 baru ke server |
| `POST` | `/api/process` | Menjalankan pipeline ekstraksi OCR dan deteksi typo |
| `POST` | `/api/check-typo` | Memeriksa ejaan kata atau daftar kalimat secara real-time |
| `POST` | `/api/export` | Menghasilkan dan mengunduh berkas transkrip `.txt`, `.json`, atau `.srt` |
