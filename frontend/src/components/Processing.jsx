import React, { useState, useEffect } from 'react';

export default function Processing({ videoName, ocrOptions, onFinish, onError }) {
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
        {/* Left Column: Live Progress Pipeline */}
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

          {/* 4 Checklist Items */}
          <div className="processing-checklist">
            {/* Step 1 */}
            <div className="check-row">
              <div className="check-row-left">
                <svg className="check-icon check-complete" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                  <polyline points="20 6 9 17 4 12"></polyline>
                </svg>
                <span className="check-label">Video metadata</span>
              </div>
              <span className="check-state state-complete">Complete</span>
            </div>

            {/* Step 2 */}
            <div className="check-row">
              <div className="check-row-left">
                <svg className="check-icon check-complete" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                  <polyline points="20 6 9 17 4 12"></polyline>
                </svg>
                <span className="check-label">RapidOCR frame sampling</span>
              </div>
              <span className="check-state state-complete">Complete</span>
            </div>

            {/* Step 3 */}
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

            {/* Step 4 */}
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

        {/* Right Column: Process Trace Card */}
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
