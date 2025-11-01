import React, { createContext, useContext, useReducer } from 'react'

export const DataContext = createContext()

const initialState = {
  folders: [],
  files: [],
  summaries: [],
  communityPosts: [],
  isLoading: false,
  error: null
}

function dataReducer(state, action) {
  switch (action.type) {
    case 'SET_LOADING':
      return {
        ...state,
        isLoading: action.payload
      }
    case 'SET_ERROR':
      return {
        ...state,
        error: action.payload,
        isLoading: false
      }
    case 'CLEAR_ERROR':
      return {
        ...state,
        error: null
      }
    case 'SET_FOLDERS':
      return {
        ...state,
        folders: action.payload
      }
    case 'ADD_FOLDER':
      return {
        ...state,
        folders: [...state.folders, action.payload]
      }
    case 'UPDATE_FOLDER':
      return {
        ...state,
        folders: state.folders.map(folder =>
          folder.id === action.payload.id ? action.payload : folder
        )
      }
    case 'DELETE_FOLDER':
      return {
        ...state,
        folders: state.folders.filter(folder => folder.id !== action.payload)
      }
    case 'SET_FILES':
      return {
        ...state,
        files: action.payload
      }
    case 'ADD_FILE':
      return {
        ...state,
        files: [...state.files, action.payload]
      }
    case 'DELETE_FILE':
      return {
        ...state,
        files: state.files.filter(file => file.id !== action.payload)
      }
    case 'SET_SUMMARIES':
      return {
        ...state,
        summaries: action.payload
      }
    case 'ADD_SUMMARY':
      return {
        ...state,
        summaries: [...state.summaries, action.payload]
      }
    case 'SET_COMMUNITY_POSTS':
      return {
        ...state,
        communityPosts: action.payload
      }
    case 'ADD_COMMUNITY_POST':
      return {
        ...state,
        communityPosts: [action.payload, ...state.communityPosts]
      }
    case 'LIKE_POST':
      return {
        ...state,
        communityPosts: state.communityPosts.map(post =>
          post.id === action.payload ? { ...post, likes: post.likes + 1 } : post
        )
      }
    default:
      return state
  }
}

export function DataProvider({ children }) {
  const [state, dispatch] = useReducer(dataReducer, initialState)

  // Folder operations
  const createFolder = (folderData) => {
    const newFolder = {
      id: Date.now().toString(),
      createdAt: new Date().toISOString(),
      ...folderData
    }
    dispatch({ type: 'ADD_FOLDER', payload: newFolder })
    return newFolder
  }

  const updateFolder = (folderId, updates) => {
    const updatedFolder = {
      ...state.folders.find(f => f.id === folderId),
      ...updates
    }
    dispatch({ type: 'UPDATE_FOLDER', payload: updatedFolder })
    return updatedFolder
  }

  const deleteFolder = (folderId) => {
    dispatch({ type: 'DELETE_FOLDER', payload: folderId })
    // Also delete files in this folder
    const filesToDelete = state.files.filter(file => file.folderId === folderId)
    filesToDelete.forEach(file => {
      dispatch({ type: 'DELETE_FILE', payload: file.id })
    })
  }

  // File operations
  const addFile = (fileData) => {
    const newFile = {
      id: Date.now().toString(),
      uploadedAt: new Date().toISOString(),
      ...fileData
    }
    dispatch({ type: 'ADD_FILE', payload: newFile })
    return newFile
  }

  const deleteFile = (fileId) => {
    dispatch({ type: 'DELETE_FILE', payload: fileId })
  }

  // Summary operations
  const addSummary = (summaryData) => {
    const newSummary = {
      id: Date.now().toString(),
      createdAt: new Date().toISOString(),
      ...summaryData
    }
    dispatch({ type: 'ADD_SUMMARY', payload: newSummary })
    return newSummary
  }

  // Community operations
  const addCommunityPost = (postData) => {
    const newPost = {
      id: Date.now().toString(),
      createdAt: new Date().toISOString(),
      likes: 0,
      ...postData
    }
    dispatch({ type: 'ADD_COMMUNITY_POST', payload: newPost })
    return newPost
  }

  const likePost = (postId) => {
    dispatch({ type: 'LIKE_POST', payload: postId })
  }

  // Utility functions
  const setLoading = (loading) => {
    dispatch({ type: 'SET_LOADING', payload: loading })
  }

  const setError = (error) => {
    dispatch({ type: 'SET_ERROR', payload: error })
  }

  const clearError = () => {
    dispatch({ type: 'CLEAR_ERROR' })
  }

  const value = {
    ...state,
    createFolder,
    updateFolder,
    deleteFolder,
    addFile,
    deleteFile,
    addSummary,
    addCommunityPost,
    likePost,
    setLoading,
    setError,
    clearError
  }

  return (
    <DataContext.Provider value={value}>
      {children}
    </DataContext.Provider>
  )
}

export function useData() {
  const context = useContext(DataContext)
  if (!context) {
    throw new Error('useData must be used within a DataProvider')
  }
  return context
}