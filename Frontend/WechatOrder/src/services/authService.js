import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1'
const TOKEN_KEY = 'access_token'
const BACKEND_USER_KEY = 'wechat_backend_username'
const BACKEND_PASS_KEY = 'wechat_backend_password'

const ENV_FALLBACK_USERNAME = import.meta.env.VITE_WECHAT_USERNAME || ''
const ENV_FALLBACK_PASSWORD = import.meta.env.VITE_WECHAT_PASSWORD || ''

let loginPromise = null

const setToken = (token) => {
  localStorage.setItem(TOKEN_KEY, token)
  localStorage.setItem('token', token)
  localStorage.setItem('auth_token', token)
}

const getBackendCredentials = () => {
  const username = localStorage.getItem(BACKEND_USER_KEY) || ENV_FALLBACK_USERNAME
  const password = localStorage.getItem(BACKEND_PASS_KEY) || ENV_FALLBACK_PASSWORD
  return { username, password }
}

export const setBackendCredentials = (username, password) => {
  localStorage.setItem(BACKEND_USER_KEY, username || '')
  localStorage.setItem(BACKEND_PASS_KEY, password || '')
}

export const hasBackendCredentials = () => {
  const { username, password } = getBackendCredentials()
  return Boolean(String(username || '').trim() && String(password || ''))
}

const login = async (username, password) => {
  const body = new URLSearchParams()
  body.append('username', username)
  body.append('password', password)

  const response = await axios.post(`${API_BASE_URL}/token`, body, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    },
    timeout: 15000
  })

  const token = response.data?.access_token
  if (!token) {
    throw new Error('登录成功但未返回 token')
  }

  setToken(token)
  return token
}

export const loginWechatBackend = async (username, password) => {
  const finalUsername = String(username || '').trim()
  const finalPassword = String(password || '')
  if (!finalUsername || !finalPassword) {
    throw new Error('请输入后台账号和密码')
  }

  const token = await login(finalUsername, finalPassword)
  setBackendCredentials(finalUsername, finalPassword)
  return token
}

export const ensureWechatAuth = async () => {
  const existingToken =
    localStorage.getItem(TOKEN_KEY) ||
    localStorage.getItem('token') ||
    localStorage.getItem('auth_token')

  if (existingToken) {
    return existingToken
  }

  const { username, password } = getBackendCredentials()
  if (!username || !password) {
    throw new Error('请先登录系统')
  }

  if (!loginPromise) {
    loginPromise = login(username, password)
      .catch((error) => {
        throw new Error(error?.response?.data?.detail || '后台登录失败，请重新登录')
      })
      .finally(() => {
        loginPromise = null
      })
  }

  return loginPromise
}

export const clearWechatAuth = () => {
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem('token')
  localStorage.removeItem('auth_token')
}
