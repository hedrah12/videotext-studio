# 🚀 Panduan Deployment Server: videotext Studio v1.0
**Proyek Capstone Kelompok 4**  
*"Pengembangan Sistem Ekstraksi Subtitle Video dan Deteksi Kesalahan Penulisan Berbasis OCR dan NLP untuk Konten Agensi"*

---

## 📋 1. Spesifikasi Server yang Direkomendasikan
Karena sistem ini menjalankan model Deep Learning inferensi per-frame (**RapidOCR DBNet + SVTR berbasis ONNX Runtime**) dan NLP (**PySastrawi + Damerau-Levenshtein**), spesifikasi server yang disarankan adalah:

| Komponen | Spesifikasi Minimum | Spesifikasi Rekomendasi (Production) |
|---|---|---|
| **OS** | Ubuntu 20.04 / 22.04 LTS, Debian 11+, atau macOS | Ubuntu 22.04 LTS / Debian 12 |
| **CPU** | 2 vCPU Core | 4 vCPU Core (Multithreaded OCR lebih cepat) |
| **RAM** | 2 GB RAM | 4 GB RAM |
| **Penyimpanan** | 10 GB SSD (untuk buffer video uploads) | 20+ GB SSD NVMe |
| **Python** | Python 3.9 - 3.11 | Python 3.10 |

---

## 💻 2. Menjalankan Sistem Secara Lokal (Windows / macOS)

### Cara Cepat (Windows):
Cukup jalankan file launcher yang sudah disediakan:
```cmd
RUN_SYSTEM_MASTER.bat
```
Atau langsung jalankan server web:
```cmd
cd web_app
run_web.bat
```
Browser akan otomatis terbuka ke `http://localhost:5000`.

---

## 🐧 3. Panduan Deployment Manual Server Linux (Ubuntu / Debian VPS)
Sistem ini berjalan mandiri (native) menggunakan Python Virtual Environment tanpa membutuhkan Docker atau containerization.

### 1. Install Dependensi Sistem Linux
```bash
sudo apt update && sudo apt install -y python3 python3-pip python3-venv ffmpeg libgomp1
```

### 2. Setup Virtual Environment Python
```bash
cd /var/www/videotext  # sesuaikan path proyek Anda
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Jalankan Server via Systemd (Otomatis Restart jika Server Reboot)
Buat service file:
```bash
sudo nano /etc/systemd/system/videotext.service
```

Isi dengan konfigurasi berikut:
```ini
[Unit]
Description=VideoText Studio v1.0 - Capstone Kelompok 4
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/videotext
ExecStart=/var/www/videotext/venv/bin/python web_app/server.py 5000
Restart=always
RestartSec=5
Environment=PORT=5000

[Install]
WantedBy=multi-user.target
```

Aktifkan service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable videotext
sudo systemctl start videotext
sudo systemctl status videotext
```

---

## 🌐 4. Konfigurasi Reverse Proxy Nginx & Domain (Opsional tapi Direkomendasikan)

Jika Anda menghubungkan domain (contoh: `videotext.kampus.ac.id`), gunakan Nginx sebagai reverse proxy.

> ⚠️ **PENTING**: Karena pemrosesan video berdurasi 15-30 detik membutuhkan waktu komputasi OCR sekitar 15-40 detik, naikkan timeout Nginx (`proxy_read_timeout 300s;`) agar tidak terjadi error `504 Gateway Timeout`!

Contoh konfigurasi Nginx (`/etc/nginx/sites-available/videotext`):
```nginx
server {
    listen 80;
    server_name domain-anda.com;

    client_max_body_size 100M;  # Izinkan upload video hingga 100MB

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeout diperpanjang untuk inferensi video OCR
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }
}
```
Aktifkan konfigurasi Nginx:
```bash
sudo ln -s /etc/nginx/sites-available/videotext /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## ✅ 5. Checklist Verifikasi Sebelum Go-Live

- [x] **File `requirements.txt`**: Sudah tersedia dan menggunakan `opencv-python-headless` (bebas dependency X11).
- [x] **Dynamic Port**: `server.py` sudah mendukung variabel environment `PORT` dari cloud.
- [x] **Streaming Seekable**: Endpoint `/api/video/<filename>` mendukung HTTP 206 Partial Content untuk seek milidetik.
- [x] **Database SQLite**: Terinisialisasi otomatis saat server start dan menyimpan riwayat analisis.
- [x] **Folder Izin Tulis**: Direktori `web_app/uploads/` dan `videotext/output/` siap menerima file.
