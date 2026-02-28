<template>
  <div class="quick-order-container">
    <!-- Floating Quick Order Button -->
    <div 
      class="quick-order-btn" 
      @click="togglePanel"
      :class="{ 'active': isVisible }"
    >
      <el-icon v-if="!isVisible"><Lightning /></el-icon>
      <el-icon v-else><Close /></el-icon>
      <span class="btn-text">{{ isVisible ? '关闭' : '快单' }}</span>
    </div>

    <!-- Quick Order Panel -->
    <div v-if="isVisible" class="quick-order-panel" @click.stop>
      <div class="panel-header">
        <h3>快速下单</h3>
        <div style="display: flex; align-items: center; gap: 10px;">
          <el-tag v-if="isOffline" type="warning" size="small">离线模式</el-tag>
          <el-button @click="resetOrder" size="small" type="info" plain>重置</el-button>
        </div>
      </div>

      <div class="panel-content">
        <!-- Customer Info -->
        <div class="section">
          <h4>客户信息</h4>
          <el-input 
            v-model="orderInfo.customerName" 
            placeholder="客户姓名" 
            size="small"
            clearable
          />
          <el-input 
            v-model="orderInfo.customerPhone" 
            placeholder="联系电话" 
            size="small"
            style="margin-top: 8px;"
            clearable
          />
        </div>

        <!-- Order Type -->
        <div class="section">
          <h4>就餐方式</h4>
          <el-radio-group v-model="orderInfo.orderType" size="small">
            <el-radio-button label="dine_in">堂食</el-radio-button>
            <el-radio-button label="takeaway">外带</el-radio-button>
            <el-radio-button label="pack">打包</el-radio-button>
          </el-radio-group>
        </div>

        <!-- Table Selection (for dine-in) -->
        <div v-if="orderInfo.orderType === 'dine_in'" class="section">
          <h4>选择桌台</h4>
          <el-select 
            v-model="orderInfo.tableId" 
            placeholder="选择桌台" 
            size="small"
            style="width: 100%;"
            clearable
          >
            <el-option 
              v-for="table in availableTables" 
              :key="table.id" 
              :label="`${table.name} (${table.capacity}人)`" 
              :value="table.id"
            />
          </el-select>
        </div>

        <!-- Quick Dish Selection -->
        <div class="section">
          <h4>快速选择菜品</h4>
          <div class="quick-dish-grid">
            <div 
              v-for="dish in quickDishes" 
              :key="dish.id"
              class="quick-dish-item"
              @click="addDish(dish)"
            >
              <div class="dish-image">
                <img :src="dish.image" :alt="dish.name" />
              </div>
              <div class="dish-info">
                <div class="dish-name">{{ dish.name }}</div>
                <div class="dish-price">¥{{ dish.price }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Selected Items -->
        <div class="section">
          <h4>已选菜品 ({{ selectedItems.length }})</h4>
          <div class="selected-items">
            <div 
              v-for="(item, index) in selectedItems" 
              :key="index"
              class="selected-item"
            >
              <span class="item-name">{{ item.name }}</span>
              <div class="item-controls">
                <el-input-number 
                  v-model="item.quantity" 
                  :min="1" 
                  :max="99"
                  size="small"
                  @change="updateItemTotal(item)"
                />
                <span class="item-total">¥{{ (item.price * item.quantity).toFixed(2) }}</span>
                <el-button 
                  @click="removeItem(index)" 
                  size="small" 
                  type="danger" 
                  circle
                >
                  <el-icon><Delete /></el-icon>
                </el-button>
              </div>
            </div>
          </div>
        </div>

        <!-- Order Summary -->
        <div class="section">
          <h4>订单汇总</h4>
          <div class="order-summary">
            <div class="summary-row">
              <span>小计:</span>
              <span>¥{{ subtotal.toFixed(2) }}</span>
            </div>
            <div class="summary-row">
              <span>总计:</span>
              <span class="total-amount">¥{{ total.toFixed(2) }}</span>
            </div>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="panel-footer">
          <el-button @click="submitOrder" type="primary" :loading="submitting">
            {{ isOffline ? '离线保存' : '提交订单' }}
          </el-button>
          <el-button @click="togglePanel">取消</el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Lightning, Close, Delete } from '@element-plus/icons-vue'
import { createOrder } from '@/services/orderService'
import offlineService from '@/services/offlineService'

export default {
  name: 'QuickOrderPanel',
  components: {
    Lightning,
    Close,
    Delete
  },
  setup() {
    const isVisible = ref(false)
    const submitting = ref(false)
    const isOffline = ref(false)
    
    // Order information
    const orderInfo = ref({
      customerName: '',
      customerPhone: '',
      orderType: 'dine_in',
      tableId: null
    })
    
    // Selected items
    const selectedItems = ref([])
    
    // Mock data
    const availableTables = ref([
      { id: 1, name: 'T001', capacity: 4 },
      { id: 2, name: 'T002', capacity: 6 },
      { id: 3, name: 'T003', capacity: 8 }
    ])
    
    const quickDishes = ref([
      { id: 1, name: '宫保鸡丁', price: 28.00, image: 'https://img.yzcdn.cn/upload_files/2023/08/01/dish1.jpg' },
      { id: 2, name: '麻婆豆腐', price: 18.00, image: 'https://img.yzcdn.cn/upload_files/2023/08/01/dish2.jpg' },
      { id: 3, name: '红烧肉', price: 38.00, image: 'https://img.yzcdn.cn/upload_files/2023/08/01/dish3.jpg' },
      { id: 4, name: '鱼香肉丝', price: 26.00, image: 'https://img.yzcdn.cn/upload_files/2023/08/01/dish4.jpg' },
      { id: 5, name: '酸辣汤', price: 12.00, image: 'https://img.yzcdn.cn/upload_files/2023/08/01/dish5.jpg' },
      { id: 6, name: '白米饭', price: 2.00, image: 'https://img.yzcdn.cn/upload_files/2023/08/01/dish6.jpg' }
    ])
    
    // Computed properties
    const subtotal = computed(() => {
      return selectedItems.value.reduce((sum, item) => {
        return sum + (item.price * item.quantity)
      }, 0)
    })
    
    const total = computed(() => {
      return subtotal.value
    })
    
    // Methods
    const togglePanel = () => {
      isVisible.value = !isVisible.value
    }
    
    const addDish = (dish) => {
      const existingItem = selectedItems.value.find(item => item.id === dish.id)
      if (existingItem) {
        existingItem.quantity += 1
        updateItemTotal(existingItem)
      } else {
        selectedItems.value.push({
          ...dish,
          quantity: 1,
          total: dish.price
        })
      }
      ElMessage.success(`已添加 ${dish.name}`)
    }
    
    const removeItem = (index) => {
      selectedItems.value.splice(index, 1)
    }
    
    const updateItemTotal = (item) => {
      item.total = item.price * item.quantity
    }
    
    const resetOrder = () => {
      orderInfo.value = {
        customerName: '',
        customerPhone: '',
        orderType: 'dine_in',
        tableId: null
      }
      selectedItems.value = []
      ElMessage.info('订单已重置')
    }
    
    const submitOrder = async () => {
      if (selectedItems.value.length === 0) {
        ElMessage.warning('请至少选择一个菜品')
        return
      }
      
      if (orderInfo.value.orderType === 'dine_in' && !orderInfo.value.tableId) {
        ElMessage.warning('请选择桌台')
        return
      }
      
      if (!orderInfo.value.customerName) {
        ElMessage.warning('请输入客户姓名')
        return
      }

      submitting.value = true
      
      try {
        const orderData = {
          customer_name: orderInfo.value.customerName,
          customer_phone: orderInfo.value.customerPhone || null,
          table_id: orderInfo.value.tableId,
          order_type: orderInfo.value.orderType,
          payment_method: 'cash',
          order_items: selectedItems.value.map(item => ({
            dish_id: item.id,
            quantity: item.quantity,
            unit_price: item.price,
            total_price: item.total
          }))
        }
        
        let result
        if (isOffline.value) {
          // 离线模式
          result = await offlineService.createOrderOffline(orderData)
          ElMessage.success('订单已保存到本地，网络恢复后将自动同步')
        } else {
          // 在线模式
          result = await createOrder(orderData)
          ElMessage.success('订单提交成功！')
        }
        
        resetOrder()
        togglePanel()
      } catch (error) {
        console.error('提交订单失败:', error)
        ElMessage.error('提交订单失败: ' + (error.response?.data?.detail || error.message))
      } finally {
        submitting.value = false
      }
    }
    
    // Close panel when clicking outside
    const handleClickOutside = (event) => {
      if (isVisible.value && !event.target.closest('.quick-order-panel') && !event.target.closest('.quick-order-btn')) {
        isVisible.value = false
      }
    }
    
    // Initialize
    let networkListener
    onMounted(() => {
      isOffline.value = offlineService.isOffline()
      networkListener = offlineService.setupNetworkListener()
      document.addEventListener('click', handleClickOutside)
    })
    
    onUnmounted(() => {
      if (networkListener) {
        networkListener()
      }
      document.removeEventListener('click', handleClickOutside)
    })
    
    return {
      isVisible,
      submitting,
      isOffline,
      orderInfo,
      selectedItems,
      availableTables,
      quickDishes,
      subtotal,
      total,
      togglePanel,
      addDish,
      removeItem,
      updateItemTotal,
      resetOrder,
      submitOrder,
      handleClickOutside
    }
  }
}
</script>

<style scoped>
.quick-order-container {
  position: fixed;
  bottom: 30px;
  right: 30px;
  z-index: 1000;
}

.quick-order-btn {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: linear-gradient(135deg, #4361ee, #3f37c9);
  color: white;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 4px 20px rgba(67, 97, 238, 0.3);
  transition: all 0.3s ease;
  border: none;
}

.quick-order-btn:hover {
  transform: scale(1.05);
  box-shadow: 0 6px 25px rgba(67, 97, 238, 0.4);
}

.quick-order-btn.active {
  background: linear-gradient(135deg, #e74c3c, #c0392b);
  transform: rotate(45deg);
}

.btn-text {
  font-size: 12px;
  margin-top: 4px;
  font-weight: 500;
}

.quick-order-panel {
  position: absolute;
  bottom: 100px;
  right: 0;
  width: 400px;
  max-height: 80vh;
  background: white;
  border-radius: 15px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  overflow: hidden;
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.panel-header {
  padding: 20px;
  background: linear-gradient(90deg, #4361ee, #3f37c9);
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.panel-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.panel-content {
  padding: 20px;
  overflow-y: auto;
  max-height: calc(80vh - 80px);
}

.section {
  margin-bottom: 20px;
}

.section h4 {
  margin: 0 0 12px 0;
  color: #2b2d42;
  font-size: 14px;
  font-weight: 600;
}

.quick-dish-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
}

.quick-dish-item {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: center;
}

.quick-dish-item:hover {
  border-color: #4361ee;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(67, 97, 238, 0.1);
}

.dish-image {
  width: 100%;
  height: 60px;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 8px;
}

.dish-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.dish-name {
  font-size: 12px;
  font-weight: 500;
  color: #2b2d42;
  margin-bottom: 4px;
}

.dish-price {
  font-size: 14px;
  font-weight: 700;
  color: #4361ee;
}

.selected-items {
  max-height: 200px;
  overflow-y: auto;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 10px;
}

.selected-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.selected-item:last-child {
  border-bottom: none;
}

.item-name {
  flex: 1;
  font-size: 14px;
  color: #2b2d42;
}

.item-controls {
  display: flex;
  align-items: center;
  gap: 10px;
}

.item-total {
  font-weight: 600;
  color: #4361ee;
  min-width: 60px;
  text-align: right;
}

.order-summary {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 15px;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 14px;
}

.summary-row:last-child {
  margin-bottom: 0;
}

.total-amount {
  font-size: 16px;
  font-weight: 700;
  color: #e74c3c;
}

.panel-footer {
  display: flex;
  gap: 10px;
  padding-top: 20px;
}

.panel-footer .el-button {
  flex: 1;
}

/* Responsive design */
@media (max-width: 768px) {
  .quick-order-panel {
    width: 320px;
    right: -20px;
  }
  
  .quick-dish-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>