import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import Button from '../../components/common/Button/Button'
import LoadingSpinner from '../../components/common/LoadingSpinner/LoadingSpinner'
import mediaService from '../../services/mediaService'
import '../SourcesPage/SourcesPage.css'
import './SummariesPage.css'

const SummariesPage = () => {
  const [summaries, setSummaries] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchSummaries()
  }, [])

  const fetchSummaries = async () => {
    try {
      setLoading(true)
      setError(null)
      
      const result = await mediaService.getSummaries()
      
      if (result.success) {
        setSummaries(result.summaries || [])
      } else {
        setError(result.error || 'Failed to fetch summaries')
      }
    } catch (err) {
      setError('Failed to fetch summaries: ' + err.message)
      console.error('Error fetching summaries:', err)
    } finally {
      setLoading(false)
    }
  }

  const getSourceFile = (summary) => {
    // Since we now get source info from the summary response,
    // use the embedded source data
    return {
      id: summary.text_source_id,
      name: summary.source_title || 'Unknown Source',
      type: 'unknown' // This could be enhanced by including type in backend response
    }
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
          {loading ? (
            <div className="summaries-page__loading">
              <LoadingSpinner />
              <p>Loading summaries...</p>
            </div>
          ) : error ? (
            <div className="summaries-page__error">
              <div className="placeholder-content">
                <div className="placeholder-content__icon">❌</div>
                <h2 className="placeholder-content__title">Error Loading Summaries</h2>
                <p className="placeholder-content__description">{error}</p>
                <Button variant="primary" onClick={fetchSummaries}>
                  Try Again
                </Button>
              </div>
            </div>
          ) : summaries.length === 0 ? (
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
                <div className="summaries-page__actions">
                  <Button variant="ghost" onClick={fetchSummaries}>
                    Refresh
                  </Button>
                  <Link to="/sources">
                    <Button variant="secondary">
                      Add More Content
                    </Button>
                  </Link>
                </div>
              </div>

              <div className="summaries-page__grid">
                {summaries.map((summary) => {
                  const sourceFile = getSourceFile(summary)
                  const wordCount = summary.metadata?.word_count || summary.content.split(' ').length
                  return (
                    <div key={summary.id} className="summary-card">
                      <div className="summary-card__header">
                        <h3 className="summary-card__title">{summary.title}</h3>
                        <div className="summary-card__meta">
                          <span className="summary-card__source">
                            Source: {sourceFile?.name || 'Unknown'}
                          </span>
                          <span className="summary-card__date">
                            {formatDate(summary.created_at)}
                          </span>
                        </div>
                      </div>

                      <div className="summary-card__content">
                        <p>{summary.content}</p>
                      </div>

                      <div className="summary-card__footer">
                        <div className="summary-card__stats">
                          <span className="summary-card__word-count">
                            {wordCount} words
                          </span>
                          <span className="summary-card__type">
                            {summary.summary_type}
                          </span>
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