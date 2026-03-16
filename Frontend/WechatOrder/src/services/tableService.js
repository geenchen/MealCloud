import apiClient from './apiClient'

export const getAvailableTables = async (area = null, capacity = null) => {
  const response = await apiClient.get('/tables/available', {
    params: { area, capacity }
  })
  return response.data
}
