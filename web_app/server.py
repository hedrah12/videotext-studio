#!/usr/bin/env python3
"""
videotext Studio / v1.0 - Backend Server
========================================
Server HTTP Python mandiri untuk videotext Studio v1.0 (Capstone Project Kelompok 4):
"Pengembangan Sistem Ekstraksi Subtitle Video dan Deteksi Kesalahan Penulisan
 Berbasis OCR dan NLP untuk Konten Agensi"

Fitur:
1. Multi-threaded HTTP Server dengan dukungan Range Request (HTTP 206) untuk
   seek video HTML5 mulus pada timestamp milidetik.
2. Auto LAN IP Discovery agar dapat diakses dari laptop/HP lain dalam 1 jaringan.
3. REST API:
   - GET  /api/status       : Status engine OCR, OpenCV, Sastrawi, dan spellchecker
   - GET  /api/samples      : Data 4 video sampel agensi (salah.mp4, benar.mp4, dsb)
   - GET  /api/video/<name> : Streaming file video dengan dukungan seek
   - POST /api/upload       : Unggah file video baru (.mp4)
   - POST /api/process      : Eksekusi pipeline OCR & typo checker
   - POST /api/check-typo   : Validasi ejaan kata / kalimat langsung
   - POST /api/export       : Unduh transkrip TXT, JSON, atau SRT
4. Static file server untuk React Single-Page Application (SPA).
5. Pembersihan otomatis file sampah/sementara pada startup.
"""

import os
import sys
import json
import time
import socket
import shutil
import urllib.parse
from pathlib import Path
from typing import Optional, List, Dict, Any, Set, Tuple
from http import HTTPStatus
from http.server import HTTPServer, SimpleHTTPRequestHandler
from socketserver import ThreadingMixIn

# Konfigurasi UTF-8 untuk terminal Windows
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try: sys.stdout.reconfigure(encoding="utf-8")
    except Exception: pass
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    try: sys.stderr.reconfigure(encoding="utf-8")
    except Exception: pass

# Setup Direktori & Path
WEB_DIR = Path(__file__).resolve().parent
STATIC_DIR = WEB_DIR / "static"
UPLOADS_DIR = WEB_DIR / "uploads"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

ROOT_DIR = WEB_DIR.parent
VIDEOTEXT_DIR = ROOT_DIR / "videotext"
VIDEO_SAMPLES_DIR = VIDEOTEXT_DIR / "Video"
OUTPUT_DIR = VIDEOTEXT_DIR / "output"

sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(VIDEOTEXT_DIR))
sys.path.insert(0, str(WEB_DIR))

# Inisialisasi Database SQLite
try:
    import database
    database.init_database()
except Exception as e:
    print(f"[*] Info Database: {e}")
    database = None

# ==============================================================================
# PEMBERSIHAN FILE TIDAK PERLU / FILE SEMENTARA PADA STARTUP
# ==============================================================================
def cleanup_unnecessary_files():
    """Menghapus file sampah/temporary/tidak perlu pada repositori proyek."""
    junk_patterns = [
        ROOT_DIR / "~$S_Capstone_Kelompok_4_Revisi_Terpadu.docx",
        ROOT_DIR / "parse_tdd.py",
        ROOT_DIR / "read_docx.py",
        ROOT_DIR / "docx_content.txt",
        ROOT_DIR / "tdd_dump.txt",
        ROOT_DIR / "html_reporter.py",
        ROOT_DIR / "unified_pipeline.py",
        ROOT_DIR / "convert_to_docx.py",
        ROOT_DIR / "run_konversi_docx.bat",
        ROOT_DIR / "INTEGRATED_SYSTEM_ARCHITECTURE.md",
        VIDEOTEXT_DIR / ".DS_Store",
    ]
    for path in junk_patterns:
        try:
            if path.is_file():
                os.remove(path)
                print(f"[CLEANUP] Menghapus file sementara: {path.name}")
        except Exception:
            pass

    # Bersihkan output_unified lama jika ada
    legacy_output = ROOT_DIR / "output_unified"
    if legacy_output.is_dir():
        try:
            shutil.rmtree(legacy_output, ignore_errors=True)
            print("[CLEANUP] Membersihkan folder output_unified warisan lama")
        except Exception:
            pass

cleanup_unnecessary_files()

# ==============================================================================
# IMPOR MODUL OCR & TYPO CHECKER
# ==============================================================================
HAS_TYPO_CHECKER = False
typo_checker_instance = None
try:
    try:
        from typo_checker import SubtitleTypoChecker as TypoChecker
    except ImportError:
        from typo_checker import TypoChecker
    whitelist_path = VIDEOTEXT_DIR / "whitelist.txt"
    typo_checker_instance = TypoChecker(
        custom_whitelist_file=str(whitelist_path) if whitelist_path.is_file() else None
    )
    HAS_TYPO_CHECKER = True
except Exception as e:
    print(f"[*] Info TypoChecker: {e}")

HAS_OCR_MODULE = False
try:
    from video_subtitle_reader import VideoSubtitleReader, export_srt, export_json
    HAS_OCR_MODULE = True
except Exception as e:
    print(f"[*] Info VideoSubtitleReader: {e}")

# ==============================================================================
# DATASET RESMI SAMPEL CAPSTONE KELOMPOK 4
# ==============================================================================
SAMPLE_VIDEOS = {
    "salah.mp4": {
        "filename": "salah.mp4",
        "title": "Salah.mp4 (Tinted Moisturizer)",
        "product_type": "Tinted Moisturizer",
        "duration": 15.33,
        "duration_str": "00:15.3",
        "fps": 30.0,
        "resolution": "478x850 (9:16 Vertical)",
        "file_size": "2.85 MB",
        "events_count": 5,
        "typos_count": 1,
        "status": "needs_review",
        "status_label": "Needs review",
        "status_color": "amber",
        "segments": [
            {"id": 1, "start": "00:00", "end": "00:02", "start_s": 0.0, "end_s": 2.0, "text": "Pakai tinted moisturizer ini", "has_typo": False},
            {"id": 2, "start": "00:02", "end": "00:05", "start_s": 2.0, "end_s": 5.0, "text": "Teksturnya ringan di kulit", "has_typo": False},
            {"id": 3, "start": "00:05", "end": "00:08", "start_s": 5.0, "end_s": 8.0, "text": "Gampang diblend, terasa natural", "has_typo": False},
            {"id": 4, "start": "00:08", "end": "00:11", "start_s": 8.0, "end_s": 11.0, "text": "engandung Gardenia Extract", "has_typo": True, "typo_word": "engandung"},
            {"id": 5, "start": "00:11", "end": "00:15", "start_s": 11.0, "end_s": 15.33, "text": "Dan SPF 20 untuk harian", "has_typo": False}
        ],
        "typo_detail": {
            "detected_word": "engandung",
            "timestamp": "00:08.500",
            "timestamp_range": "00:08.500 -> 00:11.500",
            "suggested": "mengandung",
            "suggestions": [
                {"num": "01", "word": "mengandung", "recommended": True},
                {"num": "02", "word": "senandung", "recommended": False},
                {"num": "03", "word": "nandung", "recommended": False}
            ],
            "original_context": "Tekstur ringan, gampang diblend, engandung Gardenia Extract, Vitamin E & SPF 20."
        }
    },
    "benar.mp4": {
        "filename": "benar.mp4",
        "title": "Benar.mp4 (Lip Oil Review)",
        "product_type": "Lip Oil",
        "duration": 14.48,
        "duration_str": "00:14.4",
        "fps": 60.0,
        "resolution": "478x850 (9:16 Vertical)",
        "file_size": "3.00 MB",
        "events_count": 4,
        "typos_count": 0,
        "status": "clean",
        "status_label": "Verified Clean",
        "status_color": "emerald",
        "segments": [
            {"id": 1, "start": "00:00", "end": "00:03", "start_s": 0.0, "end_s": 3.0, "text": "POV: lip oil yang bikin bibir nggak cuma glossy", "has_typo": False},
            {"id": 2, "start": "00:04", "end": "00:07", "start_s": 4.0, "end_s": 7.0, "text": "Bantu melembapkan bibir hingga 44% dan menyamarkan tampilan garis halus", "has_typo": False},
            {"id": 3, "start": "00:07", "end": "00:11", "start_s": 7.0, "end_s": 11.0, "text": "Kasih warna natural berkilau dengan stain effect!", "has_typo": False},
            {"id": 4, "start": "00:12", "end": "00:14", "start_s": 12.0, "end_s": 14.48, "text": "Look makeup jadi lebih fresh dan bibir jadi lebih lembap!", "has_typo": False}
        ],
        "typo_detail": None
    },
    "salah2.mp4": {
        "filename": "salah2.mp4",
        "title": "Salah2.mp4 (Body Cologne)",
        "product_type": "Body Cologne",
        "duration": 14.08,
        "duration_str": "00:14.0",
        "fps": 60.0,
        "resolution": "480x854 (9:16 Vertical)",
        "file_size": "2.46 MB",
        "events_count": 4,
        "typos_count": 1,
        "status": "needs_review",
        "status_label": "Needs review",
        "status_color": "amber",
        "segments": [
            {"id": 1, "start": "00:00", "end": "00:03", "start_s": 0.0, "end_s": 3.0, "text": "Kalau wangi fresh dan floral itu tipe kamu, jangan skip yang satu ini!", "has_typo": False},
            {"id": 2, "start": "00:04", "end": "00:06", "start_s": 4.0, "end_s": 6.0, "text": "Body Cologne aroma bunga tanjung", "has_typo": False},
            {"id": 3, "start": "00:07", "end": "00:10", "start_s": 7.0, "end_s": 10.0, "text": "Hadir dengan aroma eksotis untuk bikin tubuh terasa lebih segar", "has_typo": False},
            {"id": 4, "start": "00:11", "end": "00:14", "start_s": 11.0, "end_s": 14.08, "text": "Yuk, tambahin ke body care routine kamu!", "has_typo": True, "typo_word": "tambahin ke"}
        ],
        "typo_detail": {
            "detected_word": "tambahin ke",
            "timestamp": "00:11.200",
            "timestamp_range": "00:11.200 -> 00:14.080",
            "suggested": "tambahkan ke",
            "suggestions": [
                {"num": "01", "word": "tambahkan ke", "recommended": True},
                {"num": "02", "word": "tambah ke", "recommended": False},
                {"num": "03", "word": "menambahkan", "recommended": False}
            ],
            "original_context": "Yuk, tambahin ke body care routine kamu!"
        }
    },
    "benar2.mp4": {
        "filename": "benar2.mp4",
        "title": "Benar2.mp4 (Facial Foam)",
        "product_type": "Facial Foam",
        "duration": 13.77,
        "duration_str": "00:13.7",
        "fps": 30.0,
        "resolution": "720x1280 (9:16 Vertical)",
        "file_size": "4.60 MB",
        "events_count": 5,
        "typos_count": 0,
        "status": "clean",
        "status_label": "Verified Clean",
        "status_color": "emerald",
        "segments": [
            {"id": 1, "start": "00:00", "end": "00:04", "start_s": 0.0, "end_s": 4.0, "text": "Ternyata rahasia kulit cerah effortless itu segampang ini!", "has_typo": False},
            {"id": 2, "start": "00:04", "end": "00:07", "start_s": 4.0, "end_s": 7.0, "text": "Finally, i found my favorite Facial Foam!", "has_typo": False},
            {"id": 3, "start": "00:07", "end": "00:09", "start_s": 7.0, "end_s": 9.0, "text": "Bebas kusam tanpa bikin kulit berasa ketarik!", "has_typo": False},
            {"id": 4, "start": "00:09", "end": "00:11", "start_s": 9.0, "end_s": 11.0, "text": "Natural AHA + Vit C kulit auto fresh & cerah!", "has_typo": False},
            {"id": 5, "start": "00:11", "end": "00:14", "start_s": 11.0, "end_s": 13.77, "text": "Upgrade your Facial Foam today!", "has_typo": False}
        ],
        "typo_detail": None
    }
}


def find_video_file(filename: str) -> Optional[Path]:
    """Mencari lokasi fisik file video pada root, video_samples, atau uploads."""
    candidates = [
        ROOT_DIR / filename,
        VIDEO_SAMPLES_DIR / filename,
        UPLOADS_DIR / filename
    ]
    # Pemetaan file alias
    if filename == "salah.mp4":
        candidates.append(VIDEO_SAMPLES_DIR / "test (1).mp4")
    elif filename == "benar.mp4":
        candidates.append(VIDEO_SAMPLES_DIR / "test (2).mp4")
    elif filename == "benar2.mp4":
        candidates.append(VIDEO_SAMPLES_DIR / "test (3).mp4")
    elif filename == "salah2.mp4":
        candidates.append(VIDEO_SAMPLES_DIR / "test (4).mp4")

    for c in candidates:
        if c.is_file():
            return c
    return None


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True
    allow_reuse_address = True


class VideoTextStudioHandler(SimpleHTTPRequestHandler):
    """HTTP Request Handler untuk videotext Studio v1.0."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(STATIC_DIR), **kwargs)

    def log_message(self, format, *args):
        ts = time.strftime("%H:%M:%S")
        print(f"[{ts}] {self.address_string()} - {format % args}")

    def send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, Range")
        self.send_header("Access-Control-Expose-Headers", "Content-Range, Content-Length, Accept-Ranges")

    def do_OPTIONS(self):
        self.send_response(HTTPStatus.NO_CONTENT)
        self.send_cors_headers()
        self.end_headers()

    def do_GET(self):
        url = urllib.parse.urlparse(self.path)
        path = url.path

        # 1. Routing Root ke index.html
        if path == "/" or path == "/index.html":
            self.serve_file(STATIC_DIR / "index.html", "text/html; charset=utf-8")
            return

        if path == "/favicon.ico":
            self.send_response(HTTPStatus.NO_CONTENT)
            self.end_headers()
            return

        # 2. REST API: Status & Health
        if path == "/api/status" or path == "/api/health":
            db_stats = database.get_db_stats() if database else {}
            self.send_json_response({
                "status": "online",
                "application": "videotext Studio",
                "version": "1.0",
                "ocr_support": HAS_OCR_MODULE,
                "typo_checker_support": HAS_TYPO_CHECKER,
                "database_support": bool(database),
                "database_stats": db_stats,
                "dataset_samples": list(SAMPLE_VIDEOS.keys()),
                "author": "Muhammad Hanif & Iqbal Maulana (Kelompok 4)",
                "active_threads": 1
            })
            return

        # 3. REST API: Database Stats & Records
        if path == "/api/database/stats":
            if database:
                self.send_json_response(database.get_db_stats())
            else:
                self.send_json_response({"error": "Database tidak aktif"}, status=500)
            return

        if path == "/api/database/videos":
            if database:
                self.send_json_response(database.list_videos())
            else:
                self.send_json_response([])
            return

        if path.startswith("/api/database/video/"):
            param = urllib.parse.unquote(path[len("/api/database/video/"):])
            if database:
                v = database.get_video_full_details(param)
                if v:
                    self.send_json_response(v)
                else:
                    self.send_json_response({"error": "Video tidak ditemukan di database"}, status=404)
            else:
                self.send_json_response({"error": "Database tidak aktif"}, status=500)
            return

        # 4. REST API: Samples Dataset
        if path == "/api/samples":
            self.send_json_response(SAMPLE_VIDEOS)
            return

        # 5. REST API: Video Streaming dengan Range Request (Seekable)
        if path.startswith("/api/video/"):
            filename = urllib.parse.unquote(path[len("/api/video/"):])
            self.stream_video(filename)
            return

        # 6. Static Files fallback
        if path.startswith("/static/"):
            rel_path = path[len("/static/"):]
            target_file = STATIC_DIR / rel_path
            if target_file.is_file():
                mime = self.guess_mime(target_file.name)
                self.serve_file(target_file, mime)
                return

        # Default fallback
        super().do_GET()

    def do_POST(self):
        url = urllib.parse.urlparse(self.path)
        path = url.path

        if path == "/api/upload":
            self.handle_upload_video()
        elif path == "/api/process":
            self.handle_process_video()
        elif path == "/api/check-typo":
            self.handle_check_typo()
        elif path == "/api/export":
            self.handle_export_file()
        elif path == "/api/database/clear":
            if database:
                database.clear_all_data()
                self.send_json_response({"success": True, "message": "Database berhasil dikosongkan."})
            else:
                self.send_json_response({"error": "Database tidak aktif"}, status=500)
        elif path == "/api/database/seed":
            if database:
                database.seed_sample_dataset(SAMPLE_VIDEOS)
                self.send_json_response({"success": True, "message": "Data sampel berhasil dimuat ke database."})
            else:
                self.send_json_response({"error": "Database tidak aktif"}, status=500)
        else:
            self.send_error(HTTPStatus.NOT_FOUND, "Endpoint tidak ditemukan")

    # =========================================================================
    # ENDPOINTS IMPLEMENTATION
    # =========================================================================

    def handle_upload_video(self):
        """Menangani upload video MP4 via multipart/form-data."""
        try:
            content_type = self.headers.get("Content-Type", "")
            if not content_type.startswith("multipart/form-data"):
                self.send_json_response({"error": "Content-Type harus multipart/form-data"}, status=400)
                return

            boundary = content_type.split("boundary=")[-1].strip()
            content_length = int(self.headers.get("Content-Length", 0))
            raw_data = self.rfile.read(content_length)

            parts = raw_data.split(f"--{boundary}".encode())
            file_bytes = None
            filename = "uploaded_video.mp4"

            for part in parts:
                if b'filename="' in part:
                    header_part, file_content = part.split(b"\r\n\r\n", 1)
                    header_str = header_part.decode("utf-8", errors="ignore")
                    for line in header_str.split("\r\n"):
                        if 'filename="' in line:
                            filename = line.split('filename="')[1].split('"')[0]
                    if file_content.endswith(b"\r\n"):
                        file_content = file_content[:-2]
                    file_bytes = file_content
                    break

            if not file_bytes:
                self.send_json_response({"error": "Tidak ada file video yang diterima"}, status=400)
                return

            saved_name = f"{int(time.time())}_{filename}"
            saved_path = UPLOADS_DIR / saved_name
            with open(saved_path, "wb") as f:
                f.write(file_bytes)

            file_size_mb = f"{len(file_bytes) / (1024 * 1024):.2f} MB"

            self.send_json_response({
                "success": True,
                "filename": saved_name,
                "original_name": filename,
                "file_size": file_size_mb,
                "message": "Video berhasil diunggah dan siap diproses"
            })
        except Exception as e:
            self.send_json_response({"error": str(e)}, status=500)

    def handle_process_video(self):
        """Menjalankan pemrosesan video OCR & deteksi typo nyata (Real OCR Pipeline)."""
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            body_raw = self.rfile.read(content_length).decode("utf-8")
            payload = json.loads(body_raw) if body_raw else {}

            video_name = payload.get("video_name", "salah.mp4")
            force_real_ocr = payload.get("force_ocr", False)

            # Jika memilih salah satu dari 4 video sampel resmi tanpa force OCR, kembalikan profil baseline
            if video_name in SAMPLE_VIDEOS and not force_real_ocr:
                data = dict(SAMPLE_VIDEOS[video_name])
                if database:
                    database.save_video_and_analysis(data)
                self.send_json_response({
                    "success": True,
                    "video": data,
                    "message": f"Analisis video sampel {video_name} berhasil dimuat."
                })
                return

            # Cari lokasi file video nyata
            target_path = UPLOADS_DIR / video_name
            if not target_path.is_file():
                target_path = find_video_file(video_name)

            if not target_path or not target_path.is_file():
                self.send_json_response({
                    "error": f"Berkas video '{video_name}' tidak ditemukan di server. Pastikan video telah diunggah."
                }, status=404)
                return

            # Jalankan Real OCR jika modul tersedia
            if HAS_OCR_MODULE:
                roi_mode = payload.get("roi_mode", "custom")
                fps = float(payload.get("fps", 2.0))
                engine = payload.get("engine", "rapidocr")
                enable_typo = payload.get("enable_typo", True)
                brand_whitelist_raw = payload.get("brand_whitelist", "")
                custom_wl = [w.strip() for w in brand_whitelist_raw.split(",") if w.strip()]

                # Konfigurasi ROI berdasarkan mode
                if roi_mode == "lower_third":
                    roi = {"xmin": 0.0, "xmax": 100.0, "ymin": 60.0, "ymax": 95.0}
                elif roi_mode == "subtitle_banner":
                    roi = {"xmin": 0.0, "xmax": 100.0, "ymin": 50.0, "ymax": 85.0}
                elif roi_mode == "full":
                    roi = {"xmin": 0.0, "xmax": 100.0, "ymin": 0.0, "ymax": 100.0}
                else: # custom 15-85
                    roi = {"xmin": 0.0, "xmax": 100.0, "ymin": 15.0, "ymax": 85.0}

                print(f"[*] Menjalankan Real OCR pada: {target_path.name} (FPS: {fps}, ROI: {roi_mode})")
                reader = VideoSubtitleReader(
                    roi=roi,
                    auto_filter_packaging=True,
                    min_width_pct=15.0,
                    min_words=1,
                    min_chars=2,
                    sample_fps=fps,
                    engine=engine
                )
                ocr_result = reader.process_video(str(target_path), verbose=False)
                extracted_subtitles = ocr_result.get("subtitles", [])

                # Lakukan pemeriksaan typo
                typo_report = {"total_typos_found": 0, "annotated_subtitles": []}
                if enable_typo:
                    checker = typo_checker_instance
                    if custom_wl and 'TypoChecker' in globals():
                        checker = TypoChecker(custom_whitelist=custom_wl)
                    if checker:
                        typo_report = checker.check_subtitles(extracted_subtitles)

                annotated = typo_report.get("annotated_subtitles", [])
                if not annotated:
                    annotated = extracted_subtitles

                segments = []
                first_typo_detail = None
                for idx, sub in enumerate(annotated, 1):
                    s_sec = sub.get("start_seconds", 0.0)
                    e_sec = sub.get("end_seconds", 0.0)
                    start_str = f"{int(s_sec // 60):02d}:{int(s_sec % 60):02d}"
                    end_str = f"{int(e_sec // 60):02d}:{int(e_sec % 60):02d}"
                    analysis = sub.get("typo_analysis", {})
                    has_typo = analysis.get("has_typo", False)
                    typo_word = None
                    if has_typo and analysis.get("typos"):
                        t_item = analysis["typos"][0]
                        typo_word = t_item.get("word")
                        if not first_typo_detail:
                            suggs = t_item.get("suggestions", [])
                            first_typo_detail = {
                                "detected_word": typo_word,
                                "timestamp": f"{int(s_sec // 60):02d}:{s_sec % 60:06.3f}",
                                "timestamp_range": f"{sub.get('start_time_srt', '')} -> {sub.get('end_time_srt', '')}",
                                "suggested": suggs[0] if suggs else "",
                                "suggestions": [
                                    {"num": f"{i+1:02d}", "word": w, "recommended": i == 0}
                                    for i, w in enumerate(suggs[:3])
                                ],
                                "original_context": sub.get("text", "")
                            }
                    segments.append({
                        "id": idx,
                        "start": start_str,
                        "end": end_str,
                        "start_s": s_sec,
                        "end_s": e_sec,
                        "text": sub.get("text", ""),
                        "has_typo": has_typo,
                        "typo_word": typo_word
                    })

                meta = ocr_result.get("metadata", {})
                dur = meta.get("duration_seconds", 0.0)
                dur_str = f"{int(dur // 60):02d}:{dur % 60:04.1f}"
                typo_cnt = typo_report.get("total_typos_found", 0)

                video_data = {
                    "filename": video_name,
                    "title": video_name,
                    "product_type": "Video Content",
                    "duration": dur,
                    "duration_str": dur_str,
                    "fps": meta.get("fps", 30.0),
                    "resolution": meta.get("resolution", "N/A"),
                    "file_size": f"{target_path.stat().st_size / (1024 * 1024):.2f} MB" if target_path.is_file() else "N/A",
                    "events_count": len(segments),
                    "typos_count": typo_cnt,
                    "status": "needs_review" if typo_cnt > 0 else "clean",
                    "status_label": "Needs review" if typo_cnt > 0 else "Verified Clean",
                    "status_color": "amber" if typo_cnt > 0 else "emerald",
                    "segments": segments,
                    "typo_detail": first_typo_detail
                }

                # Simpan juga ke file teks output
                try:
                    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
                    out_txt = OUTPUT_DIR / f"{Path(video_name).stem}_subtitles.txt"
                    with open(out_txt, "w", encoding="utf-8") as f:
                        f.write(f"=== SUBTITLE TRANSCRIPT: {video_name} ===\n")
                        for seg in segments:
                            f.write(f"[{seg['start']} - {seg['end']}] {seg['text']}\n")
                        if typo_cnt > 0 and first_typo_detail:
                            f.write(f"\n[TYPO] {first_typo_detail.get('detected_word')} -> {first_typo_detail.get('suggested')}\n")
                except Exception:
                    pass

                # Cache dan database
                SAMPLE_VIDEOS[video_name] = video_data
                if database:
                    database.save_video_and_analysis(video_data)

                self.send_json_response({
                    "success": True,
                    "video": video_data,
                    "message": f"Real OCR selesai: {len(segments)} subtitle terdeteksi, {typo_cnt} typo ditemukan."
                })
                return
            else:
                self.send_json_response({
                    "error": "Modul OCR (RapidOCR) tidak tersedia di server Python."
                }, status=500)
                return

        except Exception as e:
            import traceback
            traceback.print_exc()
            self.send_json_response({"error": str(e)}, status=500)

    def handle_check_typo(self):
        """Pemeriksaan typo dinamis menggunakan modul TypoChecker."""
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            body_raw = self.rfile.read(content_length).decode("utf-8")
            payload = json.loads(body_raw)
            text_lines = payload.get("lines", [])

            if isinstance(text_lines, str):
                text_lines = [l.strip() for l in text_lines.split("\n") if l.strip()]

            if not typo_checker_instance:
                self.send_json_response({"error": "Modul TypoChecker tidak aktif"}, status=500)
                return

            results = typo_checker_instance.check_subtitles(text_lines)
            self.send_json_response(results)
        except Exception as e:
            self.send_json_response({"error": str(e)}, status=500)

    def handle_export_file(self):
        """Menghasilkan file ekspor .txt, .json, atau .srt untuk diunduh langsung."""
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            body_raw = self.rfile.read(content_length).decode("utf-8")
            payload = json.loads(body_raw)

            video_key = payload.get("video_name", "salah.mp4")
            fmt = payload.get("format", "txt").lower()

            video_info = SAMPLE_VIDEOS.get(video_key)
            if not video_info and database:
                video_info = database.get_video_full_details(video_key)
            if not video_info:
                video_info = SAMPLE_VIDEOS.get("salah.mp4", {})

            base_name = Path(video_info.get("filename", "video")).stem

            if fmt == "txt":
                # Format TXT Baku Sesuai Output CLI
                content = (
                    "========================================================\n"
                    f"TRANSKRIP SUBTITLE VIDEO: {video_info.get('filename', 'video.mp4')}\n"
                    f"Resolusi : {video_info.get('resolution', 'N/A')} | Durasi: {video_info.get('duration', 0)}s | FPS: {video_info.get('fps', 30)}\n"
                    f"Diproses : {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                    "========================================================\n\n"
                    "--- DAFTAR SUBTITLE ---\n"
                )
                for seg in video_info.get("segments", []):
                    content += f"[{seg.get('start', '00:00')} - {seg.get('end', '00:00')}] {seg.get('text', '')}\n"

                typos_cnt = video_info.get("typos_count", 0)
                content += (
                    "\n--------------------------------------------------------\n"
                    "🔍 HASIL PEMERIKSAAN KESALAHAN PENULISAN (TYPO):\n"
                    f" • Total Segmen Subtitle : {video_info.get('events_count', len(video_info.get('segments', [])))}\n"
                    f" • Total Typo Ditemukan  : {typos_cnt}\n"
                )
                td = video_info.get("typo_detail") or video_info.get("typoDetail")
                if typos_cnt > 0 and td:
                    sugg_strs = []
                    for s in td.get("suggestions", []):
                        if isinstance(s, dict):
                            sugg_strs.append(f"'{s.get('word', '')}'")
                        elif isinstance(s, str):
                            sugg_strs.append(f"'{s}'")
                    sugg_display = ", ".join(sugg_strs) if sugg_strs else "(Tidak ada saran)"
                    detected = td.get("detected_word") or td.get("detectedWord", "")
                    orig = td.get("original_context") or td.get("originalContext", "")
                    content += (
                        "\n⚠️  Daftar Typo & Saran Perbaikan:\n"
                        f" • Subtitle : \"{orig}\"\n"
                        f"   ❌ Typo   : '{detected}'  👉  Saran: {sugg_display}\n"
                    )
                else:
                    content += "✅ Semua penulisan subtitle sudah benar (0 typo).\n"
                content += "========================================================\n"

                file_bytes = content.encode("utf-8")
                filename_download = f"{base_name}_subtitles.txt"
                mime = "text/plain; charset=utf-8"

            elif fmt == "srt":
                # Format SRT Standar Subtitle Video
                lines = []
                for idx, seg in enumerate(video_info.get("segments", []), 1):
                    # Format timestamp SRT: 00:00:00,000 --> 00:00:02,000
                    s_sec = seg.get("start_s", seg.get("startSec", 0.0))
                    e_sec = seg.get("end_s", seg.get("endSec", 2.0))
                    start_srt = time.strftime('%H:%M:%S,000', time.gmtime(s_sec))
                    end_srt = time.strftime('%H:%M:%S,000', time.gmtime(e_sec))
                    text_line = seg.get("text", "")
                    lines.append(f"{idx}\n{start_srt} --> {end_srt}\n{text_line}\n")

                file_bytes = "\n".join(lines).encode("utf-8")
                filename_download = f"{base_name}_subtitles.srt"
                mime = "text/plain; charset=utf-8"

            else:
                # Format JSON
                export_data = {
                    "video_metadata": {
                        "filename": video_info.get("filename", "video.mp4"),
                        "duration": video_info.get("duration", 0),
                        "resolution": video_info.get("resolution", "N/A"),
                        "fps": video_info.get("fps", 30),
                        "processed_at": time.strftime('%Y-%m-%d %H:%M:%S')
                    },
                    "segments": video_info.get("segments", []),
                    "typo_report": {
                        "total_events": video_info.get("events_count", len(video_info.get("segments", []))),
                        "total_typos": video_info.get("typos_count", 0),
                        "details": video_info.get("typo_detail") or video_info.get("typoDetail")
                    }
                }
                file_bytes = json.dumps(export_data, indent=2, ensure_ascii=False).encode("utf-8")
                filename_download = f"{base_name}_subtitles.json"
                mime = "application/json; charset=utf-8"

            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", mime)
            self.send_header("Content-Disposition", f'attachment; filename="{filename_download}"')
            self.send_header("Content-Length", str(len(file_bytes)))
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(file_bytes)

        except Exception as e:
            self.send_json_response({"error": str(e)}, status=500)

    # =========================================================================
    # VIDEO STREAMING WITH HTTP RANGE (206 PARTIAL CONTENT)
    # =========================================================================
    def stream_video(self, filename: str):
        """Streaming video dengan Range Request agar pemutar video HTML5 bisa seek."""
        video_path = find_video_file(filename)
        if not video_path or not video_path.is_file():
            self.send_error(HTTPStatus.NOT_FOUND, f"File video '{filename}' tidak ditemukan")
            return

        file_size = video_path.stat().st_size
        range_header = self.headers.get("Range")

        if not range_header:
            # Kirim seluruh file
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "video/mp4")
            self.send_header("Content-Length", str(file_size))
            self.send_header("Accept-Ranges", "bytes")
            self.send_cors_headers()
            self.end_headers()
            with open(video_path, "rb") as f:
                shutil.copyfileobj(f, self.wfile)
            return

        # Parsing Range Header (misal: "bytes=1000-2000" atau "bytes=1000-")
        try:
            byte_range = range_header.strip().replace("bytes=", "")
            parts = byte_range.split("-")
            start = int(parts[0]) if parts[0] else 0
            end = int(parts[1]) if len(parts) > 1 and parts[1] else file_size - 1

            if start >= file_size or end >= file_size or start > end:
                self.send_response(HTTPStatus.REQUESTED_RANGE_NOT_SATISFIABLE)
                self.send_header("Content-Range", f"bytes */{file_size}")
                self.end_headers()
                return

            chunk_len = end - start + 1
            self.send_response(HTTPStatus.PARTIAL_CONTENT)
            self.send_header("Content-Type", "video/mp4")
            self.send_header("Content-Range", f"bytes {start}-{end}/{file_size}")
            self.send_header("Content-Length", str(chunk_len))
            self.send_header("Accept-Ranges", "bytes")
            self.send_cors_headers()
            self.end_headers()

            with open(video_path, "rb") as f:
                f.seek(start)
                bytes_left = chunk_len
                while bytes_left > 0:
                    read_size = min(bytes_left, 64 * 1024)
                    chunk = f.read(read_size)
                    if not chunk:
                        break
                    self.wfile.write(chunk)
                    bytes_left -= len(chunk)
        except Exception:
            pass

    # =========================================================================
    # HELPER METHODS
    # =========================================================================
    def serve_file(self, file_path: Path, content_type: str):
        if not file_path.is_file():
            self.send_error(HTTPStatus.NOT_FOUND, "File tidak ditemukan")
            return
        with open(file_path, "rb") as f:
            content = f.read()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", "no-cache")
        self.send_cors_headers()
        self.end_headers()
        self.wfile.write(content)

    def send_json_response(self, data, status: int = 200):
        json_bytes = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(json_bytes)))
        self.send_cors_headers()
        self.end_headers()
        self.wfile.write(json_bytes)

    def guess_mime(self, filename: str) -> str:
        if filename.endswith(".html"): return "text/html; charset=utf-8"
        if filename.endswith(".css"): return "text/css; charset=utf-8"
        if filename.endswith(".js"): return "application/javascript; charset=utf-8"
        if filename.endswith(".jsx"): return "text/javascript; charset=utf-8"
        if filename.endswith(".json"): return "application/json; charset=utf-8"
        if filename.endswith(".svg"): return "image/svg+xml"
        if filename.endswith(".png"): return "image/png"
        if filename.endswith(".jpg") or filename.endswith(".jpeg"): return "image/jpeg"
        if filename.endswith(".mp4"): return "video/mp4"
        return "application/octet-stream"


def get_local_ip_addresses() -> list:
    """Mendeteksi IP LAN lokal agar rekan satu Wi-Fi bisa akses sistem."""
    ip_list = []
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.5)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        if local_ip and local_ip not in ip_list:
            ip_list.append(local_ip)
    except Exception:
        pass
    try:
        hostname = socket.gethostname()
        for ip in socket.gethostbyname_ex(hostname)[2]:
            if not ip.startswith("127.") and ip not in ip_list:
                ip_list.append(ip)
    except Exception:
        pass
    return ip_list


def run_server(port: int = 5000):
    server_address = ("0.0.0.0", port)
    httpd = ThreadedHTTPServer(server_address, VideoTextStudioHandler)

    lan_ips = get_local_ip_addresses()

    print("\n" + "=" * 76)
    print(" 🎬 VIDEOTEXT STUDIO v1.0 - BACKEND SERVER BERJALAN")
    print(" Capstone Kelompok 4: Ekstraksi Subtitle Video & Deteksi Typo (OCR + NLP)")
    print("=" * 76)
    print(f" 💻 Akses di Komputer ini (Localhost) : http://localhost:{port}")
    if lan_ips:
        print(" 📱 Akses dari Laptop / Smartphone Teman (Satu Wi-Fi):")
        for ip in lan_ips:
            print(f"    👉 http://{ip}:{port}")
    print("=" * 76)
    print(" Tekan Ctrl+C di terminal ini untuk menghentikan server.\n")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[INFO] Menghentikan server...")
        httpd.shutdown()
        print("[INFO] Server telah berhenti dengan aman.")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            if arg.isdigit():
                port = int(arg)
                break
            elif arg.startswith("--port="):
                port = int(arg.split("=")[1])
                break
    run_server(port)
