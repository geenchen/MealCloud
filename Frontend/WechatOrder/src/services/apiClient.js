import axios from 'axios'
import { clearWechatAuth, ensureWechatAuth } from './authService'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000
})

apiClient.interceptors.request.use(async (config) => {
  let token =
    localStorage.getItem('access_token') ||
    localStorage.getItem('token') ||
    localStorage.getItem('auth_token')

  if (!token) {
    try {
      token = await ensureWechatAuth()
    } catch {
      token = null
    }
  }

  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }

  return config
})

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const status = error?.response?.status
    const originalConfig = error?.config || {}
    const requestUrl = String(originalConfig.url || '')

    if (status === 401 && !originalConfig._retry && !requestUrl.includes('/token')) {
      originalConfig._retry = true
      try {
        clearWechatAuth()
        const token = await ensureWechatAuth()
        originalConfig.headers = originalConfig.headers || {}
        originalConfig.headers.Authorization = `Bearer ${token}`
        return apiClient(originalConfig)
      } catch {
        return Promise.reject(error)
      }
    }

    return Promise.reject(error)
  }
)

export default apiClient
