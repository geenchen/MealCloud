<template>
  <div class="home-dashboard">
    <section class="hero">
      <div class="hero-left">
        <h2>营业看板</h2>
        <p>{{ todayLabel }} | {{ nowTime }}</p>
      </div>
      <div class="hero-right">
        <el-radio-group v-model="selectedRange" size="small" @change="onRangeChange">
          <el-radio-button label="today">今天</el-radio-button>
          <el-radio-button label="7d">近7天</el-radio-button>
          <el-radio-button label="month">本月</el-radio-button>
        </el-radio-group>
        <el-button :loading="loading" type="warning" plain @click="loadDashboard">刷新数据</el-button>
      </div>
    </section>

    <el-row :gutter="16" class="kpi-row">
      <el-col :xs="24" :sm="12" :lg="6">
        <el-card shadow="hover" class="kpi-card">
          <div class="kpi-title">{{ rangeLabel }}订单</div>
          <div class="kpi-value">{{ stats.orderCount }}</div>
          <div class="kpi-sub">{{ rangeHint }}订单总量</div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :lg="6">
        <el-card shadow="hover" class="kpi-card">
          <div class="kpi-title">{{ rangeLabel }}营业额</div>
          <div class="kpi-value">{{ formatMoney(stats.revenue) }}</div>
          <div class="kpi-sub">按已完成订单统计</div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :lg="6">
        <el-card shadow="hover" class="kpi-card">
          <div class="kpi-title">桌台占用率</div>
          <div class="kpi-value">{{ occupiedRate }}%</div>
          <div class="kpi-sub">{{ tableStats.occupied }} / {{ tableStats.total }} 张桌台</div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :lg="6">
        <el-card shadow="hover" class="kpi-card">
          <div class="kpi-title">{{ rangeLabel }}预定数</div>
          <div class="kpi-value">{{ bookedReservations.length }}</div>
          <div class="kpi-sub">按预定时间统计</div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" class="panel-row">
      <el-col :xs="24" :lg="10">
        <el-card class="panel-card" shadow="never">
          <template #header>
            <div class="panel-header">
              <span>桌台状态</span>
              <el-tag type="warning" effect="light">总计 {{ tableStats.total }}</el-tag>
            </div>
          </template>

          <div class="status-grid">
            <div class="status-item">
              <span>空闲</span>
              <b>{{ tableStats.available }}</b>
            </div>
            <div class="status-item">
              <span>占用</span>
              <b>{{ tableStats.occupied }}</b>
            </div>
            <div class="status-item">
              <span>预定</span>
              <b>{{ tableStats.reserved }}</b>
            </div>
            <div class="status-item">
              <span>清洁</span>
              <b>{{ tableStats.cleaning }}</b>
            </div>
          </div>

          <el-progress :percentage="occupiedRate" :stroke-width="14" status="warning" class="occupied-progress" />

          <div class="table-preview">
            <div
              v-for="table in tablePreview"
              :key="table.id"
              class="table-chip"
              :class="`status-${table.status}`"
            >
              <span class="chip-name">{{ table.name || table.table_number }}</span>
              <span class="chip-status">{{ tableStatusLabel(table.status) }}</span>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="8">
        <el-card class="panel-card" shadow="never">
          <template #header>
            <div class="panel-header">
              <span>{{ rangeLabel }}预定列表</span>
              <el-button link type="warning" @click="$router.push('/tables')">查看全部</el-button>
            </div>
          </template>

          <div v-if="bookedReservations.length === 0" class="empty-text">{{ rangeLabel }}暂无预定</div>

          <div v-else class="reservation-list">
            <div v-for="item in bookedReservations" :key="item.id" class="reservation-item">
              <div class="reservation-main">
                <strong>{{ item.customer_name }}</strong>
                <span>{{ item.party_size }} 人</span>
              </div>
              <div class="reservation-sub">
                <span>{{ formatDateTime(item.reservation_time) }}</span>
                <span>{{ item.area_name || '大厅' }}</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="6">
        <el-card class="panel-card" shadow="never">
          <template #header>
            <span>快捷入口</span>
          </template>

          <div class="quick-actions">
            <el-button type="warning" plain @click="$router.push('/order-entry')">快速下单</el-button>
            <el-button type="warning" plain @click="$router.push('/tables')">桌台管理</el-button>
            <el-button type="warning" plain @click="$router.push('/table-dashboard')">桌台监控</el-button>
            <el-button type="warning" plain @click="$router.push('/orders')">订单管理</el-button>
          </div>

          <div class="todo-box">
            <h4>{{ rangeLabel }}提醒</h4>
            <p>待清洁桌台：{{ tableStats.cleaning }}</p>
            <p>待处理订单：{{ pendingOrdersCount }}</p>
            <p>沽清/特价：前往运营工具维护</p>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" class="panel-row">
      <el-col :xs="24" :lg="14">
        <el-card class="panel-card" shadow="never">
          <template #header>
            <div class="panel-header">
              <span>{{ rangeLabel }}订单</span>
              <el-button link type="warning" @click="$router.push('/orders')">订单页</el-button>
            </div>
          </template>

          <el-table :data="recentOrders" size="small" stripe>
            <el-table-column prop="order_number" label="订单号" min-width="140" />
            <el-table-column prop="customer_name" label="客户" width="120" />
            <el-table-column label="金额" width="120">
              <template #default="scope">{{ formatMoney(scope.row.total_amount) }}</template>
            </el-table-column>
            <el-table-column label="状态" width="110">
              <template #default="scope">
                <el-tag size="small" :type="orderStatusTag(scope.row.order_status)">
                  {{ orderStatusLabel(scope.row.order_status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="时间" width="170">
              <template #default="scope">{{ formatDateTime(scope.row.created_at) }}</template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="10">
        <el-card class="panel-card" shadow="never">
          <template #header>
            <span>热销菜品（{{ rangeLabel }}）</span>
          </template>

          <el-table :data="popularDishes" size="small" stripe>
            <el-table-column prop="dish_name" label="菜品" min-width="140" />
            <el-table-column prop="order_count" label="下单次数" width="100" />
            <el-table-column prop="total_quantity" label="销量" width="90" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import apiClient from '@/services/apiClient'
import { getAllTables, getReservations, getTableStats } from '@/services/tableService'

export default {
  name: 'Home',
  data() {
    return {
      loading: false,
      timer: null,
      nowTime: '',
      selectedRange: 'today',
      stats: {
        orderCount: 0,
        revenue: 0
      },
      tableStats: {
        total: 0,
        available: 0,
        occupied: 0,
        reserved: 0,
        cleaning: 0,
        unavailable: 0
      },
      tables: [],
      reservations: [],
      recentOrders: [],
      popularDishes: [],
      pendingOrdersCount: 0
    }
  },
  computed: {
    todayLabel() {
      return new Date().toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        weekday: 'long'
      })
    },
    rangeLabel() {
      const map = {
        today: '今天',
        '7d': '近7天',
        month: '本月'
      }
      return map[this.selectedRange] || '今天'
    },
    rangeHint() {
      const map = {
        today: '今日',
        '7d': '近7天',
        month: '本月'
      }
      return map[this.selectedRange] || '今日'
    },
    occupiedRate() {
      if (!this.tableStats.total) return 0
      return Math.round((this.tableStats.occupied / this.tableStats.total) * 100)
    },
    tablePreview() {
      return this.tables.slice(0, 10)
    },
    bookedReservations() {
      const { startAt, endAt } = this.getRangeBounds(this.selectedRange)
      return this.reservations
        .filter((item) => {
          const t = new Date(item.reservation_time).getTime()
          return item.status === 'booked' && t >= startAt && t <= endAt
        })
        .sort((a, b) => new Date(a.reservation_time) - new Date(b.reservation_time))
        .slice(0, 8)
    }
  },
  async mounted() {
    this.updateClock()
    this.timer = setInterval(this.updateClock, 1000)
    await this.loadDashboard()
  },
  beforeUnmount() {
    if (this.timer) {
      clearInterval(this.timer)
      this.timer = null
    }
  },
  methods: {
    updateClock() {
      this.nowTime = new Date().toLocaleTimeString('zh-CN', { hour12: false })
    },
    onRangeChange() {
      this.loadDashboard()
    },
    getRangeDays(range) {
      if (range === '7d') return 7
      if (range === 'month') {
        const now = new Date()
        return now.getDate()
      }
      return 1
    },
    getRangeBounds(range) {
      const now = new Date()
      const end = new Date(now)
      end.setHours(23, 59, 59, 999)

      if (range === '7d') {
        const start = new Date(now)
        start.setDate(now.getDate() - 6)
        start.setHours(0, 0, 0, 0)
        return { startAt: start.getTime(), endAt: end.getTime() }
      }

      if (range === 'month') {
        const start = new Date(now.getFullYear(), now.getMonth(), 1)
        start.setHours(0, 0, 0, 0)
        return { startAt: start.getTime(), endAt: end.getTime() }
      }

      const start = new Date(now)
      start.setHours(0, 0, 0, 0)
      return { startAt: start.getTime(), endAt: end.getTime() }
    },
    formatMoney(value) {
      const amount = Number(value || 0)
      return `￥${amount.toFixed(2)}`
    },
    formatDateTime(value) {
      if (!value) return '-'
      const date = new Date(value)
      if (Number.isNaN(date.getTime())) return '-'
      return date.toLocaleString('zh-CN', {
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        hour12: false
      })
    },
    tableStatusLabel(status) {
      const map = {
        available: '空闲',
        occupied: '占用',
        reserved: '预定',
        cleaning: '清洁中',
        unavailable: '停用'
      }
      return map[status] || status
    },
    orderStatusLabel(status) {
      const map = {
        pending: '待确认',
        confirmed: '已确认',
        preparing: '制作中',
        ready: '待出餐',
        served: '已上菜',
        completed: '已完成',
        cancelled: '已取消'
      }
      return map[status] || status
    },
    orderStatusTag(status) {
      const map = {
        pending: 'warning',
        confirmed: 'primary',
        preparing: 'warning',
        ready: 'success',
        served: 'success',
        completed: 'success',
        cancelled: 'info'
      }
      return map[status] || 'info'
    },
    async loadDashboard() {
      this.loading = true
      try {
        const days = this.getRangeDays(this.selectedRange)
        const { startAt, endAt } = this.getRangeBounds(this.selectedRange)

        const [statsRes, tableStats, tables, reservations, orders] = await Promise.all([
          apiClient.get('/orders/stats', { params: { days } }),
          getTableStats(),
          getAllTables(0, 200),
          getReservations(0, 500),
          apiClient.get('/orders', { params: { skip: 0, limit: 500 } })
        ])

        const statData = statsRes?.data || {}
        const orderList = Array.isArray(orders?.data) ? orders.data : []
        const filteredOrders = orderList.filter((item) => {
          const t = new Date(item.created_at).getTime()
          return t >= startAt && t <= endAt
        })

        this.stats.orderCount = Number(statData.total_orders || 0)
        this.stats.revenue = Number(statData.total_revenue || 0)
        this.popularDishes = Array.isArray(statData.popular_dishes) ? statData.popular_dishes.slice(0, 8) : []
        this.tableStats = { ...this.tableStats, ...(tableStats || {}) }
        this.tables = Array.isArray(tables) ? tables : []
        this.reservations = Array.isArray(reservations) ? reservations : []

        this.recentOrders = [...filteredOrders]
          .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
          .slice(0, 8)

        this.pendingOrdersCount = filteredOrders.filter((item) =>
          ['pending', 'confirmed', 'preparing', 'ready', 'served'].includes(item.order_status)
        ).length
      } catch (error) {
        console.error('加载首页看板失败:', error)
        this.$message.error('看板数据加载失败，请检查服务状态')
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.home-dashboard {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.hero {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-radius: 16px;
  padding: 18px 20px;
  background: linear-gradient(110deg, #5a2f1b 0%, #7a4022 45%, #ad5b2f 100%);
  color: #ffe9d8;
}

.hero h2 {
  margin: 0;
  font-size: 26px;
}

.hero p {
  margin: 6px 0 0;
  color: #ffd6bc;
}

.hero-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.kpi-row,
.panel-row {
  margin: 0 !important;
}

.kpi-card {
  border-radius: 14px;
  border: 1px solid #f2dccd;
  background: #fffaf6;
}

.kpi-title {
  color: #8a6148;
  font-size: 13px;
}

.kpi-value {
  margin-top: 4px;
  color: #5e2f19;
  font-size: 30px;
  font-weight: 800;
  line-height: 1.15;
}

.kpi-sub {
  margin-top: 6px;
  color: #b0866b;
  font-size: 12px;
}

.panel-card {
  border-radius: 14px;
  border: 1px solid #efd9ca;
  background: #fffdfb;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.status-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.status-item {
  border: 1px solid #f0dfd3;
  background: #fff7f1;
  border-radius: 10px;
  padding: 10px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  color: #7d4a2f;
}

.status-item b {
  color: #4f2614;
  font-size: 18px;
}

.occupied-progress {
  margin-top: 14px;
}

.table-preview {
  margin-top: 12px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.table-chip {
  border-radius: 999px;
  padding: 4px 10px;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  border: 1px solid #ead2c0;
  background: #fff7f1;
}

.table-chip .chip-name {
  font-weight: 700;
}

.status-available {
  border-color: #9bcf6a;
  background: #eff9e6;
}

.status-occupied {
  border-color: #f1a85f;
  background: #fff3e6;
}

.status-reserved {
  border-color: #6eaef6;
  background: #edf5ff;
}

.status-cleaning {
  border-color: #d2b48c;
  background: #f7efe6;
}

.status-unavailable {
  border-color: #d3c7be;
  background: #f4f2f0;
}

.reservation-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.reservation-item {
  border: 1px solid #f0dfd3;
  background: #fff8f3;
  border-radius: 10px;
  padding: 10px;
}

.reservation-main {
  display: flex;
  align-items: center;
  justify-content: space-between;
  color: #5a2f1b;
}

.reservation-sub {
  margin-top: 4px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  color: #a1785f;
  font-size: 12px;
}

.quick-actions {
  display: grid;
  grid-template-columns: 1fr;
  gap: 10px;
}

.quick-actions .el-button {
  margin-left: 0;
  justify-content: flex-start;
}

.todo-box {
  margin-top: 16px;
  border-radius: 10px;
  background: #fff5ec;
  border: 1px dashed #e4b690;
  padding: 10px 12px;
}

.todo-box h4 {
  margin: 0 0 8px;
  color: #6d3a1f;
}

.todo-box p {
  margin: 4px 0;
  color: #865538;
  font-size: 13px;
}

.empty-text {
  color: #a1785f;
  text-align: center;
  padding: 14px 0;
}

@media (max-width: 768px) {
  .hero {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }

  .hero-right {
    width: 100%;
    justify-content: space-between;
    flex-wrap: wrap;
  }

  .kpi-value {
    font-size: 26px;
  }
}
</style>
