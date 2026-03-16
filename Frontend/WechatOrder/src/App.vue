<template>
  <van-nav-bar
    v-if="!hideNavBar"
    :title="title"
    :left-arrow="showBackButton"
    @click-left="goBack"
  />

  <div class="app-container">
    <router-view />
  </div>

  <van-tabbar v-model="activeTab" v-if="showTabBar" @change="onTabChange">
    <van-tabbar-item name="home" icon="home-o">工作台</van-tabbar-item>
    <van-tabbar-item name="menu" icon="orders-o">点菜</van-tabbar-item>
    <van-tabbar-item name="cart" icon="cart-o" :badge="cartStore.totalCount || undefined">暂存单</van-tabbar-item>
    <van-tabbar-item name="profile" icon="setting-o">设置</van-tabbar-item>
  </van-tabbar>
</template>

<script>
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useCartStore } from '@/stores/cart'

export default {
  name: 'App',
  setup() {
    const route = useRoute()
    const router = useRouter()
    const cartStore = useCartStore()
    const activeTab = ref('home')

    const title = computed(() => {
      const titles = {
        '/login': '系统登录',
        '/': '老板点单台',
        '/menu': '代客选菜',
        '/cart': '暂存单',
        '/profile': '门店设置',
        '/order': '确认下单',
        '/order-history': '订单记录'
      }
      return titles[route.path] || '老板点单台'
    })

    const hideNavBar = computed(() => route.path === '/login')
    const showBackButton = computed(() => !['/', '/menu', '/cart', '/profile'].includes(route.path) && !hideNavBar.value)
    const showTabBar = computed(() => ['/', '/menu', '/cart', '/profile'].includes(route.path))

    const goBack = () => router.back()

    const onTabChange = (name) => {
      const routeMap = {
        home: '/',
        menu: '/menu',
        cart: '/cart',
        profile: '/profile'
      }
      router.push(routeMap[name])
    }

    watch(
      () => route.path,
      (path) => {
        if (path === '/') activeTab.value = 'home'
        if (path === '/menu') activeTab.value = 'menu'
        if (path === '/cart') activeTab.value = 'cart'
        if (path === '/profile') activeTab.value = 'profile'
      },
      { immediate: true }
    )

    return {
      activeTab,
      cartStore,
      title,
      hideNavBar,
      showBackButton,
      showTabBar,
      goBack,
      onTabChange
    }
  }
}
</script>

<style>
:root {
  --mc-warm-bg: #fff8ef;
  --mc-panel-bg: #fffdf8;
  --mc-brand: #c45a1f;
  --mc-brand-soft: #ffe5cf;
  --mc-border: #f2dcc8;
  --mc-text: #4e2d1a;
}

#app {
  font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
  min-height: 100vh;
  background: radial-gradient(circle at 0 0, #fff3e6 0%, var(--mc-warm-bg) 46%, #fffaf3 100%);
  color: var(--mc-text);
}

.app-container {
  min-height: calc(100vh - 46px);
}

.van-nav-bar {
  background: linear-gradient(90deg, #b34d16 0%, var(--mc-brand) 45%, #d87835 100%) !important;
}

.van-nav-bar__title,
.van-nav-bar__arrow {
  color: #fff !important;
}

.van-tabbar {
  background: #fffaf5 !important;
  border-top: 1px solid var(--mc-border) !important;
}

.van-tabbar-item {
  color: #9a6c4a !important;
}

.van-tabbar-item--active {
  color: var(--mc-brand) !important;
  font-weight: 700;
}

.van-button--primary {
  background: linear-gradient(90deg, #bc4f19 0%, #d16d2f 100%) !important;
  border: none !important;
}

.van-button--warning {
  background: linear-gradient(90deg, #d36a1f 0%, #e08b3f 100%) !important;
  border: none !important;
}

.van-cell,
.van-cell-group,
.van-field {
  background: var(--mc-panel-bg) !important;
}
</style>
