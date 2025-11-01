// Mock authentication service for frontend development
// This will be replaced with real API calls when backend is ready

const MOCK_USERS = [
  {
    id: '1',
    email: 'demo@example.com',
    username: 'demo_user',
    password: 'password123', // In real app, this would be hashed
    createdAt: '2024-01-01T00:00:00.000Z'
  },
  {
    id: '2',
    email: 'test@example.com',
    username: 'test_user',
    password: 'test123',
    createdAt: '2024-01-01T00:00:00.000Z'
  }
]

// Simulate API delay
const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms))

// Generate mock JWT token
const generateMockToken = (userId) => {
  const header = btoa(JSON.stringify({ alg: 'HS256', typ: 'JWT' }))
  const payload = btoa(JSON.stringify({ 
    userId, 
    exp: Date.now() + (24 * 60 * 60 * 1000) // 24 hours
  }))
  const signature = btoa('mock-signature')
  return `${header}.${payload}.${signature}`
}

// Parse mock JWT token
const parseMockToken = (token) => {
  try {
    const parts = token.split('.')
    if (parts.length !== 3) throw new Error('Invalid token')
    
    const payload = JSON.parse(atob(parts[1]))
    if (payload.exp < Date.now()) throw new Error('Token expired')
    
    return payload
  } catch (error) {
    throw new Error('Invalid token')
  }
}

export const authService = {
  async login(email, password) {
    await delay(1000) // Simulate network delay
    
    const user = MOCK_USERS.find(u => u.email === email && u.password === password)
    
    if (!user) {
      throw new Error('Invalid email or password')
    }
    
    const token = generateMockToken(user.id)
    const { password: _, ...userWithoutPassword } = user
    
    return {
      user: userWithoutPassword,
      token
    }
  },

  async logout() {
    await delay(500)
    // In real app, this would invalidate the token on the server
    return { success: true }
  },

  async verifyToken(token) {
    await delay(500)
    
    try {
      const payload = parseMockToken(token)
      const user = MOCK_USERS.find(u => u.id === payload.userId)
      
      if (!user) {
        throw new Error('User not found')
      }
      
      const { password: _, ...userWithoutPassword } = user
      return userWithoutPassword
    } catch (error) {
      throw new Error('Invalid or expired token')
    }
  },

  async register(userData) {
    await delay(1000)
    
    // Check if user already exists
    const existingUser = MOCK_USERS.find(u => u.email === userData.email)
    if (existingUser) {
      throw new Error('User already exists with this email')
    }
    
    // Create new user
    const newUser = {
      id: (MOCK_USERS.length + 1).toString(),
      email: userData.email,
      username: userData.username || userData.email.split('@')[0],
      password: userData.password,
      createdAt: new Date().toISOString()
    }
    
    MOCK_USERS.push(newUser)
    
    const token = generateMockToken(newUser.id)
    const { password: _, ...userWithoutPassword } = newUser
    
    return {
      user: userWithoutPassword,
      token
    }
  }
}