import React, { useState } from 'react'
import { useDropzone } from 'react-dropzone'
import Button from '../Button/Button'
import LoadingSpinner from '../LoadingSpinner/LoadingSpinner'
import './MediaUpload.css'

const MediaUpload = ({ onUpload, isLoading }) => {
  const [urlInput, setUrlInput] = useState('')
  const [uploadType, setUploadType] = useState('url') // 'url' or 'file'

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: {
      'application/pdf': ['.pdf'],
      'video/*': ['.mp4', '.avi', '.mov', '.wmv'],
      'audio/*': ['.mp3', '.wav', '.m4a']
    },
    maxFiles: 1,
    onDrop: (acceptedFiles) => {
      if (acceptedFiles.length > 0) {
        onUpload({ type: 'file', data: acceptedFiles[0] })
      }
    }
  })

  const handleUrlSubmit = (e) => {
    e.preventDefault()
    if (urlInput.trim()) {
      onUpload({ type: 'url', data: urlInput.trim() })
      setUrlInput('')
    }
  }

  const isValidUrl = (string) => {
    try {
      new URL(string)
      return true
    } catch (_) {
      return false
    }
  }

  return (
    <div className="media-upload">
      <div className="media-upload__tabs">
        <button
          className={`media-upload__tab ${uploadType === 'url' ? 'active' : ''}`}
          onClick={() => setUploadType('url')}
          disabled={isLoading}
        >
          URL/Link
        </button>
        <button
          className={`media-upload__tab ${uploadType === 'file' ? 'active' : ''}`}
          onClick={() => setUploadType('file')}
          disabled={isLoading}
        >
          File Upload
        </button>
      </div>

      {uploadType === 'url' && (
        <div className="media-upload__url-section">
          <form onSubmit={handleUrlSubmit} className="media-upload__form">
            <div className="media-upload__input-group">
              <input
                type="url"
                value={urlInput}
                onChange={(e) => setUrlInput(e.target.value)}
                placeholder="Enter article URL or YouTube video link..."
                className="media-upload__input"
                disabled={isLoading}
              />
              <Button
                type="submit"
                variant="primary"
                disabled={!urlInput.trim() || !isValidUrl(urlInput) || isLoading}
              >
                {isLoading ? <LoadingSpinner size="small" /> : 'Process URL'}
              </Button>
            </div>
          </form>
          <div className="media-upload__examples">
            <p className="media-upload__examples-title">Supported formats:</p>
            <ul className="media-upload__examples-list">
              <li>News articles (any website)</li>
              <li>YouTube videos</li>
              <li>Blog posts and online content</li>
            </ul>
          </div>
        </div>
      )}

      {uploadType === 'file' && (
        <div className="media-upload__file-section">
          <div
            {...getRootProps()}
            className={`media-upload__dropzone ${isDragActive ? 'active' : ''} ${isLoading ? 'disabled' : ''}`}
          >
            <input {...getInputProps()} disabled={isLoading} />
            <div className="media-upload__dropzone-content">
              <div className="media-upload__dropzone-icon">📁</div>
              {isDragActive ? (
                <p className="media-upload__dropzone-text">Drop the file here...</p>
              ) : (
                <>
                  <p className="media-upload__dropzone-text">
                    Drag & drop a file here, or click to select
                  </p>
                  <p className="media-upload__dropzone-subtext">
                    Supports PDF, video files (MP4, AVI, MOV), and audio files
                  </p>
                </>
              )}
            </div>
          </div>
        </div>
      )}

      {isLoading && (
        <div className="media-upload__loading">
          <LoadingSpinner />
          <p>Processing media...</p>
        </div>
      )}
    </div>
  )
}

export default MediaUpload