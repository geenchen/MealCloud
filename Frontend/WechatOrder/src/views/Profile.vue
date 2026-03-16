<template>
  <div class="profile">
    <div class="hero">
      <h3>老板代客模式</h3>
      <p>当前为门店本地部署，未对顾客开放</p>
    </div>

    <van-cell-group class="panel">
      <van-cell title="当前角色" value="老板/店员" />
      <van-cell title="系统状态" value="已连接后台" />
    </van-cell-group>

    <van-cell-group class="panel mt10">
      <van-cell title="订单记录" icon="orders-o" is-link @click="goOrderHistory" />
      <van-cell title="清空暂存单" icon="delete-o" is-link @click="clearCart" />
    </van-cell-group>
  </div>
</template>

<script>
import { useRouter } from 'vue-router'
import { showConfirmDialog, Toast } from 'vant'
import { useCartStore } from '@/stores/cart'

export default {
  name: 'Profile',
  setup() {
    const router = useRouter()
    const cartStore = useCartStore()

    const goOrderHistory = () => {
      router.push('/order-history')
    }

    const clearCart = async () => {
      try {
        await showConfirmDialog({ title: '确认', message: '确定清空暂存单吗？' })
        cartStore.clearCart()
        Toast.success('已清空')
      } catch {
        // noop
      }
    }

    return {
      goOrderHistory,
      clearCart
    }
  }
}
</script>

<style scoped>
.profile {
  padding: 12px;
}

.hero {
  padding: 14px;
  border-radius: 12px;
  background: linear-gradient(120deg, #fff0de 0%, #ffe5cc 100%);
  border: 1px solid #f7d6b4;
  color: #7a431d;
  margin-bottom: 10px;
}

.hero h3 {
  margin: 0;
}

.hero p {
  margin: 6px 0 0;
  font-size: 12px;
}

.panel {
  border-radius: 14px;
  overflow: hidden;
}

.mt10 {
  margin-top: 10px;
}
</style>
