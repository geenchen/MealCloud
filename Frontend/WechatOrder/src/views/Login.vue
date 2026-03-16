<template>
  <div class="login-page">
    <div class="login-card">
      <h2>老板点单台登录</h2>
      <p>仅店内授权人员可进入</p>

      <van-field v-model="accessPassword" type="password" label="访问密码" placeholder="请输入访问密码" />
      <van-field v-model="username" label="后台账号" placeholder="请输入后台账号" />
      <van-field v-model="password" type="password" label="后台密码" placeholder="请输入后台密码" />

      <van-button block type="primary" :loading="submitting" @click="handleLogin">进入系统</van-button>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Toast } from 'vant'
import { loginWechatBackend } from '@/services/authService'
import { markAccessGranted, verifyAccessPassword } from '@/services/accessService'

export default {
  name: 'Login',
  setup() {
    const router = useRouter()
    const route = useRoute()
    const accessPassword = ref('')
    const username = ref('')
    const password = ref('')
    const submitting = ref(false)

    const handleLogin = async () => {
      if (submitting.value) return

      const check = verifyAccessPassword(accessPassword.value)
      if (!check.ok) {
        Toast.fail(check.message)
        return
      }

      submitting.value = true
      try {
        await loginWechatBackend(username.value, password.value)
        markAccessGranted()
        const redirect = String(route.query.redirect || '/')
        router.replace(redirect)
      } catch (error) {
        Toast.fail(error?.message || '登录失败')
      } finally {
        submitting.value = false
      }
    }

    return {
      accessPassword,
      username,
      password,
      submitting,
      handleLogin
    }
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  background: radial-gradient(circle at top, #fff1df 0%, #fff8ef 55%, #fffdf8 100%);
}

.login-card {
  width: 100%;
  max-width: 420px;
  padding: 18px;
  border-radius: 14px;
  background: #fffdf9;
  border: 1px solid #f2dcc8;
  box-shadow: 0 16px 32px rgba(122, 66, 28, 0.14);
}

.login-card h2 {
  margin: 0;
  color: #7a431d;
}

.login-card p {
  margin: 8px 0 14px;
  color: #9b775d;
}

.login-card :deep(.van-field) {
  margin-bottom: 8px;
  border-radius: 10px;
  background: #fff8f2;
}
</style>
