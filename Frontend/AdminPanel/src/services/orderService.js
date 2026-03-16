import apiClient from './apiClient'

export const getAllOrders = async (skip = 0, limit = 100) => {
  const response = await apiClient.get('/orders', { params: { skip, limit } })
  return response.data
}

export const getOrder = async (orderId) => {
  const response = await apiClient.get(`/orders/${orderId}`)
  return response.data
}

export const createOrder = async (orderData) => {
  const response = await apiClient.post('/orders', orderData)
  return response.data
}

export const createQuickOrder = async (orderData) => {
  const response = await apiClient.post('/orders/quick', orderData)
  return response.data
}

export const updateOrder = async (orderId, orderData) => {
  const response = await apiClient.put(`/orders/${orderId}`, orderData)
  return response.data
}

export const deleteOrder = async (orderId) => {
  const response = await apiClient.delete(`/orders/${orderId}`)
  return response.data
}

export const confirmOrder = async (orderId) => {
  const response = await apiClient.post(`/orders/${orderId}/confirm`)
  return response.data
}

export const cancelOrder = async (orderId) => {
  const response = await apiClient.post(`/orders/${orderId}/cancel`)
  return response.data
}

export const completeOrder = async (orderId) => {
  const response = await apiClient.post(`/orders/${orderId}/complete`)
  return response.data
}

export const getCustomerOrderHistory = async (customerPhone, limit = 10) => {
  const response = await apiClient.get(`/orders/customer/${customerPhone}`, { params: { limit } })
  return response.data
}

export const getOrderStats = async (days = 7) => {
  const response = await apiClient.get('/orders/stats', { params: { days } })
  return response.data
}
