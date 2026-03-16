import apiClient from './apiClient'

export const getCategories = async (skip = 0, limit = 200) => {
  const response = await apiClient.get('/categories', { params: { skip, limit } })
  return response.data
}

export const getDishes = async (skip = 0, limit = 500) => {
  const response = await apiClient.get('/dishes', { params: { skip, limit } })
  return response.data
}