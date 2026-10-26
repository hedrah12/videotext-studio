import React, { useState } from 'react';

export default function OcrSettings({ onSaveAndRun }) {
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
        {/* Left Column: OCR Configuration Card */}
        <div className="studio-card ocr-config-card">
          <h2 className="card-title" style={{ fontSize: "18px", marginBottom: "22px" }}>
            OCR configuration
          </h2>

          {/* Field 1: Recognition Engine */}
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

          {/* Field 2: Region of Interest / ROI */}
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

          {/* Field 3: Frame Sampling */}
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

          {/* Field 4: Enable Bilingual Typo Checker */}
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

          {/* Field 5: Custom Brand Whitelist */}
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

        {/* Right Column: ROI Preview Card */}
        <div className="studio-card roi-preview-card">
          <span className="eyebrow-tag" style={{ marginBottom: "14px" }}>ROI PREVIEW</span>

          {/* Phone Frame Mockup */}
          <div className="device-mockup-frame">
            <div className="frame-top-bar">
              <span className="frame-tag">FRAME 00:08.500</span>
            </div>
            <div className="phone-canvas">
              {/* Silhouette Cosmetic Bottle Graphic */}
              <div className="bottle-graphic-container">
                <div className="bottle-cap"></div>
                <div className="bottle-body">
                  <div className="bottle-label-strip"></div>
                </div>
              </div>

              {/* Translucent Pink/Purple ROI Box */}
              <div className="roi-overlay-box">
                <span className="roi-overlay-badge-pink">ROI: 15–80%</span>
              </div>

              {/* Subtitle text preview at bottom */}
              <div className="phone-subtitle-banner">
                Tekstur ringan, gampang diblend
              </div>
            </div>
          </div>

          {/* Subtitle Region Info */}
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
