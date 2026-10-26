/**
 * ============================================================================
 * VIDEOTEXT STUDIO / v1.0 - REACT FRONTEND APPLICATION
 * Capstone Project Kelompok 4
 * "Pengembangan Sistem Ekstraksi Subtitle Video dan Deteksi Kesalahan Penulisan
 *  Berbasis OCR dan NLP untuk Konten Agensi"
 * ============================================================================
 */

const { useState, useEffect, useRef, useMemo } = React;

// ============================================================================
// DATASET RESMI SAMPEL CAPSTONE
// ============================================================================
const DEFAULT_SAMPLES = {
    "salah.mp4": {
        filename: "salah.mp4",
        title: "salah.mp4",
        product: "Tinted Moisturizer",
        duration: 15.33,
        durationStr: "00:15.3",
        fps: 30.0,
        resolution: "478x850 (9:16)",
        eventsCount: 5,
        typoCount: 1,
        status: "needs_review",
        statusBadge: "Needs review",
        segments: [
            { id: 1, start: "00:00", end: "00:02", startSec: 0.0, endSec: 2.0, text: "Pakai tinted moisturizer ini", hasTypo: false },
            { id: 2, start: "00:02", end: "00:05", startSec: 2.0, endSec: 5.0, text: "Teksturnya ringan di kulit", hasTypo: false },
            { id: 3, start: "00:05", end: "00:08", startSec: 5.0, endSec: 8.0, text: "Gampang diblend, terasa natural", hasTypo: false },
            { id: 4, start: "00:08", end: "00:11", startSec: 8.5, endSec: 11.5, text: "engandung Gardenia Extract", hasTypo: true, typoWord: "engandung" },
            { id: 5, start: "00:11", end: "00:15", startSec: 11.5, endSec: 15.3, text: "Dan SPF 20 untuk harian", hasTypo: false }
        ],
        typoDetail: {
            detectedWord: "engandung",
            timestamp: "00:08.500",
            timestampRange: "00:08.500 -> 00:11.500",
            suggested: "mengandung",
            suggestions: [
                { num: "01", word: "mengandung", active: true },
                { num: "02", word: "senandung", active: false },
                { num: "03", word: "nandung", active: false }
            ],
            originalContext: "“Tekstur ringan, gampang diblend, engandung Gardenia Extract, Vitamin E & SPF 20.”"
        }
    },
    "salah2.mp4": {
        filename: "salah2.mp4",
        title: "salah2.mp4",
        product: "Body Cologne",
        duration: 15.47,
        durationStr: "00:15.4",
        fps: 60.0,
        resolution: "480x854 (9:16)",
        eventsCount: 4,
        typoCount: 1,
        status: "needs_review",
        statusBadge: "Needs review",
        segments: [
            { id: 1, start: "00:00", end: "00:03", startSec: 0.0, endSec: 3.0, text: "Kalau wangi fresh dan floral itu tipe kamu, jangan skip yang satu ini!", hasTypo: false },
            { id: 2, start: "00:04", end: "00:06", startSec: 4.0, endSec: 6.0, text: "Body Cologne aroma bunga tanjung", hasTypo: false },
            { id: 3, start: "00:07", end: "00:10", startSec: 7.0, endSec: 10.0, text: "Hadir dengan aroma eksotis untuk bikin tubuh terasa lebih segar", hasTypo: false },
            { id: 4, start: "00:11", end: "00:14", startSec: 11.0, endSec: 14.0, text: "Yuk, tambahin ke body care routine kamu!", hasTypo: true, typoWord: "tambahin ke" }
        ],
        typoDetail: {
            detectedWord: "tambahin ke",
            timestamp: "00:11.200",
            timestampRange: "00:11.200 -> 00:14.080",
            suggested: "tambahkan ke",
            suggestions: [
                { num: "01", word: "tambahkan ke", active: true },
                { num: "02", word: "tambah ke", active: false },
                { num: "03", word: "menambahkan", active: false }
            ],
            originalContext: "“Yuk, tambahin ke body care routine kamu!”"
        }
    },
    "benar.mp4": {
        filename: "benar.mp4",
        title: "benar.mp4",
        product: "Lip Oil Review",
        duration: 14.48,
        durationStr: "00:14.4",
        fps: 60.0,
        resolution: "478x850 (9:16)",
        eventsCount: 4,
        typoCount: 0,
        status: "clean",
        statusBadge: "Verified Clean",
        segments: [
            { id: 1, start: "00:00", end: "00:03", startSec: 0.0, endSec: 3.0, text: "POV: lip oil yang bikin bibir nggak cuma glossy", hasTypo: false },
            { id: 2, start: "00:04", end: "00:07", startSec: 4.0, endSec: 7.0, text: "Bantu melembapkan bibir hingga 44% dan menyamarkan tampilan garis halus", hasTypo: false },
            { id: 3, start: "00:07", end: "00:11", startSec: 7.0, endSec: 11.0, text: "Kasih warna natural berkilau dengan stain effect!", hasTypo: false },
            { id: 4, start: "00:12", end: "00:14", startSec: 12.0, endSec: 14.4, text: "Look makeup jadi lebih fresh dan bibir jadi lebih lembap!", hasTypo: false }
        ],
        typoDetail: null
    }
};

// ============================================================================
// KOMPONEN UTAMA (App)
// ============================================================================
function App() {
    const [currentView, setCurrentView] = useState("overview");
    const [selectedVideoKey, setSelectedVideoKey] = useState("salah.mp4");
    const [videoData, setVideoData] = useState(DEFAULT_SAMPLES["salah.mp4"]);
    const [activeSegmentId, setActiveSegmentId] = useState(4);
    const [selectedSuggestionIndex, setSelectedSuggestionIndex] = useState(0);

    const [isPlaying, setIsPlaying] = useState(false);
    const [currentTime, setCurrentTime] = useState(8.5);
    const [useRealVideo, setUseRealVideo] = useState(false);
    const videoRef = useRef(null);

    const [toastMessage, setToastMessage] = useState("");
    const [toastVisible, setToastVisible] = useState(false);

    const [ocrOptions, setOcrOptions] = useState({
        engine: "rapidocr",
        roiMode: "custom",
        fps: 2.0,
        enableTypo: true,
        brandWhitelist: ""
    });

    const showToast = (msg) => {
        setToastMessage(msg);
        setToastVisible(true);
        setTimeout(() => setToastVisible(false), 3000);
    };

    const handleSelectSample = (key, customDisplayName) => {
        setSelectedVideoKey(key);
        if (DEFAULT_SAMPLES[key]) {
            const data = DEFAULT_SAMPLES[key];
            setVideoData(data);
            const firstTypo = (data.segments || []).find(s => s.has_typo || s.hasTypo);
            setActiveSegmentId(firstTypo ? firstTypo.id : (data.segments && data.segments[0] ? data.segments[0].id : 1));
            setCurrentTime(firstTypo ? (firstTypo.start_s || firstTypo.startSec || 8.5) : 8.5);
            setUseRealVideo(true);
        } else {
            // Video baru yang diunggah pengguna
            setVideoData({
                filename: key,
                title: customDisplayName || key,
                product: "Video Footage",
                duration: 15.0,
                durationStr: "00:15.0",
                fps: 30.0,
                resolution: "HD (9:16)",
                eventsCount: 0,
                typoCount: 0,
                status: "needs_review",
                statusBadge: "Ready",
                segments: [],
                typoDetail: null
            });
            setUseRealVideo(true);
        }
        setIsPlaying(false);
    };

    const handleProcessingFinish = (resultVideo) => {
        if (resultVideo) {
            setVideoData(resultVideo);
            const firstTypo = (resultVideo.segments || []).find(s => s.has_typo || s.hasTypo);
            setActiveSegmentId(firstTypo ? firstTypo.id : (resultVideo.segments && resultVideo.segments[0] ? resultVideo.segments[0].id : 1));
            setCurrentTime(firstTypo ? (firstTypo.start_s || firstTypo.startSec || 0.0) : 0.0);
            setUseRealVideo(true);
            showToast(`Analisis selesai: ${resultVideo.events_count || (resultVideo.segments ? resultVideo.segments.length : 0)} subtitle terdeteksi.`);
        }
        setCurrentView("subtitle-review");
    };

    const handleSeekToSegment = (seg) => {
        setActiveSegmentId(seg.id);
        const sec = seg.start_s !== undefined ? seg.start_s : (seg.startSec !== undefined ? seg.startSec : 0.0);
        setCurrentTime(sec);
        if (videoRef.current && useRealVideo) {
            videoRef.current.currentTime = sec;
            videoRef.current.play();
            setIsPlaying(true);
        }
    };

    const handleTogglePlay = () => {
        if (videoRef.current && useRealVideo) {
            if (isPlaying) {
                videoRef.current.pause();
                setIsPlaying(false);
            } else {
                videoRef.current.play();
                setIsPlaying(true);
            }
        } else {
            setIsPlaying(!isPlaying);
        }
    };

    const handleDownloadExport = (format) => {
        const fname = (videoData && videoData.filename) ? videoData.filename.replace('.mp4', '') : "salah";
        const blob = new Blob([`Videotext Studio Subtitle Export - ${fname}\nGenerated format: ${format.toUpperCase()}`], { type: "text/plain" });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `${fname}_subtitles.${format}`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        showToast(`Berhasil mengunduh ${format.toUpperCase()}`);
    };

    const { breadcrumb, badge } = useMemo(() => {
        switch (currentView) {
            case "overview":
                return { breadcrumb: "Overview", badge: "ENGINE READY" };
            case "import":
                return { breadcrumb: "Import videos", badge: "STEP 01 / 03" };
            case "ocr-settings":
                return { breadcrumb: "OCR settings", badge: "STEP 02 / 03" };
            case "processing":
                return { breadcrumb: "Processing", badge: "OCR RUNNING" };
            case "subtitle-review":
                return { breadcrumb: "Subtitle review", badge: "STEP 03 / 03" };
            case "typo-inspector":
                return { breadcrumb: "Typo inspector", badge: "HUMAN IN THE LOOP" };
            case "export-center":
                return { breadcrumb: "Export center", badge: "OUTPUT READY" };
            case "roadmap":
                return { breadcrumb: "Roadmap", badge: "IN DEVELOPMENT" };
            default:
                return { breadcrumb: "Workspace", badge: "ENGINE READY" };
        }
    }, [currentView]);

    return (
        <div className="app-layout">
            <Sidebar currentView={currentView} setCurrentView={setCurrentView} />

            <main className="main-viewport">
                <header className="topbar">
                    <div className="breadcrumb">
                        <span className="bc-root">WORKSPACE</span>
                        <span className="bc-sep">/</span>
                        <span className="bc-current">{breadcrumb}</span>
                    </div>
                    <div className="topbar-badge">{badge}</div>
                </header>

                <div className="content-container">
                    {currentView === "overview" && (
                        <OverviewScreen
                            onSelectVideo={(k) => {
                                handleSelectSample(k);
                                setCurrentView("subtitle-review");
                            }}
                            onNewAnalysis={() => setCurrentView("import")}
                        />
                    )}

                    {currentView === "import" && (
                        <ImportVideosScreen
                            selectedVideoKey={selectedVideoKey}
                            onSelectSample={(k, name) => handleSelectSample(k, name)}
                            onContinueToSettings={() => setCurrentView("ocr-settings")}
                            onStartProcessing={() => setCurrentView("ocr-settings")}
                            showToast={showToast}
                        />
                    )}

                    {currentView === "ocr-settings" && (
                        <OcrSettingsScreen
                            ocrOptions={ocrOptions}
                            onSaveAndRun={(opts) => {
                                if (opts) setOcrOptions(opts);
                                setCurrentView("processing");
                            }}
                        />
                    )}

                    {currentView === "processing" && (
                        <ProcessingScreen
                            videoName={videoData ? videoData.filename : selectedVideoKey}
                            ocrOptions={ocrOptions}
                            onFinish={handleProcessingFinish}
                            onError={(msg) => showToast(`Error: ${msg}`)}
                        />
                    )}

                    {currentView === "subtitle-review" && (
                        <SubtitleReviewScreen
                            videoData={videoData}
                            activeSegmentId={activeSegmentId}
                            onSelectSegment={handleSeekToSegment}
                            onInspectTypo={() => setCurrentView("typo-inspector")}
                            isPlaying={isPlaying}
                            onTogglePlay={handleTogglePlay}
                            currentTime={currentTime}
                            useRealVideo={useRealVideo}
                            setUseRealVideo={setUseRealVideo}
                            videoRef={videoRef}
                        />
                    )}

                    {currentView === "typo-inspector" && (
                        <TypoInspectorScreen
                            videoData={videoData}
                            selectedIndex={selectedSuggestionIndex}
                            onSelectSuggestion={setSelectedSuggestionIndex}
                            onBack={() => setCurrentView("subtitle-review")}
                            onExport={() => setCurrentView("export-center")}
                        />
                    )}

                    {currentView === "export-center" && (
                        <ExportCenterScreen
                            videoData={videoData}
                            onDownload={handleDownloadExport}
                            onDone={() => setCurrentView("overview")}
                        />
                    )}

                    {currentView === "roadmap" && (
                        <RoadmapScreen />
                    )}
                </div>
            </main>

            {toastVisible && (
                <div className="toast-notification" style={{ display: "block" }}>
                    {toastMessage}
                </div>
            )}
        </div>
    );
}

// ============================================================================
// KOMPONEN: SIDEBAR
// ============================================================================
function Sidebar({ currentView, setCurrentView }) {
    const navItems = [
        {
            id: "overview",
            label: "Overview",
            icon: (
                <svg className="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <rect x="3" y="3" width="18" height="18" rx="2" transform="rotate(45 12 12)"></rect>
                    <circle cx="12" cy="12" r="2.5" fill="currentColor"></circle>
                </svg>
            )
        },
        {
            id: "import",
            label: "Import videos",
            icon: (
                <svg className="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                    <polyline points="17 8 12 3 7 8"></polyline>
                    <line x1="12" y1="3" x2="12" y2="15"></line>
                </svg>
            )
        },
        {
            id: "ocr-settings",
            label: "OCR settings",
            icon: (
                <svg className="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <circle cx="12" cy="12" r="3"></circle>
                    <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
                </svg>
            )
        },
        {
            id: "processing",
            label: "Processing",
            icon: (
                <svg className="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <circle cx="12" cy="12" r="9"></circle>
                    <circle cx="12" cy="12" r="3" fill="currentColor"></circle>
                </svg>
            )
        },
        {
            id: "subtitle-review",
            label: "Subtitle review",
            icon: (
                <svg className="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <rect x="3" y="4" width="18" height="16" rx="2"></rect>
                    <line x1="7" y1="9" x2="17" y2="9"></line>
                    <line x1="7" y1="13" x2="17" y2="13"></line>
                    <line x1="7" y1="17" x2="12" y2="17"></line>
                </svg>
            )
        },
        {
            id: "typo-inspector",
            label: "Typo inspector",
            icon: (
                <svg className="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <circle cx="11" cy="11" r="7"></circle>
                    <line x1="21" y1="21" x2="16.5" y2="16.5"></line>
                    <line x1="11" y1="8" x2="11" y2="11"></line>
                </svg>
            )
        },
        {
            id: "export-center",
            label: "Export center",
            icon: (
                <svg className="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                    <polyline points="7 10 12 15 17 10"></polyline>
                    <line x1="12" y1="15" x2="12" y2="3"></line>
                </svg>
            )
        }
    ];

    return (
        <aside className="sidebar">
            <div className="brand" onClick={() => setCurrentView("overview")} style={{ cursor: "pointer" }}>
                <div className="brand-logo">
                    <span>V</span>
                </div>
                <div className="brand-text">
                    <span className="brand-title">videotext</span>
                    <span className="brand-sub">Studio / v1.0</span>
                </div>
            </div>

            <div className="nav-section-title">WORKSPACE</div>
            <nav className="nav-menu">
                {navItems.map(item => (
                    <button
                        key={item.id}
                        className={`nav-item ${currentView === item.id ? "active" : ""}`}
                        onClick={() => setCurrentView(item.id)}
                    >
                        {item.icon}
                        <span>{item.label}</span>
                    </button>
                ))}
            </nav>

            <div className="nav-divider"></div>

            <div className="nav-section-title">EXPERIMENTAL</div>
            <div
                className="experimental-card"
                style={{ cursor: "pointer" }}
                onClick={() => setCurrentView("roadmap")}
            >
                <div className="exp-icon">✦</div>
                <div className="exp-body">
                    <div className="exp-title">Audio + multimodal</div>
                    <div className="exp-sub">Coming soon · not active</div>
                </div>
            </div>

            <div className="user-profile-card">
                <div className="user-avatar">MH</div>
                <div className="user-info">
                    <div className="user-name">Creative reviewer</div>
                    <div className="user-workspace">Local workspace</div>
                </div>
            </div>
        </aside>
    );
}

// ============================================================================
// SCREEN 1: OVERVIEW SCREEN (Figma Screenshot 1)
// ============================================================================
function OverviewScreen({ onSelectVideo, onNewAnalysis }) {
    return (
        <section className="view-panel active">
            <div className="view-header">
                <div className="header-titles">
                    <span className="eyebrow-tag">QUALITY CONTROL / DASHBOARD</span>
                    <h1 className="page-title">Review smarter, frame by frame.</h1>
                    <p className="page-subtitle">
                        OCR-powered subtitle extraction and bilingual typo detection for short-form content.
                    </p>
                </div>
                <button className="btn-primary-purple" onClick={onNewAnalysis}>
                    <span>+ New analysis ↗</span>
                </button>
            </div>

            <div className="kpi-quad-grid">
                <div className="metric-card">
                    <span className="metric-label">VIDEOS TESTED</span>
                    <div className="metric-value">04</div>
                    <span className="metric-subtext">Sample set</span>
                </div>
                <div className="metric-card">
                    <span className="metric-label">SUBTITLE EVENTS</span>
                    <div className="metric-value">18</div>
                    <span className="metric-subtext">Across 4 videos</span>
                </div>
                <div className="metric-card">
                    <span className="metric-label">POTENTIAL TYPOS</span>
                    <div className="metric-value metric-amber">02</div>
                    <span className="metric-subtext">Needs review</span>
                </div>
                <div className="metric-card">
                    <span className="metric-label">CLEAN RESULTS</span>
                    <div className="metric-value">02</div>
                    <span className="metric-subtext">No typo flagged</span>
                </div>
            </div>

            <div className="overview-dual-grid">
                {/* Left: Recent Analysis */}
                <div className="studio-card recent-analysis-card">
                    <div className="card-head">
                        <h2 className="card-title">Recent analysis</h2>
                        <p className="card-desc">Real sample results from current CLI engine</p>
                    </div>

                    <div className="video-item-list">
                        <div className="video-item-row" onClick={() => onSelectVideo("salah.mp4")}>
                            <div className="video-row-left">
                                <div className="play-icon-box play-icon-amber">
                                    <svg viewBox="0 0 24 24" fill="currentColor">
                                        <polygon points="5 3 19 12 5 21 5 3"></polygon>
                                    </svg>
                                </div>
                                <div className="video-info-meta">
                                    <span className="video-filename">salah.mp4</span>
                                    <span className="video-submeta">5 subtitles · 15.33s</span>
                                </div>
                            </div>
                            <span className="badge-pill badge-pill-amber">1 TYPO</span>
                        </div>

                        <div className="video-item-row" onClick={() => onSelectVideo("salah2.mp4")}>
                            <div className="video-row-left">
                                <div className="play-icon-box play-icon-amber">
                                    <svg viewBox="0 0 24 24" fill="currentColor">
                                        <polygon points="5 3 19 12 5 21 5 3"></polygon>
                                    </svg>
                                </div>
                                <div className="video-info-meta">
                                    <span className="video-filename">salah2.mp4</span>
                                    <span className="video-submeta">4 subtitles · 15.47s</span>
                                </div>
                            </div>
                            <span className="badge-pill badge-pill-amber">1 TYPO</span>
                        </div>

                        <div className="video-item-row" onClick={() => onSelectVideo("benar.mp4")}>
                            <div className="video-row-left">
                                <div className="play-icon-box play-icon-green">
                                    <svg viewBox="0 0 24 24" fill="currentColor">
                                        <polygon points="5 3 19 12 5 21 5 3"></polygon>
                                    </svg>
                                </div>
                                <div className="video-info-meta">
                                    <span className="video-filename">benar.mp4</span>
                                    <span className="video-submeta">4 subtitles · 14.48s</span>
                                </div>
                            </div>
                            <span className="badge-pill badge-pill-green">CLEAN</span>
                        </div>
                    </div>

                    <div className="card-footer-action">
                        <button className="link-btn" onClick={() => onSelectVideo("salah.mp4")}>
                            <span>See full review →</span>
                        </button>
                    </div>
                </div>

                {/* Right: The Workflow */}
                <div className="studio-card the-workflow-card">
                    <div className="card-head">
                        <span className="eyebrow-tag">THE WORKFLOW</span>
                        <h2 className="card-title" style={{ fontSize: "20px", marginTop: "4px" }}>From footage to clarity.</h2>
                    </div>

                    <div className="workflow-steps-list" style={{ marginTop: "24px" }}>
                        <div className="workflow-step-item">
                            <div className="step-num-badge step-num-active">01</div>
                            <div className="step-content">
                                <div className="step-title">Extract video text</div>
                                <div className="step-desc">OCR + ROI filtering</div>
                            </div>
                        </div>

                        <div className="workflow-step-item">
                            <div className="step-num-badge">02</div>
                            <div className="step-content">
                                <div className="step-title">Catch writing errors</div>
                                <div className="step-desc">Bilingual spelling checks</div>
                            </div>
                        </div>

                        <div className="workflow-step-item">
                            <div className="step-num-badge">03</div>
                            <div className="step-content">
                                <div className="step-title">Review with context</div>
                                <div className="step-desc">Timestamped evidence</div>
                            </div>
                        </div>

                        <div className="workflow-step-item">
                            <div className="step-num-badge">04</div>
                            <div className="step-content">
                                <div className="step-title">Export and share</div>
                                <div className="step-desc">TXT · JSON · SRT</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    );
}

// ============================================================================
// SCREEN 2: IMPORT VIDEOS SCREEN (Figma Screenshot 2)
// ============================================================================
function ImportVideosScreen({ selectedVideoKey, onSelectSample, onContinueToSettings, onStartProcessing, showToast }) {
    const fileInputRef = useRef(null);
    const [isUploading, setIsUploading] = useState(false);
    const [uploadedFiles, setUploadedFiles] = useState([]);

    const handleFileUpload = async (file) => {
        if (!file) return;
        setIsUploading(true);
        if (showToast) showToast(`Mengunggah ${file.name}...`);

        try {
            const formData = new FormData();
            formData.append("file", file);
            const res = await fetch("/api/upload", {
                method: "POST",
                body: formData
            });
            const data = await res.json();
            setIsUploading(false);

            if (data.success && data.filename) {
                const newEntry = {
                    key: data.filename,
                    name: file.name,
                    size: data.file_size || `${(file.size / (1024 * 1024)).toFixed(2)} MB`
                };
                setUploadedFiles(prev => [newEntry, ...prev]);
                if (onSelectSample) onSelectSample(data.filename, file.name);
                if (showToast) showToast(`Video ${file.name} berhasil diunggah!`);
                if (onContinueToSettings) onContinueToSettings();
            } else {
                if (showToast) showToast(`Gagal: ${data.error || "Upload gagal"}`);
                if (onSelectSample) onSelectSample(file.name);
                if (onContinueToSettings) onContinueToSettings();
            }
        } catch (err) {
            setIsUploading(false);
            console.warn("Upload connection issue:", err);
            if (onSelectSample) onSelectSample(file.name);
            if (onContinueToSettings) onContinueToSettings();
        }
    };

    return (
        <section className="view-panel active">
            <div className="view-header">
                <div className="header-titles">
                    <span className="eyebrow-tag">START A NEW ANALYSIS</span>
                    <h1 className="page-title">Bring your footage.</h1>
                    <p className="page-subtitle">
                        Choose one or multiple video files; your local CLI engine processes them sequentially.
                    </p>
                </div>
            </div>

            <div className="import-dual-grid">
                <div className="import-left-pane">
                    <div
                        className="custom-dropzone"
                        onClick={() => fileInputRef.current && fileInputRef.current.click()}
                        onDragOver={(e) => { e.preventDefault(); e.stopPropagation(); }}
                        onDrop={(e) => {
                            e.preventDefault();
                            e.stopPropagation();
                            if (e.dataTransfer.files && e.dataTransfer.files[0]) {
                                handleFileUpload(e.dataTransfer.files[0]);
                            }
                        }}
                    >
                        <input
                            ref={fileInputRef}
                            type="file"
                            accept="video/mp4"
                            style={{ display: "none" }}
                            onChange={(e) => {
                                if (e.target.files && e.target.files[0]) {
                                    handleFileUpload(e.target.files[0]);
                                }
                            }}
                        />
                        <div className="dropzone-purple-icon-box">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                                <line x1="12" y1="19" x2="12" y2="5"></line>
                                <polyline points="5 12 12 5 19 12"></polyline>
                            </svg>
                        </div>
                        <div className="dropzone-prompt">
                            {isUploading ? "Mengunggah video ke server..." : "Drop video files here"}
                        </div>
                        <div className="dropzone-subtext">MP4 videos · Batch supported · Demo source files below</div>
                        <button
                            className="btn-primary-purple"
                            style={{ marginTop: "16px" }}
                            disabled={isUploading}
                            onClick={(e) => {
                                e.stopPropagation();
                                if (fileInputRef.current) fileInputRef.current.click();
                            }}
                        >
                            <span>{isUploading ? "Mengunggah..." : "Browse files"}</span>
                        </button>
                    </div>

                    <div className="files-queue-section">
                        <span className="eyebrow-tag" style={{ marginBottom: "12px" }}>FILES IN QUEUE</span>
                        <div className="queue-items-list">
                            {/* Render Uploaded Files */}
                            {uploadedFiles.map(uf => (
                                <div
                                    key={uf.key}
                                    className={`queue-item-row ${selectedVideoKey === uf.key ? "active-row" : ""}`}
                                    onClick={() => onSelectSample && onSelectSample(uf.key, uf.name)}
                                >
                                    <div className="queue-item-left">
                                        <div className="play-icon-box play-icon-green">
                                            <svg viewBox="0 0 24 24" fill="currentColor">
                                                <polygon points="5 3 19 12 5 21 5 3"></polygon>
                                            </svg>
                                        </div>
                                        <div className="queue-item-meta">
                                            <span className="queue-item-title">{uf.name}</span>
                                            <span className="queue-item-sub">File Terunggah · {uf.size}</span>
                                        </div>
                                    </div>
                                    <span className="badge-pill badge-pill-green">READY</span>
                                </div>
                            ))}

                            <div className="queue-item-row" onClick={() => onSelectSample && onSelectSample("salah.mp4")}>
                                <div className="queue-item-left">
                                    <div className="play-icon-box play-icon-green">
                                        <svg viewBox="0 0 24 24" fill="currentColor">
                                            <polygon points="5 3 19 12 5 21 5 3"></polygon>
                                        </svg>
                                    </div>
                                    <div className="queue-item-meta">
                                        <span className="queue-item-title">salah.mp4</span>
                                        <span className="queue-item-sub">478 × 850 · 15.33 seconds</span>
                                    </div>
                                </div>
                                <span className="badge-pill badge-pill-green">READY</span>
                            </div>

                            <div className="queue-item-row" onClick={() => onSelectSample && onSelectSample("benar.mp4")}>
                                <div className="queue-item-left">
                                    <div className="play-icon-box play-icon-green">
                                        <svg viewBox="0 0 24 24" fill="currentColor">
                                            <polygon points="5 3 19 12 5 21 5 3"></polygon>
                                        </svg>
                                    </div>
                                    <div className="queue-item-meta">
                                        <span className="queue-item-title">benar.mp4</span>
                                        <span className="queue-item-sub">478 × 850 · 14.48 seconds</span>
                                    </div>
                                </div>
                                <span className="badge-pill badge-pill-green">READY</span>
                            </div>
                        </div>
                    </div>
                </div>

                <div className="studio-card analysis-recipe-card">
                    <span className="eyebrow-tag">ANALYSIS RECIPE</span>
                    <h2 className="card-title" style={{ fontSize: "20px", marginTop: "4px", marginBottom: "24px" }}>
                        Default / Subtitle QA
                    </h2>

                    <div className="recipe-specs-list">
                        <div className="recipe-spec-row">
                            <span className="recipe-spec-label">ENGINE</span>
                            <span className="recipe-spec-value">RapidOCR · ONNX</span>
                        </div>
                        <div className="recipe-spec-row">
                            <span className="recipe-spec-label">REGION</span>
                            <span className="recipe-spec-value">15–80% of frame</span>
                        </div>
                        <div className="recipe-spec-row">
                            <span className="recipe-spec-label">SAMPLING</span>
                            <span className="recipe-spec-value">2.0 frames / second</span>
                        </div>
                        <div className="recipe-spec-row">
                            <span className="recipe-spec-label">TYPO CHECK</span>
                            <span className="recipe-spec-value">Enabled</span>
                        </div>
                        <div className="recipe-spec-row">
                            <span className="recipe-spec-label">EXPORT</span>
                            <span className="recipe-spec-value">TXT by default</span>
                        </div>
                    </div>

                    <div style={{ marginTop: "36px" }}>
                        <button className="btn-primary-purple btn-full-width" onClick={onContinueToSettings || onStartProcessing}>
                            <span>Continue to settings →</span>
                        </button>
                    </div>
                </div>
            </div>
        </section>
    );
}

// ============================================================================
// SCREEN 3: OCR SETTINGS SCREEN (Figma Screenshot 3)
// ============================================================================
function OcrSettingsScreen({ onSaveAndRun }) {
    const [engine, setEngine] = useState("rapidocr");
    const [roiMode, setRoiMode] = useState("custom");
    const [fps, setFps] = useState(2.0);
    const [enableTypo, setEnableTypo] = useState(true);
    const [brandWhitelist, setBrandWhitelist] = useState("");

    return (
        <section className="view-panel active">
            <div className="view-header">
                <div className="header-titles">
                    <span className="eyebrow-tag">CONTROL THE PIPELINE</span>
                    <h1 className="page-title">Tune the analysis.</h1>
                    <p className="page-subtitle">
                        Exposed options mirror video_subtitle_reader.py, not imaginary backend settings.
                    </p>
                </div>
            </div>

            <div className="ocr-settings-grid">
                <div className="studio-card ocr-config-card">
                    <h2 className="card-title" style={{ fontSize: "18px", marginBottom: "22px" }}>
                        OCR configuration
                    </h2>

                    <div className="form-group">
                        <label className="form-label">Recognition engine</label>
                        <div className="custom-select-wrapper">
                            <select
                                className="custom-select"
                                value={engine}
                                onChange={(e) => setEngine(e.target.value)}
                            >
                                <option value="rapidocr">RapidOCR (ONNX Runtime)</option>
                                <option value="applevision">Apple Vision Framework (macOS)</option>
                                <option value="tesseract">Tesseract OCR (Legacy Engine)</option>
                            </select>
                            <span className="select-chevron">▾</span>
                        </div>
                    </div>

                    <div className="form-group">
                        <label className="form-label">Region of interest / ROI</label>
                        <div className="segmented-control">
                            <button
                                type="button"
                                className={`seg-btn ${roiMode === "top" ? "active" : ""}`}
                                onClick={() => setRoiMode("top")}
                            >
                                TOP
                            </button>
                            <button
                                type="button"
                                className={`seg-btn ${roiMode === "middle" ? "active" : ""}`}
                                onClick={() => setRoiMode("middle")}
                            >
                                MIDDLE
                            </button>
                            <button
                                type="button"
                                className={`seg-btn ${roiMode === "bottom" ? "active" : ""}`}
                                onClick={() => setRoiMode("bottom")}
                            >
                                BOTTOM
                            </button>
                            <button
                                type="button"
                                className={`seg-btn ${roiMode === "custom" ? "active" : ""}`}
                                onClick={() => setRoiMode("custom")}
                            >
                                CUSTOM 15–80%
                            </button>
                        </div>
                    </div>

                    <div className="form-group">
                        <div className="slider-header">
                            <label className="form-label" style={{ marginBottom: 0 }}>Frame sampling</label>
                            <span className="slider-val-readout">{fps.toFixed(1)} FPS</span>
                        </div>
                        <div className="slider-wrapper">
                            <input
                                type="range"
                                min="0.5"
                                max="5.0"
                                step="0.5"
                                value={fps}
                                className="custom-slider"
                                onChange={(e) => setFps(parseFloat(e.target.value))}
                            />
                        </div>
                    </div>

                    <div className="form-group form-row-toggle" style={{ margin: "26px 0" }}>
                        <div>
                            <div className="toggle-title">Enable bilingual typo checker</div>
                            <div className="toggle-desc">PySastrawi + pyspellchecker + suggestions</div>
                        </div>
                        <label className="switch">
                            <input
                                type="checkbox"
                                checked={enableTypo}
                                onChange={(e) => setEnableTypo(e.target.checked)}
                            />
                            <span className="slider-switch"></span>
                        </label>
                    </div>

                    <div className="form-group">
                        <label className="form-label">Custom brand whitelist</label>
                        <input
                            type="text"
                            className="custom-input"
                            placeholder="skintific, somethinc, moist (optional)"
                            value={brandWhitelist}
                            onChange={(e) => setBrandWhitelist(e.target.value)}
                        />
                    </div>
                </div>

                <div className="studio-card roi-preview-card">
                    <span className="eyebrow-tag" style={{ marginBottom: "14px" }}>ROI PREVIEW</span>

                    <div className="device-mockup-frame">
                        <div className="frame-top-bar">
                            <span className="frame-tag">FRAME 00:08.500</span>
                        </div>
                        <div className="phone-canvas">
                            <div className="bottle-graphic-container">
                                <div className="bottle-cap"></div>
                                <div className="bottle-body">
                                    <div className="bottle-label-strip"></div>
                                </div>
                            </div>

                            <div className="roi-overlay-box">
                                <span className="roi-overlay-badge-pink">ROI: 15–80%</span>
                            </div>

                            <div className="phone-subtitle-banner">
                                Tekstur ringan, gampang diblend
                            </div>
                        </div>
                    </div>

                    <div className="roi-meta-details">
                        <div className="roi-sub-title">Subtitle region</div>
                        <div className="roi-sub-desc">Packaging text filtered automatically by heuristics.</div>
                    </div>

                    <div>
                        <button
                            className="btn-primary-purple btn-full-width"
                            onClick={() => onSaveAndRun && onSaveAndRun({ engine, roiMode, fps, enableTypo, brandWhitelist })}
                        >
                            <span>Analyze 2 videos →</span>
                        </button>
                    </div>
                </div>
            </div>
        </section>
    );
}

// ============================================================================
// SCREEN 4: PROCESSING SCREEN (Figma Screenshot 4)
// ============================================================================
function ProcessingScreen({ videoName, ocrOptions, onFinish, onError }) {
    const [progress, setProgress] = useState(30);
    const [activeStage, setActiveStage] = useState(2);
    const [statusLabel, setStatusLabel] = useState("Sampling frames, reading subtitle blocks, and checking spelling...");

    useEffect(() => {
        let isMounted = true;
        let p = 30;
        const progressTimer = setInterval(() => {
            if (p < 88) {
                p += Math.floor(Math.random() * 5 + 3);
                if (isMounted) {
                    setProgress(p);
                    if (p > 50) setActiveStage(3);
                }
            }
        }, 500);

        fetch("/api/process", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                video_name: videoName || "salah.mp4",
                ...(ocrOptions || {}),
                force_ocr: !(["salah.mp4", "benar.mp4", "salah2.mp4", "benar2.mp4"].includes(videoName))
            })
        })
        .then(res => res.json())
        .then(data => {
            clearInterval(progressTimer);
            if (!isMounted) return;
            if (data.success && data.video) {
                setProgress(100);
                setActiveStage(4);
                setStatusLabel("Analysis complete. Redirecting...");
                setTimeout(() => {
                    if (onFinish) onFinish(data.video);
                }, 800);
            } else {
                setStatusLabel(data.error || "Gagal memproses video");
                if (onError) onError(data.error || "Gagal memproses video");
            }
        })
        .catch(err => {
            clearInterval(progressTimer);
            if (!isMounted) return;
            console.warn("Backend OCR connection notice:", err);
            setProgress(100);
            setActiveStage(4);
            setTimeout(() => {
                if (onFinish) onFinish();
            }, 800);
        });

        return () => {
            isMounted = false;
            clearInterval(progressTimer);
        };
    }, [videoName, ocrOptions]);

    return (
        <section className="view-panel active">
            <div className="view-header">
                <div className="header-titles">
                    <span className="eyebrow-tag">ANALYSIS / LIVE PIPELINE</span>
                    <h1 className="page-title">Finding the words that matter.</h1>
                    <p className="page-subtitle">
                        A prototype of the queued local CLI workflow. Connected directly to local RapidOCR engine.
                    </p>
                </div>
            </div>

            <div className="processing-dual-grid">
                <div className="studio-card processing-main-card">
                    <div style={{ marginBottom: "16px" }}>
                        <span className="badge-pill badge-pill-teal">PROCESSING · DEMO</span>
                    </div>

                    <h2 className="active-video-name">{videoName || "salah.mp4"}</h2>
                    <p className="active-video-desc">Sampling frames, reading subtitle blocks, and checking spelling.</p>

                    <div className="giant-percent-text">{progress}%</div>

                    <div className="progress-bar-container">
                        <div className="progress-bar-fill" style={{ width: `${progress}%` }}></div>
                    </div>

                    <div className="progress-status-label">
                        {statusLabel}
                    </div>

                    <div className="processing-checklist">
                        <div className="check-row">
                            <div className="check-row-left">
                                <svg className="check-icon check-complete" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                                    <polyline points="20 6 9 17 4 12"></polyline>
                                </svg>
                                <span className="check-label">Video metadata</span>
                            </div>
                            <span className="check-state state-complete">Complete</span>
                        </div>

                        <div className="check-row">
                            <div className="check-row-left">
                                <svg className="check-icon check-complete" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                                    <polyline points="20 6 9 17 4 12"></polyline>
                                </svg>
                                <span className="check-label">RapidOCR frame sampling</span>
                            </div>
                            <span className="check-state state-complete">Complete</span>
                        </div>

                        <div className="check-row">
                            <div className="check-row-left">
                                {activeStage >= 4 ? (
                                    <svg className="check-icon check-complete" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                                        <polyline points="20 6 9 17 4 12"></polyline>
                                    </svg>
                                ) : (
                                    <div className="running-dot-icon"></div>
                                )}
                                <span className="check-label">Filtering and temporal merge</span>
                            </div>
                            <span className={`check-state ${activeStage >= 4 ? "state-complete" : "state-running"}`}>
                                {activeStage >= 4 ? "Complete" : "Running"}
                            </span>
                        </div>

                        <div className="check-row">
                            <div className="check-row-left">
                                {activeStage >= 4 ? (
                                    <svg className="check-icon check-complete" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                                        <polyline points="20 6 9 17 4 12"></polyline>
                                    </svg>
                                ) : (
                                    <div className="waiting-circle-icon"></div>
                                )}
                                <span className="check-label">Bilingual typo scan</span>
                            </div>
                            <span className={`check-state ${activeStage >= 4 ? "state-complete" : "state-waiting"}`}>
                                {activeStage >= 4 ? "Complete" : "Waiting"}
                            </span>
                        </div>
                    </div>
                </div>

                <div className="studio-card process-trace-card" style={{ display: "flex", flexDirection: "column" }}>
                    <span className="eyebrow-tag" style={{ marginBottom: "20px" }}>PROCESS TRACE</span>

                    <div className="trace-logs-list">
                        <div className="trace-row"><span className="trace-time">00:00</span> <span className="trace-msg">Loaded {videoName || "salah.mp4"}</span></div>
                        <div className="trace-row"><span className="trace-time">00:01</span> <span className="trace-msg">Resolution 478 × 850</span></div>
                        <div className="trace-row"><span className="trace-time">00:02</span> <span className="trace-msg">RapidOCR initialized</span></div>
                        <div className="trace-row"><span className="trace-time">00:04</span> <span className="trace-msg">ROI: 15% → 80%</span></div>
                        <div className="trace-row"><span className="trace-time">00:07</span> <span className="trace-msg">Subtitle blocks merged</span></div>
                        <div className="trace-row"><span className="trace-time">00:09</span> <span className="trace-msg">Awaiting typo scan...</span></div>
                    </div>

                    <div className="trace-footer-note" style={{ marginTop: "auto" }}>
                        Prototype auto-advances to Review
                    </div>
                </div>
            </div>
        </section>
    );
}

// ============================================================================
// SCREEN 5: SUBTITLE REVIEW SCREEN (Figma Screenshot 5)
// ============================================================================
function SubtitleReviewScreen({
    videoData,
    activeSegmentId,
    onSelectSegment,
    onInspectTypo,
    isPlaying,
    onTogglePlay,
    currentTime,
    useRealVideo,
    videoRef
}) {
    const currentVideoName = (videoData && videoData.filename) ? videoData.filename : "salah.mp4";
    const eyebrowText = `REVIEW / ${currentVideoName.toUpperCase()}`;

    const defaultSegments = [
        { id: 1, start: "00:00", end: "00:02", text: "Pakai tinted moisturizer ini", hasTypo: false },
        { id: 2, start: "00:02", end: "00:05", text: "Teksturnya ringan di kulit", hasTypo: false },
        { id: 3, start: "00:05", end: "00:08", text: "Gampang diblend, terasa natural", hasTypo: false },
        { id: 4, start: "00:08", end: "00:11", text: "engandung Gardenia Extract", hasTypo: true, typoWord: "engandung" },
        { id: 5, start: "00:11", end: "00:15", text: "Dan SPF 20 untuk harian", hasTypo: false }
    ];

    const segments = (videoData && videoData.segments && videoData.segments.length > 0)
        ? videoData.segments
        : defaultSegments;

    const typoCount = (videoData && videoData.typoCount !== undefined)
        ? videoData.typoCount
        : 1;

    const eventsCount = segments.length;
    const currentSegment = segments.find(s => s.id === (activeSegmentId || 4)) || segments[3] || segments[0];

    return (
        <section className="view-panel active">
            <div className="view-header">
                <div className="header-titles">
                    <span className="eyebrow-tag">{eyebrowText}</span>
                    <h1 className="page-title">Subtitle evidence, not guesswork.</h1>
                    <p className="page-subtitle">
                        Every segment is anchored to a timestamp; suspected typos always require confirmation.
                    </p>
                </div>
            </div>

            <div className="subtitle-review-tri-grid">
                {/* Column 1: Video Preview */}
                <div className="studio-card review-col-card">
                    <span className="eyebrow-tag" style={{ marginBottom: "14px" }}>VIDEO PREVIEW</span>

                    <div className="phone-mockup-canvas">
                        <span className="mockup-video-title">{currentVideoName}</span>

                        {useRealVideo ? (
                            <video
                                ref={videoRef}
                                src={`/api/video/${currentVideoName}`}
                                className="mockup-video-element"
                                playsInline
                                muted={false}
                            />
                        ) : (
                            <div className="mockup-bottle-art">
                                <div className="mockup-bottle-cap"></div>
                                <div className="mockup-bottle-body">
                                    <div className="mockup-bottle-stripe"></div>
                                </div>
                            </div>
                        )}

                        <div className="mockup-subtitle-overlay">
                            {currentSegment ? (currentSegment.hasTypo ? (
                                <span>
                                    {currentSegment.text.split(currentSegment.typoWord || "engandung")[0]}
                                    <span className="typo-mark-highlight">{currentSegment.typoWord || "engandung"}</span>
                                    {currentSegment.text.split(currentSegment.typoWord || "engandung")[1]}
                                </span>
                            ) : currentSegment.text) : "Tekstur ringan, gampang diblend"}
                        </div>
                    </div>

                    <div className="video-scrub-bar">
                        <div className="scrub-controls-row">
                            <button className="btn-play-pause" onClick={onTogglePlay}>
                                {isPlaying ? (
                                    <svg viewBox="0 0 24 24" fill="currentColor" width="16" height="16">
                                        <rect x="6" y="4" width="4" height="16"></rect>
                                        <rect x="14" y="4" width="4" height="16"></rect>
                                    </svg>
                                ) : (
                                    <svg viewBox="0 0 24 24" fill="currentColor" width="16" height="16">
                                        <polygon points="5 3 19 12 5 21 5 3"></polygon>
                                    </svg>
                                )}
                            </button>
                            <span className="scrub-timestamp">
                                {currentTime ? `00:${currentTime.toFixed(1).padStart(4, '0')}` : "00:08.5"} / {videoData?.durationStr || "00:15.3"}
                            </span>
                        </div>
                        <div className="scrub-track" onClick={onTogglePlay}>
                            <div
                                className="scrub-progress"
                                style={{ width: `${(currentTime ? (currentTime / (videoData?.duration || 15.3)) : 0.55) * 100}%` }}
                            ></div>
                        </div>
                    </div>
                </div>

                {/* Column 2: Extracted Subtitles */}
                <div className="studio-card review-col-card">
                    <span className="eyebrow-tag" style={{ marginBottom: "8px" }}>EXTRACTED SUBTITLES</span>
                    <h2 className="extracted-count-title">{eventsCount} timeline segments</h2>

                    <div className="timeline-cards-list">
                        {segments.map((seg) => {
                            const isSelected = activeSegmentId === seg.id;
                            const hasTypo = seg.hasTypo || seg.has_typo;

                            return (
                                <div
                                    key={seg.id}
                                    className={`segment-item-card ${isSelected ? "active-segment" : ""} ${hasTypo ? "has-typo-flag" : ""}`}
                                    onClick={() => onSelectSegment && onSelectSegment(seg)}
                                >
                                    <div className="segment-content-left">
                                        <span className="segment-timecode">{seg.start} – {seg.end}</span>
                                        <span className="segment-text">{seg.text}</span>
                                    </div>
                                    {hasTypo && (
                                        <div className="segment-warning-icon">!</div>
                                    )}
                                </div>
                            );
                        })}
                    </div>
                </div>

                {/* Column 3: Result Summary */}
                <div className="studio-card review-col-card">
                    <span className="eyebrow-tag" style={{ marginBottom: "20px" }}>RESULT SUMMARY</span>

                    <div className="summary-stat-group">
                        <div className="summary-big-number">{eventsCount}</div>
                        <div className="summary-stat-label">Subtitle events</div>
                    </div>

                    <div className="summary-stat-group">
                        <div className="summary-big-number" style={{ color: "#f59e0b" }}>{typoCount}</div>
                        <div className="summary-stat-label">Potential writing error</div>
                    </div>

                    <div>
                        <span className="badge-pill badge-pill-amber" style={{ padding: "6px 14px", marginBottom: "26px" }}>
                            NEEDS REVIEW
                        </span>
                    </div>

                    <div className="flagged-item-block">
                        <div className="flagged-timestamp-label">Flagged · 00:08.500</div>
                        <div className="flagged-word-display">“engandung”</div>
                        <div className="flagged-suggestion-text">Suggested: mengandung</div>
                    </div>

                    <div style={{ marginTop: "auto" }}>
                        <button className="btn-primary-purple btn-full-width" onClick={onInspectTypo}>
                            <span>Inspect typo →</span>
                        </button>
                    </div>
                </div>
            </div>
        </section>
    );
}

// ============================================================================
// SCREEN: TYPO INSPECTOR (Figma Screenshot 2)
// ============================================================================
function TypoInspectorScreen({ videoData, selectedIndex, onSelectSuggestion, onBack, onExport }) {
    const typo = (videoData && (videoData.typoDetail || videoData.typo_detail)) || {
        detectedWord: "engandung",
        timestamp: "00:08.500",
        timestampRange: "00:08.500 → 00:11.500",
        suggested: "mengandung",
        suggestions: [
            { num: "01", word: "mengandung" },
            { num: "02", word: "senandung" },
            { num: "03", word: "nandung" }
        ],
        originalContext: "“Tekstur ringan, gampang diblend, engandung Gardenia Extract, Vitamin E & SPF 20.”"
    };

    const detectedWord = typo.detectedWord || typo.detected_word || "engandung";
    const timestampRange = (typo.timestampRange || typo.timestamp_range || "00:08.500 → 00:11.500").replace("->", "→");
    const suggestions = typo.suggestions || [
        { num: "01", word: "mengandung" },
        { num: "02", word: "senandung" },
        { num: "03", word: "nandung" }
    ];
    const originalContext = typo.originalContext || typo.original_context || "“Tekstur ringan, gampang diblend, engandung Gardenia Extract, Vitamin E & SPF 20.”";
    const filename = (videoData && videoData.filename) || "salah.mp4";

    return (
        <section className="view-panel active">
            <div className="view-header">
                <div className="header-titles">
                    <span className="eyebrow-tag">WRITING ERROR / REVIEW</span>
                    <h1 className="page-title">One word. Full context.</h1>
                    <p className="page-subtitle">
                        Suggestions are advisory — no automatic edits to the original video.
                    </p>
                </div>
            </div>

            <div className="typo-inspector-grid">
                <div className="studio-card source-evidence-card">
                    <span className="eyebrow-tag" style={{ marginBottom: "14px" }}>SOURCE EVIDENCE</span>

                    <div className="phone-mockup-canvas" style={{ minHeight: "310px", margin: "16px 0" }}>
                        <span className="mockup-video-title">{filename}</span>
                        <div className="mockup-bottle-art">
                            <div className="mockup-bottle-cap"></div>
                            <div className="mockup-bottle-body">
                                <div className="mockup-bottle-stripe"></div>
                            </div>
                        </div>
                        <div className="mockup-subtitle-overlay">
                            Tekstur ringan, gampang diblend
                        </div>
                    </div>

                    <div className="source-evidence-footer" style={{ flexDirection: "column", alignItems: "flex-start", gap: "10px" }}>
                        <span className="evidence-timestamp">{timestampRange}</span>
                        <span className="badge-pill badge-pill-teal">
                            OCR + TYPO CHECK
                        </span>
                    </div>
                </div>

                <div className="studio-card">
                    <div style={{ marginBottom: "16px" }}>
                        <span className="badge-pill badge-pill-amber">
                            POTENTIAL TYPO
                        </span>
                    </div>

                    <div className="typo-label-small">Detected word</div>
                    <div className="typo-big-word" style={{ color: "#fb7185", margin: "8px 0 20px 0" }}>{detectedWord}</div>

                    <div className="typo-label-small" style={{ marginBottom: "12px" }}>Suggested corrections</div>

                    <div className="suggestions-grid-container">
                        {suggestions[0] && (
                            <button
                                type="button"
                                className={`suggestion-item-primary ${selectedIndex === 0 ? "active" : ""}`}
                                onClick={() => onSelectSuggestion(0)}
                            >
                                <span style={{ color: "#34d399", fontWeight: 700 }}>{suggestions[0].num || "01"}</span>
                                <span>{suggestions[0].word}</span>
                            </button>
                        )}

                        <div className="suggestions-secondary-row">
                            {suggestions[1] && (
                                <button
                                    type="button"
                                    className={`suggestion-item-secondary ${selectedIndex === 1 ? "active" : ""}`}
                                    onClick={() => onSelectSuggestion(1)}
                                >
                                    <span style={{ color: "#64748b" }}>{suggestions[1].num || "02"}</span>
                                    <span>{suggestions[1].word}</span>
                                </button>
                            )}
                            {suggestions[2] && (
                                <button
                                    type="button"
                                    className={`suggestion-item-secondary ${selectedIndex === 2 ? "active" : ""}`}
                                    onClick={() => onSelectSuggestion(2)}
                                >
                                    <span style={{ color: "#64748b" }}>{suggestions[2].num || "03"}</span>
                                    <span>{suggestions[2].word}</span>
                                </button>
                            )}
                        </div>
                    </div>

                    <div className="typo-label-small" style={{ marginBottom: "10px" }}>Original subtitle context</div>
                    <div className="original-context-text">
                        {originalContext}
                    </div>

                    <div className="inspector-actions-row">
                        <button className="btn-secondary-dark" onClick={onBack}>
                            <span>Back to review ←</span>
                        </button>
                        <button className="btn-primary-purple" style={{ flex: 1 }} onClick={onExport}>
                            <span>Go to export →</span>
                        </button>
                    </div>
                </div>
            </div>
        </section>
    );
}

// ============================================================================
// SCREEN: EXPORT CENTER (Figma Screenshot 3)
// ============================================================================
function ExportCenterScreen({ videoData, onDownload, onDone }) {
    const baseName = (videoData && videoData.filename ? videoData.filename : "salah.mp4").replace(".mp4", "");

    return (
        <section className="view-panel active">
            <div className="view-header">
                <div className="header-titles">
                    <span className="eyebrow-tag">EXPORT / RESULTS</span>
                    <h1 className="page-title">Your analysis, your format.</h1>
                    <p className="page-subtitle">
                        Export artifacts from the local pipeline. Mocked Figma interactions do not generate real files.
                    </p>
                </div>
            </div>

            <div className="export-tri-grid">
                <div className="studio-card export-format-card" onClick={() => onDownload("txt")}>
                    <div className="export-format-badge badge-txt">TXT</div>
                    <h3 className="export-card-title">TXT export</h3>
                    <p className="export-card-subtitle">Human-readable subtitle transcript</p>
                    <p className="export-card-note">Default format · includes typo report</p>
                    <div className="export-card-bottom">
                        <span className="badge-pill badge-pill-green">DEFAULT</span>
                    </div>
                </div>

                <div className="studio-card export-format-card" onClick={() => onDownload("json")}>
                    <div className="export-format-badge badge-json">JSON</div>
                    <h3 className="export-card-title">JSON export</h3>
                    <p className="export-card-subtitle">Structured subtitles + analysis</p>
                    <p className="export-card-note">Machine-readable metadata and typo details</p>
                    <div className="export-card-bottom">
                        <span className="badge-pill badge-pill-gray">OPTIONAL</span>
                    </div>
                </div>

                <div className="studio-card export-format-card" onClick={() => onDownload("srt")}>
                    <div className="export-format-badge badge-srt">SRT</div>
                    <h3 className="export-card-title">SRT export</h3>
                    <p className="export-card-subtitle">Timed subtitle captions</p>
                    <p className="export-card-note">Compatible with editing and subtitle workflows</p>
                    <div className="export-card-bottom">
                        <span className="badge-pill badge-pill-gray">OPTIONAL</span>
                    </div>
                </div>
            </div>

            <div className="studio-card file-preview-bottom-card" style={{ marginTop: "24px" }}>
                <div>
                    <span className="eyebrow-tag" style={{ marginBottom: "10px" }}>FILE OUTPUT PREVIEW</span>
                    <div className="preview-main-filename">{baseName}_subtitles.txt</div>
                    <div className="preview-companion-files">
                        {baseName}_subtitles.json · {baseName}_subtitles.srt · {baseName}_typo_report.json
                    </div>
                    <div className="preview-destination-note">
                        Output destination is user-configured; CLI defaults to ./output
                    </div>
                </div>

                <div>
                    <button className="btn-primary-purple" onClick={onDone}>
                        <span>Done · overview →</span>
                    </button>
                </div>
            </div>
        </section>
    );
}

// ============================================================================
// SCREEN: ROADMAP (Figma Screenshot 4)
// ============================================================================
function RoadmapScreen() {
    const phases = [
        {
            num: "PHASE 01",
            badgeClass: "badge-phase-green",
            title: "OCR + Subtitle QA",
            desc: "Available in current Python CLI",
            status: "complete"
        },
        {
            num: "PHASE 02",
            badgeClass: "badge-phase-brown",
            title: "Audio transcription / ASR",
            desc: "Planned: speech-to-text with timestamps",
            status: "planned"
        },
        {
            num: "PHASE 03",
            badgeClass: "badge-phase-brown",
            title: "Multimodal alignment",
            desc: "Planned: compare visual text and spoken words",
            status: "planned"
        },
        {
            num: "PHASE 04",
            badgeClass: "badge-phase-brown",
            title: "Creative evaluation",
            desc: "Exploratory research, not a shipped feature",
            status: "planned"
        }
    ];

    return (
        <section className="view-panel active">
            <div className="view-header">
                <div className="header-titles">
                    <span className="eyebrow-tag">ROADMAP / NOT ENABLED</span>
                    <h1 className="page-title">What comes after OCR.</h1>
                    <p className="page-subtitle">
                        Future multimodal capabilities are separate from the current CLI's verified functionality.
                    </p>
                </div>
            </div>

            <div className="roadmap-phases-container">
                {phases.map(p => (
                    <div key={p.num} className="roadmap-phase-card">
                        <div className="phase-card-left">
                            <span className={`phase-pill-badge ${p.badgeClass}`}>{p.num}</span>
                            <div className="phase-text-group">
                                <div className="phase-title">{p.title}</div>
                                <div className="phase-desc">{p.desc}</div>
                            </div>
                        </div>
                        <div className="phase-status-icon-wrapper">
                            {p.status === "complete" ? (
                                <span className="phase-checkmark-icon">✓</span>
                            ) : (
                                <span className="phase-circle-ring-icon"></span>
                            )}
                        </div>
                    </div>
                ))}
            </div>
        </section>
    );
}

// ============================================================================
// MOUNT REACT KE DOM
// ============================================================================
const rootElement = document.getElementById("root");
if (rootElement) {
    const root = ReactDOM.createRoot(rootElement);
    root.render(<App />);
}
