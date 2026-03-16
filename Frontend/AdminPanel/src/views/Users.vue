<template>
  <div class="users-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>用户管理</span>
          <el-button type="primary" @click="openAddDialog">新增用户</el-button>
        </div>
      </template>

      <el-table v-loading="loading" :data="users" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="账号" min-width="140" />
        <el-table-column prop="email" label="邮箱" min-width="220" />
        <el-table-column prop="full_name" label="姓名" width="140" />
        <el-table-column label="角色" width="110">
          <template #default="scope">
            <el-tag :type="scope.row.is_admin ? 'warning' : 'info'">
              {{ scope.row.is_admin ? '管理员' : '员工' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.is_active ? 'success' : 'danger'">
              {{ scope.row.is_active ? '启用' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="创建时间" width="180">
          <template #default="scope">{{ formatDateTime(scope.row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="290" fixed="right">
          <template #default="scope">
            <el-button size="small" @click="openEditDialog(scope.row)">编辑</el-button>
            <el-button size="small" type="warning" plain @click="openPasswordDialog(scope.row)">重置密码</el-button>
            <el-button
              size="small"
              :type="scope.row.is_active ? 'danger' : 'success'"
              plain
              @click="toggleUserStatus(scope.row)"
            >
              {{ scope.row.is_active ? '禁用' : '启用' }}
            </el-button>
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
      :title="dialogType === 'add' ? '新增用户' : '编辑用户'"
      width="520px"
      :close-on-click-modal="false"
    >
      <el-form ref="userFormRef" :model="form" :rules="formRules" label-width="90px">
        <el-form-item label="账号" prop="username">
          <el-input v-model="form.username" :disabled="dialogType === 'edit'" />
        </el-form-item>

        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" />
        </el-form-item>

        <el-form-item label="姓名" prop="full_name">
          <el-input v-model="form.full_name" />
        </el-form-item>

        <el-form-item label="角色">
          <el-switch
            v-model="form.is_admin"
            :active-value="true"
            :inactive-value="false"
            active-text="管理员"
            inactive-text="员工"
          />
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

        <el-form-item v-if="dialogType === 'add'" label="密码" prop="password">
          <el-input v-model="form.password" type="password" show-password />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="saveUser">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="passwordDialogVisible"
      title="重置密码"
      width="420px"
      :close-on-click-modal="false"
    >
      <el-form ref="passwordFormRef" :model="passwordForm" :rules="passwordRules" label-width="90px">
        <el-form-item label="用户">
          <el-input :model-value="passwordTarget?.username || ''" disabled />
        </el-form-item>
        <el-form-item label="新密码" prop="password">
          <el-input v-model="passwordForm.password" type="password" show-password />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="passwordDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="savingPassword" @click="submitPasswordReset">确认重置</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { createUser, getUsers, resetUserPassword, updateUser } from '@/services/userService'

const createDefaultForm = () => ({
  id: null,
  username: '',
  email: '',
  full_name: '',
  is_admin: false,
  is_active: true,
  password: ''
})

export default {
  name: 'Users',
  data() {
    return {
      loading: false,
      saving: false,
      savingPassword: false,
      users: [],
      currentPage: 1,
      pageSize: 10,
      total: 0,
      dialogVisible: false,
      dialogType: 'add',
      form: createDefaultForm(),
      passwordDialogVisible: false,
      passwordTarget: null,
      passwordForm: {
        password: ''
      },
      formRules: {
        username: [
          { required: true, message: '请输入账号', trigger: 'blur' },
          { min: 3, max: 32, message: '账号长度 3-32 位', trigger: 'blur' }
        ],
        email: [
          { required: true, message: '请输入邮箱', trigger: 'blur' },
          { type: 'email', message: '邮箱格式不正确', trigger: 'blur' }
        ],
        password: [
          { required: true, message: '请输入密码', trigger: 'blur' },
          { min: 6, message: '密码至少 6 位', trigger: 'blur' }
        ]
      },
      passwordRules: {
        password: [
          { required: true, message: '请输入新密码', trigger: 'blur' },
          { min: 6, message: '密码至少 6 位', trigger: 'blur' }
        ]
      }
    }
  },
  async mounted() {
    await this.loadUsers()
  },
  methods: {
    formatDateTime(value) {
      if (!value) return '-'
      const date = new Date(value)
      if (Number.isNaN(date.getTime())) return '-'
      return date.toLocaleString('zh-CN', { hour12: false })
    },
    async loadUsers() {
      this.loading = true
      try {
        const skip = (this.currentPage - 1) * this.pageSize
        const list = await getUsers(skip, this.pageSize)
        this.users = Array.isArray(list) ? list : []
        this.total = skip + this.users.length + (this.users.length === this.pageSize ? 1 : 0)
      } catch (error) {
        console.error('加载用户失败:', error)
        this.$message.error(error?.response?.data?.detail || '加载用户失败')
      } finally {
        this.loading = false
      }
    },
    openAddDialog() {
      this.dialogType = 'add'
      this.form = createDefaultForm()
      this.dialogVisible = true
      this.$nextTick(() => this.$refs.userFormRef?.clearValidate())
    },
    openEditDialog(row) {
      this.dialogType = 'edit'
      this.form = {
        id: row.id,
        username: row.username,
        email: row.email,
        full_name: row.full_name || '',
        is_admin: Boolean(row.is_admin),
        is_active: Boolean(row.is_active),
        password: ''
      }
      this.dialogVisible = true
      this.$nextTick(() => this.$refs.userFormRef?.clearValidate())
    },
    async saveUser() {
      const valid = await this.$refs.userFormRef?.validate().catch(() => false)
      if (!valid) return

      this.saving = true
      try {
        if (this.dialogType === 'add') {
          await createUser({
            username: this.form.username,
            email: this.form.email,
            full_name: this.form.full_name || null,
            is_admin: this.form.is_admin,
            is_active: this.form.is_active,
            password: this.form.password
          })
          this.$message.success('用户创建成功')
        } else {
          await updateUser(this.form.id, {
            email: this.form.email,
            full_name: this.form.full_name || null,
            is_admin: this.form.is_admin,
            is_active: this.form.is_active
          })
          this.$message.success('用户更新成功')
        }

        this.dialogVisible = false
        await this.loadUsers()
      } catch (error) {
        console.error('保存用户失败:', error)
        this.$message.error(error?.response?.data?.detail || '保存用户失败')
      } finally {
        this.saving = false
      }
    },
    openPasswordDialog(row) {
      this.passwordTarget = row
      this.passwordForm.password = ''
      this.passwordDialogVisible = true
      this.$nextTick(() => this.$refs.passwordFormRef?.clearValidate())
    },
    async submitPasswordReset() {
      const valid = await this.$refs.passwordFormRef?.validate().catch(() => false)
      if (!valid || !this.passwordTarget) return

      this.savingPassword = true
      try {
        await resetUserPassword(this.passwordTarget.id, this.passwordForm.password)
        this.$message.success('密码已重置')
        this.passwordDialogVisible = false
      } catch (error) {
        console.error('重置密码失败:', error)
        this.$message.error(error?.response?.data?.detail || '重置密码失败')
      } finally {
        this.savingPassword = false
      }
    },
    async toggleUserStatus(row) {
      try {
        await updateUser(row.id, {
          is_active: !row.is_active
        })
        this.$message.success(!row.is_active ? '用户已启用' : '用户已禁用')
        await this.loadUsers()
      } catch (error) {
        console.error('更新用户状态失败:', error)
        this.$message.error(error?.response?.data?.detail || '更新用户状态失败')
      }
    },
    async handleSizeChange(size) {
      this.pageSize = size
      this.currentPage = 1
      await this.loadUsers()
    },
    async handleCurrentChange(page) {
      this.currentPage = page
      await this.loadUsers()
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
