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

export const uploadDishImage = async (file) => {
  const formData = new FormData()
  formData.append('image', file)
  const response = await apiClient.post('/dishes/upload-image', formData)
  return response.data
}

export const getCategories = async (skip = 0, limit = 100) => {
  const response = await apiClient.get('/categories', { params: { skip, limit } })
  return response.data
}

export const getCategory = async (categoryId) => {
  const response = await apiClient.get(`/categories/${categoryId}`)
  return response.data
}

export const createCategory = async (categoryData) => {
  const response = await apiClient.post('/categories', categoryData)
  return response.data
}

export const updateCategory = async (categoryId, categoryData) => {
  const response = await apiClient.put(`/categories/${categoryId}`, categoryData)
  return response.data
}

export const deleteCategory = async (categoryId) => {
  const response = await apiClient.delete(`/categories/${categoryId}`)
  return response.data
}

export const getCategoriesPage = async (skip = 0, limit = 100) => {
  const response = await apiClient.get('/categories/page', { params: { skip, limit } })
  return response.data
}

