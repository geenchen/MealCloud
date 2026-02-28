<template>
  <div class="table-dashboard">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>桌台可视化监控</span>
          <div class="header-controls">
            <el-button @click="refreshTables" :loading="loading" size="small">
              <el-icon><Refresh /></el-icon>刷新
            </el-button>
            <el-button @click="toggleViewMode" size="small">
              <el-icon><Grid v-if="viewMode === 'grid'" /><List v-else /></el-icon>
              {{ viewMode === 'grid' ? '列表' : '网格' }}
            </el-button>
          </div>
        </div>
      </template>

      <!-- Status Legend -->
      <div class="status-legend">
        <div class="legend-item">
          <div class="status-indicator available"></div>
          <span>空闲</span>
        </div>
        <div class="legend-item">
          <div class="status-indicator occupied"></div>
          <span>占用</span>
        </div>
        <div class="legend-item">
          <div class="status-indicator reserved"></div>
          <span>预订</span>
        </div>
        <div class="legend-item">
          <div class="status-indicator cleaning"></div>
          <span>清洁</span>
        </div>
      </div>

      <!-- Summary Stats -->
      <div class="summary-stats">
        <div class="stat-card">
          <div class="stat-value">{{ summaryStats.total }}</div>
          <div class="stat-label">总桌台</div>
        </div>
        <div class="stat-card">
          <div class="stat-value available">{{ summaryStats.available }}</div>
          <div class="stat-label">空闲</div>
        </div>
        <div class="stat-card">
          <div class="stat-value occupied">{{ summaryStats.occupied }}</div>
          <div class="stat-label">占用</div>
        </div>
        <div class="stat-card">
          <div class="stat-value reserved">{{ summaryStats.reserved }}</div>
          <div class="stat-label">预订</div>
        </div>
      </div>

      <!-- Table Visualization -->
      <div 
        v-if="viewMode === 'grid'" 
        class="table-grid"
        :class="`layout-${layoutType}`"
      >
        <div 
          v-for="table in tables" 
          :key="table.id"
          class="table-item"
          :class="getTableStatusClass(table)"
          @click="handleTableClick(table)"
        >
          <div class="table-content">
            <div class="table-header">
              <div class="table-number">{{ table.table_number }}</div>
              <div class="table-capacity">{{ table.capacity }}人</div>
            </div>
            <div class="table-name">{{ table.name }}</div>
            <div class="table-status">
              <div class="status-indicator" :class="table.status"></div>
              <span>{{ getStatusText(table.status) }}</span>
            </div>
            <div v-if="table.current_order" class="table-order">
             订单: {{ table.current_order }}
            </div>
            <div v-if="table.customer_name" class="table-customer">
             客: {{ table.customer_name }}
            </div>
          </div>
        </div>
      </div>

      <!-- Table List View -->
      <el-table 
        v-else 
        :data="tables" 
        style="width: 100%" 
        stripe
        @row-click="handleTableClick"
      >
        <el-table-column prop="table_number" label="桌台号" width="100" />
        <el-table-column prop="name" label="桌台名称" width="150" />
        <el-table-column prop="area" label="区域" width="120" />
        <el-table-column prop="capacity" label="容纳人数" width="100" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <div class="status-cell">
              <div class="status-indicator" :class="scope.row.status"></div>
              <span>{{ getStatusText(scope.row.status) }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="current_order" label="当前订单" width="120" />
        <el-table-column prop="customer_name" label="客户姓名" />
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button 
              size="small" 
              @click.stop="occupyTable(scope.row)"
              :disabled="scope.row.status !== 'available'"
            >
             占
            </el-button>
            <el-button 
              size="small" 
              @click.stop="freeTable(scope.row)"
              :disabled="scope.row.status !== 'occupied'"
            >
              释放
            </el-button>
            <el-button size="small" @click.stop="viewTableDetails(scope.row)">
              详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- Table Details Dialog -->
    <el-dialog v-model="showTableDetails" title="桌台详情" width="600px">
      <div v-if="selectedTable">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="桌台号">{{ selectedTable.table_number }}</el-descriptions-item>
          <el-descriptions-item label="桌台名称">{{ selectedTable.name }}</el-descriptions-item>
          <el-descriptions-item label="区域">{{ selectedTable.area }}</el-descriptions-item>
          <el-descriptions-item label="容纳人数">{{ selectedTable.capacity }}人</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(selectedTable.status)">
              {{ getStatusText(selectedTable.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="当前订单" v-if="selectedTable.current_order">
            {{ selectedTable.current_order }}
          </el-descriptions-item>
          <el-descriptions-item label="客户姓名" v-if="selectedTable.customer_name">
            {{ selectedTable.customer_name }}
          </el-descriptions-item>
        </el-descriptions>
        
        <div v-if="selectedTable.order_history" style="margin-top: 20px;">
          <h4>近期订单记录</h4>
          <el-table :data="selectedTable.order_history" style="width: 100%" size="small">
            <el-table-column prop="order_number" label="订单号" width="120" />
            <el-table-column prop="customer_name" label="客户" width="100" />
            <el-table-column prop="amount" label="金额" width="80" />
            <el-table-column prop="status" label="状态" width="80">
              <template #default="scope">
                <el-tag :type="getOrderStatusType(scope.row.status)" size="small">
                  {{ scope.row.status }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="时间" />
          </el-table>
        </div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showTableDetails = false">关闭</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh, Grid, List } from '@element-plus/icons-vue'
import { getAllTables, occupyTable, freeTable } from '@/services/tableService'

export default {
  name: 'TableDashboard',
  components: {
    Refresh,
    Grid,
    List
  },
  setup() {
    const loading = ref(false)
    const viewMode = ref('grid') // 'grid' or 'list'
    const layoutType = ref('restaurant') // 'restaurant', 'grid', 'custom'
    const tables = ref([])
    const showTableDetails = ref(false)
    const selectedTable = ref(null)

    // Mock data for demonstration
    const mockTables = [
      { id: 1, table_number: 'T001', name: '大厅1号桌', area: '大厅', capacity: 4, status: 'available', current_order: null, customer_name: null },
      { id: 2, table_number: 'T002', name: '大厅2号桌', area: '大厅', capacity: 6, status: 'occupied', current_order: 'ORD-001', customer_name: '张先生' },
      { id: 3, table_number: 'T003', name: '包间A', area: '包间', capacity: 8, status: 'reserved', current_order: null, customer_name: '李女士' },
      { id: 4, table_number: 'T004', name: '大厅3号桌', area: '大厅', capacity: 4, status: 'cleaning', current_order: null, customer_name: null },
      { id: 5, table_number: 'T005', name: '包间B', area: '包间', capacity: 10, status: 'available', current_order: null, customer_name: null },
      { id: 6, table_number: 'T006', name: '大厅4号桌', area: '大厅', capacity: 6, status: 'occupied', current_order: 'ORD-002', customer_name: '王先生' },
      { id: 7, table_number: 'T007', name: '户外1号桌', area: '户外', capacity: 4, status: 'available', current_order: null, customer_name: null },
      { id: 8, table_number: 'T008', name: '户外2号桌', area: '户外', capacity: 6, status: 'occupied', current_order: 'ORD-003', customer_name: '赵女士' }
    ]

    // Computed properties
    const summaryStats = computed(() => {
      return {
        total: tables.value.length,
        available: tables.value.filter(t => t.status === 'available').length,
        occupied: tables.value.filter(t => t.status === 'occupied').length,
        reserved: tables.value.filter(t => t.status === 'reserved').length,
        cleaning: tables.value.filter(t => t.status === 'cleaning').length
      }
    })

    // Methods
    const refreshTables = async () => {
      loading.value = true
      try {
        const response = await getAllTables()
        tables.value = response
        ElMessage.success('桌台信息已刷新')
      } catch (error) {
        console.error('刷新桌台失败:', error)
        ElMessage.error('刷新失败: ' + (error.response?.data?.detail || error.message))
        // Fallback to mock data
        tables.value = [...mockTables]
      } finally {
        loading.value = false
      }
    }

    const toggleViewMode = () => {
      viewMode.value = viewMode.value === 'grid' ? 'list' : 'grid'
    }

    const getTableStatusClass = (table) => {
      return `table-${table.status}`
    }

    const getStatusText = (status) => {
      const statusMap = {
        available: '空闲',
        occupied: '占用',
        reserved: '预订',
        cleaning: '清洁'
      }
      return statusMap[status] || '未知'
    }

    const getStatusType = (status) => {
      const typeMap = {
        available: 'success',
        occupied: 'danger',
        reserved: 'warning',
        cleaning: 'info'
      }
      return typeMap[status] || 'info'
    }

    const getOrderStatusType = (status) => {
      const typeMap = {
        '已完成': 'success',
        '制作中': 'warning',
        '待确认': 'info',
        '已取消': 'danger'
      }
      return typeMap[status] || 'info'
    }

    const handleTableClick = (table) => {
      selectedTable.value = table
      showTableDetails.value = true
    }

    const viewTableDetails = (table) => {
      handleTableClick(table)
    }

    const occupyTableHandler = async (table) => {
      if (table.status !== 'available') {
        ElMessage.warning('只能占用空闲桌台')
        return
      }

      try {
        await ElMessageBox.confirm(
          `确定要占用桌台 ${table.table_number}吗`,
          '确认占用',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )
        
        // In real implementation: await occupyTable(table.id)
        table.status = 'occupied'
        table.current_order = `ORD-${Date.now().toString().slice(-3)}`
        table.customer_name = '临时客户'
        ElMessage.success(`桌台 ${table.table_number}已占用`)
      } catch (error) {
        if (error !== 'cancel') {
          console.error('占用桌台失败:', error)
          ElMessage.error('占用失败，请重试')
        }
      }
    }

    const freeTableHandler = async (table) => {
      if (table.status !== 'occupied') {
        ElMessage.warning('只能释放占用的桌台')
        return
      }

      try {
        await ElMessageBox.confirm(
          `确定要释放桌台 ${table.table_number}吗`,
          '确认释放',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )
        
        // In real implementation: await freeTable(table.id)
        table.status = 'available'
        table.current_order = null
        table.customer_name = null
        ElMessage.success(`桌台 ${table.table_number}已释放`)
      } catch (error) {
        if (error !== 'cancel') {
          console.error('释放桌台失败:', error)
          ElMessage.error('释放失败，请重试')
        }
      }
    }

    // Initialize
    onMounted(() => {
      refreshTables()
    })

    return {
      loading,
      viewMode,
      layoutType,
      tables,
      showTableDetails,
      selectedTable,
      summaryStats,
      refreshTables,
      toggleViewMode,
      getTableStatusClass,
      getStatusText,
      getStatusType,
      getOrderStatusType,
      handleTableClick,
      viewTableDetails,
      occupyTable: occupyTableHandler,
      freeTable: freeTableHandler
    }
  }
}
</script>

<style scoped>
.table-dashboard {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-controls {
  display: flex;
  gap: 10px;
}

.status-legend {
  display: flex;
  gap: 20px;
  margin: 20px 0;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #666;
}

.status-indicator {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.status-indicator.available {
  background-color: #67c23a;
}

.status-indicator.occupied {
  background-color: #f56c6c;
}

.status-indicator.reserved {
  background-color: #e6a23c;
}

.status-indicator.cleaning {
  background-color: #909399;
}

.summary-stats {
  display: flex;
  gap: 15px;
  margin: 20px 0;
}

.stat-card {
  flex: 1;
  background: linear-gradient(145deg, #ffffff, #f8f9fa);
  border-radius: 12px;
  padding: 20px;
  text-align: center;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.8);
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 5px;
}

.stat-value.available {
  color: #67c23a;
}

.stat-value.occupied {
  color: #f56c6c;
}

.stat-value.reserved {
  color: #e6a23c;
}

.stat-label {
  font-size: 14px;
  color: #666;
}

.table-grid {
  display: grid;
  gap: 15px;
  margin-top: 20px;
}

.table-grid.layout-restaurant {
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
}

.table-grid.layout-grid {
  grid-template-columns: repeat(4, 1fr);
}

.table-item {
  background: linear-gradient(145deg, #ffffff, #f8f9fa);
  border-radius: 12px;
  padding: 15px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid transparent;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  position: relative;
  overflow: hidden;
}

.table-item:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.table-item.table-available {
  border-color: #67c23a;
}

.table-item.table-occupied {
  border-color: #f56c6c;
}

.table-item.table-reserved {
  border-color: #e6a23c;
}

.table-item.table-cleaning {
  border-color: #909399;
}

.table-content {
  text-align: center;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.table-number {
  font-size: 18px;
  font-weight: 700;
  color: #2b2d42;
}

.table-capacity {
  font-size: 14px;
  color: #666;
  background: #f0f0f0;
  padding: 2px 8px;
  border-radius: 12px;
}

.table-name {
  font-size: 14px;
  color: #666;
  margin-bottom: 10px;
}

.table-status {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  margin-bottom: 8px;
  font-size: 13px;
  font-weight: 500;
}

.table-order, .table-customer {
  font-size: 12px;
  color: #888;
  margin: 3px 0;
}

.status-cell {
  display: flex;
  align-items: center;
  gap: 6px;
}

/* Responsive design */
@media (max-width: 768px) {
  .table-dashboard {
    padding: 10px;
  }
  
  .summary-stats {
    flex-direction: column;
  }
  
  .table-grid.layout-restaurant,
  .table-grid.layout-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .status-legend {
    flex-wrap: wrap;
    gap: 10px;
  }
}
</style>