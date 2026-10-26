import React from 'react';

export default function Overview({ onSelectVideo, onNewAnalysis }) {
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

      {/* KPI Quad Grid (4 stat cards in a single row) */}
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

      {/* Dual Grid: Recent Analysis & The Workflow */}
      <div className="overview-dual-grid">
        {/* Left: Recent Analysis */}
        <div className="studio-card recent-analysis-card">
          <div className="card-head">
            <h2 className="card-title">Recent analysis</h2>
            <p className="card-desc">Real sample results from current CLI engine</p>
          </div>

          <div className="video-item-list">
            {/* Item 1: salah.mp4 */}
            <div className="video-item-row" onClick={() => onSelectVideo && onSelectVideo("salah.mp4")}>
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

            {/* Item 2: salah2.mp4 */}
            <div className="video-item-row" onClick={() => onSelectVideo && onSelectVideo("salah2.mp4")}>
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

            {/* Item 3: benar.mp4 */}
            <div className="video-item-row" onClick={() => onSelectVideo && onSelectVideo("benar.mp4")}>
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
            <button className="link-btn" onClick={() => onSelectVideo && onSelectVideo("salah.mp4")}>
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
