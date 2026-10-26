import React from 'react';

export default function Roadmap() {
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
        {phases.map((p) => (
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
