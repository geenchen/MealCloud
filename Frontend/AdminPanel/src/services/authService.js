import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8008/api/v1'

const TOKEN_KEY = 'access_token'
const USERNAME_KEY = 'username'

export const login = async ({ username, password }) => {
  const body = new URLSearchParams()
  body.append('username', username)
  body.append('password', password)

  const response = await axios.post(`${API_BASE_URL}/token`, body, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    }
  })

  const token = response.data?.access_token
  if (!token) {
    throw new Error('Token not returned by server')
  }

  localStorage.setItem(TOKEN_KEY, token)
  localStorage.setItem(USERNAME_KEY, username)
  return response.data
}

export const logout = () => {
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem('token')
  localStorage.removeItem('auth_token')
  localStorage.removeItem(USERNAME_KEY)
}

export const getCurrentUsername = () => localStorage.getItem(USERNAME_KEY) || '管理员'

export const isAuthenticated = () => {
  const token =
    localStorage.getItem(TOKEN_KEY) ||
    localStorage.getItem('token') ||
    localStorage.getItem('auth_token')
  return Boolean(token)
}
