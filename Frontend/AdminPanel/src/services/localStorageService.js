class LocalStorageService {
  constructor() {
    this.storageKey = 'mealcloud_data';
    this.syncQueueKey = 'mealcloud_sync_queue';
    this.lastSyncKey = 'mealcloud_last_sync';
  }

  // 保存数据到本地存储
  saveData(key, data) {
    try {
      const storage = this.getStorage();
      storage[key] = data;
      localStorage.setItem(this.storageKey, JSON.stringify(storage));
      return true;
    } catch (error) {
      console.error('保存本地数据失败:', error);
      return false;
    }
  }

  // 从本地存储获取数据
  getData(key, defaultValue = null) {
    try {
      const storage = this.getStorage();
      return storage[key] !== undefined ? storage[key] : defaultValue;
    } catch (error) {
      console.error('获取本地数据失败:', error);
      return defaultValue;
    }
  }

  // 删除本地数据
  removeData(key) {
    try {
      const storage = this.getStorage();
      delete storage[key];
      localStorage.setItem(this.storageKey, JSON.stringify(storage));
      return true;
    } catch (error) {
      console.error('删除本地数据失败:', error);
      return false;
    }
  }

  // 获取所有本地存储数据
  getAllData() {
    return this.getStorage();
  }

  // 清空所有本地数据
  clearAllData() {
    try {
      localStorage.removeItem(this.storageKey);
      localStorage.removeItem(this.syncQueueKey);
      localStorage.removeItem(this.lastSyncKey);
      return true;
    } catch (error) {
      console.error('清空本地数据失败:', error);
      return false;
    }
  }

  // 获取存储对象
  getStorage() {
    try {
      const data = localStorage.getItem(this.storageKey);
      return data ? JSON.parse(data) : {};
    } catch (error) {
      console.error('解析本地存储失败:', error);
      return {};
    }
  }

  // 添加到同步队列
  addToSyncQueue(operation, data) {
    try {
      const queue = this.getSyncQueue();
      const syncItem = {
        id: Date.now() + Math.random(),
        timestamp: new Date().toISOString(),
        operation,
        data
      };
      queue.push(syncItem);
      localStorage.setItem(this.syncQueueKey, JSON.stringify(queue));
      return syncItem.id;
    } catch (error) {
      console.error('添加到同步队列失败:', error);
      return null;
    }
  }

  // 获取同步队列
  getSyncQueue() {
    try {
      const queue = localStorage.getItem(this.syncQueueKey);
      return queue ? JSON.parse(queue) : [];
    } catch (error) {
      console.error('获取同步队列失败:', error);
      return [];
    }
  }

  // 从同步队列移除项目
  removeFromSyncQueue(itemId) {
    try {
      const queue = this.getSyncQueue();
      const filteredQueue = queue.filter(item => item.id !== itemId);
      localStorage.setItem(this.syncQueueKey, JSON.stringify(filteredQueue));
      return true;
    } catch (error) {
      console.error('从同步队列移除失败:', error);
      return false;
    }
  }

  // 清空同步队列
  clearSyncQueue() {
    try {
      localStorage.removeItem(this.syncQueueKey);
      return true;
    } catch (error) {
      console.error('清空同步队列失败:', error);
      return false;
    }
  }

  // 设置最后同步时间
  setLastSyncTime() {
    try {
      localStorage.setItem(this.lastSyncKey, new Date().toISOString());
      return true;
    } catch (error) {
      console.error('设置最后同步时间失败:', error);
      return false;
    }
  }

  // 获取最后同步时间
  getLastSyncTime() {
    try {
      return localStorage.getItem(this.lastSyncKey);
    } catch (error) {
      console.error('获取最后同步时间失败:', error);
      return null;
    }
  }

  // 检查是否在线
  isOnline() {
    return navigator.onLine;
  }

  // 监听网络状态变化
  onNetworkStatusChange(callback) {
    const handleOnline = () => callback(true);
    const handleOffline = () => callback(false);
    
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    
    // 返回清理函数
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }
}

// 导出单例实例
export default new LocalStorageService();