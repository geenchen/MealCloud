<template>
  <div class="order-entry">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>老板代客下单</span>
        </div>
      </template>
      
      <el-row :gutter="20">
        <el-col :span="16">
          <!-- 客户信息 -->
          <el-card shadow="never" style="margin-bottom: 20px;">
            <template #header>
              <div class="section-header">
                <span>客户信息</span>
              </div>
            </template>
            <el-form :model="customerInfo" label-width="100px">
              <el-row :gutter="20">
                <el-col :span="12">
                  <el-form-item label="客户姓名">
                    <el-input v-model="customerInfo.name" placeholder="请输入客户姓名" />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="联系电话">
                    <el-input v-model="customerInfo.phone" placeholder="请输入联系电话" />
                  </el-form-item>
                </el-col>
              </el-row>
            </el-form>
          </el-card>
          
          <!-- 订单信息 -->
          <el-card shadow="never" style="margin-bottom: 20px;">
            <template #header>
              <div class="section-header">
                <span>订单信息</span>
              </div>
            </template>
            <el-form :model="orderInfo" label-width="100px">
              <el-row :gutter="20">
                <el-col :span="12">
                  <el-form-item label="订单类型">
                    <el-select v-model="orderInfo.type" placeholder="请选择订单类型" style="width: 100%;">
                      <el-option label="堂食" value="dine_in" />
                      <el-option label="外带" value="takeaway" />
                      <el-option label="打包" value="pack" />
                      <el-option label="预约" value="preorder" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="支付方式">
                    <el-select v-model="orderInfo.paymentMethod" placeholder="请选择支付方式" style="width: 100%;">
                      <el-option label="现金" value="cash" />
                      <el-option label="微信" value="wechat" />
                      <el-option label="支付宝" value="alipay" />
                      <el-option label="混合支付" value="mixed" />
                      <el-option label="赊账" value="credit" />
                    </el-select>
                  </el-form-item>
                </el-col>
              </el-row>
              
              <el-form-item label="特殊要求">
                <el-input 
                  v-model="orderInfo.specialRequests" 
                  type="textarea" 
                  :rows="2"
                  placeholder="请输入特殊要求"
                />
              </el-form-item>
              
              <el-form-item label="预约时间" v-if="orderInfo.type === 'preorder'">
                <el-date-picker
                  v-model="orderInfo.reservationTime"
                  type="datetime"
                  placeholder="选择预约时间"
                  style="width: 100%;"
                />
              </el-form-item>
              
              <el-form-item label="预约备注" v-if="orderInfo.type === 'preorder'">
                <el-input 
                  v-model="orderInfo.reservationNotes" 
                  type="textarea" 
                  :rows="2"
                  placeholder="请输入预约备注"
                />
              </el-form-item>
            </el-form>
          </el-card>
          
          <!-- 菜品选择 -->
          <el-card shadow="never">
            <template #header>
              <div class="section-header">
                <span>选择菜品</span>
              </div>
            </template>
            
            <el-tabs v-model="activeCategory" type="card">
              <el-tab-pane 
                v-for="category in categories" 
                :key="category.id" 
                :label="category.name" 
                :name="category.id.toString()"
              >
                <div class="dish-grid">
                  <el-card 
                    v-for="dish in getDishesByCategory(category.id)" 
                    :key="dish.id"
                    class="dish-card"
                    @click="addDishToOrder(dish)"
                  >
                    <div class="dish-info">
                      <h4>{{ dish.name }}</h4>
                      <p class="dish-price">¥{{ dish.price }}</p>
                      <p class="dish-desc" v-if="dish.description">{{ dish.description }}</p>
                    </div>
                  </el-card>
                </div>
              </el-tab-pane>
            </el-tabs>
          </el-card>
        </el-col>
        
        <el-col :span="8">
          <!-- 订单预览 -->
          <el-card shadow="never" style="margin-bottom: 20px;">
            <template #header>
              <div class="section-header">
                <span>订单预览</span>
              </div>
            </template>
            
            <div class="order-preview">
              <div v-if="orderItems.length === 0" class="empty-order">
                <el-empty description="暂无菜品" :image-size="60" />
              </div>
              
              <div v-else>
                <div 
                  v-for="item in orderItems" 
                  :key="item.dishId"
                  class="order-item"
                >
                  <div class="item-info">
                    <span class="item-name">{{ item.dishName }}</span>
                    <span class="item-price">¥{{ item.unitPrice }}</span>
                  </div>
                  <div class="item-controls">
                    <el-input-number 
                      v-model="item.quantity" 
                      :min="1" 
                      :max="100"
                      size="small"
                      @change="updateItemQuantity(item)"
                    />
                    <span class="item-total">¥{{ (item.unitPrice * item.quantity).toFixed(2) }}</span>
                    <el-button 
                      type="danger" 
                      size="small" 
                      circle
                      @click="removeItemFromOrder(item.dishId)"
                    >
                      <el-icon><Delete /></el-icon>
                    </el-button>
                  </div>
                </div>
                
                <el-divider />
                
                <div class="order-summary">
                  <div class="summary-row">
                    <span>小计</span>
                    <span>¥{{ subtotal.toFixed(2) }}</span>
                  </div>
                  <div class="summary-row">
                    <span>打包费</span>
                    <el-input-number 
                      v-model="orderInfo.packingFee" 
                      :min="0" 
                      :step="0.5"
                      size="small"
                      style="width: 100px; margin-left: 10px;"
                    />
                  </div>
                  <div class="summary-row">
                    <span>服务费</span>
                    <el-input-number 
                      v-model="orderInfo.serviceFee" 
                      :min="0" 
                      :step="0.5"
                      size="small"
                      style="width: 100px; margin-left: 10px;"
                    />
                  </div>
                  <div class="summary-row">
                    <span>税费</span>
                    <el-input-number 
                      v-model="orderInfo.tax" 
                      :min="0" 
                      :step="0.1"
                      size="small"
                      style="width: 100px; margin-left: 10px;"
                    />
                  </div>
                  <div class="summary-row">
                    <span>折扣</span>
                    <el-input-number 
                      v-model="orderInfo.discount" 
                      :min="0" 
                      :step="0.5"
                      size="small"
                      style="width: 100px; margin-left: 10px;"
                    />
                  </div>
                  <el-divider />
                  <div class="summary-row total">
                    <span>总计</span>
                    <span class="total-amount">¥{{ total.toFixed(2) }}</span>
                  </div>
                  
                  <!--支付明细 -->
                  <div v-if="orderInfo.paymentMethod === 'mixed'">
                    <div class="summary-row">
                      <span>现金支付</span>
                      <el-input-number 
                        v-model="orderInfo.cashAmount" 
                        :min="0" 
                        :max="total"
                        :step="0.01"
                        size="small"
                        style="width: 100px; margin-left: 10px;"
                      />
                    </div>
                    <div class="summary-row">
                      <span>微信支付</span>
                      <el-input-number 
                        v-model="orderInfo.wechatAmount" 
                        :min="0" 
                        :max="total"
                        :step="0.01"
                        size="small"
                        style="width: 100px; margin-left: 10px;"
                      />
                    </div>
                    <div class="summary-row">
                      <span>支付宝支付</span>
                      <el-input-number 
                        v-model="orderInfo.alipayAmount" 
                        :min="0" 
                        :max="total"
                        :step="0.01"
                        size="small"
                        style="width: 100px; margin-left: 10px;"
                      />
                    </div>
                    <div class="summary-row total">
                      <span>支付总计</span>
                      <span class="total-amount">¥{{ (orderInfo.cashAmount + orderInfo.wechatAmount + orderInfo.alipayAmount).toFixed(2) }}</span>
                    </div>
                  </div>
                                    
                  <!--已付金额（用于部分支付） -->
                  <div class="summary-row" v-if="orderInfo.paymentMethod === 'partial'">
                    <span>已付金额</span>
                    <el-input-number 
                      v-model="orderInfo.paidAmount" 
                      :min="0" 
                      :max="total"
                      :step="0.01"
                      size="small"
                      style="width: 100px; margin-left: 10px;"
                    />
                  </div>
                </div>
              </div>
            </div>
          </el-card>
          
          <!-- 操作按钮 -->
          <el-card shadow="never">
            <template #header>
              <div class="section-header">
                <span>操作</span>
              </div>
            </template>
            
            <div style="text-align: center;">
              <el-button 
                type="primary" 
                size="large" 
                :disabled="orderItems.length === 0"
                @click="submitOrder"
              >
                提交订单
              </el-button>
              <el-button 
                size="large" 
                @click="resetOrder"
              >
                重置
              </el-button>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </el-card>
    
    <!-- 桌台选择对话框 -->
    <el-dialog v-model="tableDialogVisible" title="选择桌台" width="600px">
      <el-form :model="tableSelection" label-width="100px">
        <el-form-item label="就餐区域">
          <el-select v-model="tableSelection.area" placeholder="请选择区域" @change="filterTablesByArea">
            <el-option label="全部" value="" />
            <el-option label="大厅" value="大厅" />
            <el-option label="包间" value="包间" />
            <el-option label="雅座" value="雅座" />
            <el-option label="户外" value="户外" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="桌台选择">
          <el-radio-group v-model="tableSelection.selectedTableId">
            <el-row :gutter="10">
              <el-col 
                v-for="table in availableTables" 
                :key="table.id" 
                :span="6"
              >
                <el-radio :label="table.id">
                  <div class="table-option">
                    <div class="table-number">{{ table.name }}</div>
                    <div class="table-capacity">{{ table.capacity }}人</div>
                    <div class="table-area">{{ table.area }}</div>
                  </div>
                </el-radio>
              </el-col>
            </el-row>
          </el-radio-group>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="tableDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="confirmTableSelection">确认选择</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Delete } from '@element-plus/icons-vue'
import { createOrder } from '@/services/orderService'

export default {
  name: 'OrderEntry',
  components: {
    Delete
  },
  setup() {
    // 客户信息
    const customerInfo = ref({
      name: '',
      phone: ''
    })
    
    // 订单信息
    const orderInfo = ref({
      type: 'dine_in',
      paymentMethod: 'cash',
      specialRequests: '',
      packingFee: 0,
      serviceFee: 0,
      tax: 0,
      discount: 0,
      paidAmount: 0,
      isSuspended: false,  // 是否挂起（先下单后选桌）
      takeoutNumber: null,  // 取餐号
      //支付信息
      cashAmount: 0,
      wechatAmount: 0,
      alipayAmount: 0,
      //预约信息
      reservationTime: null,
      reservationNotes: ''
    })
    
    // 订单项
    const orderItems = ref([])
    
    // 示例菜品数据
    const dishes = ref([
      { id: 1, name: '宫保鸡丁', price: 28.00, description: '经典川菜，鸡肉嫩滑', categoryId: 1 },
      { id: 2, name: '麻婆豆腐', price: 18.00, description: '麻辣鲜香，豆腐嫩滑', categoryId: 1 },
      { id: 3, name: '红烧肉', price: 38.00, description: '肥瘦相间，甜咸适中', categoryId: 1 },
      { id: 4, name: '鱼香肉丝', price: 26.00, description: '酸甜可口，下饭神器', categoryId: 1 },
      { id: 5, name: '拍黄瓜', price: 10.00, description: '清爽解腻，开胃小菜', categoryId: 2 },
      { id: 6, name: '酸辣汤', price: 12.00, description: '酸辣开胃，营养丰富', categoryId: 3 },
      { id: 7, name: '白米饭', price: 2.00, description: '优质大米，粒粒分明', categoryId: 4 },
      { id: 8, name: '可乐', price: 5.00, description: '冰爽畅快，解辣必备', categoryId: 5 }
    ])
    
    // 示例分类数据
    const categories = ref([
      { id: 1, name: '热菜' },
      { id: 2, name: '凉菜' },
      { id: 3, name: '汤类' },
      { id: 4, name: '主食' },
      { id: 5, name: '饮品' }
    ])
    
    // 示例桌台数据
    const tables = ref([
      { id: 1, name: 'T001', area: '大厅', capacity: 4, status: 'available' },
      { id: 2, name: 'T002', area: '包间', capacity: 8, status: 'available' },
      { id: 3, name: 'T003', area: '大厅', capacity: 2, status: 'occupied' },
      { id: 4, name: 'T004', area: '雅座', capacity: 6, status: 'available' },
      { id: 5, name: 'T005', area: '大厅', capacity: 10, status: 'cleaning' },
      { id: 6, name: 'T006', area: '包间', capacity: 12, status: 'available' }
    ])
    
    // 当前选中的分类
    const activeCategory = ref('1')
    
    // 桌台选择相关
    const tableDialogVisible = ref(false)
    const tableSelection = ref({
      area: '',
      selectedTableId: null
    })
    
    // 计算属性
    const subtotal = computed(() => {
      return orderItems.value.reduce((sum, item) => sum + (item.unitPrice * item.quantity), 0)
    })
    
    const total = computed(() => {
      const calculatedTotal = subtotal.value + orderInfo.value.packingFee + orderInfo.value.serviceFee + orderInfo.value.tax - orderInfo.value.discount
      return Math.max(calculatedTotal, 0) // 确保不为负数
    })
    
    const availableTables = computed(() => {
      let filtered = tables.value.filter(table => table.status === 'available')
      
      if (tableSelection.value.area) {
        filtered = filtered.filter(table => table.area === tableSelection.value.area)
      }
      
      return filtered
    })
    
    // 方法
    const getDishesByCategory = (categoryId) => {
      return dishes.value.filter(dish => dish.categoryId === categoryId)
    }
    
    const addDishToOrder = (dish) => {
      // 检查是否已存在于订单中
      const existingItem = orderItems.value.find(item => item.dishId === dish.id)
      
      if (existingItem) {
        // 如果已存在，增加数量
        existingItem.quantity += 1
      } else {
        // 如果不存在，添加新项
        orderItems.value.push({
          dishId: dish.id,
          dishName: dish.name,
          unitPrice: dish.price,
          quantity: 1
        })
      }
      
      ElMessage.success(`已添加 ${dish.name}`)
    }
    
    const removeItemFromOrder = (dishId) => {
      const index = orderItems.value.findIndex(item => item.dishId === dishId)
      if (index !== -1) {
        orderItems.value.splice(index, 1)
        ElMessage.info('已从订单中移除')
      }
    }
    
    const updateItemQuantity = (item) => {
      if (item.quantity <= 0) {
        removeItemFromOrder(item.dishId)
      }
    }
    
    const showTableSelectionDialog = () => {
      tableDialogVisible.value = true
      // 重置选择
      tableSelection.value = {
        area: '',
        selectedTableId: null
      }
    }
    
    const filterTablesByArea = () => {
      // 过滤表格在 computed 属性中完成
    }
    
    const confirmTableSelection = () => {
      if (!tableSelection.value.selectedTableId) {
        ElMessage.warning('请选择桌台')
        return
      }
      
      // 这里可以将选中的桌台信息保存到订单中
      const selectedTable = tables.value.find(t => t.id === tableSelection.value.selectedTableId)
      console.log('选中桌台:', selectedTable)
      
      tableDialogVisible.value = false
      ElMessage.success(`已选择桌台: ${selectedTable.name}`)
    }
    
    const submitOrder = async () => {
      if (orderItems.value.length === 0) {
        ElMessage.warning('请至少选择一道菜')
        return
      }
      
      // 验证客户信息（对于赊账订单必须填写）
      if (orderInfo.value.paymentMethod === 'credit' && (!customerInfo.value.name || !customerInfo.value.phone)) {
        ElMessage.warning('赊账订单必须填写客户姓名和联系电话')
        return
      }
            
      //处理不同订单类型
      switch (orderInfo.value.type) {
        case 'dine_in':
          //订单处理
          if (!tableSelection.value.selectedTableId) {
            // 没有选择桌台，提供选择选项
            const action = await ElMessageBox.confirm(
              '您尚未选择桌台，是否创建挂起订单（稍后分配桌台）？',
              '桌台未选择',
              {
                confirmButtonText: '创建挂起订单',
                cancelButtonText: '选择桌台',
                type: 'warning'
              }
            ).catch(() => {
              showTableSelectionDialog()
              return 'cancel'
            })
                  
            if (action === 'confirm') {
              orderInfo.value.isSuspended = true
            } else if (action === 'cancel') {
              return
            }
          } else {
            orderInfo.value.isSuspended = false
          }
          break
                
        case 'takeaway':
        case 'pack':
          //外带/打包订单处理
          orderInfo.value.isSuspended = false
          // 生成取餐号
          const now = new Date()
          orderInfo.value.takeoutNumber = `TK${now.getHours().toString().padStart(2, '0')}${Math.floor(Math.random() * 100).toString().padStart(2, '0')}`
          break
                
        case 'preorder':
          //订单处理
          if (!tableSelection.value.selectedTableId) {
            ElMessage.warning('预约订单必须选择桌台')
            showTableSelectionDialog()
            return
          }
          if (!orderInfo.value.reservationTime) {
            ElMessage.warning('预约订单必须选择预约时间')
            return
          }
          orderInfo.value.isSuspended = false
          break
      }
            
      //处理混合支付
      if (orderInfo.value.paymentMethod === 'mixed') {
        const totalPaid = orderInfo.value.cashAmount + orderInfo.value.wechatAmount + orderInfo.value.alipayAmount
        if (Math.abs(totalPaid - total.value) > 0.01) { //考虑浮点数精度
          ElMessage.warning('混合支付金额与订单总额不匹配')
          return
        }
      }
      
      //准备订单数据
      const orderData = {
        order_number: `ORD-${Date.now()}`, // 生成订单号
        customer_name: customerInfo.value.name || null,
        customer_phone: customerInfo.value.phone || null,
        table_id: tableSelection.value.selectedTableId || null,
        order_type: orderInfo.value.type,
        payment_method: orderInfo.value.paymentMethod,
        special_requests: orderInfo.value.specialRequests,
        subtotal: subtotal.value,
        tax: orderInfo.value.tax,
        service_fee: orderInfo.value.serviceFee,
        packing_fee: orderInfo.value.packingFee,
        discount: orderInfo.value.discount,
        total_amount: total.value,
        paid_amount: orderInfo.value.paidAmount,
        remaining_amount: total.value - orderInfo.value.paidAmount,
        is_suspended: orderInfo.value.isSuspended,
        takeout_number: orderInfo.value.takeoutNumber || null,
        reservation_time: orderInfo.value.reservationTime || null,
        reservation_notes: orderInfo.value.reservationNotes || null,
        order_items: orderItems.value.map(item => ({
          dish_id: item.dishId,
          quantity: item.quantity,
          unit_price: item.unitPrice,
          total_price: item.unitPrice * item.quantity,
          special_requests: item.specialRequests || null
        }))
      }
            
      // 添加混合支付信息
      if (orderInfo.value.paymentMethod === 'mixed') {
        orderData.payment_details = {
          cash_amount: orderInfo.value.cashAmount,
          wechat_amount: orderInfo.value.wechatAmount,
          alipay_amount: orderInfo.value.alipayAmount
        }
      }
      
      try {
        // 调用后端API创建订单
        const response = await createOrder(orderData)
        ElMessage.success(`订单提交成功！${orderInfo.value.takeoutNumber ? `取餐号：${orderInfo.value.takeoutNumber}` : ''}`)
        
        // 重置表单
        resetOrder()
      } catch (error) {
        console.error('提交订单失败:', error)
        ElMessage.error('提交订单失败，请重试')
      }
    }
    
    const resetOrder = () => {
      // 重置所有数据
      customerInfo.value = { name: '', phone: '' }
      orderInfo.value = {
        type: 'dine_in',
        paymentMethod: 'cash',
        specialRequests: '',
        packingFee: 0,
        serviceFee: 0,
        tax: 0,
        discount: 0,
        paidAmount: 0,
        isSuspended: false,
        takeoutNumber: null,
        cashAmount: 0,
        wechatAmount: 0,
        alipayAmount: 0,
        reservationTime: null,
        reservationNotes: ''
      }
      orderItems.value = []
      tableSelection.value = {
        area: '',
        selectedTableId: null
      }
      
      ElMessage.info('订单已重置')
    }
    
    return {
      customerInfo,
      orderInfo,
      orderItems,
      dishes,
      categories,
      tables,
      activeCategory,
      tableDialogVisible,
      tableSelection,
      availableTables,
      subtotal,
      total,
      getDishesByCategory,
      addDishToOrder,
      removeItemFromOrder,
      updateItemQuantity,
      showTableSelectionDialog,
      filterTablesByArea,
      confirmTableSelection,
      submitOrder,
      resetOrder
    }
  }
}
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section-header {
  font-weight: bold;
  color: #303133;
}

.dish-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 15px;
}

.dish-card {
  cursor: pointer;
  transition: all 0.3s;
}

.dish-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.dish-info h4 {
  margin: 0 0 5px 0;
  font-size: 16px;
  font-weight: normal;
}

.dish-price {
  color: #f56c6c;
  font-weight: bold;
  margin: 5px 0;
}

.dish-desc {
  font-size: 12px;
  color: #909399;
  margin: 0;
}

.order-preview {
  max-height: 600px;
  overflow-y: auto;
}

.empty-order {
  text-align: center;
  padding: 40px 0;
}

.order-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px dashed #ebeef5;
}

.item-info {
  flex: 1;
}

.item-name {
  font-weight: 500;
}

.item-price {
  color: #909399;
  font-size: 12px;
  margin-left: 10px;
}

.item-controls {
  display: flex;
  align-items: center;
  gap: 8px;
}

.item-total {
  font-weight: bold;
  color: #f56c6c;
  min-width: 60px;
  text-align: right;
}

.order-summary {
  padding-top: 10px;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  padding: 5px 0;
  font-size: 14px;
}

.summary-row.total {
  font-weight: bold;
  font-size: 16px;
  color: #303133;
  padding-top: 10px;
}

.total-amount {
  color: #f56c6c;
  font-size: 18px;
}

.table-option {
  text-align: center;
  padding: 10px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  transition: all 0.3s;
}

.table-option:hover {
  border-color: #409eff;
}

.table-number {
  font-weight: bold;
  color: #303133;
}

.table-capacity {
  font-size: 12px;
  color: #909399;
}

.table-area {
  font-size: 12px;
  color: #c0c4cc;
}
</style>