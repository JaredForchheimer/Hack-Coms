import React from 'react'
import { Link } from 'react-router-dom'
import './SourcesPage.css'

const SourcesPage = () => {
  return (
    <div className="sources-page">
      <header className="page-header">
        <div className="container">
          <div className="page-header__content">
            <Link to="/" className="page-header__back">
              ← Back to Home
            </Link>
            <h1 className="page-header__title">Sources</h1>
            <p className="page-header__subtitle">
              Upload and organize your articles and videos
            </p>
          </div>
        </div>
      </header>

      <main className="page-main">
        <div className="container">
          <div className="placeholder-content">
            <div className="placeholder-content__icon">📁</div>
            <h2 className="placeholder-content__title">Sources Page</h2>
            <p className="placeholder-content__description">
              This page will feature:
            </p>
            <ul className="placeholder-content__features">
              <li>Folder tree view with drag-and-drop functionality</li>
              <li>File upload for PDFs and videos</li>
              <li>Folder creation and management</li>
              <li>File organization and search</li>
            </ul>
            <p className="placeholder-content__note">
              Coming soon! This will be implemented in the next development phase.
            </p>
          </div>
        </div>
      </main>
    </div>
  )
}

export default SourcesPage