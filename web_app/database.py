#!/usr/bin/env python3
"""
videotext Studio / v1.0 - SQLite Database Manager
==================================================
Modul Database Relasional SQLite untuk VideoText Studio (Capstone Project Kelompok 4):
"Pengembangan Sistem Ekstraksi Subtitle Video dan Deteksi Kesalahan Penulisan
 Berbasis OCR dan NLP untuk Konten Agensi"

Menyediakan fungsionalitas CRUD untuk:
1. Metadata Video (videos)
2. Segmen Subtitle Hasil OCR (subtitles)
3. Hasil Deteksi Typo NLP (typo_records)
4. Kata Kamus Kustom (custom_whitelist)
5. Log Audit Sistem (audit_logs)
"""

import os
import sys
import json
import sqlite3
import time
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

DB_PATH = Path(__file__).resolve().parent / "videotext_studio.db"
SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"


def get_db_connection() -> sqlite3.Connection:
    """Membuka koneksi ke berkas database SQLite dengan konfigurasi optimal."""
    conn = sqlite3.connect(str(DB_PATH), timeout=15.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    return conn


def init_database():
    """Inisialisasi tabel dan indeks database jika belum ada."""
    with get_db_connection() as conn:
        if SCHEMA_PATH.is_file():
            with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
                schema_sql = f.read()
            conn.executescript(schema_sql)
        else:
            # Fallback schema inline
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS videos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT UNIQUE NOT NULL,
                    original_name TEXT,
                    product_type TEXT DEFAULT 'Konten Agensi',
                    file_path TEXT,
                    file_size TEXT,
                    duration REAL DEFAULT 0.0,
                    duration_str TEXT DEFAULT '00:00.0',
                    fps REAL DEFAULT 30.0,
                    resolution TEXT DEFAULT '720x1280',
                    events_count INTEGER DEFAULT 0,
                    typos_count INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'pending',
                    status_label TEXT DEFAULT 'Menunggu Proses',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS subtitles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    video_id INTEGER NOT NULL,
                    segment_index INTEGER NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT NOT NULL,
                    start_seconds REAL DEFAULT 0.0,
                    end_seconds REAL DEFAULT 0.0,
                    text TEXT NOT NULL,
                    has_typo INTEGER DEFAULT 0,
                    typo_word TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (video_id) REFERENCES videos(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS typo_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    video_id INTEGER NOT NULL,
                    subtitle_id INTEGER,
                    detected_word TEXT NOT NULL,
                    suggested_word TEXT NOT NULL,
                    suggestions_json TEXT,
                    original_context TEXT,
                    timestamp_range TEXT,
                    is_resolved INTEGER DEFAULT 0,
                    chosen_replacement TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (video_id) REFERENCES videos(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS custom_whitelist (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    word TEXT UNIQUE NOT NULL,
                    category TEXT DEFAULT 'general',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS audit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    video_id INTEGER,
                    message TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
        conn.commit()


def get_db_stats() -> Dict[str, Any]:
    """Mengambil statistik jumlah rekaman data dari database."""
    init_database()
    with get_db_connection() as conn:
        v_count = conn.execute("SELECT COUNT(*) FROM videos;").fetchone()[0]
        s_count = conn.execute("SELECT COUNT(*) FROM subtitles;").fetchone()[0]
        t_count = conn.execute("SELECT COUNT(*) FROM typo_records;").fetchone()[0]
        w_count = conn.execute("SELECT COUNT(*) FROM custom_whitelist;").fetchone()[0]
        l_count = conn.execute("SELECT COUNT(*) FROM audit_logs;").fetchone()[0]

    return {
        "database_file": DB_PATH.name,
        "database_size_bytes": DB_PATH.stat().st_size if DB_PATH.is_file() else 0,
        "database_size_kb": round(DB_PATH.stat().st_size / 1024, 2) if DB_PATH.is_file() else 0,
        "videos_count": v_count,
        "subtitles_count": s_count,
        "typos_count": t_count,
        "whitelist_count": w_count,
        "logs_count": l_count,
        "is_empty": (v_count == 0)
    }


def list_videos() -> List[Dict[str, Any]]:
    """Mengambil seluruh riwayat video yang pernah diproses."""
    init_database()
    with get_db_connection() as conn:
        cursor = conn.execute("""
            SELECT id, filename, original_name, product_type, file_size, 
                   duration, duration_str, fps, resolution, events_count, 
                   typos_count, status, status_label, created_at
            FROM videos 
            ORDER BY id DESC;
        """)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def get_video_full_details(filename_or_id) -> Optional[Dict[str, Any]]:
    """Mengambil video lengkap beserta segmen subtitle dan detail typo."""
    init_database()
    with get_db_connection() as conn:
        if isinstance(filename_or_id, int) or (isinstance(filename_or_id, str) and filename_or_id.isdigit()):
            v_row = conn.execute("SELECT * FROM videos WHERE id = ?;", (int(filename_or_id),)).fetchone()
        else:
            v_row = conn.execute("SELECT * FROM videos WHERE filename = ?;", (str(filename_or_id),)).fetchone()

        if not v_row:
            return None

        video_id = v_row["id"]
        v_dict = dict(v_row)

        # Ambil Subtitles
        s_rows = conn.execute("""
            SELECT id, segment_index as id_seg, start_time as start, end_time as end,
                   start_seconds as start_s, end_seconds as end_s, text,
                   has_typo, typo_word
            FROM subtitles
            WHERE video_id = ?
            ORDER BY segment_index ASC;
        """, (video_id,)).fetchall()

        segments = []
        for s in s_rows:
            seg = dict(s)
            seg["id"] = seg["id_seg"]
            seg["has_typo"] = bool(seg["has_typo"])
            seg["hasTypo"] = seg["has_typo"]
            seg["startSec"] = seg.get("start_s", 0.0)
            seg["endSec"] = seg.get("end_s", 2.0)
            segments.append(seg)
        v_dict["segments"] = segments

        # Ambil Typo Detail
        t_row = conn.execute("""
            SELECT detected_word, suggested_word as suggested, suggestions_json,
                   original_context, timestamp_range, is_resolved, chosen_replacement
            FROM typo_records
            WHERE video_id = ?
            ORDER BY id ASC LIMIT 1;
        """, (video_id,)).fetchone()

        if t_row:
            t_dict = dict(t_row)
            try:
                t_dict["suggestions"] = json.loads(t_dict["suggestions_json"]) if t_dict["suggestions_json"] else []
            except Exception:
                t_dict["suggestions"] = []
            t_dict["detectedWord"] = t_dict["detected_word"]
            t_dict["timestampRange"] = t_dict["timestamp_range"]
            t_dict["originalContext"] = t_dict["original_context"]
            t_dict["timestamp"] = (t_dict["timestamp_range"] or "").split(" -> ")[0] if t_dict.get("timestamp_range") else "00:08.500"
            v_dict["typo_detail"] = t_dict
            v_dict["typoDetail"] = t_dict
        else:
            v_dict["typo_detail"] = None
            v_dict["typoDetail"] = None

        return v_dict


def save_video_and_analysis(video_data: Dict[str, Any]) -> int:
    """Menyimpan data video baru beserta subtitle dan deteksi typo ke SQLite."""
    init_database()
    filename = video_data.get("filename", f"video_{int(time.time())}.mp4")
    original_name = video_data.get("original_name", filename)
    product_type = video_data.get("product_type", "Konten Agensi")
    file_path = video_data.get("file_path", "")
    file_size = video_data.get("file_size", "0 MB")
    duration = float(video_data.get("duration", 0.0))
    duration_str = video_data.get("duration_str", "00:00.0")
    fps = float(video_data.get("fps", 30.0))
    resolution = video_data.get("resolution", "720x1280")
    segments = video_data.get("segments", [])
    events_count = len(segments)
    typos_count = int(video_data.get("typos_count", sum(1 for s in segments if s.get("has_typo") or s.get("hasTypo"))))
    status = video_data.get("status", "needs_review" if typos_count > 0 else "clean")
    status_label = video_data.get("status_label", "Needs review" if typos_count > 0 else "Verified Clean")

    with get_db_connection() as conn:
        # Cek jika video sudah ada sebelumnya, lakukan pembaruan
        existing = conn.execute("SELECT id FROM videos WHERE filename = ?;", (filename,)).fetchone()
        if existing:
            video_id = existing["id"]
            conn.execute("""
                UPDATE videos SET
                    original_name = ?, product_type = ?, file_path = ?, file_size = ?,
                    duration = ?, duration_str = ?, fps = ?, resolution = ?,
                    events_count = ?, typos_count = ?, status = ?, status_label = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?;
            """, (original_name, product_type, file_path, file_size, duration, duration_str,
                  fps, resolution, events_count, typos_count, status, status_label, video_id))
            # Hapus subtitle dan typo lama untuk diperbarui
            conn.execute("DELETE FROM subtitles WHERE video_id = ?;", (video_id,))
            conn.execute("DELETE FROM typo_records WHERE video_id = ?;", (video_id,))
        else:
            cur = conn.execute("""
                INSERT INTO videos (
                    filename, original_name, product_type, file_path, file_size,
                    duration, duration_str, fps, resolution, events_count, typos_count,
                    status, status_label
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (filename, original_name, product_type, file_path, file_size,
                  duration, duration_str, fps, resolution, events_count, typos_count,
                  status, status_label))
            video_id = cur.lastrowid

        # Simpan segmen subtitle
        for idx, seg in enumerate(segments, 1):
            s_text = seg.get("text", "")
            s_start = seg.get("start", seg.get("start_time", "00:00"))
            s_end = seg.get("end", seg.get("end_time", "00:02"))
            s_start_s = float(seg.get("start_s", seg.get("startSec", 0.0)))
            s_end_s = float(seg.get("end_s", seg.get("endSec", 2.0)))
            s_has_typo = 1 if (seg.get("has_typo") or seg.get("hasTypo")) else 0
            s_typo_word = seg.get("typo_word", seg.get("typoWord", None))

            conn.execute("""
                INSERT INTO subtitles (
                    video_id, segment_index, start_time, end_time,
                    start_seconds, end_seconds, text, has_typo, typo_word
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (video_id, idx, s_start, s_end, s_start_s, s_end_s, s_text, s_has_typo, s_typo_word))

        # Simpan rincian typo jika ada
        typo_detail = video_data.get("typo_detail") or video_data.get("typoDetail")
        if typo_detail and isinstance(typo_detail, dict):
            detected_word = typo_detail.get("detected_word", typo_detail.get("detectedWord", ""))
            suggested = typo_detail.get("suggested", "")
            suggestions_list = typo_detail.get("suggestions", [])
            sug_json = json.dumps(suggestions_list, ensure_ascii=False)
            context = typo_detail.get("original_context", typo_detail.get("originalContext", ""))
            ts_range = typo_detail.get("timestamp_range", typo_detail.get("timestampRange", ""))

            conn.execute("""
                INSERT INTO typo_records (
                    video_id, detected_word, suggested_word, suggestions_json,
                    original_context, timestamp_range
                ) VALUES (?, ?, ?, ?, ?, ?);
            """, (video_id, detected_word, suggested, sug_json, context, ts_range))

        # Catat ke log audit
        conn.execute("""
            INSERT INTO audit_logs (event_type, video_id, message)
            VALUES (?, ?, ?);
        """, ("VIDEO_SAVED", video_id, f"Video '{filename}' disimpan dengan {events_count} segmen & {typos_count} typo."))

        conn.commit()
        return video_id


def clear_all_data():
    """Mengosongkan seluruh isi tabel video, subtitle, typo, dan log di database."""
    init_database()
    with get_db_connection() as conn:
        conn.execute("DELETE FROM typo_records;")
        conn.execute("DELETE FROM subtitles;")
        conn.execute("DELETE FROM videos;")
        conn.execute("DELETE FROM audit_logs;")
        conn.execute("INSERT INTO audit_logs (event_type, message) VALUES (?, ?);",
                     ("DB_RESET", "Seluruh data video, subtitle, dan typo berhasil dikosongkan."))
        conn.commit()


def seed_sample_dataset(samples_dict: Dict[str, Any]):
    """Memasukkan 4 dataset sampel resmi Capstone ke dalam database SQLite."""
    init_database()
    for key, data in samples_dict.items():
        save_video_and_analysis(data)


# Jalankan inisialisasi pada import
init_database()

if __name__ == "__main__":
    print(f"[OK] Database SQLite aktif: {DB_PATH}")
    stats = get_db_stats()
    print(f"Statistik Awal: {stats}")
