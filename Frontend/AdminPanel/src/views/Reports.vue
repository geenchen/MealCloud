<template>
  <div class="reports">
    <el-card class="dashboard-card">
      <template #header>
        <div class="card-header">
          <span>数据统计</span>
        </div>
      </template>
      
      <el-row :gutter="20" class="stats-row">
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-number">1,248</div>
            <div class="stat-label">总订单数</div>
            <div class="stat-trend">
              <el-icon :class="trendClass('orders')"><ArrowUp v-if="trendPositive('orders')" /><ArrowDown v-else /></el-icon>
              <span :class="trendTextClass('orders')">{{ trendValue('orders') }}%</span>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-number">¥24,850</div>
            <div class="stat-label">总营业额</div>
            <div class="stat-trend">
              <el-icon :class="trendClass('revenue')"><ArrowUp v-if="trendPositive('revenue')" /><ArrowDown v-else /></el-icon>
              <span :class="trendTextClass('revenue')">{{ trendValue('revenue') }}%</span>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-number">42</div>
            <div class="stat-label">今日订单</div>
            <div class="stat-trend">
              <el-icon :class="trendClass('todayOrders')"><ArrowUp v-if="trendPositive('todayOrders')" /><ArrowDown v-else /></el-icon>
              <span :class="trendTextClass('todayOrders')">{{ trendValue('todayOrders') }}%</span>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-number">¥3,240</div>
            <div class="stat-label">今日营收</div>
            <div class="stat-trend">
              <el-icon :class="trendClass('todayRevenue')"><ArrowUp v-if="trendPositive('todayRevenue')" /><ArrowDown v-else /></el-icon>
              <span :class="trendTextClass('todayRevenue')">{{ trendValue('todayRevenue') }}%</span>
            </div>
          </el-card>
        </el-col>
      </el-row>
      
      <el-row :gutter="20" style="margin-top: 20px;">
        <el-col :span="16">
          <el-card>
            <template #header>
              <span>订单趋势图</span>
            </template>
            <div id="chart-orders" style="height: 400px;"></div>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card>
            <template #header>
              <span>热门菜品排行</span>
            </template>
            <el-table :data="popularDishes" style="width: 100%">
              <el-table-column prop="rank" label="#" width="50" />
              <el-table-column prop="name" label="菜品名称" />
              <el-table-column prop="sales" label="销量" width="80" />
            </el-table>
          </el-card>
          
          <el-card style="margin-top: 20px;">
            <template #header>
              <span>营收占比</span>
            </template>
            <div id="chart-revenue" style="height: 200px;"></div>
          </el-card>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script>
import { ArrowUp, ArrowDown } from '@element-plus/icons-vue'

export default {
  name: 'Reports',
  components: {
    ArrowUp,
    ArrowDown
  },
  data() {
    return {
      stats: {
        orders: { value: 1248, trend: 12.3 },
        revenue: { value: 24850, trend: 8.7 },
        todayOrders: { value: 42, trend: -2.1 },
        todayRevenue: { value: 3240, trend: 5.4 }
      },
      popularDishes: [
        { rank: 1, name: '宫保鸡丁', sales: 124 },
        { rank: 2, name: '麻婆豆腐', sales: 118 },
        { rank: 3, name: '红烧肉', sales: 98 },
        { rank: 4, name: '鱼香肉丝', sales: 87 },
        { rank: 5, name: '酸辣汤', sales: 76 },
        { rank: 6, name: '白米饭', sales: 245 },
        { rank: 7, name: '可乐', sales: 189 }
      ]
    }
  },
  methods: {
    trendPositive(key) {
      return this.stats[key].trend >= 0
    },
    trendClass(key) {
      return this.trendPositive(key) ? 'trend-up' : 'trend-down'
    },
    trendTextClass(key) {
      return this.trendPositive(key) ? 'text-success' : 'text-danger'
    },
    trendValue(key) {
      return Math.abs(this.stats[key].trend)
    }
  },
  mounted() {
    // 这里在真实项目中会集成图表库如ECharts或Chart.js
    // 为了演示目的，我们只显示占位符文本
    this.$nextTick(() => {
      document.getElementById('chart-orders').innerHTML = '<div style="display: flex; align-items: center; justify-content: center; height: 100%; color: #909399;">订单趋势图 (集成图表库后显示)</div>'
      document.getElementById('chart-revenue').innerHTML = '<div style="display: flex; align-items: center; justify-content: center; height: 100%; color: #909399;">营收占比图 (集成图表库后显示)</div>'
    })
  }
}
</script>

<style scoped>
.dashboard-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  text-align: center;
  padding: 20px;
}

.stat-number {
  font-size: 24px;
  font-weight: bold;
  color: #409EFF;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 10px;
}

.stat-trend {
  display: flex;
  align-items: center;
  justify-content: center;
}

.trend-up {
  color: #67C23A;
}

.trend-down {
  color: #F56C6C;
}

.text-success {
  color: #67C23A;
}

.text-danger {
  color: #F56C6C;
}
</style>