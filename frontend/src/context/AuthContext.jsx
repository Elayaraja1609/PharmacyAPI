import { createContext, useContext, useState, useEffect } from 'react'
import api from '../services/api'

const AuthContext = createContext()

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('admin_token')
    if (token) {
      verifyToken(token)
    } else {
      setLoading(false)
    }
  }, [])

  const verifyToken = async (token) => {
    try {
      const response = await api.get('/admin/verify', {
        headers: { Authorization: `Bearer ${token}` }
      })
      setUser(response.data)
      setLoading(false)
    } catch (error) {
      localStorage.removeItem('admin_token')
      setUser(null)
      setLoading(false)
    }
  }

  const login = async (username, password) => {
    try {
      const response = await api.post('/admin/login', { username, password })
      localStorage.setItem('admin_token', response.data.access_token)
      setUser({ username: response.data.username })
      return { success: true }
    } catch (error) {
      return {
        success: false,
        message: error.response?.data?.message || 'Login failed'
      }
    }
  }

  const logout = () => {
    localStorage.removeItem('admin_token')
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  )
}

