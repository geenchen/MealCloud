import apiClient from './apiClient'

export const getAllTables = async (skip = 0, limit = 100) => {
  const response = await apiClient.get('/tables', { params: { skip, limit } })
  return response.data
}

export const getAvailableTables = async (area = null, capacity = null) => {
  const response = await apiClient.get('/tables/available', {
    params: { area, capacity }
  })
  return response.data
}

export const createTable = async (tableData) => {
  const response = await apiClient.post('/tables', tableData)
  return response.data
}

export const updateTable = async (tableId, tableData) => {
  const response = await apiClient.put(`/tables/${tableId}`, tableData)
  return response.data
}

export const deleteTable = async (tableId) => {
  const response = await apiClient.delete(`/tables/${tableId}`)
  return response.data
}

export const occupyTable = async (tableId) => {
  const response = await apiClient.post(`/tables/${tableId}/occupy`)
  return response.data
}

export const freeTable = async (tableId) => {
  const response = await apiClient.post(`/tables/${tableId}/free`)
  return response.data
}

export const cleanTable = async (tableId) => {
  const response = await apiClient.post(`/tables/${tableId}/clean`)
  return response.data
}

export const mergeTables = async (tableIds, mergedTableNumber) => {
  const response = await apiClient.post('/tables/merge', null, {
    params: {
      table_ids: tableIds,
      merged_table_number: mergedTableNumber
    }
  })
  return response.data
}

export const splitTable = async (mergedTableId) => {
  const response = await apiClient.post(`/tables/split/${mergedTableId}`)
  return response.data
}

export const switchTables = async (fromTableId, toTableId) => {
  const response = await apiClient.post('/tables/switch', null, {
    params: {
      from_table_id: fromTableId,
      to_table_id: toTableId
    }
  })
  return response.data
}

export const getTableStats = async () => {
  const response = await apiClient.get('/tables/stats')
  return response.data
}

export const getTableDetails = async (tableId) => {
  const response = await apiClient.get(`/tables/${tableId}/details`)
  return response.data
}

export const batchUpdateTables = async (tableUpdates) => {
  const response = await apiClient.post('/tables/batch-update', tableUpdates)
  return response.data
}
