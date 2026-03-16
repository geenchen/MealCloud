<template>
  <div class="table-dashboard">
    <el-card class="dashboard-card">
      <template #header>
        <div class="card-header">
          <span class="panel-title">桌台可视化监控</span>
          <div class="header-controls">
            <el-button class="toolbar-btn" @click="refreshTables" :loading="loading" size="small">
              <el-icon><Refresh /></el-icon>刷新
            </el-button>
            <el-button class="toolbar-btn" @click="toggleViewMode" size="small">
              <el-icon><Grid v-if="viewMode === 'grid'" /><List v-else /></el-icon>
              {{ viewMode === 'grid' ? '列表' : '网格' }}
            </el-button>
          </div>
        </div>
      </template>

      <div class="status-legend">
        <div class="legend-item"><div class="status-indicator available"></div><span>空闲</span></div>
        <div class="legend-item"><div class="status-indicator occupied"></div><span>占用</span></div>
        <div class="legend-item"><div class="status-indicator reserved"></div><span>预占</span></div>
        <div class="legend-item"><div class="status-indicator cleaning"></div><span>清洁</span></div>
      </div>

      <div class="summary-stats">
        <div class="stat-card"><div class="stat-value">{{ summaryStats.total }}</div><div class="stat-label">总桌台</div></div>
        <div class="stat-card"><div class="stat-value available">{{ summaryStats.available }}</div><div class="stat-label">空闲</div></div>
        <div class="stat-card"><div class="stat-value occupied">{{ summaryStats.occupied }}</div><div class="stat-label">占用</div></div>
        <div class="stat-card"><div class="stat-value reserved">{{ summaryStats.reserved }}</div><div class="stat-label">预占</div></div>
      </div>

      <el-card class="hall-reservation-card" shadow="never">
        <template #header>
          <div class="hall-header">
            <span>大厅预定看板</span>
            <el-tag type="warning">{{ hallReservations.length }} 条</el-tag>
          </div>
        </template>
        <el-empty v-if="hallReservations.length === 0" description="暂无大厅预定" :image-size="68" />
        <el-table v-else :data="hallReservations" size="small" stripe class="monitor-table">
          <el-table-column label="厅区" min-width="140">
            <template #default="scope">{{ getHallAreaLabel(scope.row) }}</template>
          </el-table-column>
          <el-table-column prop="customer_name" label="预定人" width="120" />
          <el-table-column prop="customer_phone" label="电话" width="140" />
          <el-table-column prop="party_size" label="人数" width="80" />
          <el-table-column prop="notes" label="备注" min-width="140" show-overflow-tooltip />
          <el-table-column prop="reservation_time" label="预定时间" min-width="170">
            <template #default="scope">{{ formatTime(scope.row.reservation_time) }}</template>
          </el-table-column>
        </el-table>
      </el-card>

      <div v-if="viewMode === 'grid'" class="table-grid">
        <div
          v-for="table in tables"
          :key="table.id"
          class="table-item"
          :class="`table-${table.display_status || table.status}`"
          @click="viewTableDetails(table)"
        >
          <div class="table-content">
            <div class="table-header">
              <div class="table-number">{{ table.table_number }}</div>
              <div class="table-capacity">{{ table.capacity }}人</div>
            </div>
            <div class="table-name">{{ table.name }}</div>
            <div class="table-status">
              <div class="status-indicator" :class="table.display_status || table.status"></div>
              <span>{{ getStatusText(table.display_status || table.status) }}</span>
            </div>
            <div v-if="table.reservation_name" class="table-customer">预定人: {{ table.reservation_name }}</div>
            <div v-if="table.reservation_time" class="table-order">预定时间: {{ table.reservation_time }}</div>
          </div>
        </div>
      </div>

      <el-table v-else :data="tables" style="width: 100%" stripe class="monitor-table">
        <el-table-column prop="table_number" label="桌台号" width="100" />
        <el-table-column prop="name" label="桌台名称" width="150" />
        <el-table-column prop="area_name" label="区域" width="120" />
        <el-table-column prop="capacity" label="容纳人数" width="100" />
        <el-table-column prop="display_status" label="状态" width="110">
          <template #default="scope">
            <div class="status-cell">
              <div class="status-indicator" :class="scope.row.display_status || scope.row.status"></div>
              <span>{{ getStatusText(scope.row.display_status || scope.row.status) }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="reservation_name" label="预定人" width="120" />
        <el-table-column prop="reservation_time" label="预定时间" min-width="170" />
        <el-table-column label="预定操作" width="120" fixed="right">
          <template #default="scope">
            <el-button
              size="small"
              type="danger"
              plain
              :disabled="!(scope.row.reservation_id && (scope.row.display_status || scope.row.status) === 'reserved')"
              @click="handleCancelReservation(scope.row)"
            >
              取消预定
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="showTableDetails" title="桌台详情" width="640px">
      <div v-if="selectedTable">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="桌台号">{{ selectedTable.table_number }}</el-descriptions-item>
          <el-descriptions-item label="桌台名称">{{ selectedTable.name }}</el-descriptions-item>
          <el-descriptions-item label="区域">{{ selectedTable.area_name }}</el-descriptions-item>
          <el-descriptions-item label="容纳人数">{{ selectedTable.capacity }}人</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(selectedTable.display_status || selectedTable.status)">{{ getStatusText(selectedTable.display_status || selectedTable.status) }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="预定人" v-if="selectedTable.reservation_name">{{ selectedTable.reservation_name }}</el-descriptions-item>
          <el-descriptions-item label="预定电话" v-if="selectedTable.reservation_phone">{{ selectedTable.reservation_phone }}</el-descriptions-item>
          <el-descriptions-item label="预定时间" v-if="selectedTable.reservation_time">{{ selectedTable.reservation_time }}</el-descriptions-item>
        </el-descriptions>

        <div class="dialog-actions" v-if="selectedTable.reservation_id && (selectedTable.display_status || selectedTable.status) === 'reserved'">
          <el-button type="danger" plain @click="handleCancelReservation(selectedTable)">取消当前预定</el-button>
        </div>
      </div>
      <template #footer>
        <el-button @click="showTableDetails = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Grid, List, Refresh } from '@element-plus/icons-vue'
import { cancelReservation, getAllTables, getReservations } from '@/services/tableService'

export default {
  name: 'TableDashboard',
  components: { Refresh, Grid, List },
  setup() {
    const loading = ref(false)
    const viewMode = ref('grid')
    const tables = ref([])
    const hallReservations = ref([])
    const showTableDetails = ref(false)
    const selectedTable = ref(null)
    let refreshTimer = null

    const summaryStats = computed(() => ({
      total: tables.value.length,
      available: tables.value.filter((t) => (t.display_status || t.status) === 'available').length,
      occupied: tables.value.filter((t) => (t.display_status || t.status) === 'occupied').length,
      reserved: tables.value.filter((t) => (t.display_status || t.status) === 'reserved').length,
      cleaning: tables.value.filter((t) => (t.display_status || t.status) === 'cleaning').length
    }))

    const getStatusText = (status) => ({
      available: '空闲',
      occupied: '占用',
      reserved: '预占',
      cleaning: '清洁',
      unavailable: '不可用'
    }[status] || status)

    const getStatusType = (status) => ({
      available: 'success',
      occupied: 'danger',
      reserved: 'warning',
      cleaning: 'info',
      unavailable: 'info'
    }[status] || 'info')

    const formatTime = (value) => {
      if (!value) return ''
      return String(value).replace('T', ' ').slice(0, 16)
    }

    const getHallAreaLabel = (row) => {
      const area = (row?.area_name || '').trim()
      return area || '\u672a\u586b\u5199\u5385\u533a'
    }

    const enrichTableReservation = (tableList, reservations) => {
      const reservationMap = new Map()
      reservations.forEach((r) => {
        if (r.status === 'booked' && r.table_id) {
          reservationMap.set(r.table_id, r)
        }
      })

      return tableList.map((t) => {
        const r = reservationMap.get(t.id)
        const displayStatus = r ? 'reserved' : t.status
        return {
          ...t,
          display_status: displayStatus,
          reservation_id: r?.id || null,
          reservation_name: r?.customer_name || '',
          reservation_phone: r?.customer_phone || '',
          reservation_time: formatTime(r?.reservation_time)
        }
      })
    }

    const refreshTables = async () => {
      loading.value = true
      try {
        const [tableList, reservationList] = await Promise.all([
          getAllTables(),
          getReservations(0, 500, 'booked')
        ])
        const safeTables = Array.isArray(tableList) ? tableList : []
        const safeReservations = Array.isArray(reservationList) ? reservationList : []

        tables.value = enrichTableReservation(safeTables, safeReservations)
        hallReservations.value = safeReservations.filter((r) => !r.table_id)
      } catch (error) {
        ElMessage.error(error?.response?.data?.detail || '加载桌台监控失败')
      } finally {
        loading.value = false
      }
    }

    const toggleViewMode = () => {
      viewMode.value = viewMode.value === 'grid' ? 'list' : 'grid'
    }

    const viewTableDetails = (table) => {
      selectedTable.value = table
      showTableDetails.value = true
    }

    const handleCancelReservation = async (table) => {
      if (!table?.reservation_id) {
        ElMessage.warning('当前桌台没有可取消的预定')
        return
      }

      try {
        await ElMessageBox.confirm(`确认取消桌台 ${table.table_number} 的预定吗？`, '提示', {
          confirmButtonText: '确认取消',
          cancelButtonText: '返回',
          type: 'warning'
        })
        await cancelReservation(table.reservation_id)
        ElMessage.success('预定已取消')
        await refreshTables()
      } catch (error) {
        if (error === 'cancel') return
        ElMessage.error(error?.response?.data?.detail || '取消预定失败')
      }
    }

    const onTablesUpdated = () => {
      refreshTables()
    }

    onMounted(() => {
      refreshTables()
      window.addEventListener('tables-updated', onTablesUpdated)
      refreshTimer = window.setInterval(refreshTables, 30000)
    })

    onUnmounted(() => {
      window.removeEventListener('tables-updated', onTablesUpdated)
      if (refreshTimer) window.clearInterval(refreshTimer)
    })

    return {
      loading,
      viewMode,
      tables,
      hallReservations,
      showTableDetails,
      selectedTable,
      summaryStats,
      refreshTables,
      toggleViewMode,
      viewTableDetails,
      getStatusText,
      getStatusType,
      formatTime,
      getHallAreaLabel,
      handleCancelReservation
    }
  }
}
</script>

<style scoped>
.table-dashboard {
  --warm-bg-1: #fff6ee;
  --warm-bg-2: #fff9f4;
  --warm-line: #f0d9c9;
  --warm-text: #3a2418;
  --warm-muted: #8f6f5f;
  --warm-accent: #d66b31;
  padding: 20px;
  background: radial-gradient(circle at 0 0, #fff3e7 0%, #fff7f0 42%, #fffaf6 100%);
  min-height: 100%;
}

.dashboard-card {
  border-radius: 14px;
  border: 1px solid #f0d9c9;
  box-shadow: 0 12px 30px rgba(166, 91, 45, 0.12);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.panel-title {
  color: var(--warm-text);
  font-size: 28px;
  font-weight: 800;
  letter-spacing: 1px;
}

.header-controls {
  display: flex;
  gap: 10px;
}

.toolbar-btn {
  border-radius: 10px;
  border-color: #e9c8b2;
  font-weight: 600;
}

.status-legend {
  display: flex;
  gap: 20px;
  margin: 16px 0;
  padding: 12px;
  background: var(--warm-bg-1);
  border: 1px solid var(--warm-line);
  border-radius: 10px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #6e4f42;
}

.summary-stats {
  display: flex;
  gap: 12px;
  margin: 16px 0;
}

.stat-card {
  flex: 1;
  background: linear-gradient(180deg, #fffdfa 0%, #fff7ef 100%);
  border: 1px solid var(--warm-line);
  border-radius: 12px;
  padding: 16px;
  text-align: center;
}

.stat-value {
  font-size: 24px;
  font-weight: 800;
  color: var(--warm-text);
}

.stat-label {
  color: var(--warm-muted);
  font-size: 13px;
  margin-top: 4px;
}

.stat-value.available { color: #4f9b3a; }
.stat-value.occupied { color: #cf4c2d; }
.stat-value.reserved { color: #da8d1d; }

.hall-reservation-card {
  margin-bottom: 14px;
  border-radius: 12px;
  border: 1px solid var(--warm-line);
  background: #fffaf5;
}

.hall-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: var(--warm-text);
  font-weight: 700;
}

.table-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 12px;
}

.table-item {
  border: 1px solid #ead6c7;
  border-radius: 12px;
  background: #fffdfb;
  cursor: pointer;
  transition: all .2s;
}

.table-item:hover {
  box-shadow: 0 10px 20px rgba(169, 97, 52, 0.16);
  transform: translateY(-2px);
}

.table-item.table-available { border-left: 4px solid #6cae3a; }
.table-item.table-occupied { border-left: 4px solid #d3572d; }
.table-item.table-reserved { border-left: 4px solid #e0a124; }
.table-item.table-cleaning { border-left: 4px solid #8f96a3; }

.table-content { padding: 12px; }
.table-header { display: flex; justify-content: space-between; margin-bottom: 6px; }
.table-number { font-weight: 800; color: var(--warm-text); }
.table-capacity { color: var(--warm-muted); }
.table-name { margin-bottom: 8px; color: #51382b; font-weight: 600; }
.table-status { display: flex; align-items: center; gap: 8px; margin-bottom: 6px; }
.table-customer, .table-order { font-size: 12px; color: #6d584c; margin-top: 4px; }

.dialog-actions { margin-top: 14px; text-align: right; }

.status-cell { display: flex; align-items: center; gap: 8px; }
.status-indicator { width: 10px; height: 10px; border-radius: 50%; }
.status-indicator.available { background: #67c23a; }
.status-indicator.occupied { background: #f56c6c; }
.status-indicator.reserved { background: #e6a23c; }
.status-indicator.cleaning { background: #909399; }
.status-indicator.unavailable { background: #c0c4cc; }

:deep(.monitor-table .el-table__header th.el-table__cell) {
  background: #fff3e6;
  color: #7a5442;
  font-weight: 700;
}

:deep(.monitor-table .el-table__row:hover > td.el-table__cell) {
  background: #fff9f2 !important;
}

@media (max-width: 960px) {
  .panel-title {
    font-size: 22px;
  }

  .card-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .summary-stats {
    flex-wrap: wrap;
  }

  .stat-card {
    min-width: 140px;
  }
}
</style>
