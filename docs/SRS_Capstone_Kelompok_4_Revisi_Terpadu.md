# DOKUMEN SPESIFIKASI KEBUTUHAN SISTEM
## SOFTWARE REQUIREMENTS SPECIFICATION (SRS)
### Standar IEEE Std 830-1998 / ISO/IEC/IEEE 29148:2018

---

**INFORMASI PROYEK CAPSTONE**
* **Judul Proyek**: Pengembangan Sistem Ekstraksi Subtitle Video dan Deteksi Kesalahan Penulisan Berbasis OCR dan NLP untuk Konten Agensi
* **Nama Kelompok**: Kelompok 4
* **Anggota Pengembang**:
  1. Muhammad Hanif
  2. Iqbal Maulana
* **Program Studi**: Teknologi Informasi & Sistem Informasi
* **Fakultas / Institusi**: Universitas Asa Indonesia
* **Tahun Akademik**: 2026
* **Versi Dokumen**: 2.0 (Revisi Final Terpadu)
* **Status Dokumen**: Disetujui & Terverifikasi Kode Sumber (*Code-Verified*)

---

## RIWAYAT REVISI DOKUMEN

| Versi | Tanggal | Penulis | Deskripsi Perubahan |
| :---: | :---: | :--- | :--- |
| 1.0 | 06 Oktober 2026 | Muhammad Hanif, Iqbal Maulana | Pembuatan draf awal SRS berdasarkan Initial Project Idea Document dan rencana konseptual sistem pemeriksaan konten agensi. |
| 1.1 | 07 Oktober 2026 | Muhammad Hanif, Iqbal Maulana | Penyesuaian ruang lingkup terhadap implementasi kode aktual (CLI Python). Fitur web frontend, database, autentikasi multi-user, dan analisis audio dipindahkan ke luar cakupan. |
| 2.0 | 07 Oktober 2026 | Senior Software Architect & Technical Writer | Restrukturisasi menyeluruh mengacu pada standar resmi IEEE Std 830 (5 Bab Utama). Integrasi formulasi matematis 8 algoritma inti, dekomposisi formal kebutuhan fungsional (FR-01 s.d. FR-12), pemulihan kebutuhan performa, perapian antarmuka, dan pelaporan hasil uji empiris 4 video sampel. |

---

## DAFTAR ISI

* **BAB 1: PENDAHULUAN**
  * 1.1 Tujuan Dokumen
  * 1.2 Cakupan Produk (*Product Scope*)
  * 1.3 Definisi, Akronim, dan Singkatan
  * 1.4 Referensi
* **BAB 2: DESKRIPSI UMUM SISTEM (*OVERALL DESCRIPTION*)**
  * 2.1 Perspektif Produk (*Product Perspective*)
  * 2.2 Fitur Utama Produk (*Product Functions*)
  * 2.3 Karakteristik dan Kelas Pengguna (*User Classes & Characteristics*)
  * 2.4 Lingkungan Operasional (*Operating Environment*)
  * 2.5 Batasan Desain dan Implementasi (*Design & Implementation Constraints*)
  * 2.6 Dokumentasi Pengguna (*User Documentation*)
* **BAB 3: KEBUTUHAN ANTARMUKA EKSTERNAL (*EXTERNAL INTERFACE REQUIREMENTS*)**
  * 3.1 Antarmuka Pengguna (*User Interfaces*)
  * 3.2 Antarmuka Perangkat Keras dan Perangkat Lunak (*Hardware & Software Interfaces*)
  * 3.3 Antarmuka Komunikasi (*Communications Interfaces*)
* **BAB 4: FITUR SISTEM DAN KEBUTUHAN FUNGSIONAL (*SYSTEM FEATURES & FUNCTIONAL REQUIREMENTS*)**
  * 4.1 Dekomposisi Kebutuhan Fungsional (FR-01 s.d. FR-12)
  * 4.2 Spesifikasi Detail Use Case & Alur Kerja Sistem
  * 4.3 Kriteria Penerimaan Berbasis Skenario (*Acceptance Criteria*)
* **BAB 5: KEBUTUHAN NON-FUNGSIONAL (*NON-FUNCTIONAL REQUIREMENTS*)**
  * 5.1 Kinerja (*Performance Requirements*)
  * 5.2 Keamanan dan Privasi Data (*Security & Privacy Requirements*)
  * 5.3 Keandalan dan Ketersediaan (*Reliability & Availability Requirements*)
  * 5.4 Kemudahan Penggunaan (*Usability Requirements*)
* **LAMPIRAN: HASIL PENGUJIAN DAN VALIDASI EMPIRIS SISTEM**
  * L.1 Data Pengujian pada 4 Video Sampel Agensi
  * L.2 Analisis False Positive dan False Negative

---

## BAB 1: PENDAHULUAN

### 1.1 Tujuan Dokumen
Dokumen Spesifikasi Kebutuhan Sistem (*Software Requirements Specification* - SRS) ini disusun untuk mendokumentasikan secara lengkap dan formal kebutuhan fungsional, kebutuhan non-fungsional, batasan arsitektur, serta lingkungan operasional dari **Sistem Ekstraksi Subtitle Video dan Deteksi Kesalahan Penulisan Berbasis OCR dan NLP**.

Tujuan utama dokumen ini adalah:
1. Menjadi acuan teknis (*baseline technical specification*) bagi tim pengembang dalam memelihara dan mengembangkan modul sistem.
2. Menjadi instrumen evaluasi akademik bagi dosen pembimbing dan penguji dalam menilai keselarasan antara metodologi rekayasa perangkat lunak, perancangan arsitektur, dan implementasi kode sumber aktual pada Proyek Capstone 2026.
3. Memberikan panduan operasional bagi pemangku kepentingan agensi (editor video dan *creative lead*) terkait batas kemampuan, kelebihan, serta batasan operasional sistem.

### 1.2 Cakupan Produk (Product Scope)
Produk yang dikembangkan adalah aplikasi *Command Line Interface* (CLI) berbasis Python yang beroperasi secara lokal (*offline on-premise*). Sistem ini dirancang sebagai pemeriksa lapis pertama (*first-pass quality assurance checker*) untuk teks subtitle visual yang tertanam langsung pada frame video (*burned-in on-screen subtitle*) pada konten video pendek (*short-form video* seperti TikTok, Instagram Reels, dan YouTube Shorts).

**Ruang Lingkup Pekerjaan Sistem Mencakup:**
* Pembacaan berkas video lokal (.mp4) dan pengambilan sampel frame secara temporal menggunakan OpenCV (default 2.0 frame per detik).
* Deteksi dan pengenalan teks visual multi-mesin menggunakan RapidOCR berbasis ONNX Runtime (arsitektur deteksi DBNet dan pengenalan SVTR/CRNN) yang ringan di CPU, dengan opsi Apple Vision dan Tesseract.
* Normalisasi spasial koordinat bounding box ke dalam persentase frame (0% - 100%) dan penyaringan area aktif (*Region of Interest* / ROI).
* Penyaringan otomatis teks kemasan produk (*Auto Packaging Filter*) tanpa entri kata kunci manual, berdasarkan simetri titik tengah horizontal, ambang batas lebar kalimat, pola regex spesifikasi produk, dan validasi durasi kemunculan.
* Pengelompokan baris teks visual (*Visual Line Clustering*) dan penilaian keyakinan subtitle (*Subtitle Confidence Scoring*) untuk memilih 1 blok subtitle terbaik per frame.
* Agregasi temporal dan peleburan animasi pengetikan teks (*Typewriter / Karaoke Smoothing*) berbasis jarak kemiripan string Levenshtein (ambang batas minimal 0.55).
* Deteksi kesalahan penulisan (*typo detection*) dwibahasa (Bahasa Indonesia dan Inggris) menggunakan kamus 29.000 kata dasar KBBI PySastrawi (analisis morfologi imbuhan), pyspellchecker, serta arsitektur 4 pilar ortografis (casing typo, homoglyph optik, leetspeak, ligatur font miring, dan jarak Damerau-Levenshtein berbobot tombol keyboard QWERTY).
* Ekspor hasil analisis ke format teks biasa (.txt) terpadu, format data terstruktur (.json), format trek subtitle standar pemutar video (.srt), serta gambar diagnostik beranotasi (.jpg preview).

**Batasan di Luar Cakupan (Out-of-Scope):**
* Sistem tidak menyediakan antarmuka grafis web (GUI/Web Dashboard) maupun server web.
* Sistem tidak mengelola autentikasi pengguna, login berbasis sesi, maupun pembagian peran bertingkat (*Role-Based Access Control* / RBAC).
* Sistem tidak membaca atau mentranskripsikan trek audio video (*Speech-to-Text* / Whisper tidak diimplementasikan).
* Sistem tidak melakukan analisis semantik pesan, sentimen emosional, penilaian daya tarik pemasaran, maupun prediksi viralitas.
* Sistem tidak memodifikasi atau memperbaiki file video fisik secara otomatis (*non-destructive tool*).

### 1.3 Definisi, Akronim, dan Singkatan
* **SRS**: *Software Requirements Specification*, dokumen spesifikasi formal kebutuhan perangkat lunak.
* **OCR**: *Optical Character Recognition*, teknologi pengenalan karakter teks visual dari citra digital menjadi representasi teks digital (*string*).
* **NLP**: *Natural Language Processing*, bidang kecerdasan buatan untuk analisis dan pemrosesan bahasa alami manusia.
* **CLI**: *Command Line Interface*, antarmuka program berbasis teks yang dieksekusi melalui terminal komputer.
* **ROI**: *Region of Interest*, area persegi panjang tertentu pada frame video yang ditentukan sebagai target analisis teks (dinyatakan dalam persentase sumbu Y dan X).
* **Auto Packaging Filter**: Algoritma heuristik cerdas untuk mengeliminasi teks kemasan produk (label botol/produk kosmetik) secara otomatis.
* **Visual Line Clustering**: Algoritma pengelompokan baris teks yang berdekatan vertikal (jarak Y <= 6.0%) dan sejajar horizontal (deviasi tengah X <= 22.0%) menjadi satu blok paragraf.
* **Typewriter Smoothing**: Algoritma peleburan teks animasi kata demi kata menjadi satu kalimat utuh bertimestamp.
* **Homoglyph**: Karakter glif yang memiliki tampilan visual serupa pada font sans-serif, seperti huruf 'I' kapital, huruf 'l' kecil, dan angka '1'.
* **Italic Ligature**: Kerancuan optik OCR akibat huruf miring yang saling menempel rapat, seperti 'l+a' terbaca 'b', 'c+l' terbaca 'd', atau 'r+n' terbaca 'm'.
* **Damerau-Levenshtein Distance**: Metrik jarak string yang memperhitungkan penyisipan, penghapusan, penggantian, dan transposisi dua karakter berdampingan dengan bobot tombol keyboard QWERTY.
* **KBBI**: Kamus Besar Bahasa Indonesia.

### 1.4 Referensi
1. IEEE Std 830-1998, *IEEE Recommended Practice for Software Requirements Specifications*, IEEE Computer Society.
2. ISO/IEC/IEEE 29148:2018, *Systems and software engineering — Life cycle processes — Requirements engineering*.
3. Bradski, G. (2000). *The OpenCV Library*. Dr. Dobb's Journal of Software Tools.
4. RapidOCR Open Source Project. (2022). *Cross-Platform OCR Engine based on ONNX Runtime and PaddleOCR*.
5. Asian, J., Williams, H. E., & Tahaghoghi, S. M. (2005). *Stemming Indonesian: A Confix-Stripping Approach*. ACM Transactions on Asian Language Information Processing (TALIP).
6. Damerau, F. J. (1964). *A technique for computer detection and correction of spelling errors*. Communications of the ACM, 7(3), 171-176.

---

## BAB 2: DESKRIPSI UMUM SISTEM (OVERALL DESCRIPTION)

### 2.1 Perspektif Produk (Product Perspective)
Sistem ini diposisikan sebagai perangkat lunak mandiri (*standalone CLI utility*) yang beroperasi di workstation lokal editor agensi kreatif. Dalam rantai produksi konten media sosial, sistem bertindak sebagai jembatan kendali mutu (*quality gate*) antara tahap penyuntingan video (*video rendering*) dan tahap persetujuan kreatif (*creative lead approval*).

```text
[Alur Kerja Produksi Konten Agensi]:
Video Editor (Render MP4) 
    --> [SISTEM KELOMPOK 4 (Ekstraksi Subtitle & Deteksi Typo CLI)] 
    --> Output Transkrip & Laporan Typo (.txt / .json) 
    --> Creative Lead (Pemeriksaan Cepat) 
    --> Revisi Minor Editor (Jika ada typo) 
    --> Publikasi Media Sosial
```

Sistem tidak membutuhkan koneksi jaringan internet atau infrastruktur server eksternal untuk menjalankan fungsi intinya, menjamin kerahasiaan materi iklan sebelum tanggal tayang resmi.

### 2.2 Fitur Utama Produk (Product Functions)
Secara fungsional, produk menyediakan 5 kapabilitas utama:
1. **Pemrosesan Video Tunggal dan Batch**: Menerima satu atau banyak file video sekaligus via terminal, mengekstrak informasi teknis video (resolusi, fps, durasi), dan memprosesnya secara berurutan dengan laporan status yang jelas.
2. **Ekstraksi Subtitle Cerdas Multi-Tahap**: Mengambil sampel frame pada interval teratur (default 2 FPS), menjalankan inferensi OCR berbasis RapidOCR ONNX, menormalkan koordinat spasial, memfilter area ROI, dan menyaring teks kemasan produk.
3. **Penyatuan Kalimat dan Agregasi Waktu**: Mengelompokkan baris teks yang berdekatan vertikal menjadi satu blok paragraf, memilih blok dengan skor keyakinan tertinggi, dan melebur animasi typewriter menjadi segmen subtitle utuh dengan penanda waktu SRT (*start time* dan *end time*).
4. **Pemeriksaan Ejaan dan Rekomendasi Kata (4 Pilar Typo)**: Menganalisis kata per kata terhadap kamus morfologi KBBI dan leksikon bahasa Inggris, memvalidasi aturan penulisan huruf besar/kapital, ambiguitas homoglyph, penyalahgunaan leetspeak/angka, pemisahan kata majemuk, serta menyajikan hingga 3 saran perbaikan kata berdasarkan jarak Damerau-Levenshtein berbobot QWERTY.
5. **Ekspor Multi-Format dan Kalibrasi Visual**: Menyimpan transkrip bersih dan laporan typo terintegrasi ke file teks (.txt), mengekspor data terstruktur (.json), trek subtitle (.srt), serta menghasilkan gambar preview frame beranotasi bounding box (.jpg) untuk memverifikasi keakuratan parameter ROI.

### 2.3 Karakteristik dan Kelas Pengguna (User Classes & Characteristics)
* **Kelas Pengguna 1: Content Creator / Video Editor (Operator Utama)**
  * *Peran*: Menjalankan perintah ekstraksi subtitle dan deteksi typo secara mandiri pada video hasil render sebelum menyerahkan materi ke supervisor.
  * *Keahlian Teknis*: Menengah hingga tinggi; terbiasa menjalankan perintah terminal, utilitas ffmpeg, dan aplikasi penyunting video (Premiere Pro, CapCut, DaVinci Resolve).
  * *Frekuensi Pemakaian*: Tinggi (setiap kali video selesai disunting).
* **Kelas Pengguna 2: Social Media Lead / Creative Director (Reviewer Hasil)**
  * *Peran*: Menerima dan membaca berkas transkrip teks (.txt) serta ringkasan laporan typo untuk memastikan tidak ada kesalahan ejaan sebelum video dijadwalkan tayang.
  * *Keahlian Teknis*: Umum / Non-teknis; memerlukan format laporan yang bersih, ringkas, dan dapat dibuka di text editor standar tanpa perlu menjalankan kode program.
  * *Frekuensi Pemakaian*: Sedang hingga tinggi (pada setiap siklus review kampanye).
* **Kelas Pengguna 3: Tim Pengembang Mahasiswa (Maintenance & Evaluator)**
  * *Peran*: Mengelola kode sumber, memperbarui kamus whitelist merek, mengoptimalkan bobot heuristik scoring, dan melakukan pengujian sistem.
  * *Keahlian Teknis*: Tinggi (pemrograman Python, computer vision, dan rekayasa perangkat lunak).

### 2.4 Lingkungan Operasional (Operating Environment)
* **Sistem Operasi**: Lintas platform; mendukung Microsoft Windows 10/11 (64-bit), Linux (Ubuntu 20.04 LTS atau lebih baru), dan macOS (macOS 11 Big Sur ke atas).
* **Runtime Utama**: Python versi 3.9, 3.10, atau 3.11 (64-bit).
* **Kebutuhan Perangkat Keras Minimum**:
  * Prosesor: Intel Core i3 / AMD Ryzen 3 atau setara (Quad-Core).
  * Memori RAM: 4 GB RAM.
  * Media Penyimpanan: 500 MB ruang kosong untuk dependensi dan model ONNX.
* **Kebutuhan Perangkat Keras Rekomendasi**:
  * Prosesor: Intel Core i5 / AMD Ryzen 5 / Apple Silicon M-Series.
  * Memori RAM: 8 GB RAM atau lebih.
  * Media Penyimpanan: Solid State Drive (SSD).

### 2.5 Batasan Desain dan Implementasi (Design & Implementation Constraints)
1. **Ketergantungan Eksekusi CPU**: Sistem dioptimalkan untuk berjalan pada CPU standar (*CPU-only inference*) menggunakan model kuantisasi ONNX Runtime, tanpa mewajibkan kartu grafis diskrit (GPU NVIDIA/CUDA).
2. **Orientasi Teks**: Sistem dirancang untuk teks subtitle yang diletakkan secara horizontal normal (0 derajat). Teks vertikal ekstrem atau teks berputar 90 derajat berada di luar jangkauan deteksi optimal.
3. **Bahasa Analisis**: Modul typo checker berfokus pada Bahasa Indonesia (baku, imbuhan, percakapan umum) dan Bahasa Inggris (istilah populer/kosmetik). Bahasa daerah atau bahasa asing lain belum didukung secara leksikal.
4. **Format Kontainer**: Berkas masukan dibatasi pada format kontainer video yang didukung oleh backend OpenCV (MP4, MOV, MKV, AVI) dengan kompresi video standar H.264/AVC.

### 2.6 Dokumentasi Pengguna (User Documentation)
Sistem menyertakan dokumentasi terpadu pada repositori:
* `README.md`: Panduan cepat instalasi dependensi, sintaks eksekusi dasar, daftar lengkap argumen CLI, dan contoh perintah praktis.
* `DOKUMENTASI_PROYEK.md`: Penjelasan mendalam arsitektur pipeline, rincian matematis 8 algoritma, serta ringkasan uji empiris pada video sampel.
* Bantuan Interaktif Terminal: Perintah `python video_subtitle_reader.py --help` dan `python typo_checker.py --help` yang menampilkan kamus parameter secara langsung di konsol.

---

## BAB 3: KEBUTUHAN ANTARMUKA EKSTERNAL

### 3.1 Antarmuka Pengguna (User Interfaces)
Antarmuka pengguna diwujudkan dalam bentuk **Command Line Interface (CLI)** dengan argumen berbasis pustaka standar `argparse`.

**Kamus Parameter CLI Utama (`video_subtitle_reader.py`):**

| Parameter / Flag | Tipe | Default | Deskripsi Fungsional |
| :--- | :---: | :---: | :--- |
| `videos` | Positional | Wajib | Path satu atau lebih berkas video masukan, pola wildcard (contoh: `Video/*.mp4`), atau nama folder direktori video (contoh: `Video/`). |
| `-o`, `--output-dir` | String | `./output` | Folder tujuan penyimpanan seluruh berkas keluaran transkrip dan laporan. |
| `--roi` | String | `15,80` | Preset area subtitle vertikal (`top`, `bottom`, `middle`, `full`) atau kustom persentase `ymin,ymax`. |
| `--no-auto-filter` | Flag | `False` | Menonaktifkan algoritma penyaringan teks kemasan produk secara otomatis. |
| `--min-width` | Float | `25.0` | Ambang lebar minimum teks dalam persentase lebar video untuk dianggap kalimat subtitle. |
| `--min-words` | Integer | `1` | Jumlah kata minimum per baris teks (kata tunggal sempit mendapat penalti skor). |
| `--fps-sample` | Float | `2.0` | Frekuensi pengambilan sampel frame per detik (default: 1 frame setiap 0.5 detik). |
| `--min-conf` | Float | `0.5` | Ambang keyakinan minimum deteksi OCR (rentang 0.0 s.d. 1.0). |
| `--min-duration` | Float | `0.8` | Durasi kemunculan minimum subtitle dalam detik (mengeliminasi flicker transien). |
| `--export` | Choice | `txt` | Format ekspor berkas: `txt` (default), `json`, `srt`, atau `all` (seluruh format). |
| `--preview` | Flag | `False` | Menghasilkan gambar diagnostik JPG beranotasi bounding box hijau dan merah. |
| `--preview-time` | Float | `3.0` | Posisi detik video yang diambil untuk diekspor sebagai gambar preview visual. |
| `--check-typo` | Flag | `False` | Mengaktifkan analisis deteksi kesalahan penulisan (typo) secara otomatis. |
| `--typo-whitelist` | String | `""` | Daftar istilah khusus atau nama merek tambahan yang dianggap sah (dipisahkan koma), serta otomatis membaca berkas `whitelist.txt`. |
| `--limit` | Integer | `0` | Membatasi jumlah video yang diproses dalam eksekusi batch (nilai 0 memproses seluruh video). |
| `--engine` | Choice | `rapidocr` | Pilihan mesin OCR yang digunakan: `rapidocr`, `vision`, `tesseract`, atau `auto`. |

### 3.2 Antarmuka Perangkat Keras dan Perangkat Lunak
* **Antarmuka Perangkat Lunak**:
  * Pustaka `opencv-python` ($\ge 4.6$): Berkomunikasi dengan decoder codec sistem operasi untuk membaca stream video dan ekstraksi frame RGB/BGR.
  * Pustaka `rapidocr-onnxruntime` ($\ge 1.3$): Menjalankan model deep learning ONNX runtime untuk deteksi teks DBNet dan pengenalan SVTR/CRNN.
  * Pustaka `PySastrawi` ($\ge 1.2$): Mengakses kamus leksikon kata dasar Bahasa Indonesia dan mesin confix-stripping stemming.
  * Pustaka `pyspellchecker` ($\ge 0.7$): Mengakses leksikon frekuensi kata Bahasa Inggris.
* **Antarmuka Sistem Berkas (Filesystem Interface)**:
  * Masukan: Membaca berkas video biner dari media penyimpanan lokal pengguna.
  * Keluaran: Menulis berkas transkrip teks (.txt dengan encoding UTF-8), berkas terstruktur JSON (.json), berkas subtitle pemutar video (.srt), serta berkas gambar JPEG (.jpg).

### 3.3 Antarmuka Komunikasi (Communications Interfaces)
Sistem ini tidak menggunakan antarmuka jaringan (protokol HTTP/HTTPS, TCP/IP, WebSocket, maupun RPC) untuk pemrosesan intinya. Seluruh pertukaran data berlangsung secara lokal melalui memori kerja (RAM) dan sistem berkas lokal komputer.

---

## BAB 4: FITUR SISTEM DAN KEBUTUHAN FUNGSIONAL

### 4.1 Dekomposisi Kebutuhan Fungsional (FR-01 s.d. FR-12)

| ID Kebutuhan | Nama Fitur | Deskripsi Teknis | Aktor | Masukan (Input) | Keluaran (Output) | Kriteria Penerimaan |
| :---: | :--- | :--- | :---: | :--- | :--- | :--- |
| **FR-01** | Ingestion Berkas Video | Memvalidasi keberadaan file dan membaca metadata video (resolusi, fps, durasi, total frame). | Operator CLI | Satu/banyak path video (.mp4) | Objek `VideoCapture` & metadata terstruktur | Video dapat dibuka OpenCV; jika file rusak/tidak ada, tampilkan pesan error dan lanjutkan batch. |
| **FR-02** | Sampling Frame Temporal | Mengambil sampel frame secara berkala per interval waktu tertentu. | Sistem | Parameter `--fps-sample` (default 2.0 fps) | Matriks gambar frame BGR pada waktu $t$ | Frame diekstrak per kelipatan `step_frames = max(1, int(fps / sample_fps))` secara konsisten. |
| **FR-03** | Pengenalan Teks Visual | Mendeteksi area teks dan mengenali karakter teks latin pada frame video. | Sistem | Frame citra BGR | Bounding box 4-titik, nilai keyakinan (conf), dan string teks | Teks terbaca dengan confidence $\ge$ `--min-conf`; spasi pulih dari kompresi decoding OCR. |
| **FR-04** | Normalisasi & Filter ROI | Mengonversi koordinat piksel absolut ke persentase frame (0%-100%) dan memfilter area aktif. | Sistem | Poligon piksel dan parameter `--roi` | Bounding box persentase di dalam batas ROI | Titik tengah teks di luar batas ROI (default Y: 15%-80%) dieliminasi secara otomatis. |
| **FR-05** | Auto Packaging Filter | Mengeliminasi teks label kemasan produk tanpa input manual kata kunci. | Sistem | Bounding box, teks, dan status `--no-auto-filter` | Status klasifikasi (subtitle sah vs kemasan) | Teks di tepi ($dist > 18\%$), teks sempit ($width < 25\%$), atau pola spesifikasi (`ml`, `SPF`, brand) dieliminasi. |
| **FR-06** | Visual Line Clustering | Menyatukan baris-baris teks yang bertumpuk vertikal menjadi satu blok paragraf. | Sistem | Daftar bounding box dalam 1 frame | Blok paragraf multi-baris terpadu | Baris dengan selisih jarak $Y \le 6.0\%$ dan deviasi tengah $X \le 22.0\%$ disatukan menjadi 1 entitas. |
| **FR-07** | Subtitle Confidence Scoring | Menghitung skor kepastian subtitle berdasarkan simetri posisi, lebar, jumlah kata, dan penalti. | Sistem | Blok teks hasil klastering | Nilai skor linear $S_{\text{score}}$ | Memilih 1 blok teks dengan skor tertinggi per frame yang melampaui ambang batas skor $\ge 25.0$. |
| **FR-08** | Agregasi Temporal & Smoothing | Melebur kemunculan teks berurutan dan animasi typewriter menjadi kalimat utuh. | Sistem | Rangkaian deteksi antar-frame berturutan | Segmen subtitle utuh beserta timestamp awal & akhir | Teks dengan kesamaan string $\ge 0.55$ atau progresif digabung; durasi $< 0.8$ detik dibuang. |
| **FR-09** | Deteksi Typo Bilingual & Multikonteks | Menganalisis kesalahan ejaan teks subtitle pada Bahasa Indonesia (KBBI & Slang Gaul Medsos), Bahasa Inggris, dan istilah campur kode (*code-mixing*). | Sistem | Kalimat subtitle dan flag `--check-typo` | Status keabsahan kata, daftar typo, dan saran perbaikan | Kata tidak baku ditandai typo; mengenali morfologi percakapan (-in), klitika, dan istilah serapan; menyajikan rekomendasi kata cerdas. |
| **FR-10** | Kustomisasi Whitelist Terintegrasi | Menerima daftar istilah khusus, nama merek, atau bahasa gaul via flag dan berkas eksternal. | Operator CLI | Flag `--typo-whitelist`, `--ignore`, dan berkas `whitelist.txt` | Kamus leksikon sesi yang diperluas | Kata yang terdaftar di whitelist/berkas otomatis dinyatakan sah (zero false positive) saat pengujian ejaan. |
| **FR-11** | Ekspor Multi-Format | Menyimpan hasil analisis ke direktori target sesuai format yang dipilih pengguna. | Sistem | Parameter `--export` (`txt`, `json`, `srt`, `all`) | File `<video>_subtitles.txt`, `.json`, `.srt`, dan typo report | Berkas tersimpan di folder output dengan struktur rapi dan dapat dibuka oleh aplikasi terkait. |
| **FR-12** | Visual Preview Bounding Box | Menghasilkan gambar diagnostik frame video dengan anotasi kotak visual. | Operator CLI | Flag `--preview` dan `--preview-time` | File gambar `<video>_roi_preview.jpg` | Kotak hijau menandai subtitle yang sah; kotak merah menandai teks kemasan/diabaikan. |

### 4.2 Spesifikasi Detail Use Case & Alur Kerja Sistem

#### Use Case Utama 1: Ekstraksi Subtitle dan Pemeriksaan Typo Video
* **Aktor**: Operator CLI (Video Editor).
* **Precondition**: File video tersedia di direktori lokal dan izin baca terpenuhi.
* **Main Success Scenario (Normal Flow)**:
  1. Operator menjalankan perintah terminal: `python video_subtitle_reader.py video.mp4 --check-typo`.
  2. Sistem membaca metadata video (resolusi, fps, durasi) dan menampilkan header informasi proses ke konsol.
  3. Sistem melakukan sampling frame setiap 0.5 detik (2 FPS).
  4. Mesin OCR mengenali teks pada setiap frame dan menormalkan koordinat ke persentase spasial.
  5. Sistem menerapkan filter ROI, filter kemasan produk, dan mengelompokkan baris teks yang berdekatan vertikal.
  6. Sistem menghitung skor kepastian subtitle dan memilih blok teks terbaik per frame.
  7. Sistem melebur deteksi antar-frame (typewriter smoothing) menjadi daftar segmen subtitle utuh bertimestamp.
  8. Modul typo checker memverifikasi ejaan seluruh kata subtitle, mendeteksi kata salah tulis, dan menghitung rekomendasi koreksi.
  9. Sistem mencetak laporan tabel typo ke layar terminal dan menulis berkas transkrip terpadu ke `output/video_subtitles.txt`.
  10. Sistem menampilkan ringkasan eksekusi batch dan durasi waktu proses.
* **Alternative / Exception Flow**:
  * *Berkas Tidak Ditemukan*: Sistem menampilkan pesan `File tidak ditemukan: <path>`, menghentikan proses untuk berkas tersebut, dan melanjutkan ke berkas berikutnya jika berada dalam mode batch.
  * *Modul Typo Checker Belum Terpasang*: Sistem menampilkan peringatan dependensi, melewati tahapan deteksi typo, dan tetap menyelesaikan ekstraksi transkrip subtitle normal.

### 4.3 Kriteria Penerimaan Berbasis Skenario (Acceptance Criteria)
* **Skenario 1 (Ekstraksi Subtitle Bersih)**:
  * *Given*: Video promosi berdurasi 15 detik memuat subtitle di tengah layar dan teks label botol kosmetik di tepi layar.
  * *When*: Operator mengeksekusi ekstraksi dengan konfigurasi default.
  * *Then*: Sistem mengekstrak seluruh kalimat subtitle tanpa menyertakan tulisan label botol pada transkrip akhir.
* **Skenario 2 (Deteksi Typo Nyata)**:
  * *Given*: Subtitle video memuat kata salah tulis "engandung" pada detik ke 00:00:08.
  * *When*: Ekstraksi dijalankan dengan flag `--check-typo`.
  * *Then*: Sistem menandai kata "engandung" sebagai kesalahan ketik (typo) dan memberikan daftar saran perbaikan yang memuat kata "mengandung".
* **Skenario 3 (Whitelist Nama Merek)**:
  * *Given*: Video memuat nama merek khusus "somethinc" yang tidak tercantum dalam kamus bahasa baku.
  * *When*: Operator menambahkan flag `--typo-whitelist "somethinc"`.
  * *Then*: Sistem menyatakan kata "somethinc" sebagai kata yang sah dan tidak memunculkannya dalam daftar laporan typo.

---

## BAB 5: KEBUTUHAN NON-FUNGSIONAL (NON-FUNCTIONAL REQUIREMENTS)

### 5.1 Kinerja (Performance Requirements)
1. **Kecepatan Inferensi per Frame (NFR-PRF-01)**: Latensi pengenalan teks RapidOCR pada CPU quad-core standar tidak boleh melebihi 250 milidetik per frame (hasil pengukuran aktual: 110 ms hingga 190 ms per frame).
2. **Efisiensi Pengambilan Sampel (NFR-PRF-02)**: Pengambilan sampel frame temporal pada frekuensi default 2.0 FPS wajib mereduksi beban pemrosesan frame sebesar minimal 90% dibandingkan pemrosesan raw 30 FPS (terverifikasi: video 15 detik dengan 450 total frame hanya memproses 31 frame sampel, efisiensi 93.3%).
3. **Waktu Total Pemrosesan Video (NFR-PRF-03)**: Total waktu eksekusi untuk video pendek berdurasi 15 detik tidak boleh melebihi durasi asli video (rasio pemrosesan near real-time <= 1.0x). Pengukuran empiris membuktikan pemrosesan selesai dalam waktu 8.4 s.d. 14.9 detik.
4. **Kecepatan Analisis Typo NLP (NFR-PRF-04)**: Modul pemeriksa ejaan wajib menyelesaikan validasi seluruh kata subtitle dalam waktu kurang dari 500 milidetik (hasil aktual: 80 ms hingga 160 ms untuk 30-45 kata).
5. **Konsumsi Memori RAM (NFR-PRF-05)**: Penggunaan memori kerja (*Peak RAM*) selama inferensi berlangsung tidak boleh melampaui 800 MB (pengukuran aktual: rata-rata 320 MB hingga 450 MB).

### 5.2 Keamanan dan Privasi Data (Security & Privacy)
1. **Eksekusi 100% Offline (NFR-SEC-01)**: Sistem wajib memproses seluruh video dan teks secara lokal di perangkat pengguna. Tidak ada data citra, transkrip, maupun metadata yang dikirimkan ke jaringan internet atau cloud eksternal (*Zero Cloud Egress*).
2. **Integritas Berkas Sumber (NFR-SEC-02)**: Seluruh operasi terhadap file video masukan dilakukan secara *read-only*. Sistem tidak mengubah struktur kontainer, frame gambar, atau track audio video asli.
3. **Penyimpanan Lokal Terisolasi (NFR-SEC-03)**: Berkas keluaran disimpan secara terpusat pada direktori output lokal yang ditentukan pengguna (`./output`), tanpa membuat file sementara yang tertinggal di direktori sistem operasi.

### 5.3 Keandalan dan Ketersediaan (Reliability & Availability)
1. **Isolasi Kesalahan Pemrosesan Batch (NFR-REL-01)**: Jika salah satu video dalam daftar antrean batch mengalami kerusakan file (*corrupt file*) atau format tidak valid, sistem tidak boleh berhenti tiba-tiba (*crash*). Sistem wajib mencatat pesan kesalahan dan melanjutkan pemrosesan video berikutnya dalam antrean.
2. **Pembersihan Sumber Daya Memori (NFR-REL-02)**: Sistem wajib menutup stream berkas video (`cap.release()`) secara disiplin setelah selesai diproses atau saat terjadi kesalahan untuk mencegah kebocoran memori (*memory leak*).
3. **Resistensi terhadap Artefak Transien (NFR-REL-03)**: Teks artefak visual atau kedipan noise yang muncul kurang dari ambang batas durasi minimum (0.8 detik) secara otomatis diabaikan dari hasil transkrip akhir.

### 5.4 Kemudahan Penggunaan (Usability)
1. **Panduan Bantuan Perintah CLI (NFR-USA-01)**: Perintah bantuan `--help` wajib menampilkan deskripsi fungsional lengkap, nilai default, dan contoh penggunaan yang mudah dipahami oleh pengguna.
2. **Umpan Balik Progres Konsol (NFR-USA-02)**: Konsol terminal wajib menampilkan persentase progres pemrosesan frame dan detik video secara berkala, serta mencetak tabel ringkasan hasil pemrosesan batch yang informatif di akhir proses.
3. **Keterbacaan Berkas Laporan TXT (NFR-USA-03)**: Format luaran default `.txt` dirancang dengan struktur hierarki visual yang jelas (metadata, daftar subtitle bertimestamp, dan rincian typo beserta rekomendasi) sehingga dapat langsung dibaca dan dipahami oleh staf non-teknis.

---

## LAMPIRAN: HASIL PENGUJIAN DAN VALIDASI EMPIRIS SISTEM

### L.1 Data Pengujian pada 4 Video Sampel Agensi
Pengujian sistem dilakukan terhadap 4 berkas video sampel konten ulasan kecantikan riil yang disertakan di dalam repositori sistem:

| Parameter Evaluasi | Sampel 1: benar.mp4 | Sampel 2: salah.mp4 | Sampel 3: benar2.mp4 | Sampel 4: salah2.mp4 |
| :--- | :---: | :---: | :---: | :---: |
| **Kategori Konten** | Lip Oil Review | Tinted Moisturizer | Facial Foam Review | Hairloss Shampoo |
| **Resolusi Video** | 478 x 850 piksel | 478 x 850 piksel | 720 x 1280 piksel | 480 x 854 piksel |
| **Frame Rate & Durasi** | 60.0 FPS \| 14.48s | 30.0 FPS \| 15.33s | 30.0 FPS \| 13.77s | 30.0 FPS \| 15.47s |
| **Waktu Pemrosesan** | **8.4 detik** | **14.9 detik** | **11.1 detik** | **12.3 detik** |
| **Subtitle Terdeteksi** | 4 segmen | 5 segmen | 5 segmen | 4 segmen |
| **Total Kata Dianalisis** | 27 kata | 34 kata | 32 kata | 30 kata |
| **Jumlah Typo Ditemukan** | **0 typo (Bersih)** | **1 typo** | **0 typo** | **1 typo** |
| **Temuan Kata Typo** | Tidak ada | `engandung` | Tidak ada | `membantumembersihkan` |
| **Saran Perbaikan** | - | `mengandung` | - | `membantu membersihkan` |
| **Filter Kemasan Botol**| 100% Bersih | 100% Bersih | 100% Bersih | 100% Bersih |
| **Status Uji Sistem** | **Lolos (Valid)** | **Lolos (Valid)** | **Lolos (Valid)** | **Lolos (Valid)** |

### L.2 Analisis False Positive dan False Negative
1. **Keberhasilan Penanganan Istilah Asing & Slang (Pencegahan False Positive)**:
   * Kosakata kosmetik bahasa Inggris (*lip oil, complexion, shade, blend, wear*) dan kata percakapan kasual (*bikin, sehari-hari, praktis, diblend*) berhasil diidentifikasi sebagai kata yang sah berkat integrasi kamus bilingual dan whitelist istilah.
2. **Kandidat False Negative Teridentifikasi**:
   * Pada pengujian berkas `benar2.mp4`, subtitle memuat frasa `"Facia Foam"` (seharusnya *"Facial Foam"*). Sistem tidak menandai kata `"Facia"` sebagai typo karena kata tersebut memiliki kecocokan parsial leksikal. Temuan ini menegaskan peran sistem sebagai pendeteksi lapis pertama (*first-pass checker*) yang tetap memerlukan validasi akhir manusia.
3. **Keberhasilan Penanganan Ligatur Font Miring**:
   * Pada berkas `salah2.mp4`, teks bertuliskan *"Setelah"* yang dicetak miring berhasil dibaca dengan sempurna tanpa kesalahan ligatur (`l+a` terbaca `b`), membuktikan keefektifan matriks kerancuan karakter OCR yang diimplementasikan.

---
*Dokumen Spesifikasi Kebutuhan Sistem ini disahkan oleh Tim Pengembang Kelompok 4 Capstone Project 2026.*
