import React, { useState, useEffect, useRef, useMemo } from 'react';
import Sidebar from './components/Sidebar';
import SubtitleReview from './components/SubtitleReview';
import TypoInspector from './components/TypoInspector';
import ExportCenter from './components/ExportCenter';
import Roadmap from './components/Roadmap';
import Overview from './components/Overview';
import ImportVideos from './components/ImportVideos';
import OcrSettings from './components/OcrSettings';
import Processing from './components/Processing';

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

export default function App() {
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
      {/* Sidebar matching Figma */}
      <Sidebar currentView={currentView} setCurrentView={setCurrentView} />

      {/* Main Viewport */}
      <main className="main-viewport">
        {/* Topbar with exact Breadcrumb and Pill Badge */}
        <header className="topbar">
          <div className="breadcrumb">
            <span className="bc-root">WORKSPACE</span>
            <span className="bc-sep">/</span>
            <span className="bc-current">{breadcrumb}</span>
          </div>
          <div className="topbar-badge">{badge}</div>
        </header>

        {/* View Switcher */}
        <div className="content-container">
          {currentView === "overview" && (
            <Overview
              samples={DEFAULT_SAMPLES}
              onSelectVideo={(k) => {
                handleSelectSample(k);
                setCurrentView("subtitle-review");
              }}
              onNewAnalysis={() => setCurrentView("import")}
            />
          )}

          {currentView === "import" && (
            <ImportVideos
              samples={DEFAULT_SAMPLES}
              selectedKey={selectedVideoKey}
              onSelectSample={(k, name) => {
                handleSelectSample(k, name);
              }}
              onContinueToSettings={() => setCurrentView("ocr-settings")}
              onStartProcessing={() => setCurrentView("ocr-settings")}
              showToast={showToast}
            />
          )}

          {currentView === "ocr-settings" && (
            <OcrSettings
              ocrOptions={ocrOptions}
              onSaveAndRun={(opts) => {
                if (opts) setOcrOptions(opts);
                setCurrentView("processing");
              }}
            />
          )}

          {currentView === "processing" && (
            <Processing
              videoName={videoData ? videoData.filename : selectedVideoKey}
              ocrOptions={ocrOptions}
              onFinish={handleProcessingFinish}
              onError={(msg) => showToast(`Error: ${msg}`)}
            />
          )}

          {currentView === "subtitle-review" && (
            <SubtitleReview
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
            <TypoInspector
              videoData={videoData}
              selectedIndex={selectedSuggestionIndex}
              onSelectSuggestion={setSelectedSuggestionIndex}
              onBack={() => setCurrentView("subtitle-review")}
              onExport={() => setCurrentView("export-center")}
            />
          )}

          {currentView === "export-center" && (
            <ExportCenter
              videoData={videoData}
              onDownload={handleDownloadExport}
              onDone={() => setCurrentView("overview")}
            />
          )}

          {currentView === "roadmap" && <Roadmap />}
        </div>
      </main>

      {/* Toast Notification */}
      {toastVisible && (
        <div className="toast-notification" style={{ display: "block" }}>
          {toastMessage}
        </div>
      )}
    </div>
  );
}
