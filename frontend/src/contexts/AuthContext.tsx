import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { authAPI } from '@/services/api'
import toast from 'react-hot-toast'

interface User {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
  is_staff: boolean
}

interface AuthContextType {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  hasCheckedAuth: boolean
  login: (username: string, password: string) => Promise<boolean>
  logout: () => void
  register: (userData: any) => Promise<boolean>
  updateProfile: (profileData: any) => Promise<boolean>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

interface AuthProviderProps {
  children: ReactNode
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [hasCheckedAuth, setHasCheckedAuth] = useState(false)

  const isAuthenticated = !!user

  useEffect(() => {
    checkAuthStatus()
  }, [])

  const checkAuthStatus = async () => {
    try {
      console.log('🔍 Checking auth status...')
      const token = localStorage.getItem('access_token')
      console.log('📝 Token found:', token ? 'Yes' : 'No')
      
      if (token) {
        console.log('🔐 Attempting to get user profile...')
        try {
          const response = await authAPI.getProfile()
          console.log('✅ Profile response:', response.data)
          setUser(response.data)
        } catch (profileError: any) {
          console.error('❌ Profile fetch error:', profileError)
          if (profileError.response?.status === 401) {
            // Token is invalid, remove it
            console.log('🚫 Invalid token, removing...')
            localStorage.removeItem('access_token')
            localStorage.removeItem('refresh_token')
            setUser(null)
          }
        }
      } else {
        console.log('❌ No token found, user not authenticated')
        setUser(null)
      }
    } catch (error) {
      console.error('❌ Error checking auth status:', error)
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      setUser(null)
    } finally {
      console.log('🏁 Auth check complete, setting loading to false')
      setHasCheckedAuth(true)
      setIsLoading(false)
    }
  }

  const login = async (username: string, password: string): Promise<boolean> => {
    try {
      console.log('🔐 Starting login process...')
      setIsLoading(true)
      
      console.log('📡 Calling login API...')
      const response = await authAPI.login({ username, password })
      console.log('✅ Login API response:', response.data)
      
      const { access, refresh } = response.data
      
      console.log('💾 Storing tokens...')
      localStorage.setItem('access_token', access)
      localStorage.setItem('refresh_token', refresh)
      
      console.log('👤 Getting user profile...')
      const profileResponse = await authAPI.getProfile()
      console.log('✅ Profile response:', profileResponse.data)
      setUser(profileResponse.data)
      
      toast.success('Login successful!')
      console.log('🎉 Login completed successfully!')
      return true
    } catch (error: any) {
      console.error('❌ Login error:', error)
      const message = error.response?.data?.detail || 'Login failed. Please try again.'
      toast.error(message)
      return false
    } finally {
      setIsLoading(false)
    }
  }

  const logout = async () => {
    try {
      // For JWT tokens, logout is handled on the frontend by removing tokens
      // No need to call backend API since JWT tokens are stateless
      console.log('🔓 Logging out user...')
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      // Remove tokens from localStorage
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      
      // Clear user state
      setUser(null)
      
      // Show success message
      toast.success('Logged out successfully')
      
      console.log('✅ Logout completed successfully')
    }
  }

  const register = async (userData: any): Promise<boolean> => {
    try {
      setIsLoading(true)
      await authAPI.register(userData)
      toast.success('Registration successful! Please log in.')
      return true
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Registration failed. Please try again.'
      toast.error(message)
      return false
    } finally {
      setIsLoading(false)
    }
  }

  const updateProfile = async (profileData: any): Promise<boolean> => {
    try {
      setIsLoading(true)
      const response = await authAPI.updateProfile(profileData)
      setUser(response.data)
      toast.success('Profile updated successfully!')
      return true
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Profile update failed. Please try again.'
      toast.error(message)
      return false
    } finally {
      setIsLoading(false)
    }
  }

  const value: AuthContextType = {
    user,
    isAuthenticated,
    isLoading,
    hasCheckedAuth,
    login,
    logout,
    register,
    updateProfile,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
