<template>
  <div class="tables">
    <el-card class="table-panel">
      <template #header>
        <div class="card-header">
          <span class="panel-title">桌台管理</span>
          <div class="header-actions">
            <el-button class="header-btn ghost-btn" type="primary" plain @click="openReservationList">预定列表</el-button>
            <el-button class="header-btn warm-btn" type="warning" plain @click="openReserveDialog('hall')">大厅预定</el-button>
            <el-button class="header-btn main-btn" type="primary" @click="addTable">新增桌台</el-button>
          </div>
        </div>
      </template>

      <el-table v-loading="loading" :data="tables" stripe class="table-grid">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="table_number" label="桌台号" width="120" />
        <el-table-column prop="name" label="桌台名称" min-width="140" />
        <el-table-column prop="area_name" label="区域" width="120" />
        <el-table-column prop="capacity" label="容纳人数" width="110" />
        <el-table-column prop="status" label="状态" width="110">
          <template #default="scope">
            <el-tag class="status-tag" :type="getStatusType(scope.row.status)">{{ getStatusLabel(scope.row.status) }}</el-tag>
          </template>
        </el-table-column>

        <el-table-column label="当前预定" min-width="220">
          <template #default="scope">
            <div v-if="getBookedReservationForTable(scope.row.id)" class="reservation-cell">
              <div>{{ getBookedReservationForTable(scope.row.id).customer_name }} / {{ getBookedReservationForTable(scope.row.id).customer_phone }}</div>
              <div class="reservation-time">{{ formatTime(getBookedReservationForTable(scope.row.id).reservation_time) }}</div>
            </div>
            <span v-else class="empty-text">无</span>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="360" fixed="right">
          <template #default="scope">
            <div class="action-group">
              <el-button class="action-btn" size="small" @click="editTable(scope.row)">编辑</el-button>
              <el-button
                v-if="scope.row.status === 'reserved'"
                class="action-btn"
                size="small"
                type="danger"
                plain
                @click="cancelTableReservation(scope.row)"
              >
                取消预定
              </el-button>
              <el-button
                v-else
                class="action-btn"
                size="small"
                type="warning"
                plain
                :disabled="!canReserve(scope.row.status)"
                @click="openReserveDialog('table', scope.row)"
              >
                预定
              </el-button>
              <el-dropdown trigger="click">
                <el-button class="action-btn more-btn" size="small" plain>更多操作</el-button>
                <template #dropdown>
                  <el-dropdown-menu class="action-menu">
                    <el-dropdown-item :disabled="scope.row.status !== 'available'" @click="handleOccupy(scope.row)">占用</el-dropdown-item>
                    <el-dropdown-item :disabled="scope.row.status !== 'occupied'" @click="handleFree(scope.row)">释放</el-dropdown-item>
                    <el-dropdown-item :disabled="scope.row.status === 'cleaning'" @click="handleClean(scope.row)">清洁</el-dropdown-item>
                    <el-dropdown-item :disabled="scope.row.status !== 'cleaning'" @click="handleCleanDone(scope.row)">完成清洁</el-dropdown-item>
                    <el-dropdown-item divided @click="handleDelete(scope.row)">删除</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        :current-page="currentPage"
        :page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
        style="margin-top: 16px"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </el-card>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="560px">
      <el-form :model="currentTable" label-width="100px">
        <el-form-item label="桌台号" required>
          <el-input v-model="currentTable.table_number" :disabled="dialogType === 'edit'" />
        </el-form-item>
        <el-form-item label="桌台名称" required>
          <el-input v-model="currentTable.name" />
        </el-form-item>
        <el-form-item label="区域">
          <el-input v-model="currentTable.area_name" />
        </el-form-item>
        <el-form-item label="容纳人数">
          <el-input-number v-model="currentTable.capacity" :min="1" :max="30" style="width: 100%" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="currentTable.status" style="width: 100%">
            <el-option label="空闲" value="available" />
            <el-option label="占用" value="occupied" />
            <el-option label="预订" value="reserved" />
            <el-option label="清洁" value="cleaning" />
            <el-option label="不可用" value="unavailable" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="currentTable.description" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveTable">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="reservationDialogVisible"
      :title="reservationDialogTitle"
      width="620px"
      top="6vh"
      class="reservation-dialog"
      :close-on-click-modal="false"
    >
      <el-form :model="reservationForm" label-width="110px" class="reservation-form">
        <el-form-item label="预定类型">
          <el-radio-group v-model="reservationForm.reservation_type">
            <el-radio-button label="table">桌台预定</el-radio-button>
            <el-radio-button label="hall">大厅预定</el-radio-button>
          </el-radio-group>
        </el-form-item>

        <el-form-item v-if="reservationForm.reservation_type === 'table'" label="选择桌台" required>
          <el-select v-model="reservationForm.table_id" placeholder="请选择桌台" filterable style="width: 100%">
            <el-option
              v-for="item in reservableTableOptions"
              :key="item.id"
              :label="`${item.table_number} / ${item.name} / ${item.area_name}`"
              :value="item.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item v-else label="选择厅区" required>
          <el-select v-model="reservationForm.area_name" placeholder="请选择厅区" filterable allow-create default-first-option style="width: 100%">
            <el-option v-for="area in areaOptions" :key="area" :label="area" :value="area" />
          </el-select>
        </el-form-item>

        <el-form-item label="预定人" required>
          <el-input v-model="reservationForm.customer_name" placeholder="请输入预定人姓名" />
        </el-form-item>

        <el-form-item label="联系电话" required>
          <el-input v-model="reservationForm.customer_phone" placeholder="请输入联系电话" />
        </el-form-item>

        <el-form-item label="人数" required>
          <el-input-number v-model="reservationForm.party_size" :min="1" :max="50" style="width: 100%" />
        </el-form-item>

        <el-form-item label="预定时间" required>
          <el-date-picker
            v-model="reservationForm.reservation_time"
            type="datetime"
            format="YYYY-MM-DD HH:mm"
            value-format="YYYY-MM-DDTHH:mm:ss"
            :clearable="false"
            placeholder="请选择预定时间"
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item label="备注">
          <el-input v-model="reservationForm.notes" type="textarea" :rows="3" maxlength="120" show-word-limit placeholder="如：靠窗、宝宝椅、忌口等" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="reservationDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="reservationSaving" @click="saveReservation">保存预定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="reservationListVisible" title="预定列表" width="1260px" top="5vh" class="reservation-list-dialog">
      <div class="reservation-list-toolbar">
        <el-date-picker
          v-model="reservationTimeRange"
          type="datetimerange"
          @change="onReservationRangeChange"
          start-placeholder="开始时间"
          end-placeholder="结束时间"
          format="YYYY-MM-DD HH:mm"
          value-format="YYYY-MM-DDTHH:mm:ss"
          range-separator="至"
          :unlink-panels="true"
          style="width: 420px"
        />
        <div class="quick-range-group">
          <el-button class="quick-range-btn" :class="{ active: activeQuickRange === 'today' }" plain @click="applyQuickReservationRange('today')">今天</el-button>
          <el-button class="quick-range-btn" :class="{ active: activeQuickRange === '7d' }" plain @click="applyQuickReservationRange('7d')">近7天</el-button>
          <el-button class="quick-range-btn" :class="{ active: activeQuickRange === '30d' }" plain @click="applyQuickReservationRange('30d')">近30天</el-button>
        </div>
        <el-button class="toolbar-reset" plain @click="resetReservationFilters">重置筛选</el-button>
      </div>
      <el-table v-loading="reservationLoading" :data="filteredReservations" stripe class="reservation-list-table">
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column label="预定类型" width="100">
          <template #default="scope">{{ scope.row.table_id ? '桌台预定' : '大厅预定' }}</template>
        </el-table-column>
        <el-table-column label="桌台/厅区" min-width="140">
          <template #default="scope">{{ getReservationTargetLabel(scope.row) }}</template>
        </el-table-column>
        <el-table-column prop="customer_name" label="预定人" width="100" />
        <el-table-column prop="customer_phone" label="电话" width="130" />
        <el-table-column prop="party_size" label="人数" width="80" />
        <el-table-column label="预定时间" width="190">
          <template #default="scope">{{ formatTime(scope.row.reservation_time) }}</template>
        </el-table-column>
        <el-table-column label="状态" width="110">
          <template #default="scope">
            <el-tag :type="getReservationStatusType(scope.row.status)">{{ getReservationStatusLabel(scope.row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="190" fixed="right">
          <template #default="scope">
            <el-button class="list-action-btn" size="small" type="success" plain :disabled="scope.row.status !== 'booked'" @click="handleReservationArrive(scope.row)">到店</el-button>
            <el-button class="list-action-btn" size="small" type="danger" plain :disabled="scope.row.status !== 'booked'" @click="handleReservationCancel(scope.row)">取消</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
  </div>
</template>

<script>
import {
  arriveReservation,
  cancelReservation,
  cleanTable,
  completeTableCleaning,
  createReservation,
  createTable,
  deleteTable,
  freeTable,
  getAllTables,
  getReservations,
  occupyTable,
  updateTable
} from '@/services/tableService'

const createDefaultTable = () => ({
  id: null,
  table_number: '',
  name: '',
  area_name: '大厅',
  capacity: 4,
  status: 'available',
  is_active: true,
  description: ''
})

const pad = (n) => String(n).padStart(2, '0')
const formatDateTimeLocal = (date) => {
  const y = date.getFullYear()
  const m = pad(date.getMonth() + 1)
  const d = pad(date.getDate())
  const h = pad(date.getHours())
  const mm = pad(date.getMinutes())
  const ss = pad(date.getSeconds())
  return `${y}-${m}-${d}T${h}:${mm}:${ss}`
}

const createDefaultReservation = () => ({
  reservation_type: 'table',
  table_id: null,
  area_name: '',
  customer_name: '',
  customer_phone: '',
  party_size: 2,
  reservation_time: '',
  notes: ''
})

export default {
  name: 'Tables',
  data() {
    return {
      loading: false,
      tables: [],
      bookedReservations: [],
      currentPage: 1,
      pageSize: 10,
      total: 0,

      dialogVisible: false,
      dialogType: 'add',
      currentTable: createDefaultTable(),

      reservationDialogVisible: false,
      reservationDialogTitle: '新增预定',
      reservationSaving: false,
      reservationForm: createDefaultReservation(),

      reservationListVisible: false,
      reservationLoading: false,
      reservations: [],
      allAreaNames: [],
      reservationTimeRange: [],
      activeQuickRange: ''
    }
  },

  computed: {
    dialogTitle() {
      return this.dialogType === 'add' ? '新增桌台' : '编辑桌台'
    },
    areaOptions() {
      const set = new Set()
      ;[...this.allAreaNames, ...this.tables.map((t) => t.area_name)].forEach((area) => {
        const name = (area || '').trim()
        if (name) set.add(name)
      })
      return Array.from(set)
    },
    reservableTableOptions() {
      return this.tables.filter((t) => ['available', 'reserved'].includes(t.status))
    },

    tableLabelMap() {
      const map = {}
      this.tables.forEach((t) => {
        map[t.id] = t.name || t.table_number || `桌台#${t.id}`
      })
      return map
    },
    filteredReservations() {
      const range = this.reservationTimeRange || []
      if (!range[0] && !range[1]) return this.reservations

      const start = range[0] ? new Date(range[0]).getTime() : Number.NEGATIVE_INFINITY
      const end = range[1] ? new Date(range[1]).getTime() : Number.POSITIVE_INFINITY

      return this.reservations.filter((r) => {
        const ts = new Date(r.reservation_time).getTime()
        if (Number.isNaN(ts)) return false
        return ts >= start && ts <= end
      })
    }
  },
  async mounted() {
    await this.refreshTablePage()
  },
  methods: {
    notifyTableMonitorUpdate() {
      window.dispatchEvent(new CustomEvent('tables-updated', { detail: { at: Date.now() } }))
    },
    formatTime(value) {
      if (!value) return ''
      return String(value).replace('T', ' ').slice(0, 16)
    },
    getBookedReservationForTable(tableId) {
      return this.bookedReservations.find((r) => r.table_id === tableId)
    },
    getReservationTargetLabel(row) {
      if (row.table_id) {
        return this.tableLabelMap[row.table_id] || `桌台#${row.table_id}`
      }
      return row.area_name || '大厅'
    },
    canReserve(status) {
      return ['available', 'reserved'].includes(status)
    },
    getStatusLabel(status) {
      const map = {
        available: '空闲',
        occupied: '占用',
        reserved: '预订',
        cleaning: '清洁',
        unavailable: '不可用'
      }
      return map[status] || status
    },
    getStatusType(status) {
      const map = {
        available: 'success',
        occupied: 'danger',
        reserved: 'warning',
        cleaning: 'info',
        unavailable: 'info'
      }
      return map[status] || 'info'
    },
    getReservationStatusLabel(status) {
      const map = {
        booked: '已预定',
        arrived: '已到店',
        cancelled: '已取消',
        completed: '已完成'
      }
      return map[status] || status
    },
    getReservationStatusType(status) {
      const map = {
        booked: 'warning',
        arrived: 'success',
        cancelled: 'info',
        completed: 'success'
      }
      return map[status] || 'info'
    },
    getDefaultReservationTime() {
      const date = new Date(Date.now() + 30 * 60 * 1000)
      date.setSeconds(0)
      date.setMilliseconds(0)
      return formatDateTimeLocal(date)
    },
    async refreshTablePage() {
      await Promise.all([this.loadTables(), this.loadBookedReservations(), this.loadAreaNames()])
    },
    async loadTables() {
      this.loading = true
      try {
        const skip = (this.currentPage - 1) * this.pageSize
        const data = await getAllTables(skip, this.pageSize)
        const list = Array.isArray(data) ? data : []
        this.tables = list
        this.total = skip + this.tables.length + (this.tables.length === this.pageSize ? 1 : 0)
      } catch (error) {
        this.$message.error(error?.response?.data?.detail || '加载桌台失败')
      } finally {
        this.loading = false
      }
    },
    async loadAreaNames() {
      try {
        const data = await getAllTables(0, 500)
        const list = Array.isArray(data) ? data : []
        this.allAreaNames = Array.from(new Set(list.map((t) => (t.area_name || '').trim()).filter(Boolean)))
      } catch {
        this.allAreaNames = []
      }
    },
    async loadBookedReservations() {
      try {
        const data = await getReservations(0, 300, 'booked')
        this.bookedReservations = Array.isArray(data) ? data : []
      } catch {
        this.bookedReservations = []
      }
    },
    async loadReservations() {
      this.reservationLoading = true
      try {
        const data = await getReservations(0, 300)
        this.reservations = Array.isArray(data) ? data : []
      } catch (error) {
        this.$message.error(error?.response?.data?.detail || '加载预定失败')
      } finally {
        this.reservationLoading = false
      }
    },
    openReservationList() {
      this.applyQuickReservationRange('today')
      this.reservationListVisible = true
      this.loadReservations()
    },
    openReserveDialog(type, row = null) {
      this.reservationForm = createDefaultReservation()
      this.reservationForm.reservation_type = type
      this.reservationForm.reservation_time = this.getDefaultReservationTime()
      if (type === 'table' && row) {
        this.reservationDialogTitle = `桌台预定 - ${row.table_number}`
        this.reservationForm.table_id = row.id
        this.reservationForm.area_name = row.area_name || '大厅'
      } else {
        this.reservationDialogTitle = '大厅预定'
        this.reservationForm.table_id = null
        this.reservationForm.area_name = ''
      }
      this.reservationDialogVisible = true
    },
    async saveReservation() {
      const customerName = (this.reservationForm.customer_name || '').trim()
      const customerPhone = (this.reservationForm.customer_phone || '').trim()

      if (!customerName) return this.$message.warning('请输入预定人')
      if (!customerPhone) return this.$message.warning('请输入联系电话')
      if (this.reservationForm.reservation_type === 'table' && !this.reservationForm.table_id) return this.$message.warning('请选择桌台')
      if (this.reservationForm.reservation_type === 'hall' && !(this.reservationForm.area_name || '').trim()) return this.$message.warning('请选择厅区')
      if (!this.reservationForm.reservation_time) return this.$message.warning('请选择预定时间')

      const payload = {
        table_id: this.reservationForm.reservation_type === 'table' ? this.reservationForm.table_id : null,
        area_name: this.reservationForm.reservation_type === 'hall' ? this.reservationForm.area_name : null,
        customer_name: customerName,
        customer_phone: customerPhone,
        party_size: Number(this.reservationForm.party_size || 0),
        reservation_time: this.reservationForm.reservation_time,
        notes: this.reservationForm.notes || null
      }

      this.reservationSaving = true
      try {
        await createReservation(payload)
        this.$message.success('预定创建成功')
        this.reservationDialogVisible = false
        await Promise.all([this.refreshTablePage(), this.loadReservations()])
        this.notifyTableMonitorUpdate()
      } catch (error) {
        this.$message.error(error?.response?.data?.detail || '保存预定失败')
      } finally {
        this.reservationSaving = false
      }
    },
    async cancelTableReservation(row) {
      const booked = this.getBookedReservationForTable(row.id)
      if (!booked) {
        this.$message.warning('该桌台当前没有可取消的预定')
        return
      }

      try {
        await this.$confirm(`确认取消桌台 ${row.table_number} 的预定吗？`, '提示', {
          confirmButtonText: '确认取消',
          cancelButtonText: '返回',
          type: 'warning'
        })
        await cancelReservation(booked.id)
        this.$message.success('桌台预定已取消')
        await Promise.all([this.refreshTablePage(), this.loadReservations()])
        this.notifyTableMonitorUpdate()
      } catch (error) {
        if (error === 'cancel') return
        this.$message.error(error?.response?.data?.detail || '取消预定失败')
      }
    },
    async handleReservationCancel(row) {
      try {
        await cancelReservation(row.id)
        this.$message.success('预定已取消')
        await Promise.all([this.refreshTablePage(), this.loadReservations()])
        this.notifyTableMonitorUpdate()
      } catch (error) {
        this.$message.error(error?.response?.data?.detail || '取消预定失败')
      }
    },
    async handleReservationArrive(row) {
      try {
        await arriveReservation(row.id)
        this.$message.success('已登记到店')
        await Promise.all([this.refreshTablePage(), this.loadReservations()])
        this.notifyTableMonitorUpdate()
      } catch (error) {
        this.$message.error(error?.response?.data?.detail || '登记到店失败')
      }
    },
    addTable() {
      this.dialogType = 'add'
      this.currentTable = createDefaultTable()
      this.dialogVisible = true
    },
    editTable(row) {
      this.dialogType = 'edit'
      this.currentTable = {
        id: row.id,
        table_number: row.table_number,
        name: row.name,
        area_name: row.area_name || '大厅',
        capacity: row.capacity,
        status: row.status,
        is_active: row.is_active ?? true,
        description: row.description || ''
      }
      this.dialogVisible = true
    },
    async saveTable() {
      if (!this.currentTable.table_number || !this.currentTable.name) {
        this.$message.warning('请填写桌台号和桌台名称')
        return
      }

      try {
        if (this.dialogType === 'add') {
          await createTable({
            table_number: this.currentTable.table_number,
            name: this.currentTable.name,
            area_name: this.currentTable.area_name || '大厅',
            capacity: Number(this.currentTable.capacity),
            status: this.currentTable.status,
            is_active: true,
            description: this.currentTable.description || null
          })
          this.$message.success('新增成功')
        } else {
          await updateTable(this.currentTable.id, {
            name: this.currentTable.name,
            area_name: this.currentTable.area_name || '大厅',
            capacity: Number(this.currentTable.capacity),
            status: this.currentTable.status,
            is_active: Boolean(this.currentTable.is_active),
            description: this.currentTable.description || null
          })
          this.$message.success('修改成功')
        }

        this.dialogVisible = false
        await this.refreshTablePage()
        this.notifyTableMonitorUpdate()
      } catch (error) {
        this.$message.error(error?.response?.data?.detail || '保存桌台失败')
      }
    },
    async handleDelete(row) {
      try {
        await this.$confirm(`确认删除桌台「${row.table_number}」吗？`, '提示', {
          confirmButtonText: '确认',
          cancelButtonText: '取消',
          type: 'warning'
        })
        await deleteTable(row.id)
        this.$message.success('删除成功')
        await this.refreshTablePage()
        this.notifyTableMonitorUpdate()
      } catch (error) {
        if (error === 'cancel') return
        this.$message.error(error?.response?.data?.detail || '删除桌台失败')
      }
    },
    async handleOccupy(row) {
      try {
        await occupyTable(row.id)
        this.$message.success('桌台已占用')
        await this.refreshTablePage()
        this.notifyTableMonitorUpdate()
      } catch (error) {
        this.$message.error(error?.response?.data?.detail || '占用桌台失败')
      }
    },
    async handleFree(row) {
      try {
        await freeTable(row.id)
        this.$message.success('桌台已释放')
        await this.refreshTablePage()
        this.notifyTableMonitorUpdate()
      } catch (error) {
        this.$message.error(error?.response?.data?.detail || '释放桌台失败')
      }
    },
    async handleClean(row) {
      try {
        await cleanTable(row.id)
        this.$message.success('桌台已设为清洁中')
        await this.refreshTablePage()
        this.notifyTableMonitorUpdate()
      } catch (error) {
        this.$message.error(error?.response?.data?.detail || '清洁桌台失败')
      }
    },
    async handleCleanDone(row) {
      try {
        await completeTableCleaning(row.id)
        this.$message.success('桌台清洁已完成，已恢复空闲')
        await this.refreshTablePage()
        this.notifyTableMonitorUpdate()
      } catch (error) {
        this.$message.error(error?.response?.data?.detail || '完成清洁失败')
      }
    },
    async handleSizeChange(size) {
      this.pageSize = size
      this.currentPage = 1
      await this.refreshTablePage()
    },
    async handleCurrentChange(page) {
      this.currentPage = page
      await this.refreshTablePage()
    },
    resetReservationFilters() {
      this.reservationTimeRange = []
      this.activeQuickRange = ''
    },
    onReservationRangeChange() {
      this.activeQuickRange = ''
    },
    applyQuickReservationRange(kind) {
      const start = new Date()
      start.setHours(0, 0, 0, 0)
      const end = new Date(start)

      if (kind === 'today') {
        end.setHours(23, 59, 59, 0)
      } else if (kind === '7d') {
        end.setDate(end.getDate() + 6)
        end.setHours(23, 59, 59, 0)
      } else if (kind === '30d') {
        end.setDate(end.getDate() + 29)
        end.setHours(23, 59, 59, 0)
      } else {
        end.setHours(23, 59, 59, 0)
      }

      this.reservationTimeRange = [formatDateTimeLocal(start), formatDateTimeLocal(end)]
      this.activeQuickRange = kind
    }
  }
}
</script>

<style scoped>
.tables {
  --brand: #d2642f;
  --brand-soft: #fff2e8;
  --line: #efd8c7;
  --text-main: #3a2418;
  --text-muted: #8f6f5f;
  padding: 20px;
  background: radial-gradient(circle at 0 0, #fff3e7 0%, #fff7f0 40%, #fffaf6 100%);
  min-height: 100%;
}

.table-panel {
  border-radius: 14px;
  border: 1px solid #efd8c7;
  box-shadow: 0 12px 30px rgba(166, 91, 45, 0.12);
}

.panel-title {
  color: var(--text-main);
  font-size: 28px;
  font-weight: 700;
  letter-spacing: 1px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.header-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.header-btn {
  min-width: 102px;
  font-weight: 600;
}

.main-btn {
  box-shadow: 0 8px 20px rgba(210, 100, 47, 0.32);
}

.ghost-btn {
  background: var(--brand-soft);
}

.warm-btn {
  background: #ffe9d7;
}

.table-grid {
  border-radius: 10px;
  overflow: hidden;
  border: 1px solid var(--line);
}

.reservation-cell {
  line-height: 1.4;
}

.reservation-time {
  color: var(--text-muted);
  font-size: 12px;
}

.empty-text {
  color: var(--text-muted);
}

.status-tag {
  min-width: 56px;
  text-align: center;
  border-radius: 999px;
}

.action-group {
  display: flex;
  flex-wrap: nowrap;
  gap: 6px;
  align-items: center;
}

.action-btn {
  border-radius: 8px;
  font-weight: 600;
}

.more-btn {
  border-color: #e6c6b1;
}

.reservation-form {
  background: linear-gradient(180deg, #fff8f2 0%, #fff3e9 100%);
  border: 1px solid #f0d7c6;
  border-radius: 14px;
  padding: 18px 18px 8px;
}

:deep(.reservation-dialog .el-dialog),
:deep(.reservation-list-dialog .el-dialog) {
  max-width: calc(100vw - 32px);
  border-radius: 18px;
  overflow: hidden;
  border: 1px solid #f0d7c6;
  box-shadow: 0 24px 52px rgba(116, 58, 25, 0.22);
}

:deep(.reservation-dialog .el-dialog__header),
:deep(.reservation-list-dialog .el-dialog__header) {
  background: linear-gradient(90deg, #fff1e3 0%, #ffe4c8 100%);
  border-bottom: 1px solid #f0d7c6;
  padding: 18px 22px 14px;
}

:deep(.reservation-dialog .el-dialog__title),
:deep(.reservation-list-dialog .el-dialog__title) {
  color: #6b3f2a;
  font-size: 28px;
  font-weight: 700;
}

:deep(.reservation-dialog .el-dialog__body) {
  padding: 16px 22px 12px;
  background: #fffdfb;
}

:deep(.reservation-form .el-form-item) {
  margin-bottom: 14px;
}

:deep(.reservation-form .el-input__wrapper),
:deep(.reservation-form .el-textarea__inner),
:deep(.reservation-form .el-select__wrapper),
:deep(.reservation-form .el-input-number) {
  box-shadow: 0 0 0 1px #e5c8b2 inset;
  border-radius: 10px;
}

:deep(.reservation-list-dialog .el-dialog__body) {
  padding: 16px 22px 18px;
  background: #fffdfb;
}

.reservation-list-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 14px;
  padding: 12px;
  border-radius: 12px;
  border: 1px solid #f1d9c8;
  background: linear-gradient(90deg, #fff6ed 0%, #fffdf9 100%);
}

.quick-range-group {
  display: flex;
  align-items: center;
  gap: 6px;
}

.quick-range-btn {
  min-width: 94px;
  border-color: #deb79d;
  color: #8a5235;
  font-weight: 600;
}

.quick-range-btn.active {
  background: linear-gradient(90deg, #d86b2f 0%, #e7924f 100%);
  border-color: #d46d31;
  color: #fff;
  box-shadow: 0 8px 18px rgba(216, 107, 47, 0.28);
}

.toolbar-reset {
  border-color: #deb79d;
  color: #8a5235;
  font-weight: 600;
}

.list-action-btn {
  min-width: 72px;
  border-radius: 10px;
  font-weight: 600;
}

:deep(.reservation-list-table .el-table__header th.el-table__cell) {
  background: #fff3e6;
  color: #7a5442;
  font-weight: 700;
}

:deep(.reservation-list-table .el-table__row td.el-table__cell) {
  padding-top: 14px;
  padding-bottom: 14px;
}

:deep(.reservation-list-table .el-table__row:hover > td.el-table__cell) {
  background: #fff8f0 !important;
}

:deep(.table-grid .el-table__header th.el-table__cell) {
  background: #fff3e6;
  color: #7a5442;
  font-weight: 600;
}

:deep(.table-grid .el-table__row td.el-table__cell) {
  padding-top: 14px;
  padding-bottom: 14px;
}

:deep(.table-grid .el-table__row:hover > td.el-table__cell) {
  background: #fff9f2 !important;
}

:deep(.action-menu .el-dropdown-menu__item) {
  min-width: 108px;
}

@media (max-width: 960px) {
  .panel-title {
    font-size: 22px;
  }

  .card-header {
    align-items: flex-start;
    flex-direction: column;
  }

  .header-actions {
    width: 100%;
  }

  .reservation-list-toolbar {
    flex-wrap: wrap;
  }

  .quick-range-group {
    width: 100%;
  }

  .quick-range-btn,
  .toolbar-reset {
    flex: 1;
  }

  :deep(.reservation-list-dialog .el-date-editor.el-input__wrapper) {
    width: 100% !important;
  }
}
</style>












