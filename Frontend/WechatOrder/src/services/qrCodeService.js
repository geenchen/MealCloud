import axios from 'axios';

const API_BASE_URL = '/api/v1';

// 生成桌台二维码
export const generateTableQRCode = async (tableId) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/tables/${tableId}/qrcode-data`);
    return response.data;
  } catch (error) {
    console.error('获取桌台二维码数据失败:', error);
    throw error;
  }
};

// 获取桌台二维码URL
export const getTableQRCodeUrl = async (tableId) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/tables/${tableId}/qrcode-url`);
    return response.data;
  } catch (error) {
    console.error('获取桌台二维码URL失败:', error);
    throw error;
  }
};

// 通过二维码数据解析桌台信息
export const parseQRCodeData = async (qrCodeData) => {
  try {
    // 如果是base64编码的数据，先解码
    let parsedData;
    try {
      const decoded = atob(qrCodeData);
      parsedData = JSON.parse(decoded);
    } catch (e) {
      // 如果不是base64编码，直接解析为JSON
      parsedData = JSON.parse(qrCodeData);
    }
    
    // 如果是桌台码，则返回桌台信息
    if (parsedData.type === 'table') {
      const tableResponse = await axios.get(`${API_BASE_URL}/tables/${parsedData.tableId}`);
      return {
        type: 'table',
        table: tableResponse.data,
        isTableCode: true
      };
    } 
    // 如果是前台码，则返回前台信息
    else if (parsedData.type === 'frontdesk') {
      return {
        type: 'frontdesk',
        isTableCode: false
      };
    }
    
    return null;
  } catch (error) {
    console.error('解析二维码数据失败:', error);
    throw error;
  }
};

// 扫描二维码智能识别
export const scanQRCode = async (qrCodeData) => {
  try {
    const parsedResult = await parseQRCodeData(qrCodeData);
    
    if (!parsedResult) {
      throw new Error('无效的二维码数据');
    }
    
    // 根据二维码类型返回不同结果
    if (parsedResult.isTableCode) {
      // 返回桌台相关信息，用于自动绑定桌台
      return {
        type: 'table',
        table: parsedResult.table,
        autoBind: true,
        message: `已识别桌台: ${parsedResult.table.name}`
      };
    } else {
      // 返回前台模式，用于外带/打包模式
      return {
        type: 'frontdesk',
        autoBind: false,
        message: '已进入前台模式，可进行外带点餐'
      };
    }
  } catch (error) {
    console.error('扫描二维码失败:', error);
    throw error;
  }
};

// 生成前台二维码（用于外带模式）
export const generateFrontDeskQRCode = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/tables/frontdesk/qrcode-data`);
    return response.data;
  } catch (error) {
    console.error('获取前台二维码数据失败:', error);
    throw error;
  }
};

// 获取前台二维码URL
export const getFrontDeskQRCodeUrl = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/tables/frontdesk/qrcode-url`);
    return response.data;
  } catch (error) {
    console.error('获取前台二维码URL失败:', error);
    throw error;
  }
};