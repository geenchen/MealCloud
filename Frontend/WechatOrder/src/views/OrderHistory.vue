<template>
  <div class="order-history">
    <van-loading v-if="loading" class="loading" size="24px">加载中...</van-loading>
    <van-empty v-else-if="orders.length === 0" description="暂无历史订单" />

    <van-cell-group v-else class="panel">
      <van-cell
        v-for="order in orders"
        :key="order.id"
        :title="`订单 #${order.id}`"
        :label="formatTime(order.created_at)"
      >
        <template #value>
          <div class="value-block">
            <van-tag :type="statusType(order.order_status)">{{ statusLabel(order.order_status) }}</van-tag>
            <div class="amount">¥{{ Number(order.total_amount || 0).toFixed(2) }}</div>
          </div>
        </template>
      </van-cell>
    </van-cell-group>
  </div>
</template>

<script>
import { onMounted, onUnmounted, ref } from 'vue'
import { Toast } from 'vant'
import { getOrder } from '@/services/orderService'
import { ensureWechatAuth } from '@/services/authService'

const ORDER_IDS_KEY = 'wechat_order_ids'

export default {
  name: 'OrderHistory',
  setup() {
    const loading = ref(false)
    const orders = ref([])
    const alive = ref(true)

    const loadOrders = async () => {
      loading.value = true
      try {
        await ensureWechatAuth()
        const raw = localStorage.getItem(ORDER_IDS_KEY)
        const ids = raw ? JSON.parse(raw) : []
        if (!Array.isArray(ids) || ids.length === 0) {
          if (alive.value) orders.value = []
          return
        }

        const result = await Promise.all(
          ids.map(async (id) => {
            try {
              return await getOrder(id)
            } catch {
              return null
            }
          })
        )

        if (alive.value) {
          orders.value = result.filter(Boolean)
        }
      } catch (error) {
        if (alive.value) {
          Toast.fail(error?.response?.data?.detail || '加载订单失败')
        }
      } finally {
        if (alive.value) {
          loading.value = false
        }
      }
    }

    const statusLabel = (status) => {
      const map = {
        pending: '待处理',
        confirmed: '已确认',
        preparing: '制作中',
        ready: '待上菜',
        served: '已上菜',
        completed: '已完成',
        cancelled: '已取消'
      }
      return map[status] || status
    }

    const statusType = (status) => {
      if (status === 'completed') return 'success'
      if (status === 'cancelled') return 'danger'
      if (status === 'pending') return 'warning'
      return 'primary'
    }

    const formatTime = (value) => (value ? String(value).replace('T', ' ').slice(0, 16) : '-')

    onMounted(() => {
      alive.value = true
      loadOrders()
    })

    onUnmounted(() => {
      alive.value = false
      loading.value = false
    })

    return {
      loading,
      orders,
      statusLabel,
      statusType,
      formatTime
    }
  }
}
</script>

<style scoped>
.order-history {
  padding: 12px;
}

.panel {
  border-radius: 14px;
  overflow: hidden;
}

.loading {
  display: block;
  margin-top: 20px;
  text-align: center;
}

.value-block {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 6px;
}

.amount {
  color: #c6511a;
  font-weight: 700;
}
</style>
