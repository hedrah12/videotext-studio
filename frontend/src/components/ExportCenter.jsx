import React from 'react';

export default function ExportCenter({ videoData, onDownload, onDone }) {
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

      {/* 3 Format Cards in a Row */}
      <div className="export-tri-grid">
        {/* TXT */}
        <div className="studio-card export-format-card" onClick={() => onDownload && onDownload("txt")}>
          <div className="export-format-badge badge-txt">TXT</div>
          <h3 className="export-card-title">TXT export</h3>
          <p className="export-card-subtitle">Human-readable subtitle transcript</p>
          <p className="export-card-note">Default format · includes typo report</p>
          <div className="export-card-bottom">
            <span className="badge-pill badge-pill-green">
              DEFAULT
            </span>
          </div>
        </div>

        {/* JSON */}
        <div className="studio-card export-format-card" onClick={() => onDownload && onDownload("json")}>
          <div className="export-format-badge badge-json">JSON</div>
          <h3 className="export-card-title">JSON export</h3>
          <p className="export-card-subtitle">Structured subtitles + analysis</p>
          <p className="export-card-note">Machine-readable metadata and typo details</p>
          <div className="export-card-bottom">
            <span className="badge-pill badge-pill-gray">
              OPTIONAL
            </span>
          </div>
        </div>

        {/* SRT */}
        <div className="studio-card export-format-card" onClick={() => onDownload && onDownload("srt")}>
          <div className="export-format-badge badge-srt">SRT</div>
          <h3 className="export-card-title">SRT export</h3>
          <p className="export-card-subtitle">Timed subtitle captions</p>
          <p className="export-card-note">Compatible with editing and subtitle workflows</p>
          <div className="export-card-bottom">
            <span className="badge-pill badge-pill-gray">
              OPTIONAL
            </span>
          </div>
        </div>
      </div>

      {/* Bottom Card: File Output Preview */}
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
