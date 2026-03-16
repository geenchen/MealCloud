<template>
  <div class="orders-page">
    <el-card>
      <template #header>
        <div class="toolbar">
          <div class="toolbar-left">
            <el-input
              v-model="searchQuery"
              placeholder="搜索订单号/客户/电话"
              clearable
              style="width: 260px"
              @input="currentPage = 1"
            />
            <el-select
              v-model="statusFilter"
              placeholder="订单状态"
              clearable
              style="width: 150px"
              @change="currentPage = 1"
            >
              <el-option label="待确认" value="pending" />
              <el-option label="已确认" value="confirmed" />
              <el-option label="制作中" value="preparing" />
              <el-option label="待出餐" value="ready" />
              <el-option label="已上菜" value="served" />
              <el-option label="已完成" value="completed" />
              <el-option label="已取消" value="cancelled" />
            </el-select>
          </div>

          <div class="toolbar-right">
            <el-button type="warning" plain :loading="loading" @click="loadData">刷新</el-button>
          </div>
        </div>
      </template>

      <el-table v-loading="loading" :data="pagedOrders" stripe>
        <el-table-column prop="order_number" label="订单号" min-width="170" />
        <el-table-column label="客户" width="140">
          <template #default="scope">{{ scope.row.customer_name || '-' }}</template>
        </el-table-column>
        <el-table-column label="电话" width="140">
          <template #default="scope">{{ scope.row.customer_phone || '-' }}</template>
        </el-table-column>
        <el-table-column label="桌台" width="140">
          <template #default="scope">{{ tableName(scope.row.table_id) }}</template>
        </el-table-column>
        <el-table-column label="订单类型" width="100">
          <template #default="scope">
            <el-tag size="small" :type="orderTypeTag(scope.row.order_type)">
              {{ orderTypeLabel(scope.row.order_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="支付" width="100">
          <template #default="scope">{{ paymentMethodLabel(scope.row.payment_method) }}</template>
        </el-table-column>
        <el-table-column label="状态" width="110">
          <template #default="scope">
            <el-tag size="small" :type="orderStatusTag(scope.row.order_status)">
              {{ orderStatusLabel(scope.row.order_status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="金额" width="120">
          <template #default="scope">{{ formatMoney(scope.row.total_amount) }}</template>
        </el-table-column>
        <el-table-column label="创建时间" width="170">
          <template #default="scope">{{ formatDateTime(scope.row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="scope">
            <el-button size="small" @click="openDetail(scope.row)">详情</el-button>
            <el-button
              v-if="scope.row.order_status === 'pending'"
              size="small"
              type="primary"
              :loading="actionLoadingId === scope.row.id"
              @click="confirm(scope.row)"
            >
              确认
            </el-button>
            <el-button
              v-if="canComplete(scope.row.order_status)"
              size="small"
              type="success"
              :loading="actionLoadingId === scope.row.id"
              @click="complete(scope.row)"
            >
              完成
            </el-button>
            <el-button
              v-if="canCancel(scope.row.order_status)"
              size="small"
              type="danger"
              plain
              :loading="actionLoadingId === scope.row.id"
              @click="cancel(scope.row)"
            >
              取消
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        :current-page="currentPage"
        :page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="filteredOrders.length"
        layout="total, sizes, prev, pager, next, jumper"
        style="margin-top: 16px"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </el-card>

    <el-dialog v-model="detailVisible" width="840px" :title="`订单详情 - ${selectedOrder?.order_number || ''}`">
      <div v-if="selectedOrder">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="订单号">{{ selectedOrder.order_number }}</el-descriptions-item>
          <el-descriptions-item label="订单状态">
            <el-tag size="small" :type="orderStatusTag(selectedOrder.order_status)">
              {{ orderStatusLabel(selectedOrder.order_status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="客户">{{ selectedOrder.customer_name || '-' }}</el-descriptions-item>
          <el-descriptions-item label="电话">{{ selectedOrder.customer_phone || '-' }}</el-descriptions-item>
          <el-descriptions-item label="桌台">{{ tableName(selectedOrder.table_id) }}</el-descriptions-item>
          <el-descriptions-item label="订单类型">{{ orderTypeLabel(selectedOrder.order_type) }}</el-descriptions-item>
          <el-descriptions-item label="支付方式">{{ paymentMethodLabel(selectedOrder.payment_method) }}</el-descriptions-item>
          <el-descriptions-item label="支付状态">{{ paymentStatusLabel(selectedOrder.payment_status) }}</el-descriptions-item>
          <el-descriptions-item label="小计">{{ formatMoney(selectedOrder.subtotal) }}</el-descriptions-item>
          <el-descriptions-item label="总计">{{ formatMoney(selectedOrder.total_amount) }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatDateTime(selectedOrder.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="备注">{{ selectedOrder.special_requests || '-' }}</el-descriptions-item>
        </el-descriptions>

        <h4 class="section-title">菜品明细</h4>
        <el-table :data="selectedOrderItems" size="small" stripe>
          <el-table-column label="菜品" min-width="180">
            <template #default="scope">{{ dishName(scope.row.dish_id) }}</template>
          </el-table-column>
          <el-table-column label="单价" width="120">
            <template #default="scope">{{ formatMoney(scope.row.unit_price) }}</template>
          </el-table-column>
          <el-table-column prop="quantity" label="数量" width="80" />
          <el-table-column label="小计" width="120">
            <template #default="scope">{{ formatMoney(scope.row.total_price) }}</template>
          </el-table-column>
          <el-table-column label="状态" width="160">
            <template #default="scope">
              <el-tag size="small" :type="scope.row.is_prepared ? 'success' : 'info'">
                {{ scope.row.is_prepared ? '已制作' : '待制作' }}
              </el-tag>
              <el-tag size="small" style="margin-left: 6px" :type="scope.row.is_served ? 'success' : 'info'">
                {{ scope.row.is_served ? '已上菜' : '未上菜' }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <template #footer>
        <el-button @click="detailVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ElMessage, ElMessageBox } from 'element-plus'
import { completeOrder, confirmOrder, getAllOrders, getOrder, cancelOrder } from '@/services/orderService'
import { getDishes } from '@/services/dishService'
import { getAllTables } from '@/services/tableService'

export default {
  name: 'Orders',
  data() {
    return {
      loading: false,
      actionLoadingId: null,
      orders: [],
      tableMap: {},
      dishMap: {},
      searchQuery: '',
      statusFilter: '',
      currentPage: 1,
      pageSize: 10,
      detailVisible: false,
      selectedOrder: null,
      selectedOrderItems: []
    }
  },
  computed: {
    filteredOrders() {
      const query = this.searchQuery.trim().toLowerCase()
      return this.orders.filter((order) => {
        const byStatus = this.statusFilter ? order.order_status === this.statusFilter : true
        const byQuery = !query
          ? true
          : [order.order_number, order.customer_name, order.customer_phone]
              .filter(Boolean)
              .some((v) => String(v).toLowerCase().includes(query))
        return byStatus && byQuery
      })
    },
    pagedOrders() {
      const start = (this.currentPage - 1) * this.pageSize
      return this.filteredOrders.slice(start, start + this.pageSize)
    }
  },
  async mounted() {
    await this.loadData()
  },
  methods: {
    formatMoney(v) {
      return `￥${Number(v || 0).toFixed(2)}`
    },
    formatDateTime(v) {
      if (!v) return '-'
      const d = new Date(v)
      if (Number.isNaN(d.getTime())) return '-'
      return d.toLocaleString('zh-CN', { hour12: false })
    },
    orderTypeLabel(v) {
      return (
        {
          dine_in: '堂食',
          takeaway: '外带',
          pack: '打包',
          preorder: '预定'
        }[v] || v || '-'
      )
    },
    orderTypeTag(v) {
      return (
        {
          dine_in: 'primary',
          takeaway: 'success',
          pack: 'warning',
          preorder: 'info'
        }[v] || 'info'
      )
    },
    paymentMethodLabel(v) {
      return (
        {
          cash: '现金',
          wechat: '微信',
          alipay: '支付宝',
          mixed: '混合',
          credit: '赊账'
        }[v] || v || '-'
      )
    },
    paymentStatusLabel(v) {
      return (
        {
          pending: '待支付',
          partial: '部分支付',
          paid: '已支付',
          credit: '赊账'
        }[v] || v || '-'
      )
    },
    orderStatusLabel(v) {
      return (
        {
          pending: '待确认',
          confirmed: '已确认',
          preparing: '制作中',
          ready: '待出餐',
          served: '已上菜',
          completed: '已完成',
          cancelled: '已取消'
        }[v] || v || '-'
      )
    },
    orderStatusTag(v) {
      return (
        {
          pending: 'warning',
          confirmed: 'primary',
          preparing: 'warning',
          ready: 'success',
          served: 'success',
          completed: 'success',
          cancelled: 'info'
        }[v] || 'info'
      )
    },
    tableName(tableId) {
      if (!tableId) return '-'
      const table = this.tableMap[tableId]
      if (!table) return `桌台#${tableId}`
      return table.name || table.table_number || `桌台#${tableId}`
    },
    dishName(dishId) {
      if (!dishId) return '-'
      const dish = this.dishMap[dishId]
      return dish?.name || `菜品#${dishId}`
    },
    canComplete(status) {
      return ['confirmed', 'preparing', 'ready', 'served'].includes(status)
    },
    canCancel(status) {
      return !['completed', 'cancelled'].includes(status)
    },
    async loadData() {
      this.loading = true
      try {
        const [orders, tables, dishes] = await Promise.all([
          getAllOrders(0, 500),
          getAllTables(0, 500),
          getDishes(0, 500)
        ])

        this.orders = Array.isArray(orders) ? orders : []
        this.tableMap = Object.fromEntries((Array.isArray(tables) ? tables : []).map((t) => [t.id, t]))
        this.dishMap = Object.fromEntries((Array.isArray(dishes) ? dishes : []).map((d) => [d.id, d]))
      } catch (error) {
        console.error('加载订单失败:', error)
        ElMessage.error(error?.response?.data?.detail || '加载订单失败')
      } finally {
        this.loading = false
      }
    },
    async openDetail(row) {
      try {
        const detail = await getOrder(row.id)
        this.selectedOrder = detail
        this.selectedOrderItems = Array.isArray(detail?.order_items) ? detail.order_items : []
        this.detailVisible = true
      } catch (error) {
        console.error('加载订单详情失败:', error)
        ElMessage.error(error?.response?.data?.detail || '加载订单详情失败')
      }
    },
    async confirm(row) {
      this.actionLoadingId = row.id
      try {
        await confirmOrder(row.id)
        ElMessage.success('订单已确认')
        await this.loadData()
      } catch (error) {
        console.error('确认订单失败:', error)
        ElMessage.error(error?.response?.data?.detail || '确认订单失败')
      } finally {
        this.actionLoadingId = null
      }
    },
    async complete(row) {
      this.actionLoadingId = row.id
      try {
        await completeOrder(row.id)
        ElMessage.success('订单已完成')
        await this.loadData()
      } catch (error) {
        console.error('完成订单失败:', error)
        ElMessage.error(error?.response?.data?.detail || '完成订单失败')
      } finally {
        this.actionLoadingId = null
      }
    },
    async cancel(row) {
      const confirmed = await ElMessageBox.confirm(`确认取消订单 ${row.order_number} 吗？`, '提示', {
        type: 'warning',
        confirmButtonText: '确认取消',
        cancelButtonText: '返回'
      }).then(() => true).catch(() => false)

      if (!confirmed) return

      this.actionLoadingId = row.id
      try {
        await cancelOrder(row.id)
        ElMessage.success('订单已取消')
        await this.loadData()
      } catch (error) {
        console.error('取消订单失败:', error)
        ElMessage.error(error?.response?.data?.detail || '取消订单失败')
      } finally {
        this.actionLoadingId = null
      }
    },
    handleSizeChange(size) {
      this.pageSize = size
      this.currentPage = 1
    },
    handleCurrentChange(page) {
      this.currentPage = page
    }
  }
}
</script>

<style scoped>
.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.section-title {
  margin: 16px 0 10px;
  color: #6b3d26;
}

@media (max-width: 768px) {
  .toolbar {
    flex-direction: column;
    align-items: stretch;
  }

  .toolbar-left {
    flex-wrap: wrap;
  }
}
</style>


