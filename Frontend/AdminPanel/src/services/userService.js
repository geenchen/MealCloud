import apiClient from './apiClient'

export const getUsers = async (skip = 0, limit = 100) => {
  const response = await apiClient.get('/users', { params: { skip, limit } })
  return response.data
}

export const createUser = async (payload) => {
  const response = await apiClient.post('/users', payload)
  return response.data
}

export const updateUser = async (userId, payload) => {
  const response = await apiClient.put(`/users/${userId}`, payload)
  return response.data
}

export const resetUserPassword = async (userId, password) => {
  const response = await apiClient.put(`/users/${userId}/password`, { password })
  return response.data
}

export const disableUser = async (userId) => {
  const response = await apiClient.delete(`/users/${userId}`)
  return response.data
}
