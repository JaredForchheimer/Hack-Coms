import React, { useState, useContext } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { DataContext } from '../../context/DataContext'
import MediaUpload from '../../components/common/MediaUpload/MediaUpload'
import ValidationResult from '../../components/common/ValidationResult/ValidationResult'
import LoadingSpinner from '../../components/common/LoadingSpinner/LoadingSpinner'
import Button from '../../components/common/Button/Button'
import mediaService from '../../services/mediaService'
import './SourcesPage.css'

const SourcesPage = () => {
  const navigate = useNavigate()
  const { addFile, addSummary } = useContext(DataContext)
  
  const [isProcessing, setIsProcessing] = useState(false)
  const [currentStep, setCurrentStep] = useState('upload') // 'upload', 'validating', 'validation-result', 'generating-summary'
  const [extractedContent, setExtractedContent] = useState(null)
  const [validationResult, setValidationResult] = useState(null)
  const [error, setError] = useState(null)

  const handleMediaUpload = async (uploadData) => {
    setIsProcessing(true)
    setError(null)
    setCurrentStep('validating')

    try {
      let result
      
      if (uploadData.type === 'url') {
        result = await mediaService.extractTextFromUrl(uploadData.data)
      } else {
        result = await mediaService.processFile(uploadData.data)
      }

      if (!result.success) {
        throw new Error(result.error)
      }

      setExtractedContent(result)

      // Validate the extracted content
      const contentToValidate = result.transcript || result.content
      const validation = await mediaService.validateContent(contentToValidate)

      if (!validation.success) {
        throw new Error(validation.error)
      }

      setValidationResult(validation)
      setCurrentStep('validation-result')
    } catch (err) {
      setError(err.message)
      setCurrentStep('upload')
    } finally {
      setIsProcessing(false)
    }
  }

  const handleAcceptContent = async () => {
    setIsProcessing(true)
    setCurrentStep('generating-summary')

    try {
      const contentToSummarize = extractedContent.transcript || extractedContent.content
      const summaryResult = await mediaService.generateSummary(
        contentToSummarize,
        extractedContent.title
      )

      if (!summaryResult.success) {
        throw new Error(summaryResult.error)
      }

      // Add the source file to data context
      const sourceFile = {
        id: Date.now().toString(),
        name: extractedContent.title,
        type: extractedContent.type,
        content: contentToSummarize,
        uploadedAt: new Date().toISOString(),
        validated: true,
        validationResult
      }
      addFile(sourceFile)

      // Add the summary to data context
      const summary = {
        id: Date.now().toString() + '_summary',
        sourceId: sourceFile.id,
        title: `Summary: ${extractedContent.title}`,
        content: summaryResult.summary,
        wordCount: summaryResult.wordCount,
        generatedAt: summaryResult.generatedAt
      }
      addSummary(summary)

      // Navigate to summaries page
      navigate('/summaries')
    } catch (err) {
      setError(err.message)
      setCurrentStep('validation-result')
    } finally {
      setIsProcessing(false)
    }
  }

  const handleRejectContent = () => {
    setCurrentStep('upload')
    setExtractedContent(null)
    setValidationResult(null)
    setError(null)
  }

  const resetUpload = () => {
    setCurrentStep('upload')
    setExtractedContent(null)
    setValidationResult(null)
    setError(null)
    setIsProcessing(false)
  }

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
              Upload and validate your articles and videos
            </p>
          </div>
        </div>
      </header>

      <main className="page-main">
        <div className="container">
          {error && (
            <div className="sources-page__error">
              <p>❌ {error}</p>
              <Button variant="secondary" onClick={resetUpload}>
                Try Again
              </Button>
            </div>
          )}

          {currentStep === 'upload' && (
            <div className="sources-page__upload">
              <MediaUpload
                onUpload={handleMediaUpload}
                isLoading={isProcessing}
              />
            </div>
          )}

          {currentStep === 'validating' && (
            <div className="sources-page__validating">
              <LoadingSpinner />
              <h3>Processing and Validating Content...</h3>
              <p>Extracting text and checking for inappropriate content</p>
            </div>
          )}

          {currentStep === 'validation-result' && validationResult && (
            <div className="sources-page__validation">
              <div className="sources-page__content-preview">
                <h3>Extracted Content:</h3>
                <div className="sources-page__content-card">
                  <h4>{extractedContent.title}</h4>
                  <p className="sources-page__content-type">
                    Type: {extractedContent.type}
                  </p>
                  <div className="sources-page__content-text">
                    {(extractedContent.transcript || extractedContent.content).substring(0, 300)}
                    {(extractedContent.transcript || extractedContent.content).length > 300 && '...'}
                  </div>
                </div>
              </div>
              
              <ValidationResult
                result={validationResult}
                onAccept={handleAcceptContent}
                onReject={handleRejectContent}
                isLoading={isProcessing}
              />
            </div>
          )}

          {currentStep === 'generating-summary' && (
            <div className="sources-page__generating">
              <LoadingSpinner />
              <h3>Generating Summary...</h3>
              <p>Creating AI-powered summary of your content</p>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}

export default SourcesPage