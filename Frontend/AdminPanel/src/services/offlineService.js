import localStorageService from './localStorageService';
import { getAllTables, createTable, updateTable } from './tableService';
import { createQuickOrder, getAllOrders } from './orderService';
import { getDishes } from './dishService';

class OfflineService {
  constructor() {
    this.isSyncing = false;
    this.syncInterval = null;
    this.networkListener = null;
    this.setupNetworkListener();
    this.startAutoSync();
  }

  // 设置网络状态监听器
  setupNetworkListener() {
    this.networkListener = localStorageService.onNetworkStatusChange((isOnline) => {
      if (isOnline) {
        console.log('网络已连接，开始同步数据...');
        this.syncPendingData();
      } else {
        console.log('网络已断开，进入离线模式');
      }
    });
  }

  // 开始自动同步
  startAutoSync() {
    // 每5分钟检查一次同步
    this.syncInterval = setInterval(() => {
      if (localStorageService.isOnline()) {
        this.syncPendingData();
      }
    }, 5 * 60 * 1000);
  }

  // 停止自动同步
  stopAutoSync() {
    if (this.syncInterval) {
      clearInterval(this.syncInterval);
      this.syncInterval = null;
    }
  }

  // 同步待处理数据
  async syncPendingData() {
    if (this.isSyncing || !localStorageService.isOnline()) {
      return;
    }

    this.isSyncing = true;
    try {
      const syncQueue = localStorageService.getSyncQueue();
      
      if (syncQueue.length === 0) {
        return;
      }

      console.log(`开始同步 ${syncQueue.length} 个待处理操作...`);
      
      // 按顺序处理同步队列
      for (const item of syncQueue) {
        try {
          await this.processSyncItem(item);
          localStorageService.removeFromSyncQueue(item.id);
        } catch (error) {
          console.error(`同步操作失败 ID: ${item.id}`, error);
          // 继续处理下一个项目，不中断整个同步过程
        }
      }

      localStorageService.setLastSyncTime();
      console.log('数据同步完成');

    } catch (error) {
      console.error('同步过程中发生错误:', error);
    } finally {
      this.isSyncing = false;
    }
  }

  // 处理单个同步项目
  async processSyncItem(item) {
    const { operation, data } = item;
    
    switch (operation) {
      case 'CREATE_TABLE':
        await createTable(data);
        break;
      case 'UPDATE_TABLE':
        await updateTable(data.id, data);
        break;
      case 'CREATE_ORDER':
        await createQuickOrder(data);
        break;
      case 'UPDATE_ORDER':
        // 实现订单更新逻辑
        break;
      default:
        console.warn(`未知的同步操作: ${operation}`);
    }
  }

  // 离线创建桌台
  async createTableOffline(tableData) {
    // 生成临时ID
    const tempId = `temp_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const offlineTable = {
      ...tableData,
      id: tempId,
      isOffline: true,
      createdAt: new Date().toISOString()
    };

    // 保存到本地存储
    const tables = localStorageService.getData('tables', []);
    tables.push(offlineTable);
    localStorageService.saveData('tables', tables);

    // 添加到同步队列
    localStorageService.addToSyncQueue('CREATE_TABLE', tableData);

    return offlineTable;
  }

  // 离线创建订单
  async createOrderOffline(orderData) {
    // 生成临时ID和订单号
    const tempId = `temp_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const orderNumber = `OFFLINE_${Date.now()}`;
    
    const offlineOrder = {
      ...orderData,
      id: tempId,
      order_number: orderNumber,
      isOffline: true,
      order_status: 'pending',
      created_at: new Date().toISOString()
    };

    // 保存到本地存储
    const orders = localStorageService.getData('orders', []);
    orders.push(offlineOrder);
    localStorageService.saveData('orders', orders);

    // 添加到同步队列
    localStorageService.addToSyncQueue('CREATE_ORDER', orderData);

    return offlineOrder;
  }

  // 获取本地桌台数据（在线+离线）
  async getTables(includeOffline = true) {
    try {
      // 尝试获取在线数据
      const onlineTables = await getAllTables();
      
      if (includeOffline) {
        // 合并离线数据
        const offlineTables = localStorageService.getData('tables', []);
        return [...onlineTables, ...offlineTables.filter(t => t.isOffline)];
      }
      
      return onlineTables;
    } catch (error) {
      // 网络错误时返回本地数据
      console.warn('获取在线桌台数据失败，使用本地缓存:', error);
      return localStorageService.getData('tables', []);
    }
  }

  // 获取本地订单数据（在线+离线）
  async getOrders(includeOffline = true) {
    try {
      // 尝试获取在线数据
      const onlineOrders = await getAllOrders();
      
      if (includeOffline) {
        // 合并离线数据
        const offlineOrders = localStorageService.getData('orders', []);
        return [...onlineOrders, ...offlineOrders.filter(o => o.isOffline)];
      }
      
      return onlineOrders;
    } catch (error) {
      // 网络错误时返回本地数据
      console.warn('获取在线订单数据失败，使用本地缓存:', error);
      return localStorageService.getData('orders', []);
    }
  }

  // 获取本地菜品数据
  async getDishes() {
    try {
      // 尝试获取在线数据
      const onlineDishes = await getDishes();
      // 缓存到本地
      localStorageService.saveData('dishes', onlineDishes);
      return onlineDishes;
    } catch (error) {
      // 网络错误时返回本地缓存
      console.warn('获取在线菜品数据失败，使用本地缓存:', error);
      return localStorageService.getData('dishes', []);
    }
  }

  // 检查离线状态
  isOffline() {
    return !localStorageService.isOnline();
  }

  // 获取同步状态
  getSyncStatus() {
    return {
      isSyncing: this.isSyncing,
      isOnline: localStorageService.isOnline(),
      pendingSyncCount: localStorageService.getSyncQueue().length,
      lastSyncTime: localStorageService.getLastSyncTime()
    };
  }

  // 清理资源
  destroy() {
    this.stopAutoSync();
    if (this.networkListener) {
      this.networkListener();
    }
  }
}

// 导出单例实例
export default new OfflineService();