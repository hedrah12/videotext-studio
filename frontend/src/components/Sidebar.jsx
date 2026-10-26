import React from 'react';

export default function Sidebar({ currentView, setCurrentView }) {
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
      {/* Brand Logo & Name */}
      <div className="brand" onClick={() => setCurrentView("overview")} style={{ cursor: "pointer" }}>
        <div className="brand-logo">
          <span>V</span>
        </div>
        <div className="brand-text">
          <span className="brand-title">videotext</span>
          <span className="brand-sub">Studio / v1.0</span>
        </div>
      </div>

      {/* Main Navigation */}
      <div className="nav-section-title">WORKSPACE</div>
      <nav className="nav-menu">
        {navItems.map((item) => (
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

      {/* Experimental Feature */}
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

      {/* User Profile Card at Bottom */}
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
