<template>
  <div class="dishes">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>菜品管理</span>
          <el-button type="primary" @click="addDish">新增菜品</el-button>
        </div>
      </template>

      <el-table v-loading="loading" :data="dishes" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="菜品名称" min-width="160" />
        <el-table-column prop="categoryName" label="分类" width="140" />
        <el-table-column prop="price" label="价格" width="120">
          <template #default="scope">￥{{ Number(scope.row.price).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="stock_quantity" label="库存" width="120" />
        <el-table-column prop="is_available" label="状态" width="110">
          <template #default="scope">
            <el-tag :type="scope.row.is_available ? 'success' : 'danger'">
              {{ scope.row.is_available ? '上架' : '下架' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220">
          <template #default="scope">
            <el-button size="small" @click="editDish(scope.row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDeleteDish(scope.row)">删除</el-button>
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

    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="520px"
      top="6vh"
      :close-on-click-modal="false"
      destroy-on-close
      class="dish-dialog"
    >
      <div class="dish-form-scroll">
        <el-form :model="currentDish" label-width="90px">
        <el-form-item label="菜品名称" required>
          <el-input v-model="currentDish.name" />
        </el-form-item>

        <el-form-item label="分类" required>
          <el-select v-model="currentDish.category_id" placeholder="请选择分类" style="width: 100%">
            <el-option
              v-for="category in categories"
              :key="category.id"
              :label="category.name"
              :value="category.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="价格" required>
          <el-input-number v-model="currentDish.price" :min="0" :step="0.01" :precision="2" style="width: 100%" />
        </el-form-item>

        <el-form-item label="库存">
          <el-input-number v-model="currentDish.stock_quantity" :min="-1" style="width: 100%" />
        </el-form-item>

        <el-form-item label="状态">
          <el-switch
            v-model="currentDish.is_available"
            :active-value="true"
            :inactive-value="false"
            active-text="上架"
            inactive-text="下架"
          />
        </el-form-item>

        <el-form-item label="描述">
          <el-input v-model="currentDish.description" type="textarea" :rows="3" />
        </el-form-item>
        </el-form>
      </div>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveDish">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { createDish, deleteDish, getCategories, getDishes, updateDish } from '@/services/dishService'

const createDefaultDish = () => ({
  id: null,
  name: '',
  category_id: null,
  price: 0,
  stock_quantity: -1,
  is_available: true,
  description: ''
})

export default {
  name: 'Dishes',
  data() {
    return {
      loading: false,
      dishes: [],
      categories: [],
      currentPage: 1,
      pageSize: 10,
      total: 0,
      dialogVisible: false,
      dialogType: 'add',
      currentDish: createDefaultDish()
    }
  },
  computed: {
    dialogTitle() {
      return this.dialogType === 'add' ? '新增菜品' : '编辑菜品'
    }
  },
  async mounted() {
    await this.loadCategories()
    await this.loadDishes()
  },
  methods: {
    async loadCategories() {
      try {
        const categories = await getCategories(0, 200)
        this.categories = Array.isArray(categories) ? categories : []
      } catch (error) {
        console.error('加载分类失败:', error)
        this.$message.error('加载分类失败，请检查后端服务或登录状态')
      }
    },
    async loadDishes() {
      this.loading = true
      try {
        const skip = (this.currentPage - 1) * this.pageSize
        const data = await getDishes(skip, this.pageSize)
        const list = Array.isArray(data) ? data : []
        this.dishes = list.map((dish) => ({
          ...dish,
          price: Number(dish.price),
          stock_quantity: dish.stock_quantity ?? -1,
          categoryName: this.getCategoryName(dish.category_id)
        }))
        this.total = skip + this.dishes.length + (this.dishes.length === this.pageSize ? 1 : 0)
      } catch (error) {
        console.error('加载菜品失败:', error)
        this.$message.error('加载菜品失败，请检查后端服务或登录状态')
      } finally {
        this.loading = false
      }
    },
    getCategoryName(categoryId) {
      const hit = this.categories.find((item) => item.id === categoryId)
      return hit ? hit.name : `分类#${categoryId ?? '-'}`
    },
    addDish() {
      this.dialogType = 'add'
      this.currentDish = createDefaultDish()
      this.dialogVisible = true
    },
    editDish(row) {
      this.dialogType = 'edit'
      this.currentDish = {
        id: row.id,
        name: row.name,
        category_id: row.category_id,
        price: Number(row.price),
        stock_quantity: row.stock_quantity ?? -1,
        is_available: Boolean(row.is_available),
        description: row.description || ''
      }
      this.dialogVisible = true
    },
    async handleDeleteDish(row) {
      try {
        await this.$confirm(`确认删除菜品「${row.name}」吗？`, '提示', {
          confirmButtonText: '确认',
          cancelButtonText: '取消',
          type: 'warning'
        })

        await deleteDish(row.id)
        this.$message.success('删除成功')
        await this.loadDishes()
      } catch (error) {
        if (error === 'cancel') return
        console.error('删除菜品失败:', error)
        this.$message.error('删除菜品失败')
      }
    },
    async saveDish() {
      if (!this.currentDish.name || !this.currentDish.category_id) {
        this.$message.warning('请填写菜品名称和分类')
        return
      }

      const payload = {
        name: this.currentDish.name,
        category_id: Number(this.currentDish.category_id),
        price: Number(this.currentDish.price),
        stock_quantity: Number(this.currentDish.stock_quantity),
        is_available: Boolean(this.currentDish.is_available),
        description: this.currentDish.description || null
      }

      try {
        if (this.dialogType === 'add') {
          await createDish(payload)
          this.$message.success('新增成功')
        } else {
          await updateDish(this.currentDish.id, payload)
          this.$message.success('修改成功')
        }

        this.dialogVisible = false
        await this.loadDishes()
      } catch (error) {
        console.error('保存菜品失败:', error)
        this.$message.error('保存菜品失败，请检查参数或登录状态')
      }
    },
    async handleSizeChange(size) {
      this.pageSize = size
      this.currentPage = 1
      await this.loadDishes()
    },
    async handleCurrentChange(page) {
      this.currentPage = page
      await this.loadDishes()
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

.dish-form-scroll {
  max-height: 65vh;
  overflow-y: auto;
  padding-right: 8px;
  box-sizing: border-box;
}

:deep(.dish-dialog) {
  max-width: 520px;
  width: calc(100vw - 32px);
}

@media (max-width: 768px) {
  :deep(.dish-dialog) {
    width: 92vw !important;
    max-width: 92vw;
    margin-top: 3vh !important;
  }

  .dish-form-scroll {
    max-height: 70vh;
  }
}
</style>
