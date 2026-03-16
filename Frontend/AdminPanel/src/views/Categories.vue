<template>
  <div class="categories">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>分类管理</span>
          <el-button type="primary" @click="openCreateDialog">新增分类</el-button>
        </div>
      </template>

      <el-table v-loading="loading" :data="categories" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="分类名称" min-width="180" />
        <el-table-column prop="description" label="描述" min-width="220" show-overflow-tooltip>
          <template #default="scope">
            {{ scope.row.description || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="sort_order" label="排序" width="100" />
        <el-table-column prop="is_active" label="状态" width="120">
          <template #default="scope">
            <el-tag :type="scope.row.is_active ? 'success' : 'danger'">
              {{ scope.row.is_active ? '启用' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220">
          <template #default="scope">
            <el-button size="small" @click="openEditDialog(scope.row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        style="margin-top: 16px"
        layout="total, sizes, prev, pager, next, jumper"
        :current-page="currentPage"
        :page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="total"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </el-card>

    <el-dialog
      v-model="dialogVisible"
      :title="dialogMode === 'create' ? '新增分类' : '编辑分类'"
      width="520px"
      top="6vh"
      :close-on-click-modal="false"
      destroy-on-close
    >
      <el-form :model="form" label-width="90px">
        <el-form-item label="分类名称" required>
          <el-input v-model="form.name" maxlength="50" show-word-limit />
        </el-form-item>

        <el-form-item label="排序">
          <el-input-number v-model="form.sort_order" :min="0" :max="9999" style="width: 100%" />
        </el-form-item>

        <el-form-item label="状态">
          <el-switch
            v-model="form.is_active"
            :active-value="true"
            :inactive-value="false"
            active-text="启用"
            inactive-text="停用"
          />
        </el-form-item>

        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="3" maxlength="200" show-word-limit />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSubmit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { createCategory, deleteCategory, getCategoriesPage, updateCategory } from '@/services/dishService'

const createDefaultForm = () => ({
  id: null,
  name: '',
  description: '',
  sort_order: 0,
  is_active: true
})

export default {
  name: 'Categories',
  data() {
    return {
      loading: false,
      saving: false,
      categories: [],
      currentPage: 1,
      pageSize: 10,
      total: 0,
      dialogVisible: false,
      dialogMode: 'create',
      form: createDefaultForm()
    }
  },
  async mounted() {
    await this.loadCategories()
  },
  methods: {
    async loadCategories() {
      this.loading = true
      try {
        const skip = (this.currentPage - 1) * this.pageSize
        const data = await getCategoriesPage(skip, this.pageSize)
        const list = Array.isArray(data?.items) ? data.items : []

        this.categories = list.map((item) => ({
          ...item,
          sort_order: Number(item.sort_order ?? 0),
          is_active: Boolean(item.is_active)
        }))

        this.total = Number(data?.total ?? 0)
      } catch (error) {
        console.error('加载分类失败:', error)
        this.$message.error(error?.response?.data?.detail || '加载分类失败，请检查后端服务')
      } finally {
        this.loading = false
      }
    },
    openCreateDialog() {
      this.dialogMode = 'create'
      this.form = createDefaultForm()
      this.dialogVisible = true
    },
    openEditDialog(row) {
      this.dialogMode = 'edit'
      this.form = {
        id: row.id,
        name: row.name,
        description: row.description || '',
        sort_order: Number(row.sort_order ?? 0),
        is_active: Boolean(row.is_active)
      }
      this.dialogVisible = true
    },
    async handleSubmit() {
      const payload = {
        name: (this.form.name || '').trim(),
        description: this.form.description?.trim() || null,
        sort_order: Number(this.form.sort_order ?? 0),
        is_active: Boolean(this.form.is_active)
      }

      this.saving = true
      try {
        if (this.dialogMode === 'create') {
          await createCategory(payload)
          this.$message.success('新增分类成功')
        } else {
          await updateCategory(this.form.id, payload)
          this.$message.success('修改分类成功')
        }

        this.dialogVisible = false
        await this.loadCategories()
      } catch (error) {
        console.error('保存分类失败:', error)
        this.$message.error(error?.response?.data?.detail || '保存分类失败')
      } finally {
        this.saving = false
      }
    },
    async handleDelete(row) {
      try {
        await this.$confirm(`确认删除分类「${row.name}」吗？`, '提示', {
          confirmButtonText: '确认',
          cancelButtonText: '取消',
          type: 'warning'
        })

        await deleteCategory(row.id)
        this.$message.success('删除分类成功')
        await this.loadCategories()
      } catch (error) {
        if (error === 'cancel') return
        console.error('删除分类失败:', error)
        this.$message.error(error?.response?.data?.detail || '删除分类失败')
      }
    },
    async handleSizeChange(size) {
      this.pageSize = size
      this.currentPage = 1
      await this.loadCategories()
    },
    async handleCurrentChange(page) {
      this.currentPage = page
      await this.loadCategories()
    }
  }
}
</script>

<style scoped>
.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
</style>