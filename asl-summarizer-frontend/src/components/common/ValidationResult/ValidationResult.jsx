import React from 'react'
import Button from '../Button/Button'
import './ValidationResult.css'

const ValidationResult = ({ result, onAccept, onReject, isLoading }) => {
  const { accepted, checks, reason } = result

  const getCheckIcon = (passed) => passed ? '❌' : '✅'
  const getCheckStatus = (passed) => passed ? 'failed' : 'passed'

  const checkLabels = {
    pornography: 'Pornography',
    profanity: 'Profanity',
    hateSpeech: 'Hate Speech',
    discrimination: 'Discrimination',
    racism: 'Racism',
    politicalBias: 'Political Bias'
  }

  return (
    <div className={`validation-result ${accepted ? 'accepted' : 'rejected'}`}>
      <div className="validation-result__header">
        <div className="validation-result__status">
          <span className="validation-result__icon">
            {accepted ? '✅' : '❌'}
          </span>
          <h3 className="validation-result__title">
            Content {accepted ? 'Accepted' : 'Rejected'}
          </h3>
        </div>
        <p className="validation-result__reason">{reason}</p>
      </div>

      <div className="validation-result__checks">
        <h4 className="validation-result__checks-title">Validation Checks:</h4>
        <div className="validation-result__checks-grid">
          {Object.entries(checks).map(([key, failed]) => (
            <div
              key={key}
              className={`validation-result__check ${getCheckStatus(failed)}`}
            >
              <span className="validation-result__check-icon">
                {getCheckIcon(failed)}
              </span>
              <span className="validation-result__check-label">
                {checkLabels[key]}
              </span>
            </div>
          ))}
        </div>
      </div>

      <div className="validation-result__actions">
        {accepted ? (
          <Button
            variant="success"
            onClick={onAccept}
            disabled={isLoading}
          >
            Generate Summary
          </Button>
        ) : (
          <div className="validation-result__rejected-actions">
            <Button
              variant="secondary"
              onClick={onReject}
              disabled={isLoading}
            >
              Try Another Source
            </Button>
            <Button
              variant="ghost"
              onClick={onAccept}
              disabled={isLoading}
            >
              Override & Continue
            </Button>
          </div>
        )}
      </div>
    </div>
  )
}

export default ValidationResult