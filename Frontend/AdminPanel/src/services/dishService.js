import apiClient from './apiClient'

export const getDishes = async (skip = 0, limit = 100) => {
  const response = await apiClient.get('/dishes', { params: { skip, limit } })
  return response.data
}

export const getDish = async (dishId) => {
  const response = await apiClient.get(`/dishes/${dishId}`)
  return response.data
}

export const createDish = async (dishData) => {
  const response = await apiClient.post('/dishes', dishData)
  return response.data
}

export const updateDish = async (dishId, dishData) => {
  const response = await apiClient.put(`/dishes/${dishId}`, dishData)
  return response.data
}

export const deleteDish = async (dishId) => {
  const response = await apiClient.delete(`/dishes/${dishId}`)
  return response.data
}

export const getCategories = async (skip = 0, limit = 100) => {
  const response = await apiClient.get('/categories', { params: { skip, limit } })
  return response.data
}
