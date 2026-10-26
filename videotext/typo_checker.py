#!/usr/bin/env python3
"""
Subtitle Typo Checker
Modul dan CLI untuk mendeteksi kesalahan penulisan (typo/ejaan) pada teks subtitle video.
Mendukung:
 - Bahasa Indonesia (KBBI kata dasar & imbuhan via PySastrawi + kosakata percakapan)
 - Bahasa Inggris (pyspellchecker untuk istilah umum seperti POV, glossy, blend, dll)
 - Whitelist akronim, istilah kecantikan/produk, dan istilah teknis
 - 4 Pilar Arsitektur Deteksi Typo Modern:
    1. Pilar Casing & Accidental Shift-Key (BIsa, DAn, seLalu)
    2. Pilar Optical Homoglyph Ambiguity (I kapital vs l kecil vs 1 angka)
    3. Pilar Alphanumeric & Leetspeak (8isa, k4mu, 5emua) dengan filter satuan resmi
    4. Pilar Damerau-Levenshtein Transposisi & QWERTY Keyboard Proximity
 - Ekspor laporan typo ke JSON dan TXT
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
import re
import argparse
import difflib
import glob
from pathlib import Path
from typing import List, Dict, Any, Optional, Set, Tuple

# Coba impor library spellchecker & Sastrawi
HAS_SPELLCHECKER = False
try:
    from spellchecker import SpellChecker
    HAS_SPELLCHECKER = True
except ImportError:
    HAS_SPELLCHECKER = False

HAS_SASTRAWI = False
try:
    from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
    HAS_SASTRAWI = True
except ImportError:
    HAS_SASTRAWI = False


# ==============================================================================
# KONSTANTA DAN POLA REGEX
# ==============================================================================

# Regex untuk satuan ukuran resmi dan angka teknis yang sah
VALID_UNIT_PATTERN = re.compile(
    r"^(\d+(?:ml|mg|gr|gram|kg|l|cm|mm|%|k|x|th|st|nd|rd|h|fps|rb|jt)|spf\d+|no\d+|isi\d+)$",
    re.IGNORECASE
)

# Daftar akronim, istilah kecantikan, produk, bahasa gaul, percakapan sehari-hari, dan istilah bahasa Inggris
COMMON_WHITELIST = {
    # 1. Akronim, Singkatan & Satuan Teknis
    "pov", "spf", "uv", "uva", "uvb", "pa", "bpom", "halal", "exp", "mfg", "ml", "mg", "gr", "gram", "kg",
    "bb", "cc", "aha", "bha", "pha", "vit", "co", "cod", "vt", "fyp", "ootd", "fomo", "faq", "id", "no",

    # 2. Bahasa Gaul Media Sosial & Gen Z (TikTok, IG Reels, X)
    "gue", "gw", "gua", "gwa", "lo", "lu", "elu", "elo", "doi", "baper", "mager", "kepo", "pansos", "fomo",
    "ootd", "spill", "racun", "racunin", "racunnya", "checkout", "naksir", "cus", "cuss", "capcus",
    "gas", "gaskeun", "otw", "mantul", "mantep", "kece", "gemoy", "gemes", "ucul", "anjay", "anjir",
    "lebay", "alay", "gercep", "bestie", "beb", "bebeb", "bund", "bunda", "bro", "brok", "sis", "sist",
    "cuy", "guys", "gaes", "gais", "gengs", "santuy", "santai", "bet", "bat", "bats", "beut", "bgt",
    "bucin", "salty", "flexing", "relate", "relatable", "valid", "vibe", "vibes", "mood", "slay", "slayyy",
    "kecebadai", "cakep", "cakepbgt", "worthit", "worthy", "unboxing", "haul", "konten", "ngonten",
    "ngedit", "ngeshare", "posting", "ngepost", "repost", "story", "feeds", "reels", "live", "join",
    "tap", "taptap", "keranjang", "etalase", "flashsale", "ongkir", "gratisongkir", "trusted",
    "rekomen", "rekomenin", "recommended", "rekomenbgt", "pol", "puol", "pool", "poll", "parah",
    "parahbgt", "goks", "gokil", "gacor", "salfok", "overthinking", "healing", "insecure", "anxiety",
    "metime", "nodebat", "mimin", "admin", "olshop", "reseller", "dropship", "ready", "restock",
    "po", "preorder", "soldout", "habis", "ludes", "cuan", "affiliate", "shopee", "tiktok", "tokopedia",

    # 3. Bahasa Percakapan Sehari-hari & Informal Indonesia
    "bikin", "bikinan", "nggak", "ngga", "ga", "gak", "cuma", "cuman", "banget", "yuk", "deh", "dong",
    "nih", "tuh", "kok", "kan", "lah", "pun", "aja", "ajaa", "ajalah", "udah", "udh", "belum", "blm",
    "gimana", "gmn", "kayak", "kyk", "kek", "kalo", "klo", "kalau", "emang", "emangnya", "mang",
    "bener", "beneran", "gapapa", "gpp", "gamau", "gatau", "gabisa", "gbs", "gabut", "liat", "ngeliat",
    "ngeliatin", "keliatan", "keliatannya", "ketauan", "denger", "dengerin", "ngomong", "ngomongin",
    "ngasih", "kasih", "ngambil", "ambil", "bawa", "bawanya", "pake", "pakenya", "kepake", "cobain",
    "nyobain", "nyoba", "rasain", "ngerasain", "rasanya", "jalan", "nemu", "nemuin", "nyari", "cari",
    "dapet", "dapetin", "dapetnya", "kena", "mikir", "mikirnya", "kepikiran", "tau", "taunya",
    "ngaruh", "ngaruhnya", "mempan", "mempannya", "nampol", "nampolbgt", "cocok", "cocoknya",
    "cocokbgt", "pas", "pasnya", "pasbgt", "nyaman", "nyamannya", "tahan", "tahanlama", "awet",
    "awetnya", "awetbgt", "luntur", "lunturnya", "gampang", "gampangnya", "gampangbgt", "susah",
    "susahnya", "ribet", "ribetnya", "simpel", "praktis", "sehari-hari", "skincarean", "makeupan",
    "kinclong", "kusem", "cerahan", "putihan", "pilihan", "tekstur", "ringan", "diblend", "melembapkan",
    "menyamarkan", "mengandung", "berkilau", "lembap", "halus", "warna", "tampilan", "garis", "kulit",
    "wajah", "bibir", "mata", "pipi", "cantik", "rekomendasi", "favorit", "produk",

    # 4. Istilah Kecantikan, Skincare, Rambut & Wewangian (Bilingual English-Indo)
    "lip", "oil", "tint", "liptint", "lipmatte", "lipcream", "lipgloss", "lipbalm", "lipstick",
    "glossy", "gloss", "matte", "stain", "blush", "blushon", "eyeliner", "mascara", "serum",
    "moisturizer", "toner", "sunscreen", "sunblock", "sunstick", "cushion", "foundation", "complexion",
    "concealer", "powder", "loosepowder", "compactpowder", "setting", "settingspray", "primer",
    "shade", "swatch", "swatches", "blend", "contour", "highlighter", "highlight", "skincare", "makeup",
    "fresh", "dewy", "glow", "glowing", "effect", "finish", "clean", "look", "base", "wear",
    "extract", "vitamin", "gardenia", "peach", "berry", "cherry", "nude", "natural", "light",
    "shampoo", "hairloss", "hairfall", "hair", "fall", "care", "haircare", "ginseng", "panax",
    "panthenol", "sophora", "soybean", "protein", "root", "rootextract", "conditioner", "hairmask",
    "hairoil", "hairtonic", "facial", "foam", "wash", "facialwash", "cleanser", "micellar",
    "bright", "brightening", "skin", "skinbarrier", "barrier", "langsat", "effortless",
    "scent", "scents", "fragrance", "fragrances", "mist", "bodymist", "spray", "body", "splash",
    "floral", "fruity", "woody", "musk", "amber", "sweet", "vanilla", "citrus", "aroma", "notes",
    "elegance", "classy", "luxury", "affordable", "budget", "dupes", "dupe", "staple", "daily",
    "routine", "step", "prep", "prime", "lock", "bake", "baking", "touchup", "retouch",
    "longlasting", "longwear", "transferproof", "smudgeproof", "waterproof", "sweatproof",
    "lightweight", "breathable", "hydrating", "hydration", "soothing", "calming", "antiaging",
    "acneprone", "ceramide", "niacinamide", "hyaluronic", "retinol", "peptide", "salicylic",
    "centella", "cica", "mugwort", "aloe", "collagen", "glutathione", "arbutin", "peeling", "scrub",
    "exfoliate", "exfoliating", "bodywash", "bodylotion", "bodyscrub", "bodybutter", "deodorant",

    # 5. Kata Tugas, Preposisi, Konjungsi & Kata Hubung Baku/Cakapan
    "ke", "di", "dari", "pada", "untuk", "bagi", "sama", "saat", "waktu", "biar", "agar", "supaya",
    "jika", "kalau", "tapi", "tetapi", "dan", "serta", "atau", "maka", "lalu", "terus", "juga",
    "lagi", "masih", "pernah", "sempat", "bakal", "mau", "akan", "bisa", "dapat", "boleh", "harus",
    "mesti", "wajib", "tidak", "tak", "bukan", "jangan", "tanpa", "tentang", "oleh", "seperti",
    "ya", "yah", "hai", "halo", "oh", "eh", "ah", "ha", "se", "si", "itu", "ini",

    # 6. Kata Kerja & Bahasa Inggris Populer untuk Konten
    "find", "your", "make", "it", "but", "and", "for", "with", "all", "day", "night",
    "setelah", "sebelum", "karena", "sehingga", "terasa", "kerontokan", "keramas",
    "rambut", "rontok", "patah", "mengkilaukan", "membersihkan", "mengurangi", "membantu",
    "ketarik", "kusam", "segampang"
}

# ==============================================================================
# MATRIKS KERANCUAN OPTIK & TYPO (CONFUSION MATRICES)
# ==============================================================================

# PILAR 2: Pasangan Homoglyph Optik (Bentuk visual garis tegak/lingkaran serupa)
HOMOGLYPH_PAIRS = [
    ('I', 'l'), ('l', 'I'),       # 'I' kapital <-> 'l' kecil (misal: 'kembaIi' -> 'kembali', 'Iebih' -> 'lebih')
    ('I', 'i'), ('i', 'I'),       # 'I' kapital <-> 'i' kecil
    ('l', 'i'), ('i', 'l'),       # 'l' kecil <-> 'i' kecil (misal: 'blsa' -> 'bisa', 'kllit' -> 'kulit')
    ('O', 'o'), ('o', 'O'),       # 'O' kapital <-> 'o' kecil
    ('0', 'o'), ('o', '0'),       # Angka 0 <-> huruf o
    ('1', 'l'), ('l', '1'),       # Angka 1 <-> l kecil
    ('1', 'i'), ('i', '1'),       # Angka 1 <-> i kecil
    ('|', 'l'), ('|', 'I'),       # Garis pipa <-> l atau I
]

# PILAR 3: Pasangan Leetspeak / Angka Campur Huruf
LEET_CONFUSION_MAP = [
    ('8', 'b'), ('8', 'B'),
    ('0', 'o'), ('0', 'O'),
    ('1', 'i'), ('1', 'l'), ('1', 'I'),
    ('3', 'e'), ('3', 'E'),
    ('4', 'a'), ('4', 'A'),
    ('5', 's'), ('5', 'S'),
    ('7', 't'), ('7', 'T'),
    ('2', 'z'), ('2', 'Z'),
]

# PILAR 4 (Bagian A): Matriks Ligature Font Miring (Italic Ligatures) & Kerning Rapat OCR
OCR_CHARACTER_CONFUSION_MATRIX = [
    ('b', 'la'), ('la', 'b'),       # 'l' miring menyentuh 'a' terbaca 'b' ('setebh' -> 'setelah', 'sekobh' -> 'sekolah')
    ('d', 'cl'), ('cl', 'd'),       # 'c' menyentuh 'l' terbaca 'd' ('c1ear' / 'dear' -> 'clear')
    ('m', 'rn'), ('rn', 'm'),       # 'r' rapat dengan 'n' terbaca 'm' ('karnu' -> 'kamu', 'temyata' -> 'ternyata')
    ('m', 'nn'), ('nn', 'm'),       # 'n' ganda terbaca 'm' ('tennan' -> 'teman')
    ('w', 'vv'), ('vv', 'w'),       # dua 'v' terbaca 'w' ('vvarna' -> 'warna')
    ('w', 'uu'), ('uu', 'w'),       # dua 'u' terbaca 'w'
    ('h', 'li'), ('li', 'h'),       # 'l' dan 'i' terbaca 'h' ('lialus' -> 'halus')
    ('h', 'tl'), ('tl', 'h'),
    ('k', 'lc'), ('lc', 'k'),       # 'l' dan 'c' terbaca 'k'
    ('u', 'ii'), ('ii', 'u'),       # dua 'i' terbaca 'u' ('kiilit' -> 'kulit')
    ('g', 'cj'), ('cj', 'g'),
    ('d', 'ol'), ('ol', 'd'),
    ('b', 'lo'), ('lo', 'b'),
    ('q', 'g'), ('g', 'q'),
    ('c', 'e'), ('e', 'c'),
]

# PILAR 4 (Bagian B): QWERTY Keyboard Proximity Map (Tombol Bertetangga Fisik Keyboard)
QWERTY_ADJACENT = {
    'q': 'wa12', 'w': 'qesa23', 'e': 'wrsd34', 'r': 'etfd45', 't': 'rygf56',
    'y': 'tuhg67', 'u': 'yijh78', 'i': 'uojk89', 'o': 'ipkl90', 'p': 'ol0',
    'a': 'qwsz', 's': 'qweadzx', 'd': 'ersfcx', 'f': 'rtdgvc', 'g': 'tyfhvb',
    'h': 'yugjbn', 'j': 'uikhmn', 'k': 'iojlm', 'l': 'opk',
    'z': 'asx', 'x': 'zsdc', 'c': 'xdfv', 'v': 'cfgb', 'b': 'vghn8', 'n': 'bhjm', 'm': 'njk'
}


def qwerty_substitution_cost(c1: str, c2: str) -> float:
    """Menghitung bobot jarak substitusi tombol keyboard QWERTY."""
    if c1 == c2:
        return 0.0
    c1_low, c2_low = c1.lower(), c2.lower()
    if c2_low in QWERTY_ADJACENT.get(c1_low, ''):
        return 0.6  # Tombol bersebelahan mendapat penalti lebih rendah
    return 1.0


def damerau_levenshtein_distance(s1: str, s2: str) -> float:
    """
    Menghitung jarak Damerau-Levenshtein yang mendukung:
    - Insertion (penyisipan)
    - Deletion (penghapusan)
    - Substitution dengan bobot QWERTY
    - Transposition (tukar posisi huruf bertetangga, misal 'bsia' -> 'bisa')
    """
    len1, len2 = len(s1), len(s2)
    d = {}
    for i in range(-1, len1 + 1):
        d[(i, -1)] = i + 1
    for j in range(-1, len2 + 1):
        d[(-1, j)] = j + 1

    for i in range(len1):
        for j in range(len2):
            cost = qwerty_substitution_cost(s1[i], s2[j])
            d[(i, j)] = min(
                d[(i - 1, j)] + 1.0,         # deletion
                d[(i, j - 1)] + 1.0,         # insertion
                d[(i - 1, j - 1)] + cost     # substitution
            )
            # Transposition check
            if i > 0 and j > 0 and s1[i] == s2[j - 1] and s1[i - 1] == s2[j]:
                d[(i, j)] = min(d[(i, j)], d[(i - 2, j - 2)] + 0.8)

    return d[(len1 - 1, len2 - 1)]


class SubtitleTypoChecker:
    """Kelas pemeriksa kesalahan ketik (typo) untuk subtitle bilingual (Indonesia + Inggris)."""

    def __init__(self, custom_whitelist: Optional[List[str]] = None, custom_whitelist_file: Optional[str] = None):
        self.whitelist: Set[str] = set(COMMON_WHITELIST)

        # 1. Muat otomatis berkas kustom pengguna jika ada (whitelist.txt / kamus_gaul.txt)
        search_dirs = [Path.cwd(), Path(__file__).parent]
        for sdir in search_dirs:
            for fname in ["whitelist.txt", "kamus_gaul.txt", "custom_whitelist.txt"]:
                wfile = sdir / fname
                if wfile.is_file():
                    try:
                        with open(wfile, "r", encoding="utf-8") as f:
                            for line in f:
                                line = line.strip()
                                if line and not line.startswith("#"):
                                    for item in re.split(r"[,;\s]+", line):
                                        if item.strip():
                                            self.whitelist.add(item.lower().strip())
                    except Exception:
                        pass

        # 1b. Muat dari berkas spesifik jika diberikan
        if custom_whitelist_file and Path(custom_whitelist_file).is_file():
            try:
                with open(custom_whitelist_file, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            for item in re.split(r"[,;\s]+", line):
                                if item.strip():
                                    self.whitelist.add(item.lower().strip())
            except Exception:
                pass

        # 2. Tambahkan whitelist manual dari parameter pemanggilan
        if custom_whitelist:
            for w in custom_whitelist:
                self.whitelist.add(w.lower().strip())

        # Inisialisasi Sastrawi (Kamus Bahasa Indonesia)
        self.dict_words: Set[str] = set()
        self.stemmer = None
        if HAS_SASTRAWI:
            factory = StemmerFactory()
            self.dict_words = factory.get_words()
            self.stemmer = factory.create_stemmer()

        # Inisialisasi English SpellChecker
        self.en_checker = SpellChecker() if HAS_SPELLCHECKER else None

        # Bangun daftar kata referensi untuk pencarian rekomendasi perbaikan
        self.reference_words: Set[str] = set(self.whitelist)
        if self.dict_words:
            self.reference_words.update(self.dict_words)

    # --------------------------------------------------------------------------
    # PILAR 1: DETEKSI KESALAHAN HURUF BESAR/KAPITAL (CASING TYPO)
    # --------------------------------------------------------------------------
    def is_casing_typo(self, token: str) -> bool:
        """
        Mendeteksi ketidaksengajaan tombol shift atau caps lock:
        - Huruf ke-1 dan ke-2 kapital, lalu huruf kecil (misal: 'BIsa', 'DAn', 'YAng')
        - Huruf kapital nyasar di tengah kata kecil (misal: 'seLalu', 'kanDungan', 'bisaA')
        Abaikan jika akronim ALL CAPS (BPOM, SPF) atau camelCase terdaftar di whitelist.
        """
        if len(token) <= 1 or token.isdigit():
            return False
        # Abaikan jika ALL CAPS (misal: 'BPOM', 'SPF', 'POV', atau penekanan teriakan subtitle)
        if token.isupper():
            return False
        # Pola double caps di awal (misal: 'BIsa', 'DAn')
        if re.match(r"^[A-Z]{2}[a-z]+$", token):
            return True
        # Pola huruf besar nyasar di tengah kata kecil (misal: 'seLalu', 'kanDungan')
        if re.match(r"^[a-z]+[A-Z]+[a-zA-Z]*$", token):
            if token in self.whitelist:
                return False
            return True
        return False

    # --------------------------------------------------------------------------
    # PILAR 3: DETEKSI KATA ALPHANUMERIC (LEETSPEAK / TYPO ANGKA)
    # --------------------------------------------------------------------------
    def is_alphanumeric_typo(self, token: str) -> bool:
        """
        Mendeteksi kata campuran huruf dan angka yang tidak baku (misal: '8isa', 'b1sa', 'k4mu', '5emua').
        Kecuali satuan ukuran atau kode resmi (misal: '50ml', 'spf30', '100mg', '1st', '10x').
        """
        has_alpha = bool(re.search(r"[A-Za-z]", token))
        has_digit = bool(re.search(r"\d", token))
        if has_alpha and has_digit:
            if VALID_UNIT_PATTERN.match(token):
                return False
            return True
        return False

    def is_base_valid(self, word: str) -> bool:
        """Mengecek keabsahan kata dasar / bentuk bersih terhadap KBBI / English / Whitelist."""
        clean = re.sub(r"[^a-zA-Z0-9áéíóúÁÉÍÓÚ]", "", word).lower().strip()
        if not clean or clean.isdigit() or len(clean) <= 1:
            return True
        if clean in self.whitelist:
            return True
        if self.en_checker and clean in self.en_checker:
            return True
        if self.dict_words:
            if clean in self.dict_words:
                return True
            if self.stemmer:
                stemmed = self.stemmer.stem(clean)
                if stemmed in self.dict_words:
                    return True

            # Morfologi bahasa Indonesia percakapan (akhiran -in, misal: 'tambahin', 'masukin', 'cobain')
            if clean.endswith("in") and len(clean) >= 5:
                base_in = clean[:-2]
                if base_in in self.dict_words or (self.stemmer and self.stemmer.stem(base_in) in self.dict_words):
                    return True

            # Klitika kepunyaan pada kata asing/serapan/whitelist (misal: 'harianmu', 'freshnya')
            for enc in ["nya", "mu", "ku"]:
                if clean.endswith(enc) and len(clean) > len(enc) + 2:
                    stem_enc = clean[:-len(enc)]
                    if stem_enc in self.whitelist or (self.en_checker and stem_enc in self.en_checker):
                        return True
                    if self.stemmer and self.stemmer.stem(stem_enc) in self.dict_words:
                        return True

            # Kata serapan resmi berakhiran -itas (misal: 'rutinitas', 'aktivitas', 'efektivitas')
            if clean.endswith("itas") and len(clean) >= 7:
                base_itas = clean[:-4]
                if base_itas in self.dict_words or (self.en_checker and (base_itas + "e") in self.en_checker):
                    return True

        # Kata campur kode (code-mixing) imbuhan Indonesia + kata bahasa Inggris (misal: 'dibuild', 'diblend', 'diswatch', 'ngepost')
        for pref in ["di", "ter", "ber", "nge", "ng"]:
            if clean.startswith(pref) and len(clean) > len(pref) + 2:
                root_en = clean[len(pref):]
                if (self.en_checker and root_en in self.en_checker) or root_en in self.whitelist:
                    return True

        return False

    def is_valid_word(self, token: str) -> bool:
        """
        Mengecek apakah satu kata valid dalam kaidah ortografi dan kamus bahasa.
        Memfilter Casing Typo (Pilar 1) dan Alphanumeric Typo (Pilar 3).
        """
        clean_raw = token.strip(".,!?:;\"'()%-")
        if not clean_raw or clean_raw.isdigit() or len(clean_raw) <= 1:
            return True

        # Satuan ukuran dan kode teknis resmi (misal: '50ml', 'spf30', '100mg', '1st')
        if VALID_UNIT_PATTERN.match(clean_raw):
            return True

        # 1. Cek Pilar 1: Casing Typo (BIsa, DAn, seLalu)
        if self.is_casing_typo(clean_raw):
            return False

        # 2. Cek Pilar 3: Alphanumeric Typo (8isa, k4mu, 5emua)
        if self.is_alphanumeric_typo(clean_raw):
            return False

        # Cek kata ulang bertanda hubung bahasa Indonesia (misal: 'sehari-hari', 'kadang-kadang')
        if "-" in clean_raw:
            parts = [p.strip() for p in clean_raw.split("-") if p.strip()]
            if parts and all(self.is_valid_word(p) for p in parts):
                return True

        return self.is_base_valid(clean_raw)

    # --------------------------------------------------------------------------
    # PILAR 1 RESOLUTION: REKONSTRUKSI CASING
    # --------------------------------------------------------------------------
    def resolve_casing(self, word: str) -> List[str]:
        """Merekonstruksi kata dengan typo casing (misal: 'BIsa' -> 'Bisa', 'bisa')."""
        cands = []
        w_title = word.capitalize()
        w_lower = word.lower()
        if self.is_base_valid(w_title) and w_title not in cands:
            cands.append(w_title)
        if self.is_base_valid(w_lower) and w_lower not in cands:
            cands.append(w_lower)
        return cands

    # --------------------------------------------------------------------------
    # PILAR 2 RESOLUTION: REKONSTRUKSI HOMOGLYPH OPTIK
    # --------------------------------------------------------------------------
    def resolve_homoglyphs(self, word: str) -> List[str]:
        """
        Menyelesaikan ambiguitas glif visual yang identik (I kapital vs l kecil vs 1 angka).
        Misal: 'kembaIi' -> 'kembali', 'Iebih' -> 'Lebih'/'lebih', 'blsa' -> 'bisa', 'haI' -> 'hal'.
        """
        cands = []

        # Kasus 1: Huruf 'I' kapital di tengah atau akhir kata kecil (misal: 'kembaIi', 'haI')
        if "I" in word and re.search(r"[a-z]", word):
            sub_l = word.replace("I", "l")
            if self.is_base_valid(sub_l) and sub_l not in cands:
                cands.append(sub_l)
            sub_i = word.replace("I", "i")
            if self.is_base_valid(sub_i) and sub_i not in cands:
                cands.append(sub_i)

        # Kasus 2: Huruf 'I' kapital di awal kata diikuti huruf kecil (misal: 'Iebih' -> 'Lebih', 'Iihat' -> 'Lihat')
        if word.startswith("I") and len(word) > 1 and word[1:].islower():
            sub_l_start = "L" + word[1:]
            if self.is_base_valid(sub_l_start) and sub_l_start not in cands:
                cands.append(sub_l_start)
            sub_lower = sub_l_start.lower()
            if self.is_base_valid(sub_lower) and sub_lower not in cands:
                cands.append(sub_lower)

        # Kasus 3: Huruf 'l' kecil diapit konsonan yang seharusnya 'i' (misal: 'blsa' -> 'bisa', 'kllit' -> 'kulit')
        if "l" in word.lower():
            sub_i = word.lower().replace("l", "i")
            if self.is_base_valid(sub_i) and sub_i not in cands:
                cands.append(sub_i)

        # Kasus 4: Pasangan homoglyph umum
        for bad, good in HOMOGLYPH_PAIRS:
            if bad in word:
                sub = word.replace(bad, good)
                if self.is_base_valid(sub) and sub not in cands:
                    cands.append(sub)

        return cands

    # --------------------------------------------------------------------------
    # PILAR 3 RESOLUTION: REKONSTRUKSI LEETSPEAK / ALPHANUMERIC
    # --------------------------------------------------------------------------
    def resolve_leetspeak(self, word: str) -> List[str]:
        """
        Merekonstruksi kata yang tercampur angka (leetspeak atau typo tombol angka).
        Misal: '8isa' -> 'bisa', 'k4mu' -> 'kamu', '5emua' -> 'semua', 'b1sa' -> 'bisa'.
        """
        cands = []
        w_lower = word.lower()
        for num, char in [('8', 'b'), ('1', 'i'), ('1', 'l'), ('0', 'o'), ('3', 'e'), ('4', 'a'), ('5', 's'), ('7', 't'), ('2', 'z')]:
            if num in w_lower:
                cand = w_lower.replace(num, char)
                if self.is_base_valid(cand) and cand not in cands:
                    cands.append(cand)
        return cands

    # --------------------------------------------------------------------------
    # PILAR 4 (Bagian A) RESOLUTION: REKONSTRUKSI LIGATURE OCR FONT MIRING
    # --------------------------------------------------------------------------
    def resolve_ocr_character_confusion(self, word: str) -> List[str]:
        """
        Merekonstruksi kata yang terdistorsi oleh kesalahan optik karakter OCR / font miring
        menggunakan matriks kerancuan karakter (misal: 'setebh' -> 'setelah', 'vvarna' -> 'warna').
        """
        cands = []
        w_lower = re.sub(r"[^a-zA-Z0-9]", "", word).lower().strip()
        if not w_lower or len(w_lower) <= 1:
            return []

        for bad, good in OCR_CHARACTER_CONFUSION_MATRIX:
            if bad in w_lower:
                c = w_lower.replace(bad, good)
                if self.is_base_valid(c) and c not in cands:
                    cands.append(c)

        return cands

    # --------------------------------------------------------------------------
    # PIPELINE REKOMENDASI PERBAIKAN KATA (SUGGESTIONS)
    # --------------------------------------------------------------------------
    def suggest_corrections(self, misspelled_word: str, max_suggestions: int = 3) -> List[str]:
        """
        Memberikan saran perbaikan kata berdasarkan 4 Pilar Arsitektur:
        1. Pilar Casing (BIsa -> Bisa)
        2. Pilar Homoglyph (kembaIi -> kembali, Iebih -> Lebih, blsa -> bisa)
        3. Pilar Leetspeak (8isa -> bisa, k4mu -> kamu)
        4. Pilar Ligature OCR & Damerau-Levenshtein QWERTY Proximity
        """
        raw_word = misspelled_word.strip(".,!?:;\"'()%-")
        clean = re.sub(r"[^a-zA-Z0-9áéíóúÁÉÍÓÚ]", "", raw_word)
        if not clean:
            return []

        suggestions = []

        # 1. PILAR 1: Casing Typo (misal: 'BIsa' -> 'Bisa', 'bisa')
        if self.is_casing_typo(raw_word):
            casing_cands = self.resolve_casing(raw_word)
            for c in casing_cands:
                if c not in suggestions:
                    suggestions.append(c)
            if suggestions:
                return suggestions[:max_suggestions]

        # 2. PILAR 2: Homoglyph Optik (misal: 'kembaIi' -> 'kembali', 'Iebih' -> 'Lebih', 'blsa' -> 'bisa')
        homo_cands = self.resolve_homoglyphs(raw_word)
        for hc in homo_cands:
            if hc not in suggestions:
                suggestions.append(hc)
        if suggestions:
            return suggestions[:max_suggestions]

        # 3. PILAR 3: Alphanumeric & Leetspeak (misal: '8isa' -> 'bisa', 'k4mu' -> 'kamu')
        if self.is_alphanumeric_typo(raw_word):
            leet_cands = self.resolve_leetspeak(raw_word)
            for lc in leet_cands:
                if lc not in suggestions:
                    suggestions.append(lc)
            if suggestions:
                return suggestions[:max_suggestions]

        # 4. PILAR 4 (A): OCR Ligature & Font Miring (misal: 'setebh' -> 'setelah', 'vvarna' -> 'warna')
        ocr_cands = self.resolve_ocr_character_confusion(clean)
        for oc in ocr_cands:
            if oc not in suggestions:
                suggestions.append(oc)
        if suggestions:
            return suggestions[:max_suggestions]

        # 5. PILAR 4 (B): Transposisi Huruf Berdampingan / Slip Jari (misal: 'bsia' -> 'bisa', 'adlaah' -> 'adalah')
        clean_lower = clean.lower()
        w_chars = list(clean_lower)
        for i in range(len(w_chars) - 1):
            w_chars[i], w_chars[i + 1] = w_chars[i + 1], w_chars[i]
            trans_cand = "".join(w_chars)
            if self.is_base_valid(trans_cand) and trans_cand not in suggestions:
                suggestions.append(trans_cand)
            w_chars[i], w_chars[i + 1] = w_chars[i + 1], w_chars[i]
        if suggestions:
            return suggestions[:max_suggestions]

        # 6. Pemecahan kata majemuk yang tertempel tanpa spasi (misal: 'Findyour' -> 'Find your', 'aftershower' -> 'after shower')
        found_compound_split = False
        for i in range(3, len(clean_lower) - 2):
            left = clean_lower[:i]
            right = clean_lower[i:]
            if self.is_base_valid(left) and self.is_base_valid(right) and len(left) >= 3 and len(right) >= 3:
                if raw_word and raw_word[0].isupper():
                    split_cand = f"{left.capitalize()} {right}"
                else:
                    split_cand = f"{left} {right}"
                if split_cand not in suggestions:
                    suggestions.append(split_cand)
                    found_compound_split = True
                    break

        # Jika merupakan dua kata valid yang menempel (seperti 'Findyour' atau 'makeit'), prioritaskan rekomendasi pemisahan
        if found_compound_split:
            return suggestions[:max_suggestions]

        # 6. Pola umum: kehilangan awalan imbuhan bahasa Indonesia (misal: 'engandung' -> 'mengandung')
        common_prefixes = ['m', 'me', 'men', 'meng', 'di', 'ter', 'ber', 'pe', 'peng']
        for pref in common_prefixes:
            candidate = pref + clean_lower
            if self.is_base_valid(candidate) and candidate not in suggestions:
                suggestions.append(candidate)

        # 7. Pola umum: kelebihan atau kekurangan 1 huruf di awal
        if len(clean_lower) > 2:
            if self.is_base_valid(clean_lower[1:]) and clean_lower[1:] not in suggestions:
                suggestions.append(clean_lower[1:])

        # 8. PILAR 4 (B): Damerau-Levenshtein dengan QWERTY Keyboard Proximity Re-ranking
        # Gunakan difflib untuk pra-seleksi cepat, lalu peringkat ulang dengan Damerau-Levenshtein
        fast_matches = difflib.get_close_matches(clean_lower, self.reference_words, n=15, cutoff=0.55)
        if fast_matches:
            scored = []
            for m in fast_matches:
                dist = damerau_levenshtein_distance(clean_lower, m)
                scored.append((dist, m))
            scored.sort(key=lambda x: x[0])
            for _, m in scored:
                if m not in suggestions:
                    suggestions.append(m)

        # 9. Fallback ke English SpellChecker jika ada
        if self.en_checker and len(suggestions) < max_suggestions:
            en_candidates = self.en_checker.candidates(clean_lower)
            if en_candidates:
                for cand in list(en_candidates)[:max_suggestions]:
                    if cand not in suggestions:
                        suggestions.append(cand)

        return suggestions[:max_suggestions]

    # --------------------------------------------------------------------------
    # PEMERIKSAAN TEKS (CHECK TEXT)
    # --------------------------------------------------------------------------
    def check_text(self, text: str) -> Dict[str, Any]:
        """
        Menganalisis satu kalimat teks untuk mendeteksi kata-kata yang berpotensi typo.
        Menerapkan alur bertingkat:
        - Lapis 1 & 2: Token-Pair Analysis (frasa terpotong semu / OCR ligature split).
        - Lapis 3: Pemeriksaan Token Individual dengan 4 Pilar Deteksi Typo.
        """
        raw_tokens = re.findall(r"\b[A-Za-z0-9'-]+\b", text)
        typos = []
        skip_indices = set()

        # --- LAPIS 1 & 2: Pemeriksaan Frasa / Token Bertetangga (Token-Pair Analysis) ---
        for i in range(len(raw_tokens) - 1):
            if i in skip_indices:
                continue

            t1 = raw_tokens[i]
            t2 = raw_tokens[i + 1]
            merged_lower = f"{t1}{t2}".lower().strip()

            # Jika token kedua adalah pecahan kata semu / non-word (misal: 'ebh', 'bagai')
            if not self.is_base_valid(t2) and len(t2) <= 5:
                # 1. Cek langsung jika merged adalah kata valid di KBBI (misal: 'se' + 'bagai' = 'sebagai')
                if self.is_base_valid(merged_lower):
                    typos.append({
                        "word": f"{t1} {t2}",
                        "suggestions": [merged_lower]
                    })
                    skip_indices.add(i)
                    skip_indices.add(i + 1)
                    continue

                # 2. Cek apakah gabungan kata terdistorsi oleh OCR Character Confusion Matrix (misal: 'Set' + 'ebh' -> 'setelah')
                conf_cands = self.resolve_ocr_character_confusion(merged_lower)
                if conf_cands:
                    typos.append({
                        "word": f"{t1} {t2}",
                        "suggestions": conf_cands[:3]
                    })
                    skip_indices.add(i)
                    skip_indices.add(i + 1)
                    continue

                # 3. Dynamic Smart-Merge & Levenshtein KBBI jika t1 adalah awalan pendek atau t1 sendiri tidak valid
                if (len(t1) <= 3 or not self.is_valid_word(t1)) and not self.is_alphanumeric_typo(t2):
                    matches = difflib.get_close_matches(merged_lower, self.reference_words, n=3, cutoff=0.70)
                    if matches:
                        typos.append({
                            "word": f"{t1} {t2}",
                            "suggestions": matches
                        })
                        skip_indices.add(i)
                        skip_indices.add(i + 1)
                        continue

        # --- LAPIS 3: Pemeriksaan Token Individual Standar dengan 4 Pilar ---
        for idx, token in enumerate(raw_tokens):
            if idx in skip_indices:
                continue

            # Lewati jika murni angka
            if token.isdigit() or len(token) <= 1:
                continue

            if not self.is_valid_word(token):
                suggs = self.suggest_corrections(token)
                typos.append({
                    "word": token,
                    "suggestions": suggs
                })

        return {
            "has_typo": len(typos) > 0,
            "typo_count": len(typos),
            "typos": typos
        }

    def check_subtitles(self, subtitles_list: Any) -> Dict[str, Any]:
        """
        Menganalisis seluruh daftar segmen subtitle dan menghasilkan laporan komprehensif.
        Mendukung input berupa list of dicts (standar OCR), list of str (baris teks), atau teks tunggal.
        """
        if isinstance(subtitles_list, str):
            subtitles_list = [{"id": 1, "text": subtitles_list.strip()}]
        elif isinstance(subtitles_list, (list, tuple)):
            normalized = []
            for idx, item in enumerate(subtitles_list):
                if isinstance(item, str):
                    normalized.append({
                        "id": idx + 1,
                        "text": item.strip(),
                        "start_time_srt": f"00:{idx:02d}:00,000",
                        "end_time_srt": f"00:{idx:02d}:05,000"
                    })
                elif isinstance(item, dict):
                    normalized.append(item)
                else:
                    normalized.append({"id": idx + 1, "text": str(item)})
            subtitles_list = normalized
        else:
            subtitles_list = []

        total_words = 0
        total_typos = 0
        annotated_subtitles = []
        typo_summary = []

        for sub in subtitles_list:
            text = sub.get("text", "") or sub.get("subtitle", "") or sub.get("content", "")
            words = text.split()
            total_words += len(words)

            analysis = self.check_text(text)
            sub_copy = dict(sub)
            sub_copy["typo_analysis"] = analysis

            if analysis["has_typo"]:
                total_typos += analysis["typo_count"]
                typo_summary.append({
                    "subtitle_id": sub.get("id"),
                    "timestamp": f"{sub.get('start_time_srt', '')} --> {sub.get('end_time_srt', '')}".strip(" ->"),
                    "text": text,
                    "typos": analysis["typos"]
                })

            annotated_subtitles.append(sub_copy)

        return {
            "total_subtitles_analyzed": len(subtitles_list),
            "total_words_analyzed": total_words,
            "total_typos_found": total_typos,
            "has_typo": total_typos > 0,
            "typo_details": typo_summary,
            "annotated_subtitles": annotated_subtitles
        }


# Alias kompatibilitas
TypoChecker = SubtitleTypoChecker


def format_typo_terminal_report(report: Dict[str, Any], filename: str) -> str:
    """Membuat tampilan laporan teks terminal yang rapi dan mudah dibaca."""
    lines = []
    lines.append("========================================================")
    lines.append(f"🔍 LAPORAN PEMERIKSAAN TYPO: {filename}")
    lines.append("========================================================")
    lines.append(f" • Total Subtitle Dianalisis : {report['total_subtitles_analyzed']}")
    lines.append(f" • Total Kata Dianalisis     : {report['total_words_analyzed']}")
    lines.append(f" • Total Typo Ditemukan      : {report['total_typos_found']}")
    lines.append("--------------------------------------------------------")

    if report["total_typos_found"] == 0:
        lines.append("✅ TIDAK ADA TYPO! Semua penulisan subtitle sudah benar.")
    else:
        lines.append("⚠️  DAFTAR KATA YANG DIDUGA SALAH TULIS (TYPO):")
        for item in report["typo_details"]:
            lines.append(f"\n[ID #{item['subtitle_id']}] Waktu: {item['timestamp']}")
            lines.append(f"  Teks Asli : \"{item['text']}\"")
            for tp in item["typos"]:
                sugg_str = ", ".join([f"'{s}'" for s in tp["suggestions"]]) if tp["suggestions"] else "(Tidak ada saran)"
                lines.append(f"  ❌ Kata Typo : '{tp['word']}'  👉  Saran Perbaikan: {sugg_str}")

    lines.append("========================================================\n")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="CLI Pemeriksa Kesalahan Ketik (Typo Checker) pada Subtitle Video (JSON atau TXT) Batch."
    )
    parser.add_argument("input_files", nargs="*", default=[], help="Satu atau lebih berkas JSON/TXT, pola wildcard (*.txt), atau folder direktori")
    parser.add_argument("-t", "--text", type=str, default=None, help="Teks atau kalimat langsung untuk diperiksa typo-nya")
    parser.add_argument("-o", "--output-report", help="Path untuk menyimpan laporan hasil pemeriksaan typo (JSON/TXT)")
    parser.add_argument("--whitelist", type=str, default="", help="Kata tambahan yang dianggap benar dipisahkan koma")

    args = parser.parse_args()

    custom_wl = [w.strip() for w in args.whitelist.split(",") if w.strip()]
    checker = SubtitleTypoChecker(custom_whitelist=custom_wl)

    # Mode 1: Pemeriksaan Teks Langsung via argumen --text
    if args.text is not None and args.text.strip():
        report = checker.check_subtitles([args.text.strip()])
        terminal_output = format_typo_terminal_report(report, "Input Teks Langsung")
        print(terminal_output)
        if args.output_report:
            with open(args.output_report, "w", encoding="utf-8") as f:
                if args.output_report.endswith(".json"):
                    json.dump(report, f, indent=2, ensure_ascii=False)
                else:
                    f.write(terminal_output)
            print(f"💾 Laporan tersimpan di: {args.output_report}")
        return

    # Mode 2: Resolusi berkas input: dukung nama file, daftar file, wildcard, atau folder
    resolved_paths: List[Path] = []
    for arg in args.input_files:
        if any(c in arg for c in ["*", "?", "["]):
            matched = glob.glob(arg)
            if matched:
                for m in sorted(matched):
                    mp = Path(m)
                    if mp.is_file() and mp.suffix.lower() in [".json", ".txt"] and mp not in resolved_paths:
                        resolved_paths.append(mp)
            continue

        p = Path(arg)
        if p.is_dir():
            folder_files = sorted(list(p.glob("*_subtitles.txt")) + list(p.glob("*_subtitles.json")))
            if not folder_files:
                folder_files = sorted(list(p.glob("*.txt")) + list(p.glob("*.json")))
            for f in folder_files:
                if f.is_file() and f not in resolved_paths:
                    resolved_paths.append(f)
            continue

        if p.exists() and p.is_file():
            if p not in resolved_paths:
                resolved_paths.append(p)
        else:
            print(f"❌ File tidak ditemukan: {p}")

    if not resolved_paths:
        print("❌ Tidak ada berkas subtitle (.json / .txt) yang valid atau gunakan opsi --text \"kalimat\".")
        sys.exit(1)

    total_batch_typos = 0
    total_batch_words = 0
    batch_summary = []

    for idx, input_path in enumerate(resolved_paths, 1):
        # Muat file JSON subtitle jika ekstensi .json
        if input_path.suffix.lower() == ".json":
            with open(input_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            subtitles = data.get("subtitles", [])
        elif input_path.suffix.lower() == ".txt":
            # Parse file TXT dengan pemfilteran header metadata otomatis
            subtitles = []
            sub_id = 1
            with open(input_path, "r", encoding="utf-8") as f:
                content = f.read()

            if "--- DAFTAR SUBTITLE ---" in content:
                subtitle_part = content.split("--- DAFTAR SUBTITLE ---")[1]
                for sep in ["---", "===", "🔍", "HASIL PEMERIKSAAN"]:
                    if sep in subtitle_part:
                        subtitle_part = subtitle_part.split(sep)[0]
                lines = subtitle_part.strip().splitlines()
            else:
                lines = content.splitlines()

            for line in lines:
                line = line.strip()
                if not line or line.startswith("#") or line.startswith("="):
                    continue
                m = re.match(r"^\[(.*?)\]\s*(.*)$", line)
                if m:
                    subtitles.append({"id": sub_id, "start_time_srt": m.group(1), "end_time_srt": "", "text": m.group(2).strip()})
                    sub_id += 1
                elif not any(h in line for h in ["TRANSKRIP", "Resolusi", "Diproses", "HASIL PEMERIKSAAN", "Daftar Typo", "Total Kata"]):
                    subtitles.append({"id": sub_id, "text": line})
                    sub_id += 1
        else:
            continue

        report = checker.check_subtitles(subtitles)
        terminal_output = format_typo_terminal_report(report, input_path.name)
        print(terminal_output)

        total_batch_typos += report["total_typos_found"]
        total_batch_words += report["total_words_analyzed"]
        batch_summary.append({
            "file": input_path.name,
            "subtitles": report["total_subtitles_analyzed"],
            "words": report["total_words_analyzed"],
            "typos": report["total_typos_found"]
        })

    # Jika memproses banyak berkas, tampilkan ringkasan eksekutif batch
    if len(resolved_paths) > 1:
        print("========================================================")
        print("✨ RINGKASAN BATCH TYPO CHECKER")
        print("========================================================")
        for bs in batch_summary:
            status_ico = "⚠️" if bs["typos"] > 0 else "✅"
            print(f" {status_ico} {bs['file']:<25} : {bs['typos']:>2} typo dari {bs['words']:>3} kata ({bs['subtitles']} sub)")
        print("--------------------------------------------------------")
        print(f" 📊 TOTAL : {len(resolved_paths)} berkas | {total_batch_words} kata | {total_batch_typos} typo ditemukan")
        print("========================================================\n")

    # Simpan output jika diminta (khusus berkas tunggal atau berkas pertama)
    if args.output_report and len(resolved_paths) == 1:
        out_path = Path(args.output_report)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        if out_path.suffix.lower() == ".json":
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            print(f"💾 Laporan tersimpan di: {out_path}")
        else:
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(terminal_output)
            print(f"💾 Laporan tersimpan di: {out_path}")


if __name__ == "__main__":
    main()
