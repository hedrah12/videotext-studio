#!/usr/bin/env python3
"""
Video Subtitle Reader CLI
Aplikasi Python untuk membaca dan mengekstrak teks (subtitle) dari file video
menggunakan Computer Vision & OCR, dengan fitur canggih:
 - Pemfilteran otomatis teks kemasan produk (Auto Packaging Filter tanpa perlu ketik manual)
 - Penilaian kecerdasan subtitle (Subtitle Confidence Scoring & Visual Line Clustering)
 - Filter Region of Interest (ROI) (top, bottom, middle, full, atau custom ymin,ymax)
 - Pembersihan otomatis efek animasi teks (typewriter/karaoke smoothing)
 - Ekspor ke format JSON, SRT, dan TXT
 - Mode visual preview untuk kalibrasi ROI & bounding box
"""

import os
import sys

# Konfigurasi encoding terminal agar kompatibel dengan Windows CMD/PowerShell (UTF-8 Emoji)
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import json
import time
import argparse
import difflib
import tempfile
import re
import glob
from pathlib import Path
from typing import List, Dict, Any, Optional

import cv2

# Cek ketersediaan RapidOCR (Cross-platform ONNX)
HAS_RAPID_OCR = False
try:
    from rapidocr_onnxruntime import RapidOCR
    HAS_RAPID_OCR = True
except ImportError:
    HAS_RAPID_OCR = False

# Cek ketersediaan Apple Vision framework pada macOS
HAS_APPLE_VISION = False
try:
    import Vision
    from Cocoa import NSURL
    from Quartz import CIImage
    HAS_APPLE_VISION = True
except ImportError:
    HAS_APPLE_VISION = False

# Regex nama brand / varian kemasan
BRAND_REGEX = re.compile(
    r'(sariayu|martha\s*tilaar|marthatilaar|martha|tilaar|tinted\s*moisturizer|tinte\s*d?|sar\s*layu|hadisuwarno|hadisuwar|rudy)',
    re.IGNORECASE
)

# Regex label spesifikasi produk terisolasi yang persis menempel pada botol/kemasan
SPEC_LABEL_REGEX = re.compile(
    r'.*(netto:?\s*\d*.*|spf\s*\d+|vegan|bpom|halal|moist\s*and|natural\s*look|ginseng\s*extrac.*|solution\s*shampoo|hairloss\s*solution).*',
    re.IGNORECASE
)

# Prefix noise / angka / label kemasan yang sering menempel di awal subtitle karena OCR
PREFIX_NOISE_REGEX = re.compile(
    r'^(netto:?\s*|\d+\s*|with\s+|vor,?:?\s*)+',
    re.IGNORECASE
)


class TextDetector:
    """Mesin OCR untuk mendeteksi teks dan bounding box pada frame video (Mendukung RapidOCR, Apple Vision, dan Tesseract)."""

    def __init__(self, engine: str = "rapidocr", min_confidence: float = 0.5):
        self.min_confidence = min_confidence
        self.engine = engine.lower().strip()
        
        if self.engine == "auto":
            if HAS_RAPID_OCR:
                self.engine = "rapidocr"
            elif HAS_APPLE_VISION:
                self.engine = "vision"
            else:
                self.engine = "tesseract"

        if self.engine == "rapidocr":
            if not HAS_RAPID_OCR:
                raise RuntimeError(
                    "RapidOCR tidak tersedia. Pastikan paket 'rapidocr-onnxruntime' sudah terinstall:\n"
                    "pip install rapidocr-onnxruntime"
                )
            self.rapid_ocr = RapidOCR()
        elif self.engine == "vision":
            if not HAS_APPLE_VISION:
                raise RuntimeError(
                    "Apple Vision tidak tersedia. Pastikan Anda menjalankan di macOS dengan paket 'pyobjc-framework-Vision'."
                )

    def detect(self, frame_bgr) -> List[Dict[str, Any]]:
        """Mendeteksi teks pada frame BGR."""
        if self.engine == "rapidocr":
            return self._detect_rapidocr(frame_bgr)
        elif self.engine == "vision":
            return self._detect_vision(frame_bgr)
        elif self.engine == "tesseract":
            return self._detect_tesseract(frame_bgr)
        return []

    def _clean_spaces(self, text: str) -> str:
        """Memulihkan spasi yang hilang akibat kompresi decoding OCR pada teks latin."""
        # 1. Spasi setelah tanda baca (koma, titik dua, titik koma, seru, tanya) jika diikuti huruf/angka
        t = re.sub(r'([,;!?])([A-Za-z0-9])', r'\1 \2', text)
        # 2. Pisahkan camelCase (misal: 'favoriteFacial' -> 'favorite Facial', 'RootExtract' -> 'Root Extract')
        t = re.sub(r'([a-z])([A-Z])', r'\1 \2', t)
        # 3. Spasi di sekitar simbol ampersand (&)
        t = re.sub(r'([A-Za-z0-9])&', r'\1 & ', t)
        t = re.sub(r'&([A-Za-z0-9])', r' & \1', t)
        # 4. Spasi antara singkatan dan angka/kata (misal: 'SPF20' -> 'SPF 20')
        t = re.sub(r'\b(SPF|SPF:?)(\d+)\b', r'\1 \2', t, flags=re.IGNORECASE)
        # 5. Pisahkan kata ganti orang/kata kerja yang sering menyatu (misal: 'ifoundmy' -> 'i found my')
        t = re.sub(r'\b(i)(found|got|feel|love|like|think|want|have|see|need|make|know)(my|the|a|this|it)\b', r'\1 \2 \3', t, flags=re.IGNORECASE)
        t = re.sub(r'\b(i)(found|got|feel|love|like|think|want|have|see|need|make|know)\b', r'\1 \2', t, flags=re.IGNORECASE)
        t = re.sub(r'\b(found|got|feel|love|like|think|want|have|see|need|make|know)(my|the|a|this|it)\b', r'\1 \2', t, flags=re.IGNORECASE)
        # 6. Pemulihan generik kerancuan optik OCR pada font miring/ligature ('l+a' terbaca 'b' -> 'elah', 'olah')
        t = re.sub(r'\b([A-Za-z]+)\s*ebh\b', r'\1elah', t)
        t = re.sub(r'\b([A-Za-z]+)\s*obh\b', r'\1olah', t)
        t = re.sub(r'\b([A-Za-z]+)\s+elah\b', r'\1elah', t)
        return re.sub(r'\s+', ' ', t).strip()

    def _detect_rapidocr(self, frame_bgr) -> List[Dict[str, Any]]:
        orig_h, orig_w = frame_bgr.shape[:2]
        
        # Scaling cerdas: Jika resolusi video < 1400px, lakukan upscaling 2x agar celah spasi antar huruf terbaca jelas
        scale = 2.0 if max(orig_h, orig_w) < 1400 else 1.0
        if scale != 1.0:
            proc_frame = cv2.resize(frame_bgr, (0, 0), fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
        else:
            proc_frame = frame_bgr

        cur_h, cur_w = proc_frame.shape[:2]
        result, _ = self.rapid_ocr(proc_frame)
        if not result:
            return []

        results = []
        for box, text, conf in result:
            conf = float(conf)
            if conf < self.min_confidence:
                continue

            cleaned_text = self._clean_spaces(text)
            if not cleaned_text:
                continue

            # Hitung koordinat persentase (0-100%) terhadap frame yang diproses
            xmin = min(pt[0] for pt in box)
            xmax = max(pt[0] for pt in box)
            ymin = min(pt[1] for pt in box)
            ymax = max(pt[1] for pt in box)

            xmin_pct = (xmin / cur_w) * 100.0
            xmax_pct = (xmax / cur_w) * 100.0
            ymin_pct = (ymin / cur_h) * 100.0
            ymax_pct = (ymax / cur_h) * 100.0

            results.append({
                "text": cleaned_text,
                "confidence": round(conf, 3),
                "bbox_pct": {
                    "xmin": round(xmin_pct, 2),
                    "xmax": round(xmax_pct, 2),
                    "ymin": round(ymin_pct, 2),
                    "ymax": round(ymax_pct, 2),
                    "width": round(xmax_pct - xmin_pct, 2),
                    "height": round(ymax_pct - ymin_pct, 2),
                    "center_x": round((xmin_pct + xmax_pct) / 2.0, 2),
                    "center_y": round((ymin_pct + ymax_pct) / 2.0, 2),
                }
            })
        return results

    def _detect_vision(self, frame_bgr) -> List[Dict[str, Any]]:
        success, buffer = cv2.imencode(".jpg", frame_bgr)
        if not success:
            return []
        
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
            tmp_path = tmp.name
            tmp.write(buffer.tobytes())

        results = []
        try:
            url = NSURL.fileURLWithPath_(tmp_path)
            ci_image = CIImage.imageWithContentsOfURL_(url)
            if not ci_image:
                return []

            handler = Vision.VNImageRequestHandler.alloc().initWithCIImage_options_(ci_image, None)
            request = Vision.VNRecognizeTextRequest.alloc().init()
            request.setRecognitionLevel_(Vision.VNRequestTextRecognitionLevelAccurate)
            request.setUsesLanguageCorrection_(True)

            success, _ = handler.performRequests_error_([request], None)
            if not success or not request.results():
                return []

            for observation in request.results():
                top_candidate = observation.topCandidates_(1)[0]
                conf = float(top_candidate.confidence())
                if conf < self.min_confidence:
                    continue

                bb = observation.boundingBox()
                # Cocoa origin: bottom-left (y=0 bottom, y=1 top).
                # Ubah ke koordinat gambar standar (0,0 top-left) dalam persen (0-100).
                xmin_pct = float(bb.origin.x) * 100.0
                xmax_pct = float(bb.origin.x + bb.size.width) * 100.0
                ymin_pct = (1.0 - (bb.origin.y + bb.size.height)) * 100.0
                ymax_pct = (1.0 - bb.origin.y) * 100.0

                text = top_candidate.string().strip()
                if not text:
                    continue

                results.append({
                    "text": text,
                    "confidence": round(conf, 3),
                    "bbox_pct": {
                        "xmin": round(xmin_pct, 2),
                        "xmax": round(xmax_pct, 2),
                        "ymin": round(ymin_pct, 2),
                        "ymax": round(ymax_pct, 2),
                        "width": round(xmax_pct - xmin_pct, 2),
                        "height": round(ymax_pct - ymin_pct, 2),
                        "center_x": round((xmin_pct + xmax_pct) / 2.0, 2),
                        "center_y": round((ymin_pct + ymax_pct) / 2.0, 2),
                    }
                })
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

        return results

    def _detect_tesseract(self, frame_bgr) -> List[Dict[str, Any]]:
        try:
            import pytesseract
            rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
            data = pytesseract.image_to_data(rgb, output_type=pytesseract.Output.DICT)
            h, w = frame_bgr.shape[:2]
            results = []
            n_boxes = len(data["text"])
            for i in range(n_boxes):
                text = data["text"][i].strip()
                conf = float(data["conf"][i]) / 100.0
                if conf >= self.min_confidence and text:
                    x, y, bw, bh = data["left"][i], data["top"][i], data["width"][i], data["height"][i]
                    xmin_pct = (x / w) * 100.0
                    xmax_pct = ((x + bw) / w) * 100.0
                    ymin_pct = (y / h) * 100.0
                    ymax_pct = ((y + bh) / h) * 100.0
                    results.append({
                        "text": text,
                        "confidence": round(conf, 3),
                        "bbox_pct": {
                            "xmin": round(xmin_pct, 2),
                            "xmax": round(xmax_pct, 2),
                            "ymin": round(ymin_pct, 2),
                            "ymax": round(ymax_pct, 2),
                            "width": round(xmax_pct - xmin_pct, 2),
                            "height": round(ymax_pct - ymin_pct, 2),
                            "center_x": round((xmin_pct + xmax_pct) / 2.0, 2),
                            "center_y": round((ymin_pct + ymax_pct) / 2.0, 2),
                        }
                    })
            return results
        except ImportError:
            raise RuntimeError("pytesseract belum terinstall.")


def parse_roi(roi_str: Optional[str], 
              ymin: Optional[float] = None, 
              ymax: Optional[float] = None,
              xmin: Optional[float] = None, 
              xmax: Optional[float] = None) -> Dict[str, float]:
    """Mengurai parameter ROI ke dalam persentase frame (0-100%)."""
    roi = {
        "xmin": 0.0,
        "xmax": 100.0,
        "ymin": 0.0,
        "ymax": 100.0
    }

    if roi_str:
        s = roi_str.lower().strip()
        if s == "top":
            roi.update({"ymin": 12.0, "ymax": 35.0, "xmin": 5.0, "xmax": 95.0})
        elif s == "bottom":
            roi.update({"ymin": 55.0, "ymax": 90.0, "xmin": 5.0, "xmax": 95.0})
        elif s == "middle":
            roi.update({"ymin": 30.0, "ymax": 70.0, "xmin": 5.0, "xmax": 95.0})
        elif s == "full":
            roi.update({"ymin": 0.0, "ymax": 100.0, "xmin": 0.0, "xmax": 100.0})
        else:
            parts = [float(p.strip()) for p in s.split(",") if p.strip()]
            if len(parts) == 2:
                roi["ymin"], roi["ymax"] = parts[0], parts[1]
            elif len(parts) == 4:
                roi["xmin"], roi["xmax"], roi["ymin"], roi["ymax"] = parts

    if xmin is not None: roi["xmin"] = float(xmin)
    if xmax is not None: roi["xmax"] = float(xmax)
    if ymin is not None: roi["ymin"] = float(ymin)
    if ymax is not None: roi["ymax"] = float(ymax)

    return roi


def is_within_roi(box: Dict[str, float], roi: Dict[str, float]) -> bool:
    """Mengecek apakah pusat teks berada dalam ROI."""
    cx = box["center_x"]
    cy = box["center_y"]
    return (
        roi["xmin"] <= cx <= roi["xmax"] and
        roi["ymin"] <= cy <= roi["ymax"]
    )


def string_similarity(a: str, b: str) -> float:
    """Menghitung rasio kesamaan dua string (0.0 - 1.0)."""
    return difflib.SequenceMatcher(None, a.lower().strip(), b.lower().strip()).ratio()


def is_progressive_or_continuation(text_a: str, text_b: str) -> bool:
    """Mengecek apakah text_b adalah kelanjutan/animasi pengetikan dari text_a."""
    clean_a = text_a.lower().strip()
    clean_b = text_b.lower().strip()
    
    if clean_b.startswith(clean_a) or clean_a.startswith(clean_b):
        return True
    
    words_a = set(clean_a.split())
    words_b = set(clean_b.split())
    if words_a and words_b:
        intersection = words_a.intersection(words_b)
        smaller = min(len(words_a), len(words_b))
        if smaller > 0 and (len(intersection) / smaller) >= 0.65:
            return True

    return False


def seconds_to_srt_time(seconds: float) -> str:
    """Mengubah detik ke format timestamp SRT (HH:MM:SS,mmm)."""
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int(round((seconds - int(seconds)) * 1000))
    if millis >= 1000:
        secs += 1
        millis = 0
    return f"{hrs:02d}:{mins:02d}:{secs:02d},{millis:03d}"


class VideoSubtitleReader:
    """Mesin ekstraksi subtitle video cerdas dengan deteksi otomatis teks kemasan."""

    def __init__(
        self,
        roi: Optional[Dict[str, float]] = None,
        auto_filter_packaging: bool = True,
        min_width_pct: float = 12.0,
        min_words: int = 1,
        min_chars: int = 2,
        min_confidence: float = 0.5,
        sample_fps: float = 2.0,
        min_duration: float = 0.6,
        ignore_keywords: Optional[List[str]] = None,
        engine: str = "rapidocr"
    ):
        self.roi = roi or {"xmin": 0.0, "xmax": 100.0, "ymin": 0.0, "ymax": 100.0}
        self.auto_filter_packaging = auto_filter_packaging
        self.min_width_pct = min_width_pct
        self.min_words = min_words
        self.min_chars = min_chars
        self.sample_fps = sample_fps
        self.min_duration = min_duration
        self.ignore_keywords = [k.lower().strip() for k in (ignore_keywords or []) if k.strip()]
        self.detector = TextDetector(engine=engine, min_confidence=min_confidence)

    def is_manual_ignored(self, text: str) -> bool:
        """Cek apakah teks mengandung kata kunci yang diabaikan manual oleh pengguna."""
        lower = text.lower()
        for kw in self.ignore_keywords:
            if kw in lower:
                return True
        return False

    def clean_text(self, text: str) -> str:
        """Membersihkan prefix noise OCR seperti angka acak atau 'Netto:' di awal baris."""
        cleaned = PREFIX_NOISE_REGEX.sub('', text.strip()).strip()
        return cleaned if cleaned else text

    def is_isolated_packaging_label(self, text: str, width: float) -> bool:
        """
        Mengecek apakah suatu teks adalah label kemasan produk terisolasi (misal: 'Netto: 30g', 'SPF 20', 'VEGAN', 'SARIAYU MARTHA TILAAR').
        PENTING: Jika teks merupakan kalimat subtitle yang membahas manfaat produk (misal: 'mengandung Vitamin E & SPF 20'),
        maka teks tersebut BUKAN kemasan melainkan subtitle yang sah.
        """
        if not self.auto_filter_packaging:
            return False

        clean = text.strip()
        words = clean.split()

        # 1. Label spesifikasi pendek terisolasi (misal 'Netto: 30 g', 'SPF 20', 'VEGAN', 'Moist and', 'Natural Look', 'GINSENG EXTRACT')
        if SPEC_LABEL_REGEX.search(clean) and (width < 45.0 or len(words) <= 3):
            return True

        # 2. Murni nama brand / varian kemasan tanpa kalimat (misal 'SARIAYU MARTHA TILAAR', 'TINTE D', 'RUDY HADISUWARNO')
        if BRAND_REGEX.search(clean):
            if len(words) <= 3 or width < 45.0:
                return True

        # 3. Potongan sangat pendek dan sempit (1 kata <= 5 huruf dan width < 22%)
        if len(words) == 1 and (width < 22.0 or len(clean) <= 4):
            return True

        return False

    def calculate_subtitle_score(self, block: Dict[str, Any]) -> float:
        """
        Memberi skor kepastian apakah blok teks adalah subtitle video:
        - Simetri horizontal / perataan: (+45 poin).
        - Lebar teks kalimat: (+35 poin).
        - Jumlah kata: (+25 poin).
        - Penalti hanya untuk label kemasan terisolasi (-50 poin).
        """
        words = block["text"].split()
        cx = block["center_x"]
        w = block["width"]
        txt = block["text"]

        # 1. Centering (Subtitle berada di tengah atau rata kiri tengah)
        dist_from_center = abs(cx - 50.0)
        center_score = max(-25.0, 45.0 - (dist_from_center * 2.2))
        # Penalti untuk teks di tepi kiri/kanan (biasanya botol/produk yang dipegang di pinggir layar)
        if dist_from_center > 18.0 and w < 60.0:
            center_score -= 30.0

        # 2. Width (Subtitle kalimat membentang horizontal)
        width_score = min(35.0, w * 0.7)

        # 3. Word count (Subtitle berupa frasa/kalimat)
        word_score = min(25.0, len(words) * 5.0)
        if len(words) == 1:
            word_score = -20.0

        # 4. Packaging penalty (Hanya untuk label terisolasi)
        pack_penalty = 0.0
        if self.auto_filter_packaging and self.is_isolated_packaging_label(txt, w):
            pack_penalty = -50.0

        return center_score + width_score + word_score + pack_penalty

    def cluster_and_select_best_subtitle(self, items: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        1. Mengelompokkan baris teks yang berdekatan secara vertikal menjadi satu kesatuan paragraf subtitle.
        2. Memilih blok subtitle terbaik dengan skor tertinggi dan mengabaikan teks kemasan produk.
        """
        if not items:
            return None

        # Urutkan berdasarkan koordinat Y dari atas ke bawah
        items.sort(key=lambda x: x["bbox_pct"]["ymin"])

        clusters = []
        curr = [items[0]]

        for it in items[1:]:
            prev = curr[-1]
            dy = it["bbox_pct"]["ymin"] - prev["bbox_pct"]["ymax"]
            dx_center = abs(it["bbox_pct"]["center_x"] - prev["bbox_pct"]["center_x"])

            # Jika baris kedua berada tepat di bawah baris pertama (jarak Y <= 6% dan center_x sejalan)
            if dy <= 6.0 and dx_center <= 22.0:
                curr.append(it)
            else:
                clusters.append(curr)
                curr = [it]

        if curr:
            clusters.append(curr)

        # Hitung skor untuk setiap cluster
        scored_blocks = []
        for cl in clusters:
            txt = " ".join([x["text"] for x in cl]).strip()
            max_w = max([x["bbox_pct"]["width"] for x in cl])
            avg_cx = sum([x["bbox_pct"]["center_x"] for x in cl]) / len(cl)
            min_y = min([x["bbox_pct"]["ymin"] for x in cl])
            max_y = max([x["bbox_pct"]["ymax"] for x in cl])
            avg_conf = sum([x["confidence"] for x in cl]) / len(cl)

            block = {
                "text": txt,
                "confidence": round(avg_conf, 3),
                "width": max_w,
                "center_x": avg_cx,
                "ymin": min_y,
                "ymax": max_y
            }

            score = self.calculate_subtitle_score(block)
            # Ambang batas skor untuk diterima sebagai subtitle sah (adaptif terhadap subtitle pendek/rata tengah)
            min_threshold = 16.0 if self.auto_filter_packaging else 10.0
            if score >= min_threshold:
                scored_blocks.append((score, block))

        if not scored_blocks:
            return None

        # Ambil blok dengan skor subtitle tertinggi di frame ini
        scored_blocks.sort(key=lambda x: x[0], reverse=True)
        best_score, best_block = scored_blocks[0]
        return best_block

    def process_video(self, video_path: str, verbose: bool = True) -> Dict[str, Any]:
        """Menganalisis video dan menghasilkan struktur data subtitle terstruktur."""
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"File video tidak ditemukan: {video_path}")

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Gagal membuka video: {video_path}")

        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        duration = total_frames / fps if fps > 0 else 0.0

        step_frames = max(1, int(fps / self.sample_fps))

        if verbose:
            print(f"\n========================================================")
            print(f"🎬 Memproses: {os.path.basename(video_path)}")
            print(f"   Resolusi      : {width}x{height} | Durasi: {duration:.2f}s | FPS: {fps:.2f}")
            print(f"   Sampling      : setiap {1.0/self.sample_fps:.2f}s ({step_frames} frame/langkah)")
            print(f"   Filter ROI    : X [{self.roi['xmin']:.1f}% - {self.roi['xmax']:.1f}%], Y [{self.roi['ymin']:.1f}% - {self.roi['ymax']:.1f}%]")
            print(f"   Auto Kemasan  : {'AKTIF (Otomatis mengabaikan teks kemasan/produk)' if self.auto_filter_packaging else 'NONAKTIF'}")
            if self.ignore_keywords:
                print(f"   Ignore Manual : {', '.join(self.ignore_keywords)}")
            print(f"========================================================")

        raw_detections = []
        frame_idx = 0
        total_samples = (total_frames + step_frames - 1) // step_frames
        sample_count = 0

        while frame_idx < total_frames:
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            ret, frame = cap.read()
            if not ret:
                break

            current_time = frame_idx / fps
            detections = self.detector.detect(frame)

            # Filter awal: ROI & lebar minimum
            valid_items = []
            for item in detections:
                box = item["bbox_pct"]
                text = item["text"].strip()

                if not is_within_roi(box, self.roi):
                    continue

                if box["width"] < self.min_width_pct:
                    continue

                if self.is_manual_ignored(text):
                    continue

                if self.is_isolated_packaging_label(text, box["width"]):
                    continue

                cleaned_text = self.clean_text(text)
                if len(cleaned_text) < self.min_chars:
                    continue

                item["text"] = cleaned_text
                valid_items.append(item)

            # Evaluasi kecerdasan subtitle: pilih blok subtitle sah & abaikan teks kemasan
            best_subtitle_block = self.cluster_and_select_best_subtitle(valid_items)
            if best_subtitle_block:
                words = best_subtitle_block["text"].split()
                if len(words) >= self.min_words and len(best_subtitle_block["text"]) >= self.min_chars:
                    raw_detections.append({
                        "timestamp": round(current_time, 2),
                        "text": best_subtitle_block["text"],
                        "confidence": best_subtitle_block["confidence"],
                        "bbox_pct": {
                            "ymin": best_subtitle_block["ymin"],
                            "ymax": best_subtitle_block["ymax"],
                            "width": best_subtitle_block["width"],
                            "center_x": best_subtitle_block["center_x"]
                        }
                    })

            sample_count += 1
            if verbose and sample_count % 5 == 0:
                pct = (sample_count / total_samples) * 100.0
                print(f"   ⏳ Menganalisis frame: {pct:5.1f}% ({current_time:.1f}s / {duration:.1f}s)", end="\r", flush=True)

            frame_idx += step_frames

        cap.release()
        if verbose:
            print(f"   ✅ Selesai mengekstrak {sample_count} sampel frame.")

        # Agregasi & deduplikasi timeline subtitle
        subtitles = self._aggregate_subtitles(raw_detections, step_seconds=1.0 / self.sample_fps)

        result = {
            "metadata": {
                "file_name": os.path.basename(video_path),
                "file_path": os.path.abspath(video_path),
                "resolution": f"{width}x{height}",
                "fps": round(fps, 2),
                "duration_seconds": round(duration, 2),
                "processed_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "roi_filter": self.roi,
                "auto_packaging_filter": self.auto_filter_packaging,
                "min_words": self.min_words,
                "ignore_keywords": self.ignore_keywords
            },
            "total_subtitles_found": len(subtitles),
            "subtitles": subtitles
        }

        return result

    def _aggregate_subtitles(self, raw_detections: List[Dict[str, Any]], step_seconds: float) -> List[Dict[str, Any]]:
        """Menggabungkan frame berurutan menjadi segmen subtitle utuh."""
        if not raw_detections:
            return []

        events = []
        current_event = None

        for det in raw_detections:
            t = det["timestamp"]
            text = det["text"]
            conf = det["confidence"]

            if current_event is None:
                current_event = {
                    "start_time": t,
                    "end_time": t + step_seconds,
                    "text": text,
                    "confidences": [conf]
                }
            else:
                sim = string_similarity(current_event["text"], text)
                time_diff = t - current_event["end_time"]
                is_prog = is_progressive_or_continuation(current_event["text"], text)

                # Jika teks sama/mirip atau kelanjutan animasi typewriter
                if (sim >= 0.55 or is_prog) and time_diff <= (step_seconds * 2.2):
                    current_event["end_time"] = t + step_seconds
                    current_event["confidences"].append(conf)
                    if len(text) > len(current_event["text"]):
                        current_event["text"] = text
                else:
                    events.append(current_event)
                    current_event = {
                        "start_time": t,
                        "end_time": t + step_seconds,
                        "text": text,
                        "confidences": [conf]
                    }

        if current_event:
            events.append(current_event)

        # Peleburan segmen bertetangga jika merupakan kelanjutan frasa
        merged_events = []
        for ev in events:
            if not merged_events:
                merged_events.append(ev)
                continue

            prev = merged_events[-1]
            time_gap = ev["start_time"] - prev["end_time"]

            if time_gap <= (step_seconds * 1.5) and is_progressive_or_continuation(prev["text"], ev["text"]):
                prev["end_time"] = ev["end_time"]
                prev["confidences"].extend(ev["confidences"])
                if len(ev["text"]) > len(prev["text"]):
                    prev["text"] = ev["text"]
            else:
                merged_events.append(ev)

        # Format final ke output subtitle
        formatted = []
        sub_id = 1
        for ev in merged_events:
            dur = ev["end_time"] - ev["start_time"]
            if dur < self.min_duration:
                continue

            avg_conf = sum(ev["confidences"]) / len(ev["confidences"])
            formatted.append({
                "id": sub_id,
                "start_seconds": round(ev["start_time"], 2),
                "end_seconds": round(ev["end_time"], 2),
                "duration_seconds": round(dur, 2),
                "start_time_srt": seconds_to_srt_time(ev["start_time"]),
                "end_time_srt": seconds_to_srt_time(ev["end_time"]),
                "text": ev["text"],
                "confidence": round(avg_conf, 3)
            })
            sub_id += 1

        return formatted

    def generate_preview(self, video_path: str, output_image_path: str, timestamp_sec: float = 3.0) -> bool:
        """Membuat gambar preview beranotasi visual (hijau: subtitle, merah: kemasan/diabaikan)."""
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        frame_idx = int(timestamp_sec * fps)
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ret, frame = cap.read()
        cap.release()

        if not ret:
            return False

        h, w = frame.shape[:2]
        overlay = frame.copy()

        rx1 = int((self.roi["xmin"] / 100.0) * w)
        rx2 = int((self.roi["xmax"] / 100.0) * w)
        ry1 = int((self.roi["ymin"] / 100.0) * h)
        ry2 = int((self.roi["ymax"] / 100.0) * h)

        cv2.rectangle(overlay, (rx1, ry1), (rx2, ry2), (0, 255, 0), -1)
        cv2.addWeighted(overlay, 0.12, frame, 0.88, 0, frame)
        cv2.rectangle(frame, (rx1, ry1), (rx2, ry2), (0, 255, 0), 2)
        cv2.putText(frame, f"ROI Active Area (Y: {self.roi['ymin']}% - {self.roi['ymax']}%)", 
                    (rx1 + 10, max(25, ry1 + 25)), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 0), 2)

        detections = self.detector.detect(frame)
        for det in detections:
            box = det["bbox_pct"]
            text = det["text"]
            bx1 = int((box["xmin"] / 100.0) * w)
            bx2 = int((box["xmax"] / 100.0) * w)
            by1 = int((box["ymin"] / 100.0) * h)
            by2 = int((box["ymax"] / 100.0) * h)

            blk = {
                "text": text,
                "center_x": box["center_x"],
                "width": box["width"]
            }
            score = self.calculate_subtitle_score(blk)
            is_valid = (
                is_within_roi(box, self.roi) and 
                not self.is_manual_ignored(text) and 
                box["width"] >= self.min_width_pct and
                score >= 30.0
            )

            color = (0, 255, 0) if is_valid else (0, 0, 255)
            cv2.rectangle(frame, (bx1, by1), (bx2, by2), color, 2)
            label = text if len(text) <= 28 else text[:25] + "..."
            cv2.putText(frame, label, (bx1, max(20, by1 - 6)), cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 1)

        os.makedirs(os.path.dirname(output_image_path) or ".", exist_ok=True)
        cv2.imwrite(output_image_path, frame)
        return True


def export_json(data: Dict[str, Any], filepath: str):
    """Menyimpan data subtitle ke format JSON."""
    os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def export_srt(data: Dict[str, Any], filepath: str):
    """Menyimpan data subtitle ke format SRT."""
    os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        for sub in data.get("subtitles", []):
            f.write(f"{sub['id']}\n")
            f.write(f"{sub['start_time_srt']} --> {sub['end_time_srt']}\n")
            f.write(f"{sub['text']}\n\n")


def export_txt(data: Dict[str, Any], filepath: str, typo_report: Optional[Dict[str, Any]] = None, audience_report: Optional[Dict[str, Any]] = None):
    """Menyimpan transkrip subtitle ke format teks biasa (.txt) beserta hasil analisis typo dan intelijen audiens/hook jika ada."""
    os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"========================================================\n")
        f.write(f"TRANSKRIP SUBTITLE VIDEO: {data['metadata']['file_name']}\n")
        f.write(f"Resolusi : {data['metadata']['resolution']} | Durasi: {data['metadata']['duration_seconds']}s | FPS: {data['metadata']['fps']}\n")
        f.write(f"Diproses : {data['metadata']['processed_at']}\n")
        f.write(f"========================================================\n\n")
        
        f.write("--- DAFTAR SUBTITLE ---\n")
        for sub in data.get("subtitles", []):
            start = sub['start_time_srt'][:8]
            end = sub['end_time_srt'][:8]
            f.write(f"[{start} - {end}] {sub['text']}\n")

        # Jika ada laporan typo, lampirkan langsung ke dalam file TXT
        if typo_report:
            f.write("\n--------------------------------------------------------\n")
            f.write("🔍 HASIL PEMERIKSAAN KESALAHAN PENULISAN (TYPO):\n")
            f.write(f" • Total Kata Dianalisis : {typo_report['total_words_analyzed']}\n")
            f.write(f" • Total Typo Ditemukan  : {typo_report['total_typos_found']}\n")
            if typo_report['total_typos_found'] == 0:
                f.write("✅ Semua penulisan subtitle sudah benar (0 typo).\n")
            else:
                f.write("\n⚠️  Daftar Typo & Saran Perbaikan:\n")
                for item in typo_report['typo_details']:
                    f.write(f" • Subtitle : \"{item['text']}\"\n")
                    for tp in item['typos']:
                        sugg_str = ", ".join([f"'{s}'" for s in tp['suggestions']]) if tp['suggestions'] else "(Tidak ada saran)"
                        f.write(f"   ❌ Typo   : '{tp['word']}'  👉  Saran: {sugg_str}\n")
            f.write("========================================================\n")

        # Jika ada laporan target audiens dan hook, lampirkan langsung
        if audience_report:
            aud = audience_report.get("target_audience", {})
            hooks = audience_report.get("suggested_hooks", [])
            init_audit = audience_report.get("initial_hook_audit", {})
            f.write("\n--------------------------------------------------------\n")
            f.write("🎯 TARGET AUDIENCE & 3-SECOND HOOK INTELLIGENCE:\n")
            f.write(f" • Kategori Konten   : {audience_report.get('category', '-')}\n")
            if init_audit:
                f.write(f" • Skor Retensi Awal : {init_audit.get('retention_score', 0)} / 100 [{init_audit.get('rating', '-')}]\n")
            f.write(f" • Demografi Sasaran : {aud.get('demographics', '-')}\n")
            f.write(f" • Tone of Voice     : {aud.get('tone_of_voice', '-')}\n")
            f.write(f" • Content Angle     : {aud.get('content_angle', '-')}\n")
            f.write(f" • Motivasi Audiens   : {aud.get('desires', '-')}\n")
            f.write("\n💡 Rekomendasi 5 Hook Strategis (3 Detik Pertama):\n")
            for idx, h in enumerate(hooks, 1):
                f.write(f" [{idx}] {h.get('formula', 'Hook')}:\n")
                f.write(f"     👉 \"{h.get('hook_text', '')}\"\n")
            f.write("========================================================\n")


def main():
    parser = argparse.ArgumentParser(
        description="Aplikasi CLI untuk membaca dan mengekstrak subtitle video ke TXT (dengan deteksi typo & auto-filter kemasan produk)."
    )
    parser.add_argument("videos", nargs="+", help="File video yang akan diproses (contoh: benar.mp4 salah.mp4)")
    parser.add_argument("-o", "--output-dir", default="./output", help="Folder direktori output (default: ./output)")
    parser.add_argument("--roi", default="10,90", 
                        help="Area vertikal subtitle: 'top', 'bottom', 'middle', 'full', atau 'ymin,ymax' (default: '10,90')")
    parser.add_argument("--roi-ymin", type=float, help="Batas atas ROI dalam persen 0-100")
    parser.add_argument("--roi-ymax", type=float, help="Batas bawah ROI dalam persen 0-100")
    parser.add_argument("--roi-xmin", type=float, help="Batas kiri ROI dalam persen 0-100")
    parser.add_argument("--roi-xmax", type=float, help="Batas kanan ROI dalam persen 0-100")
    
    # Fitur Otomatis
    parser.add_argument("--no-auto-filter", action="store_true", help="Nonaktifkan filter otomatis teks kemasan produk")
    
    # Filter Tambahan
    parser.add_argument("--min-width", type=float, default=12.0, help="Lebar minimum teks dalam persen lebar frame video (default: 12.0)")
    parser.add_argument("--min-words", type=int, default=1, help="Jumlah kata minimum per baris (default: 1)")
    parser.add_argument("--ignore", type=str, default="", help="Kata kunci tambahan yang diabaikan manual dipisahkan koma (opsional)")
    parser.add_argument("--fps-sample", type=float, default=2.0, help="Frekuensi sampling frame per detik (default: 2.0 fps)")
    parser.add_argument("--min-conf", type=float, default=0.5, help="Keyakinan minimum OCR 0.0 - 1.0 (default: 0.5)")
    parser.add_argument("--min-duration", type=float, default=0.8, help="Durasi minimum subtitle dalam detik (default: 0.8s)")
    parser.add_argument("--export", choices=["txt", "json", "srt", "all"], default="txt", help="Format ekspor (txt, json, srt, all). Default: txt")
    parser.add_argument("--preview", action="store_true", help="Buat gambar visualisasi ROI dan bounding box teks")
    parser.add_argument("--preview-time", type=float, default=3.0, help="Timestamp detik untuk gambar preview (default: 3.0)")
    # Fitur Pemeriksaan Typo
    parser.add_argument("--check-typo", "--check-typos", dest="check_typo", action="store_true", help="Deteksi kesalahan penulisan (typo) secara otomatis pada teks subtitle")
    parser.add_argument("--typo-whitelist", type=str, default="", help="Daftar kata tambahan yang dianggap benar (dipisahkan koma)")
    # Fitur Intelijen Konten & Hook (Integrasi audience_hook_advisor)
    parser.add_argument("--analyze-audience", action="store_true", help="Analisis profil target audiens dan formula rekomendasi hook 3 detik secara terpadu")
    parser.add_argument("--html-report", action="store_true", help="Hasilkan dashboard visual HTML interaktif modern")
    # Fitur Batch & Pembatasan
    parser.add_argument("--limit", type=int, default=0, help="Batasi jumlah video yang diproses dalam mode batch (0 = proses semua)")
    parser.add_argument("--engine", choices=["rapidocr", "vision", "tesseract", "auto"], default="rapidocr", help="Mesin OCR yang digunakan (default: rapidocr)")

    args = parser.parse_args()

    # Resolusi berkas video: dukung nama file tunggal, daftar file, wildcard (*.mp4), atau nama folder direktori
    resolved_video_paths: List[Path] = []
    for video_arg in args.videos:
        # 1. Cek jika argumen mengandung pola wildcard
        if any(char in video_arg for char in ["*", "?", "["]):
            matched = glob.glob(video_arg)
            if matched:
                for m in sorted(matched):
                    mp = Path(m)
                    if mp.is_file() and mp not in resolved_video_paths:
                        resolved_video_paths.append(mp)
            else:
                print(f"⚠️  Tidak ada file video yang cocok dengan pola: {video_arg}")
            continue

        p = Path(video_arg)
        # 2. Cek jika argumen adalah folder/direktori (misal: 'Video' atau 'Video/')
        if p.is_dir():
            folder_videos = []
            for ext in ["*.mp4", "*.mkv", "*.mov", "*.avi", "*.MP4", "*.MOV"]:
                folder_videos.extend(p.glob(ext))
            folder_videos = sorted(list(set(folder_videos)))
            if folder_videos:
                for fv in folder_videos:
                    if fv not in resolved_video_paths:
                        resolved_video_paths.append(fv)
            else:
                print(f"⚠️  Tidak ditemukan berkas video (.mp4/.mov) di dalam folder: {p}")
            continue

        # 3. File spesifik
        if p.exists() and p.is_file():
            if p not in resolved_video_paths:
                resolved_video_paths.append(p)
        else:
            print(f"❌ File tidak ditemukan: {p}")

    if not resolved_video_paths:
        print("❌ Tidak ada berkas video yang valid untuk diproses.")
        return

    # Batasi jumlah video jika parameter --limit diaktifkan
    if args.limit > 0 and len(resolved_video_paths) > args.limit:
        resolved_video_paths = resolved_video_paths[:args.limit]

    roi_config = parse_roi(
        args.roi,
        ymin=args.roi_ymin,
        ymax=args.roi_ymax,
        xmin=args.roi_xmin,
        xmax=args.roi_xmax
    )

    ignore_list = [k.strip() for k in args.ignore.split(",") if k.strip()]

    reader = VideoSubtitleReader(
        roi=roi_config,
        auto_filter_packaging=not args.no_auto_filter,
        min_width_pct=args.min_width,
        min_words=args.min_words,
        min_confidence=args.min_conf,
        sample_fps=args.fps_sample,
        min_duration=args.min_duration,
        ignore_keywords=ignore_list,
        engine=args.engine
    )

    # Inisialisasi Typo Checker jika flag aktif
    typo_checker = None
    if args.check_typo:
        try:
            from typo_checker import SubtitleTypoChecker, format_typo_terminal_report
            custom_wl = [w.strip() for w in args.typo_whitelist.split(",") if w.strip()]
            typo_checker = SubtitleTypoChecker(custom_whitelist=custom_wl)
        except ImportError:
            print("⚠️  Modul typo_checker tidak ditemukan. Fitur deteksi typo dilewati.")

    print("========================================================")
    print("🚀 Video Subtitle Reader CLI (Batch Processing Mode)")
    print(f"⚙️  Mesin OCR     : {reader.detector.engine.upper()}")
    print(f"📦 Jumlah Video : {len(resolved_video_paths)}")
    print(f"📂 Direktori Out : {os.path.abspath(args.output_dir)}")
    if args.check_typo:
        print("🔍 Cek Typo     : AKTIF (Deteksi ejaan & saran perbaikan)")
    print("========================================================")

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    summary_list = []

    for idx, video_path in enumerate(resolved_video_paths, 1):
        print(f"\n[{idx}/{len(resolved_video_paths)}] Memproses: {video_path.name}...")

        try:
            start_t = time.time()
            data = reader.process_video(str(video_path), verbose=True)
            elapsed = time.time() - start_t

            stem = video_path.stem
            
            # Pemeriksaan Typo jika diaktifkan
            typo_count = 0
            if typo_checker:
                typo_report = typo_checker.check_subtitles(data["subtitles"])
                data["typo_analysis"] = {
                    "total_words_analyzed": typo_report["total_words_analyzed"],
                    "total_typos_found": typo_report["total_typos_found"],
                    "has_typo": typo_report["has_typo"],
                    "details": typo_report["typo_details"]
                }
                typo_count = typo_report["total_typos_found"]

                # Simpan file laporan typo JSON hanya jika format json/all dipilih
                if args.export in ["json", "all"]:
                    typo_json_path = output_dir / f"{stem}_typo_report.json"
                    with open(typo_json_path, "w", encoding="utf-8") as f:
                        json.dump(typo_report, f, indent=2, ensure_ascii=False)
                
                # Tampilkan laporan typo di layar terminal
                print("\n" + format_typo_terminal_report(typo_report, video_path.name))

            # Analisis Target Audiens & Hook jika diaktifkan
            audience_report = None
            if args.analyze_audience or args.html_report:
                try:
                    # Tambahkan path audience_hook_advisor ke sys.path
                    adv_path = Path(__file__).resolve().parent.parent / "audience_hook_advisor"
                    root_path = Path(__file__).resolve().parent.parent
                    if str(adv_path) not in sys.path: sys.path.insert(0, str(adv_path))
                    if str(root_path) not in sys.path: sys.path.insert(0, str(root_path))
                    
                    from advisor import ContentHookAdvisor
                    adv = ContentHookAdvisor()
                    full_text = " ".join([s['text'] for s in data.get("subtitles", [])])
                    audience_report = adv.analyze(full_text)
                    audience_report["subtitles"] = [s['text'] for s in data.get("subtitles", [])]
                    audience_report["metadata"]["file_name"] = video_path.name
                    audience_report["metadata"]["duration_seconds"] = data.get("metadata", {}).get("duration_seconds", 0)
                    if typo_checker:
                        audience_report["typo_analysis"] = data.get("typo_analysis", {})
                    
                    data["audience_intelligence"] = audience_report
                    print("\n🎯 ANALISIS AUDIENS & HOOK TERPADU:")
                    print(f" • Kategori Konten   : {audience_report.get('category')}")
                    init_audit = audience_report.get("initial_hook_audit", {})
                    if init_audit:
                        print(f" • Skor Retensi Awal : {init_audit.get('retention_score')}/100 [{init_audit.get('rating')}]")
                    print(f" • Rekomendasi Hook  : {len(audience_report.get('suggested_hooks', []))} formula copywriting siap pakai")
                except Exception as adv_err:
                    print(f"⚠️ Gagal menjalankan analisis audiens: {adv_err}")

            # Simpan sesuai format yang dipilih (Default: TXT saja)
            if args.export in ["json", "all"]:
                json_path = output_dir / f"{stem}_subtitles.json"
                export_json(data, str(json_path))
                print(f"   💾 JSON : {json_path.name}")

            if args.export in ["srt", "all"]:
                srt_path = output_dir / f"{stem}_subtitles.srt"
                export_srt(data, str(srt_path))
                print(f"   💾 SRT  : {srt_path.name}")

            if args.export in ["txt", "all"]:
                txt_path = output_dir / f"{stem}_subtitles.txt"
                export_txt(data, str(txt_path), typo_report=(typo_report if typo_checker else None), audience_report=audience_report)
                print(f"   💾 TXT  : {txt_path.name}")

            # Dashboard Visual HTML
            if args.html_report or (args.export == "all" and audience_report):
                try:
                    from html_reporter import HTMLDashboardReporter
                    html_path = output_dir / f"{stem}_dashboard.html"
                    HTMLDashboardReporter.generate_html_report(audience_report, str(html_path))
                    print(f"   🌐 HTML : {html_path.name} (Dashboard Interaktif)")
                except Exception as html_err:
                    print(f"⚠️ Gagal membuat laporan HTML: {html_err}")

            # Preview gambar visualisasi ROI
            if args.preview:
                preview_path = output_dir / f"{stem}_roi_preview.jpg"
                if reader.generate_preview(str(video_path), str(preview_path), timestamp_sec=args.preview_time):
                    print(f"   🖼️  Preview: {preview_path.name}")

            summary_item = {
                "video": video_path.name,
                "subtitles": len(data["subtitles"]),
                "time": f"{elapsed:.1f}s"
            }
            if typo_checker:
                summary_item["typos"] = f"{typo_count} typo"
            summary_list.append(summary_item)

        except Exception as e:
            print(f"❌ Terjadi kesalahan saat memproses {video_path.name}: {e}")

    print("\n========================================================")
    print("✨ RINGKASAN HASIL PROSES (BATCH REPORT)")
    print("========================================================")
    total_videos = len(summary_list)
    total_subs = sum(s["subtitles"] for s in summary_list)
    total_typos = sum(int(s["typos"].split()[0]) for s in summary_list if "typos" in s) if typo_checker else 0

    for s in summary_list:
        typo_info = f" | {s['typos']}" if "typos" in s else ""
        print(f" • {s['video']:<25} : {s['subtitles']:>2} subtitle terdeteksi{typo_info} (Waktu: {s['time']})")
    
    print("--------------------------------------------------------")
    print(f" 📊 STATISTIK TOTAL : {total_videos} video | {total_subs} subtitle | {total_typos} typo")
    print(f" 📂 Output Folder    : {os.path.abspath(args.output_dir)}\n")


if __name__ == "__main__":
    main()
