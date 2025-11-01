import React from 'react'
import { Link } from 'react-router-dom'
import '../SourcesPage/SourcesPage.css'

const TranslationPage = () => {
  return (
    <div className="sources-page">
      <header className="page-header">
        <div className="container">
          <div className="page-header__content">
            <Link to="/" className="page-header__back">
              ← Back to Home
            </Link>
            <h1 className="page-header__title">Real-time Translation</h1>
            <p className="page-header__subtitle">
              Watch ASL interpretations of your summaries
            </p>
          </div>
        </div>
      </header>

      <main className="page-main">
        <div className="container">
          <div className="placeholder-content">
            <div className="placeholder-content__icon">🤟</div>
            <h2 className="placeholder-content__title">Real-time Translation Page</h2>
            <p className="placeholder-content__description">
              This page will feature:
            </p>
            <ul className="placeholder-content__features">
              <li>Folder selection for ASL translation</li>
              <li>Custom ASL video player with controls</li>
              <li>Real-time translation playback</li>
              <li>Speed and accessibility controls</li>
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

export default TranslationPage