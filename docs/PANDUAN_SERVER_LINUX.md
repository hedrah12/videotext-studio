# 🚀 Panduan Deployment Server Linux (Native Python): VideoText Studio v1.0
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

## 🐧 2. Setup Manual pada Server Linux (VPS)

### Langkah 1: Install Dependensi Sistem Linux
```bash
sudo apt update && sudo apt install -y python3 python3-pip python3-venv ffmpeg libgomp1 git
```

### Langkah 2: Clone Repositori & Setup Virtual Environment
```bash
cd /var/www
sudo git clone https://github.com/<username>/<nama-repo>.git videotext
cd videotext

# Buat virtual environment mandiri
python3 -m venv venv
source venv/bin/activate

# Install dependensi
pip install --upgrade pip
pip install -r requirements.txt
```

### Langkah 3: Setup Service Systemd (Jalan Otomatis di Background)
Buat service systemd agar server tetap menyala dan otomatis restart saat reboot:
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

Aktifkan dan jalankan service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable videotext
sudo systemctl start videotext
sudo systemctl status videotext
```

---

## 🌐 3. Konfigurasi Reverse Proxy Nginx & Domain (Opsional)

Jika ingin diakses melalui domain (misal: `videotext.kampus.ac.id`) atau port 80/443:

> ⚠️ **PENTING**: Karena inferensi video OCR membutuhkan waktu komputasi (15-40 detik tergantung durasi), wajib atur timeout Nginx (`proxy_read_timeout 300s;`) agar tidak muncul error `504 Gateway Timeout`.

Buat konfigurasi Nginx:
```bash
sudo nano /etc/nginx/sites-available/videotext
```

Isi konfigurasi:
```nginx
server {
    listen 80;
    server_name domain-anda.com;

    client_max_body_size 100M;  # Batas maksimal upload video

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeout komputasi OCR
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }
}
```

Aktifkan site:
```bash
sudo ln -s /etc/nginx/sites-available/videotext /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## ✅ 4. Checklist Verifikasi Sistem

- [x] **File `requirements.txt`**: Menggunakan `opencv-python-headless` (bebas dependensi GUI X11).
- [x] **Dynamic Port**: `server.py` membaca environment `PORT`.
- [x] **Streaming Seekable**: Mendukung HTTP 206 Partial Content untuk seek milidetik.
- [x] **Database SQLite**: Terinisialisasi otomatis dari `schema.sql`.
- [x] **Folder Static UI**: Frontend langsung disajikan dari `web_app/static/` tanpa perlu node server terpisah.
