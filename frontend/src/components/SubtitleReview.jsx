import React from 'react';

export default function SubtitleReview({
  videoData,
  activeSegmentId,
  onSelectSegment,
  onInspectTypo,
  isPlaying,
  onTogglePlay,
  currentTime,
  useRealVideo,
  setUseRealVideo,
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

          {/* Video Scrub Bar */}
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

          {/* Stat 1 */}
          <div className="summary-stat-group">
            <div className="summary-big-number">{eventsCount}</div>
            <div className="summary-stat-label">Subtitle events</div>
          </div>

          {/* Stat 2 */}
          <div className="summary-stat-group">
            <div className="summary-big-number" style={{ color: "#f59e0b" }}>{typoCount}</div>
            <div className="summary-stat-label">Potential writing error</div>
          </div>

          {/* Badge */}
          <div>
            <span className="badge-pill badge-pill-amber" style={{ padding: "6px 14px", marginBottom: "26px" }}>
              NEEDS REVIEW
            </span>
          </div>

          {/* Flagged Item Details */}
          <div className="flagged-item-block">
            <div className="flagged-timestamp-label">Flagged · 00:08.500</div>
            <div className="flagged-word-display">“engandung”</div>
            <div className="flagged-suggestion-text">Suggested: mengandung</div>
          </div>

          {/* Action Button */}
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
