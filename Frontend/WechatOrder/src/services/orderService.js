import apiClient from './apiClient'

export const createOrder = async (orderData) => {
  const response = await apiClient.post('/orders', orderData)
  return response.data
}

export const getOrder = async (orderId) => {
  const response = await apiClient.get(`/orders/${orderId}`)
  return response.data
}

export const getAllOrders = async (skip = 0, limit = 50) => {
  const response = await apiClient.get('/orders', { params: { skip, limit } })
  return response.data
}
