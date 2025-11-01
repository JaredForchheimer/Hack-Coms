// Mock data for development and testing

export const mockFolders = [
  {
    id: '1',
    name: 'Medical Articles',
    parentId: null,
    userId: '1',
    createdAt: '2024-01-15T10:00:00.000Z'
  },
  {
    id: '2',
    name: 'Technology News',
    parentId: null,
    userId: '1',
    createdAt: '2024-01-16T14:30:00.000Z'
  },
  {
    id: '3',
    name: 'Educational Content',
    parentId: null,
    userId: '1',
    createdAt: '2024-01-17T09:15:00.000Z'
  },
  {
    id: '4',
    name: 'Research Papers',
    parentId: '3',
    userId: '1',
    createdAt: '2024-01-18T11:45:00.000Z'
  }
]

export const mockFiles = [
  {
    id: '1',
    name: 'heart-disease-study.pdf',
    type: 'pdf',
    size: 2048576, // 2MB
    folderId: '1',
    uploadedAt: '2024-01-15T10:30:00.000Z',
    url: '/mock-files/heart-disease-study.pdf'
  },
  {
    id: '2',
    name: 'diabetes-prevention.pdf',
    type: 'pdf',
    size: 1536000, // 1.5MB
    folderId: '1',
    uploadedAt: '2024-01-15T11:00:00.000Z',
    url: '/mock-files/diabetes-prevention.pdf'
  },
  {
    id: '3',
    name: 'ai-breakthrough-video.mp4',
    type: 'video',
    size: 15728640, // 15MB
    folderId: '2',
    uploadedAt: '2024-01-16T15:00:00.000Z',
    url: '/mock-files/ai-breakthrough-video.mp4'
  },
  {
    id: '4',
    name: 'quantum-computing-article.pdf',
    type: 'pdf',
    size: 3072000, // 3MB
    folderId: '2',
    uploadedAt: '2024-01-16T16:30:00.000Z',
    url: '/mock-files/quantum-computing-article.pdf'
  },
  {
    id: '5',
    name: 'learning-theory-research.pdf',
    type: 'pdf',
    size: 4194304, // 4MB
    folderId: '4',
    uploadedAt: '2024-01-18T12:00:00.000Z',
    url: '/mock-files/learning-theory-research.pdf'
  }
]

export const mockSummaries = [
  {
    id: '1',
    folderId: '1',
    sourceFiles: ['1', '2'],
    content: 'This summary covers recent advances in cardiovascular health research, including prevention strategies for heart disease and diabetes management techniques. Key findings suggest that early intervention and lifestyle modifications can significantly reduce risk factors.',
    aslVideoUrl: '/mock-videos/medical-summary-asl.mp4',
    createdAt: '2024-01-15T12:00:00.000Z'
  },
  {
    id: '2',
    folderId: '2',
    sourceFiles: ['3', '4'],
    content: 'Technology summary focusing on artificial intelligence breakthroughs and quantum computing developments. The content explores how these emerging technologies are reshaping various industries and their potential future applications.',
    aslVideoUrl: '/mock-videos/tech-summary-asl.mp4',
    createdAt: '2024-01-16T17:00:00.000Z'
  },
  {
    id: '3',
    folderId: '4',
    sourceFiles: ['5'],
    content: 'Educational research summary examining modern learning theories and their practical applications in academic settings. The research highlights effective teaching methodologies and student engagement strategies.',
    aslVideoUrl: '/mock-videos/education-summary-asl.mp4',
    createdAt: '2024-01-18T13:30:00.000Z'
  }
]

export const mockCommunityPosts = [
  {
    id: '1',
    userId: '1',
    username: 'demo_user',
    summaryId: '1',
    aslVideoUrl: '/mock-videos/medical-summary-asl.mp4',
    description: 'Great summary of recent medical research on heart disease prevention! Really helpful for understanding the key points.',
    likes: 15,
    createdAt: '2024-01-15T13:00:00.000Z'
  },
  {
    id: '2',
    userId: '2',
    username: 'test_user',
    summaryId: '2',
    aslVideoUrl: '/mock-videos/tech-summary-asl.mp4',
    description: 'Amazing breakdown of AI and quantum computing advances. The ASL interpretation makes it so much more accessible!',
    likes: 23,
    createdAt: '2024-01-16T18:00:00.000Z'
  },
  {
    id: '3',
    userId: '1',
    username: 'demo_user',
    summaryId: '3',
    aslVideoUrl: '/mock-videos/education-summary-asl.mp4',
    description: 'This educational research summary is perfect for teachers and students. Love how clear the ASL translation is.',
    likes: 8,
    createdAt: '2024-01-18T14:00:00.000Z'
  },
  {
    id: '4',
    userId: '2',
    username: 'test_user',
    summaryId: '1',
    aslVideoUrl: '/mock-videos/medical-summary-asl.mp4',
    description: 'Shared this medical summary with my family. The ASL interpretation helps everyone understand the health tips better.',
    likes: 12,
    createdAt: '2024-01-19T10:30:00.000Z'
  }
]

// Helper functions for mock data
export const getMockDataByUserId = (userId) => {
  return {
    folders: mockFolders.filter(folder => folder.userId === userId),
    files: mockFiles,
    summaries: mockSummaries,
    communityPosts: mockCommunityPosts
  }
}

export const getFilesByFolderId = (folderId) => {
  return mockFiles.filter(file => file.folderId === folderId)
}

export const getFoldersByParentId = (parentId) => {
  return mockFolders.filter(folder => folder.parentId === parentId)
}

export const getSummariesByFolderId = (folderId) => {
  return mockSummaries.filter(summary => summary.folderId === folderId)
}

// File type helpers
export const getFileIcon = (fileType) => {
  switch (fileType) {
    case 'pdf':
      return '📄'
    case 'video':
      return '🎥'
    default:
      return '📁'
  }
}

export const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

export const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}