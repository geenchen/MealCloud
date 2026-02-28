<template>
  <div class="order">
    <van-nav-bar 
      title="提交订单" 
      left-text="返回"
      left-arrow
      @click-left="$router.back()"
    />
    
    <!-- 收货/就餐信息 -->
    <van-cell-group title="订单信息" inset>
      <van-field
        v-model="order.customerName"
        label="姓名"
        placeholder="请输入姓名（可选）"
        :border="false"
      />
      <van-field
        v-model="order.customerPhone"
        label="电话"
        placeholder="请输入联系电话（可选）"
        :border="false"
      />
      
      <!-- 就餐方式选择 -->
      <van-cell title="就餐桌台" :value="diningOptionText" is-link @click="showDiningOptions = true" />
      
      <!-- 如果选择了具体桌台，显示桌台详情 -->
      <van-cell 
        v-if="order.diningOption === 'table' && order.table" 
        :title="`桌台: ${order.table.name}`" 
        :label="`${order.table.area} - ${order.table.capacity}人桌`"
      />
    </van-cell-group>

    <!-- 订单商品 -->
    <van-cell-group title="订单商品" inset style="margin-top: 10px;">
      <van-cell 
        v-for="item in orderItems" 
        :key="item.id" 
        :border="false"
      >
        <div class="order-item">
          <span class="item-name">{{ item.name }}</span>
          <span class="item-price">¥{{ item.price }}</span>
          <span class="item-quantity">x{{ item.quantity }}</span>
          <span class="item-subtotal">¥{{ (item.price * item.quantity).toFixed(2) }}</span>
        </div>
      </van-cell>
      <van-cell>
        <div class="order-summary">
          <div class="summary-row">
            <span>小计</span>
            <span>¥{{ subtotal.toFixed(2) }}</span>
          </div>
          <div class="summary-row">
            <span>打包费</span>
            <span>+¥{{ order.packingFee.toFixed(2) }}</span>
          </div>
          <div class="summary-row total">
            <span>总计</span>
            <span class="total-price">¥{{ total.toFixed(2) }}</span>
          </div>
        </div>
      </van-cell>
    </van-cell-group>

    <!-- 特殊要求 -->
    <van-cell-group title="特殊要求" inset style="margin-top: 10px;">
      <van-field
        v-model="order.specialRequests"
        rows="2"
        autosize
        type="textarea"
        maxlength="100"
        placeholder="请输入特殊要求（如：不要香菜、微辣等）"
        show-word-limit
      />
    </van-cell-group>

    <!-- 支付方式 -->
    <van-cell-group title="支付方式" inset style="margin-top: 10px;">
      <van-radio-group v-model="order.paymentMethod" direction="vertical">
        <van-cell title="现金支付" clickable @click="order.paymentMethod = 'cash'">
          <template #right-icon>
            <van-radio name="cash" />
          </template>
        </van-cell>
        <van-cell title="微信支付" clickable @click="order.paymentMethod = 'wechat'">
          <template #right-icon>
            <van-radio name="wechat" />
          </template>
        </van-cell>
        <van-cell title="支付宝" clickable @click="order.paymentMethod = 'alipay'">
          <template #right-icon>
            <van-radio name="alipay" />
          </template>
        </van-cell>
        <van-cell title="混合支付" clickable @click="order.paymentMethod = 'mixed'">
          <template #right-icon>
            <van-radio name="mixed" />
          </template>
        </van-cell>
        <van-cell 
          v-if="isRegularCustomer" 
          title="赊账" 
          clickable 
          @click="order.paymentMethod = 'credit'"
        >
          <template #right-icon>
            <van-radio name="credit" />
          </template>
        </van-cell>
      </van-radio-group>
    </van-cell-group>

    <!-- 悬浮提交按钮 -->
    <div class="order-footer">
      <div class="total-info">
        <p>合计: <span class="total-price">¥{{ total.toFixed(2) }}</span></p>
      </div>
      <van-button 
        type="primary" 
        size="large" 
        :loading="submitting"
        @click="submitOrder"
      >
        提交订单
      </van-button>
    </div>
    
    <!-- 就餐方式选择弹窗 -->
    <van-action-sheet 
      v-model:show="showDiningOptions" 
      :actions="diningActions" 
      @select="onDiningOptionSelect"
      cancel-text="取消"
      description="请选择就餐方式"
    />
    
    <!-- 桌台选择弹窗 -->
    <van-popup v-model:show="showTableSelection" position="bottom" round>
      <van-picker
        :columns="tableColumns"
        @cancel="showTableSelection = false"
        @confirm="onTableConfirm"
      />
    </van-popup>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { Toast, Dialog } from 'vant'

export default {
  name: 'Order',
  setup() {
    // 订单初始数据
    const order = ref({
      customerName: '',
      customerPhone: '',
      diningOption: 'takeout', // dine_in, takeout, pack, preorder, table
      table: null, // 选中的桌台
      specialRequests: '',
      paymentMethod: 'cash',
      packingFee: 0,
      orderType: 'takeaway' // 默认外带
    })

    // 示例订单项
    const orderItems = ref([
      { id: 1, name: '宫保鸡丁', price: 28.00, quantity: 1 },
      { id: 2, name: '白米饭', price: 2.00, quantity: 2 }
    ])

    const showDiningOptions = ref(false)
    const showTableSelection = ref(false)
    const submitting = ref(false)
    
    // 模拟用户是否为常客
    const isRegularCustomer = ref(true)

    // 就餐选项
    const diningActions = ref([
      { name: '堂食', value: 'dine_in', description: '在店内用餐' },
      { name: '外带', value: 'takeout', description: '取餐号模式' },
      { name: '打包', value: 'pack', description: '带包装离开' },
      { name: '预约', value: 'preorder', description: '预定未来时间' },
      { name: '选择桌台', value: 'table', description: '指定具体桌台', color: '#ee0a24' },
      { name: '老板下单', value: 'boss_order', description: '由老板代为下单', color: '#3884ff' }
    ])

    // 模拟桌台数据
    const tables = ref([
      { id: 1, name: 'T001', area: '大厅', capacity: 4, status: 'available' },
      { id: 2, name: 'T002', area: '包间', capacity: 8, status: 'available' },
      { id: 3, name: 'T003', area: '大厅', capacity: 2, status: 'occupied' },
      { id: 4, name: 'T004', area: '雅座', capacity: 6, status: 'available' }
    ])

    // 桌台列数据
    const tableColumns = computed(() => {
      return tables.value
        .filter(table => table.status === 'available') // 只显示可用桌台
        .map(table => ({
          text: `${table.name}(${table.area}-${table.capacity}人)`,
          value: table.id,
          ...table
        }))
    })

    // 计算属性
    const subtotal = computed(() => {
      return orderItems.value.reduce((sum, item) => sum + (item.price * item.quantity), 0)
    })

    const total = computed(() => {
      return subtotal.value + order.value.packingFee
    })

    const diningOptionText = computed(() => {
      const option = diningActions.value.find(opt => opt.value === order.value.diningOption)
      return option ? option.name : '选择就餐桌台'
    })

    // 方法
    const onDiningOptionSelect = (action) => {
      showDiningOptions.value = false
      
      if (action.value === 'table') {
        // 如果选择桌台，显示桌台选择器
        if (tableColumns.value.length > 0) {
          showTableSelection.value = true
        } else {
          Toast('暂无可用餐台')
        }
      } else if (action.value === 'pack') {
        // 打包需要额外收取打包费
        order.value.packingFee = 1.00
      } else {
        // 其他选项取消打包费
        order.value.packingFee = 0
      }
      
      // 更新订单类型
      order.value.diningOption = action.value
      switch(action.value) {
        case 'dine_in':
        case 'table':
          order.value.orderType = 'dine_in'
          break
        case 'takeout':
          order.value.orderType = 'takeaway'
          break
        case 'pack':
          order.value.orderType = 'pack'
          break
        case 'preorder':
          order.value.orderType = 'preorder'
          break
        default:
          order.value.orderType = 'takeaway'
      }
    }

    const onTableConfirm = (value, index) => {
      // 确认选择桌台
      const selectedTable = tables.value.find(table => table.id === value)
      if (selectedTable) {
        order.value.table = selectedTable
        order.value.diningOption = 'table'
        Toast.success(`已选择${selectedTable.name}`)
      }
      showTableSelection.value = false
    }

    const submitOrder = () => {
      if (submitting.value) return
      
      // 显示确认对话框
      Dialog.confirm({
        title: '确认订单',
        message: `请确认订单信息\n\n总计: ¥${total.value.toFixed(2)}\n就餐方式: ${diningOptionText.value}\n支付方式: ${getPaymentMethodName(order.value.paymentMethod)}`,
      }).then(() => {
        // 提交订单
        submitting.value = true
        
        // 模拟API调用
        setTimeout(() => {
          submitting.value = false
          Toast.success('订单提交成功！')
          
          // 返回首页
          setTimeout(() => {
            // 这里应该导航到订单详情或首页
            console.log('订单已提交:', order.value)
          }, 1000)
        }, 1500)
      }).catch(() => {
        // 用户取消
      })
    }

    const getPaymentMethodName = (method) => {
      const methods = {
        'cash': '现金支付',
        'wechat': '微信支付',
        'alipay': '支付宝',
        'mixed': '混合支付',
        'credit': '赊账'
      }
      return methods[method] || '未知支付方式'
    }

    return {
      order,
      orderItems,
      showDiningOptions,
      showTableSelection,
      submitting,
      isRegularCustomer,
      diningActions,
      tableColumns,
      subtotal,
      total,
      diningOptionText,
      onDiningOptionSelect,
      onTableConfirm,
      submitOrder,
      getPaymentMethodName
    }
  }
}
</script>

<style scoped>
.order-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f5f5f5;
}

.item-name {
  flex: 2;
  color: #333;
}

.item-price {
  flex: 1;
  color: #ee0a24;
  text-align: center;
}

.item-quantity {
  flex: 1;
  text-align: center;
}

.item-subtotal {
  flex: 1;
  color: #ee0a24;
  text-align: right;
  font-weight: bold;
}

.order-summary {
  width: 100%;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  padding: 5px 0;
  font-size: 14px;
}

.summary-row.total {
  padding: 10px 0;
  border-top: 1px solid #f5f5f5;
  font-weight: bold;
  font-size: 16px;
}

.total-price {
  color: #ee0a24;
  font-weight: bold;
}

.order-footer {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 15px 16px;
  background: #fff;
  box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.total-info {
  flex: 1;
  text-align: left;
  margin-right: 15px;
}

.total-info .total-price {
  font-size: 18px;
}
</style>