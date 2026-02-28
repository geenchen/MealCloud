<template>
  <div class="tables">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>桌台管理</span>
          <el-button type="primary" @click="addTable">新增桌台</el-button>
        </div>
      </template>

      <el-table v-loading="loading" :data="tables" stripe>
        <el-table-column prop="id" label="ID" width="90" />
        <el-table-column prop="table_number" label="桌台号" width="120" />
        <el-table-column prop="name" label="桌台名称" min-width="160" />
        <el-table-column prop="area_name" label="区域" width="120" />
        <el-table-column prop="capacity" label="容纳人数" width="110" />
        <el-table-column prop="status" label="状态" width="110">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)">{{ getStatusLabel(scope.row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="360">
          <template #default="scope">
            <el-button size="small" @click="editTable(scope.row)">编辑</el-button>
            <el-button
              size="small"
              type="success"
              plain
              :disabled="scope.row.status !== 'available'"
              @click="handleOccupy(scope.row)"
            >占用</el-button>
            <el-button
              size="small"
              type="warning"
              plain
              :disabled="scope.row.status !== 'occupied'"
              @click="handleFree(scope.row)"
            >释放</el-button>
            <el-button size="small" type="info" plain @click="handleClean(scope.row)">清洁</el-button>
            <el-button size="small" type="danger" @click="handleDelete(scope.row)">删除</el-button>
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
  </div>
</template>

<script>
import {
  cleanTable,
  createTable,
  deleteTable,
  freeTable,
  getAllTables,
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

export default {
  name: 'Tables',
  data() {
    return {
      loading: false,
      tables: [],
      currentPage: 1,
      pageSize: 10,
      total: 0,
      dialogVisible: false,
      dialogType: 'add',
      currentTable: createDefaultTable()
    }
  },
  computed: {
    dialogTitle() {
      return this.dialogType === 'add' ? '新增桌台' : '编辑桌台'
    }
  },
  async mounted() {
    await this.loadTables()
  },
  methods: {
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
    async loadTables() {
      this.loading = true
      try {
        const skip = (this.currentPage - 1) * this.pageSize
        const data = await getAllTables(skip, this.pageSize)
        const list = Array.isArray(data) ? data : []
        this.tables = list
        this.total = skip + this.tables.length + (this.tables.length === this.pageSize ? 1 : 0)
      } catch (error) {
        console.error('加载桌台失败:', error)
        this.$message.error('加载桌台失败，请检查后端服务或登录状态')
      } finally {
        this.loading = false
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
        await this.loadTables()
      } catch (error) {
        console.error('保存桌台失败:', error)
        this.$message.error('保存桌台失败，请检查参数或登录状态')
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
        await this.loadTables()
      } catch (error) {
        if (error === 'cancel') return
        console.error('删除桌台失败:', error)
        this.$message.error('删除桌台失败')
      }
    },
    async handleOccupy(row) {
      try {
        await occupyTable(row.id)
        this.$message.success('桌台已占用')
        await this.loadTables()
      } catch (error) {
        console.error('占用桌台失败:', error)
        this.$message.error('占用桌台失败')
      }
    },
    async handleFree(row) {
      try {
        await freeTable(row.id)
        this.$message.success('桌台已释放')
        await this.loadTables()
      } catch (error) {
        console.error('释放桌台失败:', error)
        this.$message.error('释放桌台失败')
      }
    },
    async handleClean(row) {
      try {
        await cleanTable(row.id)
        this.$message.success('桌台已设为清洁')
        await this.loadTables()
      } catch (error) {
        console.error('清洁桌台失败:', error)
        this.$message.error('清洁桌台失败')
      }
    },
    async handleSizeChange(size) {
      this.pageSize = size
      this.currentPage = 1
      await this.loadTables()
    },
    async handleCurrentChange(page) {
      this.currentPage = page
      await this.loadTables()
    }
  }
}
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
