<template>
  <div class="order">
    <van-empty v-if="cartStore.items.length === 0" description="当前没有可提交的菜品" />

    <template v-else>
      <van-cell-group title="客户信息" inset class="panel">
        <van-field v-model="form.customerName" label="姓名" placeholder="选填" />
        <van-field v-model="form.customerPhone" label="电话" placeholder="选填" />
      </van-cell-group>

      <van-cell-group title="订单设置" inset class="panel mt10">
        <van-field label="就餐方式">
          <template #input>
            <van-radio-group v-model="form.orderType" direction="horizontal">
              <van-radio name="dine_in">堂食</van-radio>
              <van-radio name="takeaway">外带</van-radio>
              <van-radio name="pack">打包</van-radio>
            </van-radio-group>
          </template>
        </van-field>

        <van-field
          v-if="form.orderType === 'dine_in'"
          label="就餐厅区"
          is-link
          readonly
          :model-value="form.diningArea || '请选择厅区'"
          @click="areaPickerVisible = true"
        />

        <van-field
          v-if="form.orderType === 'dine_in'"
          label="桌台"
          is-link
          readonly
          :model-value="selectedTableLabel"
          @click="openTablePicker"
        />

        <van-field label="支付方式">
          <template #input>
            <van-radio-group v-model="form.paymentMethod" direction="horizontal">
              <van-radio name="cash">现金</van-radio>
              <van-radio name="wechat">微信</van-radio>
              <van-radio name="alipay">支付宝</van-radio>
            </van-radio-group>
          </template>
        </van-field>

        <van-field v-model="form.specialRequests" label="备注" type="textarea" rows="2" maxlength="120" show-word-limit placeholder="口味、忌口等" />
      </van-cell-group>

      <van-cell-group title="菜品明细" inset class="panel mt10">
        <van-cell v-for="item in cartStore.items" :key="item.id" :title="item.name" :label="`x${item.quantity}`" :value="`¥${(Number(item.price) * Number(item.quantity)).toFixed(2)}`" />
        <van-cell title="小计" :value="`¥${subtotal.toFixed(2)}`" />
        <van-cell title="打包费" :value="`¥${packingFee.toFixed(2)}`" />
        <van-cell title="总计" :value="`¥${total.toFixed(2)}`" />
      </van-cell-group>

      <div class="footer">
        <div class="price">待支付 ¥{{ total.toFixed(2) }}</div>
        <van-button type="danger" :loading="submitting" @click="submitOrder">提交订单</van-button>
      </div>
    </template>

    <van-action-sheet v-model:show="areaPickerVisible" title="选择厅区">
      <div class="table-list">
        <van-empty v-if="areaOptions.length === 0" description="暂无可用厅区" />
        <van-cell
          v-for="area in areaOptions"
          :key="area"
          is-link
          :title="area"
          @click="selectArea(area)"
        />
      </div>
    </van-action-sheet>

    <van-action-sheet v-model:show="tablePickerVisible" title="选择桌台">
      <div class="table-list">
        <van-empty v-if="filteredTables.length === 0" description="当前厅区暂无可用桌台" />
        <van-cell
          v-for="table in filteredTables"
          :key="table.id"
          is-link
          :title="table.name || table.table_number"
          :label="`${table.area_name || '大厅'} · ${table.capacity}人`"
          @click="selectTable(table)"
        />
      </div>
    </van-action-sheet>
  </div>
</template>

<script>
import { computed, onMounted, onUnmounted, reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { showConfirmDialog, Toast } from 'vant'
import { useCartStore } from '@/stores/cart'
import { createOrder } from '@/services/orderService'
import { getAvailableTables } from '@/services/tableService'
import { ensureWechatAuth } from '@/services/authService'

const ORDER_IDS_KEY = 'wechat_order_ids'

const appendOrderId = (id) => {
  try {
    const raw = localStorage.getItem(ORDER_IDS_KEY)
    const list = raw ? JSON.parse(raw) : []
    const next = [id, ...list.filter((item) => Number(item) !== Number(id))].slice(0, 30)
    localStorage.setItem(ORDER_IDS_KEY, JSON.stringify(next))
  } catch {
    localStorage.setItem(ORDER_IDS_KEY, JSON.stringify([id]))
  }
}

export default {
  name: 'Order',
  setup() {
    const router = useRouter()
    const cartStore = useCartStore()

    const availableTables = ref([])
    const areaPickerVisible = ref(false)
    const tablePickerVisible = ref(false)
    const submitting = ref(false)
    const submitLock = ref(false)
    const alive = ref(true)

    const form = reactive({
      customerName: '',
      customerPhone: '',
      orderType: cartStore.orderContext.orderType || 'dine_in',
      diningArea: '',
      tableId: cartStore.orderContext.tableId || null,
      paymentMethod: 'wechat',
      specialRequests: ''
    })

    const subtotal = computed(() => cartStore.totalAmount)
    const packingFee = computed(() => (['takeaway', 'pack'].includes(form.orderType) ? 1 : 0))
    const total = computed(() => subtotal.value + packingFee.value)

    const areaOptions = computed(() => {
      const set = new Set(availableTables.value.map((table) => (table.area_name || '').trim()).filter(Boolean))
      return Array.from(set)
    })

    const filteredTables = computed(() => {
      if (!form.diningArea) return []
      return availableTables.value.filter((table) => (table.area_name || '大厅') === form.diningArea)
    })

    const selectedTableLabel = computed(() => {
      if (!form.tableId) return '请选择桌台'
      const selected = availableTables.value.find((item) => Number(item.id) === Number(form.tableId))
      return selected ? `${selected.name || selected.table_number} (${selected.area_name || '大厅'})` : `桌台#${form.tableId}`
    })

    const loadTables = async () => {
      try {
        await ensureWechatAuth()
        const data = await getAvailableTables()
        if (!alive.value) return
        availableTables.value = Array.isArray(data) ? data : []

        if (!form.diningArea && form.tableId) {
          const selected = availableTables.value.find((item) => Number(item.id) === Number(form.tableId))
          form.diningArea = selected?.area_name || ''
        }
      } catch (error) {
        if (alive.value) {
          Toast.fail(error?.response?.data?.detail || '加载桌台失败')
        }
      }
    }

    const selectArea = (area) => {
      form.diningArea = area
      form.tableId = null
      areaPickerVisible.value = false
    }

    const openTablePicker = () => {
      if (!form.diningArea) {
        Toast('请先选择就餐厅区')
        return
      }
      tablePickerVisible.value = true
    }

    const selectTable = (table) => {
      form.tableId = table.id
      tablePickerVisible.value = false
      cartStore.orderContext.tableId = table.id
      cartStore.orderContext.tableName = table.name || table.table_number || ''
    }

    const buildOrderPayload = () => {
      const orderItems = cartStore.items.map((item) => ({
        dish_id: Number(item.id),
        quantity: Number(item.quantity),
        unit_price: Number(item.price),
        total_price: Number(item.price) * Number(item.quantity),
        special_requests: null
      }))

      return {
        order_number: `WX${Date.now()}${Math.floor(Math.random() * 1000000)}`,
        customer_name: form.customerName || null,
        customer_phone: form.customerPhone || null,
        table_id: form.orderType === 'dine_in' ? form.tableId : null,
        order_type: form.orderType,
        payment_method: form.paymentMethod,
        payment_status: 'pending',
        order_status: 'pending',
        subtotal: subtotal.value,
        tax: 0,
        service_fee: 0,
        packing_fee: packingFee.value,
        discount: 0,
        total_amount: total.value,
        paid_amount: 0,
        remaining_amount: total.value,
        special_requests: form.specialRequests || null,
        is_takeout: form.orderType !== 'dine_in',
        takeout_number: null,
        waiter_id: null,
        is_suspended: false,
        order_items: orderItems
      }
    }

    const submitOrder = async () => {
      if (submitLock.value || submitting.value || cartStore.items.length === 0) return
      submitLock.value = true

      try {
        if (form.orderType === 'dine_in' && !form.diningArea) {
          Toast('请选择就餐厅区后再提交')
          return
        }

        if (form.orderType === 'dine_in' && !form.tableId) {
          Toast('请选择桌台后再提交')
          return
        }

        try {
          await showConfirmDialog({
            title: '确认提交',
            message: `共 ${cartStore.totalCount} 份菜品，合计 ¥${total.value.toFixed(2)}`
          })
        } catch {
          return
        }

        submitting.value = true
        try {
          await ensureWechatAuth()
          const payload = buildOrderPayload()
          const created = await createOrder(payload)
          if (!alive.value) return

          appendOrderId(created.id)
          cartStore.clearCart()
          Toast.success(`下单成功，订单号 #${created.id}`)
          router.replace('/order-history')
        } catch (error) {
          if (alive.value) {
            Toast.fail(error?.response?.data?.detail || '提交订单失败')
          }
        } finally {
          if (alive.value) {
            submitting.value = false
          }
        }
      } finally {
        submitLock.value = false
      }
    }

    watch(
      () => form.orderType,
      (type) => {
        if (type === 'dine_in' && availableTables.value.length === 0) {
          loadTables()
        }
        if (type !== 'dine_in') {
          form.diningArea = ''
          form.tableId = null
        }
      }
    )

    onMounted(() => {
      alive.value = true
      if (form.orderType === 'dine_in') {
        loadTables()
      }
    })

    onUnmounted(() => {
      alive.value = false
      submitting.value = false
      areaPickerVisible.value = false
      tablePickerVisible.value = false
    })

    return {
      cartStore,
      form,
      availableTables,
      areaOptions,
      filteredTables,
      areaPickerVisible,
      tablePickerVisible,
      selectedTableLabel,
      subtotal,
      packingFee,
      total,
      submitting,
      selectArea,
      openTablePicker,
      selectTable,
      submitOrder
    }
  }
}
</script>

<style scoped>
.order {
  padding: 12px;
  padding-bottom: 84px;
}

.panel {
  border-radius: 14px;
  overflow: hidden;
}

.mt10 {
  margin-top: 10px;
}

.footer {
  position: fixed;
  left: 10px;
  right: 10px;
  bottom: 56px;
  height: 58px;
  background: #fffaf5;
  border: 1px solid #f3dfcd;
  border-radius: 14px;
  box-shadow: 0 8px 20px rgba(121, 62, 29, 0.12);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 12px;
}

.price {
  color: #c6511a;
  font-weight: 700;
  font-size: 18px;
}

.table-list {
  max-height: 50vh;
  overflow: auto;
}
</style>
