<template>
  <div class="login-page">
    <div class="login-card">
      <h2 class="title">餐饮后台登录</h2>
      <p class="subtitle">请输入账号密码进入系统</p>

      <el-form ref="formRef" :model="form" :rules="rules" label-position="top" @keyup.enter="submit">
        <el-form-item label="账号" prop="username">
          <el-input v-model="form.username" placeholder="请输入账号" autocomplete="username" />
        </el-form-item>

        <el-form-item label="密码" prop="password">
          <el-input
            v-model="form.password"
            type="password"
            show-password
            placeholder="请输入密码"
            autocomplete="current-password"
          />
        </el-form-item>

        <el-button :loading="submitting" type="primary" class="submit-btn" @click="submit">登录</el-button>
      </el-form>

      <div class="hint">默认管理员账号：admin / admin123</div>
    </div>
  </div>
</template>

<script>
import { login } from '@/services/authService'

export default {
  name: 'Login',
  data() {
    return {
      submitting: false,
      form: {
        username: 'admin',
        password: 'admin123'
      },
      rules: {
        username: [{ required: true, message: '请输入账号', trigger: 'blur' }],
        password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
      }
    }
  },
  methods: {
    async submit() {
      const formValid = await this.$refs.formRef.validate().catch(() => false)
      if (!formValid) {
        return
      }

      this.submitting = true
      try {
        await login(this.form)
        this.$message.success('登录成功')
        const redirect = this.$route.query.redirect || '/'
        this.$router.replace(redirect)
      } catch (error) {
        console.error('登录失败:', error)
        this.$message.error(error?.response?.data?.detail || '登录失败，请检查账号密码')
      } finally {
        this.submitting = false
      }
    }
  }
}
</script>

<style scoped>
.login-page {
  position: fixed;
  inset: 0;
  width: 100vw;
  height: 100vh;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: radial-gradient(circle at top left, #ffdfc4 0%, #fff3e7 42%, #ffe8d6 100%);
}

.login-card {
  width: 420px;
  max-width: calc(100vw - 32px);
  border-radius: 14px;
  padding: 28px;
  box-sizing: border-box;
  background: #fffdfb;
  border: 1px solid #efc9ab;
  box-shadow: 0 14px 30px rgba(159, 85, 45, 0.22);
}

.title {
  margin: 0;
  color: #5a2f1b;
  font-size: 28px;
}

.subtitle {
  margin: 8px 0 20px;
  color: #8b5d45;
}

.submit-btn {
  width: 100%;
  margin-top: 8px;
}

.hint {
  margin-top: 14px;
  color: #9f745a;
  font-size: 12px;
}
</style>


