import axios from 'axios';

const API_BASE_URL = '/api/v1';

// 获取所有订单
export const getAllOrders = async (skip = 0, limit = 100) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/orders`, {
      params: { skip, limit }
    });
    return response.data;
  } catch (error) {
    console.error('获取订单列表失败:', error);
    throw error;
  }
};

// 获取订单详情
export const getOrder = async (orderId) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/orders/${orderId}`);
    return response.data;
  } catch (error) {
    console.error('获取订单详情失败:', error);
    throw error;
  }
};

// 创建订单
export const createOrder = async (orderData) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/orders`, orderData);
    return response.data;
  } catch (error) {
    console.error('创建订单失败:', error);
    throw error;
  }
};

//快创建订单
export const createQuickOrder = async (orderData) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/orders/quick`, orderData);
    return response.data;
  } catch (error) {
    console.error('快速创建订单失败:', error);
    throw error;
  }
};

// 更新订单
export const updateOrder = async (orderId, orderData) => {
  try {
    const response = await axios.put(`${API_BASE_URL}/orders/${orderId}`, orderData);
    return response.data;
  } catch (error) {
    console.error('更新订单失败:', error);
    throw error;
  }
};

// 删除订单
export const deleteOrder = async (orderId) => {
  try {
    const response = await axios.delete(`${API_BASE_URL}/orders/${orderId}`);
    return response.data;
  } catch (error) {
    console.error('删除订单失败:', error);
    throw error;
  }
};

//确认订单
export const confirmOrder = async (orderId) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/orders/${orderId}/confirm`);
    return response.data;
  } catch (error) {
    console.error('确认订单失败:', error);
    throw error;
  }
};

//取订单
export const cancelOrder = async (orderId) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/orders/${orderId}/cancel`);
    return response.data;
  } catch (error) {
    console.error('取消订单失败:', error);
    throw error;
  }
};

//完成订单
export const completeOrder = async (orderId) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/orders/${orderId}/complete`);
    return response.data;
  } catch (error) {
    console.error('完成订单失败:', error);
    throw error;
  }
};

// 获取客户订单历史
export const getCustomerOrderHistory = async (customerPhone, limit = 10) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/orders/customer/${customerPhone}`, {
      params: { limit }
    });
    return response.data;
  } catch (error) {
    console.error('获取客户订单历史失败:', error);
    throw error;
  }
};

// 获取订单统计
export const getOrderStats = async (days = 7) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/orders/stats`, {
      params: { days }
    });
    return response.data;
  } catch (error) {
    console.error('获取订单统计失败:', error);
    throw error;
  }
};