import React, { useRef, useState } from 'react';

export default function ImportVideos({ selectedKey, onSelectSample, onStartProcessing, onContinueToSettings, showToast }) {
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
        {/* Left Column: Dropzone + Queue */}
        <div className="import-left-pane">
          {/* Dropzone */}
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

          {/* Files in Queue */}
          <div className="files-queue-section" style={{ marginTop: "28px" }}>
            <span className="eyebrow-tag" style={{ marginBottom: "12px" }}>FILES IN QUEUE</span>
            <div className="queue-items-list">
              {/* Render Uploaded Files */}
              {uploadedFiles.map(uf => (
                <div
                  key={uf.key}
                  className={`queue-item-row ${selectedKey === uf.key ? "active-row" : ""}`}
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

              {/* Queue Item 1 */}
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

              {/* Queue Item 2 */}
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

        {/* Right Column: Analysis Recipe */}
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
