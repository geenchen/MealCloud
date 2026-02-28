<template>
  <div class="users">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>用户管理</span>
          <el-button type="primary" @click="addUser">新增用户</el-button>
        </div>
      </template>
      
      <el-table :data="users" style="width: 100%" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="用户名" width="120" />
        <el-table-column prop="email" label="邮箱" width="200" />
        <el-table-column prop="fullName" label="姓名" width="120" />
        <el-table-column prop="role" label="角色" width="100">
          <template #default="scope">
            <el-tag :type="getRoleType(scope.row.role)">
              {{ scope.row.role }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="isActive" label="状态" width="80">
          <template #default="scope">
            <el-tag :type="scope.row.isActive ? 'success' : 'danger'">
              {{ scope.row.isActive ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="createdAt" label="创建时间" width="150" />
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button size="small" @click="editUser(scope.row)">编辑</el-button>
            <el-button 
              size="small" 
              :type="scope.row.isActive ? 'warning' : 'success'" 
              @click="toggleUserStatus(scope.row)"
            >
              {{ scope.row.isActive ? '禁用' : '启用' }}
            </el-button>
            <el-button size="small" type="danger" @click="deleteUser(scope.row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <el-pagination
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
        :current-page="currentPage"
        :page-sizes="[10, 20, 50, 100]"
        :page-size="pageSize"
        layout="total, sizes, prev, pager, next, jumper"
        :total="total"
        style="margin-top: 20px;"
      />
    </el-card>
    
    <!-- 用户编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px">
      <el-form :model="currentUser" :rules="rules" ref="userForm" label-width="100px">
        <el-form-item label="用户名" prop="username">
          <el-input 
            v-model="currentUser.username" 
            :disabled="dialogType === 'edit'"
            placeholder="请输入用户名"
          ></el-input>
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input 
            v-model="currentUser.email" 
            placeholder="请输入邮箱"
          ></el-input>
        </el-form-item>
        <el-form-item label="姓名" prop="fullName">
          <el-input 
            v-model="currentUser.fullName" 
            placeholder="请输入姓名"
          ></el-input>
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="currentUser.role" placeholder="请选择角色" style="width: 100%;">
            <el-option label="管理员" value="管理员"></el-option>
            <el-option label="服务员" value="服务员"></el-option>
            <el-option label="厨师" value="厨师"></el-option>
            <el-option label="收银员" value="收银员"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="状态" prop="isActive">
          <el-switch
            v-model="currentUser.isActive"
            :active-value="true"
            :inactive-value="false"
            inline-prompt
            active-text="启用"
            inactive-text="禁用"
          />
        </el-form-item>
        <el-form-item v-if="dialogType === 'add'" label="密码" prop="password">
          <el-input 
            v-model="currentUser.password" 
            type="password"
            show-password
            placeholder="请输入密码"
          ></el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveUser">保存</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
export default {
  name: 'Users',
  data() {
    return {
      users: [
        { id: 1, username: 'admin', email: 'admin@example.com', fullName: '系统管理员', role: '管理员', isActive: true, createdAt: '2023-01-01' },
        { id: 2, username: 'staff001', email: 'staff001@example.com', fullName: '张三', role: '服务员', isActive: true, createdAt: '2023-05-15' },
        { id: 3, username: 'chef001', email: 'chef001@example.com', fullName: '李师傅', role: '厨师', isActive: true, createdAt: '2023-06-20' },
        { id: 4, username: 'cashier001', email: 'cashier001@example.com', fullName: '王收银', role: '收银员', isActive: true, createdAt: '2023-07-10' },
        { id: 5, username: 'staff002', email: 'staff002@example.com', fullName: '赵四', role: '服务员', isActive: false, createdAt: '2023-08-05' }
      ],
      currentPage: 1,
      pageSize: 10,
      total: 5,
      dialogVisible: false,
      dialogType: 'add', // 'add' 或 'edit'
      currentUser: {
        id: null,
        username: '',
        email: '',
        fullName: '',
        role: '服务员',
        isActive: true,
        password: ''
      },
      rules: {
        username: [
          { required: true, message: '请输入用户名', trigger: 'blur' },
          { min: 3, max: 15, message: '长度在 3 到 15 个字符', trigger: 'blur' }
        ],
        email: [
          { required: true, message: '请输入邮箱地址', trigger: 'blur' },
          { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
        ],
        fullName: [
          { required: true, message: '请输入姓名', trigger: 'blur' }
        ],
        password: [
          { required: this.dialogType === 'add', message: '请输入密码', trigger: 'blur' },
          { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
        ]
      }
    }
  },
  computed: {
    dialogTitle() {
      return this.dialogType === 'add' ? '新增用户' : '编辑用户'
    }
  },
  methods: {
    addUser() {
      this.dialogType = 'add'
      this.currentUser = {
        id: null,
        username: '',
        email: '',
        fullName: '',
        role: '服务员',
        isActive: true,
        password: ''
      }
      this.dialogVisible = true
      this.$nextTick(() => {
        if (this.$refs.userForm) {
          this.$refs.userForm.clearValidate()
        }
      })
    },
    editUser(row) {
      this.dialogType = 'edit'
      this.currentUser = { ...row }
      this.dialogVisible = true
      this.$nextTick(() => {
        if (this.$refs.userForm) {
          this.$refs.userForm.clearValidate()
        }
      })
    },
    deleteUser(id) {
      this.$confirm('确定要删除这个用户吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        this.users = this.users.filter(item => item.id !== id)
        this.total = this.users.length
        this.$message.success('删除成功！')
      })
    },
    toggleUserStatus(user) {
      user.isActive = !user.isActive
      const action = user.isActive ? '启用' : '禁用'
      this.$message.success(`${user.username} 已${action}`)
    },
    saveUser() {
      this.$refs.userForm.validate((valid) => {
        if (valid) {
          if (this.dialogType === 'add') {
            const newId = Math.max(...this.users.map(u => u.id), 0) + 1
            const newUser = {
              ...this.currentUser,
              id: newId,
              createdAt: new Date().toISOString().split('T')[0]
            }
            delete newUser.password // 实际应用中，这里应该加密密码并发送到后端
            this.users.push(newUser)
            this.total = this.users.length
            this.$message.success('新增成功！')
          } else {
            const index = this.users.findIndex(item => item.id === this.currentUser.id)
            if (index !== -1) {
              // 保留原始密码字段（如果不是编辑状态则不会显示）
              const updatedUser = { ...this.currentUser }
              delete updatedUser.password
              this.users.splice(index, 1, updatedUser)
              this.$message.success('修改成功！')
            }
          }
          this.dialogVisible = false
        } else {
          this.$message.error('请填写正确的用户信息！')
        }
      })
    },
    getRoleType(role) {
      switch(role) {
        case '管理员': return 'primary'
        case '服务员': return 'success'
        case '厨师': return 'warning'
        case '收银员': return 'info'
        default: return 'info'
      }
    },
    handleSizeChange(val) {
      this.pageSize = val
    },
    handleCurrentChange(val) {
      this.currentPage = val
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

.dialog-footer {
  text-align: right;
}
</style>