import React from 'react';

export default function TypoInspector({
  videoData,
  selectedIndex,
  onSelectSuggestion,
  onBack,
  onExport
}) {
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
        {/* LEFT COLUMN: SOURCE EVIDENCE */}
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

        {/* RIGHT COLUMN: POTENTIAL TYPO */}
        <div className="studio-card">
          <div style={{ marginBottom: "16px" }}>
            <span className="badge-pill badge-pill-amber">
              POTENTIAL TYPO
            </span>
          </div>

          <div className="typo-label-small">Detected word</div>
          <div className="typo-big-word" style={{ color: "#fb7185", margin: "8px 0 20px 0" }}>{detectedWord}</div>

          <div className="typo-label-small" style={{ marginBottom: "12px" }}>Suggested corrections</div>

          {/* Suggestions Layout: Top Primary full width, Bottom Secondary 2 columns */}
          <div className="suggestions-grid-container">
            {suggestions[0] && (
              <button
                type="button"
                className={`suggestion-item-primary ${selectedIndex === 0 ? "active" : ""}`}
                onClick={() => onSelectSuggestion && onSelectSuggestion(0)}
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
                  onClick={() => onSelectSuggestion && onSelectSuggestion(1)}
                >
                  <span style={{ color: "#64748b" }}>{suggestions[1].num || "02"}</span>
                  <span>{suggestions[1].word}</span>
                </button>
              )}
              {suggestions[2] && (
                <button
                  type="button"
                  className={`suggestion-item-secondary ${selectedIndex === 2 ? "active" : ""}`}
                  onClick={() => onSelectSuggestion && onSelectSuggestion(2)}
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
