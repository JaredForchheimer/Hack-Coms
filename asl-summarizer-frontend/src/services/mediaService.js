// Media processing and validation service
import axios from 'axios'

// Real API endpoints
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api'

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000, // 60 seconds for LLM operations
  headers: {
    'Content-Type': 'application/json'
  }
})

// Add response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    console.error('API Error:', error.response?.data || error.message)
    return Promise.reject(error.response?.data || { success: false, error: error.message })
  }
)

export const mediaService = {
  // Extract text from URL (news article or YouTube video)
  async extractTextFromUrl(url) {
    try {
      console.log('Extracting text from URL:', url)
      
      const response = await apiClient.post('/media/extract-url', { url })
      
      return {
        success: response.success,
        type: response.type,
        title: response.title,
        transcript: response.transcript,
        content: response.content,
        duration: response.duration,
        thumbnail: response.thumbnail,
        author: response.author,
        publishDate: response.publishDate,
        validation: response.validation
      }
    } catch (error) {
      console.error('Error extracting text:', error)
      return {
        success: false,
        error: error.error || 'Failed to extract text from URL'
      }
    }
  },

  // Validate content using LLM APIs
  async validateContent(content) {
    try {
      console.log('Validating content...')
      
      const response = await apiClient.post('/media/validate', { content })
      
      return {
        success: response.success,
        accepted: response.accepted,
        checks: response.checks,
        reason: response.reason
      }
    } catch (error) {
      console.error('Error validating content:', error)
      return {
        success: false,
        error: error.error || 'Failed to validate content'
      }
    }
  },

  // Generate summary using LLM APIs and store in database
  async generateSummary(content, title, sourceData = {}) {
    try {
      console.log('Generating summary...')
      
      const payload = {
        content,
        title,
        source_data: {
          type: sourceData.type || 'unknown',
          url: sourceData.url || null,
          metadata: sourceData.metadata || {}
        }
      }
      
      const response = await apiClient.post('/media/summarize', payload)
      
      return {
        success: response.success,
        summary: response.summary,
        wordCount: response.wordCount,
        generatedAt: response.generatedAt,
        sourceId: response.source_id,
        summaryId: response.summary_id
      }
    } catch (error) {
      console.error('Error generating summary:', error)
      return {
        success: false,
        error: error.error || 'Failed to generate summary'
      }
    }
  },

  // Process uploaded file
  async processFile(file) {
    try {
      console.log('Processing file:', file.name)
      
      const formData = new FormData()
      formData.append('file', file)
      
      const response = await axios.post(`${API_BASE_URL}/media/process-file`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        },
        timeout: 60000
      })
      
      return response.data
    } catch (error) {
      console.error('Error processing file:', error)
      const errorData = error.response?.data || { success: false, error: error.message }
      return {
        success: false,
        error: errorData.error || 'Failed to process file'
      }
    }
  },

  // Get all sources from database
  async getSources(limit = 100, offset = 0, search = '') {
    try {
      const params = { limit, offset }
      if (search) params.search = search
      
      const response = await apiClient.get('/sources', { params })
      
      return {
        success: response.success,
        sources: response.sources || [],
        count: response.count || 0
      }
    } catch (error) {
      console.error('Error fetching sources:', error)
      return {
        success: false,
        error: error.error || 'Failed to fetch sources',
        sources: []
      }
    }
  },

  // Get all summaries from database
  async getSummaries(limit = 100, offset = 0) {
    try {
      const response = await apiClient.get('/summaries', {
        params: { limit, offset }
      })
      
      return {
        success: response.success,
        summaries: response.summaries || [],
        count: response.count || 0
      }
    } catch (error) {
      console.error('Error fetching summaries:', error)
      return {
        success: false,
        error: error.error || 'Failed to fetch summaries',
        summaries: []
      }
    }
  },

  // Get source by ID
  async getSourceById(id) {
    try {
      const response = await apiClient.get(`/sources/${id}`)
      return {
        success: response.success,
        source: response.source
      }
    } catch (error) {
      console.error('Error fetching source:', error)
      return {
        success: false,
        error: error.error || 'Failed to fetch source'
      }
    }
  },

  // Get summary by ID
  async getSummaryById(id) {
    try {
      const response = await apiClient.get(`/summaries/${id}`)
      return {
        success: response.success,
        summary: response.summary
      }
    } catch (error) {
      console.error('Error fetching summary:', error)
      return {
        success: false,
        error: error.error || 'Failed to fetch summary'
      }
    }
  },

  // Get application statistics
  async getStatistics() {
    try {
      const response = await apiClient.get('/statistics')
      return {
        success: response.success,
        statistics: response.statistics
      }
    } catch (error) {
      console.error('Error fetching statistics:', error)
      return {
        success: false,
        error: error.error || 'Failed to fetch statistics',
        statistics: {}
      }
    }
  }
}

export default mediaService