<template>
  <div class="order-entry">
    <el-card>
      <template #header>
        <div class="page-header">
          <span>快速下单</span>
          <el-tag type="warning" effect="light">新手引导模式</el-tag>
        </div>
      </template>

      <el-alert
        title="建议流程：1. 填客户信息 2. 选订单类型与桌台 3. 选菜 4. 提交订单"
        type="warning"
        :closable="false"
        show-icon
        class="guide-alert"
      />

      <el-steps :active="currentStep" align-center finish-status="success" class="guide-steps">
        <el-step title="客户信息" />
        <el-step title="订单与桌台" />
        <el-step title="选择菜品" />
        <el-step title="确认提交" />
      </el-steps>

      <el-row :gutter="20">
        <el-col :span="16">
          <el-card shadow="never" class="section-card">
            <template #header>
              <div class="section-header">客户信息</div>
            </template>
            <el-form :model="customerInfo" label-width="90px">
              <el-row :gutter="20">
                <el-col :span="12">
                  <el-form-item label="客户姓名">
                    <el-input v-model="customerInfo.name" placeholder="选填，赊账/预定建议填写" />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="联系电话">
                    <el-input v-model="customerInfo.phone" placeholder="选填，赊账/预定建议填写" />
                  </el-form-item>
                </el-col>
              </el-row>
            </el-form>
          </el-card>

          <el-card shadow="never" class="section-card">
            <template #header>
              <div class="section-header">订单信息</div>
            </template>
            <el-form :model="orderInfo" label-width="100px">
              <el-row :gutter="20">
                <el-col :span="12">
                  <el-form-item label="订单类型" required>
                    <el-select v-model="orderInfo.type" style="width: 100%" @change="onOrderTypeChange">
                      <el-option label="堂食" value="dine_in" />
                      <el-option label="外带" value="takeaway" />
                      <el-option label="打包" value="pack" />
                      <el-option label="预定" value="preorder" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="支付方式" required>
                    <el-select v-model="orderInfo.paymentMethod" style="width: 100%">
                      <el-option label="现金" value="cash" />
                      <el-option label="微信" value="wechat" />
                      <el-option label="支付宝" value="alipay" />
                      <el-option label="混合支付" value="mixed" />
                      <el-option label="赊账" value="credit" />
                    </el-select>
                  </el-form-item>
                </el-col>
              </el-row>

              <el-form-item label="桌台选择" v-if="['dine_in', 'preorder'].includes(orderInfo.type)">
                <div class="table-select-row">
                  <el-button type="warning" plain @click="openTableSelectionDialog">选择桌台</el-button>
                  <el-tag v-if="selectedTable" type="success" effect="light">
                    已选：{{ selectedTable.name || selectedTable.table_number }} / {{ selectedTable.area_name || '大厅' }}
                  </el-tag>
                  <el-tag v-else type="info" effect="plain">未选择桌台</el-tag>
                  <el-button v-if="selectedTableId" link type="danger" @click="clearSelectedTable">清除</el-button>
                </div>
              </el-form-item>

              <el-form-item label="特殊要求">
                <el-input v-model="orderInfo.specialRequests" type="textarea" :rows="2" placeholder="如：少辣、先上凉菜" />
              </el-form-item>

              <el-form-item label="预定时间" v-if="orderInfo.type === 'preorder'" required>
                <el-date-picker
                  v-model="orderInfo.reservationTime"
                  type="datetime"
                  placeholder="请选择预定到店时间"
                  style="width: 100%"
                />
              </el-form-item>

              <el-form-item label="预定备注" v-if="orderInfo.type === 'preorder'">
                <el-input v-model="orderInfo.reservationNotes" type="textarea" :rows="2" placeholder="备注包间需求、生日布置等" />
              </el-form-item>
            </el-form>
          </el-card>

          <el-card shadow="never" class="section-card">
            <template #header>
              <div class="section-header">选择菜品</div>
            </template>

            <el-tabs v-if="categories.length > 0" v-model="activeCategory" type="card" v-loading="categoryLoading || dishLoading">
              <el-tab-pane v-for="category in categories" :key="category.id" :label="category.name" :name="String(category.id)">
                <div class="dish-grid" v-if="getDishesByCategory(category.id).length > 0">
                  <el-card
                    v-for="dish in getDishesByCategory(category.id)"
                    :key="dish.id"
                    class="dish-card"
                    @click="addDishToOrder(dish)"
                  >
                    <div class="dish-info">
                      <h4>{{ dish.name }}</h4>
                      <p class="dish-price">￥{{ Number(dish.price).toFixed(2) }}</p>
                      <p class="dish-desc" v-if="dish.description">{{ dish.description }}</p>
                    </div>
                  </el-card>
                </div>
                <el-empty v-else description="当前分类暂无可售菜品" :image-size="80" />
              </el-tab-pane>
            </el-tabs>
            <el-empty v-else-if="!categoryLoading" description="暂无分类，请先维护分类/菜品" :image-size="80" />
          </el-card>
        </el-col>

        <el-col :span="8">
          <el-card shadow="never" class="section-card sticky-summary">
            <template #header>
              <div class="section-header">订单预览</div>
            </template>

            <div class="order-preview" v-if="orderItems.length > 0">
              <div v-for="item in orderItems" :key="item.dishId" class="order-item">
                <div class="item-head">
                  <span class="item-name">{{ item.dishName }}</span>
                  <span class="item-subtotal">￥{{ (item.unitPrice * item.quantity).toFixed(2) }}</span>
                </div>
                <div class="item-ctrl">
                  <el-input-number v-model="item.quantity" :min="1" :max="99" size="small" @change="updateItemQuantity(item)" />
                  <el-button type="danger" size="small" plain @click="removeItemFromOrder(item.dishId)">移除</el-button>
                </div>
              </div>

              <el-divider />

              <div class="summary-row"><span>小计</span><span>￥{{ subtotal.toFixed(2) }}</span></div>
              <div class="summary-row fee">
                <span>打包费</span>
                <el-input-number v-model="orderInfo.packingFee" :min="0" :step="0.5" size="small" />
              </div>
              <div class="summary-row fee">
                <span>服务费</span>
                <el-input-number v-model="orderInfo.serviceFee" :min="0" :step="0.5" size="small" />
              </div>
              <div class="summary-row fee">
                <span>税费</span>
                <el-input-number v-model="orderInfo.tax" :min="0" :step="0.1" size="small" />
              </div>
              <div class="summary-row fee">
                <span>折扣</span>
                <el-input-number v-model="orderInfo.discount" :min="0" :step="0.5" size="small" />
              </div>
              <div class="summary-row total"><span>总计</span><span>￥{{ total.toFixed(2) }}</span></div>

              <div v-if="orderInfo.paymentMethod === 'mixed'" class="mixed-pay">
                <div class="summary-row fee"><span>现金</span><el-input-number v-model="orderInfo.cashAmount" :min="0" :step="0.01" size="small" /></div>
                <div class="summary-row fee"><span>微信</span><el-input-number v-model="orderInfo.wechatAmount" :min="0" :step="0.01" size="small" /></div>
                <div class="summary-row fee"><span>支付宝</span><el-input-number v-model="orderInfo.alipayAmount" :min="0" :step="0.01" size="small" /></div>
              </div>
            </div>
            <el-empty v-else description="请先选择菜品" :image-size="68" />
          </el-card>

          <el-card shadow="never" class="section-card">
            <template #header>
              <div class="section-header">操作</div>
            </template>

            <div class="submit-actions">
              <el-button type="primary" size="large" :disabled="orderItems.length === 0" @click="submitOrder">提交订单</el-button>
              <el-button size="large" @click="resetOrder">重置</el-button>
            </div>
            <p class="submit-tip">提示：堂食/预定建议先选桌台；赊账建议填写客户姓名和电话。</p>
          </el-card>
        </el-col>
      </el-row>
    </el-card>

    <el-dialog v-model="tableDialogVisible" title="选择桌台" width="760px" destroy-on-close>
      <div class="table-dialog-toolbar">
        <el-select v-model="tableFilterArea" clearable placeholder="筛选就餐区域" style="width: 220px">
          <el-option v-for="area in areaOptions" :key="area" :label="area" :value="area" />
        </el-select>
        <el-input v-model="tableKeyword" clearable placeholder="搜索桌号/桌名" style="width: 220px" />
      </div>

      <div class="table-dialog-grid">
        <div
          v-for="table in filteredTables"
          :key="table.id"
          class="table-card"
          :class="{ active: selectedTableDraftId === table.id }"
          @click="selectedTableDraftId = table.id"
        >
          <div class="table-card-head">
            <strong>{{ table.name || table.table_number }}</strong>
            <el-tag size="small" type="success">{{ table.capacity }}人</el-tag>
          </div>
          <div class="table-card-meta">{{ table.area_name || '大厅' }}</div>
          <div class="table-card-status">状态：{{ tableStatusLabel(table.status) }}</div>
        </div>
      </div>

      <el-empty v-if="filteredTables.length === 0" description="没有可选桌台" :image-size="70" />

      <template #footer>
        <el-button @click="tableDialogVisible = false">取消</el-button>
        <el-button type="primary" :disabled="!selectedTableDraftId" @click="confirmTableSelection">确认选择</el-button>
      </template>
    </el-dialog>
    <el-dialog v-model="submitConfirmVisible" title="?????" width="720px" destroy-on-close>
      <el-descriptions :column="1" border size="small">
        <el-descriptions-item label="????">{{ orderTypeLabel(orderInfo.type) }}</el-descriptions-item>
        <el-descriptions-item label="??">{{ selectedTable ? `${selectedTable.name || selectedTable.table_number} / ${selectedTable.area_name || '??'}` : (orderInfo.isSuspended ? '???????????' : '???') }}</el-descriptions-item>
        <el-descriptions-item label="??">{{ customerInfo.name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="??">{{ customerInfo.phone || '-' }}</el-descriptions-item>
        <el-descriptions-item label="????">{{ totalDishCount }} ?</el-descriptions-item>
        <el-descriptions-item label="????">{{ paymentMethodLabel(orderInfo.paymentMethod) }}</el-descriptions-item>
        <el-descriptions-item label="????"><span class="confirm-total">?{{ total.toFixed(2) }}</span></el-descriptions-item>
      </el-descriptions>

      <el-divider />

      <el-table :data="orderItems" size="small" stripe max-height="260">
        <el-table-column prop="dishName" label="??" min-width="200" />
        <el-table-column label="??" width="80">
          <template #default="scope">{{ scope.row.quantity }}</template>
        </el-table-column>
        <el-table-column label="??" width="120">
          <template #default="scope">?{{ Number(scope.row.unitPrice).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column label="??" width="120">
          <template #default="scope">?{{ (scope.row.unitPrice * scope.row.quantity).toFixed(2) }}</template>
        </el-table-column>
      </el-table>

      <template #footer>
        <el-button @click="submitConfirmVisible = false">????</el-button>
        <el-button type="primary" :loading="submitting" @click="executeSubmitOrder">????</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { computed, onMounted, ref, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { createOrder } from '@/services/orderService'
import { getCategories, getDishes } from '@/services/dishService'
import { getAllTables } from '@/services/tableService'

export default {
  name: 'OrderEntry',
  setup() {
    const customerInfo = ref({ name: '', phone: '' })

    const orderInfo = ref({
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
    })

    const orderItems = ref([])
    const dishes = ref([])
    const categories = ref([])
    const tables = ref([])
    const activeCategory = ref('')

    const dishLoading = ref(false)
    const categoryLoading = ref(false)
    const tableLoading = ref(false)

    const tableDialogVisible = ref(false)
    const selectedTableId = ref(null)
    const selectedTableDraftId = ref(null)
    const tableFilterArea = ref('')
    const tableKeyword = ref('')
    const submitConfirmVisible = ref(false)
    const submitting = ref(false)
    const pendingOrderData = ref(null)

    const currentStep = computed(() => {
      if (!orderItems.value.length) return 2
      if (!customerInfo.value.name && !customerInfo.value.phone) return 1
      return 3
    })

    const areaOptions = computed(() => {
      return [...new Set(tables.value.map((t) => t.area_name).filter(Boolean))]
    })

    const selectedTable = computed(() => {
      return tables.value.find((t) => t.id === selectedTableId.value) || null
    })

    const filteredTables = computed(() => {
      const keyword = tableKeyword.value.trim().toLowerCase()
      return tables.value
        .filter((t) => ['available', 'reserved'].includes(t.status))
        .filter((t) => (tableFilterArea.value ? t.area_name === tableFilterArea.value : true))
        .filter((t) => {
          if (!keyword) return true
          const txt = `${t.name || ''} ${t.table_number || ''}`.toLowerCase()
          return txt.includes(keyword)
        })
    })

    const subtotal = computed(() => orderItems.value.reduce((sum, item) => sum + item.unitPrice * item.quantity, 0))
    const totalDishCount = computed(() => orderItems.value.reduce((sum, item) => sum + item.quantity, 0))
    const total = computed(() => {
      const value = subtotal.value + orderInfo.value.packingFee + orderInfo.value.serviceFee + orderInfo.value.tax - orderInfo.value.discount
      return Math.max(value, 0)
    })

    const normalizeDish = (dish) => ({
      ...dish,
      id: Number(dish.id),
      categoryId: Number(dish.category_id ?? dish.categoryId ?? 0),
      price: Number(dish.price ?? 0),
      description: dish.description || ''
    })

    const getDishesByCategory = (categoryId) => {
      return dishes.value.filter((d) => d.categoryId === Number(categoryId))
    }

    const loadCategories = async () => {
      categoryLoading.value = true
      try {
        const data = await getCategories(0, 200)
        categories.value = Array.isArray(data) ? data : []
        if (!activeCategory.value && categories.value.length) {
          activeCategory.value = String(categories.value[0].id)
        }
      } catch (error) {
        console.error('加载分类失败:', error)
        ElMessage.error('加载分类失败')
      } finally {
        categoryLoading.value = false
      }
    }

    const loadDishes = async () => {
      dishLoading.value = true
      try {
        const data = await getDishes(0, 500)
        dishes.value = (Array.isArray(data) ? data : []).map(normalizeDish)
      } catch (error) {
        console.error('加载菜品失败:', error)
        ElMessage.error('加载菜品失败')
      } finally {
        dishLoading.value = false
      }
    }

    const loadTables = async () => {
      tableLoading.value = true
      try {
        const data = await getAllTables(0, 500)
        tables.value = Array.isArray(data) ? data : []
      } catch (error) {
        console.error('加载桌台失败:', error)
        ElMessage.error('加载桌台失败')
      } finally {
        tableLoading.value = false
      }
    }

    const addDishToOrder = (dish) => {
      const hit = orderItems.value.find((item) => item.dishId === dish.id)
      if (hit) {
        hit.quantity += 1
      } else {
        orderItems.value.push({
          dishId: dish.id,
          dishName: dish.name,
          unitPrice: Number(dish.price),
          quantity: 1,
          specialRequests: ''
        })
      }
      ElMessage.success(`已添加 ${dish.name}`)
    }

    const removeItemFromOrder = (dishId) => {
      orderItems.value = orderItems.value.filter((item) => item.dishId !== dishId)
    }

    const updateItemQuantity = (item) => {
      if (item.quantity <= 0) {
        removeItemFromOrder(item.dishId)
      }
    }

    const clearSelectedTable = () => {
      selectedTableId.value = null
    }

    const tableStatusLabel = (status) => {
      return {
        available: '空闲',
        reserved: '已预定',
        occupied: '占用中',
        cleaning: '清洁中',
        unavailable: '停用'
      }[status] || status
    }

    const openTableSelectionDialog = () => {
      selectedTableDraftId.value = selectedTableId.value
      tableDialogVisible.value = true
    }

    const confirmTableSelection = () => {
      selectedTableId.value = selectedTableDraftId.value
      tableDialogVisible.value = false
      if (selectedTable.value) {
        ElMessage.success(`已选择桌台 ${selectedTable.value.name || selectedTable.value.table_number}`)
      }
    }

    const onOrderTypeChange = (type) => {
      if (!['dine_in', 'preorder'].includes(type)) {
        selectedTableId.value = null
      }
    }

    const validateMixedPay = () => {
      if (orderInfo.value.paymentMethod !== 'mixed') return true
      const totalPaid = orderInfo.value.cashAmount + orderInfo.value.wechatAmount + orderInfo.value.alipayAmount
      if (Math.abs(totalPaid - total.value) > 0.01) {
        ElMessage.warning('混合支付金额与订单总额不一致')
        return false
      }
      return true
    }

    const ensureTableForDineIn = async () => {
      if (!['dine_in', 'preorder'].includes(orderInfo.value.type)) return true
      if (selectedTableId.value) return true

      const action = await ElMessageBox.confirm(
        '当前未选择桌台。你可以先去选桌台，或创建挂起订单（稍后分配桌台）。',
        '缺少桌台',
        {
          confirmButtonText: '创建挂起订单',
          cancelButtonText: '去选择桌台',
          type: 'warning'
        }
      ).then(() => 'suspend').catch(() => 'pick')

      if (action === 'pick') {
        openTableSelectionDialog()
        return false
      }

      orderInfo.value.isSuspended = true
      return true
    }

    const orderTypeLabel = (type) => ({ dine_in: '堂食', takeaway: '外带', pack: '打包', preorder: '预定' }[type] || type)

    const paymentMethodLabel = (method) => ({
      cash: '现金',
      wechat: '微信',
      alipay: '支付宝',
      mixed: '混合支付',
      credit: '赊账'
    }[method] || method)

    const buildOrderPayload = () => {
      const now = new Date()
      if (['takeaway', 'pack'].includes(orderInfo.value.type)) {
        orderInfo.value.takeoutNumber = `TK${now.getHours().toString().padStart(2, '0')}${Math.floor(Math.random() * 100)
          .toString()
          .padStart(2, '0')}`
      }

      const paidAmount =
        orderInfo.value.paymentMethod === 'mixed'
          ? orderInfo.value.cashAmount + orderInfo.value.wechatAmount + orderInfo.value.alipayAmount
          : orderInfo.value.paymentMethod === 'credit'
            ? 0
            : total.value

      const paymentStatus = paidAmount <= 0 ? 'pending' : paidAmount >= total.value ? 'paid' : 'partial'

      return {
        order_number: `ORD-${Date.now()}`,
        customer_name: customerInfo.value.name || null,
        customer_phone: customerInfo.value.phone || null,
        table_id: selectedTableId.value || null,
        order_type: orderInfo.value.type,
        payment_method: orderInfo.value.paymentMethod,
        payment_status: paymentStatus,
        special_requests: orderInfo.value.specialRequests,
        subtotal: subtotal.value,
        tax: orderInfo.value.tax,
        service_fee: orderInfo.value.serviceFee,
        packing_fee: orderInfo.value.packingFee,
        discount: orderInfo.value.discount,
        total_amount: total.value,
        paid_amount: paidAmount,
        remaining_amount: total.value - paidAmount,
        is_suspended: orderInfo.value.isSuspended,
        takeout_number: orderInfo.value.takeoutNumber || null,
        reservation_time: orderInfo.value.reservationTime || null,
        reservation_notes: orderInfo.value.reservationNotes || null,
        is_takeout: ['takeaway', 'pack'].includes(orderInfo.value.type),
        order_items: orderItems.value.map((item) => ({
          dish_id: item.dishId,
          quantity: item.quantity,
          unit_price: item.unitPrice,
          total_price: item.unitPrice * item.quantity,
          special_requests: item.specialRequests || null
        }))
      }
    }

    const submitOrder = async () => {
      if (!orderItems.value.length) {
        ElMessage.warning('请先选择至少一个菜品')
        return
      }

      if (orderInfo.value.paymentMethod === 'credit' && (!customerInfo.value.name || !customerInfo.value.phone)) {
        ElMessage.warning('赊账订单请填写客户姓名和电话')
        return
      }

      if (orderInfo.value.type === 'preorder' && !orderInfo.value.reservationTime) {
        ElMessage.warning('预定订单请填写预定时间')
        return
      }

      if (!(await ensureTableForDineIn())) {
        return
      }

      if (!validateMixedPay()) {
        return
      }

      pendingOrderData.value = buildOrderPayload()
      submitConfirmVisible.value = true
    }

    const executeSubmitOrder = async () => {
      if (!pendingOrderData.value) {
        submitConfirmVisible.value = false
        return
      }

      submitting.value = true
      try {
        await createOrder(pendingOrderData.value)
        submitConfirmVisible.value = false
        ElMessage.success(`订单提交成功${orderInfo.value.takeoutNumber ? `，取餐号：${orderInfo.value.takeoutNumber}` : ''}`)
        pendingOrderData.value = null
        resetOrder()
      } catch (error) {
        console.error('提交订单失败:', error)
        ElMessage.error(error?.response?.data?.detail || '提交订单失败')
      } finally {
        submitting.value = false
      }
    }

    const resetOrder = () => {
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
      selectedTableId.value = null
      orderItems.value = []
      submitConfirmVisible.value = false
      pendingOrderData.value = null
    }

    watch(
      () => orderInfo.value.paymentMethod,
      (method) => {
        if (method !== 'mixed') {
          orderInfo.value.cashAmount = 0
          orderInfo.value.wechatAmount = 0
          orderInfo.value.alipayAmount = 0
        }
      }
    )

    onMounted(async () => {
      await Promise.allSettled([loadCategories(), loadDishes(), loadTables()])
    })

    return {
      customerInfo,
      orderInfo,
      orderItems,
      dishes,
      categories,
      tables,
      activeCategory,
      dishLoading,
      categoryLoading,
      tableLoading,
      tableDialogVisible,
      selectedTableId,
      selectedTableDraftId,
      tableFilterArea,
      tableKeyword,
      areaOptions,
      submitConfirmVisible,
      submitting,
      selectedTable,
      filteredTables,
      subtotal,
      total,
      totalDishCount,
      currentStep,
      getDishesByCategory,
      addDishToOrder,
      removeItemFromOrder,
      updateItemQuantity,
      clearSelectedTable,
      tableStatusLabel,
      orderTypeLabel,
      paymentMethodLabel,
      openTableSelectionDialog,
      confirmTableSelection,
      onOrderTypeChange,
      submitOrder,
      executeSubmitOrder,
      resetOrder
    }
  }
}
</script>

<style scoped>
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.guide-alert {
  margin-bottom: 14px;
}

.guide-steps {
  margin: 8px 0 18px;
}

.section-card {
  margin-bottom: 16px;
}

.section-header {
  font-weight: 700;
  color: #4b2c1c;
}

.table-select-row {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.dish-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 12px;
}

.dish-card {
  cursor: pointer;
  border: 1px solid #f0d8c6;
  transition: all 0.2s ease;
}

.dish-card:hover {
  transform: translateY(-2px);
  border-color: #dd8e5a;
  box-shadow: 0 6px 14px rgba(141, 71, 31, 0.16);
}

.dish-info h4 {
  margin: 0;
}

.dish-price {
  margin: 8px 0 4px;
  color: #c6542e;
  font-weight: 700;
}

.dish-desc {
  margin: 0;
  font-size: 12px;
  color: #8d705f;
}

.sticky-summary {
  position: sticky;
  top: 14px;
}

.order-preview {
  max-height: 420px;
  overflow: auto;
  padding-right: 4px;
}

.order-item {
  border: 1px solid #f0dfd3;
  border-radius: 10px;
  padding: 8px;
  margin-bottom: 8px;
  background: #fff9f4;
}

.item-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.item-name {
  font-weight: 600;
}

.item-subtotal {
  color: #c6542e;
  font-weight: 700;
}

.item-ctrl {
  margin-top: 8px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.summary-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin: 8px 0;
}

.summary-row.fee :deep(.el-input-number) {
  width: 120px;
}

.confirm-total {
  color: #c6542e;
  font-weight: 700;
  font-size: 16px;
}

.summary-row.total {
  font-size: 18px;
  font-weight: 700;
  color: #c6542e;
}

.submit-actions {
  display: flex;
  justify-content: center;
  gap: 10px;
}

.submit-tip {
  margin: 12px 0 0;
  font-size: 12px;
  color: #8d705f;
  text-align: center;
}

.table-dialog-toolbar {
  display: flex;
  gap: 10px;
  margin-bottom: 12px;
  flex-wrap: wrap;
}

.table-dialog-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(170px, 1fr));
  gap: 10px;
  margin-bottom: 8px;
}

.table-card {
  border: 1px solid #e9d4c5;
  border-radius: 10px;
  padding: 10px;
  cursor: pointer;
  background: #fffaf6;
  transition: all 0.2s;
}

.table-card:hover {
  border-color: #dd8e5a;
}

.table-card.active {
  border-color: #dd8e5a;
  box-shadow: 0 0 0 2px rgba(221, 142, 90, 0.2);
  background: #fff4ea;
}

.table-card-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 6px;
}

.table-card-meta,
.table-card-status {
  font-size: 12px;
  color: #7f6556;
}

@media (max-width: 992px) {
  .sticky-summary {
    position: static;
  }
}
</style>







