import React from 'react'
import { Link } from 'react-router-dom'
import '../SourcesPage/SourcesPage.css'

const CommunityPage = () => {
  return (
    <div className="sources-page">
      <header className="page-header">
        <div className="container">
          <div className="page-header__content">
            <Link to="/" className="page-header__back">
              ← Back to Home
            </Link>
            <h1 className="page-header__title">Community</h1>
            <p className="page-header__subtitle">
              Share and discover ASL summary videos
            </p>
          </div>
        </div>
      </header>

      <main className="page-main">
        <div className="container">
          <div className="placeholder-content">
            <div className="placeholder-content__icon">👥</div>
            <h2 className="placeholder-content__title">Community Page</h2>
            <p className="placeholder-content__description">
              This page will feature:
            </p>
            <ul className="placeholder-content__features">
              <li>Instagram-like feed of ASL summary videos</li>
              <li>Post creation button in top right corner</li>
              <li>Like and interaction features</li>
              <li>Community sharing and discovery</li>
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

export default CommunityPage