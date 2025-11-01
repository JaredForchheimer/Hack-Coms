import React from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import Button from '../../components/common/Button/Button'
import './HomePage.css'

const HomePage = () => {
  console.log('HomePage component rendering...')
  const { user, logout } = useAuth()
  console.log('HomePage user:', user)

  const handleLogout = async () => {
    try {
      await logout()
    } catch (error) {
      console.error('Logout failed:', error)
    }
  }

  const navigationCards = [
    {
      id: 'sources',
      title: 'Sources',
      description: 'Upload and organize your articles and videos into folders',
      icon: '📁',
      path: '/sources',
      color: 'blue'
    },
    {
      id: 'summaries',
      title: 'Summaries',
      description: 'Generate summaries from your stored content',
      icon: '📝',
      path: '/summaries',
      color: 'green'
    },
    {
      id: 'translation',
      title: 'Real-time Translation',
      description: 'Watch ASL interpretations of your summaries',
      icon: '🤟',
      path: '/translation',
      color: 'purple'
    },
    {
      id: 'community',
      title: 'Community',
      description: 'Share and discover ASL summary videos',
      icon: '👥',
      path: '/community',
      color: 'orange'
    }
  ]

  return (
    <div className="home-page">
      <header className="home-header">
        <div className="container">
          <div className="home-header__content">
            <div className="home-header__brand">
              <h1 className="home-header__title">ASL Article Summarizer</h1>
              <p className="home-header__subtitle">
                Welcome back, {user?.username || user?.email}!
              </p>
            </div>
            <Button
              variant="secondary"
              size="medium"
              onClick={handleLogout}
              className="home-header__logout"
            >
              Sign Out
            </Button>
          </div>
        </div>
      </header>

      <main className="home-main">
        <div className="container">
          <section className="home-intro">
            <h2 className="home-intro__title">
              Transform Articles into Accessible ASL Content
            </h2>
            <p className="home-intro__description">
              Upload your articles and videos, generate intelligent summaries, 
              and access ASL interpretations to make content more accessible for everyone.
            </p>
          </section>

          <section className="home-navigation">
            <div className="navigation-grid">
              {navigationCards.map((card) => (
                <Link
                  key={card.id}
                  to={card.path}
                  className={`navigation-card navigation-card--${card.color}`}
                >
                  <div className="navigation-card__icon">
                    {card.icon}
                  </div>
                  <div className="navigation-card__content">
                    <h3 className="navigation-card__title">
                      {card.title}
                    </h3>
                    <p className="navigation-card__description">
                      {card.description}
                    </p>
                  </div>
                  <div className="navigation-card__arrow">
                    →
                  </div>
                </Link>
              ))}
            </div>
          </section>

          <section className="home-features">
            <h3 className="home-features__title">Key Features</h3>
            <div className="features-grid">
              <div className="feature-item">
                <div className="feature-item__icon">🗂️</div>
                <h4 className="feature-item__title">Smart Organization</h4>
                <p className="feature-item__description">
                  Create folders and organize your content with drag-and-drop functionality
                </p>
              </div>
              <div className="feature-item">
                <div className="feature-item__icon">🤖</div>
                <h4 className="feature-item__title">AI Summaries</h4>
                <p className="feature-item__description">
                  Generate intelligent summaries from multiple sources automatically
                </p>
              </div>
              <div className="feature-item">
                <div className="feature-item__icon">🎥</div>
                <h4 className="feature-item__title">ASL Translation</h4>
                <p className="feature-item__description">
                  Watch real-time ASL interpretations of your summarized content
                </p>
              </div>
              <div className="feature-item">
                <div className="feature-item__icon">🌐</div>
                <h4 className="feature-item__title">Community Sharing</h4>
                <p className="feature-item__description">
                  Share your ASL videos with the community and discover others' content
                </p>
              </div>
            </div>
          </section>
        </div>
      </main>

      <footer className="home-footer">
        <div className="container">
          <p className="home-footer__text">
            Making content accessible through technology and community
          </p>
        </div>
      </footer>
    </div>
  )
}

export default HomePage