-- ==============================================================================
-- VIDEOTEXT STUDIO v1.0 - DATABASE SCHEMA (SQLITE / MYSQL COMPATIBLE)
-- Capstone Project Kelompok 4: Muhammad Hanif & Iqbal Maulana
-- "Pengembangan Sistem Ekstraksi Subtitle Video dan Deteksi Kesalahan Penulisan
--  Berbasis OCR dan NLP untuk Konten Agensi"
-- ==============================================================================

-- 1. TABEL UTAMA: VIDEOS
-- Menyimpan metadata video yang diunggah atau diproses oleh sistem
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
    status TEXT DEFAULT 'pending', -- 'pending', 'processing', 'clean', 'needs_review'
    status_label TEXT DEFAULT 'Menunggu Proses',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_videos_filename ON videos(filename);
CREATE INDEX IF NOT EXISTS idx_videos_status ON videos(status);

-- 2. TABEL: SUBTITLES
-- Menyimpan segmen transkrip subtitle hasil ekstraksi OCR per video
CREATE TABLE IF NOT EXISTS subtitles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    video_id INTEGER NOT NULL,
    segment_index INTEGER NOT NULL,
    start_time TEXT NOT NULL,
    end_time TEXT NOT NULL,
    start_seconds REAL DEFAULT 0.0,
    end_seconds REAL DEFAULT 0.0,
    text TEXT NOT NULL,
    has_typo INTEGER DEFAULT 0, -- 0 = False, 1 = True
    typo_word TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (video_id) REFERENCES videos(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_subtitles_video_id ON subtitles(video_id);
CREATE INDEX IF NOT EXISTS idx_subtitles_has_typo ON subtitles(has_typo);

-- 3. TABEL: TYPO_RECORDS
-- Menyimpan rincian deteksi kesalahan penulisan (NLP/PySastrawi/Levenshtein)
CREATE TABLE IF NOT EXISTS typo_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    video_id INTEGER NOT NULL,
    subtitle_id INTEGER,
    detected_word TEXT NOT NULL,
    suggested_word TEXT NOT NULL,
    suggestions_json TEXT, -- Format JSON: [{"num":"01", "word":"mengandung", "recommended":true}, ...]
    original_context TEXT,
    timestamp_range TEXT,
    is_resolved INTEGER DEFAULT 0, -- 0 = Unresolved, 1 = Resolved
    chosen_replacement TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (video_id) REFERENCES videos(id) ON DELETE CASCADE,
    FOREIGN KEY (subtitle_id) REFERENCES subtitles(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_typos_video_id ON typo_records(video_id);

-- 4. TABEL: CUSTOM_WHITELIST
-- Menyimpan kata-kata khusus (istilah kecantikan, nama merek, slang)
CREATE TABLE IF NOT EXISTS custom_whitelist (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word TEXT UNIQUE NOT NULL,
    category TEXT DEFAULT 'general', -- 'beauty', 'brand', 'slang', 'tech'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_whitelist_word ON custom_whitelist(word);

-- 5. TABEL: AUDIT_LOGS
-- Mencatat seluruh aktivitas inferensi, ekstraksi, ekspor, dan manajemen data
CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT NOT NULL, -- 'UPLOAD', 'OCR_EXTRACT', 'TYPO_AUDIT', 'EXPORT', 'DB_CLEAR'
    video_id INTEGER,
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (video_id) REFERENCES videos(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_audit_logs_event ON audit_logs(event_type);
