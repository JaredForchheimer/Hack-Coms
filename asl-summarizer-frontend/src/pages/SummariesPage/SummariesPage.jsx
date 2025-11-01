import React, { useContext } from 'react'
import { Link } from 'react-router-dom'
import { DataContext } from '../../context/DataContext'
import Button from '../../components/common/Button/Button'
import '../SourcesPage/SourcesPage.css'
import './SummariesPage.css'

const SummariesPage = () => {
  const { summaries, files } = useContext(DataContext)

  const getSourceFile = (sourceId) => {
    return files.find(file => file.id === sourceId)
  }

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  return (
    <div className="sources-page">
      <header className="page-header">
        <div className="container">
          <div className="page-header__content">
            <Link to="/" className="page-header__back">
              ← Back to Home
            </Link>
            <h1 className="page-header__title">Summaries</h1>
            <p className="page-header__subtitle">
              AI-generated summaries from your validated content
            </p>
          </div>
        </div>
      </header>

      <main className="page-main">
        <div className="container">
          {summaries.length === 0 ? (
            <div className="summaries-page__empty">
              <div className="placeholder-content">
                <div className="placeholder-content__icon">📝</div>
                <h2 className="placeholder-content__title">No Summaries Yet</h2>
                <p className="placeholder-content__description">
                  Upload and validate content in the Sources page to generate summaries.
                </p>
                <Link to="/sources">
                  <Button variant="primary">
                    Upload Content
                  </Button>
                </Link>
              </div>
            </div>
          ) : (
            <div className="summaries-page__content">
              <div className="summaries-page__header">
                <h2>Generated Summaries ({summaries.length})</h2>
                <Link to="/sources">
                  <Button variant="secondary">
                    Add More Content
                  </Button>
                </Link>
              </div>

              <div className="summaries-page__grid">
                {summaries.map((summary) => {
                  const sourceFile = getSourceFile(summary.sourceId)
                  return (
                    <div key={summary.id} className="summary-card">
                      <div className="summary-card__header">
                        <h3 className="summary-card__title">{summary.title}</h3>
                        <div className="summary-card__meta">
                          <span className="summary-card__source">
                            Source: {sourceFile?.name || 'Unknown'}
                          </span>
                          <span className="summary-card__date">
                            {formatDate(summary.generatedAt)}
                          </span>
                        </div>
                      </div>

                      <div className="summary-card__content">
                        <p>{summary.content}</p>
                      </div>

                      <div className="summary-card__footer">
                        <div className="summary-card__stats">
                          <span className="summary-card__word-count">
                            {summary.wordCount} words
                          </span>
                          {sourceFile && (
                            <span className="summary-card__type">
                              {sourceFile.type}
                            </span>
                          )}
                        </div>
                        <div className="summary-card__actions">
                          <Button variant="ghost" size="small">
                            View Source
                          </Button>
                          <Button variant="primary" size="small">
                            Create ASL Video
                          </Button>
                        </div>
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}

export default SummariesPage