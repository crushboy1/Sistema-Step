import React, { createContext, useContext, useState, useEffect } from 'react'

const AuthContext = createContext()

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Simular verificación de autenticación
    const token = localStorage.getItem('token')
    const userData = localStorage.getItem('user')
    
    if (token && userData) {
      setUser(JSON.parse(userData))
    }
    setLoading(false)
  }, [])

  const login = async (email, password) => {
    try {
      // Simular llamada a API
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      // Datos de usuario simulados
      const userData = {
        id: 1,
        name: 'Juan Pérez',
        email: email,
        role: email.includes('tutor') ? 'tutor' : 'estudiante',
        avatar: `https://ui-avatars.com/api/?name=${encodeURIComponent('Juan Pérez')}&background=3b82f6&color=fff`
      }
      
      localStorage.setItem('token', 'fake-jwt-token')
      localStorage.setItem('user', JSON.stringify(userData))
      setUser(userData)
      
      return { success: true }
    } catch (error) {
      return { success: false, error: 'Credenciales inválidas' }
    }
  }

  const register = async (userData) => {
    try {
      // Simular llamada a API
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      const newUser = {
        id: Date.now(),
        name: `${userData.firstName} ${userData.lastName}`,
        email: userData.email,
        role: userData.role,
        avatar: `https://ui-avatars.com/api/?name=${encodeURIComponent(userData.firstName + ' ' + userData.lastName)}&background=3b82f6&color=fff`
      }
      
      localStorage.setItem('token', 'fake-jwt-token')
      localStorage.setItem('user', JSON.stringify(newUser))
      setUser(newUser)
      
      return { success: true }
    } catch (error) {
      return { success: false, error: 'Error al registrar usuario' }
    }
  }

  const logout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    setUser(null)
  }

  const value = {
    user,
    login,
    register,
    logout,
    loading
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}